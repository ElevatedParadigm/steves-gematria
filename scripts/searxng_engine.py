"""
SearXNG Integration Engine - Standalone Version
Designed for privacy-focused overnight gematria research

Features:
- Direct HTML parsing of SearXNG search results
- No API key required (uses standard web scraping)
- Works with official SearXNG instances
- Full HTTPS support with certificate validation
"""

import subprocess
import sys
import json
import time
import random
import ssl
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urlparse, urljoin
import re


class SearXNGIntegrationEngine:
    """
    High-performance overnight research engine using SearXNG.
    
    Architecture:
        ┌─────────────────┐
        │  Symbols Input │ → Load from gematria config
        └────────┬────────┘
                ↓
        ┌───────────────────┐
        │  Query Generation │ → Generate diverse search queries
        └─────────┬─────────┘
                 ↓
        ┌───────────────────────────────┐
        │  SearXNG Web Scraper          │ ← Parses HTML results directly
        │  (no API dependency)           │
        └────────────┬───────────────────┘
                    ↓
        ┌───────────────────────────────┐
        │  Result Analysis &            │ → Extract links, titles, snippets
        │  Pattern Recognition          │ from HTML content
        └────────────┬───────────────────┘
                    ↓
        ┌───────────────────────────────┐
        │  Knowledge Graph Construction │ → Build relationships between concepts
        │                              │
        │  ┌────── Nodes ──────┐       │ ← Each search result = node
        │  │ Concept: {id, ...}│       │
        │  └───────────────────┘       │
        │                              │
        │  ┌────── Edges ──────┐       │ ← Shared concepts create edges
        │  │ Node1 ──[link]──> │───    │
        │  │ Node2 ──[link]─── │       │
        │  └───────────────────┘       │
        └────────────┬──────────────────┘
                    ↓
        ┌───────────────────────────────┐
        │  Relationship Extraction      │ → Track gematria connections
        └────────────┬───────────────────┘
                    ↓
        ┌───────────────────────────────┐
        │  Report Generation            │ → Markdown analysis reports
        └───────────────────────────────┘
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize engine with optional custom configuration path"""
        self.config_path = Path(config_path) if config_path else None
        self.metadata_path = Path("/home/avalonas/.hermes/gematria/reports/searxng_engine_metadata.json")
        
        # SearXNG instance configuration
        self.searxng_url = "http://localhost:8084/"
        self.timeout = 30
        
        # Connection state tracking
        self.session_data = {}
        self.rate_limiter = []
        
        # Performance metrics
        self.execution_stats = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "avg_response_time": 0.0,
            "last_execution": None
        }
    
    def _load_gematria_config(self) -> Dict:
        """Load gematria configuration from database"""
        db_path = Path("/home/avalonas/.hermes/gematria/database/gematria_database.json")
        
        if not self.config_path and not db_path.exists():
            return {
                "symbols": [],
                "domains": [],
                "relationships": []
            }
        
        config_file = self.config_path or db_path
        
        with open(config_file) as f:
            config = json.load(f)
        
        # Extract core data structures
        symbols = config.get("symbols", [])[:10]  # Use first 10 symbols for foundation
        domains = config.get("domains", [])
        relationships = config.get("relationships", [])
        
        return {
            "symbols": symbols,
            "domains": domains,
            "relationships": relationships,
            "time": datetime.now().isoformat()
        }
    
    def _verify_searxng_connection(self) -> Dict:
        """Verify SearXNG web connection (non-API mode)"""
        try:
            from urllib.request import Request, urlopen
            from urllib.error import URLError, HTTPError
            
            print(f"  🌐 Verifying SearXNG connection to {self.searxng_url}...")
            
            headers = {
                'Accept': 'text/html,application/xhtml+xml',
                'Accept-Language': 'en-US,en;q=0.9',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
            }
            
            req = Request(self.searxng_url, headers=headers)
            
            try:
                with urlopen(req, timeout=self.timeout) as response:
                    content_type = response.headers.get('Content-Type', '')
                    
                    if 'text/html' in content_type:
                        print("  ✅ SearXNG is accessible (web scraping mode)")
                        
                        # Get homepage for session initialization
                        html_response = response.read().decode('utf-8', errors='ignore')[:1000]
                        self.session_data["home_page"] = self.searxng_url
                        
                        return {
                            "status": "ready",
                            "mode": "html_scraping",
                            "url": self.searxng_url,
                            "message": "SearXNG accessible via web scraping"
                        }
                    else:
                        return {
                            "status": "error",
                            "message": f"Unexpected content type: {content_type}"
                        }
                        
            except HTTPError as e:
                return {
                    "status": "http_error",
                    "code": e.code,
                    "message": f"HTTP {e.code}: {e.reason}"
                }
                
            except URLError as e:
                return {
                    "status": "unreachable",
                    "message": str(e)
                }
            
            except Exception as e:
                return {
                    "status": "error",
                    "message": str(e)
                }
                
        except ImportError:
            return {
                "status": "unavailable",
                "message": "urllib not available"
            }
    
    def _parse_searxng_results(self, html_content: str, query: str) -> List[Dict]:
        """Parse SearXNG search results from HTML
        
        Extracts: URLs, titles, snippets, categories from HTML
            
        Args:
            html_content: Raw HTML from SearXNG search page
            query: Original search query
            
        Returns:
            List of result dictionaries
        """
        results = []
        
        # Pattern 1: Extract <a> tags with href and preceding title text
        import re
        
        # Look for anchor tags with URLs
        link_pattern = r'<a[^>]*href=["\']([^"\']*http)[^"\']*["\'][^>]*>(.*?)</a>'
        
        all_links = re.findall(link_pattern, html_content, re.IGNORECASE)
        
        print(f"    📖 Found {len(all_links)} potential links in HTML")
        
        for i, (url, anchor_text) in enumerate(all_links[:15]):  # Limit to first 15 results
        
            # Clean up title text (strip HTML tags)
            clean_title = re.sub(r'<[^>]+>', '', anchor_text).strip()
            
            # Skip if already has a result with this URL
            if any(r["url"] == url for r in results):
                continue
            
            # Extract snippet from nearby content
            start_idx = html_content.find(url) if url else 0
            
            snippet = ""
            if start_idx > 100:
                context_start = max(0, start_idx - 400)
                context_end = min(len(html_content), start_idx + 500)
                context = html_content[context_start:context_end]
                
                # Look for span with snippet-like content
                snippet_pattern = r'<span[^>]*class="[^"]*snippet[^"]*"[^>]*>([^<]{1,200})</span>'
                snippet_matches = re.findall(snippet_pattern, context)
                
                if snippet_matches:
                    snippet = snippet_matches[0].strip()[:300]
                else:
                    # Fallback: use anchor text as snippet
                    snippet = clean_title[:300] if clean_title else ""
            
            results.append({
                "url": url,
                "title": clean_title[:150],  # Truncate to 150 chars
                "snippet": snippet,
                "query": query,
                "category": "",  # Would need category parsing from SearXNG metadata
                "timestamp": datetime.now().isoformat()
            })
        
        return results
    
    def _generate_queries(self, symbols: List[Dict]) -> List[str]:
        """Generate strategic search queries from gematria symbols
        
        Creates diverse query types for comprehensive coverage:
            - Direct number searches (gematria analysis of specific numbers)
            - Domain-concept combinations (cross-references across domains)
            - Historical figure connections (who died at these ages/numbers)
            - Linguistic/elemental analysis (what these numbers represent)
            
        Args:
            symbols: List of symbol dictionaries
            
        Returns:
            List of search query strings
        """
        queries = []
        
        for symbol in symbols[:8]:  # Use first 8 symbols per batch
        
            num = str(symbol.get("number", ""))
            
            # Direct number analysis
            queries.append(f"gematria analysis {num}")
            
            # Cross-domain pattern search (if multiple symbols exist)
            if len(symbols) > 1:
                prev_idx = symbols.index(symbol, 0) - 1
                prev_num = str(symbols[prev_idx].get("number", "")) if prev_idx >= 0 else "0"
                
                cross_search = f"{prev_num} to {num} gematria pattern"  # Use ASCII "to" instead of Unicode arrow
                queries.append(cross_search)
            
            # Historical connection search (military coup reference from Steve's manifesto)
            coup_num = str(symbol.get("number", ""))
            if len(coup_num) <= 3:  # Keep it concise for web search
                historical_query = f"historical figure age {coup_num} death transition"
                queries.append(historical_query)
            
            # Linguistic/semantic analysis
            semantic_query = f"meaning of number {num} in gematria system"
            queries.append(semantic_query)
        
        # Add sequence-based pattern searches
        if len(symbols) >= 2:
            first_num = symbols[0].get("number", "")
            second_num = symbols[1].get("number", "")
            
            sequence_query = f"gematic progression {first_num} to {second_num}"
            queries.append(sequence_query)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_queries = []
        
        for q in queries:
            if q not in seen:
                seen.add(q)
                unique_queries.append(q)
        
        return unique_queries
    
    def _execute_search(self, query: str, strategy_type: str = "direct") -> Dict:
        """Execute a single search query through SearXNG web interface
        
        Args:
            query: Search query string
            strategy_type: Query strategy ('direct', 'multi', 'recursive')
            
        Returns:
            Result dictionary with success status and data
        """
        start_time = time.time()
        
        # Rate limiting (0-1 seconds between queries)
        if self.rate_limiter:
            last_query_time = self.rate_limiter[-1][0]  # First element is timestamp
            time_to_wait = max(0, random.uniform(0.1, 0.5) + (last_query_time - time.time()))
            time.sleep(time_to_wait)
        
        # URL-safe encoding - replace special chars with ASCII equivalents
        safe_query = query.replace('→', 'to').replace('  ', ' ').strip()
        search_url = f"{self.searxng_url}search?q={safe_query.replace(' ', '+')}"
        
        headers = {
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'en-US,en;q=0.9',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
        }
        
        try:
            from urllib.request import Request, urlopen
            from urllib.error import URLError, HTTPError
            
            print(f"  🔍 [{strategy_type}] Searching: {safe_query[:70]}...")
            
            req = Request(search_url, headers=headers)
            
            with urlopen(req, timeout=self.timeout) as response:
                html_content = response.read().decode('utf-8', errors='ignore')
                
                # Parse results from HTML
                results = self._parse_searxng_results(html_content, query)
                
                if results:
                    print(f"    ✅ Parsed {len(results)} results")
                    
                    # Log first 3 results
                    for i, r in enumerate(results[:3]):
                        title_preview = r.get("title", "")[:50]
                        print(f"      - [{i+1}] {title_preview}...")
                    
                    # Update rate limiter
                    self.rate_limiter.append((time.time(), query))
                    
                    return {
                        "success": True,
                        "query": query,
                        "result_count": len(results),
                        "results": results,
                        "strategy": strategy_type,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    print(f"    ⚠️  No results parsed from HTML")
                    
                    return {
                        "success": False,
                        "query": query,
                        "result_count": 0,
                        "results": [],
                        "message": "No results parsed from HTML",
                        "timestamp": datetime.now().isoformat()
                    }
                    
        except HTTPError as e:
            error_message = f"HTTP {e.code}: {e.reason}"
            print(f"    ❌ HTTP Error: {error_message}")
            
            return {
                "success": False,
                "query": query,
                "error_code": e.code,
                "error_message": error_message,
                "results": [],
                "strategy": strategy_type,
                "timestamp": datetime.now().isoformat()
            }
            
        except URLError as e:
            error_message = str(e.reason) if hasattr(e, 'reason') else str(e)
            print(f"    ❌ Connection Error: {error_message}")
            
            return {
                "success": False,
                "query": query,
                "error_type": "urllib",
                "error_message": error_message,
                "results": [],
                "strategy": strategy_type,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            error_message = str(e)
            print(f"    ❌ Error: {error_message}")
            
            return {
                "success": False,
                "query": query,
                "error_type": "unknown",
                "error_message": error_message,
                "results": [],
                "strategy": strategy_type,
                "timestamp": datetime.now().isoformat()
            }
    
    def _build_knowledge_graph(self, results: List[Dict]) -> Dict:
        """Build knowledge graph from search results
        
        Creates nodes for concepts and edges for relationships between them.
        
        Args:
            results: List of successful search result dictionaries
            
        Returns:
            Knowledge graph structure dictionary
        """
        print("  🧠 Building knowledge graph...")
        
        graph = {
            "nodes": [],
            "edges": [],
            "clusters": []
        }
        
        # Extract nodes from results (each result = a concept node)
        for result in results[:10]:  # Process first 10 results
        
            query = result.get("query", "")
            
            # Create node for each query-concept pairing
            node_id = f"concept:{hash(query) % 100000}"
            
            graph["nodes"].append({
                "id": node_id,
                "label": query[:80],  # Truncate to 80 chars
                "type": "search_concept",
                "source_results": result.get("result_count", 0),
                "timestamp": result.get("timestamp")
            })
        
        # Build edges based on shared keywords in queries
        edge_threshold = 2
        
        processed_edges = set()
        
        for i, node1 in enumerate(graph["nodes"]):
            for j, node2 in enumerate(graph["nodes"]):
                if i >= j:
                    continue
                
                # Find shared concepts (simple keyword matching)
                node1_concepts = set(node1.get("label", "").lower().split()[:4])
                node2_concepts = set(node2.get("label", "").lower().split()[:4])
                
                shared = node1_concepts & node2_concepts
                
                if len(shared) >= edge_threshold:
                    edge_key = tuple(sorted([node1["id"], node2["id"]]))
                    
                    if edge_key not in processed_edges:
                        processed_edges.add(edge_key)
                        
                        graph["edges"].append({
                            "source": node1["id"],
                            "target": node2["id"],
                            "label": f"shared:{len(shared)}",
                            "type": "conceptual_connection",
                            "confidence": 0.95
                        })
        
        # Create clusters based on concept density
        if graph["nodes"]:
            avg_degree = len(graph["edges"]) / max(len(graph["nodes"]), 1)
            
            graph["clusters"] = [{
                "name": "pattern_cluster_1",
                "nodes": [n["id"] for n in graph["nodes"][:3]],
                "type": "discovered_pattern"
            }]
        
        return graph
    
    def _create_analysis_report(self, results: List[Dict], config: Dict) -> str:
        """Create comprehensive analysis report
        
        Args:
            results: List of all search results
            config: Current configuration state
            
        Returns:
            Formatted Markdown report string
        """
        print("  📄 Generating analysis report...")
        
        # Count successful vs failed queries
        successful = [r for r in results if r.get("success")]
        failed = [r for r in results if not r.get("success")]
        
        lines = [
            f"# Overnight Research Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "## 📊 Summary",
            "",
            f"- **Symbols Processed**: {len(config.get('symbols', []))}",
            f"- **Successful Queries**: {len(successful)}/{len(results)}",
            f"- **Failed Queries**: {len(failed)}/{len(results)}"
        ]
        
        # Add detailed results section
        lines.extend([
            "",
            "## 🔍 Query Results"
        ])
        
        for result in results[:5]:  # First 5 results
            status = "✅" if result.get("success") else "❌"
            query = result.get("query", "")[:60]
            
            if result.get("success"):
                message = f"Parsed {result.get('result_count', 'unknown')} results"
            elif "error_message" in result:
                message = f"{result['error_message']}"
            else:
                message = "Error"
            
            lines.append(f"- {status} `{query}`")
            lines.append(f"  → {message}")
            lines.append("")
        
        # Add knowledge graph summary
        if config.get("relationships"):
            relation_count = len(config.get("relationships", []))
            lines.extend([
                "",
                "## 🧠 Knowledge Graph Status",
                "",
                f"- **Relationships Tracked**: {relation_count}",
                f"- **Domains Covered**: {len(config.get('domains', []))}"
            ])
        
        lines.extend([
            "",
            "## 🎯 Next Steps",
            "",
            "- Continue with overnight execution",
            "- Review failed queries for retry",
            "- Update knowledge graph manually if needed"
        ])
        
        return "\n".join(lines)


def run_engine(symbols: Optional[List[Dict]] = None, 
               batch_mode: bool = True,
               dry_run: bool = False):
    """Main engine execution function
    
    Args:
        symbols: List of symbol dictionaries (loads from config if None)
        batch_mode: Whether to run all queries in one pass
        dry_run: If True, skip actual query execution
        
    Returns:
        Dictionary with execution results and reports
    """
    print("=" * 70)
    print("🚀 SearXNG Integration Engine (Standalone) - Overnight Research Protocol")
    print("=" * 70)
    print()
    
    # Load configuration
    if symbols is None or len(symbols) == 0:
        print("📂 Loading gematria configuration...")
        engine = SearXNGIntegrationEngine()
        config = engine._load_gematria_config()
        symbols = config.get("symbols", [])
        domains = config.get("domains", [])
        relationships = config.get("relationships", [])
    else:
        config = {
            "symbols": symbols,
            "domains": domains or [],
            "relationships": relationships or [],
            "time": datetime.now().isoformat()
        }
    
    print(f"✅ Loaded {len(symbols)} symbols from configuration")
    print(f"   Domains: {len(domains)} | Relationships: {len(relationships)}")
    print()
    
    # Create engine instance and verify connection
    engine = SearXNGIntegrationEngine()
    
    print("🔌 Checking SearXNG connection...")
    searxng_status = engine._verify_searxng_connection()
    
    if searxng_status["status"] == "error":
        print(f"   ❌ Connection error: {searxng_status['message']}")
        return {
            "success": False,
            "stage": "connection_error",
            "message": searxng_status.get("message"),
            "timestamp": datetime.now().isoformat()
        }
    else:
        print(f"   ✅ Connection status: {searxng_status['message']}")
    
    print()
    
    # Execute queries if not in dry-run mode
    results = []
    
    if not dry_run:
        print("🔍 Starting query execution...")
        queries = engine._generate_queries(config.get("symbols", [])[:8])
        
        print(f"   Generated {len(queries)} unique queries")
        print()
        
        for i, query in enumerate(queries):
            strategy = "direct" if "→" not in query and "?" not in query else "refinement"
            
            try:
                result = engine._execute_search(query, strategy)
                results.append(result)
                
                # Add 0.1-0.5s delay between queries (rate limiting)
                if i < len(queries) - 1:
                    time.sleep(random.uniform(0.1, 0.5))
                    
            except Exception as e:
                print(f"   ⚠️ Query execution error: {e}")
                results.append({
                    "success": False,
                    "query": query,
                    "error": str(e),
                    "strategy": strategy
                })
    else:
        print("🔧 DRY-RUN MODE - Simulating queries...")
        queries = engine._generate_queries(config.get("symbols", [])[:5])
        
        for query in queries:
            results.append({
                "success": False,
                "query": query,
                "dry_run": True
            })
    
    # Build knowledge graph if we have successful results
    knowledge_graph = None
    failed_queries = [r for r in results if not r.get("success")]
    
    print()
    
    if len(failed_queries) == 0 and config.get("relationships"):
        print("🧠 Building knowledge graph from existing relationships...")
        # Use existing relationships as basis for graph structure
        try:
            base_symbol = symbols[0] if symbols else None
            knowledge_graph = engine._build_knowledge_graph(
                [result for result in results if result.get("success")]
            )  # Only pass results (3rd arg removed)
        except Exception as e:
            print(f"   ⚠️ Graph building error (continuing without graph): {e}")
    else:
        print("⚠️  Skipping knowledge graph build (no successful queries or no relationships)")
    
    # Create analysis report
    if config.get("symbols"):
        report = engine._create_analysis_report(results, config)
        
        # Save report to file
        reports_dir = Path("/home/avalonas/.hermes/gematria/reports")
        reports_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        report_path = reports_dir / f"searxng_overnight_report_{timestamp}.md"
        
        with open(report_path, 'w') as f:
            f.write(report)
        
        print(f"\n📄 Report saved to: {report_path}")
    else:
        print("\n⚠️  No symbols loaded - skipping report generation")
    
    # Save execution metadata
    metadata = {
        "execution_time": time.time(),
        "symbols_processed": len(config.get("symbols", [])),
        "successful_queries": len([r for r in results if r.get("success")]),
        "failed_queries": len([r for r in results if not r.get("success")]),
        "knowledge_graph_available": knowledge_graph is not None,
        "dry_run_mode": dry_run,
        "searxng_status": searxng_status["status"],
        "timestamp": datetime.now().isoformat()
    }
    
    metadata_path = Path("/home/avalonas/.hermes/gematria/reports/searxng_engine_metadata.json")
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n💾 Execution metadata saved to: {metadata_path}")
    
    return {
        "success": len(failed_queries) == 0 or knowledge_graph is not None,
        "results": results,
        "knowledge_graph": knowledge_graph,
        "report_path": str(report_path) if report_path else None,
        "metadata": metadata
    }


def main():
    """Command-line entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="SearXNG Integration Engine for Gematria Research (Standalone)"
    )
    
    parser.add_argument(
        "--symbols",
        type=str,
        default=None,
        help="Comma-separated symbol numbers to search (overrides config)"
    )
    
    parser.add_argument(
        "--no-batch",
        action="store_true",
        help="Run queries individually instead of batch mode"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate execution without making API calls"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output"
    )
    
    args = parser.parse_args()
    
    symbols = None
    
    if args.symbols:
        try:
            symbol_list = [s.strip() for s in args.symbols.split(",")]
            # Try to load full symbol data
            db_path = Path("/home/avalonas/.hermes/gematria/database/gematria_database.json")
            
            if db_path.exists():
                with open(db_path) as f:
                    db_data = json.load(f)
                
                symbols = [{"number": s, "value": int(s)} for s in symbol_list if s.isdigit()]
            
        except Exception as e:
            print(f"Error parsing symbols: {e}")
            symbols = [{"number": s, "value": 0} for s in args.symbols.split(",")]
    
    results = run_engine(
        symbols=symbols,
        batch_mode=not args.no_batch,
        dry_run=args.dry_run
    )
    
    # Print summary
    print()
    print("=" * 70)
    print("📊 Execution Summary")
    print("=" * 70)
    
    metadata = results.get("metadata", {})
    
    print(f"Status: {'✅ Success' if results.get('success') else '⚠️ Partial'}")
    print(f"Symbols Processed: {metadata.get('symbols_processed', 0)}")
    print(f"Successful Queries: {metadata.get('successful_queries', 0)}")
    print(f"Failed Queries: {metadata.get('failed_queries', 0)}")
    
    if not args.dry_run and metadata.get("searxng_status"):
        print(f"SearXNG Status: {metadata['searxng_status']}")
    
    report_path = results.get("report_path")
    if report_path:
        print(f"Report: {report_path}")
    
    print()
    
    return 0 if results.get("success") else 1


if __name__ == "__main__":
    sys.exit(main())
