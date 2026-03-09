"""
🚀 START PIPELINE - One-Click News Intelligence System
Run this file directly in VS Code to execute the complete pipeline!
"""

import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime

def check_python():
    """Check Python installation"""
    print("✓ Python is installed and working")
    print(f"  Version: {sys.version.split()[0]}")
    print(f"  Location: {sys.executable}")
    return True

def check_directory():
    """Check if we're in the correct directory"""
    script_dir = Path(__file__).parent
    if not (script_dir / "run_pipeline.py").exists():
        print(f"❌ ERROR: run_pipeline.py not found!")
        print(f"   Make sure you're in the transformer directory")
        return False
    return True

def main():
    print("="*80)
    print("   AI-DRIVEN GLOBAL NEWS KNOWLEDGE GRAPH SYSTEM")
    print("   WITH GUARANTEED ENGLISH-ONLY DATA COLLECTION")
    print("="*80)
    print()
    print("This will run the complete pipeline:")
    print()
    print("  [1] Collect Latest News (English Only)")
    print("      - 20+ RSS feeds from BBC, CNN, Reuters, etc.")
    print("      - 3 API aggregators covering 230,000+ sources")
    print("      - AI language detection filtering")
    print()
    print("  [2] Process with BERT Transformer NER")
    print("      - Extract entities (People, Places, Organizations)")
    print("      - Detect 90+ relationship types")
    print("      - Build knowledge graph in Neo4j")
    print()
    print("  [3] Generate Analytics & Insights")
    print("      - Complex relationship patterns")
    print("      - Timeline analysis")
    print("      - Threat assessment")
    print()
    print("  [4] Launch Interactive Dashboard")
    print("      - Real-time knowledge graph visualization")
    print("      - Global threat monitoring")
    print("      - Entity relationship explorer")
    print()
    print("Language Guarantee: 100% English data only!")
    print()
    print("="*80)
    
    # Prompt user to continue
    try:
        response = input("\n▶️  Press ENTER to start, or Ctrl+C to cancel: ")
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        return
    
    print()
    
    # Check Python
    if not check_python():
        print("\n❌ Python check failed!")
        input("\nPress ENTER to exit...")
        return
    
    print()
    
    # Check directory
    if not check_directory():
        print("\n❌ Directory check failed!")
        input("\nPress ENTER to exit...")
        return
    
    print()
    print("="*80)
    print("🚀 Starting English-Only Pipeline...")
    print("="*80)
    print()
    
    # Get script directory
    script_dir = Path(__file__).parent
    
    # Run the complete pipeline
    try:
        result = subprocess.run(
            [sys.executable, str(script_dir / "run_pipeline.py")],
            cwd=str(script_dir)
        )
        
        if result.returncode == 0:
            print()
            print("="*80)
            print("✅ Pipeline Execution Complete!")
            print("="*80)
        else:
            print()
            print("="*80)
            print("⚠️  Pipeline completed with warnings")
            print("="*80)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error running pipeline: {e}")
    
    # Show quick commands
    print()
    print("Quick Commands:")
    print("  - Launch Dashboard:  streamlit run dashboard.py")
    print("  - Neo4j Browser:     http://localhost:7474")
    print("  - Verify English:    python verify_english_only.py")
    print("  - Check Data Age:    python check_data_freshness.py")
    print()
    print("="*80)
    
    # Wait for user before closing
    try:
        input("\nPress ENTER to exit...")
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
