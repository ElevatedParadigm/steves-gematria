#!/usr/bin/env python3
"""
Webhook Event Handler - Level 1 Trigger Integration
Processes incoming webhook events and triggers appropriate searches via Local Firecrawl Runner.
Phase 2, Option B: Full Webhook Integration
"""

import json
import subprocess
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Paths
DB_PATH = Path.home() / ".hermes/gematria/database/gematria_database.json"
FIRECRAWL_RUNNER = Path.home() / ".hermes/gematria/scripts/local_firecrawl_runner_v2.py"
OBSIDIAN_EXPORTS = Path.home() / ".hermes/gematria/obsidian_exports"

# Domain keyword mappings for routing events
DOMAIN_KEYWORDS = {
    "geopolitical": ["Israel", "Gaza", "Hezbollah", "Trump", "US foreign policy"],
    "religious": ["Temple Mount", "Jerusalem", "church", "mosque", "gospel"],
    "economic": ["Bitcoin", "crypto", "gold", "inflation", "stock market"],
    "military": ["coup", "troops", "defense budget", "weapon system", "fighter jet"],
    "elemental": ["fire volcano", "climate disaster", "wildfire", "earthquake", "tsunami"],
    "cryptographic": ["aes encryption", "hash algorithm", "private key", "public key"]
}

CORE_SYMBOLS = ["124", "963", "55", "111", "279", "666"]


