"""
NLP PROCESSING & KNOWLEDGE GRAPH CONSTRUCTION LAYER
Reads raw articles from MongoDB, extracts entities/relationships, stores in Neo4j
"""

import requests
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
from neo4j import GraphDatabase
from pymongo import MongoClient
from datetime import datetime
import re

# -------------------------
# CONFIGURATION
# -------------------------

# MongoDB Configuration
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB = "global_news_intelligence"
MONGO_COLLECTION = "raw_articles"

# Neo4j Configuration
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "jill2143"

# -------------------------
# CONNECT TO MONGODB
# -------------------------

print("📊 Connecting to databases...")

try:
    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client[MONGO_DB]
    articles_collection = db[MONGO_COLLECTION]
    print("✓ Connected to MongoDB")
except Exception as e:
    print(f"✗ MongoDB connection failed: {e}")
    exit(1)

# -------------------------
# CONNECT TO NEO4J
# -------------------------

try:
    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USER, NEO4J_PASSWORD)
    )
    driver.verify_connectivity()
    print("✓ Connected to Neo4j")
except Exception as e:
    print(f"✗ Neo4j connection failed: {e}")
    driver = None

# -------------------------
# LOAD TRANSFORMER MODEL
# -------------------------

print("\n🤖 Loading NER Transformer Model...")
print("   Model: dslim/bert-base-NER (Fast & Accurate)")

ner_pipeline = pipeline(
    "ner",
    model="dslim/bert-base-NER",
    aggregation_strategy="simple"
)
print("✓ BERT NER model loaded successfully")

# -------------------------
# RELATIONSHIP EXTRACTION FUNCTIONS
# -------------------------

def get_sentiment(relation_type):
    """Determine sentiment of relationship"""
    positive_relations = [
        'PEACE_WITH', 'ALLIED_WITH', 'TREATY_WITH', 'AGREEMENT_WITH', 'COOPERATES_WITH',
        'SUPPORTS', 'AIDS', 'HELPS', 'ASSISTS', 'PARTNERS_WITH', 'COLLABORATES_WITH',
        'CELEBRATES', 'PRAISE', 'ENDORSES', 'DEAL_WITH', 'TRADES_WITH', 'INVESTS_IN',
        'PROTECTS', 'DEFENDS', 'RESCUES', 'ELECTS', 'VOTES_FOR', 'RECOGNIZES',
        'ACKNOWLEDGES', 'MEETS', 'VISITS', 'DISCUSSES_WITH', 'TALKS_WITH', 'SIGNS_WITH',
        'NEGOTIATES_WITH', 'JOINS', 'UNITES_WITH', 'EXPORTS_TO', 'IMPORTS_FROM',
        'BUYS_FROM', 'SELLS_TO', 'MERGES_WITH', 'ACQUIRES', 'FUNDS', 'FINANCES',
        'APPOINTS', 'NOMINATES', 'SUCCEEDS'
    ]
    
    negative_relations = [
        'ATTACKS', 'INVADES', 'BOMBS', 'WAR_WITH', 'FIGHTS', 'CONFLICT_WITH', 'SANCTIONS',
        'CONDEMNS', 'BLAMES', 'ACCUSES', 'OPPOSES', 'ARRESTS', 'SUES', 'THREATENS',
        'BANS', 'BLOCKS', 'BOYCOTTS', 'REJECTS', 'DENOUNCES', 'CRITICIZES', 'EXPELS',
        'DEFEATS', 'HACKS', 'CYBER_ATTACK', 'SPIES_ON', 'PROTESTS_AGAINST', 'TENSION_WITH',
        'STRIKES', 'AIRSTRIKES', 'BATTLES', 'SHOOTS', 'KILLS', 'DESTROYS', 'LAUNCHES_ATTACK',
        'RAIDS', 'BOMBARDS', 'ASSAULTS', 'DETAINS', 'CHARGES', 'PROSECUTES', 'SENTENCES',
        'CONVICTS', 'INDICTS', 'INTIMIDATES', 'BLACKMAILS', 'COERCES', 'BREACHES',
        'SURVEILS', 'WIRETAPS', 'MONITORS', 'EMBARGOES', 'DISMISSES', 'FIRES', 'OVERTHROWS'
    ]
    
    if relation_type in positive_relations:
        return 'positive'
    elif relation_type in negative_relations:
        return 'negative'
    else:
        return 'neutral'

