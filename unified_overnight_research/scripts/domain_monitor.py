#!/usr/bin/env python3
"""
Domain Monitor - News Feed and Research Database Monitoring

This script uses web_search, web_extract, and terminal tools to monitor
research domains for new developments, using Firecrawl for intelligent 
content extraction.

Usage:
    python domain_monitor.py --scan --domains math,bio,astronomy  # Scan specified domains
    python domain_monitor.py --monitor-domains                     # Start continuous monitoring
    python domain_monitor.py --epstein-files                      # Monitor Epstein files specifically
    python domain_monitor.py --keywords "gematria symbol patterns" # Monitor by keyword

Monitoring Domains:
- Mathematics (arxiv, mathoverflow, research repositories)
- Molecular Biology (bioRxiv, Nature, Science journals)
- Astronomy (arxiv astro-ph, NASA archives, observatory data)
- Geography (geographic information systems, mapping databases)
- Physics (arxiv physics, research preprints)
- Chemistry (chemical databases, reaction monitoring)
"""

import argparse
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

# Hermes Agent tools
from hermes_tools import web_search, web_extract, terminal


class DomainMonitor:
    """Monitor research domains for new developments and pattern detection."""
    
    def __init__(self, 
                 domain_database_path=None,
                 output_dir="."):
        """Initialize domain monitor with configuration."""
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Database paths for tracking found items
        self.pattern_db = self.output_dir / "patterns_database.json"
        self.domain_status = self.output_dir / "domain_status.json"
        
        # Firecrawl API (from gematria-firecrawl-integration skill)
        self.firecrawl_client = None  # Initialized by gematria-firecrawl-integration skill
        
        # Domain configurations
        self.domains = {
            "Mathematics": {
                "sources": [
                    "https://arxiv.org/list/math/",
                    "https://mathoverflow.net/questions",
                    "https://www.cambridge.org/core/journals/mathematical-proceedings-of-the-cambridge-philosophical-society"
                ],
                "keywords": ["fractal geometry", "golden ratio applications", 
                           "Fibonacci sequences mathematics", "graph theory protein folding"]
            },
            
            "Molecular Biology": {
                "sources": [
                    "https://www.biorxiv.org/content",
                    "https://pubmed.ncbi.nlm.nih.gov/",
                    "https://www.nature.com/ssubjects/genetics-and-genomics"
                ],
                "keywords": ["DNA structure analysis", "protein folding pathways",
                           "enzyme-substrate binding", "transmembrane proteins"]
            },
            
            "Astronomy": {
                "sources": [
                    "https://arxiv.org/list/astro-ph/",
                    "https://www.nasa.gov/news/",
                    "https://astronomy.osu.edu/news"
                ],
                "keywords": ["galaxy filament networks", "cosmic web structure",
                           "accretion disk spirals", "planetary ring systems"]
            },
            
            "Geography": {
                "sources": [
                    "https://www.usgs.gov/newsroom",
                    "https://earthobservatory.nasa.gov/",
                    "https://www.nationalgeographic.com/environment/"
                ],
                "keywords": ["volcanic island chains", "tectonic plate boundaries",
                           "mountain ranges bridges", "crossroads cities"]
            },
            
            "Physics": {
                "sources": [
                    "https://arxiv.org/list/physics/",
                    "https://www.aps.org/publications/",
                    "https://physicsworld.com/a/"
                ],
                "keywords": ["quantum tunneling", "event horizon physics",
                           "critical mass calculations", "phase transitions"]
            },
            
            "Chemistry": {
                "sources": [
                    "https://pubs.acs.org/news",
                    "https://www.rsc.org/newsroom/",
                    "https://www.chemicalxchange.com/"
                ],
                "keywords": ["catalyst activation energies", "bond dissociation",
                           "electron affinity measurements", "zwitterionic equilibrium"]
            }
        }
    
    def search_domain_patterns(self, domain: str, keywords: list = None,
                               limit: int = 5) -> dict:
        """
        Search for pattern-related content in a specific domain.
        
        Args:
            domain: Domain name (e.g., "Mathematics", "Molecular Biology")
            keywords: Keywords to search for (optional, uses domain defaults)
            limit: Number of results to return
    
        Returns:
            dict with search results and analysis
        """
        
        # Use keywords from domain config or provided
        if not keywords:
            keywords = self.domains[domain].get("keywords", [])
        
        # Build comprehensive search query
        domain_query = f"{domain} research patterns {', '.join(keywords[:3])}"
        
        print(f"\n🔍 Searching domain: {domain}")
        print(f"   Query: {domain_query}")
        
        # Use web_search tool (or Firecrawl if available)
        try:
            results = web_search(query=domain_query, limit=limit)
            
            search_data = {
                "domain": domain,
                "query": domain_query,
                "timestamp": datetime.now().isoformat(),
                "results": [],
                "pattern_correlations": {},
                "domain_overlap_signals": []
            }
            
            # Process each result
            for item in results.get("data", {}).get("web", []):
                url = item.get("url", "")
                title = item.get("title", "")
                description = item.get("description", "")
                
                search_data["results"].append({
                    "url": url,
                    "title": title[:200],  # Truncate long titles
                    "snippet": description[:300]
                })
                
                # Check for pattern correlations
                correlation = self.detect_pattern_correlation(title, description)
                if correlation:
                    domain_name = correlation.get("domain", domain)
                    if domain_name not in search_data["pattern_correlations"]:
                        search_data["pattern_correlations"][domain_name] = []
                    
                    search_data["pattern_correlations"][domain_name].append({
                        "signal": correlation.get("signal_type"),
                        "description": correlation.get("description")
                    })
                
                # Check for domain overlap signals
                overlaps = self.detect_domain_overlaps(title, description)
                if overlaps:
                    search_data["domain_overlap_signals"].extend(overlaps)
            
            # Save to database
            self.update_pattern_database(search_data)
            
            print(f"   Found {len(results.get('data', {}).get('web', []))} results")
            
            return search_data
            
        except Exception as e:
            print(f"   ⚠️  Search error: {str(e)}")
            return {"error": str(e)}
    
    def detect_pattern_correlation(self, title: str, 
                                   description: str = "") -> dict:
        """
        Detect pattern correlations in search results.
        
        Args:
            title: Result title
            description: Result description
    
        Returns:
            dict with correlation analysis or None if no patterns found
        """
        
        # Check for threshold/bridge language (124° patterns)
        threshold_keywords = [
            "bridge", "threshold", "connection", "interface", 
            "transformation", "tunneling", "barrier", "horizon"
        ]
        
        # Check for completion/wholeness language (666° → 9)
        completion_keywords = [
            "completion", "wholeness", "integration", "unified", 
            "holistic", "cycle complete", "reduction to"
        ]
        
        # Check for recursive patterns (111°)
        recursive_keywords = [
            "recursive", "fractal", "iterative", "self-similar",
            "recursive loop", "dimensional bridge"
        ]
        
        # Check for molecular-quantum connections (55°)
        molecular_quantum_keywords = [
            "molecular", "quantum", "electron", "protein channel",
            "transmembrane", "activation energy", "catalyst"
        ]
        
        # Check for critical thresholds (963°)
        threshold_energy_keywords = [
            "critical mass", "phase transition", "tipping point",
            "vessel holds fire", "transformation bridge"
        ]
        
        # Check for domain integration (279°)
        integration_keywords = [
            "integrate", "multi-domain", "cross-disciplinary",
            "religious secular", "scientific spiritual"
        ]
        
        detected_patterns = []
        
        # Analyze title and description
        text_to_analyze = f"{title} {description}"
        
        for keyword_group in [threshold_keywords, recursive_keywords, 
                              molecular_quantum_keywords]:
            if any(kw.lower() in text_to_analyze.lower() for kw in keyword_group):
                detected_patterns.append({
                    "type": "threshold/bridge",
                    "signal_strength": "strong" if len(keyword_group) > 2 else "moderate",
                    "context": f"Pattern detected in {text_to_analyze[:100]}"
                })
        
        # Check for domain overlap signals
        domain_overlap_terms = [
            "interdisciplinary", "multidisciplinary", "cross-domain",
            "connects", "bridges", "links between"
        ]
        
        if any(term.lower() in text_to_analyze.lower() for term in domain_overlap_terms):
            detected_patterns.append({
                "type": "domain_overlap",
                "signal_strength": "strong",
                "context": "Cross-domain connection identified"
            })
        
        if detected_patterns:
            return {
                "domain": self._infer_domain_from_text(title, description),
                "signal_type": "pattern_correlation",
                "patterns": detected_patterns
            }
        
        return None
    
    def detect_domain_overlaps(self, title: str, 
                               description: str = "") -> list:
        """
        Detect domain overlap signals in search results.
        
        Args:
            title: Result title
            description: Result description
    
        Returns:
            List of domain overlap signals
        """
        
        overlaps = []
        text_to_analyze = f"{title} {description}"
        
        # Check for multi-domain references
        if any(term.lower() in text_to_analyze.lower() for term in [
            "mathematics biology", "astronomy physics", 
            "molecular geometry", "cosmic chemistry"
        ]):
            overlaps.append({
                "type": "primary_secondary_domain_overlap",
                "source": title[:100],
                "confidence": 0.85
            })
        
        # Check for bridge language indicating domain connection
        if any(term.lower() in text_to_analyze.lower() for term in [
            "bridge between", "connecting", "unifying", 
            "integrating multiple"
        ]):
            overlaps.append({
                "type": "domain_bridge_structure",
                "source": title[:100],
                "confidence": 0.8
            })
        
        return overlaps
    
    def _infer_domain_from_text(self, title: str, 
                                description: str = "") -> str:
        """Infer which domain a result belongs to."""
        
        text_lower = f"{title} {description}".lower()
        
        domain_indicators = {
            "Mathematics": ["mathematical", "equation", "formula", "theorem"],
            "Molecular Biology": ["DNA", "protein", "enzyme", "cell", "molecule"],
            "Astronomy": ["galaxy", "cosmic", "star", "planet", "orbit"],
            "Geography": ["geographic", "landscape", "island", "mountain", "river"],
            "Physics": ["quantum", "particle", "energy", "force", "dimension"],
            "Chemistry": ["chemical", "molecule", "reaction", "element", "compound"]
        }
        
        for domain, indicators in domain_indicators.items():
            if any(ind.lower() in text_lower for ind in indicators):
                return domain
        
        return "General"  # Fallback
    
    def update_pattern_database(self, new_data: dict):
        """
        Update the pattern database with new findings.
        
        Args:
            new_data: Search data to add to database
        """
        
        try:
            # Load existing database or create new
            if self.pattern_db.exists():
                with open(self.pattern_db, 'r') as f:
                    db = json.load(f)
            else:
                db = {
                    "patterns": [],
                    "domain_status": {}
                }
            
            # Add new pattern to database
            db["patterns"].append({
                "timestamp": datetime.now().isoformat(),
                "domain": new_data.get("domain"),
                "source": new_data.get("results", [{}])[0].get("title") if new_data.get("results") else "Unknown"
            })
            
            # Limit database size (keep last 100 patterns)
            db["patterns"] = db["patterns"][-100:]
            
            # Save updated database
            with open(self.pattern_db, 'w') as f:
                json.dump(db, f, indent=2)
            
            print(f"   ✅ Updated pattern database")
            
        except Exception as e:
            print(f"   ⚠️  Could not update database: {str(e)}")
    
    def scan_all_domains(self):
        """Scan all configured domains for patterns."""
        
        print("\n" + "=" * 70)
        print("🔍 SCANNING ALL RESEARCH DOMAINS FOR PATTERNS")
        print("=" * 70)
        
        total_results = 0
        
        for domain_name, config in self.domains.items():
            # Search each domain
            result = self.search_domain_patterns(domain=domain_name)
            
            if result.get("error"):
                continue
            
            total_results += len(result.get("results", []))
        
        print(f"\n📊 Scan Complete:")
        print(f"   Total results found: {total_results}")
        print(f"   Domain database updated")
    
    def monitor_news_feeds(self):
        """
        Monitor news feeds for research domain updates.
        
        Returns:
            List of recent news items from configured domains
        """
        
        print("\n📰 Monitoring Research News Feeds...")
        
        news_items = []
        
        # Monitor each domain's news sources
        for domain_name, config in self.domains.items():
            print(f"\n   Domain: {domain_name}")
            
            for source_url in config["sources"]:
                try:
                    # Extract content from news source
                    result = web_extract(urls=[source_url])
                    
                    if result.get("results"):
                        for item in result["results"]:
                            if item.get("title") and "news" in item.get("title", "").lower():
                                news_items.append({
                                    "domain": domain_name,
                                    "source": source_url,
                                    "title": item.get("title", ""),
                                    "content": item.get("content", "")[:500],
                                    "timestamp": datetime.now().isoformat()
                                })
                                
                except Exception as e:
                    print(f"      ⚠️  Could not extract from {source_url}: {str(e)}")
        
        # Save news items to file
        news_file = self.output_dir / "research_news.json"
        with open(news_file, 'w') as f:
            json.dump({
                "news_items": news_items,
                "timestamp": datetime.now().isoformat()
            }, f, indent=2)
        
        print(f"\n📰 Found {len(news_items)} recent news items")
        print(f"   Saved to: {news_file}")
        
        return news_items


