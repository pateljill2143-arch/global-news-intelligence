"""
STEP 3: EXTRACT ENTITIES FROM ARTICLES
Converts text into entities using BERT NER
Saves entities to JSON for relationship building
"""

from pymongo import MongoClient
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
from pathlib import Path
import json
from datetime import datetime
import re

# Configuration
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB = "global_news_intelligence"
MONGO_COLLECTION = "raw_articles"

# Output directory
OUTPUT_DIR = Path(__file__).parent / "extracted_entities"
OUTPUT_DIR.mkdir(exist_ok=True)

def load_ner_model():
    """Load BERT NER model"""
    print("🤖 Loading BERT NER model...")
    tokenizer = AutoTokenizer.from_pretrained("dslim/bert-base-NER")
    model = AutoModelForTokenClassification.from_pretrained("dslim/bert-base-NER")
    ner_pipeline = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")
    print("  ✓ Model loaded")
    return ner_pipeline

def clean_entity_name(name):
    """Clean and validate entity name"""
    # Remove special characters and cleanup
    name = name.replace('##', '').strip()
    name = re.sub(r'[^a-zA-Z0-9\s\-\.]', '', name)
    name = name.strip()
    
    # Filter out invalid entities
    if len(name) < 3:  # Too short
        return None
    if name.lower() in ['the', 'and', 'or', 'but', 'for', 'with', 'from', 'to', 'in', 'on', 'at']:
        return None
    if any(char.isdigit() for char in name) and len(name) < 4:  # Just numbers or too short with numbers
        return None
    
    return name

def extract_entities_from_text(text, ner_pipeline):
    """Extract entities from text"""
    if not text or len(text.strip()) < 10:
        return []
    
    try:
        text = text[:2000]  # Limit length
        results = ner_pipeline(text)
        
        entities = []
        seen_entities = set()  # Track unique entities
        
        for entity in results:
            if entity['score'] > 0.85:  # High confidence only
                # Clean entity name
                clean_name = clean_entity_name(entity['word'])
                
                if clean_name and clean_name.lower() not in seen_entities:
                    entities.append({
                        'name': clean_name,
                        'type': entity['entity_group'],
                        'score': float(entity['score'])
                    })
                    seen_entities.add(clean_name.lower())
        
        return entities
    except:
        return []

def main():
    print("="*80)
    print("STEP 3: EXTRACTING ENTITIES (Converting to Entities)")
    print("="*80)
    
    # Connect to MongoDB
    print("\n📊 Connecting to MongoDB...")
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION]
    
    # Get unprocessed articles
    articles = list(collection.find({"processed": False}).limit(1000))  # Process 1000 at a time
    
    if not articles:
        print("\n⚠️  No unprocessed articles found")
        print("   Run steps 1 and 2 first!")
        return
    
    print(f"  ✓ Found {len(articles)} unprocessed articles")
    
    # Load NER model
    ner_pipeline = load_ner_model()
    
    # Extract entities
    print(f"\n🔍 Extracting entities from {len(articles)} articles...")
    
    articles_with_entities = []
    
    for i, article in enumerate(articles, 1):
        if i % 50 == 0:  # Progress every 50 articles
            print(f"  Processed {i}/{len(articles)}...")
        
        # Combine title and description
        text = f"{article.get('title', '')} {article.get('description', '')}"
        
        # Extract entities
        entities = extract_entities_from_text(text, ner_pipeline)
        
        if entities:
            articles_with_entities.append({
                'article_id': str(article['_id']),
                'url': article.get('url'),
                'title': article.get('title'),
                'entities': entities,
                'extracted_at': datetime.utcnow().isoformat()
            })
    
    # Save entities to JSON
    output_file = OUTPUT_DIR / f"entities_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(articles_with_entities, f, indent=2, ensure_ascii=False)
    
    # Mark articles as processed in MongoDB
    article_ids = [article['_id'] for article in articles]
    collection.update_many(
        {'_id': {'$in': article_ids}},
        {'$set': {'processed': True}}
    )
    
    print(f"\n{'='*80}")
    print("📊 ENTITY EXTRACTION SUMMARY")
    print(f"{'='*80}")
    print(f"✅ Articles processed: {len(articles)}")
    print(f"🎯 Articles with entities: {len(articles_with_entities)}")
    print(f"📁 Saved to: {output_file}")
    
    # Count total entities
    total_entities = sum(len(a['entities']) for a in articles_with_entities)
    print(f"📊 Total entities extracted: {total_entities}")
    print(f"✅ Articles marked as processed in MongoDB")
    
    print(f"\n➡️  Next step: Run 4_relationship_building/build_relationships.py")
    
    client.close()

if __name__ == "__main__":
    main()
