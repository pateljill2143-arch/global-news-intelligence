"""
STEP 2: STORE DATA IN MONGODB
Reads collected JSON files and stores in MongoDB database
"""

from pymongo import MongoClient
from pathlib import Path
import json
from datetime import datetime

# Configuration
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB = "global_news_intelligence"
MONGO_COLLECTION = "raw_articles"

# Input directory (from step 1)
INPUT_DIR = Path(__file__).parent.parent / "1_data_collection" / "collected_data"

def store_in_mongodb():
    """Store all collected JSON files in MongoDB"""
    print("="*80)
    print("STEP 2: STORING DATA IN MONGODB")
    print("="*80)
    
    # Connect to MongoDB
    print("\n📊 Connecting to MongoDB...")
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION]
        
        # Create indexes
        collection.create_index([("url", 1)], unique=True)
        collection.create_index([("processed", 1)])
        
        print("  ✓ Connected successfully")
    except Exception as e:
        print(f"  ✗ Connection failed: {e}")
        return
    
    # Find all JSON files
    json_files = list(INPUT_DIR.glob("*.json"))
    
    if not json_files:
        print("\n⚠️  No JSON files found in collected_data folder")
        print("   Run collect_api_data.py or collect_infinite_data.py first!")
        return
    
    print(f"\n📁 Found {len(json_files)} JSON files to process")
    
    total_new = 0
    total_duplicate = 0
    
    # Process each JSON file
    for json_file in json_files:
        print(f"\n📄 Processing: {json_file.name}")
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                articles = json.load(f)
            
            new_count = 0
            duplicate_count = 0
            
            for article in articles:
                # Mark as not processed
                article['processed'] = False
                
                try:
                    collection.insert_one(article)
                    new_count += 1
                except:
                    duplicate_count += 1  # Duplicate URL
            
            print(f"  ✓ New: {new_count}, Duplicates: {duplicate_count}")
            
            total_new += new_count
            total_duplicate += duplicate_count
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    # Summary
    total_in_db = collection.count_documents({})
    unprocessed = collection.count_documents({"processed": False})
    
    print(f"\n{'='*80}")
    print("📊 MONGODB STORAGE SUMMARY")
    print(f"{'='*80}")
    print(f"✅ New articles stored: {total_new}")
    print(f"⏭️  Duplicates skipped: {total_duplicate}")
    print(f"📦 Total in database: {total_in_db}")
    print(f"⏳ Unprocessed articles: {unprocessed}")
    
    print(f"\n➡️  Next step: Run 3_entity_extraction/extract_entities.py")
    
    client.close()

if __name__ == "__main__":
    store_in_mongodb()
