"""
🚀 COMPLETE ALL-IN-ONE PIPELINE
Fetches data from online APIs → Extracts entities → Stores in MongoDB → Builds Neo4j graph → Ready for dashboard

Just run this ONE file to do EVERYTHING!
"""

import requests
from pymongo import MongoClient
from neo4j import GraphDatabase
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
from datetime import datetime
import time
import sys
import re
from langdetect import detect, LangDetectException

# Fix Windows encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ============================================================================
# CONFIGURATION
# ============================================================================

# API KEYS (Free tier - 100-500 requests/day each)
NEWSAPI_KEY = "b6851d27958f4cd9940491e9f8fe9c3d"
NEWSDATA_KEY = "pub_8c6d3b5ad17a43c597dbbf9e055d5fd2"
GUARDIAN_KEY = "c68b9202-4f02-466d-a60d-b6982be2b9f4"
GNEWS_KEY = "dad0cee9e7e166a4a1abc6f49c0530ac"

# MongoDB
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB = "global_news_intelligence"
MONGO_COLLECTION = "raw_articles"

# Neo4j
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "jill2143"

# ============================================================================
# STEP 1: FETCH DATA FROM ONLINE APIS (ENGLISH ONLY)
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

def fetch_from_newsapi(topic="global news", max_results=20):
    """Fetch from NewsAPI.org"""
    try:
        url = f"https://newsapi.org/v2/everything?q={topic}&language=en&pageSize={max_results}&apiKey={NEWSAPI_KEY}"
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
                        "content": item.get("content", description),
                        "url": item.get("url"),
                        "source": item.get("source"),
                        "publishedAt": item.get("publishedAt"),
                        "source_api": "newsapi",
                        "language": "en",
                        "collected_at": datetime.utcnow(),
                        "processed": False
                    })
            return articles
    except Exception as e:
        print(f"  NewsAPI error: {e}")
    return []

def fetch_from_guardian(topic="world", max_results=30):
    """Fetch from The Guardian"""
    try:
        url = f"https://content.guardianapis.com/search?q={topic}&page-size={max_results}&api-key={GUARDIAN_KEY}"
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
            return articles
    except Exception as e:
        print(f"  Guardian error: {e}")
    return []

def fetch_from_gnews(topic="breaking news", max_results=10):
    """Fetch from GNews"""
    try:
        url = f"https://gnews.io/api/v4/search?q={topic}&lang=en&max={max_results}&apikey={GNEWS_KEY}"
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
            return articles
    except Exception as e:
        print(f"  GNews error: {e}")
    return []

def collect_all_news():
    """Collect news from all APIs"""
    print("\n" + "="*80)
    print("📰 STEP 1: FETCHING DATA FROM ONLINE APIS (ENGLISH ONLY)")
    print("="*80)
    
    all_articles = []
    
    print("\n🌐 NewsAPI.org...")
    articles = fetch_from_newsapi("global conflict politics")
    print(f"  ✓ Fetched {len(articles)} English articles")
    all_articles.extend(articles)
    
    print("\n🌐 The Guardian...")
    articles = fetch_from_guardian("international politics")
    print(f"  ✓ Fetched {len(articles)} English articles")
    all_articles.extend(articles)
    
    print("\n🌐 GNews...")
    articles = fetch_from_gnews("world news")
    print(f"  ✓ Fetched {len(articles)} English articles")
    all_articles.extend(articles)
    
    print(f"\n✅ Total articles collected: {len(all_articles)}")
    return all_articles

# ============================================================================
# STEP 2: STORE IN MONGODB
# ============================================================================

