"""
🚀 QUICK START - Run complete pipeline immediately (no prompts)
Just click the play button ▶️ in VS Code!
"""

import subprocess
import sys
from pathlib import Path

# Get script directory
SCRIPT_DIR = Path(__file__).parent

print("🚀 Starting Complete English-Only News Pipeline...")
print("="*80)

# Run pipeline directly
subprocess.run([sys.executable, str(SCRIPT_DIR / "run_pipeline.py")])

print("\n✅ Done! Launch dashboard: streamlit run dashboard.py")
