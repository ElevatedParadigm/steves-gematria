#!/usr/bin/env python3
"""
Simple Local Web Scraper - Uses ONLY Python standard library
Runs on localhost:3003 with Firecrawl-compatible API
Fixed version without title attribute issues
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.request
import urllib.parse
import json
from datetime import datetime
from html.parser import HTMLParser

class MarkdownHTMLParser(HTMLParser):
    """Simple parser to convert HTML to basic markdown structure"""
    
    def __init__(self, url=""):
        super().__init__()
        self.raw_text = ""
        self.in_h1 = False
        self.in_h2 = False
        self.url = url
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "h1":
            self.in_h1 = True
        elif tag == "h2":
            self.in_h2 = True
            
    def handle_endtag(self, tag):
        if tag in ("h1", "h2"):
            setattr(self, f"in_{tag}", False)
            
    def handle_data(self, data):
        text = data.strip()
        if text and not self.raw_text.endswith("\n\n"):
            self.raw_text += "\n"
        
        if self.in_h1:
            self.raw_text += f"# {text}\n\n"
        elif self.in_h2:
            self.raw_text += f"## {text}\n\n"
        else:
            # Just append content, avoid title attribute issues
            self.raw_text += text[:500]  # Limit content length
    
    def get_markdown(self):
        return self.raw_text or "No significant content found."

class ScraperHandler(SimpleHTTPRequestHandler):
    
    def do_POST(self):
        url = None
        
        if self.path == "/v1/scraper" or self.path == "/v1/scrape":
            # Parse query string from URL (some clients send URL in query)
            url = self.path.split("?")[0] if "?" in self.path else None
            
            # Try form data
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > 0:
                    body = self.rfile.read(content_length).decode()
                    data = json.loads(body) if body else {}
                    url = data.get("url") or url
            except:
                pass
            
            # Check X-URL header
            if not url:
                url = self.headers.get("X-URL", "")
            
            if not url:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Missing URL parameter\n")
                return
            
            result = scrape_url(url)
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result, indent=2).encode())
            
        else:
            super().do_POST()
    
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = {
                "status": "ok",
                "service": "Local Lightweight Scraper (Standard Library)",
                "version": "1.0"
            }
            self.wfile.write(json.dumps(response).encode())
        elif self.path == "/docs":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = {
                "service": "Local Lightweight Scraper",
                "endpoints": {
                    "/health": "Health check",
                    "/v1/scraper?url=https://example.com": "Scrape a URL (POST)"
                }
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            super().do_GET()
    
    def log_message(self, format, *args):
        timestamp = datetime.now().strftime('%H:%M:%S')
        if args:
            message = format % args
        else:
            message = format
        print(f"[{timestamp}] {message}")

def scrape_url(url: str) -> dict:
    """Scrape a URL using standard library requests"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"
        }
        
        request = urllib.request.Request(
            url,
            headers=headers,
            method="GET"
        )
        
        response = urllib.request.urlopen(request, timeout=30)
        
        # Parse HTML with our custom parser
        html_text = response.read().decode("utf-8", errors="ignore")
        parser = MarkdownHTMLParser(url=url)
        parser.feed(html_text)
        
        return {
            "success": True,
            "markdown": parser.get_markdown(),
            "html": html_text[:2000],  # First 2KB of raw HTML
            "metadata": {
                "url": url,
                "status_code": response.status,
                "scrapedAt": datetime.now().isoformat()
            }
        }
        
    except urllib.error.HTTPError as e:
        return {
            "success": False,
            "error": f"HTTP Error {e.code}: {e.reason}",
            "metadata": {"url": url, "status": e.code}
        }
    except urllib.error.URLError as e:
        return {
            "success": False,
            "error": f"URL Error: {str(e)}",
            "metadata": {"url": url, "status": 502}
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error: {type(e).__name__}: {str(e)}",
            "metadata": {"url": url, "status": 500}
        }

if __name__ == "__main__":
    host = "0.0.0.0"
    port = 3003
    
    print(f"🔥 Starting Local Lightweight Scraper on http://{host}:{port}")
    print("   - Standard library only (no pip dependencies)")
    print("   - Use POST /v1/scraper?url=... to scrape URLs")
    server = HTTPServer((host, port), ScraperHandler)
    print("✅ Server running. Press Ctrl+C to stop.")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        server.shutdown()