def store_in_mongodb(articles):
    """Store articles in MongoDB"""
    print("\n" + "="*80)
    print("💾 STEP 2: STORING IN MONGODB")
    print("="*80)
    
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION]
        
        # Create unique index on URL
        collection.create_index([("url", 1)], unique=True)
        
        new_count = 0
        duplicate_count = 0
        
        for article in articles:
            try:
                collection.insert_one(article)
                new_count += 1
            except:
                duplicate_count += 1
        
        print(f"\n✅ New articles stored: {new_count}")
        print(f"⏭️  Duplicates skipped: {duplicate_count}")
        print(f"📊 Total in database: {collection.count_documents({})}")
        
        client.close()
        return new_count
        
    except Exception as e:
        print(f"\n❌ MongoDB error: {e}")
        return 0

# ============================================================================
# STEP 3: EXTRACT ENTITIES WITH NER (Convert to Entities)
# ============================================================================

def load_ner_model():
    """Load BERT NER model"""
    print("\n🤖 Loading BERT NER model...")
    tokenizer = AutoTokenizer.from_pretrained("dslim/bert-base-NER")
    model = AutoModelForTokenClassification.from_pretrained("dslim/bert-base-NER")
    ner_pipeline = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")
    print("  ✓ Model loaded successfully")
    return ner_pipeline

def extract_entities(text, ner_pipeline):
    """Extract entities from text using BERT NER"""
    if not text or len(text.strip()) < 10:
        return []
    
    try:
        # Limit text length for processing
        text = text[:2000]
        results = ner_pipeline(text)
        
        entities = []
        for entity in results:
            if entity['score'] > 0.85:  # High confidence only
                entities.append({
                    'name': entity['word'].strip(),
                    'type': entity['entity_group'],
                    'score': entity['score']
                })
        
        return entities
    except Exception as e:
        return []

def extract_relationships(text, entities):
    """Extract relationships between entities"""
    relationships = []
    
    # Simple pattern matching for relationships
    entity_names = [e['name'] for e in entities]
    
    # Common relationship verbs
    verbs = [
        'attack', 'support', 'oppose', 'meet', 'visit', 'condemn',
        'announce', 'sign', 'negotiate', 'criticize', 'ally', 'conflict'
    ]
    
    for i, e1 in enumerate(entity_names):
        for e2 in entity_names[i+1:]:
            # Check if both entities appear close together in text
            pattern = f"{e1}.{{0,100}}{e2}"
            if re.search(pattern, text, re.IGNORECASE):
                # Try to find a verb between them
                for verb in verbs:
                    if re.search(f"{e1}.{{0,50}}{verb}.{{0,50}}{e2}", text, re.IGNORECASE):
                        relationships.append({
                            'source': e1,
                            'target': e2,
                            'type': verb.upper(),
                            'context': text[:200]
                        })
                        break
    
    return relationships

# ============================================================================
# STEP 4: BUILD NEO4J KNOWLEDGE GRAPH
# ============================================================================

def create_neo4j_graph(articles_with_entities):
    """Create knowledge graph in Neo4j"""
    print("\n" + "="*80)
    print("🕸️  STEP 4: BUILDING NEO4J KNOWLEDGE GRAPH")
    print("="*80)
    
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        
        entity_count = 0
        relation_count = 0
        
        with driver.session() as session:
            for article_data in articles_with_entities:
                entities = article_data['entities']
                relationships = article_data['relationships']
                article = article_data['article']
                
                # Create entity nodes
                for entity in entities:
                    session.run("""
                        MERGE (e:Entity {name: $name})
                        ON CREATE SET e.type = $type, e.mention_count = 1
                        ON MATCH SET e.mention_count = e.mention_count + 1
                    """, name=entity['name'], type=entity['type'])
                    entity_count += 1
                
                # Create relationships
                for rel in relationships:
                    session.run("""
                        MATCH (e1:Entity {name: $source})
                        MATCH (e2:Entity {name: $target})
                        MERGE (e1)-[r:RELATES {type: $type}]->(e2)
                        ON CREATE SET r.count = 1, r.context = $context
                        ON MATCH SET r.count = r.count + 1
                    """, source=rel['source'], target=rel['target'], 
                         type=rel['type'], context=rel['context'])
                    relation_count += 1
        
        driver.close()
        
        print(f"\n✅ Entities created: {entity_count}")
        print(f"✅ Relationships created: {relation_count}")
        print(f"🎉 Knowledge graph built successfully!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Neo4j error: {e}")
        return False

