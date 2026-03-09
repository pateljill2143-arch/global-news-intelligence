"""
📍 DATA STORAGE LOCATIONS - Where Your Data is Stored
"""

print("""
================================================================================
    WHERE YOUR DATA IS STORED
================================================================================

Your data is stored in TWO separate databases:


╔═══════════════════════════════════════════════════════════════════════════╗
║ 1. MONGODB - RAW ARTICLES STORAGE                                        ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                           ║
║ 📍 Location:                                                              ║
║    localhost:27017                                                        ║
║    Database: global_news_intelligence                                     ║
║    Collection: raw_articles                                               ║
║                                                                           ║
║ 💾 What's stored here:                                                    ║
║    • All collected news articles (title, description, content)            ║
║    • Article metadata (URL, source, published date)                       ║
║    • Collection timestamp                                                 ║
║    • Processing status (processed: true/false)                            ║
║    • Language info (language: "en")                                       ║
║                                                                           ║
║ 📂 Physical location (default):                                           ║
║    C:\Program Files\MongoDB\Server\7.0\data\                              ║
║    (or wherever you installed MongoDB)                                    ║
║                                                                           ║
║ 🔍 How to view:                                                           ║
║    1. MongoDB Compass (GUI):                                              ║
║       • Open MongoDB Compass                                              ║
║       • Connect to: mongodb://localhost:27017                             ║
║       • Browse: global_news_intelligence > raw_articles                   ║
║                                                                           ║
║    2. Command line:                                                       ║
║       python check_mongodb.py                                             ║
║                                                                           ║
║    3. Python script:                                                      ║
║       from pymongo import MongoClient                                     ║
║       client = MongoClient("mongodb://localhost:27017/")                  ║
║       db = client["global_news_intelligence"]                             ║
║       articles = db["raw_articles"]                                       ║
║       print(articles.count_documents({}))                                  ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝


╔═══════════════════════════════════════════════════════════════════════════╗
║ 2. NEO4J - KNOWLEDGE GRAPH STORAGE                                       ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                           ║
║ 📍 Location:                                                              ║
║    bolt://localhost:7687                                                  ║
║    Web Interface: http://localhost:7474                                   ║
║    Database: neo4j                                                        ║
║                                                                           ║
║ 💾 What's stored here:                                                    ║
║    • Entity nodes (people, organizations, locations)                      ║
║    • Relationships between entities                                       ║
║    • Relationship metadata (type, count, context)                         ║
║    • Entity mention counts                                                ║
║                                                                           ║
║ 📂 Physical location (default):                                           ║
║    C:\Users\<YourUsername>\.Neo4jDesktop\relate-data\dbmss\              ║
║    (or your Neo4j installation directory)                                 ║
║                                                                           ║
║ 🔍 How to view:                                                           ║
║    1. Neo4j Browser (GUI):                                                ║
║       • Open browser: http://localhost:7474                               ║
║       • Login: neo4j / jill2143                                           ║
║       • Run query: MATCH (n) RETURN n LIMIT 100                           ║
║                                                                           ║
║    2. Command line:                                                       ║
║       python query_neo4j.py                                               ║
║                                                                           ║
║    3. Python script:                                                      ║
║       from neo4j import GraphDatabase                                     ║
║       driver = GraphDatabase.driver(                                      ║
║           "bolt://localhost:7687",                                        ║
║           auth=("neo4j", "jill2143")                                      ║
║       )                                                                   ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝


================================================================================
📊 YOUR CURRENT DATA
================================================================================
""")

# Check MongoDB
try:
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
    db = client["global_news_intelligence"]
    collection = db["raw_articles"]
    
    total = collection.count_documents({})
    processed = collection.count_documents({"processed": True})
    unprocessed = collection.count_documents({"processed": False})
    
    print("📦 MONGODB:")
    print(f"   Total articles: {total:,}")
    print(f"   Processed: {processed:,}")
    print(f"   Unprocessed: {unprocessed:,}")
    
    # Get latest article
    latest = collection.find_one(sort=[("collected_at", -1)])
    if latest:
        print(f"   Latest: {latest.get('title', 'N/A')[:60]}...")
    
    client.close()
    
except Exception as e:
    print(f"📦 MONGODB: Not accessible ({e})")

print()

# Check Neo4j
try:
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "jill2143"))
    
    with driver.session() as session:
        # Count entities
        result = session.run("MATCH (n:Entity) RETURN count(n) as count")
        entity_count = result.single()["count"]
        
        # Count relationships
        result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
        rel_count = result.single()["count"]
    
    print("🕸️  NEO4J:")
    print(f"   Total entities: {entity_count:,}")
    print(f"   Total relationships: {rel_count:,}")
    
    driver.close()
    
except Exception as e:
    print(f"🕸️  NEO4J: Not accessible ({e})")

print("""

================================================================================
🔧 HOW TO ACCESS YOUR DATA
================================================================================

VIEW RAW ARTICLES:
------------------
1. MongoDB Compass (best for browsing):
   - Download: https://www.mongodb.com/try/download/compass
   - Connect to: mongodb://localhost:27017
   - Navigate to: global_news_intelligence > raw_articles

2. Command line:
   python check_mongodb.py

3. Export to file:
   mongoexport --db=global_news_intelligence --collection=raw_articles --out=articles.json


VIEW KNOWLEDGE GRAPH:
---------------------
1. Neo4j Browser (best for visualization):
   - Open: http://localhost:7474
   - Login: neo4j / jill2143
   
   Sample queries:
   • View all: MATCH (n)-[r]->(m) RETURN n,r,m LIMIT 100
   • Top entities: MATCH (n:Entity) RETURN n ORDER BY n.mention_count DESC LIMIT 20
   • Find connections: MATCH (n:Entity {name: "USA"})-[r]-(m) RETURN n,r,m

2. Command line:
   python query_neo4j.py
   python query_triples.py

3. Dashboard:
   streamlit run dashboard.py


BACKUP YOUR DATA:
-----------------
MongoDB:
  mongodump --db=global_news_intelligence --out=backup/

Neo4j:
  1. Open Neo4j Desktop
  2. Click on your database
  3. Click "..." > "Create dump"


================================================================================
💾 DATA STORAGE SIZE
================================================================================

Typical storage per 10,000 articles:

MongoDB (Raw articles):
  • ~100-200 MB per 10,000 articles
  • With full content: ~500 MB - 1 GB

Neo4j (Knowledge graph):
  • ~50-100 MB per 10,000 articles processed
  • Grows with relationships

Expected total:
  • 10,000 articles: ~300-500 MB
  • 100,000 articles: ~3-5 GB
  • 1,000,000 articles: ~30-50 GB


================================================================================
🔍 QUICK CHECK COMMANDS
================================================================================

Check MongoDB:
  python check_mongodb.py

Check Neo4j:
  python query_neo4j.py

Check data freshness:
  python check_data_freshness.py

Verify all English:
  python verify_english_only.py


================================================================================
📍 SUMMARY
================================================================================

Your data is stored in TWO places:

1. 📦 MongoDB (localhost:27017)
   → Raw news articles
   → Database: global_news_intelligence
   → Collection: raw_articles
   → View with: MongoDB Compass or python check_mongodb.py

2. 🕸️  Neo4j (localhost:7474)
   → Knowledge graph (entities + relationships)
   → Database: neo4j
   → View with: http://localhost:7474 or dashboard

Both are stored LOCALLY on your computer.
Both are private and secure.
Both can be backed up and exported.

================================================================================
""")

input("\nPress ENTER to exit...")
