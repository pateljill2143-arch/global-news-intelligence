"""
Clean database - Remove all non-English articles
"""
from pymongo import MongoClient
from langdetect import detect, LangDetectException

# Connect to MongoDB
mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["global_news_intelligence"]
articles_collection = db["raw_articles"]

print("="*80)
print("🧹 CLEANING NON-ENGLISH ARTICLES FROM DATABASE")
print("="*80)

total_before = articles_collection.count_documents({})
print(f"\nTotal articles before cleaning: {total_before}")

# Find and remove non-English articles
to_delete = []

cursor = articles_collection.find({}, {"_id": 1, "title": 1, "description": 1})

print("\n🔍 Scanning for non-English articles...")

for i, article in enumerate(cursor, 1):
    if i % 500 == 0:
        print(f"  Scanned {i}/{total_before} articles...", flush=True)
    
    title = article.get("title", "")
    description = article.get("description", "")
    text = f"{title} {description}"
    
    if len(text.strip()) < 10:
        continue
    
    try:
        lang = detect(text[:500])
        if lang != 'en':
            to_delete.append(article["_id"])
    except LangDetectException:
        pass  # Keep if detection fails

# Delete non-English articles
if to_delete:
    print(f"\n🗑️  Deleting {len(to_delete)} non-English articles...")
    result = articles_collection.delete_many({"_id": {"$in": to_delete}})
    print(f"   ✓ Deleted {result.deleted_count} articles")
else:
    print("\n✅ No non-English articles found!")

total_after = articles_collection.count_documents({})
print(f"\nTotal articles after cleaning: {total_after}")
print(f"Articles removed: {total_before - total_after}")

print("\n" + "="*80)
print("✅ DATABASE CLEANED - ENGLISH ONLY")
print("="*80)

mongo_client.close()
