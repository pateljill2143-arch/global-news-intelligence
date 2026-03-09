# 🚀 News Intelligence Pipeline Workflow

## 📂 Folder Structure

```
pipeline_workflow/
│
├── 1_data_collection/           # STEP 1: Fetch data from APIs & Internet
│   ├── collect_api_data.py      #   - Collect from NewsAPI, Guardian, GNews
│   ├── collect_infinite_data.py  #   - Collect from 40+ RSS feeds (unlimited)
│   └── collected_data/          #   - JSON files with raw data
│
├── 2_mongodb_storage/           # STEP 2: Store data in MongoDB
│   └── store_in_mongodb.py      #   - Read JSON files and store in database
│
├── 3_entity_extraction/         # STEP 3: Convert to entities
│   ├── extract_entities.py      #   - Use BERT NER to extract entities
│   └── extracted_entities/      #   - JSON files with entities
│
├── 4_relationship_building/     # STEP 4: Build relationships
│   └── build_relationships.py   #   - Create knowledge graph in Neo4j
│
├── 5_dashboard_visualization/   # STEP 5: Make visible on dashboard
│   └── launch_dashboard.py      #   - Launch interactive dashboard
│
└── RUN_COMPLETE_WORKFLOW.py    # ⚡ Run ALL steps automatically
```

---

## 🎯 How to Use

### Option 1: Run Complete Workflow (Recommended)
```powershell
python pipeline_workflow\RUN_COMPLETE_WORKFLOW.py
```
This runs all 5 steps automatically!

### Option 2: Run Individual Steps

**Step 1: Collect Data**
```powershell
# From APIs (NewsAPI, Guardian, GNews)
python pipeline_workflow\1_data_collection\collect_api_data.py

# From Internet (40+ RSS feeds)
python pipeline_workflow\1_data_collection\collect_infinite_data.py
```

**Step 2: Store in MongoDB**
```powershell
python pipeline_workflow\2_mongodb_storage\store_in_mongodb.py
```

**Step 3: Extract Entities**
```powershell
python pipeline_workflow\3_entity_extraction\extract_entities.py
```

**Step 4: Build Relationships**
```powershell
python pipeline_workflow\4_relationship_building\build_relationships.py
```

**Step 5: Launch Dashboard**
```powershell
python pipeline_workflow\5_dashboard_visualization\launch_dashboard.py
```

---

## 📊 Data Flow

```
APIs + Internet
      ↓
  JSON Files (1_data_collection/collected_data/)
      ↓
   MongoDB (raw_articles collection)
      ↓
Entity Extraction (BERT NER)
      ↓
  JSON Files (3_entity_extraction/extracted_entities/)
      ↓
   Neo4j (Entity nodes + Relationship edges)
      ↓
  Dashboard (Interactive visualization)
```

---

## ✅ What Gets Created

### 1. Data Collection (`1_data_collection/collected_data/`)
- `api_data_YYYYMMDD_HHMMSS.json` - Articles from APIs
- `rss_data_YYYYMMDD_HHMMSS.json` - Articles from RSS feeds

### 2. MongoDB Database
- Database: `global_news_intelligence`
- Collection: `raw_articles`
- Fields: title, description, content, url, source, language, etc.

### 3. Entity Extraction (`3_entity_extraction/extracted_entities/`)
- `entities_YYYYMMDD_HHMMSS.json` - Extracted entities with types

### 4. Neo4j Knowledge Graph
- Nodes: Entity (name, type, mention_count)
- Relationships: RELATES (type, count)

### 5. Dashboard
- URL: http://localhost:8501
- Shows: Knowledge graph, entities, relationships, analytics

---

## 🔧 Requirements

- MongoDB running on `localhost:27017`
- Neo4j running on `localhost:7687`
- Python packages: pymongo, neo4j, transformers, streamlit, feedparser, langdetect

---

## 💡 Tips

1. **For maximum data**: Run both collect scripts in step 1
2. **Continuous collection**: Run `collect_infinite_data.py` repeatedly
3. **Check progress**: Look in `collected_data/` and `extracted_entities/` folders
4. **View database**: Use MongoDB Compass or `python check_mongodb.py`
5. **View graph**: Access Neo4j Browser at http://localhost:7474

---

## 🚀 Quick Start

1. **Run complete workflow**:
   ```powershell
   python pipeline_workflow\RUN_COMPLETE_WORKFLOW.py
   ```

2. **Wait for completion** (~10-20 minutes for 100 articles)

3. **View dashboard** at http://localhost:8501

---

## ⚠️ Troubleshooting

**Issue**: "No JSON files found"
- **Solution**: Run step 1 first to collect data

**Issue**: "MongoDB not accessible"
- **Solution**: Start MongoDB with `mongod` command

**Issue**: "Neo4j connection failed"
- **Solution**: Start Neo4j Desktop or service

**Issue**: "No module named 'pymongo'"
- **Solution**: Run `python install_packages.py`

---

✅ **Everything is organized and ready to use!**
