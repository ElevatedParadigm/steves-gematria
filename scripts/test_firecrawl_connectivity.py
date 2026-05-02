#!/usr/bin/env python3
"""
Firecrawl API Connectivity Test — Debug Cloud API Issues
Tests different endpoints and formats to identify the correct API structure
"""

import json
import urllib.request
from pathlib import Path

# ============================================================================
# FIRECRAWL CONFIGURATION TESTING
# ============================================================================

API_KEYS = {
    "env_file": "/home/avalonas/.hermes/.env",
    "env_var": "FIRECRAWL_API_KEY"
}

# Try different endpoint formats
TEST_ENDPOINTS = {
    "cloud_search_v1": (
        "https://api.firecrawl.dev/v1/search",
        {"query": "test query"},
        {}
    ),
    "cloud_search_v1_with_options": (
        "https://api.firecrawl.dev/v1/search",
        {"query": "test 124 gematria", "options": {"pageOptions": {"maxNumberOfPages": 1}}},
        {}
    ),
    "cloud_extract_v1": (
        "https://api.firecrawl.dev/v1/extract",
        {"url": "https://www.wikipedia.org/wiki/Firecrawl"},
        {}
    ),
    "cloud_health_v1": (
        "https://api.firecrawl.dev/v1/health",
        {},
        {}
    )
}

# ============================================================================
# API CLIENT
# ============================================================================