def main():
    """Main entry point for domain monitor."""
    
    parser = argparse.ArgumentParser(
        description="Monitor research domains for new developments"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # Scan all domains command
    scan_parser = subparsers.add_parser("scan", 
                                        help="Scan all configured domains for patterns")
    
    # Monitor news feeds command
    monitor_parser = subparsers.add_parser("monitor-domains",
                                           help="Start monitoring news feeds")
    
    # Epstein files monitoring (specific)
    epstein_parser = subparsers.add_parser("epstein-files",
                                           help="Monitor Epstein files release specifically")
    
    # Keywords-based monitoring
    keywords_parser = subparsers.add_parser("keywords",
                                            help="Monitor by custom keywords")
    keywords_parser.add_argument("--keywords", required=True,
                                 help="Keywords to monitor (e.g., 'gematria patterns')")
    
    # Pattern database command
    db_parser = subparsers.add_parser("patterns",
                                      help="View/update pattern database")
    db_parser.add_argument("--add", nargs="+", default=None,
                          help="Patterns to add to database")
    db_parser.add_argument("--clear", action="store_true",
                          help="Clear pattern database")
    
    args = parser.parse_args()
    
    # Initialize monitor
    output_path = Path("/home/avalonas/.hermes/gematria/unified_overnight_research/domains")
    monitor = DomainMonitor(output_dir=output_path)
    
    # Handle commands
    if args.command == "scan":
        monitor.scan_all_domains()
        
    elif args.command == "monitor-domains":
        news_items = monitor.monitor_news_feeds()
        
    elif args.command == "epstein-files":
        print("\n📂 Monitoring Epstein Files Release...")
        
        # Search for recent Epstein files announcements
        epstein_query = (
            "Epstein files release Justice Department court filings announcement"
        )
        
        try:
            results = web_search(query=epstein_query, limit=5)
            
            print(f"\n📂 Recent Epstein Files Results:")
            
            for item in results.get("data", {}).get("web", []):
                print(f"\n   [{item.get('title', 'No title')}")
                print(f"      URL: {item.get('url', '')}")
                if item.get('description'):
                    desc = item['description'][:200]
                    print(f"      {desc}...")
            
            # Save results
            output_file = output_path / "epstein_files_results.json"
            with open(output_file, 'w') as f:
                json.dump({
                    "query": epstein_query,
                    "timestamp": datetime.now().isoformat(),
                    "results": results.get("data", {})
                }, f, indent=2)
            
            print(f"\n📂 Results saved to: {output_file}")
            
        except Exception as e:
            print(f"⚠️  Search error: {str(e)}")
        
    elif args.command == "keywords":
        # Search with custom keywords
        search_query = f"research patterns {args.keywords}"
        
        try:
            results = web_search(query=search_query, limit=5)
            
            print(f"\n🔍 Search Results for: '{search_query}'")
            
            for item in results.get("data", {}).get("web", []):
                print(f"\n   [{item.get('title', 'No title')[:60]}...")
                
        except Exception as e:
            print(f"⚠️  Search error: {str(e)}")
        
    elif args.command == "patterns":
        if args.add:
            # Add patterns to database (placeholder for now)
            print(f"\n📝 Adding patterns to database...")
            
        elif args.clear:
            # Clear pattern database
            try:
                with open(monitor.pattern_db, 'w') as f:
                    json.dump({"patterns": []}, f)
                print(f"✅ Pattern database cleared")
            except Exception as e:
                print(f"⚠️  Could not clear database: {str(e)}")
            
        else:
            # View current patterns
            if monitor.pattern_db.exists():
                with open(monitor.pattern_db, 'r') as f:
                    db = json.load(f)
                
                print(f"\n📊 Current Patterns Database:")
                print(f"   Total patterns: {len(db.get('patterns', []))}")
                
                if db.get("patterns"):
                    for pattern in db["patterns"][-5:]:  # Show last 5
                        print(f"\n      [{pattern['timestamp'][:19]}]")
                        print(f"        Domain: {pattern.get('domain')}")
                        print(f"        Source: {pattern.get('source')[:80]}...")
            else:
                print("No patterns found in database yet.")


if __name__ == "__main__":
    main()
