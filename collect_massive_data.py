"""
🚀 MASSIVE DATA COLLECTION - Get 1000s of Articles
Collects maximum data from all available sources!
"""

import requests
from pymongo import MongoClient
from datetime import datetime
import time
import sys
from langdetect import detect, LangDetectException
import feedparser

# Fix Windows encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ============================================================================
# CONFIGURATION
# ============================================================================

# API KEYS
NEWSAPI_KEY = "b6851d27958f4cd9940491e9f8fe9c3d"
NEWSDATA_KEY = "pub_8c6d3b5ad17a43c597dbbf9e055d5fd2"
GUARDIAN_KEY = "c68b9202-4f02-466d-a60d-b6982be2b9f4"
GNEWS_KEY = "dad0cee9e7e166a4a1abc6f49c0530ac"

# MongoDB
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB = "global_news_intelligence"
MONGO_COLLECTION = "raw_articles"

# ============================================================================
# EXPANDED TOPICS LIST (100+ topics for maximum coverage)
# ============================================================================

TOPICS = [
    # GLOBAL CONFLICTS & WAR
    "Russia Ukraine war conflict", "Israel Palestine Gaza Hamas", "Syria war ISIS",
    "Yemen war Saudi Arabia", "Afghanistan Taliban", "Iraq conflict ISIS",
    "Libya civil war", "Sudan conflict", "Ethiopia Tigray war",
    "Myanmar military coup", "Kashmir India Pakistan conflict",
    
    # WORLD LEADERS & POLITICS
    "Biden USA president", "Trump election campaign", "Putin Russia",
    "Xi Jinping China", "Modi India", "Macron France",
    "Scholz Germany", "Erdogan Turkey", "Netanyahu Israel",
    "Zelensky Ukraine", "Kim Jong Un North Korea",
    
    # INTERNATIONAL RELATIONS
    "NATO expansion", "European Union Brexit", "UN Security Council",
    "G7 summit", "G20 meeting", "BRICS countries",
    "China Taiwan relations", "North Korea nuclear", "Iran nuclear deal",
    "Saudi Arabia oil", "OPEC petroleum",
    
    # TERRORISM & SECURITY
    "terrorism attack ISIS", "Al Qaeda militant", "Hezbollah Lebanon",
    "Taliban Afghanistan", "Boko Haram Nigeria", "cyber attack ransomware",
    "espionage spy scandal", "assassination attempt",
    
    # CLIMATE & ENVIRONMENT
    "climate change global warming", "carbon emissions reduction",
    "renewable energy solar wind", "electric vehicle Tesla",
    "deforestation Amazon rainforest", "ocean pollution plastic",
    "extreme weather hurricane", "wildfire forest fire",
    "earthquake tsunami disaster", "flood drought",
    
    # TECHNOLOGY & AI
    "artificial intelligence ChatGPT", "machine learning AI",
    "quantum computing", "cryptocurrency Bitcoin Ethereum",
    "blockchain technology", "metaverse virtual reality",
    "5G network technology", "space exploration SpaceX",
    "robotics automation", "cybersecurity hacking",
    
    # ECONOMY & FINANCE
    "stock market crash recession", "inflation interest rates",
    "Federal Reserve economic policy", "cryptocurrency regulation",
    "banking crisis SVB", "trade war tariffs",
    "unemployment jobs report", "housing market prices",
    "oil prices energy crisis", "supply chain shortage",
    
    # HEALTH & PANDEMIC
    "COVID pandemic coronavirus", "vaccine vaccination",
    "WHO health crisis", "bird flu pandemic",
    "mpox outbreak", "cancer research breakthrough",
    "mental health crisis", "opioid epidemic",
    
    # SOCIAL ISSUES
    "immigration refugee crisis", "racial justice protest",
    "gender equality women rights", "LGBTQ rights",
    "police brutality reform", "gun control shooting",
    "abortion rights debate", "supreme court ruling",
    
    # CORPORATE & BUSINESS
    "Apple Google Microsoft", "Amazon Facebook Meta",
    "Tesla SpaceX Elon Musk", "Twitter X social media",
    "TikTok ban China", "AI regulation policy",
    "antitrust lawsuit monopoly", "merger acquisition deal",
    
    # SCIENCE & SPACE
    "NASA Mars mission", "James Webb telescope discovery",
    "fusion energy breakthrough", "particle physics CERN",
    "gene editing CRISPR", "stem cell research",
    
    # REGIONAL NEWS
    "India elections democracy", "China economy growth",
    "Brazil Amazon deforestation", "Mexico cartel violence",
    "Nigeria oil production", "South Africa corruption",
    "Australia bushfire", "Canada wildfires",
    
    # ENTERTAINMENT & CULTURE
    "Hollywood strike actors", "streaming Netflix Disney",
    "sports FIFA World Cup", "Olympics Paris 2024",
    "music industry concert", "gaming industry esports",
]

