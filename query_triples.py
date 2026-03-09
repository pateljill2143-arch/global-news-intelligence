from neo4j import GraphDatabase
from datetime import datetime, timedelta

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "jill2143"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

print("=" * 80)
print("KNOWLEDGE GRAPH - HISTORICAL & CURRENT CONNECTIONS")
print("=" * 80)

with driver.session() as session:
    
    # Statistics
    print("\n📊 DATABASE STATISTICS:\n")
    result = session.run("""
        MATCH (n:Entity)
        RETURN count(n) as TotalEntities
    """)
    print(f"Total Entities: {result.single()['TotalEntities']}")
    
    result = session.run("""
        MATCH ()-[r]->()
        RETURN count(r) as TotalRelationships
    """)
    print(f"Total Relationships: {result.single()['TotalRelationships']}")
    
    # Query 1: Show all triples with full metadata
    print("\n📊 SAMPLE TRIPLES WITH METADATA:\n")
    result = session.run("""
        MATCH (n:Entity)-[r]->(m:Entity)
        RETURN n.name as Subject, 
               type(r) as Predicate, 
               m.name as Object,
               r.date as Date,
               r.source as Source,
               r.sentiment as Sentiment
        ORDER BY r.timestamp DESC
        LIMIT 20
    """)
    
    for record in result:
        print(f"Triple: {record['Subject']} → [{record['Predicate']}] → {record['Object']}")
        print(f"  📅 Date: {record['Date']}")
        print(f"  📰 Source: {record['Source']}")
        print(f"  😊 Sentiment: {record['Sentiment']}")
        print()
    
    # Most mentioned entities (historical + current)
    print("\n⭐ MOST MENTIONED ENTITIES (OVER TIME):\n")
    result = session.run("""
        MATCH (n:Entity)
        WHERE n.mention_count IS NOT NULL
        RETURN n.name as Entity, 
               n.mention_count as Mentions,
               n.first_seen as FirstSeen,
               n.last_seen as LastSeen
        ORDER BY Mentions DESC
        LIMIT 15
    """)
    
    for record in result:
        print(f"  {record['Entity']}: {record['Mentions']} mentions")
    
    # Find connections between entities
    print("\n\n🔗 ENTITY CONNECTION PATHS (2-hop connections):\n")
    result = session.run("""
        MATCH path = (a:Entity)-[r1]->(b:Entity)-[r2]->(c:Entity)
        WHERE a <> c
        RETURN DISTINCT a.name, type(r1), b.name, type(r2), c.name
        LIMIT 10
    """)
    
    for record in result:
        print(f"  {record['a.name']} → {record['type(r1)']} → {record['b.name']} → {record['type(r2)']} → {record['c.name']}")
    
    # Negative relationships (conflicts, attacks, etc.)
    print("\n\n🔴 CONFLICTS & TENSIONS:\n")
    result = session.run("""
        MATCH (n:Entity)-[r]->(m:Entity)
        WHERE r.sentiment = 'negative'
        RETURN n.name, type(r) as relation, m.name, r.date
        ORDER BY r.date DESC
        LIMIT 15
    """)
    
    for record in result:
        date_str = record['r.date'][:10] if record['r.date'] else 'Unknown'
        print(f"⚔️  {record['n.name']} --[{record['relation']}]--> {record['m.name']} ({date_str})")
    
    # Positive relationships (cooperation, agreements, etc.)
    print("\n\n🟢 COOPERATION & AGREEMENTS:\n")
    result = session.run("""
        MATCH (n:Entity)-[r]->(m:Entity)
        WHERE r.sentiment = 'positive'
        RETURN n.name, type(r) as relation, m.name, r.date
        ORDER BY r.date DESC
        LIMIT 15
    """)
    
    for record in result:
        date_str = record['r.date'][:10] if record['r.date'] else 'Unknown'
        print(f"🤝 {record['n.name']} --[{record['relation']}]--> {record['m.name']} ({date_str})")
    
    # Group by relationship type
    print("\n\n📈 RELATIONSHIP TYPES DISTRIBUTION:\n")
    result = session.run("""
        MATCH ()-[r]->()
        RETURN type(r) as RelationType, count(r) as Count
        ORDER BY Count DESC
        LIMIT 20
    """)
    
    for record in result:
        print(f"  {record['RelationType']}: {record['Count']}")
    
    # Timeline view
    print("\n\n📅 TIMELINE OF EVENTS:\n")
    result = session.run("""
        MATCH (n:Entity)-[r]->(m:Entity)
        WHERE r.date IS NOT NULL
        RETURN n.name, type(r) as relation, m.name, r.date, r.source
        ORDER BY r.date DESC
        LIMIT 20
    """)
    
    for record in result:
        date_str = record['r.date'][:10] if record['r.date'] else 'Unknown'
        print(f"🕒 {date_str}: {record['n.name']} → {record['relation']} → {record['m.name']}")
        print(f"   Source: {record['r.source']}\n")

driver.close()
print("=" * 80)
print("✅ To keep adding data, run trans.py again anytime!")
print("=" * 80)

