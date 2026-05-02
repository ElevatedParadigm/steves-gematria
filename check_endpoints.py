#!/usr/bin/env python3
import requests
from pathlib import Path

print("="*60)
print("Firecrawl Available Endpoints")
print("="*60)

base = "http://localhost:3002"
endpoints = [
    "/", "/v1/", "/api/v1/",
    "/search", "/v1/search", "/api/v1/search",
    "/scrape", "/v1/scrape", "/api/v1/scrape",
]

for ep in endpoints:
    try:
        r = requests.get(f"{base}{ep}", timeout=5)
        if r.status_code == 200 or r.status_code == 404:
            content_type = r.headers.get('Content-Type', 'unknown')
            print(f"{ep:20} -> {r.status_code} ({content_type[:30]})")
    except Exception as e:
        print(f"{ep:20} -> Error {str(e)[:40]}")

print("\n" + "="*60)