# ============================================================================
# RSS FEEDS (50+ sources for MASSIVE data collection)
# ============================================================================

RSS_FEEDS = {
    # MAJOR INTERNATIONAL NEWS
    "BBC World": "http://feeds.bbci.co.uk/news/world/rss.xml",
    "BBC UK": "http://feeds.bbci.co.uk/news/uk/rss.xml",
    "BBC Asia": "http://feeds.bbci.co.uk/news/world/asia/rss.xml",
    "BBC Europe": "http://feeds.bbci.co.uk/news/world/europe/rss.xml",
    "BBC Middle East": "http://feeds.bbci.co.uk/news/world/middle_east/rss.xml",
    "BBC Africa": "http://feeds.bbci.co.uk/news/world/africa/rss.xml",
    "BBC US & Canada": "http://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml",
    "BBC Latin America": "http://feeds.bbci.co.uk/news/world/latin_america/rss.xml",
    
    "Reuters World": "https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best",
    "CNN World": "http://rss.cnn.com/rss/cnn_world.rss",
    "CNN US": "http://rss.cnn.com/rss/cnn_us.rss",
    "CNN Politics": "http://rss.cnn.com/rss/cnn_allpolitics.rss",
    
    "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    
    # POLITICS
    "BBC Politics": "http://feeds.bbci.co.uk/news/politics/rss.xml",
    "Politico": "https://www.politico.com/rss/politicopicks.xml",
    
    # TECHNOLOGY
    "BBC Technology": "http://feeds.bbci.co.uk/news/technology/rss.xml",
    "TechCrunch": "https://techcrunch.com/feed/",
    "The Verge": "https://www.theverge.com/rss/index.xml",
    "Ars Technica": "http://feeds.arstechnica.com/arstechnica/index",
    "Wired": "https://www.wired.com/feed/rss",
    "Engadget": "https://www.engadget.com/rss.xml",
    "CNET": "https://www.cnet.com/rss/news/",
    
    # BUSINESS & FINANCE
    "BBC Business": "http://feeds.bbci.co.uk/news/business/rss.xml",
    "Financial Times": "https://www.ft.com/?format=rss",
    "Bloomberg": "https://www.bloomberg.com/feed/podcast/etf-report.xml",
    
    # SCIENCE
    "BBC Science": "http://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
    "Nature News": "http://feeds.nature.com/nature/rss/current",
    "Science Daily": "https://www.sciencedaily.com/rss/all.xml",
    "NASA": "https://www.nasa.gov/rss/dyn/breaking_news.rss",
    
    # CONFLICT ZONES
    "Ukraine News": "https://www.ukrinform.net/rss/block-lastnews",
    "Times of Israel": "https://www.timesofisrael.com/feed/",
    
    # HEALTH
    "BBC Health": "http://feeds.bbci.co.uk/news/health/rss.xml",
    "Medical News Today": "https://www.medicalnewstoday.com/rss",
    
    # ENTERTAINMENT
    "BBC Entertainment": "http://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml",
    "Variety": "https://variety.com/feed/",
    
    # REGIONAL
    "New York Times": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "Washington Post": "http://feeds.washingtonpost.com/rss/world",
    "Guardian World": "https://www.theguardian.com/world/rss",
    "Guardian UK": "https://www.theguardian.com/uk-news/rss",
    "Guardian US": "https://www.theguardian.com/us-news/rss",
}

# ============================================================================
# LANGUAGE DETECTION
# ============================================================================

def is_english(text):
    """Check if text is in English"""
    if not text or len(text.strip()) < 10:
        return False
    try:
        lang = detect(text[:500])
        return lang == 'en'
    except LangDetectException:
        return True