def map_verb_to_relation(verb, doc_text=""):
    """Map verb to semantic relationship type based on context"""
    
    verb_lower = verb.lower()
    doc_lower = doc_text.lower()
    
    # Military/Conflict actions
    military_keywords = {
        'attack': 'ATTACKS', 'invade': 'INVADES', 'bomb': 'BOMBS', 'strike': 'STRIKES',
        'airstrike': 'AIRSTRIKES', 'fight': 'FIGHTS', 'battle': 'BATTLES',
        'shoot': 'SHOOTS', 'kill': 'KILLS', 'destroy': 'DESTROYS', 'launch': 'LAUNCHES_ATTACK',
        'raid': 'RAIDS', 'bombard': 'BOMBARDS', 'assault': 'ASSAULTS'
    }
    
    # Diplomatic/Political actions
    diplomatic_keywords = {
        'sanction': 'SANCTIONS', 'condemn': 'CONDEMNS', 'denounce': 'DENOUNCES',
        'criticize': 'CRITICIZES', 'oppose': 'OPPOSES', 'support': 'SUPPORTS',
        'endorse': 'ENDORSES', 'recognize': 'RECOGNIZES', 'acknowledge': 'ACKNOWLEDGES',
        'negotiate': 'NEGOTIATES_WITH', 'meet': 'MEETS', 'visit': 'VISITS',
        'discuss': 'DISCUSSES_WITH', 'talk': 'TALKS_WITH', 'sign': 'SIGNS_WITH'
    }
    
    # Economic actions
    economic_keywords = {
        'trade': 'TRADES_WITH', 'export': 'EXPORTS_TO', 'import': 'IMPORTS_FROM',
        'invest': 'INVESTS_IN', 'buy': 'BUYS_FROM', 'sell': 'SELLS_TO',
        'purchase': 'PURCHASES_FROM', 'acquire': 'ACQUIRES', 'merge': 'MERGES_WITH',
        'partner': 'PARTNERS_WITH', 'fund': 'FUNDS', 'finance': 'FINANCES'
    }
    
    # Legal/Judicial actions
    legal_keywords = {
        'arrest': 'ARRESTS', 'detain': 'DETAINS', 'charge': 'CHARGES',
        'sue': 'SUES', 'prosecute': 'PROSECUTES', 'sentence': 'SENTENCES',
        'convict': 'CONVICTS', 'acquit': 'ACQUITS', 'pardon': 'PARDONS',
        'investigate': 'INVESTIGATES', 'indict': 'INDICTS'
    }
    
    # Alliance/Cooperation
    alliance_keywords = {
        'ally': 'ALLIED_WITH', 'collaborate': 'COLLABORATES_WITH', 
        'cooperate': 'COOPERATES_WITH', 'help': 'HELPS', 'assist': 'ASSISTS',
        'aid': 'AIDS', 'defend': 'DEFENDS', 'protect': 'PROTECTS',
        'join': 'JOINS', 'unite': 'UNITES_WITH'
    }
    
    # Leadership/Political changes
    leadership_keywords = {
        'elect': 'ELECTS', 'appoint': 'APPOINTS', 'nominate': 'NOMINATES',
        'resign': 'RESIGNS_FROM', 'dismiss': 'DISMISSES', 'fire': 'FIRES',
        'replace': 'REPLACES', 'succeed': 'SUCCEEDS', 'overthrow': 'OVERTHROWS'
    }
    
    # Threats/Warnings
    threat_keywords = {
        'threaten': 'THREATENS', 'warn': 'WARNS', 'intimidate': 'INTIMIDATES',
        'blackmail': 'BLACKMAILS', 'coerce': 'COERCES'
    }
    
    # Technology/Cyber
    cyber_keywords = {
        'hack': 'HACKS', 'breach': 'BREACHES', 'spy': 'SPIES_ON',
        'surveil': 'SURVEILS', 'wiretap': 'WIRETAPS', 'monitor': 'MONITORS'
    }
    
    # Check all categories
    all_keywords = {
        **military_keywords, **diplomatic_keywords, **economic_keywords,
        **legal_keywords, **alliance_keywords, **leadership_keywords,
        **threat_keywords, **cyber_keywords
    }
    
    # Direct match
    for keyword, relation in all_keywords.items():
        if keyword in verb_lower:
            return relation
    
    # Context-based detection for "war" scenarios
    if 'war' in doc_lower or 'conflict' in doc_lower:
        if any(w in verb_lower for w in ['with', 'against', 'versus']):
            return 'WAR_WITH'
    
    # Default to generic relationship
    return 'RELATED_TO'

