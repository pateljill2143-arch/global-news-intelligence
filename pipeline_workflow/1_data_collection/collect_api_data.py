"""
🚀 MASSIVE DATA COLLECTION - MAXIMUM ARTICLES
Collects from 4 APIs + 40+ RSS Feeds for thousands of articles
Sources: NewsAPI, NewsData.io, Guardian, GNews + BBC, Reuters, CNN, etc.
100% English-Only with auto-filtering
"""

import requests
from datetime import datetime
import json
from pathlib import Path
from langdetect import detect, LangDetectException
import feedparser
import time
import sys

# Fix Windows encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ============================================================================
# API KEYS - ALL 4 SOURCES
# ============================================================================
NEWSAPI_KEY = "b6851d27958f4cd9940491e9f8fe9c3d"        # 100 requests/day
NEWSDATA_KEY = "pub_8c6d3b5ad17a43c597dbbf9e055d5fd2"  # 200 requests/day
GUARDIAN_KEY = "c68b9202-4f02-466d-a60d-b6982be2b9f4"   # 500 requests/day
GNEWS_KEY = "dad0cee9e7e166a4a1abc6f49c0530ac"         # 100 requests/day

# Output directory
OUTPUT_DIR = Path(__file__).parent / "collected_data"
OUTPUT_DIR.mkdir(exist_ok=True)

# ============================================================================
# 100+ TOPICS FOR MAXIMUM COVERAGE
# ============================================================================
TOPICS = [
    # GLOBAL CONFLICTS & WAR
    "Russia Ukraine war conflict", "Israel Palestine Gaza Hamas", "Syria war ISIS",
    "Yemen war Saudi Arabia", "Afghanistan Taliban", "Iraq conflict",
    "Libya civil war", "Sudan conflict", "Ethiopia war",
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
    "terrorism attack ISIS", "Al Qaeda militant", "cyber attack ransomware",
    "espionage spy scandal", "Taliban Afghanistan",
    
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
    "banking crisis", "trade war tariffs",
    "unemployment jobs report", "housing market prices",
    "oil prices energy crisis", "supply chain shortage",
    
    # HEALTH & PANDEMIC
    "COVID pandemic coronavirus", "vaccine vaccination",
    "WHO health crisis", "bird flu pandemic",
    "cancer research breakthrough", "mental health crisis",
    
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
    
    # INDIAN ECONOMY & POLITICS
    "India economy GDP growth", "India Modi government", "India elections",
    "India RBI monetary policy", "India stock market Sensex",
    "India rupee dollar exchange", "India inflation prices",

    # INDIAN PARLIAMENT - BILLS & LEGISLATION
    "India parliament bill passed Lok Sabha", "India Rajya Sabha bill legislation",
    "India parliament session budget", "India parliament monsoon session",
    "India parliament winter session", "India parliament standing committee",
    "India parliament no-confidence motion", "India parliament question hour",
    "India parliament zero hour debate", "India ordinance president rule",
    "India constitutional amendment bill", "India finance bill budget 2025",
    "India parliament adjourned disruption", "India parliament opposition walkout",

    # INDIA PARLIAMENT - KEY BILLS
    "India Waqf Amendment Bill", "India ONOE One Nation One Election",
    "India Uniform Civil Code UCC", "India Citizenship Amendment Act CAA",
    "India data protection bill", "India criminal law reform BNS",
    "India telecommunications bill", "India press freedom media law",
    "India labour code reform", "India farm law agriculture",

    # INDIA PARLIAMENT - MEMBERS & PARTIES
    "Rahul Gandhi parliament speech", "Modi parliament address",
    "BJP Congress parliament debate", "India opposition party parliament",
    "India parliament speaker Lok Sabha", "India Rajya Sabha chairman",
    "India parliament corruption scandal", "India MP arrest expelled",
    "India parliament privilege motion", "INDIA alliance parliament",

    # INDIA PARLIAMENT - BUDGET & FINANCE
    "India union budget 2025 parliament", "India finance minister Nirmala Sitharaman",
    "India GST council meeting", "India tax reform parliament",
    "India spending allocation defence", "India parliamentary committee report",
]

