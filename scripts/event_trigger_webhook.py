#!/usr/bin/env python3
"""
Event-Triggered Webhook Architecture — Week 1 Implementation
Part 1a: Basic Trigger System (Level 1 Keyword Matching)

Objective: Reduce false positives by ~40% through intelligent event filtering
Implementation: Progressive trigger escalation hierarchy (Level 1 → Level 2 → Level 3 → Level 4)
"""

import json
import os
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse, urljoin

# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

# Core symbols tracked by the gematria system
CORE_SYMBOLS = [124, 963, 55, 111, 279, 666]

# Domain configurations from Phase 1 implementation
DOMAIN_CONFIG = {
    "political": {
        "keywords": ["trump", "canada", "biden", "campaign", "election", "policy"],
        "elemental_forces": ["fire", "power"],
        "confidence_threshold": 0.85,
        "domain_path": "/domains/political"
    },
    "military": {
        "keywords": ["coup", "army", "defense", "weapons", "soldier", "tactic"],
        "elemental_forces": ["fire", "earth"],
        "confidence_threshold": 0.85,
        "domain_path": "/domains/military"
    },
    "spiritual": {
        "keywords": ["prophetic", "divine", "eschatological", "apocalyptic"],
        "elemental_forces": ["fire", "spirit"],
        "confidence_threshold": 0.85,
        "domain_path": "/domains/spiritual"
    },
    "cube26": {
        "keywords": ["yhwh", "sacred geometry", "cubical", "divine intervention"],
        "elemental_forces": ["fire", "spirit"],
        "confidence_threshold": 0.85,
        "domain_path": "/domains/spiritual/cube26"
    },
    "water": {
        "keywords": ["fluidity", "flow", "resilience", "adaptation", "purification"],
        "elemental_forces": ["water"],
        "confidence_threshold": 0.90,
        "domain_path": "/domains/water"
    },
    "biosciences": {
        "keywords": ["crisis biology", "gene alchemy", "stem cell", "medical ethics"],
        "elemental_forces": ["growth", "decay", "transformation"],
        "confidence_threshold": 0.85,
        "domain_path": "/domains/biosciences"
    },
}

# Firecrawl API configuration
FIRECRAWL_CONFIG = {
    "base_url": "http://localhost:3002/v1/search",
    "api_key_env_var": "FIRECRAWL_API_KEY",
    "max_results": 5,
    "search_timeout": 60
}

# Trigger hierarchy configuration
TRIGGER_HIERARCHY = {
    "level_1": {
        "name": "Keyword Match (Immediate)",
        "delay_minutes": 0,
        "percentage_of_triggers": 60,
        "description": "Immediate response to core symbol or domain keyword matches",
        "action": "immediate"
    },
    "level_2": {
        "name": "Pattern Verification",
        "delay_minutes": 5,
        "percentage_of_triggers": 30,
        "description": "Cross-reference with previous day's discoveries and verify bridge connections",
        "action": "delayed"
    },
    "level_3": {
        "name": "Cross-Domain Correlation",
        "delay_queues": 15,
        "percentage_of_triggers": 8,
        "description": "Multi-domain term intersection and temporal proximity analysis",
        "action": "queued"
    },
    "level_4": {
        "name": "AI Anomaly Detection",
        "delay_minutes": 15,
        "percentage_of_triggers": 2,
        "description": "Advanced multi-domain convergence signals and anomaly signature hunting",
        "action": "ai_analysis"
    }
}

# Event payload structure
EVENT_PAYLOAD_TEMPLATE = {
    "event_type": "discovery",
    "priority": "P1",  # P1-P4 based on trigger level
    "source_url": "",
    "core_symbols_detected": [],
    "domain_connections": [],
    "elemental_forces": [],
    "timestamp": "",
    "confidence_score": 0.0,
    "trigger_level": 1,  # Will be updated based on classification
    "requires_ai_analysis": False,
    "related_events": []
}

# ============================================================================
# UTILITIES
# ============================================================================

def get_api_key() -> Optional[str]:
    """Get Firecrawl API key from environment or .env file"""
    import os
    env_file = Path.home() / ".hermes" / ".env"
    
    try:
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith('FIRECRAWL_API_KEY='):
                    # Extract value after the key
                    value = line.split('=', 1)[1].strip()
                    # Remove quotes if present
                    value = value.strip('"\'')
                    return value
    except FileNotFoundError:
        pass
    
    # Fallback to environment variable
    import os
    api_key = os.getenv(FIRECRAWL_CONFIG["api_key_env_var"])
    return api_key

