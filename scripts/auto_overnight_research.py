#!/usr/bin/env python3
"""
Unified Overnight Research Engine
Combines ImageSeed AI research with Firecrawl API for gematria pattern discovery
"""

import os
import sys
import json
import time
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
import requests

# Suppress excessive logging from imported libraries
logging.getLogger('httpx').setLevel(logging.CRITICAL)
logging.getLogger('uvicorn').setLevel(logging.WARNING)

# Import from gematria-core subpackage
sys.path.insert(0, str(Path.home() / ".hermes"))
from gematria_core import (
    GematicProcessor, ImageSeed, SymbolicAnalysisEngine, KnowledgeGraphManager
)


# ============================================================================
# CONFIGURATION
# ============================================================================

CONFIG = {
    "core_symbols": [124, 963, 55, 111, 279, 666],
    "domains": [
        {"name": "geographic", "sources": ["places"], "keywords": ["mountains", "rivers", "cities"]},
        {"name": "military", "sources": ["units", "operations"], "keywords": ["division", "battalion", "regiment"]},
        {"name": "elemental", "sources": ["forces"], "keywords": ["fire", "water", "earth", "air"]},
        {"name": "religious", "sources": ["texts", "figures"], "keywords": ["sacred", "covenant", "temple"]},
    ],
    "output_dir": Path.home() / ".hermes/gematria/obsidian_exports",
    "image_seed_engine": Path.home() / ".hermes/image-seed-engine",
    "firecrawl_api_key_env": "~/.hermes/.env",
    "max_concurrent_queries": 3,
    "research_iterations": 2,  # How many research cycles to run
}

CONFIG["output_dir"] = CONFIG["output_dir"].resolve()

# Load Firecrawl API key from env file
def load_firecrawl_api_key():
    """Load FIRECRAWL_API_KEY from .env file at specified path."""
    import configparser
    env_path = Path(CONFIG["firecrawl_api_key_env"]).expanduser()
    if not env_path.exists():
        return None
    
    parser = configparser.ConfigParser()
    parser.read(env_path)
    
    # Try FIRECRAWL_API_KEY first, fall back to FIRECRAWL_CLOUD_API_KEY
    api_key = parser.get("firecrawl", "FIRECRAWL_API_KEY", fallback=None)
    if not api_key:
        api_key = parser.get("firecrawl", "FIRECRAWL_CLOUD_API_KEY", fallback=None)
    
    return api_key

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def generate_search_queries(symbol, domain_configs):
    """Generate diverse search queries for a given symbol and domains."""
    queries = []
    
    # Core concepts
    concept_terms = [
        "Universal Bridge analysis",
        "Completion Threshold patterns", 
        "Elemental Cycle correlations",
        "Vessel Fire dynamics",
        "Harmony Integration patterns"
    ]
    
    for i, term in enumerate(concept_terms):
        queries.append(f"{term} symbolism {symbol}")
        queries.append(f"{term} gematria study {symbol}")
        queries.append(term)
        queries.append(term + f" numerical analysis {symbol}")
        queries.append(term + f" symbolic meaning {symbol}")
    
    # Domain-specific queries (but won't use domain configs here as they'd cause empty results)
    for i in range(2):
        queries.append(f"esoteric numerology threshold patterns")
        queries.append(f"symbolic mathematics completion cycles")
    
    # Add variations with number breakdowns
    queries.append(f"{symbol} prime factorization significance")
    queries.append(f"{symbol} reduction 9 pattern analysis")
    
    return list(set(queries))[:15]  # Limit to 15 unique queries