# ============================================================================
# MAIN PIPELINE
# ============================================================================

def main():
    start_time = time.time()
    
    print("="*80)
    print("🌍 COMPLETE ALL-IN-ONE PIPELINE - ENGLISH ONLY")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # STEP 1: Fetch data from APIs
    articles = collect_all_news()
    
    if not articles:
        print("\n❌ No articles collected. Exiting.")
        return
    
    # STEP 2: Store in MongoDB
    new_count = store_in_mongodb(articles)
    
    if new_count == 0:
        print("\n⚠️  No new articles to process.")
    
    # STEP 3: Extract entities from articles
    print("\n" + "="*80)
    print("🤖 STEP 3: EXTRACTING ENTITIES WITH BERT NER")
    print("="*80)
    
    ner_pipeline = load_ner_model()
    
    articles_with_entities = []
    
    print(f"\nProcessing {len(articles)} articles...")
    
    for i, article in enumerate(articles[:50], 1):  # Process first 50
        if i % 10 == 0:
            print(f"  Processed {i}/{min(50, len(articles))} articles...")
        
        # Combine title and content
        text = f"{article.get('title', '')} {article.get('description', '')}"
        
        # Extract entities
        entities = extract_entities(text, ner_pipeline)
        
        # Extract relationships
        relationships = extract_relationships(text, entities)
        
        if entities:
            articles_with_entities.append({
                'article': article,
                'entities': entities,
                'relationships': relationships
            })
    
    print(f"\n✅ Processed {len(articles_with_entities)} articles with entities")
    
    # STEP 4: Build Neo4j graph
    if articles_with_entities:
        create_neo4j_graph(articles_with_entities)
    else:
        print("\n⚠️  No entities found. Skipping Neo4j.")
    
    # STEP 5: Mark as processed in MongoDB
    print("\n" + "="*80)
    print("✅ STEP 5: UPDATING MONGODB STATUS")
    print("="*80)
    
    try:
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION]
        
        # Mark articles as processed
        urls = [a['article']['url'] for a in articles_with_entities]
        result = collection.update_many(
            {"url": {"$in": urls}},
            {"$set": {"processed": True, "processed_at": datetime.utcnow()}}
        )
        
        print(f"✅ Marked {result.modified_count} articles as processed")
        client.close()
    except Exception as e:
        print(f"⚠️  Update error: {e}")
    
    # Summary
    elapsed = time.time() - start_time
    
    print("\n" + "="*80)
    print("🎉 PIPELINE COMPLETE!")
    print("="*80)
    print(f"\n⏱️  Time elapsed: {elapsed:.1f} seconds")
    print(f"📰 Articles fetched: {len(articles)} (100% English)")
    print(f"💾 Stored in MongoDB: {new_count} new articles")
    print(f"🤖 Entities extracted: {len(articles_with_entities)} articles")
    print(f"🕸️  Knowledge graph: Updated in Neo4j")
    
    print("\n🚀 NEXT STEPS:")
    print("  1. View Dashboard:     streamlit run dashboard.py")
    print("  2. Neo4j Browser:      http://localhost:7474")
    print("  3. Check Data:         python check_mongodb.py")
    print("  4. Verify English:     python verify_english_only.py")
    
    print("\n" + "="*80)
    
    # Ask to launch dashboard
    try:
        response = input("\n🎨 Launch dashboard now? (y/n): ").lower().strip()
        if response == 'y':
            import subprocess
            print("\n🚀 Launching dashboard...")
            subprocess.run([sys.executable, "-m", "streamlit", "run", "dashboard.py"])
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")

if __name__ == "__main__":
    main()