def load_database() -> dict:
    """Load gematria database."""
    try:
        with open(DB_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Database load failed: {e}")
        return {"metadata": {}}


def search_with_curl(query: str) -> dict:
    """Simple curl-based web search (DuckDuckGo) with retries."""
    for attempt in range(3):
        try:
            search_term = query.replace(" ", "+")
            
            result = subprocess.run(
                ["curl", "-sL", "--max-time", "15", 
                 f"https://duckduckgo.com/?q={search_term}&iax=answers&ia=web"],
                capture_output=True, 
                text=True,
                timeout=18
            )
            
            if result.returncode == 0:
                return {
                    "method": "curl",
                    "success": True,
                    "response": result.stdout[:10000],
                    "status_code": 200,
                    "query": query
                }
        except subprocess.TimeoutExpired:
            print(f"   ⚠️  Attempt {attempt + 1}: Timeout ({15}s)")
        except Exception as e:
            print(f"   ⚠️  Attempt {attempt + 1}: {str(e)[:60]}")
        
        if attempt < 2:
            import time
            time.sleep(1)
    
    return {"method": "curl", "success": False, "error": "All attempts failed"}


def route_event_to_keywords(event_type: str, event_data: dict) -> List[str]:
    """Route event to appropriate domain keywords."""
    
    # Extract keywords from event data if present
    event_keywords = []
    
    if "keywords" in event_data:
        for kw in event_data["keywords"]:
            if len(kw) >= 2 and len(kw) <= 10:
                event_keywords.append(kw.upper())
    
    # Also check for uppercase terms directly in the message
    text = str(event_data).upper()
    keywords = re.findall(r'\b[A-Z]{2,10}\b', text)[:10]
    event_keywords.extend(keywords)
    
    if event_keywords:
        return list(set(event_keywords))[:5]  # Limit to top 5
    
    # Fallback: use domain-based routing
    for domain, keywords in DOMAIN_KEYWORDS.items():
        if domain.lower() in str(event_data).lower():
            return [kw.upper() for kw in keywords[:3]]
    
    # Generic search terms for unknown events
    generic_terms = ["event", "breaking news", "analysis"]
    return generic_terms[:2]


def build_search_query(query: str) -> str:
    """Build enriched search query from simple term."""
    domain_keywords = DOMAIN_KEYWORDS
    
    for domain, keywords in domain_keywords.items():
        if any(kw.lower() in query.lower() for kw in keywords):
            base = query.split()[0] if query else "event"
            return f"{base} {', '.join(keywords[:2])}"
    
    # Add context from recent database entries
    db = load_database()
    entries = db.get("entries", {})
    if entries:
        sample_entry = list(entries.values())[0]
        title = sample_entry.get("title", "")
        enriched = f"{query} {title[:50]}".strip()
        return enriched
    
    return query


def extract_patterns(html_content: Optional[str]) -> dict:
    """Extract patterns from HTML content."""
    if not html_content:
        return {"keywords": [], "dates": [], "numbers": []}
    
    patterns = {
        "keywords": [],
        "dates": [],
        "numbers": []
    }
    
    # Extract uppercase keywords (2-10 chars)
    keywords = re.findall(r'\b[A-Z]{2,10}\b', html_content)
    patterns["keywords"] = list(set(keywords))[:30]
    
    # Extract dates (various formats)
    dates = re.findall(r'(?:\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4}|[A-Za-z]+?\s+\d{1,2},?\s+\d{4})', html_content)
    patterns["dates"] = list(set(dates))[:20]
    
    # Extract numbers (including decimals)
    numbers = re.findall(r'\b\d+(?:\.\d+)?\b', html_content)
    patterns["numbers"] = list(set(numbers))[:15]
    
    return patterns


def analyze_core_symbols(html_content: Optional[str]) -> dict:
    """Analyze HTML content for core symbol patterns (124, 963, 55, 111, 279, 666)."""
    
    symbols = {sym: 0 for sym in CORE_SYMBOLS}
    
    if html_content:
        # Look for number sequences that match core symbols
        for symbol in CORE_SYMBOLS:
            count = 0
            patterns = [f"{symbol}", f" {symbol} ", f",{symbol},", f"\n{symbol}\n"]
            for pattern in patterns:
                count += html_content.lower().count(pattern.lower())
            symbols[symbol] = count
    
    return symbols


def process_search_results(html: Optional[str], query: str) -> dict:
    """Process search results and extract gematria-relevant data."""
    
    patterns = extract_patterns(html)
    
    # Count occurrences of key terms
    key_terms = ["Israel", "Temple", "Jerusalem", "Bitcoin", "coup", "fire", 
                 "encryption", "volcano", "Trump"]
    
    term_counts = {}
    html_lower = html.lower() if html else ""
    for term in key_terms:
        term_lower = term.lower()
        match = re.findall(rf'\b{term_lower}\b', html_lower)
        term_counts[term] = len(match)
    
    return {
        "query": query,
        "patterns": patterns,
        "term_counts": term_counts,
        "word_count": len([c for c in html.split()]) if html else 0,
        "gematria_relevance": sum(term_counts.values()) > 5
    }


def update_database(query: str, results: dict) -> bool:
    """Update gematria database with new search results."""
    
    try:
        db = load_database()
        
        # Generate unique key for this search
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        key = f"{query.replace(' ', '_')[:30]}_{timestamp}"
        
        # Create entry
        entry = {
            "key": key,
            "title": query,
            "core_symbols_detected": list(CORE_SYMBOLS),
            "timeline_range": results.get("patterns", {}).get("dates", [])[:5],
            "keywords_found": results.get("patterns", {}).get("keywords", []),
            "numbers_found": results.get("patterns", {}).get("numbers", []),
            "word_count": results.get("word_count", 0),
            "gematria_relevance": results.get("gematria_relevance", False)
        }
        
        # Add to entries
        db.setdefault("entries", {})[key] = entry
        
        # Update metadata
        metadata = db.setdefault("metadata", {})
        metadata.setdefault("core_symbols", CORE_SYMBOLS)
        metadata.setdefault("domains_tracked", list(DOMAIN_KEYWORDS.keys()))
        metadata.setdefault("elemental_forces", ["fire", "volcano", "frequency", "resonance"])
        
        # Save updated database
        with open(DB_PATH, 'w') as f:
            json.dump(db, f, indent=2)
        
        print(f"   [✓] Database updated with entry: {key}")
        return True
        
    except Exception as e:
        print(f"   [ERROR] Database update failed: {e}")
        return False


def process_webhook_payload(payload: dict) -> dict:
    """Process incoming webhook event and trigger search."""
    
    print("\n" + "="*60)
    print("📡 WEBHOOK EVENT RECEIVED")
    print("="*60)
    
    # Extract event data
    event_type = payload.get("type", "unknown")
    event_data = payload.get("data", {})
    keywords = payload.get("keywords", [])
    
    # Route to appropriate search terms
    search_terms = route_event_to_keywords(event_type, event_data)
    
    print(f"\n📍 Event Type: {event_type}")
    print(f"   Keywords detected: {len(keywords)}")
    for term in search_terms[:3]:
        print(f"      - {term}")
    
    # Execute searches for each keyword
    results = {}
    
    for i, query in enumerate(search_terms):
        print(f"\n🔍 Running search #{i+1}: '{query}'")
        
        # Build enriched query
        enriched_query = build_search_query(query)
        print(f"   Enriched: '{enriched_query}'")
        
        # Search via local Firecrawl runner
        result = search_with_curl(enriched_query)
        
        if result["success"]:
            processed = process_search_results(result["response"], enriched_query)
            
            # Analyze core symbols from results
            symbols = analyze_core_symbols(result["response"])
            
            print(f"   ✅ Search successful: {processed['word_count']} words analyzed")
            print(f"      Keywords extracted: {len(processed['patterns']['keywords'])}")
            print(f"      Dates found: {len(processed['patterns']['dates'])}")
            print(f"      Numbers detected: {len(processed['patterns']['numbers'])}")
            
            # Store results by domain/category
            results[query] = {
                "search_term": enriched_query,
                "response": result["response"][:500],  # Store first 500 chars
                "processed": processed,
                "symbols": symbols
            }
            
            # Update database
            update_database(enriched_query, processed)
        else:
            print(f"   ⚠️  Search failed for '{query}': {result.get('error', 'Unknown')}")
    
    return {
        "event_type": event_type,
        "keywords_processed": list(results.keys()) if results else [],
        "total_searches": len(results),
        "results": results
    }


def handle_webhook_endpoint(host: str = "localhost", port: int = 8080):
    """Simple HTTP webhook receiver (using built-in http.server)."""
    
    from http.server import HTTPServer, BaseHTTPRequestHandler
    
    class WebhookHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else b""
            
            # Parse JSON payload
            try:
                payload = json.loads(body.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                self.send_response(202)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "accepted", "message": "Invalid JSON"}).encode())
                return
            
            print(f"\n📩 Raw webhook payload received:")
            for key, value in payload.items():
                if isinstance(value, str) and len(value) > 100:
                    print(f"   {key}: {value[:100]}...")
                else:
                    print(f"   {key}: {value}")
            
            # Process event
            result = process_webhook_payload(payload)
            
            # Send response
            self.send_response(202)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {
                "status": "accepted",
                "event_type": result["event_type"],
                "keywords_processed": result["keywords_processed"],
                "total_searches": result["total_searches"]
            }
            self.wfile.write(json.dumps(response).encode())
            
        def log_message(self, format, *args):
            print(f"{self.address_string()} - {format % args}")
    
    server = HTTPServer((host, port), WebhookHandler)
    print(f"\n🌐 Webhook listener started at http://{host}:{port}/webhook")
    print(f"   Endpoint: POST /webhook")
    print(f"\n   Waiting for events... (Press Ctrl+C to stop)")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n⏹️  Webhook listener stopped.")