def extract_smart_relationships(text, entity_list):
    """
    Extract relationships between entities using enhanced pattern matching
    Returns list of (entity1, relation, entity2) tuples
    """
    relationships = []
    text_lower = text.lower()
    
    # Try to find pairs of entities with verbs between them
    for i, e1 in enumerate(entity_list):
        for j, e2 in enumerate(entity_list):
            if i >= j:  # Skip same entity and already checked pairs
                continue
            
            e1_pos = text_lower.find(e1.lower())
            e2_pos = text_lower.find(e2.lower())
            
            if e1_pos != -1 and e2_pos != -1:
                # Get text between entities
                start = min(e1_pos, e2_pos)
                end = max(e1_pos, e2_pos)
                between_text = text_lower[start:end]
                
                # Determine direction (who's first in sentence)
                first_entity = e1 if e1_pos < e2_pos else e2
                second_entity = e2 if e1_pos < e2_pos else e1
                
                # Find action verb
                relation_type = extract_action(text, first_entity, second_entity)
                
                # Only add if we found a meaningful relationship
                if relation_type != 'MENTIONED_WITH' or len(between_text) < 100:
                    relationships.append((first_entity, relation_type, second_entity))
    
    return relationships

def extract_action(text, entity1, entity2):
    """Simplified keyword-based fallback for when dependency parsing doesn't find relationships"""
    
    # Quick keyword mapping
    keyword_map = {
        'attack': 'ATTACKS', 'invade': 'INVADES', 'bomb': 'BOMBS', 'strike': 'STRIKES',
        'war': 'WAR_WITH', 'fight': 'FIGHTS', 'sanction': 'SANCTIONS', 'trade': 'TRADES_WITH',
        'support': 'SUPPORTS', 'oppose': 'OPPOSES', 'meet': 'MEETS', 'visit': 'VISITS',
        'condemn': 'CONDEMNS', 'help': 'HELPS', 'ally': 'ALLIED_WITH', 'partner': 'PARTNERS_WITH'
    }
    
    text_lower = text.lower()
    e1_pos = text_lower.find(entity1.lower())
    e2_pos = text_lower.find(entity2.lower())
    
    if e1_pos != -1 and e2_pos != -1:
        start = min(e1_pos, e2_pos)
        end = max(e1_pos, e2_pos)
        between_text = text_lower[start:end]
        
        for keyword, relation in keyword_map.items():
            if keyword in between_text:
                return relation
    
    for keyword, relation in keyword_map.items():
        if keyword in text_lower:
            return relation
    
    return 'MENTIONED_WITH'

def create_relation(tx, e1, relation_type, e2, metadata):
    """Create relationship with metadata in Neo4j"""
    tx.run(
        """
        MERGE (a:Entity {name:$e1})
        ON CREATE SET a.first_seen = timestamp(), a.mention_count = 1
        ON MATCH SET a.mention_count = a.mention_count + 1, a.last_seen = timestamp()
        
        MERGE (b:Entity {name:$e2})
        ON CREATE SET b.first_seen = timestamp(), b.mention_count = 1
        ON MATCH SET b.mention_count = b.mention_count + 1, b.last_seen = timestamp()
        
        CREATE (a)-[r:%s]->(b)
        SET r.date = $date,
            r.source = $source,
            r.sentiment = $sentiment,
            r.text_snippet = $text_snippet,
            r.article_url = $article_url,
            r.timestamp = timestamp(),
            r.added_on = datetime()
        """ % relation_type,
        e1=e1,
        e2=e2,
        date=metadata.get('date'),
        source=metadata.get('source'),
        sentiment=metadata.get('sentiment'),
        text_snippet=metadata.get('text_snippet'),
        article_url=metadata.get('article_url')
    )