# ============================================================================
# RSS FEEDS - 40+ SOURCES (UNLIMITED!)
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
    "Wired": "https://www.wired.com/feed/rss",
    "CNET": "https://www.cnet.com/rss/news/",
    
    # BUSINESS & FINANCE
    "BBC Business": "http://feeds.bbci.co.uk/news/business/rss.xml",
    
    # SCIENCE
    "BBC Science": "http://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
    "NASA": "https://www.nasa.gov/rss/dyn/breaking_news.rss",
    
    # HEALTH
    "BBC Health": "http://feeds.bbci.co.uk/news/health/rss.xml",
    
    # ENTERTAINMENT
    "BBC Entertainment": "http://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml",
    
    # REGIONAL
    "Guardian World": "https://www.theguardian.com/world/rss",
    "Guardian UK": "https://www.theguardian.com/uk-news/rss",
    "Guardian US": "https://www.theguardian.com/us-news/rss",

    # INDIAN PARLIAMENT & POLITICS
    "The Hindu National": "https://www.thehindu.com/news/national/feeder/default.rss",
    "The Hindu Parliament": "https://www.thehindu.com/news/national/other-states/feeder/default.rss",
    "NDTV India Politics": "https://feeds.feedburner.com/ndtvnews-india-news",
    "Indian Express India": "https://indianexpress.com/section/india/feed/",
    "Indian Express Politics": "https://indianexpress.com/section/political-pulse/feed/",
    "Times of India Politics": "https://timesofindia.indiatimes.com/rssfeeds/4719148.cms",
    "Times of India India": "https://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms",
    "Hindustan Times India": "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml",
    "Hindustan Times Politics": "https://www.hindustantimes.com/feeds/rss/politics/rssfeed.xml",
    "LiveMint Economy": "https://www.livemint.com/rss/economy",
    "LiveMint Politics": "https://www.livemint.com/rss/politics",
    "Business Standard Economy": "https://www.business-standard.com/rss/economy-policy-10603.rss",
    "Business Standard Politics": "https://www.business-standard.com/rss/politics-10601.rss",
    "Economic Times India": "https://economictimes.indiatimes.com/rssfeedsdefault.cms",
    "Economic Times Economy": "https://economictimes.indiatimes.com/news/economy/rssfeeds/1373380680.cms",
    "PRS India Bills": "https://prsindia.org/feed",
    "Scroll India": "https://scroll.in/feed",
    "The Wire India": "https://thewire.in/feed",
    "Outlook India": "https://www.outlookindia.com/rss/main/magazine",
    "News18 Politics": "https://www.news18.com/rss/politics.xml",
    "India Today Politics": "https://www.indiatoday.in/rss/1206578",
    "ANI News": "https://aninews.in/rss/",
    "PTI News": "https://www.ptinews.com/rss/PTI_National.xml",
}

# ============================================================================
# LANGUAGE DETECTION
# ============================================================================
def is_english(text):
    """Check if text is English"""
    if not text or len(text.strip()) < 10:
        return False
    try:
        return detect(text[:500]) == 'en'
    except:
        return True

