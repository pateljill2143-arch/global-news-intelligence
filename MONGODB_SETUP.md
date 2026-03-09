# MongoDB Installation & Setup

## Install MongoDB Community Server

### Windows:
1. Download MongoDB Community Server from: https://www.mongodb.com/try/download/community
2. Run the installer (.msi file)
3. Choose "Complete" installation
4. Install as a Windows Service (recommended)
5. Add MongoDB bin to PATH: `C:\Program Files\MongoDB\Server\7.0\bin`

### Verify Installation:
```powershell
mongod --version
mongo --version
```

## Install Python MongoDB Driver

```powershell
pip install pymongo
```

## Verify MongoDB is Running

```powershell
# Check if MongoDB service is running
Get-Service -Name MongoDB

# Or connect via mongo shell
mongosh
```

## MongoDB Database Structure

Our system creates:
- **Database**: `global_news_intelligence`
- **Collection**: `raw_articles`

### Document Schema:
```json
{
  "_id": ObjectId,
  "title": "Article title",
  "description": "Article description",
  "content": "Full article content",
  "url": "https://...",
  "source": {
    "id": "source-id",
    "name": "Source Name"
  },
  "author": "Author name",
  "publishedAt": "2026-03-01T10:00:00Z",
  "category": "Topic category",
  "collected_at": ISODate,
  "processed": false,
  "processed_at": ISODate,
  "entities_found": 0,
  "relationships_created": 0
}
```

## Useful MongoDB Commands

### In mongosh:
```javascript
// Use database
use global_news_intelligence

// Count documents
db.raw_articles.countDocuments()

// View unprocessed articles
db.raw_articles.find({processed: false}).limit(5)

// View processed articles
db.raw_articles.find({processed: true}).limit(5)

// Get statistics
db.raw_articles.aggregate([
  {
    $group: {
      _id: "$processed",
      count: { $sum: 1 }
    }
  }
])

// Reset all to unprocessed (if needed)
db.raw_articles.updateMany({}, {$set: {processed: false}})

// Delete all articles (clean start)
db.raw_articles.deleteMany({})
```

## Troubleshooting

### MongoDB not starting:
```powershell
# Start MongoDB service
net start MongoDB

# Stop MongoDB service
net stop MongoDB
```

### Connection errors:
- Check MongoDB is running: `Get-Service MongoDB`
- Check port 27017 is not blocked
- Verify connection string: `mongodb://localhost:27017/`
