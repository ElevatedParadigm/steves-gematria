#!/usr/bin/env python3
"""
Pattern Discovery Agent
========================

Specialized agent for scanning web content using Firecrawl to detect
core gematria patterns across multiple domains.

Capabilities:
- Real-time web scanning via Firecrawl API
- Symbol frequency analysis
- Domain coverage tracking  
- Occurrence timestamping
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import aiohttp
from pydantic import BaseModel, Field

# Add parent to path for imports
sys.path.insert(0, str(Path.home()))
sys.path.insert(0, str(Path.home() / ".hermes"))
sys.path.insert(0, str(Path.home() / ".hermes/gematria/scripts"))

class PatternOccurrence(BaseModel):
    """Represents a discovered pattern occurrence"""
    symbol: int
    url: str
    domain: str
    timestamp: str
    context: Optional[str] = None
    frequency_estimate: Optional[float] = None
    
    @classmethod
    def from_firecrawl(cls, data: Dict) -> "PatternOccurrence":
        """Parse Firecrawl search results"""
        if not data.get("success"):
            return cls(
                symbol=0, url="", domain="", timestamp=""
            )
            
        items = data.get("data", {}).get("markdown", "")
        domains_found = data.get("data", {}).get("domains", [])
        
        # Parse occurrences from markdown content
        occurrences = []
        if items:
            for symbol in [124, 963, 55, 111, 279, 666]:
                if f"{symbol}" in items or f"§{symbol}" in items:
                    occurrences.append({
                        "symbol": symbol,
                        "url": data.get("url", ""),
                        "domain": domains_found[0] if domains_found else "",
                        "timestamp": datetime.now().isoformat(),
                        "context": items[:500] if len(items) > 500 else items
                    })
        
        return occurrences

class PatternDiscoveryAgent:
    """
    Agent responsible for discovering gematria patterns across the web.
    
    Routes:
    • Search queries → Firecrawl API
    • Result parsing → Occurrence extraction  
    • Domain tracking → Unique domain registry
    
    Dependencies:
    • Firecrawl local instance (localhost:3002) or cloud API
    • Core symbols configuration (124, 963, 55, 111, 279, 666)
    """
    
    def __init__(self):
        self.agent_id = "pattern-discovery"
        self.agent_type = "discovery"
        self.name = f"[{self.agent_id}] Pattern Discovery Agent"
        self.core_symbols = [124, 963, 55, 111, 279, 666]
        self.fallback_url = "https://api.firecrawl.dev/v1/search"
        self.discovered_patterns: List[Dict] = []
        self.domains_discovered: set = set()
        
    async def initialize(self):
        """Agent initialization"""
        self.log("INFO", f"Pattern Discovery Agent initialized")
        self.log("INFO", f"Core symbols tracked: {self.core_symbols}")
        
    async def execute_task(self, task_payload: Dict) -> Dict:
        """Execute specific discovery task"""
        task_name = task_payload.get("type", "unknown")
        
        if task_name == "search":
            return await self.search_web(task_payload.get("query", str(task_payload)))
        elif task_name == "scan_domains":
            return await self.scan_specific_domains(task_payload.get("domains", []))
        else:
            return await self.search_web(str(task_payload))
            
    async def execute_workflow(self) -> Dict:
        """Run daily discovery workflow"""
        self.log("INFO", "Starting pattern discovery workflow")
        
        # Import the overnight research functions directly with correct names
        from overnight_research import GematriaOvernightAnalyzer, GEMATRIA_DB, FIRECRAWL_URL
        
        analyzer = GematriaOvernightAnalyzer(GEMATRIA_DB)
        
        # Search for each core symbol using the analyzer's perform_search method
        all_results = {}
        
        for symbol in self.core_symbols:
            try:
                results = analyzer.perform_search(str(symbol))
                
                if results and "success" in results:
                    occurrences = results.get("data", {}).get("markdown", "")
                    domain = results.get("data", {}).get("domains", [results.get("url", "")])[0] if isinstance(results.get("data"), dict) else ""
                    
                    occurrence_count = occurrences.count(str(symbol)) + occurrences.count(f"§{symbol}")
                    
                    self.log("INFO", f"Symbol {symbol}: found in domain '{domain[:100]}...'")
                    self.domains_discovered.add(domain)
                    
                    all_results[f"symbol_{symbol}"] = [
                        {
                            "url": results.get("url", ""),
                            "markdown": occurrences[:1000],  # Truncate long content
                            "occurrences": occurrence_count
                        }
                    ]
                else:
                    self.log("WARN", f"Symbol {symbol} returned empty or invalid result")
                    all_results[f"symbol_{symbol}"] = []
                    
            except Exception as e:
                self.log("ERROR", f"Symbol {symbol} search failed: {str(e)}")
                all_results[f"symbol_{symbol}"] = []
        
        # Summary
        summary = {
            "total_symbols_searched": len(self.core_symbols),
            "symbols_with_occurrences": sum(1 for k, v in all_results.items() if v and len(v) > 0),
            "domains_found": list(self.domains_discovered)[:20],  # Top 20
            "by_symbol": {k: len(v) for k, v in all_results.items()},
            "timestamp": datetime.now().isoformat()
        }
        
        self.log("INFO", f"Discovery workflow complete. Found occurrences in {summary['symbols_with_occurrences']}/{len(self.core_symbols)} symbols")
        
        return summary

    async def search_web(self, query: str) -> Dict:
        """Search web using Firecrawl API"""
        
        try:
            if FIRECRAWL_BASE_URL and "api.firecrawl.dev" not in FIRECRAWL_BASE_URL:
                url = f"{FIRECRAWL_BASE_URL}/v1/search"
                self.log("INFO", f"Using local Firecrawl: {url}")
            else:
                url = "https://api.firecrawl.dev/v1/search"
                self.log("INFO", "Using Firecrawl cloud API")
                
        except Exception as e:
            self.log("WARN", f"Could not determine base URL, using default. Error: {str(e)}")
            url = "https://api.firecrawl.dev/v1/search"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json={
                        "query": query,
                        "options": {
                            "limit": 5,
                            "exclude_current_page_from_results": False,
                            "scrapeOptions": {
                                "formats": ["markdown"],
                                "timeout": 30000
                            }
                        },
                        "pageOptions": {
                            "format": "markdown",
                            "fallback" : True
                        }
                    },
                    headers={"Authorization": f"Bearer {FIRECRAWL_API_KEY}"}
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        # Parse and extract occurrences
                        markdown = result.get("data", {}).get("markdown", "")
                        domains = result.get("data", {}).get("domains", [])
                        
                        occurrence_count = 0
                        for symbol in self.core_symbols:
                            occurrence_count += markdown.count(str(symbol)) + markdown.count(f"§{symbol}")
                            
                        return {
                            "success": True,
                            "url": result.get("url", ""),
                            "query": query,
                            "domains": domains[:3],  # Top 3 domains
                            "markdown": markdown[:5000] if markdown else "",  # Truncate
                            "occurrences": occurrence_count
                        }
                    else:
                        error_text = await response.text()
                        self.log("ERROR", f"Firecrawl API returned {response.status}: {error_text[:200]}")
                        return {
                            "success": False,
                            "error": f"API Error {response.status}",
                            "details": error_text[:500] if error_text else ""
                        }
                        
        except Exception as e:
            self.log("ERROR", f"Search request failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def scan_specific_domains(self, domains: List[str]) -> Dict:
        """Scan specific domains for core symbols"""
        
        results = []
        
        for domain in domains:
            query = f"{domain} 124 OR {domain} 963 OR {domain} 55"
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        "https://api.firecrawl.dev/v1/search",
                        json={
                            "query": query,
                            "options": {
                                "limit": 3,
                                "exclude_current_page_from_results": False,
                                "scrapeOptions": {"formats": ["markdown"], "timeout": 30000}
                            },
                            "pageOptions": {"format": "markdown", "fallback": True}
                        },
                        headers={"Authorization": f"Bearer {FIRECRAWL_API_KEY}"}
                    ) as response:
                        
                        if response.status == 200:
                            result = await response.json()
                            results.append({
                                "domain": domain,
                                "query": query,
                                "url": result.get("url", ""),
                                "markdown": result.get("data", {}).get("markdown", "")[:3000]
                            })
            except Exception as e:
                self.log("WARN", f"Domain {domain} scan failed: {str(e)}")
        
        return {
            "success": True,
            "domains_scanned": len(domains),
            "results": results[:10]  # Limit to top 10 for readability
        }

    def log(self, level: str, message: str):
        print(f"[{self.name}] [{level}] {message}")
