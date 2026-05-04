#!/usr/bin/env python3
"""
🌙 STEVE'S GEMATRIA UNIFIED OVERNIGHT RESEARCH PIPELINE - CONTINUOUS LOOP MODE
Continuous Loop Mode (repeat=9999) with symbol-keying strategies, hidden layering detection,
and image-seed bootstrapping from existing vault.

Configuration:
- 30 items per cycle processing rate
- Hidden layering detection across all core symbols (124, 666, 963, 55, 111, 279)
- Symbol-keying strategies as default search terms (from current session)
- Git version tracking enabled
- Continuous loop mode with repeat=9999

Usage: python unified_loop_runner.py [--mode overnight]
"""

import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime

REPO_PATH = Path("/home/avalonas/.hermes/gematria/unified_overnight_research")
SCRIPTS_DIR = REPO_PATH / "scripts"
LOG_DIR = REPO_PATH / "logs"

def main():
    print("\n" + "="*80)
    print("🌙 STEVE'S GEMATRIA UNIFIED OVERNIGHT RESEARCH PIPELINE")
    print("🔄 CONTINUOUS LOOP MODE (repeat=9999)")
    print("="*80 + "\n")
    
    # Check if hermes_tools venv is available
    hermes_venv = Path("/home/avalonas/.hermes/hermes-agent/venv/bin/python")
    repo_venv = REPO_PATH / "venv" / "bin" / "python"
    
    python_cmd = None
    
    if hermes_venv.exists():
        print(f"✅ Found Hermes Agent venv: {hermes_venv}")
        python_cmd = hermes_venv
    elif repo_venv.exists():
        print(f"✅ Found repo venv: {repo_venv}")
        python_cmd = repo_venv
    else:
        print("⚠️ No virtual environment found!")
        print("Using system Python - may fail if hermes_tools not available")
        python_cmd = sys.executable
    
    loop_runner = SCRIPTS_DIR / "overnight_research_loop.py"
    
    if not loop_runner.exists():
        print(f"❌ overnight_research_loop.py not found at: {loop_runner}")
        return False
    
    print(f"\n📄 Running: {loop_runner.name}")
    print("-"*80)
    
    # Execute the loop runner script
    try:
        result = subprocess.run(
            [python_cmd, str(loop_runner)],
            check=False,
            capture_output=False,
            text=True,
            cwd=str(REPO_PATH)
        )
        
        print(f"\n✅ Execution completed with exit code: {result.returncode}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error executing loop runner: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