def main():
    """Main entry point - choose mode."""
    
    print("\n" + "="*60)
    print("🌉 LEVEL 1 TRIGGER INTEGRATION")
    print("="*60 + "\n")
    
    args = sys.argv[1:]
    
    if "--listen" in args:
        # Start webhook listener
        if len(args) != 3:
            host = "localhost"
            port = 8080
            for i, arg in enumerate(args):
                if i == 0:
                    host = arg
                else:
                    port = int(arg)
        print("\n🎯 Starting webhook listener...")
        handle_webhook_endpoint(host, port)
        
    elif "--process" in args:
        # Process standalone webhook payload
        if len(args) != 2:
            print("Usage: python webhook_handler.py --process <payload_json_file>")
            sys.exit(1)
        
        payload_path = Path(args[1])
        if not payload_path.exists():
            print(f"[ERROR] Payload file not found: {payload_path}")
            sys.exit(1)
        
        with open(payload_path, 'r') as f:
            payload = json.load(f)
        
        result = process_webhook_payload(payload)
        print(f"\n✅ Webhook processing complete!")
        print(f"   Event type: {result['event_type']}")
        print(f"   Keywords processed: {', '.join(result['keywords_processed'][:5])}")
        print(f"   Total searches performed: {result['total_searches']}")
        
    else:
        print("\nUsage:")
        print("  python webhook_handler.py --listen <host> <port> - Start webhook receiver")
        print("  python webhook_handler.py --process <payload.json> - Process standalone event")
        print("  (no args) - Show this help\n")


if __name__ == "__main__":
    main()
