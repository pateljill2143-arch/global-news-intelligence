"""
CONTINUOUS DATA COLLECTION - Dynamic News Intelligence System
Runs the pipeline on a schedule to keep data fresh and dynamic
"""

import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
import schedule

SCRIPT_DIR = Path(__file__).parent

def run_pipeline():
    """Execute the full pipeline"""
    print("\n" + "="*80)
    print(f"🔄 PIPELINE EXECUTION - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    try:
        # Run collection
        print("\n📰 Collecting new articles...")
        result = subprocess.run(
            [sys.executable, str(SCRIPT_DIR / "collect_news_multisource.py")],
            capture_output=True,
            text=True,
            cwd=str(SCRIPT_DIR)
        )
        
        if "New articles stored:" in result.stdout:
            # Extract count
            for line in result.stdout.split('\n'):
                if "New articles stored:" in line:
                    print(f"  ✓ {line.strip()}")
        
        # Run processing
        print("\n🤖 Processing articles and building knowledge graph...")
        result = subprocess.run(
            [sys.executable, str(SCRIPT_DIR / "process_articles.py")],
            capture_output=True,
            text=True,
            cwd=str(SCRIPT_DIR)
        )
        
        if "Processed" in result.stdout:
            for line in result.stdout.split('\n'):
                if "Processed" in line and "articles" in line:
                    print(f"  ✓ {line.strip()}")
        
        print(f"\n✅ Pipeline completed at {datetime.now().strftime('%H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ Pipeline error: {e}")

def main():
    print("="*80)
    print("🌐 DYNAMIC NEWS INTELLIGENCE SYSTEM - CONTINUOUS MODE")
    print("="*80)
    print("\n📅 SCHEDULE CONFIGURATION:")
    print("  • Every 1 hour  - Collect fresh news")
    print("  • Every 1 hour  - Process and update knowledge graph")
    print("  • API Limits: Guardian (500/day), GNews (100/day)")
    print("\n⏰ Starting continuous monitoring...")
    print("  Press Ctrl+C to stop\n")
    
    # Schedule options - choose one:
    
    # Option 1: Run every hour (recommended for free API limits)
    schedule.every(1).hours.do(run_pipeline)
    
    # Option 2: Run every 30 minutes (more frequent)
    # schedule.every(30).minutes.do(run_pipeline)
    
    # Option 3: Run every 6 hours (conservative)
    # schedule.every(6).hours.do(run_pipeline)
    
    # Option 4: Run at specific times
    # schedule.every().day.at("09:00").do(run_pipeline)
    # schedule.every().day.at("15:00").do(run_pipeline)
    # schedule.every().day.at("21:00").do(run_pipeline)
    
    # Run immediately on startup
    print("🚀 Running initial pipeline execution...")
    run_pipeline()
    
    # Keep running scheduled tasks
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Continuous monitoring stopped by user")
        print(f"Last run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
