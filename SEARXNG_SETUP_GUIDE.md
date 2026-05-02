# 🔮 Steve's Gematria - Self-Hosted Web Search Setup

**Target:** SearXNG (Self-hosted, privacy-first, unlimited, free)  
**Status:** Ready for deployment  

---

## 📋 Solution Comparison

| Solution | Privacy | Unlimited | Local | Cost | Best For |
|----------|---------|-----------|-------|------|----------|
| **SearXNG** ✅ | ★★★★★ | Yes | Yes | Free | Your needs! |
| Serper.dev | ★★★★☆ | No* | No | $50/mo | Easy setup |
| DuckDuckGo API | ★★★★★ | No (rate-limited) | No | Free tier | Quick testing |
| Bing Search API | ★★★★☆ | No | No | Free/$299 | Enterprise |
| Firecrawl local | ★★★★☆ | Yes* | Yes | Free | If Docker works |

*Local instances have unlimited calls but require setup

---

## 🔧 Option 1: Deploy SearXNG (Recommended)

### Requirements:
- Docker + Docker Compose (already in your stack!)
- ~500MB RAM minimum
- Any port available (default: 8080)

### Step-by-Step Deployment:

```bash
# 1. Create searxng directory
cd /home/avalonas/.hermes/gematria
mkdir -p searxng/searxng-searxng/config

# 2. Download default config
wget -O searxng/searxng-searxng/docker-entrypoint.sh \
  https://raw.githubusercontent.com/searxng/searxng/stable/debian/bookworm/distroless/docker-entrypoint.sh

mkdir searxng/searxng-searxng/data

# 3. Configure instance (privacy-focused)
cat > searxng/searxng-searxng/config.yml << 'EOF'
usage_stats:
  send: false
default_theme: monochrome
brand: Steve's Gematria Search

searchengines:
  - name: duckduckgo
    engine: duckduckgo
    shortcut: ddg
    disabled: false
    weight: 100
    http_args:
      headers:
        Accept-Language: en-US,en;q=0.9

  - name: bing
    engine: bing
    shortcut: bing
    disabled: false
    weight: 80
    
  - name: google
    engine: google
    shortcut: ggl
    disabled: false
    weight: 70
    base_url: 'https://www.google.com/search'
    
  - name: startpage
    engine: startpage
    shortcut: sp
    disabled: false
    weight: 85
    parameters:
      q: '{query}&client=searxng'

# Privacy settings (default, no tracking)
enable_cors_header: true
cors_domain: "*"
EOF

echo "✅ SearXNG config created"
```

### Step 4: Create docker-compose.yml

```bash
cat > /home/avalonas/.hermes/gematria/searxng/docker-compose.yml << 'EOF'
version: '3.8'

services:
  searxng:
    image: docker.io/searxng/searxng:stable
    container_name: gematria-searxng
    volumes:
      - ./searxng/searxng/data:/data
      - ./searxng/searxng/config.yml:/etc/searxng/settings.yml:ro
    ports:
      - "8080:8080"
    environment:
      - SEARXNG_SETTINGS_FILE=/etc/searxng/settings.yml
    restart: unless-stopped

  redis:
    image: docker.io/library/redis:alpine
    container_name: gematria-searxng-redis
    ports:
      - "6380:6379"
    volumes:
      - ./searxng/searxng/data/redis:/data

EOF
echo "✅ Docker compose created"
```

### Step 5: Deploy with existing containers

```bash
cd /home/avalonas/.hermes/gematria/searxng
docker-compose up -d

# Wait for startup (should take ~30 seconds)
sleep 10
curl http://localhost:8080

echo "✅ SearXNG should be accessible at http://localhost:8080"
```

---

## 🔧 Option 2: Alternative - Local Firecrawl Fix

If your goal is to use Firecrawl specifically, we can try:

### Check what happened with containers:

```bash
# See if containers exist but aren't running
docker ps -a | grep firecrawl

# If they're not there, recreate them
cd /home/avalonas/.hermes/gematria
docker run -d \
  --name firecrawl-api-1 \
  -p 3002:3000 \
  -e FIRECRAWL_API_KEY='[REDACTED]' \
  -v $(pwd)/firecrawl:/app/storage \
  library/firecrawl/firecrawl:latest

# Wait for startup
sleep 15
curl http://localhost:3002/health
```

### Or try with existing containers from your gateway config:

Your current config.yaml shows:
```yaml
web:
  backend: firecrawl
```

Let me check if we can activate your existing Firecrawl setup.

---

## 🧪 Testing the Search System

Once deployed, test it:

```bash
# Test SearXNG endpoint
curl "http://localhost:8080/search?q=test&format=json" | jq .

# Or use API directly
curl "http://localhost:8080/api/http/duckduckgo" \
  -H "Content-Type: application/json" \
  -d '{"q": "fire symbolism"}' | jq .data.web
```

---

## 🔗 Integration with Your Existing Scripts

Update `hybrid_full_scan.py` to use SearXNG:

```python
def run_firecrawl_search(url, query, options=None):
    """Try Firecrawl first, fallback to SearXNG"""
    
    try:
        # Try local Firecrawl first (if containers are running)
        import requests
        
        if options is None:
            options = {'includePages': True, 'limit': 5}
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer YOUR_KEY'
        }
        
        payload = {
            'query': query,
            'options': options,
            'page': 1
        }
        
        search_url = url.rstrip('/') + '/v1/search'
        
        response = requests.post(search_url, json=payload, headers=headers, timeout=120)
        
        if response.status_code == 200:
            return response.json()
        
    except Exception as e:
        pass  # Fallback to SearXNG
    
    # Fallback to SearXNG API
    import urllib.request, json
    
    searx_url = "http://localhost:8080/api/http/duckduckgo"
    
    payload = {
        'q': query,
        'format': 'json'
    }
    
    req = urllib.request.Request(
        searx_url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    with urllib.request.urlopen(req, timeout=60) as response:
        results = json.loads(response.read().decode())
        
        return {
            'data': {
                'web': results.get('results', [])[:5]  # Limit to top 5
            }
        }
```

---

## 🎯 Recommendation & Next Steps

### **Best Path Forward:**

1. **Deploy SearXNG** (Option 1 above) - Takes ~2 minutes with Docker
   - ✅ Unlimited calls
   - ✅ Full privacy
   - ✅ Works offline once set up
   - ✅ Free forever

2. **Update search scripts** to use SearXNG API
   - Replace `localhost:3002` with `localhost:8080`
   - No authentication required (public endpoint)

3. **Test with sample queries**
   - Verify results are coming back
   - Check relevance for your domain-specific queries

4. **Integrate into overnight research protocol**
   - Update all scripts to use SearXNG fallback
   - Run test scan to populate database

---

## 📊 Expected Results

With proper web search infrastructure, you'll get:

- ✅ Real web pages with actual content about patterns
- ✅ Symbolic analysis from multiple sources (DDG, Bing, Google)
- ✅ Cross-references between domains automatically
- ✅ Pattern discovery without manual data entry
- ✅ Privacy-respecting, unlimited use

---

## 🚀 **Ready to deploy?**

I'll create:
1. Docker compose files for SearXNG
2. Updated search scripts using SearXNG API
3. Integration guide with existing database structure

**Shall I proceed with creating the deployment packages?** This will give you unlimited, private, free web search that actually works! 🎯
