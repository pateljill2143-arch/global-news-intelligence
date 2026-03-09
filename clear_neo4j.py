from neo4j import GraphDatabase

# -------------------------
# CONFIGURATION
# -------------------------

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "jill2143"

# -------------------------
# CONNECT AND CLEAR
# -------------------------

driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASSWORD)
)

with driver.session() as session:
    # Get count before deletion
    result = session.run("MATCH (n:Entity) RETURN count(n) as count")
    count_before = result.single()["count"]
    
    result = session.run("MATCH ()-[r:RELATED_TO]->() RETURN count(r) as count")
    rels_before = result.single()["count"]
    
    print(f"Before: {count_before} entities, {rels_before} relationships")
    
    # Delete all
    session.run("MATCH (n:Entity) DETACH DELETE n")
    
    print("✓ All data cleared from Neo4j!")

driver.close()
