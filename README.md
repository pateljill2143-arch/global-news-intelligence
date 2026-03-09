# AI-Driven Global News Knowledge Graph System

## 🎯 System Architecture

This system implements a **multi-layer pipeline architecture** for building a global intelligence knowledge graph from news data.

```
┌─────────────────────────────────────────────────────────────┐
│  1. DATA COLLECTION LAYER (collect_news.py)                 │
│     Fetches news from APIs → Stores in MongoDB              │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  2. DOCUMENT STORAGE LAYER (MongoDB)                         │
│     Raw articles stored as documents with metadata           │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  3. NLP PROCESSING LAYER (process_articles.py)               │
│     BERT NER → Extract Entities → Detect Relationships       │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  4. KNOWLEDGE GRAPH LAYER (Neo4j)                            │
│     Entities as Nodes → Relationships as Edges               │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  5. QUERY & ANALYSIS (query_triples.py, Neo4j Browser)       │
│     Explore connections, patterns, and timelines             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
transformer/
│
├── collect_news.py          # Stage 1: Fetch news → Store in MongoDB
├── process_articles.py      # Stage 2: Process MongoDB → Build Neo4j graph
├── run_pipeline.py          # Master orchestrator (runs all stages)
│
├── trans.py                 # Legacy: Direct processing (old approach)
├── query_triples.py         # Query and analyze knowledge graph
├── query_neo4j.py           # Neo4j statistics
├── clear_neo4j.py           # Clear Neo4j database
│
├── MONGODB_SETUP.md         # MongoDB installation guide
└── README.md                # This file
```

---

## 🚀 Quick Start

### Prerequisites

1. **Python 3.9+** with packages:
   ```powershell
   pip install transformers torch neo4j pymongo requests
   ```

2. **MongoDB Community Server**
   - See `MONGODB_SETUP.md` for installation
   - Ensure service is running: `Get-Service MongoDB`

3. **Neo4j Database**
   - Already installed and configured
   - Running on `bolt://localhost:7687`

### Running the System

**Option 1: Full Pipeline (Recommended)**
```powershell
python run_pipeline.py
```
This runs all stages sequentially.

**Option 2: Step-by-Step**
```powershell
# Step 1: Collect news articles
python collect_news.py

# Step 2: Process articles and build knowledge graph
python process_articles.py

# Step 3: Query the knowledge graph
python query_triples.py
```

**Option 3: Continuous Updates**
```powershell
# Add new articles anytime
python collect_news.py

# Process only unprocessed articles
python process_articles.py
```

---

## 📊 Data Flow

### 1. News Collection
- Fetches from **25 topic categories**
- Stores **raw JSON** in MongoDB
- Marks articles as `processed: false`
- Prevents duplicates via unique URL index

### 2. NLP Processing
- Reads unprocessed articles from MongoDB
- **BERT-based NER** extracts entities:
  - Persons (PER)
  - Organizations (ORG)
  - Locations (LOC)
  - Miscellaneous (MISC)

### 3. Relationship Extraction
- Analyzes text between entities
- Detects **100+ relationship types**:
  - ATTACKS, SANCTIONS, TRADES_WITH
  - MEETS, SUPPORTS, CONDEMNS
  - INVESTS_IN, NEGOTIATES_WITH, etc.

### 4. Knowledge Graph Construction
- Creates **Subject-Predicate-Object** triples
- Stores with metadata:
  - Date, Source, Sentiment
  - Article URL, Text snippet
  - Timestamps

### 5. Entity Tracking
- Counts entity mentions over time
- Tracks `first_seen` and `last_seen`
- Enables historical analysis

---

## 🔍 Querying the Knowledge Graph

### Python Queries
```powershell
python query_triples.py
```

Shows:
- Database statistics
- Sample triples with metadata
- Most mentioned entities
- Connection paths
- Conflicts & cooperations
- Timeline of events

### Neo4j Browser
Open: http://localhost:7474

**Example Cypher Queries:**

```cypher
// View all relationships
MATCH (n:Entity)-[r]->(m:Entity)
RETURN n, r, m
LIMIT 100

// Find conflicts
MATCH (n)-[r]->(m)
WHERE r.sentiment = 'negative'
RETURN n.name, type(r), m.name, r.date
ORDER BY r.date DESC

// 2-hop connections
MATCH (a)-[r1]->(b)-[r2]->(c)
WHERE a <> c
RETURN a.name, type(r1), b.name, type(r2), c.name
LIMIT 20

// Most mentioned entities
MATCH (n:Entity)
RETURN n.name, n.mention_count
ORDER BY n.mention_count DESC
LIMIT 20
```