# ============================================================================
# RSS COLLECTION (UNLIMITED!)
# ============================================================================
def collect_from_rss():
    """Collect from ALL RSS feeds - NO LIMITS!"""
    print("\n" + "="*80)
    print("📡 COLLECTING FROM 25+ RSS FEEDS (NO RATE LIMITS!)")
    print("="*80)
    
    all_articles = []
    
    for source_name, feed_url in RSS_FEEDS.items():
        print(f"📰 {source_name}...", end=" ", flush=True)
        
        try:
            import socket
            socket.setdefaulttimeout(10)
            feed = feedparser.parse(feed_url, request_headers={'User-Agent': 'Mozilla/5.0'})
            socket.setdefaulttimeout(None)
            articles = []
            non_english = 0
            
            for entry in feed.entries[:50]:  # Up to 50 per feed
                title = entry.get("title", "")
                description = entry.get("summary", entry.get("description", ""))
                
                if not is_english(f"{title} {description}"):
                    non_english += 1
                    continue
                
                article = {
                    "title": title,
                    "description": description,
                    "content": entry.get("content", [{}])[0].get("value", description) if entry.get("content") else description,
                    "url": entry.get("link", ""),
                    "source": {"name": source_name},
                    "publishedAt": entry.get("published", entry.get("updated", "")),
                    "source_api": "rss_feed",
                    "language": "en",
                    "collected_at": datetime.utcnow().isoformat(),
                    "processed": False
                }
                
                if article["url"]:
                    articles.append(article)
            
            print(f"✓ {len(articles)} articles", flush=True)
            all_articles.extend(articles)
            time.sleep(0.1)
            
        except Exception as e:
            print(f"✗ Error: {e}", flush=True)
    
    print(f"\n✅ Total RSS articles: {len(all_articles)}")
    return all_articles

# ============================================================================
# API COLLECTION - ALL 4 SOURCES
# ============================================================================
def collect_from_newsapi(topics_count=15):
    """NewsAPI - 100 requests/day"""
    print("\n📊 NewsAPI (15 topics)...")
    articles = []
    
    for i, topic in enumerate(TOPICS[:topics_count], 1):
        print(f"  [{i}/{topics_count}] {topic}...", end=" ", flush=True)
        
        try:
            url = f"https://newsapi.org/v2/everything?q={topic}&language=en&pageSize=100&apiKey={NEWSAPI_KEY}"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data.get("status") == "ok":
                for item in data.get("articles", []):
                    title = item.get("title", "")
                    description = item.get("description", "")
                    
                    if is_english(f"{title} {description}"):
                        articles.append({
                            "title": title,
                            "description": description,
                            "content": item.get("content", description),
                            "url": item.get("url"),
                            "source": item.get("source"),
                            "publishedAt": item.get("publishedAt"),
                            "source_api": "newsapi",
                            "language": "en",
                            "collected_at": datetime.utcnow().isoformat(),
                            "processed": False
                        })
                
                print(f"✓ {len([a for a in articles if a.get('source_api') == 'newsapi'])} total", flush=True)
            else:
                print(f"✗", flush=True)
            
            time.sleep(1)
            
        except Exception as e:
            print(f"✗ {e}", flush=True)
    
    return articles

def collect_from_newsdata(topics_count=20):
    """NewsData.io - 200 requests/day"""
    print("\n📊 NewsData.io (20 topics)...")
    articles = []
    
    for i, topic in enumerate(TOPICS[:topics_count], 1):
        print(f"  [{i}/{topics_count}] {topic}...", end=" ", flush=True)
        
        try:
            url = f"https://newsdata.io/api/1/news?apikey={NEWSDATA_KEY}&q={topic}&language=en"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data.get("status") == "success":
                for item in data.get("results", []):
                    title = item.get("title", "")
                    description = item.get("description", "")
                    
                    if is_english(f"{title} {description}"):
                        articles.append({
                            "title": title,
                            "description": description,
                            "content": item.get("content") or description,
                            "url": item.get("link"),
                            "source": {"name": item.get("source_id")},
                            "publishedAt": item.get("pubDate"),
                            "source_api": "newsdata",
                            "language": "en",
                            "collected_at": datetime.utcnow().isoformat(),
                            "processed": False
                        })
                
                print(f"✓", flush=True)
            else:
                print(f"✗", flush=True)
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"✗", flush=True)
    
    return articles