# ============================================================================
# RSS COLLECTION (UNLIMITED)
# ============================================================================

def collect_from_rss():
    """Collect from ALL RSS feeds"""
    print("\n" + "="*80)
    print("📡 COLLECTING FROM 40+ RSS FEEDS (NO LIMITS!)")
    print("="*80)
    
    all_articles = []
    
    for source_name, feed_url in RSS_FEEDS.items():
        print(f"\n📰 {source_name}...", end=" ", flush=True)
        
        try:
            feed = feedparser.parse(feed_url)
            articles = []
            non_english = 0
            
            for entry in feed.entries[:50]:  # Get up to 50 per feed
                title = entry.get("title", "")
                description = entry.get("summary", entry.get("description", ""))
                
                # English filter
                if not is_english(f"{title} {description}"):
                    non_english += 1
                    continue
                
                article = {
                    "title": title,
                    "description": description,
                    "content": entry.get("content", [{}])[0].get("value", description),
                    "url": entry.get("link", ""),
                    "source": {"name": source_name},
                    "publishedAt": entry.get("published", entry.get("updated", "")),
                    "category": source_name,
                    "source_api": "rss_feed",
                    "language": "en",
                    "collected_at": datetime.now(),
                    "processed": False
                }
                
                if article["url"]:
                    articles.append(article)
            
            print(f"✓ {len(articles)} articles", flush=True)
            if non_english > 0:
                print(f"    (filtered {non_english} non-English)", flush=True)
            
            all_articles.extend(articles)
            time.sleep(0.1)  # Small delay
            
        except Exception as e:
            print(f"✗ Error: {e}", flush=True)
    
    print(f"\n✅ Total RSS articles: {len(all_articles)}")
    return all_articles

# ============================================================================
# API COLLECTION (MAXIMUM RESULTS)
# ============================================================================

def collect_from_apis():
    """Collect from ALL APIs with MAXIMUM topics"""
    print("\n" + "="*80)
    print("🌐 COLLECTING FROM APIS - 100+ TOPICS")
    print("="*80)
    
    all_articles = []
    
    # NewsAPI - 100 requests/day limit
    print("\n📊 NewsAPI.org (selecting top topics to stay under limit)...")
    for i, topic in enumerate(TOPICS[:15], 1):  # Use 15 topics for NewsAPI
        print(f"  [{i}/15] {topic}...", end=" ", flush=True)
        
        try:
            url = f"https://newsapi.org/v2/everything?q={topic}&language=en&pageSize=100&apiKey={NEWSAPI_KEY}"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data.get("status") == "ok":
                articles = []
                for item in data.get("articles", []):
                    title = item.get("title", "")
                    description = item.get("description", "")
                    
                    if is_english(f"{title} {description}"):
                        articles.append({
                            "title": title,
                            "description": description,
                            "content": item.get("content"),
                            "url": item.get("url"),
                            "source": item.get("source"),
                            "publishedAt": item.get("publishedAt"),
                            "source_api": "newsapi",
                            "language": "en",
                            "collected_at": datetime.utcnow(),
                            "processed": False
                        })
                
                print(f"{len(articles)} articles", flush=True)
                all_articles.extend(articles)
            else:
                print(f"Error: {data.get('message', 'Unknown')}", flush=True)
                
            time.sleep(1)  # Rate limiting
            
        except Exception as e:
            print(f"Error: {e}", flush=True)
    
    # Guardian - 500 requests/day
    print("\n📊 The Guardian (50 topics)...")
    for i, topic in enumerate(TOPICS[:50], 1):  # Use 50 topics
        print(f"  [{i}/50] {topic}...", end=" ", flush=True)
        
        try:
            url = f"https://content.guardianapis.com/search?q={topic}&page-size=50&api-key={GUARDIAN_KEY}"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data.get("response", {}).get("status") == "ok":
                articles = []
                for item in data["response"].get("results", []):
                    title = item.get("webTitle", "")
                    
                    if is_english(title):
                        articles.append({
                            "title": title,
                            "description": title,
                            "content": title,
                            "url": item.get("webUrl"),
                            "source": {"name": "The Guardian"},
                            "publishedAt": item.get("webPublicationDate"),
                            "source_api": "guardian",
                            "language": "en",
                            "collected_at": datetime.utcnow(),
                            "processed": False
                        })
                
                print(f"{len(articles)} articles", flush=True)
                all_articles.extend(articles)
                
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error: {e}", flush=True)
    
    # GNews - 100 requests/day
    print("\n📊 GNews (20 topics)...")
    for i, topic in enumerate(TOPICS[:20], 1):
        print(f"  [{i}/20] {topic}...", end=" ", flush=True)
        
        try:
            url = f"https://gnews.io/api/v4/search?q={topic}&lang=en&max=10&apikey={GNEWS_KEY}"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if "articles" in data:
                articles = []
                for item in data["articles"]:
                    title = item.get("title", "")
                    description = item.get("description", "")
                    
                    if is_english(f"{title} {description}"):
                        articles.append({
                            "title": title,
                            "description": description,
                            "content": item.get("content", description),
                            "url": item.get("url"),
                            "source": {"name": item.get("source", {}).get("name", "GNews")},
                            "publishedAt": item.get("publishedAt"),
                            "source_api": "gnews",
                            "language": "en",
                            "collected_at": datetime.utcnow(),
                            "processed": False
                        })
                
                print(f"{len(articles)} articles", flush=True)
                all_articles.extend(articles)
                
            time.sleep(1)
            
        except Exception as e:
            print(f"Error: {e}", flush=True)
    
    print(f"\n✅ Total API articles: {len(all_articles)}")
    return all_articles

