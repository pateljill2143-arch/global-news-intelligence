"""Check MongoDB to see collected articles"""
from pymongo import MongoClient

mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["global_news_intelligence"]
articles_collection = db["raw_articles"]

# Count total articles
total = articles_collection.count_documents({})
print(f"Total articles in database: {total}")

# Count by source API
sources = articles_collection.distinct("source_api")
print(f"\nBreakdown by source:")
for source in sources:
    count = articles_collection.count_documents({"source_api": source})
    print(f"  {source}: {count}")

# Show latest 5 articles
print(f"\n Latest 5 articles:")
latest = articles_collection.find().sort([("collected_at", -1)]).limit(5)
for i, article in enumerate(latest, 1):
    print(f"{i}. [{article.get('source_api')}] {article.get('title')[:80]}")
    print(f"   URL: {article.get('url')}")
    print(f"   Category: {article.get('category')}")
    print()

mongo_client.close()
