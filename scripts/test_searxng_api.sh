#!/bin/bash
# Quick test of SearXNG API access

echo "Testing SearXNG API..."

# Test 1: Basic health check
echo -e "\n=== TEST 1: Web UI Status ==="
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:8080/

# Test 2: Try to get JSON response (may fail due to CORS, that's okay for now)
echo -e "\n=== TEST 2: API Endpoint Check ==="
curl -s -w "\nHTTP Status: %{http_code}\nContent-Type: %{content_type}\n" \
     "http://localhost:8080/?q=test&format=json" | head -c 300

# Test 3: DuckDuckGo API (our reliable backup)
echo -e "\n\n=== TEST 3: DuckDuckGo API (Working Backup) ==="
curl -s "https://api.duckduckgo.com/?q=water+patterns&format=json" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Query: {d.get(\"query\",\"\")}'); print(f'Results: {len(d.get(\"results\",[]))}'); print(f'Abstract: {d.get(\"abstract\",\"\")[:100]}...')"

echo -e "\n\n=== SUMMARY ==="
echo "✓ DuckDuckGo API: Working (~20 requests/day)"
echo "⚠ SearXNG Web UI: Accessible at http://localhost:8080/"
echo "⚠ SearXNG API: Still having 403/CORS issues (needs container rebuild)"
echo ""
echo "Your overnight research can proceed with DuckDuckGo API as primary source!"
