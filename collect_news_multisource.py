"""
MULTI-SOURCE DATA COLLECTION LAYER
Fetches news from MULTIPLE free APIs to bypass rate limits
Sources: NewsData.io, The Guardian, GNews, NewsAPI
"""

import requests
from pymongo import MongoClient
from datetime import datetime, timedelta
import time
import sysfrom langdetect import detect, LangDetectException
# Fix Windows console encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# -------------------------
# API KEYS (All FREE tier)
# -------------------------

# NewsAPI - 100 requests/day
NEWSAPI_KEY = "b6851d27958f4cd9940491e9f8fe9c3d"

# NewsData.io - 200 requests/day
# Sign up at: https://newsdata.io/register
NEWSDATA_KEY = "pub_8c6d3b5ad17a43c597dbbf9e055d5fd2"  # FREE: 200 requests/day

# The Guardian - 500 requests/day, 5000/month
# Sign up at: https://open-platform.theguardian.com/access/
GUARDIAN_KEY = "c68b9202-4f02-466d-a60d-b6982be2b9f4"  # FREE: 500 requests/day

# GNews.io - 100 requests/day
# Sign up at: https://gnews.io/
GNEWS_KEY = "dad0cee9e7e166a4a1abc6f49c0530ac"  # FREE: 100 requests/day

# -------------------------
# MONGODB
# -------------------------

MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB = "global_news_intelligence"
MONGO_COLLECTION = "raw_articles"

try:
    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client[MONGO_DB]
    articles_collection = db[MONGO_COLLECTION]
    
    articles_collection.create_index([("url", 1)], unique=True)
    articles_collection.create_index([("publishedAt", -1)])
    articles_collection.create_index([("processed", 1)])
    articles_collection.create_index([("source_api", 1)])  # Track which API
    
    print("✓ Connected to MongoDB", flush=True)
except Exception as e:
    print(f"✗ MongoDB failed: {e}", flush=True)
    exit(1)

# -------------------------
# LANGUAGE DETECTION
# -------------------------

def is_english(text):
    """Verify text is in English (safety check for APIs)"""
    if not text or len(text.strip()) < 10:
        return False
    try:
        lang = detect(text[:500])  # Check first 500 chars
        return lang == 'en'
    except LangDetectException:
        return True  # If detection fails, allow through (likely too short)

# -------------------------
# SEARCH TOPICS (Prioritized)
# -------------------------

priority_topics = [
    # GLOBAL CONFLICTS
    "Russia Ukraine war",
    "Israel Palestine Gaza",
    "China Taiwan",
    "Iran nuclear",
    
    # MAJOR POWERS
    "USA Trump Biden election",
    "China Xi Jinping",
    "India Modi",
    "Russia Putin",
    
    # TECHNOLOGY
    "artificial intelligence AI",
    "ChatGPT OpenAI",
    "cryptocurrency Bitcoin",
    
    # CLIMATE
    "climate change",
    "global warming",
    
    # ECONOMY
    "stock market",
    "inflation recession",
    
    # HEALTH
    "COVID pandemic",
    "vaccine health",
]

# -------------------------
# FETCH FROM NEWSDATA.IO
# -------------------------

def fetch_newsdata(topic, max_results=10):
    """NewsData.io API - 200 requests/day - ENGLISH ONLY"""
    if NEWSDATA_KEY == "YOUR_KEY_HERE":
        return []
    
    try:
        url = f"https://newsdata.io/api/1/news?apikey={NEWSDATA_KEY}&q={topic}&language=en"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get("status") == "success" and "results" in data:
            articles = []
            non_english_count = 0
            
            for item in data["results"][:max_results]:
                title = item.get("title", "")
                description = item.get("description", "")
                
                # Double-check language (API filter sometimes unreliable)
                if not is_english(f"{title} {description}"):
                    non_english_count += 1
                    continue
                
                article = {
                    "title": title,
                    "description": description,
                    "content": item.get("content") or description,
                    "url": item.get("link"),
                    "source": {"name": item.get("source_id")},
                    "publishedAt": item.get("pubDate"),
                    "category": topic,
                    "source_api": "newsdata.io",
                    "language": "en",
                    "collected_at": datetime.utcnow(),
                    "processed": False
                }
                articles.append(article)
            
            if non_english_count > 0:
                print(f" (filtered {non_english_count} non-English)", end="", flush=True)
            
            return articles
        else:
            error_msg = data.get('message', data.get('results', {}).get('message', 'Unknown'))
            print(f"[NewsData: {error_msg}]")
            return []
    except Exception as e:
        print(f"[NewsData error: {e}]")
        return []

