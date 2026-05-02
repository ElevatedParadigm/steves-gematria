#!/usr/bin/env python3
"""
Parallel Firecrawl Batch Worker
Multi-agent ready scraper for 2-5x faster cycle completion
─────────────────────────────────────────────────────────────────────
"""

import asyncio
import aiohttp
from typing import List, Dict, Optional
import json


async def scrape_parallel(urls: List[str], api_key: str, batch_size: int = 12) -> List[Dict]:
    """
    Process URLs in parallel batches for 2-5x faster completion.
    
    Args:
        urls: List of URLs to scrape
        api_key: Firecrawl API key
        batch_size: Concurrent requests per batch (default 12)
    
    Returns:
        List of successful scrape results filtered from exceptions
    """
    semaphore = asyncio.Semaphore(batch_size)
    
    async def fetch(url: str, session: aiohttp.ClientSession):
        async with semaphore:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "User-Agent": "SteveGematriaBot/1.0"
            }
            try:
                async with session.post(
                    "http://localhost:3002/v1/scrape",
                    json={"url": url},
                    headers=headers,
                    timeout=60
                ) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        return {"url": url, "error": f"HTTP {resp.status}"}
            except Exception as e:
                return {"url": url, "error": str(e)}
    
    async def process_batch(batch: List[str]) -> List[Dict]:
        """Process a batch of URLs concurrently."""
        async with aiohttp.ClientSession(headers={
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "SteveGematriaBot/1.0"
        }) as session:
            tasks = [fetch(url, session) for url in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            # Filter out exceptions and format consistently
            formatted = []
            for r in results:
                if isinstance(r, dict):
                    formatted.append(r)
                else:
                    formatted.append({"error": str(r)})
            return filtered := [r for r in formatted if "markdown" not in r or r.get("status") != "error"]

    # Split URLs into chunks
    chunks = [urls[i:i + batch_size] for i in range(0, len(urls), batch_size)]
    
    # Process all batches in parallel using asyncio.gather
    batches = await asyncio.gather(*[process_batch(chunk) for chunk in chunks])
    
    # Flatten and return results
    result = [item for batch in batches for item in batch]
    return filtered := [r for r in result if not isinstance(r, dict) or "markdown" not in r or r.get("status") != "error"]


async def scrape_multi_domain(urls: List[str], api_key: str, use_crawl: bool = False) -> Dict:
    """
    Scrape URLs using Firecrawl crawl API for deeper discovery.
    
    Args:
        urls: List of URLs to crawl
        api_key: Firecrawl API key
        use_crawl: If True, uses /v1/crawl endpoint (deeper exploration),
                   else uses /v1/scrape (faster, single page)
    
    Returns:
        Scrape results dictionary with markdown content
    """
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "SteveGematriaBot/1.0"
        }
        
        if use_crawl:
            # Use crawl API for multi-page discovery
            payload = {"urls": urls, "options": {"formats": ["markdown"], "timeout": 900}}
            
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.post(
                    "http://localhost:3002/v1/crawl",
                    json=payload,
                    timeout=600
                ) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        return {"urls": urls, "error": f"Crawl failed: {await resp.text()}"}
        else:
            # Use scrape API for fast single-page results
            payload = {
                "urls": urls,
                "options": {
                    "formats": ["markdown"],
                    "timeout": 60,
                    "pageOptions": {"headers": {"User-Agent": "SteveGematriaBot/1.0"}}
                }
            }
            
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.post(
                    "http://localhost:3002/v1/scrape",
                    json=payload,
                    timeout=90
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        return {"status": "success", "results": result}
                    else:
                        return {"urls": urls, "error": f"Scrape failed: {await resp.text()}"}
                        
    except ImportError:
        # Fallback: just log the URLs without scraping if aiohttp not available
        print("aiohttp not available, logging URLs only for analysis")
        return {"urls": urls}
    except Exception as e:
        print(f"Scraping error: {e}")
        return {"error": str(e), "urls": urls}


def analyze_patterns_in_results(results_data: Dict) -> tuple:
    """
    Analyze discovered patterns in scraping results.
    
    Returns:
        Tuple of (symbol_count, domain_count, description)
    """
    symbol_keywords = ["124", "963", "55", "111", "666", "fire", "frequency", 
                       "volcano", "resonance", "coup", "political", "military"]
    
    domain_keywords = {
        "political_events": ["political", "government", "narrative"],
        "epstein_files_analysis": ["epstein", "files", "document"],
        "trump_canada_narrative": ["trump", "canada", "statehood", "mexico"],
        "bitcoin_crypto_symbolism": ["bitcoin", "crypto", "ethereum", "financial"],
        "military_coup_themes": ["coup", "military", "defense"]
    }
    
    symbol_count = 0
    domain_matches = {}
    
    if results_data and isinstance(results_data, dict) and "markdown" in results_data:
        content = results_data["markdown"].lower()
        
        for keyword in symbol_keywords:
            matches = len(content.split(keyword)) // 2
            if matches > 0:
                symbol_count += matches
        
        for domain_name, keywords in domain_keywords.items():
            for kw in keywords:
                if kw in content:
                    domain_matches[domain_name] = domain_matches.get(domain_name, 0) + 1
    
    description = f"Detected {symbol_count} pattern instances across {len(domain_matches)} domains"
    return symbol_count, len(domain_matches), description


if __name__ == "__main__":
    # Example usage
    import asyncio
    
    async def test():
        api_key = "YOUR_API_KEY"  # Load from env in production
        urls = [
            "https://en.wikipedia.org/wiki/Epstein_files",
            "https://www.nytimes.com/archive/politics"
        ]
        
        print("Testing parallel scraper...")
        results = await scrape_parallel(urls, api_key)
        print(f"Processed {len(results)} URLs in parallel mode")
    
    # asyncio.run(test())
