"""Check if data is static or dynamic - show timestamps"""
from pymongo import MongoClient
from datetime import datetime

mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["global_news_intelligence"]
articles_collection = db["raw_articles"]

# Get latest article with timestamp
latest = articles_collection.find_one(
    {"collected_at": {"$exists": True}},
    sort=[("collected_at", -1)]
)

if latest:
    collected_time = latest.get('collected_at')
    if isinstance(collected_time, str):
        collected_time = datetime.fromisoformat(collected_time.replace('Z', '+00:00'))
    
    time_diff = datetime.now() - collected_time
    hours_old = time_diff.total_seconds() / 3600
    
    print("="*60)
    print("📊 DATA FRESHNESS CHECK")
    print("="*60)
    print(f"\nTotal articles: {articles_collection.count_documents({})}")
    print(f"\nLast data collection:")
    print(f"  Timestamp: {collected_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Age: {hours_old:.1f} hours ago")
    
    if hours_old < 1:
        print(f"  Status: 🟢 DYNAMIC (Fresh data)")
    elif hours_old < 24:
        print(f"  Status: 🟡 SEMI-STATIC (Updated within 24h)")
    else:
        print(f"  Status: 🔴 STATIC (Data is {hours_old/24:.1f} days old)")
else:
    print("No articles with timestamps found")

# Check if there are unprocessed articles
unprocessed = articles_collection.count_documents({"processed": {"$ne": True}})
print(f"\nUnprocessed articles: {unprocessed}")

print("\n" + "="*60)
print("💡 TO MAKE DATA DYNAMIC:")
print("="*60)
print("Run one of these:")
print("  1. python run_continuous_rss.py    (Updates every 10 min)")
print("  2. python run_continuous.py        (Updates every 1 hour)")
print("  3. setup_auto_collection.bat       (Windows Task Scheduler)")
print("="*60)

mongo_client.close()