# -------------------------
# FETCH FROM THE GUARDIAN
# -------------------------

def fetch_guardian(topic, max_results=50):
    """The Guardian API - 500 requests/day - ENGLISH ONLY"""
    if GUARDIAN_KEY == "YOUR_KEY_HERE":
        return []
    
    try:
        # Guardian has generous limits - fetch more
        url = f"https://content.guardianapis.com/search?q={topic}&page-size={max_results}&api-key={GUARDIAN_KEY}"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get("response", {}).get("status") == "ok":
            articles = []
            non_english_count = 0
            results = data["response"].get("results", [])
            if not results:
                return []
            
            for item in results:
                # Guardian returns minimal data without show-fields param
                # Just use what's available
                if item.get("webUrl") and item.get("webTitle"):
                    title = item.get("webTitle")
                    
                    # Language check
                    if not is_english(title):
                        non_english_count += 1
                        continue
                    
                    article = {
                        "title": title,
                        "description": title,  # Use title as description
                        "content": title,  # Minimal content
                        "url": item.get("webUrl"),
                        "source": {"name": "The Guardian"},
                        "publishedAt": item.get("webPublicationDate"),
                        "category": topic,
                        "source_api": "guardian",
                        "language": "en",
                        "collected_at": datetime.utcnow(),
                        "processed": False
                    }
                    articles.append(article)
            
            if non_english_count > 0:
                print(f" (filtered {non_english_count} non-English)", end="", flush=True)
            
            return articles
        else:
            error_msg = data.get('message', 'Unknown')
            print(f"[Guardian: {error_msg}]")
            return []
    except Exception as e:
        print(f"[Guardian error: {e}]")
        return []

# -------------------------
# FETCH FROM GNEWS
# -------------------------

def fetch_gnews(topic, max_results=10):
    """GNews API - 100 requests/day - ENGLISH ONLY"""
    if GNEWS_KEY == "YOUR_KEY_HERE":
        return []
    
    try:
        url = f"https://gnews.io/api/v4/search?q={topic}&lang=en&max={max_results}&apikey={GNEWS_KEY}"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if "articles" in data and data.get("totalArticles", 0) > 0:
            articles = []
            non_english_count = 0
            
            for item in data["articles"]:
                if item.get("url") and item.get("title"):
                    title = item.get("title")
                    description = item.get("description", title)
                    
                    # Language verification
                    if not is_english(f"{title} {description}"):
                        non_english_count += 1
                        continue
                    
                    article = {
                        "title": title,
                        "description": description,
                        "content": item.get("content", description),
                        "url": item.get("url"),
                        "source": {"name": item.get("source", {}).get("name", "GNews")},
                        "publishedAt": item.get("publishedAt"),
                        "category": topic,
                        "source_api": "gnews",
                        "language": "en",
                        "collected_at": datetime.utcnow(),
                        "processed": False
                    }
                    articles.append(article)
            
            if non_english_count > 0:
                print(f" (filtered {non_english_count} non-English)", end="", flush=True)
            
            return articles
        else:
            error_msg = data.get('errors', data.get('message', 'No articles'))
            print(f"[GNews: {error_msg}]")
            return []
    except Exception as e:
        print(f"[GNews error: {e}]")
        return []

# -------------------------
# FETCH FROM NEWSAPI (Legacy)
# -------------------------

