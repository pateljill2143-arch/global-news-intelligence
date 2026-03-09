"""
🧹 CLEANUP SCRIPT - Remove Unwanted Files
Removes old, redundant, and test files to keep project clean
"""

import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

# Files to remove (old/redundant/test files)
FILES_TO_REMOVE = [
    # OLD/LEGACY SCRIPTS
    "trans.py",                          # Old legacy approach
    "collect_news.py",                   # Replaced by collect_news_multisource.py
    
    # TEST FILES
    "test_apis.py",
    "test_improved_relations.py",
    "test_spacy_ner.py",
    "test_english_pipeline.py",
    
    # DOCUMENTATION-ONLY FILES (info is elsewhere)
    "ENGLISH_ONLY_VERIFICATION.py",     # Info in QUICK_START.txt
    "SYSTEM_ARCHITECTURE.py",            # Info in README.md
    "QUICK_STEPS.txt",                   # Replaced by QUICK_START.txt
    
    # REDUNDANT BATCH FILES
    "run_everything.bat",                # Have START_PIPELINE.bat/.py
    "update_dashboard.bat",              # Single command, not needed
    "setup_github.bat",                  # One-time setup
    "push_to_github.bat",                # Use git directly
]

def main():
    print("="*80)
    print("🧹 PROJECT CLEANUP - REMOVING UNWANTED FILES")
    print("="*80)
    print()
    
    print("Files to be removed:")
    print("-"*80)
    
    for filename in FILES_TO_REMOVE:
        filepath = SCRIPT_DIR / filename
        if filepath.exists():
            print(f"  ❌ {filename}")
        else:
            print(f"  ⚠️  {filename} (already deleted)")
    
    print()
    print("="*80)
    
    # Ask for confirmation
    try:
        response = input("\n⚠️  Delete these files? (yes/no): ").lower().strip()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        return
    
    if response not in ['yes', 'y']:
        print("\n❌ Cleanup cancelled - no files removed")
        return
    
    # Remove files
    print()
    print("="*80)
    print("🗑️  REMOVING FILES...")
    print("="*80)
    print()
    
    removed_count = 0
    failed_count = 0
    
    for filename in FILES_TO_REMOVE:
        filepath = SCRIPT_DIR / filename
        
        if filepath.exists():
            try:
                filepath.unlink()
                print(f"✅ Removed: {filename}")
                removed_count += 1
            except Exception as e:
                print(f"❌ Failed to remove {filename}: {e}")
                failed_count += 1
        else:
            print(f"⏭️  Skipped: {filename} (doesn't exist)")
    
    # Summary
    print()
    print("="*80)
    print("📊 CLEANUP SUMMARY")
    print("="*80)
    print(f"✅ Files removed: {removed_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"📁 Project is now cleaner!")
    print()
    
    print("="*80)
    print("✅ CLEANUP COMPLETE!")
    print("="*80)
    print()
    print("Your project now contains only essential files:")
    print()
    print("📂 CORE FUNCTIONALITY:")
    print("  ✓ collect_rss.py")
    print("  ✓ collect_news_multisource.py")
    print("  ✓ process_articles.py")
    print("  ✓ dashboard.py / dashboard_cloud.py")
    print()
    print("🔄 PIPELINE & AUTOMATION:")
    print("  ✓ run_pipeline.py")
    print("  ✓ run_continuous.py / run_continuous_rss.py")
    print("  ✓ START_PIPELINE.py / QUICK_RUN.py")
    print()
    print("🔧 UTILITIES:")
    print("  ✓ verify_english_only.py")
    print("  ✓ check_data_freshness.py")
    print("  ✓ check_mongodb.py")
    print("  ✓ clean_non_english_articles.py")
    print("  ✓ clear_neo4j.py")
    print()
    print("📊 ANALYTICS:")
    print("  ✓ query_neo4j.py")
    print("  ✓ query_triples.py")
    print()
    print("📄 DOCUMENTATION:")
    print("  ✓ README.md")
    print("  ✓ QUICK_START.txt")
    print("  ✓ requirements.txt")
    print()
    print("="*80)
    
    input("\nPress ENTER to exit...")

if __name__ == "__main__":
    main()
