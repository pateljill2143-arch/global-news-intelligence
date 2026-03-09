"""
REAL-TIME RSS FEED COLLECTOR - True Dynamic Data
Collects from RSS feeds which update continuously (no rate limits!)
"""

import feedparser
from pymongo import MongoClient
from datetime import datetime
import time
import sys
from langdetect import detect, LangDetectException

# Fix Windows encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# MongoDB
mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["global_news_intelligence"]
articles_collection = db["raw_articles"]

print("✓ Connected to MongoDB", flush=True)

# RSS FEEDS - NO RATE LIMITS, UPDATE EVERY FEW MINUTES
rss_feeds = {
    # GLOBAL NEWS
    "BBC World": "http://feeds.bbci.co.uk/news/world/rss.xml",
    "Reuters World": "https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best",
    "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    "CNN World": "http://rss.cnn.com/rss/cnn_world.rss",
    
    # REGIONAL
    "BBC Asia": "http://feeds.bbci.co.uk/news/world/asia/rss.xml",
    "BBC Europe": "http://feeds.bbci.co.uk/news/world/europe/rss.xml",
    "BBC Middle East": "http://feeds.bbci.co.uk/news/world/middle_east/rss.xml",
    "BBC Africa": "http://feeds.bbci.co.uk/news/world/africa/rss.xml",
    
    # POLITICS
    "BBC Politics": "http://feeds.bbci.co.uk/news/politics/rss.xml",
    "Politico": "https://www.politico.com/rss/politicopicks.xml",
    
    # TECHNOLOGY
    "BBC Technology": "http://feeds.bbci.co.uk/news/technology/rss.xml",
    "TechCrunch": "https://techcrunch.com/feed/",
    "The Verge": "https://www.theverge.com/rss/index.xml",
    "Ars Technica": "http://feeds.arstechnica.com/arstechnica/index",
    
    # BUSINESS
    "BBC Business": "http://feeds.bbci.co.uk/news/business/rss.xml",
    "Financial Times": "https://www.ft.com/?format=rss",
    
    # SCIENCE
    "BBC Science": "http://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
    "Nature News": "http://feeds.nature.com/nature/rss/current",
    
    # CONFLICT ZONES
    "Ukraine News": "https://www.ukrinform.net/rss/block-lastnews",
    "Times of Israel": "https://www.timesofisrael.com/feed/",
}

def is_english(text):
    """Check if text is in English"""
    if not text or len(text.strip()) < 10:
        return False
    try:
        # Detect language from title and description
        lang = detect(text[:500])  # Use first 500 chars for detection
        return lang == 'en'
    except LangDetectException:
        # If detection fails, assume English (likely too short)
        return True

def fetch_rss(source_name, feed_url):
    """Fetch articles from RSS feed - ENGLISH ONLY"""
    try:
        feed = feedparser.parse(feed_url)
        articles = []
        non_english_count = 0
        
        for entry in feed.entries[:20]:  # Get latest 20
            title = entry.get("title", "")
            description = entry.get("summary", entry.get("description", ""))
            content = entry.get("content", [{}])[0].get("value", description)
            
            # LANGUAGE FILTER: Check if content is English
            text_to_check = f"{title} {description}"
            if not is_english(text_to_check):
                non_english_count += 1
                continue  # Skip non-English articles
            
            article = {
                "title": title,
                "description": description,
                "content": content,
                "url": entry.get("link", ""),
                "source": {"name": source_name},
                "publishedAt": entry.get("published", entry.get("updated", "")),
                "category": source_name,
                "source_api": "rss_feed",
                "language": "en",  # Mark as English
                "collected_at": datetime.now(),
                "processed": False
            }
            
            if article["url"]:  # Only if has valid URL
                articles.append(article)
        
        if non_english_count > 0:
            print(f"   (Filtered {non_english_count} non-English articles)", flush=True)
        
        return articles
    except Exception as e:
        print(f"   ✗ {source_name}: {e}", flush=True)
        return []

# COLLECT FROM ALL RSS FEEDS
print("\n📡 REAL-TIME RSS FEED COLLECTION")
print("="*80, flush=True)
print("RSS feeds update every few minutes - TRUE dynamic data!", flush=True)
print("="*80, flush=True)

total_collected = 0
total_new = 0
total_duplicates = 0

for source_name, feed_url in rss_feeds.items():
    print(f"\n🔍 {source_name}", flush=True)
    
    articles = fetch_rss(source_name, feed_url)
    
    if articles:
        new_count = 0
        dup_count = 0
        
        for article in articles:
            try:
                articles_collection.insert_one(article)
                new_count += 1
            except Exception:
                dup_count += 1  # Duplicate URL
        
        total_collected += len(articles)
        total_new += new_count
        total_duplicates += dup_count
        
        print(f"   ✓ Fetched: {len(articles)} | New: {new_count} | Duplicates: {dup_count}", flush=True)
    
    time.sleep(0.2)  # Small delay between feeds

# SUMMARY
print("\n" + "="*80, flush=True)
print("📊 RSS COLLECTION SUMMARY", flush=True)
print("="*80, flush=True)
print(f"Total articles fetched: {total_collected}", flush=True)
print(f"New articles stored: {total_new}", flush=True)
print(f"Duplicate articles skipped: {total_duplicates}", flush=True)

# Database stats
total_in_db = articles_collection.count_documents({})
unprocessed = articles_collection.count_documents({"processed": False})

print(f"\n📦 DATABASE STATUS", flush=True)
print(f"Total articles in database: {total_in_db}", flush=True)
print(f"Unprocessed articles: {unprocessed}", flush=True)

mongo_client.close()
print("\n✓ RSS collection complete!", flush=True)
print("\n💡 RSS feeds can be checked every 5-10 minutes for truly dynamic data!")
print("   Run: python run_continuous_rss.py")