class FirecrawlDebugClient:
    """Debug client for testing Firecrawl API connectivity"""
    
    def __init__(self):
        self.api_key = None
        self.env_file = Path(API_KEYS["env_file"])
        
    def load_api_key(self):
        """Load API key from environment or .env file"""
        # Try .env file first
        try:
            with open(self.env_file, 'r') as f:
                for line in f:
                    if line.startswith('FIRECRAWL_API_KEY='):
                        value = line.split('=', 1)[1].strip()
                        # Remove quotes
                        value = value.strip('"\'')
                        self.api_key = value
                        print(f"✅ API key found in .env file")
                        return True
        except FileNotFoundError:
            pass
        
        # Try environment variable
        import os
        self.api_key = os.getenv(API_KEYS["env_var"])
        
        if self.api_key:
            print(f"✅ API key found in environment variable")
            return True
        
        print(f"❌ No FIRECRAWL_API_KEY configured")
        print(f"   Expected in: {self.env_file}")
        print(f"   Or environment variable: {API_KEYS['env_var']}")
        return False
    
    def make_request(self, url: str, payload: dict, method: str = "POST") -> dict:
        """Make HTTP request to Firecrawl API"""
        
        if not self.api_key:
            raise ValueError("No API key configured")
        
        try:
            # Prepare headers
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # Build request body
            req_body = json.dumps(payload).encode('utf-8')
            
            # Make request
            req = urllib.request.Request(
                url, 
                data=req_body, 
                headers=headers,
                method=method
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                status = response.status
                
                if status == 200:
                    data = json.loads(response.read())
                    return {
                        "status": "success",
                        "http_status": status,
                        "data": data
                    }
                else:
                    error_data = response.read()
                    try:
                        error_json = json.loads(error_data)
                        return {
                            "status": "error",
                            "http_status": status,
                            "error_message": str(error_json.get('error', '')),
                            "raw_response": error_json
                        }
                    except:
                        return {
                            "status": "error",
                            "http_status": status,
                            "error_message": error_data.decode('utf-8')
                        }
                        
        except urllib.error.HTTPError as e:
            return {
                "status": "error",
                "http_status": e.code,
                "reason": str(e.reason),
                "read_error": True  # Can't read response body
            }
            
        except Exception as e:
            return {
                "status": "error",
                "reason": str(type(e).__name__),
                "message": str(e)
            }

# ============================================================================
# MAIN TESTING FUNCTION
# ============================================================================

def main():
    """Main test function"""
    
    print("=" * 70)
    print("🔬 FIRECRAWL API CONNECTIVITY TEST")
    print("=" * 70)
    print()
    
    # Load API key
    client = FirecrawlDebugClient()
    if not client.load_api_key():
        print("\n⚠️  Cannot test without API key")
        return
    
    print(f"API Key Status: ✓ Loaded from {API_KEYS['env_file']}")
    print()
    
    # Test each endpoint
    results = {}
    
    for name, (url, payload, options) in TEST_ENDPOINTS.items():
        print("=" * 70)
        print(f"📡 Testing: {name}")
        print(f"URL: {url}")
        print()
        
        try:
            result = client.make_request(url, payload)
            
            if "status" in result and result["status"] == "success":
                print(f"✅ SUCCESS (HTTP {result['http_status']})")
                
                # Display response data (truncated for readability)
                if "data" in result:
                    data = result["data"]
                    
                    if isinstance(data, dict):
                        # Handle single object responses
                        url_key = next((k for k in data.keys() if 'url' in k.lower()), "")
                        print(f"\n📄 Response structure:")
                        
                        for key in list(data.keys())[:5]:  # Show first 5 keys
                            value = data[key]
                            if isinstance(value, str):
                                print(f"   ├─ {key}: {value[:60]}...")
                            elif isinstance(value, list):
                                print(f"   ├─ {key}: [{len(value)} items]")
                            else:
                                print(f"   ├─ {key}: {str(value)[:40]}...")
                    elif isinstance(data, list) and len(data) > 0:
                        # Handle array responses
                        item = data[0] if isinstance(data[0], dict) else data[0]
                        print(f"\n📄 Response structure (first item):")
                        
                        for key in list(item.keys())[:5]:
                            value = item[key]
                            if isinstance(value, str):
                                print(f"   ├─ {key}: {value[:60]}...")
                            else:
                                print(f"   ├─ {key}: [{type(value).__name__}]")
                    
            elif "status" in result and result["status"] == "error":
                print(f"❌ ERROR (HTTP {result.get('http_status', 'N/A')})")
                
                if "error_message" in result:
                    error_msg = result["error_message"]
                    # Truncate very long errors
                    if len(error_msg) > 200:
                        print(f"   Error message: {error_msg[:200]}...")
                    else:
                        print(f"   Error message: {error_msg}")
                
                if "reason" in result and result["read_error"]:
                    print(f"⚠️  Could not read response body (check authorization)")
            
        except Exception as e:
            print(f"❌ EXCEPTION: {type(e).__name__}: {e}")
        
        print()
    
    # Summary
    print("=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    success_count = sum(1 for r in results.values() if r.get("status") == "success")
    error_count = sum(1 for r in results.values() if r.get("status") == "error")
    
    print(f"Successful Tests: {success_count}/{len(results)}")
    print(f"Failing Tests: {error_count}/{len(results)}")
    print()
    
    # Recommendations based on results
    recommendations = []
    
    for name, result in results.items():
        if result["status"] == "error":
            reason = result.get("reason", "Unknown error")
            
            if "Authorization" in str(reason):
                recommendations.append(
                    "❗ Check FIRECRAWL_API_KEY environment variable or .env file"
                )
            elif "404" in str(result):
                recommendations.append(
                    "❗ 404 error — API endpoint may be deprecated or wrong version"
                )
            elif "429" in str(result) or "rate" in str(reason).lower():
                recommendations.append("⚠️  Rate limit exceeded — wait before retrying")
    
    if recommendations:
        print("\n📝 RECOMMENDATIONS:")
        for rec in recommendations:
            print(f"   {rec}")
    else:
        print("\n✅ All tests completed successfully!")
    
    # Save test results
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = Path.home() / ".hermes" / "gematria" / "test_results"
    results_file.mkdir(parents=True, exist_ok=True)
    
    with open(results_file / f"firecrawl_connectivity_test_{timestamp}.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📝 Test results saved to: {results_file}/firecrawl_connectivity_test_{timestamp}.json")

if __name__ == "__main__":
    main()