### MongoDB Queries

```powershell
mongosh
```

```javascript
use global_news_intelligence

// Count articles
db.raw_articles.countDocuments()

// Unprocessed articles
db.raw_articles.find({processed: false}).count()

// View article
db.raw_articles.findOne()

// Articles by source
db.raw_articles.aggregate([
  {$group: {_id: "$source.name", count: {$sum: 1}}},
  {$sort: {count: -1}}
])
```

---

## 🎨 Knowledge Graph Features

### Triple Structure
```
Subject: Russia
Predicate: ATTACKS
Object: Ukraine
Metadata:
  - date: "2026-03-01T15:30:00Z"
  - source: "Reuters"
  - sentiment: "negative"
  - article_url: "https://..."
  - text_snippet: "Russia attacks Ukraine..."
```

### Entity Tracking
```
Entity: USA
  - mention_count: 45
  - first_seen: 1709200000 (timestamp)
  - last_seen: 1709290000 (timestamp)
```

### Relationship Types (100+)

**Military:** ATTACKS, INVADES, BOMBS, STRIKES, WAR_WITH
**Economic:** TRADES_WITH, SANCTIONS, INVESTS_IN, EXPORTS_TO
**Diplomatic:** MEETS, SUPPORTS, CONDEMNS, NEGOTIATES_WITH
**Legal:** SUES, ARRESTS, APPEALS_AGAINST, INVESTIGATES
**Political:** ELECTS, VOTES_FOR, RESIGNS_FROM, EXPELS

---

## 📈 Advantages of This Architecture

### Separation of Concerns
✅ **Collection** separated from **Processing**
✅ Can re-process articles with improved algorithms
✅ Easy to add new data sources

### Scalability
✅ MongoDB handles millions of documents
✅ Process articles in batches
✅ Add new articles without reprocessing old ones

### Data Persistence
✅ Raw articles preserved forever
✅ Can trace back to original text
✅ Supports audit and verification

### Flexibility
✅ Process same articles multiple times with different models
✅ Easy to experiment with new NER models
✅ Can add new relationship types retroactively

---

## 🔧 Maintenance Commands

### Reset Processing Status
```javascript
// MongoDB
db.raw_articles.updateMany({processed: true}, {$set: {processed: false}})
```

### Clear Knowledge Graph
```powershell
python clear_neo4j.py
```

### View Statistics
```powershell
python query_neo4j.py
python query_triples.py
```

---

## 📊 Output Example

```
AI-DRIVEN GLOBAL NEWS KNOWLEDGE GRAPH SYSTEM
================================================================================

Stage 1-2: Data Collection & Storage
✓ Fetched 250 articles from 25 topics
✓ Stored 183 new articles in MongoDB

Stage 3-4: NLP Processing & Knowledge Graph Construction
✓ Processed 183 articles
✓ Created 421 entity relationships

DATABASE STATS:
  Total Entities: 287
  Total Relationships: 421
  Most Connected: Russia (28 connections)

SAMPLE TRIPLES:
  Russia → ATTACKS → Ukraine (negative)
  USA → SANCTIONS → Russia (negative)
  India → TRADES_WITH → Russia (neutral)
  Biden → MEETS → Xi (neutral)
```

---

## 🛠️ Troubleshooting

### MongoDB Connection Error
```powershell
# Check service
Get-Service MongoDB

# Start if stopped
net start MongoDB
```

### Neo4j Connection Error
```powershell
# Check Neo4j is running
# Open Neo4j Desktop or Browser
```

### No Articles Processed
- Check MongoDB has unprocessed articles
- Verify News API key is valid
- Check internet connection

---

## 📝 Next Steps

1. **Add More Data Sources**
   - GDELT database integration
   - RSS feeds
   - Twitter/social media

2. **Improve NLP**
   - Use spaCy for dependency parsing
   - Add coreference resolution
   - Better relationship extraction

3. **Visualization Dashboard**
   - Streamlit web interface
   - Interactive graph visualization
   - Real-time monitoring

4. **Automation**
   - Schedule collection (Windows Task Scheduler)
   - Automatic processing pipeline
   - Alert system for events

---

## 👤 Author

Patel - Global Intelligence Graph System
March 2026
