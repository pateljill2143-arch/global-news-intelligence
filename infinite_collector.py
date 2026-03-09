"""
♾️  INFINITE DATA COLLECTOR
Runs 24/7 collecting data continuously - Gets 1000s of articles automatically!
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime
import time

SCRIPT_DIR = Path(__file__).parent

def run_collection():
    """Run massive data collection"""
    print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - Starting collection cycle...")
    
    subprocess.run([
        sys.executable, 
        str(SCRIPT_DIR / "collect_massive_data.py")
    ], input=b"y\n")  # Auto-confirm

def main():
    print("="*80)
    print("♾️  INFINITE DATA COLLECTOR - 24/7 AUTOMATIC MODE")
    print("="*80)
    print()
    print("This will run FOREVER, collecting massive amounts of data:")
    print()
    print("  • Collects from 40+ RSS feeds")
    print("  • Collects from 3 APIs with 100+ topics")
    print("  • Runs every 6 hours (to respect API limits)")
    print("  • 100% English-only")
    print("  • Auto-stores in MongoDB")
    print()
    print("⏰ Schedule:")
    print("  • Run 1: Immediate")
    print("  • Run 2: +6 hours")
    print("  • Run 3: +12 hours")
    print("  • Run 4: +18 hours")
    print("  • Continues forever...")
    print()
    print("📊 Expected data collection:")
    print("  • Per cycle: 2,000-10,000 articles")
    print("  • Per day: 8,000-40,000 articles")
    print("  • Per week: 56,000-280,000 articles")
    print()
    print("⚠️  Press Ctrl+C to stop anytime")
    print("="*80)
    
    try:
        input("\n▶️  Start infinite collection? Press ENTER...")
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled")
        return
    
    # Run immediately
    print("\n🚀 CYCLE #1 - Initial collection...")
    run_collection()
    
    # Continue forever
    cycle = 2
    wait_hours = 6
    
    while True:
        try:
            wait_seconds = wait_hours * 3600
            next_run = datetime.now().timestamp() + wait_seconds
            next_run_time = datetime.fromtimestamp(next_run).strftime('%Y-%m-%d %H:%M:%S')
            
            print("\n" + "="*80)
            print(f"💤 Waiting {wait_hours} hours until next collection...")
            print(f"   Next run: {next_run_time}")
            print(f"   Press Ctrl+C to stop")
            print("="*80)
            
            time.sleep(wait_seconds)
            
            print(f"\n🚀 CYCLE #{cycle} - Starting collection...")
            run_collection()
            
            cycle += 1
            
        except KeyboardInterrupt:
            print("\n\n⏹️  Infinite collector stopped")
            print(f"Total cycles completed: {cycle - 1}")
            print(f"Stopped at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            break

if __name__ == "__main__":
    main()