def fetch_newsapi(topic, max_results=100):
    """NewsAPI.org - 100 requests/day - ENGLISH ONLY"""
    try:
        url = f"https://newsapi.org/v2/everything?q={topic}&language=en&pageSize={max_results}&apiKey={NEWSAPI_KEY}"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get("status") == "ok" and "articles" in data:
            articles = []
            non_english_count = 0
            
            for item in data["articles"]:
                title = item.get("title", "")
                description = item.get("description", "")
                
                # Double-check language
                if not is_english(f"{title} {description}"):
                    non_english_count += 1
                    continue
                
                article = {
                    "title": title,
                    "description": description,
                    "content": item.get("content"),
                    "url": item.get("url"),
                    "source": item.get("source"),
                    "publishedAt": item.get("publishedAt"),
                    "category": topic,
                    "source_api": "newsapi.org",
                    "language": "en",
                    "collected_at": datetime.utcnow(),
                    "processed": False
                }
                articles.append(article)
            
            if non_english_count > 0:
                print(f" (filtered {non_english_count} non-English)", end="", flush=True)
            
            return articles
        else:
            # Likely rate limited, skip silently
            return []
    except Exception as e:
        return []

# -------------------------
# MAIN COLLECTION LOOP
# -------------------------

print("\n📰 MULTI-SOURCE NEWS COLLECTION")
print("=" * 80)
sys.stdout.flush()

# API sources to try (in order)
api_sources = [
    ("The Guardian", fetch_guardian, 50),  # Most generous: 500/day
    ("NewsData.io", fetch_newsdata, 10),   # 200/day
    ("GNews", fetch_gnews, 10),            # 100/day
    ("NewsAPI", fetch_newsapi, 100),       # 100/day (might be exhausted)
]

total_collected = 0
total_new = 0
total_duplicates = 0

for topic in priority_topics:
    print(f"\n🔍 Topic: {topic}", flush=True)
    topic_articles = []
    
    # Try each API source
    for api_name, fetch_func, max_results in api_sources:
        try:
            print(f"   🔄 Trying {api_name}...", end=" ", flush=True)
            articles = fetch_func(topic, max_results)
            if articles:
                print(f"✓ {len(articles)} articles", flush=True)
                topic_articles.extend(articles)
            else:
                print(f"✗ No articles returned", flush=True)
            time.sleep(0.5)  # Rate limiting
        except Exception as e:
            print(f"✗ Exception: {e}", flush=True)
    
    # Store to MongoDB
    new_count = 0
    dup_count = 0
    
    for article in topic_articles:
        try:
            articles_collection.insert_one(article)
            new_count += 1
        except Exception:
            dup_count += 1  # Duplicate URL
    
    total_collected += len(topic_articles)
    total_new += new_count
    total_duplicates += dup_count
    
    print(f"   📊 Stored: {new_count} new | {dup_count} duplicates", flush=True)

# -------------------------
# SUMMARY
# -------------------------

print("\n" + "=" * 80, flush=True)
print("📊 MULTI-SOURCE COLLECTION SUMMARY", flush=True)
print("=" * 80, flush=True)
print(f"Total articles collected: {total_collected}", flush=True)
print(f"New articles stored: {total_new}", flush=True)
print(f"Duplicate articles skipped: {total_duplicates}", flush=True)

# Database stats
total_in_db = articles_collection.count_documents({})
unprocessed = articles_collection.count_documents({"processed": False})

# Count by source API
print(f"\n📦 DATABASE STATUS")
print(f"Total articles in database: {total_in_db}")
print(f"Unprocessed articles: {unprocessed}")

# Break down by source
print(f"\n📡 BREAKDOWN BY API SOURCE")
for api_name in ["newsapi.org", "guardian", "newsdata.io", "gnews"]:
    count = articles_collection.count_documents({"source_api": api_name})
    if count > 0:
        print(f"   {api_name}: {count} articles")

mongo_client.close()
print("\n✓ Multi-source collection complete!")
print("\n💡 TO GET MORE DATA:")
print("   1. Sign up for FREE API keys at:")
print("      - NewsData.io: https://newsdata.io/register (200/day)")
print("      - The Guardian: https://open-platform.theguardian.com/access/ (500/day)")
print("      - GNews: https://gnews.io/ (100/day)")
print("   2. Add keys to this script")
print("   3. Run again to collect from multiple sources")
print("   4. Total potential: 900+ requests/day across all APIs!")
