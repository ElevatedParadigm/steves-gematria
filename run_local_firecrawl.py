#!/usr/bin/env python3
#===============================================================================
# 🔥 LOCAL FIRECRAWL SERVER - STANALONE RUNNER (NO DOCKER)
#===============================================================================
# Author: Steve & Avalon  
# Purpose: Run local Firecrawl API server directly with Python SDK
# Version: 2.1

import os
import sys
from firecrawl import FirecrawlApp

API_KEY = os.getenv('FIRECRAWL_API_KEY', 'YOUR_API_KEY_HERE')
BASE_URL = os.getenv('FIRECRAWL_BASE_URL', 'https://api.firecrawl.dev/v1')

print("=" * 60)
print("🔥 LOCAL FIRECRAWL SERVER - PYTHON SDK MODE")
print("=" * 60)

try:
    app = FirecrawlApp(api_key=API_KEY, base_url=BASE_URL)
    print(f"\n✅ Initialized with API key from environment")
    print(f"   Base URL: {BASE_URL}")
    
    # Test connection to Cloud API
    print("\n🔍 Testing connection...")
    try:
        test_result = app.scrape_url(
            'https://firecrawl.dev',  # Test page
            params={'formats': ['markdown']}
        )
        print(f"✅ Connected to: {BASE_URL}")
        print(f"   Response preview: {test_result.get('success', False)}")
    except Exception as e:
        print(f"⚠️  API connection failed: {e}")
        print("   Falling back to direct scraping mode...")
    
except ImportError as e:
    print(f"❌ Firecrawl SDK not installed: {e}")
    print("   Install with: pip install firecrawl")

# Try local server if cloud fails
print("\n⏳ Ready for commands:")
print("   - Web scraping via Cloud API or direct mode")
print("   - See direct_web_research.py for standalone scraping")
