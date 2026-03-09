"""
STEP 4: BUILD RELATIONSHIPS BETWEEN ENTITIES
Creates knowledge graph in Neo4j with entity relationships
"""

from neo4j import GraphDatabase
from pathlib import Path
import json
import re

# Configuration
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "jill2143"

# Input directory (from step 3)
INPUT_DIR = Path(__file__).parent.parent / "3_entity_extraction" / "extracted_entities"

# ── Verb → Neo4j relationship label mapping ──────────────────────────────────
# Each verb detected in article text becomes a named, typed relationship in Neo4j
# so the graph browser shows ATTACKS, SANCTIONS, TRADES_WITH etc. — not just RELATES.
VERB_TO_REL_TYPE = {
    'attack':    'ATTACKS',
    'strike':    'STRIKES',
    'bomb':      'BOMBS',
    'invade':    'INVADES',
    'threaten':  'THREATENS',
    'conflict':  'IN_CONFLICT_WITH',
    'support':   'SUPPORTS',
    'ally':      'ALLIED_WITH',
    'help':      'HELPS',
    'cooperate': 'COOPERATES_WITH',
    'partner':   'PARTNERS_WITH',
    'trade':     'TRADES_WITH',
    'export':    'EXPORTS_TO',
    'import':    'IMPORTS_FROM',
    'invest':    'INVESTS_IN',
    'sanction':  'SANCTIONS',
    'tariff':    'IMPOSES_TARIFF_ON',
    'meet':      'MEETS_WITH',
    'visit':     'VISITS',
    'negotiate': 'NEGOTIATES_WITH',
    'sign':      'SIGNS_AGREEMENT_WITH',
    'agree':     'AGREES_WITH',
    'announce':  'ANNOUNCES',
    'oppose':    'OPPOSES',
    'condemn':   'CONDEMNS',
    'criticize': 'CRITICIZES',
    'dispute':   'DISPUTES_WITH',
}


def cleanup_invalid_data(session):
    """Remove invalid entities and stale generic RELATES relationships from Neo4j"""
    print("\n🧹 Cleaning up invalid data...")

    # Delete old generic RELATES relationships (replaced by typed ones)
    result = session.run("""
        MATCH ()-[r:RELATES]-()
        DELETE r
        RETURN count(r) as deleted
    """)
    deleted = result.single()["deleted"]
    if deleted > 0:
        print(f"  ✓ Removed {deleted} old generic RELATES relationships")
    
    # Delete entities with names shorter than 3 characters
    result = session.run("""
        MATCH (e:Entity)
        WHERE size(e.name) < 3
        DETACH DELETE e
        RETURN count(e) as deleted
    """)
    deleted = result.single()["deleted"]
    if deleted > 0:
        print(f"  ✓ Removed {deleted} invalid entities (too short)")
    
    # Delete entities with common invalid names
    invalid_names = ['di', 'mo', 'car', 'ney', 'al', 'za', 'the', 'and', 'or', 'but']
    result = session.run("""
        MATCH (e:Entity)
        WHERE toLower(e.name) IN $invalid_names
        DETACH DELETE e
        RETURN count(e) as deleted
    """, invalid_names=invalid_names)
    deleted = result.single()["deleted"]
    if deleted > 0:
        print(f"  ✓ Removed {deleted} invalid entities (common fragments)")
    
    print("  ✓ Cleanup complete")

def is_valid_entity(name):
    """Validate entity name before processing"""
    if not name or len(name) < 3:
        return False
    # Filter out common words and fragments
    invalid = ['the', 'and', 'or', 'but', 'for', 'with', 'from', 'to', 'in', 'on', 'at', 
               'di', 'mo', 'car', 'ney', 'al', 'za']
    if name.lower() in invalid:
        return False
    return True

def detect_sentiment(text, rel_type):
    """Detect sentiment of relationship"""
    positive_words = ['trade', 'support', 'ally', 'help', 'cooperate', 'agree', 'partner', 'boost', 'growth']
    negative_words = ['attack', 'strike', 'conflict', 'war', 'sanction', 'condemn', 'oppose', 'threaten', 'crisis']
    
    text_lower = text.lower()
    rel_lower = rel_type.lower()
    
    if any(word in rel_lower or word in text_lower for word in negative_words):
        return 'negative'
    elif any(word in rel_lower or word in text_lower for word in positive_words):
        return 'positive'
    return 'neutral'

