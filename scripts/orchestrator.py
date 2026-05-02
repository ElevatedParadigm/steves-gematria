#!/usr/bin/env python3
"""
Gematria Orchestrator - Central coordinator for overnight research loops
Steve's Gematria Visual Archive System
"""

import sys
from pathlib import Path

# CRITICAL: Add parent directory to path BEFORE importing hermes_tools
SCRIPTS_DIR = Path(__file__).parent
BASE_DIR = SCRIPTS_DIR.parent  # /home/avalonas/.hermes/gematria
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR.parent))  # Add ~/.hermes for hermes_tools

# Now safe to import
from hermes_tools import execute_code, terminal, search_files, write_file, read_file

print("🔮 Gematria Orchestrator Loaded Successfully!")
print(f"   Base Directory: {BASE_DIR}")
print(f"   Scripts Directory: {SCRIPTS_DIR}")