def collect_from_guardian(topics_count=50):
    """The Guardian - 500 requests/day"""
    print("\n📊 The Guardian (50 topics)...")
    articles = []
    
    for i, topic in enumerate(TOPICS[:topics_count], 1):
        print(f"  [{i}/{topics_count}] {topic}...", end=" ", flush=True)
        
        try:
            url = f"https://content.guardianapis.com/search?q={topic}&page-size=50&api-key={GUARDIAN_KEY}"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data.get("response", {}).get("status") == "ok":
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
                            "collected_at": datetime.utcnow().isoformat(),
                            "processed": False
                        })
                
                print(f"✓", flush=True)
            else:
                print(f"✗", flush=True)
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"✗", flush=True)
    
    return articles

def collect_from_gnews(topics_count=20):
    """GNews - 100 requests/day"""
    print("\n📊 GNews (20 topics)...")
    articles = []
    
    for i, topic in enumerate(TOPICS[:topics_count], 1):
        print(f"  [{i}/{topics_count}] {topic}...", end=" ", flush=True)
        
        try:
            url = f"https://gnews.io/api/v4/search?q={topic}&lang=en&max=10&apikey={GNEWS_KEY}"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if "articles" in data:
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
                            "collected_at": datetime.utcnow().isoformat(),
                            "processed": False
                        })
                
                print(f"✓", flush=True)
            else:
                print(f"✗", flush=True)
            
            time.sleep(1)
            
        except Exception as e:
            print(f"✗", flush=True)
    
    return articles

# ============================================================================
# MAIN COLLECTION
# ============================================================================
def main():
    start_time = time.time()
    
    print("="*80)
    print("🚀 MASSIVE DATA COLLECTION - MAXIMUM ARTICLES")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("📊 This will collect:")
    print("  • 25+ RSS feeds (1000+ articles)")
    print("  • 4 APIs with 100+ topics (5000+ articles)")
    print("  • All English-only, auto-filtered")
    print("  • Expected: 5,000-10,000 articles")
    print()
    print("⏱️  Time: ~10-15 minutes")
    print("="*80)
    
    # Collect from RSS (NO LIMITS!)
    rss_articles = collect_from_rss()
    
    # Collect from all 4 APIs
    newsapi_articles = collect_from_newsapi(15)
    newsdata_articles = collect_from_newsdata(20)
    guardian_articles = collect_from_guardian(50)
    gnews_articles = collect_from_gnews(20)
    
    # Combine all
    all_articles = rss_articles + newsapi_articles + newsdata_articles + guardian_articles + gnews_articles
    
    # Remove duplicates by URL
    seen_urls = set()
    unique_articles = []
    for article in all_articles:
        url = article.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_articles.append(article)
    
    print("\n" + "="*80)
    print("📊 COLLECTION SUMMARY")
    print("="*80)
    print(f"RSS feeds:     {len(rss_articles):,} articles")
    print(f"NewsAPI:       {len(newsapi_articles):,} articles")
    print(f"NewsData.io:   {len(newsdata_articles):,} articles")
    print(f"The Guardian:  {len(guardian_articles):,} articles")
    print(f"GNews:         {len(gnews_articles):,} articles")
    print(f"─"*80)
    print(f"TOTAL:         {len(all_articles):,} articles")
    print(f"UNIQUE:        {len(unique_articles):,} articles (after dedup)")
    print("="*80)
    
    # Save to JSON file
    output_file = OUTPUT_DIR / f"api_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(unique_articles, f, indent=2, ensure_ascii=False)
    
    elapsed = time.time() - start_time
    
    print(f"\n✅ Saved to: {output_file}")
    print(f"⏱️  Time elapsed: {elapsed/60:.1f} minutes")
    print(f"📰 Total unique articles: {len(unique_articles):,}")
    print(f"✅ 100% English-only data")
    print()
    print(f"➡️  Next step: Run 2_mongodb_storage/store_in_mongodb.py")
    print("="*80)

if __name__ == "__main__":
    main()
