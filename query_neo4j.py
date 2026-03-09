from neo4j import GraphDatabase

# -------------------------
# CONFIGURATION
# -------------------------

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "jill2143"

# -------------------------
# CONNECT TO NEO4J
# -------------------------

driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASSWORD)
)

# -------------------------
# QUERY FUNCTIONS
# -------------------------

def get_all_entities():
    """Get all entities in the graph"""
    with driver.session() as session:
        result = session.run("MATCH (n:Entity) RETURN n.name as name")
        entities = [record["name"] for record in result]
        return entities

def get_entity_connections(entity_name):
    """Get all entities connected to a specific entity"""
    with driver.session() as session:
        result = session.run(
            """
            MATCH (n:Entity {name: $name})-[:RELATED_TO]-(connected)
            RETURN connected.name as name
            """,
            name=entity_name
        )
        connections = [record["name"] for record in result]
        return connections

def get_most_connected_entities(limit=10):
    """Get entities with most connections"""
    with driver.session() as session:
        result = session.run(
            """
            MATCH (n:Entity)-[r:RELATED_TO]-()
            RETURN n.name as entity, count(r) as connections
            ORDER BY connections DESC
            LIMIT $limit
            """,
            limit=limit
        )
        entities = [(record["entity"], record["connections"]) for record in result]
        return entities

def get_statistics():
    """Get graph statistics"""
    with driver.session() as session:
        # Count entities
        entities_result = session.run("MATCH (n:Entity) RETURN count(n) as count")
        entity_count = entities_result.single()["count"]
        
        # Count relationships
        rels_result = session.run("MATCH ()-[r:RELATED_TO]->() RETURN count(r) as count")
        rel_count = rels_result.single()["count"]
        
        return {
            "entities": entity_count,
            "relationships": rel_count
        }

def clear_all_data():
    """Delete all entities and relationships"""
    with driver.session() as session:
        session.run("MATCH (n:Entity) DETACH DELETE n")
        print("All data cleared!")

# -------------------------
# MAIN
# -------------------------

if __name__ == "__main__":
    
    print("=" * 50)
    print("NEO4J KNOWLEDGE GRAPH QUERY TOOL")
    print("=" * 50)
    
    # Get statistics
    stats = get_statistics()
    print(f"\n📊 STATISTICS:")
    print(f"   Entities: {stats['entities']}")
    print(f"   Relationships: {stats['relationships']}")
    
    # Get most connected entities
    print(f"\n🔗 TOP 10 MOST CONNECTED ENTITIES:")
    top_entities = get_most_connected_entities(10)
    for entity, connections in top_entities:
        print(f"   {entity}: {connections} connections")
    
    # Get all entities
    print(f"\n📍 ALL ENTITIES:")
    all_entities = get_all_entities()
    for entity in all_entities[:20]:  # Show first 20
        print(f"   - {entity}")
    
    if len(all_entities) > 20:
        print(f"   ... and {len(all_entities) - 20} more")
    
    # Example: Get connections for a specific entity
    if all_entities:
        example_entity = all_entities[0]
        print(f"\n🔍 CONNECTIONS FOR '{example_entity}':")
        connections = get_entity_connections(example_entity)
        for conn in connections:
            print(f"   - {conn}")
    
    driver.close()
    print("\n✓ Done!")
