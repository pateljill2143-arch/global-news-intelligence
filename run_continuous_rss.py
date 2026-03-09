"""
CONTINUOUS RSS MONITORING - Real-time Dynamic Data
Monitors RSS feeds every 10 minutes and auto-processes new articles
TRUE DYNAMIC SYSTEM - NO API RATE LIMITS!
"""

import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
UPDATE_INTERVAL = 600  # 10 minutes (600 seconds)

def run_rss_collection():
    """Collect from RSS feeds"""
    print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - Checking RSS feeds...", flush=True)
    
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "collect_rss.py")],
        capture_output=True,
        text=True,
        cwd=str(SCRIPT_DIR)
    )
    
    # Extract summary
    for line in result.stdout.split('\n'):
        if "New articles stored:" in line or "Total articles fetched:" in line:
            print(f"  {line.strip()}", flush=True)

def run_processing():
    """Process unprocessed articles"""
    print(f"  🤖 Processing new articles...", flush=True)
    
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "process_articles.py")],
        capture_output=True,
        text=True,
        cwd=str(SCRIPT_DIR)
    )
    
    for line in result.stdout.split('\n'):
        if "Processed" in line and "articles" in line:
            print(f"  {line.strip()}", flush=True)

def main():
    print("="*80)
    print("🌐 REAL-TIME NEWS INTELLIGENCE SYSTEM")
    print("="*80)
    print("\n📡 RSS FEED MONITORING (No API Limits!)")
    print(f"  • Update Interval: {UPDATE_INTERVAL // 60} minutes")
    print(f"  • Sources: 20+ RSS feeds (BBC, Reuters, CNN, Al Jazeera, etc.)")
    print(f"  • Auto-processing: Enabled")
    print("\n⏰ System will update every {} minutes".format(UPDATE_INTERVAL // 60))
    print("  Press Ctrl+C to stop\n")
    
    # Run immediately
    print("🚀 Initial collection...", flush=True)
    run_rss_collection()
    run_processing()
    
    # Continuous monitoring
    iteration = 1
    while True:
        try:
            print(f"\n{'='*80}")
            print(f"💤 Waiting {UPDATE_INTERVAL // 60} minutes until next update...")
            print(f"   Next update at: {datetime.fromtimestamp(time.time() + UPDATE_INTERVAL).strftime('%H:%M:%S')}")
            print(f"{'='*80}\n", flush=True)
            
            time.sleep(UPDATE_INTERVAL)
            
            print(f"\n🔄 UPDATE CYCLE #{iteration}")
            run_rss_collection()
            run_processing()
            
            iteration += 1
            
        except KeyboardInterrupt:
            print("\n\n⏹️  Continuous monitoring stopped")
            print(f"Total update cycles: {iteration - 1}")
            print(f"Stopped at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            break

if __name__ == "__main__":
    main()
