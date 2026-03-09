"""
🔧 QUICK FIX - Install All Packages in Virtual Environment
Run this if you get "No module named" errors
"""

import subprocess
import sys
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "Scripts" / "python.exe"

print("="*80)
print("🔧 INSTALLING ALL REQUIRED PACKAGES")
print("="*80)
print()

if VENV_PYTHON.exists():
    print(f"✓ Virtual environment found at: {VENV_PYTHON}")
    print()
    print("📦 Installing packages from requirements.txt...")
    print("-"*80)
    
    subprocess.run([
        str(VENV_PYTHON),
        "-m", "pip", "install", "-r", "requirements.txt"
    ])
    
    print()
    print("="*80)
    print("✅ INSTALLATION COMPLETE!")
    print("="*80)
    print()
    print("Now you can run:")
    print("  python complete_pipeline.py")
    print("  OR")
    print("  Double-click: RUN_COMPLETE.bat")
    print()
    
else:
    print("⚠️  Virtual environment not found!")
    print("   Creating virtual environment...")
    
    # Create venv
    subprocess.run([sys.executable, "-m", "venv", ".venv"])
    
    print("   Installing packages...")
    subprocess.run([
        str(VENV_PYTHON),
        "-m", "pip", "install", "-r", "requirements.txt"
    ])
    
    print()
    print("✅ Virtual environment created and packages installed!")
    print()

print("="*80)
input("Press ENTER to exit...")