def detect_relationships(text, entities):
    """Detect relationships between entities.
    Returns dicts with 'rel_label' — the actual Neo4j relationship type to use.
    """
    relationships = []

    # Filter valid entities first
    entity_names = [e['name'] for e in entities if is_valid_entity(e['name'])]

    seen_relationships = set()  # Track to avoid duplicates

    for i, e1 in enumerate(entity_names):
        for e2 in entity_names[i+1:]:
            if e1 == e2:  # Skip self-relationships
                continue

            # Check if both entities appear together in the text
            pattern = f"{re.escape(e1)}.{{0,100}}{re.escape(e2)}"
            if not re.search(pattern, text, re.IGNORECASE):
                continue

            # Find the most specific verb between them
            for verb, rel_label in VERB_TO_REL_TYPE.items():
                if re.search(
                    f"{re.escape(e1)}.{{0,50}}{verb}.{{0,50}}{re.escape(e2)}",
                    text, re.IGNORECASE
                ):
                    rel_key = f"{e1}|{rel_label}|{e2}"
                    if rel_key not in seen_relationships:
                        sentiment = detect_sentiment(text, verb)
                        relationships.append({
                            'source':    e1,
                            'target':    e2,
                            'rel_label': rel_label,   # e.g. ATTACKS, SANCTIONS
                            'verb':      verb,         # original verb for context
                            'sentiment': sentiment,
                        })
                        seen_relationships.add(rel_key)
                    break
    return relationships

def build_neo4j_graph():
    """Build knowledge graph in Neo4j"""
    print("="*80)
    print("STEP 4: BUILDING RELATIONSHIPS IN NEO4J")
    print("="*80)
    
    # Find entity JSON files
    json_files = list(INPUT_DIR.glob("*.json"))
    
    if not json_files:
        print("\n⚠️  No entity files found")
        print("   Run step 3 first!")
        return
    
    print(f"\n📁 Found {len(json_files)} entity files")
    
    # Connect to Neo4j
    print("\n🕸️  Connecting to Neo4j...")
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        driver.verify_connectivity()
        print("  ✓ Connected successfully")
    except Exception as e:
        print(f"  ✗ Connection failed: {e}")
        return
    
    entity_count = 0
    relation_count = 0

    # Clean up first in its own session
    with driver.session() as session:
        cleanup_invalid_data(session)

    # Process each file in its OWN session to avoid timeout
    for json_file in json_files:
        print(f"\n📄 Processing: {json_file.name}")
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                articles_data = json.load(f)
            
            # Use a fresh session per file
            with driver.session() as session:
                for article_data in articles_data:
                    title = article_data.get('title', '')
                    entities = article_data.get('entities', [])
                    
                    valid_entities = [e for e in entities if is_valid_entity(e['name'])]
                    
                    for entity in valid_entities:
                        try:
                            session.run("""
                                MERGE (e:Entity {name: $name})
                                ON CREATE SET e.type = $type, e.mention_count = 1
                                ON MATCH SET e.mention_count = e.mention_count + 1
                            """, name=entity['name'], type=entity['type'])
                            entity_count += 1
                        except Exception:
                            pass
                    
                    relationships = detect_relationships(title, valid_entities)
                    
                    for rel in relationships:
                        try:
                            # Embed the relationship label directly in the Cypher
                            # so Neo4j stores ATTACKS, SANCTIONS, TRADES_WITH etc.
                            # instead of a generic RELATES with a type property.
                            # rel['rel_label'] comes from VERB_TO_REL_TYPE and is
                            # always an uppercase identifier — no injection risk.
                            rel_label = rel['rel_label']
                            session.run(f"""
                                MATCH (e1:Entity {{name: $source}})
                                MATCH (e2:Entity {{name: $target}})
                                MERGE (e1)-[r:{rel_label}]->(e2)
                                ON CREATE SET r.count = 1,
                                              r.sentiment = $sentiment,
                                              r.verb = $verb,
                                              r.date = datetime()
                                ON MATCH SET r.count = r.count + 1
                            """, source=rel['source'], target=rel['target'],
                                sentiment=rel['sentiment'], verb=rel['verb'])
                            relation_count += 1
                        except Exception:
                            pass
            
            print(f"  ✓ Processed")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    driver.close()
    
    print(f"\n{'='*80}")
    print("📊 RELATIONSHIP BUILDING SUMMARY")
    print(f"{'='*80}")
    print(f"✅ Entities created: {entity_count}")
    print(f"🔗 Relationships created: {relation_count}")
    print(f"🕸️  Knowledge graph built in Neo4j")
    
    print(f"\n➡️  Next step: Run 5_dashboard_visualization/launch_dashboard.py")

if __name__ == "__main__":
    build_neo4j_graph()