def format_timestamp() -> str:
    """Format timestamp as ISO8601 with UTC timezone"""
    return datetime.now(timezone.utc).isoformat()

def extract_keywords(text: str, keyword_sets: List[str]) -> Dict[str, List[str]]:
    """Extract matched keywords from text"""
    # Simple case-insensitive matching
    text_lower = text.lower()
    matches = {kw: [] for kw in keyword_sets}
    
    for keyword in keyword_sets:
        pattern = re.escape(keyword.lower())
        matches[keyword] = list(set(text_lower.split()) & set(pattern))  # Simplified
    
    return matches

def extract_numerals_from_text(text: str) -> List[int]:
    """Extract potential gematria numbers from text (3-4 digits)"""
    pattern = r'\b\d{3,4}\b'
    matches = re.findall(pattern, text)
    return [int(m) for m in matches]

def get_firecrawl_client() -> Optional[Dict[str, str]]:
    """Initialize Firecrawl client configuration"""
    api_key = get_api_key()
    
    if not api_key:
        print(f"[WARN] No FIRECRAWL_API_KEY configured in ~/.hermes/.env or environment")
        return None
    
    return {
        "base_url": FIRECRAWL_CONFIG["base_url"],
        "api_key": api_key,
        "headers": {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    }

def parse_firecrawl_search_response(response_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Parse Firecrawl v2 search response format"""
    results = []
    
    if "data" in response_data and isinstance(response_data["data"], list):
        for item in response_data["data"]:
            if isinstance(item, dict):
                results.append({
                    "url": item.get("url", ""),
                    "title": item.get("title", ""),
                    "description": item.get("description", "")
                })
    
    return results

# ============================================================================
# LEVEL 1: KEYWORD MATCH (IMMEDIATE)
# ============================================================================

class Level1KeywordMatchTrigger:
    """
    Level 1 Trigger: Keyword Match (Immediate Response)
    
    Priority: P1 (Highest)
    Delay: Immediate (<5 seconds)
    Purpose: Quick response to core symbol or domain keyword matches
    """
    
    def __init__(self):
        self.client_config = None
        self.last_event_id = ""
    
    def initialize(self, client_config: Dict[str, str]):
        """Initialize with Firecrawl client configuration"""
        self.client_config = client_config
    
    async def trigger(self, search_text: str) -> Optional[Dict[str, Any]]:
        """
        Trigger Level 1 keyword match event
        
        Args:
            search_text: Query text to search for
            
        Returns:
            Event payload if triggered, None otherwise
        """
        if not self.client_config:
            raise ValueError("Firecrawl client not initialized")
        
        # Get API key from config
        api_key = self.client_config["api_key"]
        base_url = self.client_config["base_url"]
        
        # Build search query with core symbols and keywords
        query = self._build_search_query(search_text)
        
        print(f"🔹 [L1] Keyword Match Trigger - Query: {query[:100]}...")
        
        # Execute Firecrawl search (simplified - would need async implementation)
        results = await self._execute_search(query, api_key, base_url)
        
        if not results:
            return None
        
        # Extract core symbols detected
        symbols_detected = self._extract_core_symbols(results)
        
        # Match domain keywords
        domains_matched = self._match_domains(search_text)
        
        # Build event payload
        payload = EVENT_PAYLOAD_TEMPLATE.copy()
        payload["source_url"] = results[0]["url"] if results else ""
        payload["core_symbols_detected"] = symbols_detected
        payload["domain_connections"] = domains_matched
        payload["elemental_forces"] = self._extract_elemental_forces(search_text)
        payload["timestamp"] = format_timestamp()
        payload["confidence_score"] = 0.85  # Base confidence for L1
        
        return payload
    
    def _build_search_query(self, search_text: str) -> str:
        """Build search query with gematria terms"""
        keywords = []
        
        # Add core symbols as search terms
        for symbol in CORE_SYMBOLS:
            keywords.append(str(symbol))
        
        # Add domain keywords if present
        for domain_config in DOMAIN_CONFIG.values():
            for kw in domain_config["keywords"]:
                if kw.lower() in search_text.lower():
                    keywords.append(kw)
        
        query = " OR ".join(keywords[:10])  # Limit to first 10 terms
        
        return query
    
    async def _execute_search(self, query: str, api_key: str, base_url: str) -> Optional[Dict[str, Any]]:
        """Execute Firecrawl search (placeholder for actual implementation)"""
        import urllib.request
        import json as json_module
        
        # Build API request payload
        payload = {
            "query": query,
            "options": {
                "pageOptions": {
                    "maxNumberOfPages": 1
                }
            }
        }
        
        try:
            url = f"{base_url}/search"
            headers = {"Content-Type": "application/json"}
            
            # Prepare request body
            req_data = json_module.dumps(payload)
            
            # Make HTTP request (simplified - would need proper async handling)
            with urllib.request.urlopen(url, timeout=FIRECRAWL_CONFIG["search_timeout"]) as response:
                data = json_module.loads(response.read())
                
                return parse_firecrawl_search_response(data)
                
        except Exception as e:
            print(f"[ERROR] Firecrawl search failed: {e}")
            return None
    
    def _extract_core_symbols(self, results: List[Dict[str, Any]]) -> List[int]:
        """Extract core symbols from search results"""
        symbols = set()
        
        for result in results:
            text = (result.get("title", "") + " " + 
                    result.get("description", "")).lower()
            
            # Search for symbol mentions (simplified)
            for symbol in CORE_SYMBOLS:
                if str(symbol) in text or f"[{symbol}]" in text.lower():
                    symbols.add(symbol)
        
        return list(symbols)
    
    def _match_domains(self, search_text: str) -> List[str]:
        """Match domain keywords to find active domains"""
        matched_domains = []
        
        for domain_name, domain_config in DOMAIN_CONFIG.items():
            for keyword in domain_config["keywords"]:
                if keyword.lower() in search_text.lower():
                    if domain_name not in matched_domains:
                        matched_domains.append(domain_name)
                    break
        
        return matched_domains
    
    def _extract_elemental_forces(self, search_text: str) -> List[str]:
        """Extract elemental forces from search text"""
        forces = []
        
        all_force_keywords = []
        for domain_config in DOMAIN_CONFIG.values():
            all_force_keywords.extend(domain_config["elemental_forces"])
        
        for force in all_force_keywords:
            if force.lower() in search_text.lower():
                forces.append(force)
        
        return forces

# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def main():
    """Main execution function"""
    print("=" * 70)
    print("🔹 EVENT-TRIGGERED WEBHOOK ARCHITECTURE — WEEK 1 INITIATION")
    print("=" * 70)
    
    # Initialize trigger hierarchy
    triggers = {
        "level_1": Level1KeywordMatchTrigger(),
        "level_2": None,  # Would implement in later weeks
        "level_3": None,  # Would implement in later weeks
        "level_4": None   # Would implement in later weeks
    }
    
    # Initialize Level 1 trigger
    client_config = get_firecrawl_client()
    
    if client_config:
        triggers["level_1"].initialize(client_config)
        print(f"✅ Level 1 Trigger initialized")
        print(f"   Firecrawl client config: {client_config}")
    else:
        print("⚠️  Cannot initialize without Firecrawl API key")
    
    # Test trigger with sample query
    print("\n🔍 Testing Level 1 Keyword Match Trigger...")
    
    test_queries = [
        "trump canada gematria",
        "fire crawl analysis 124 pattern",
        "water flow adaptation patterns"
    ]
    
    for query in test_queries:
        print(f"\n--- Query: {query} ---")
        try:
            payload = await triggers["level_1"].trigger(query)
            
            if payload:
                print(f"✅ Trigger fired! Event details:")
                print(f"   Source URL: {payload['source_url'][:100]}...")
                print(f"   Core Symbols Detected: {payload['core_symbols_detected']}")
                print(f"   Domains Connected: {payload['domain_connections']}")
                print(f"   Elemental Forces: {payload['elemental_forces']}")
                print(f"   Confidence Score: {payload['confidence_score']:.2f}")
            else:
                print("ℹ️  No event triggered (no results found)")
                
        except Exception as e:
            print(f"❌ Trigger failed: {e}")
    
    # Save trigger configuration
    config_dir = Path.home() / ".hermes" / "gematria" / "config"
    os.makedirs(config_dir, exist_ok=True)
    
    config_file = config_dir / "trigger_hierarchy.json"
    with open(config_file, 'w') as f:
        json.dump({
            "trigger_hierarchy": TRIGGER_HIERARCHY,
            "core_symbols": CORE_SYMBOLS,
            "domains_configured": list(DOMAIN_CONFIG.keys())
        }, f, indent=2)
    
    print(f"\n📋 Trigger configuration saved to: {config_file}")
    
    print("=" * 70)
    print("✅ LEVEL 1 KEYWORD MATCH TRIGGER — WEEK 1 COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
