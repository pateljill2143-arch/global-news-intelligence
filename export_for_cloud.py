"""
Export knowledge graph data for Streamlit Cloud deployment
"""

from neo4j import GraphDatabase
from pymongo import MongoClient
import json
from datetime import datetime

print("Exporting data for cloud deployment...")

# Connect to databases
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "jill2143"))
mongo_client = MongoClient("mongodb://localhost:27017/")
articles_collection = mongo_client["global_news_intelligence"]["raw_articles"]

# Export data
export_data = {
    "exported_at": datetime.now().isoformat(),
    "entities": [],
    "relationships": [],
    "conflicts": [],
    "cooperations": [],
    "articles": [],
    "stats": {}
}

with driver.session() as session:
    # Get all entities with mentions
    result = session.run("""
        MATCH (e:Entity)
        RETURN e.name as name, e.mention_count as mentions
        ORDER BY e.mention_count DESC
    """)
    export_data["entities"] = [{"name": r["name"], "mentions": r["mentions"]} for r in result]
    
    # Get conflicts
    result = session.run("""
        MATCH (e1:Entity)-[r:ATTACKS|WAR_WITH|STRIKES]->(e2:Entity)
        RETURN e1.name as source, type(r) as relation, e2.name as target, 
               r.date as date, r.sentiment as sentiment
        ORDER BY r.date DESC
        LIMIT 100
    """)
    export_data["conflicts"] = [
        {
            "source": r["source"],
            "relation": r["relation"],
            "target": r["target"],
            "date": str(r["date"])[:10] if r["date"] else "N/A",
            "sentiment": r["sentiment"]
        }
        for r in result
    ]
    
    # Get cooperations
    result = session.run("""
        MATCH (e1:Entity)-[r:TRADES_WITH|ALLIED_WITH|SUPPORTS|HELPS]->(e2:Entity)
        RETURN e1.name as source, type(r) as relation, e2.name as target,
               r.date as date, r.sentiment as sentiment
        ORDER BY r.date DESC
        LIMIT 100
    """)
    export_data["cooperations"] = [
        {
            "source": r["source"],
            "relation": r["relation"],
            "target": r["target"],
            "date": str(r["date"])[:10] if r["date"] else "N/A",
            "sentiment": r["sentiment"]
        }
        for r in result
    ]
    
    # Get all relationships for stats
    result = session.run("""
        MATCH ()-[r]->()
        RETURN type(r) as relation_type, count(*) as count
        ORDER BY count DESC
    """)
    export_data["relationship_types"] = [
        {"type": r["relation_type"], "count": r["count"]}
        for r in result
    ]
    
    # Get stats
    entity_count = session.run("MATCH (e:Entity) RETURN count(e) as count").single()["count"]
    rel_count = session.run("MATCH ()-[r]->() RETURN count(r) as count").single()["count"]
    
    export_data["stats"] = {
        "total_entities": entity_count,
        "total_relationships": rel_count
    }

# Get latest articles from MongoDB
articles = articles_collection.find({"processed": True}).sort([("collected_at", -1)]).limit(50)
export_data["articles"] = [
    {
        "title": a.get("title", ""),
        "source": a.get("source", {}).get("name", "Unknown"),
        "category": a.get("category", "N/A"),
        "date": str(a.get("publishedAt", ""))[:10]
    }
    for a in articles
]

export_data["stats"]["total_articles"] = articles_collection.count_documents({})
export_data["stats"]["unprocessed"] = articles_collection.count_documents({"processed": False})

# Save to JSON
with open("graph_data_export.json", "w", encoding='utf-8') as f:
    json.dump(export_data, f, indent=2, ensure_ascii=False)

print(f"✓ Exported {len(export_data['entities'])} entities")
print(f"✓ Exported {len(export_data['conflicts'])} conflicts")
print(f"✓ Exported {len(export_data['cooperations'])} cooperations")
print(f"✓ Exported {len(export_data['articles'])} articles")
print(f"\n✓ Data saved to: graph_data_export.json")
print(f"\nYou can now deploy dashboard_cloud.py to Streamlit Cloud!")

driver.close()
mongo_client.close()