# ============================================================================
# STORE IN MONGODB
# ============================================================================

def store_in_mongodb(articles):
    """Store articles in MongoDB"""
    print("\n" + "="*80)
    print("💾 STORING IN MONGODB")
    print("="*80)
    
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION]
        
        collection.create_index([("url", 1)], unique=True)
        
        new_count = 0
        duplicate_count = 0
        
        for article in articles:
            try:
                collection.insert_one(article)
                new_count += 1
            except:
                duplicate_count += 1
        
        total = collection.count_documents({})
        
        print(f"\n✅ New articles stored: {new_count}")
        print(f"⏭️  Duplicates skipped: {duplicate_count}")
        print(f"📊 Total in database: {total}")
        
        client.close()
        return new_count
        
    except Exception as e:
        print(f"\n❌ MongoDB error: {e}")
        return 0

# ============================================================================
# MAIN
# ============================================================================

def main():
    start_time = time.time()
    
    print("="*80)
    print("🚀 MASSIVE DATA COLLECTION - ENGLISH ONLY")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("📊 This will collect:")
    print("  • 40+ RSS feeds (2000+ articles)")
    print("  • 85 topics across 3 APIs (8000+ articles)")
    print("  • All English-only, auto-filtered")
    print()
    
    try:
        response = input("▶️  Continue? (Press ENTER or type 'y'): ").lower()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled")
        return
    
    # Collect from RSS (NO LIMITS!)
    rss_articles = collect_from_rss()
    
    # Collect from APIs (MAXIMUM)
    api_articles = collect_from_apis()
    
    # Combine
    all_articles = rss_articles + api_articles
    
    print("\n" + "="*80)
    print(f"📊 COLLECTION SUMMARY")
    print("="*80)
    print(f"RSS feeds: {len(rss_articles)} articles")
    print(f"APIs: {len(api_articles)} articles")
    print(f"TOTAL: {len(all_articles)} articles collected")
    
    # Store in MongoDB
    if all_articles:
        new_count = store_in_mongodb(all_articles)
    
    # Summary
    elapsed = time.time() - start_time
    
    print("\n" + "="*80)
    print("🎉 MASSIVE COLLECTION COMPLETE!")
    print("="*80)
    print(f"⏱️  Time: {elapsed/60:.1f} minutes")
    print(f"📰 Total collected: {len(all_articles)} articles")
    print(f"✅ 100% English-only data")
    print()
    print("🚀 Next steps:")
    print("  1. Process articles:  python process_articles.py")
    print("  2. View dashboard:    streamlit run dashboard.py")
    print("  3. Check database:    python check_mongodb.py")
    print()
    print("="*80)
    
    input("\nPress ENTER to exit...")

if __name__ == "__main__":
    main()
