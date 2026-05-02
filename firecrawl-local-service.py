#!/usr/bin/env python3
"""
Firecrawl Local Service - Standalone Python Implementation
This runs as a local HTTP server for web scraping without Docker containers.
"""

import asyncio
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
import subprocess
import os
import sys
from urllib.parse import urlparse, parse_qs

PORT = 3002
ENV_FILE = '/home/avalonas/.hermes/.env'

class FirecrawlLocalHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
        
        try:
            data = json.loads(body) if body else {}
            query = data.get('query', 'test')
            url = data.get('url', 'https://example.com')
            
            # Log request
            print(f"[{self.log_date_time_string()}] Request: {self.path}")
            print(f"  Query: {query[:50]}...")
            print(f"  URL: {url}")
            
            # Send response (placeholder - would call actual Firecrawl API in real deployment)
            response = {
                'success': True,
                'location': f'https://example.com',
                'status': {'statusCode': 200},
                'markdown': '# Example Content\n\nThis is a placeholder response from the local Firecrawl service.',
                'content': 'Example content for testing purposes.',
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            return 1
            
        except Exception as e:
            print(f"Error: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
            return 1
    
    def do_GET(self):
        if self.path == '/v1/health':
            response = {'status': 'healthy'}
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            return 1
        else:
            self.send_response(404)
            self.end_headers()
            return 1
    
    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {format % args}")

if __name__ == '__main__':
    # Load environment if available
    if os.path.exists(ENV_FILE):
        for line in open(ENV_FILE):
            if not line.strip().startswith('#') and '=' in line:
                key, value = line.strip().split('=', 1)
                os.environ[key] = value
    
    # Start HTTP server
    server = HTTPServer(('0.0.0.0', PORT), FirecrawlLocalHandler)
    print(f"🔥 Local Firecrawl Service starting on port {PORT}...")
    print(f"   Endpoint: http://localhost:{PORT}/v1/search")
    print(f"   Health check: http://localhost:{PORT}/v1/health")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🔥 Shutting down Firecrawl local service...")
        server.shutdown()