def store_entities(entity_names, text, article_metadata):
    """Store entity relationships in Neo4j using enhanced pattern matching"""
    if driver is None:
        return 0
    
    # Extract relationships using smart pattern matching
    relationships = extract_smart_relationships(text, entity_names)
    
    # If we found specific relationships, use them
    if relationships:
        with driver.session() as session:
            for e1, relation_type, e2 in relationships:
                sentiment = get_sentiment(relation_type)
                
                metadata = {
                    'date': article_metadata.get('publishedAt', ''),
                    'source': article_metadata.get('source', ''),
                    'sentiment': sentiment,
                    'text_snippet': text[:200],
                    'article_url': article_metadata.get('url', '')
                }
                
                print(f"      → {e1} --[{relation_type}]({sentiment})--> {e2}")
                session.execute_write(create_relation, e1, relation_type, e2, metadata)
        return len(relationships)
    
    return 0

# -------------------------
# PROCESS ARTICLES FROM MONGODB
# -------------------------

print("\n" + "=" * 80)
print("🔄 PROCESSING UNPROCESSED ARTICLES")
print("=" * 80)

# Get unprocessed articles
unprocessed_articles = list(articles_collection.find({"processed": False}).limit(100))

print(f"\nFound {len(unprocessed_articles)} unprocessed articles")

articles_processed = 0
relationships_created = 0

for article in unprocessed_articles:
    
    title = article.get("title", "")
    description = article.get("description", "")
    url = article.get("url", "")
    published_at = article.get("publishedAt", "")
    source_name = article.get("source", {}).get("name", "Unknown")
    
    if not title or title == "[Removed]":
        # Mark as processed even if invalid
        articles_collection.update_one(
            {"_id": article["_id"]},
            {"$set": {"processed": True, "processed_at": datetime.utcnow()}}
        )
        continue
    
    full_text = f"{title}. {description}"
    
    print(f"\n[{articles_processed + 1}] {title}")
    print(f"   📅 {published_at} | 📰 {source_name}")
    
    # Extract entities using BERT Transformer
    entities_result = ner_pipeline(full_text)
    entity_names = []
    
    for e in entities_result:
        if e["entity_group"] in ["LOC", "ORG", "PER", "MISC"]:
            entity = e["word"].strip().replace("##", "")
            
            # Skip if starts with ## or too short
            if entity.startswith("##") or len(entity) < 2:
                continue
            
            # Skip common stop words
            skip_words = ["the", "a", "an", "this", "that", "he", "she", "it", "me", "my", "be", "are", "is"]
            if entity.lower() in skip_words:
                continue
            
            entity_names.append(entity)
            print(f"   Entity: {entity} ({e['entity_group']}) [score: {e['score']:.2f}]")
    
    # Store relationships
    rel_count = 0
    if len(entity_names) > 1:
        article_metadata = {
            'publishedAt': published_at,
            'source': source_name,
            'url': url
        }
        rel_count = store_entities(entity_names, full_text, article_metadata)
        relationships_created += rel_count
    
    # Mark as processed in MongoDB
    articles_collection.update_one(
        {"_id": article["_id"]},
        {
            "$set": {
                "processed": True,
                "processed_at": datetime.utcnow(),
                "entities_found": len(entity_names),
                "relationships_created": rel_count
            }
        }
    )
    
    articles_processed += 1

# -------------------------
# SUMMARY
# -------------------------

print("\n" + "=" * 80)
print("📊 PROCESSING SUMMARY")
print("=" * 80)
print(f"✓ Processed {articles_processed} articles")
print(f"✓ Created {relationships_created} relationships")

mongo_client.close()
driver.close()

print("\n✓ Knowledge graph updated!")
print("Run query_triples.py to explore the knowledge graph")
