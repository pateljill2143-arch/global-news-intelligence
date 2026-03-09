"""
Verify that all collected data is in English only
"""
from pymongo import MongoClient
from langdetect import detect, LangDetectException
from collections import Counter

# Connect to MongoDB
mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["global_news_intelligence"]
articles_collection = db["raw_articles"]

print("="*80)
print("🌐 LANGUAGE VERIFICATION - CHECKING ALL ARTICLES")
print("="*80)

# Get all articles
total_articles = articles_collection.count_documents({})
print(f"\nTotal articles in database: {total_articles}")

# Check language distribution
languages = []
non_english = []
error_count = 0

print("\n📊 Analyzing language of all articles...")
print("This may take a minute...\n")

cursor = articles_collection.find({}, {"title": 1, "description": 1, "url": 1, "source_api": 1})

for i, article in enumerate(cursor, 1):
    if i % 500 == 0:
        print(f"  Checked {i}/{total_articles} articles...", flush=True)
    
    title = article.get("title", "")
    description = article.get("description", "")
    text = f"{title} {description}"
    
    if len(text.strip()) < 10:
        continue
    
    try:
        lang = detect(text[:500])
        languages.append(lang)
        
        if lang != 'en':
            non_english.append({
                "title": title[:100],
                "url": article.get("url"),
                "source": article.get("source_api"),
                "detected_lang": lang
            })
    except LangDetectException:
        error_count += 1

# Results
lang_counts = Counter(languages)

print("\n" + "="*80)
print("📊 LANGUAGE DISTRIBUTION")
print("="*80)

for lang, count in lang_counts.most_common():
    percentage = (count / len(languages)) * 100
    lang_name = {
        'en': 'English',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese',
        'ru': 'Russian',
        'ar': 'Arabic',
        'zh-cn': 'Chinese',
        'ja': 'Japanese',
        'hi': 'Hindi'
    }.get(lang, lang.upper())
    
    print(f"{lang_name:20s}: {count:5d} articles ({percentage:5.2f}%)")

if non_english:
    print(f"\n⚠️  FOUND {len(non_english)} NON-ENGLISH ARTICLES:")
    print("="*80)
    for i, item in enumerate(non_english[:10], 1):  # Show first 10
        print(f"\n{i}. [{item['detected_lang'].upper()}] {item['title']}")
        print(f"   Source: {item['source']}")
        print(f"   URL: {item['url']}")
    
    if len(non_english) > 10:
        print(f"\n... and {len(non_english) - 10} more non-English articles")
    
    print("\n💡 To remove non-English articles, run:")
    print("   python clean_non_english_articles.py")
else:
    print("\n✅ ALL ARTICLES ARE IN ENGLISH!")
    print("   Your system is collecting ENGLISH-ONLY data successfully.")

print(f"\nDetection errors: {error_count}")
print("\n" + "="*80)

# Check if new language field exists
with_lang_field = articles_collection.count_documents({"language": "en"})
print(f"\n📌 Articles with 'language' field: {with_lang_field}/{total_articles}")

if with_lang_field < total_articles:
    print("   ℹ️  Old articles don't have language field")
    print("   ℹ️  New collections will auto-filter non-English")

mongo_client.close()
