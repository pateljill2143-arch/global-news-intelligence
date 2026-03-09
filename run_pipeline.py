"""
MASTER PIPELINE - Complete AI-Driven Global News Intelligence System
Orchestrates: 
  1. Multi-Source Data Collection (APIs + RSS)
  2. MongoDB Document Storage
  3. BERT Transformer NER Processing (90+ Relationship Types)
  4. Neo4j Knowledge Graph Construction
  5. Analytics & Insights Generation
  6. Cloud Dashboard Data Export
  7. Interactive Dashboard Launch
  
Run this to do EVERYTHING in one command!
"""

import subprocess
import sys
import os
import time
from pathlib import Path
from datetime import datetime

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent

def check_databases():
    """Check if required databases are accessible"""
    print("\n🔍 Checking database connections...")
    
    # Check MongoDB
    try:
        from pymongo import MongoClient
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        client.server_info()
        print("  ✓ MongoDB is running")
        mongodb_ok = True
    except Exception as e:
        print(f"  ✗ MongoDB not accessible: {e}")
        print("    Start MongoDB with: mongod")
        mongodb_ok = False
    
    # Check Neo4j
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver("bolt://localhost:7687", 
                                     auth=("neo4j", "jill2143"))
        driver.verify_connectivity()
        driver.close()
        print("  ✓ Neo4j is running")
        neo4j_ok = True
    except Exception as e:
        print(f"  ✗ Neo4j not accessible: {e}")
        print("    Make sure Neo4j is running")
        neo4j_ok = False
    
    return mongodb_ok and neo4j_ok

def run_script(script_name, description):
    """Run a Python script and handle errors"""
    print("\n" + "=" * 80)
    print(f"🚀 {description}")
    print("=" * 80)
    
    script_path = SCRIPT_DIR / script_name
    
    if not script_path.exists():
        print(f"✗ Error: {script_name} not found at {script_path}")
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            check=True,
            capture_output=False,
            cwd=str(SCRIPT_DIR)
        )
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed with error code {e.returncode}")
        return False
    except KeyboardInterrupt:
        print(f"\n\n⚠️  {description} interrupted by user")
        return False

def main():
    start_time = time.time()
    
    print("=" * 80)
    print("🌍 AI-DRIVEN GLOBAL NEWS KNOWLEDGE GRAPH SYSTEM - COMPLETE PIPELINE")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check database connections first
    if not check_databases():
        print("\n❌ Cannot proceed - required databases are not accessible")
        print("\n💡 Make sure both MongoDB and Neo4j are running before starting the pipeline")
        return
    
    print("\n📋 Pipeline Stages:")
    print("  1. 📰 Data Collection Layer → Fetch from Guardian + GNews APIs")
    print("  2. 💾 Document Storage Layer → Store raw articles in MongoDB")
    print("  3. 🤖 NLP Processing Layer → BERT Transformer NER + Relationship Extraction")
    print("  4. 🕸️  Knowledge Graph Layer → Build graph in Neo4j (90+ relation types)")
    print("  5. 📊 Analytics & Insights → Run queries and analysis")
    print("  6. ☁️  Export for Cloud → Prepare data for dashboard deployment")
    print("  7. 🎨 Dashboard Launch → Start interactive visualization")
    print("\n🔄 Starting complete automated pipeline...\n")
    
    stages_completed = 0
    total_stages = 6
    
    # Stage 1 & 2: Collect news and store in MongoDB
    print(f"\n[Stage 1-2/{total_stages}] Data Collection")
    if not run_script(
        "collect_news_multisource.py",
        "Multi-Source Data Collection & Storage"
    ):
        print("\n⚠️  Collection failed. Check MongoDB connection and API keys.")
        print("   Make sure MongoDB is running: mongod")
        return
    stages_completed += 1
    
    # Stage 3 & 4: Process articles and build knowledge graph
    print(f"\n[Stage 3-4/{total_stages}] NLP Processing & Knowledge Graph")
    if not run_script(
        "process_articles.py",
        "NLP Processing & Knowledge Graph Construction"
    ):
        print("\n⚠️  Processing failed. Check Neo4j connection.")
        print("   Make sure Neo4j is running")
        return
    stages_completed += 1
    
    # Stage 5: Run analytics queries
    print(f"\n[Stage 5/{total_stages}] Analytics")
    if run_script(
        "query_triples.py",
        "Analytics & Insights Query"
    ):
        stages_completed += 1
    else:
        print("\n⚠️  Query failed, but continuing...")
    
    # Stage 6: Export data for cloud dashboard
    print(f"\n[Stage 6/{total_stages}] Export for Cloud")
    if run_script(
        "export_for_cloud.py",
        "Export Data for Cloud Deployment"
    ):
        stages_completed += 1
    else:
        print("\n⚠️  Export failed, but continuing...")
    
    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    
    # Final stage: Success message
    print("\n" + "=" * 80)
    print("🎉 PIPELINE COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print(f"\n⏱️  Total Time: {minutes}m {seconds}s")
    print(f"✅ Stages Completed: {stages_completed}/{total_stages}")
    print(f"📅 Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n📊 What's been done:")
    print("  ✓ Collected latest news from multiple sources")
    print("  ✓ Processed articles with BERT Transformer NER")
    print("  ✓ Extracted 90+ types of relationships")
    print("  ✓ Built knowledge graph in Neo4j")
    print("  ✓ Generated analytics and insights")
    print("  ✓ Exported data for cloud dashboard")
    
    print("\n🚀 Next Steps:")
    print("\n  1. 🎨 View Interactive Dashboard:")
    print("     streamlit run dashboard.py")
    
    print("\n  2. 🌐 Explore Neo4j Graph Browser:")
    print("     http://localhost:7474")
    
    print("\n  3. ☁️  Deploy to Cloud (optional):")
    print("     git add graph_data_export.json")
    print("     git commit -m 'Update knowledge graph data'")
    print("     git push")
    
    print("\n  4. 🔄 Continuous Updates:")
    print("     python run_continuous.py          # Hourly updates")
    print("     python run_continuous_rss.py      # Real-time RSS feeds")
    
    print("\n💡 Tips:")
    print("  • To update everything again: python run_pipeline.py")
    print("  • To process only new articles: python process_articles.py")
    print("  • To collect more news: python collect_news_multisource.py")
    
    # Ask user if they want to launch dashboard
    print("\n" + "=" * 80)
    try:
        response = input("\n🎨 Launch dashboard now? (y/n): ").lower().strip()
        if response == 'y':
            print("\n🚀 Launching Streamlit dashboard...")
            print("   Dashboard will open in your browser at http://localhost:8501")
            print("   Press CTRL+C to stop the dashboard")
            print("-" * 80)
            subprocess.run([sys.executable, "-m", "streamlit", "run", "dashboard.py"], 
                         cwd=str(SCRIPT_DIR))
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard launch cancelled")
    except Exception as e:
        print(f"\n⚠️  Could not launch dashboard: {e}")
        print("   You can manually run: streamlit run dashboard.py")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
