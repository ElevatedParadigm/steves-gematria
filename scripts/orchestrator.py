#!/usr/bin/env python3
"""
Gematria Orchestrator - Central coordinator for overnight research loops
Steve's Gematria Visual Archive System
"""

import sys
from pathlib import Path

import sys
from pathlib import Path

# Import from Hermes venv (correct location)
HERMES_VENV_PATH = str(Path.home() / ".hermes/hermes-agent/venv/lib/python3.12/site-packages")
if HERMES_VENV_PATH not in sys.path:
    sys.path.insert(0, HERMES_VENV_PATH)

from hermes_tools import terminal, search_files, write_file, read_file, web_search, web_extract

print("🔮 Gematria Orchestrator Loaded Successfully!")
# Script paths resolved via pathlib
SCRIPTS_DIR = Path(__file__).parent
BASE_DIR = SCRIPTS_DIR.parent  # /home/avalonas/.hermes/gematria
print(f"   Base Directory: {BASE_DIR}")
print(f"   Scripts Directory: {SCRIPTS_DIR}")