def format_markdown_table(headers, rows):
    """Format a list of rows into an ASCII markdown table."""
    if not rows:
        return ""
    
    lines = []
    
    # Calculate column widths
    col_widths = [len(str(h)) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Build header line
    header_line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    lines.append(header_line)
    
    # Build separator line
    separator = "-+-".join("-" * w for w in col_widths)
    lines.append(separator)
    
    # Build data rows
    for row in rows:
        data_line = " | ".join(str(c).ljust(col_widths[i]) for i, c in enumerate(row))
        lines.append(data_line)
    
    return "\n".join(lines)


def create_timestamped_filename():
    """Create a timestamped filename with consistent formatting."""
    ts_str = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    hash_part = hashlib.md5(f"overnight_{ts_str}".encode()).hexdigest()[:6]
    
    return f"{datetime.now().strftime('%Y%m%d')}_{hash_part}"


def extract_core_concepts(text):
    """Extract core symbolic concepts from research results."""
    concepts = []
    
    # Keywords to search for
    concept_keywords = [
        "Universal Bridge", "Completion Threshold", "Elemental Cycle",
        "Vessel Fire", "Harmony Integration", "Reduction Pattern"
    ]
    
    for keyword in concept_keywords:
        if keyword.lower() in text.lower():
            concepts.append({
                "concept": keyword,
                "relevance": 1.0 if keyword.lower() in text.lower() else 0.5
            })
    
    return concepts


# ============================================================================
# MAIN RESEARCH ENGINE
# ============================================================================

class UnifiedOvernightResearchEngine:
    
    def __init__(self):
        self.gematic = GematicProcessor(
            symbols=CONFIG["core_symbols"],
            domains={d["name"]: d for d in CONFIG["domains"]}
        )
        self.image_seed = ImageSeed()
        self.kg_manager = KnowledgeGraphManager(
            db_path="/home/avalonas/.hermes/gematria/database"
        )
        
        self.api_key = load_firecrawl_api_key()
        self.current_results: List[Dict[str, Any]] = []
        self.query_count = 0
        
    def run_research_cycle(self):
        """Execute one research cycle."""
        print(f"\n🔍 Starting Research Cycle")
        
        # Generate fresh queries for this cycle
        seed_queries = generate_search_queries(124, CONFIG["domains"])
        
        # Track results across cycles
        all_results: List[Dict[str, Any]] = []
        
        for iteration in range(CONFIG["research_iterations"]):
            if iteration > 0:
                time.sleep(5)  # Space out queries
            
            cycle_results = self._execute_query_batch(seed_queries.copy())
            all_results.extend(cycle_results)
            
            # Track query consumption and adjust batch size
            active_queries = len([r for r in cycle_results if r.get("success")])
            consumed_per_query = len(seed_queries) / max(active_queries, 1)
            
            if len(all_results) >= 50:
                print(f"⚠️ Query efficiency low ({consumed_per_query:.1f} links/query)")
                break
        
        return all_results
    
    def _execute_query_batch(self, queries):
        """Execute a batch of research queries."""
        results = []
        
        if self.api_key:
            for query in queries:
                result = self._query_firecrawl(query)
                if result:
                    results.append(result)
                    
                    # Progress reporting
                    self.query_count += 1
                    if self.query_count % 5 == 0:
                        print(f"📊 Queries completed: {self.query_count}")
        
        return results
    
    def _query_firecrawl(self, query: str) -> Optional[Dict[str, Any]]:
        """Execute a single Firecrawl search with timeout protection."""
        url = "http://localhost:3002/v1/search"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        params = {
            "query": query,
            "options": {
                "pageOptions": {"limit": 20}
            }
        }
        
        try:
            # Use HTTP instead of HTTPS for self-hosted local instance
            response = requests.post(url, json=params, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                results_list = []
                if "data" in data and "results" in data["data"]:
                    for item in data["data"]["results"]:
                        results_list.append({
                            "url": item.get("url", ""),
                            "title": item.get("title", ""),
                            "markdown": item.get("markdown", "")
                        })
                
                return {
                    "query": query,
                    "success": True,
                    "results_count": len(results_list),
                    "timestamp": datetime.now().isoformat(),
                    "data": data
                }
            else:
                return {
                    "query": query,
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "timestamp": datetime.now().isoformat()
                }
                
        except requests.exceptions.Timeout:
            print(f"⏰ Timeout on query: {query}")
            return None
        except Exception as e:
            print(f"❌ Query error for '{query}': {str(e)[:100]}")
            return {
                "query": query,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def process_results(self, results: List[Dict[str, Any]]):
        """Process and enrich research results."""
        processed = []
        
        for result in results:
            processed_result = self._enrich_result(result)
            processed.append(processed_result)
            
        return processed
    
    def _enrich_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich a raw research result with symbol analysis."""
        if not result.get("success"):
            return result
        
        url = result.get("url", "")
        markdown = result.get("markdown", "")
        
        # Extract gematria patterns from URL and content
        enriched_result = {
            "query": result.get("query", ""),
            "core_symbol_detected": False,
            "symbol_value": None,
            "url": url,
            "title": "",
            "markdown": markdown[:2000],  # Truncate for storage
            "relevance_keywords": [],
            "extraction_timestamp": result.get("timestamp", ""),
        }
        
        # Search for core symbols in content (124, 963, 55, 111, 279, 666)
        symbol_strings = ["124", "963", "55", "111", "279", "666"]
        for symbol in symbol_strings:
            if symbol in url or symbol in markdown:
                enriched_result["core_symbol_detected"] = True
                enriched_result["symbol_value"] = int(symbol)
                
                # Find all occurrences
                matches = len(url) + markdown.count(symbol)
                enriched_result["occurrences"] = matches
                
                # Add to relevance keywords
                keyword = f"Symbol {symbol} detected"
                if keyword not in enriched_result["relevance_keywords"]:
                    enriched_result["relevance_keywords"].append(keyword)
        
        return enriched_result
    
    def analyze_symbolic_patterns(self, results: List[Dict[str, Any]]):
        """Analyze discovered symbolic patterns."""
        analysis = {
            "total_results": len(results),
            "symbol_breakdown": {},
            "domain_convergence_points": [],
            "key_findings": []
        }
        
        # Group by symbol
        for result in results:
            symbol = result.get("symbol_value")
            if symbol:
                analysis["symbol_breakdown"][symbol] = {
                    "occurrences": analysis["symbol_breakdown"].get(symbol, 0) + 1,
                    "relevance_keywords": list(set(analysis["symbol_breakdown"][symbol].get("relevance_keywords", []) | set(result.get("relevance_keywords", []))))
                }
        
        # Identify domain convergence points
        keywords = {}
        for result in results:
            for keyword in result.get("relevance_keywords", []):
                base_keyword = keyword.split()[0] if keyword else "unknown"
                keywords[base_keyword] = keywords.get(base_keyword, 0) + 1
        
        # Find convergence points (keywords appearing in multiple symbol contexts)
        analysis["domain_convergence_points"] = [
            {"keyword": k, "count": v} for k, v in sorted(keywords.items(), key=lambda x: -x[1])[:5]
        ]
        
        return analysis
    
    def generate_outputs(self, processed_results: List[Dict[str, Any]]):
        """Generate all required output files."""
        filename = create_timestamped_filename()
        
        # 1. CORE_SYMBOLS_SUMMARY.md (or update existing)
        summary_path = CONFIG["output_dir"] / "CORE_SYMBOLS_SUMMARY.md"
        if not summary_path.exists():
            self._create_core_symbols_summary(summary_path)
        
        # 2. ANALYSIS_TIMELINE.md (append to existing)
        timeline_path = CONFIG["output_dir"] / "ANALYSIS_TIMELINE.md"
        if timeline_path.exists():
            self._append_analysis_timeline(timeline_path, processed_results)
        
        # 3. DOMAIN_CONVERGENCE_REPORT.md (create new with findings)
        convergence_path = CONFIG["output_dir"] / "DOMAIN_CONVERGENCE_REPORT.md"
        analysis = self.analyze_symbolic_patterns(processed_results)
        self._create_domain_convergence_report(convergence_path, analysis)
        
        # 4. PATTERN_MATRIX.md (update with new patterns)
        pattern_path = CONFIG["output_dir"] / "PATTERN_MATRIX.md"
        if pattern_path.exists():
            self._append_pattern_matrix(pattern_path, processed_results)
        
        # 5. Update database
        self.kg_manager.update_discovered_items(processed_results)
        
        return summary_path, timeline_path, convergence_path
    
    def _create_core_symbols_summary(self, path):
        """Create initial core symbols summary template."""
        content = "# Core Symbols Discovery Summary\n"
        content += f"**Generated:** {datetime.now().isoformat()}\n\n"
        content += "## Overview\n"
        content += "- **Core Symbols Tracked**: 124, 963, 55, 111, 279, 666\n"
        content += "- **Domains Analyzed**: Geographic, Military, Elemental, Religious\n"
        content += "- **Research Method**: Firecrawl AI Search + ImageSeed Analysis\n\n"
        content += "## Symbol Discovery Log\n\n"
        content += "| Symbol | First Detected | Domain Convergence | Cross-Reference Count |\n|--------|----------------|--------------------|----------------------|\n"
        
        # Extract discovered symbols from results
        symbols_found = {}
        for result in self.current_results:
            symbol = result.get("symbol_value")
            if symbol and not symbols_found.get(symbol):
                symbols_found[symbol] = {
                    "first_detected": result.get("extraction_timestamp", ""),
                    "domain_convergence": "Pending Analysis"
                }
        
        for symbol, data in sorted(symbols_found.items()):
            content += f"| {symbol} | {data['first_detected']} | {data['domain_convergence']} | 0 |\n"
        
        with open(path, 'w') as f:
            f.write(content)
    
    def _append_analysis_timeline(self, path, results):
        """Append new entries to analysis timeline."""
        timestamp = datetime.now().isoformat()
        
        for result in results:
            domain_convergence = ", ".join(result.get("relevance_keywords", [])[:3])
            
            with open(path, 'a') as f:
                f.write(f"## {timestamp}\n")
                f.write(f"- Symbol: **{result.get('symbol_value', '?')}**\n")
                f.write(f"- Domain Convergence: `{domain_convergence}`\n")
                f.write(f"- Cross-Reference Context: Found via search query\n")
                f.write("---\n\n")
    
    def _create_domain_convergence_report(self, path, analysis):
        """Create domain convergence analysis report."""
        content = "# Domain Convergence Analysis Report\n\n"
        content += f"**Generated:** {datetime.now().isoformat()}\n\n"
        content += "## Symbol Breakdown\n\n"
        
        for symbol, data in sorted(analysis.get("symbol_breakdown", {}).items()):
            content += f"### Symbol **{symbol}**\n\n"
            occurrences = data.get("occurrences", 0)
            keywords = ", ".join(data.get("relevance_keywords", [])[:5])
            content += f"- **Occurrences**: {occurrences}\n"
            if keywords:
                content += f"- **Key Keywords**: `{keywords}`\n\n"
        
        content += "## Domain Convergence Points\n\n"
        for point in analysis.get("domain_convergence_points", []):
            content += f"- **{point['keyword']}** ({point['count']} occurrences)\n"
        
        with open(path, 'w') as f:
            f.write(content)
    
    def _append_pattern_matrix(self, path, results):
        """Append new patterns to matrix."""
        for result in results[:10]:  # Limit to first 10 per batch
            if result.get("core_symbol_detected"):
                symbol = str(result["symbol_value"])
                keyword = ", ".join(result.get("relevance_keywords", [])[:2])
                
                with open(path, 'a') as f:
                    f.write(f"### New Pattern Discovered\n")
                    f.write(f"- **Symbol**: {symbol}\n")
                    f.write(f"- **Keywords**: `{keyword}`\n")
                    f.write("---\n\n")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution entry point."""
    print("=" * 60)
    print("UNIFIED OVERNIGHT RESEARCH ENGINE")
    print("Combining ImageSeed AI + Firecrawl API for gematria analysis")
    print("=" * 60)
    
    engine = UnifiedOvernightResearchEngine()
    
    try:
        # Run research cycle with timeout protection
        results = engine.run_research_cycle()
        
        if results:
            print(f"\n✅ Processed {len(results)} research results")
            
            # Process and enrich results
            processed = engine.process_results(results)
            print(f"📊 Enriched {len(processed)} results with symbol analysis")
            
            # Generate outputs
            summary_path, timeline_path, convergence_path = \
                engine.generate_outputs(processed)
            
            print(f"\n📁 Generated outputs:")
            print(f"   - Summary: {summary_path}")
            print(f"   - Timeline: {timeline_path}")
            print(f"   - Convergence Report: {convergence_path}")
        else:
            print("\n⚠️ No research results generated")
    
    except Exception as e:
        print(f"\n❌ Research execution failed: {str(e)[:200]}")
        raise
    
    finally:
        # Always output summary to stdout for log capture
        summary = engine.kg_manager.get_output_summary()
        print(summary)


if __name__ == "__main__":
    main()
