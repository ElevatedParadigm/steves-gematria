"""
Overnight Research Protocol - Option 1 Implementation
Uses Firecrawl API with proper error handling and result aggregation
"""

import os
from pathlib import Path
import json
from datetime import datetime, timedelta
import time

# ============== DATABASE AND CONFIGURATION ==============
DATABASE_FILE = str(Path.home() / ".hermes/gematria/database/gematria_database.json")

CORE_SYMBOLS = [124, 963, 55, 111, 279, 666]
SYMBOL_NAMES = {
    124: "Universal Bridge",
    963: "Completion Threshold", 
    55: "Elemental Cycle",
    111: "Pattern Amplifier",
    279: "Cycle Turning Point",
    666: "Wholeness Marker"
}

DOMAINS = ["biblical", "military", "elemental", "geographic", "historical"]

# Firecrawl API configuration from ~/.hermes/.env
ENV_FILE = str(Path.home() / ".hermes" / ".env")

def load_env_values():
    """Load specific environment variables safely."""
    values = {}
    try:
        with open(ENV_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    values[key.strip()] = value.strip()
    except Exception as e:
        print(f"⚠️ Warning: Could not read .env file: {e}")
    
    return values

def firecrawl_search(query: str) -> dict:
    """Search via Firecrawl self-hosted endpoint."""
    
    env_vars = load_env_values()
    
    # Try to get API key and base URL
    api_key = env_vars.get('FIRECRAWL_API_KEY', '').strip().replace('*', 'YOUR_KEY')  # Replace redacted value
    base_url = env_vars.get('FIRECRAWL_API_URL', 'http://localhost:3002/api/v1')
    
    print(f"    🔧 Using Firecrawl endpoint: {base_url}")
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    # Add Authorization if API key exists and is not placeholder
    if api_key.lower() != 'your_key'.lower():
        headers['Authorization'] = f'Bearer {api_key}'
    
    payload = {
        "query": query,
        "options": {
            "page": {
                "maxResults": 10
            }
        },
        "scrapeOptions": {}
    }
    
    try:
        import urllib.request
        
        req = urllib.request.Request(
            base_url,
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            print(f"    ✓ Firecrawl Search Success")
            print(f"    - Results returned: {len(result.get('data', []))}")
            return result
            
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print(f"    ⚠️ Unauthorized - API key may be invalid or not set")
        elif e.code == 404:
            print(f"    ❌ Not Found (endpoint or resource)")
        else:
            print(f"    ❌ HTTP {e.code}: {e.reason}")
        return {"success": False, "error": f"HTTP {e.code}: {e.reason}"}
        
    except urllib.error.URLError as e:
        print(f"    ❌ Connection Error: {str(e.reason)}")
        return {"success": False, "error": "Connection failed"}
        
    except json.JSONDecodeError as e:
        print(f"    ❌ Invalid JSON response")
        return {"success": False, "error": f"Invalid response format"}
        
    except Exception as e:
        print(f"    ❌ Search error ({type(e).__name__}): {str(e)}")
        return {"success": False, "error": str(e)}
