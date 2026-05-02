# ============== DATABASE AND CONFIGURATION ==============
import os
import sys
from pathlib import Path
from datetime import datetime

# Database location
DATABASE_FILE = str(Path.home() / ".hermes/gematria/database/gematria_database.json")

# Core symbols and their symbolic meanings
CORE_SYMBOLS = [124, 963, 55, 111, 279, 666]
SYMBOL_NAMES = {
    124: "Universal Bridge",
    963: "Completion Threshold", 
    55: "Elemental Cycle",
    111: "Pattern Amplifier",
    279: "Cycle Turning Point",
    666: "Wholeness Marker"
}

# Domains for cross-domain analysis
DOMAINS = ["biblical", "military", "elemental", "geographic", "historical"]

# Search engine configuration - USE FIRECRAWL CLOUD API (more reliable)
USE_DB_AUTHENTICATION = os.getenv('USE_DB_AUTHENTICATION', 'false').lower() in ('true', '1', 'yes')

# Firecrawl cloud API endpoint (default for self-hosted or when local is unavailable)
FIRECRAWL_CLOUD_URL = "https://api.firecrawl.dev/v1"

# Fallback to SearXNG if Firecrawl fails
SEARXNG_URL = "http://localhost:8084/search"
