#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Overnight Research Runner - Manual Protocol v2.0
Uses generated Hellboy image analysis queries to scan web and update knowledge graph
Falls back to database-only analysis if web searches unavailable
"""

import json
import re
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import quote as urlquote

class OvernightResearchRunner:
    """
    Runs overnight research protocol with Hellboy-derived queries.
    Supports both web search and database-only modes.
    """
    
    def __init__(self):
        self.db_path = Path.home() / '.hermes' / 'gematria' / 'database' / 'gematria_database.json'
        self.research_logs_dir = Path.home() / '.hermes' / 'gematria' / 'research_logs'
        self.results_count = 0
        self.web_search_available = False
        
    def load_queries_from_analysis(self, timestamp=None):
        """Load research queries from Hellboy analysis file"""
        
        # Try with timestamp first, then fallback to latest
        possible_files = [
            f"hellboy_image_analysis_20260428.json",  # Yesterday
            "hellboy_image_analysis_20260428.json",   # Original name without time
            f"hellboy_image_analysis_{timestamp or datetime.now().strftime('%Y%m%d')}.json"
        ]
        
        analysis_file = None
        for filename in possible_files:
            filepath = self.research_logs_dir / filename
            if filepath.exists():
                with open(filepath) as f:
                    return json.load(f)
        
        print("⚠️  No Hellboy analysis file found! Running database-only analysis...")
        return None
    
    def test_web_search(self, query="Hellboy numerology"):
        """Test if web search is available (using curl or requests)"""
        print("\n🔍 Testing web search connectivity...")
        
        try:
            # Method 1: Try Firecrawl cloud endpoint as backup
            import requests
            
            # Check env file for API key
            env_file = Path.home() / '.hermes' / '.env'
            api_key = None
            if env_file.exists():
                with open(env_file) as f:
                    for line in f:
                        if 'FIRECRAWL_API_KEY' in line.upper():
                            # Extract value (remove quotes and whitespace)
                            match = re.search(r'FIRECRAWL_API_KEY\s*[=:]\s*"([^"]*)"', line, re.IGNORECASE)
                            if match:
                                api_key = match.group(1).strip()
                        
            if not api_key:
                # Try without key for test (some endpoints allow it)
                api_key = "test-key"
            
            # Test with small search query
            response = requests.get(
                "https://api.firecrawl.dev/v1/scrape",
                params={
                    'url': 'https://en.wikipedia.org/wiki/Numerology',
                    'formats': ['markdown']
                },
                headers={
                    'Authorization': f'Bearer {api_key}' if api_key != 'test-key' else '',
                    'Content-Type': 'application/json'
                }
            )
            
            if response.status_code in [200, 206]:
                self.web_search_available = True
                print("✅ Web search available via Firecrawl Cloud API")
                return True
            
        except Exception as e:
            print(f"⚠️  Web search test failed: {str(e)[:80]}...")
        
        # Fallback: Use SearXNG via curl if available
        try:
            import subprocess
            result = subprocess.run(
                ['curl', '-s', 'http://localhost:8084/search?q=test&format=json'],
                capture_output=True, text=True, timeout=10
            )
            
            if result.return_code == 0 and len(result.stdout.strip()) > 10:
                self.web_search_available = True
                print("✅ Web search available via SearXNG localhost:8084")
                return True
                
        except Exception as e:
            pass
        
        self.web_search_available = False
        print("⚠️  No web search available - will run database-only analysis")
        return False
    
    def search_web_simple(self, query_string, max_results=3):
        """Simple web search using curl to SearXNG"""
        
        if not self.web_search_available:
            return []
        
        try:
            import subprocess
            
            encoded_query = urlquote(query_string)
            
            # Try multiple endpoints
            urls_to_try = [
                f'http://localhost:8084/search?q={encoded_query}&format=json',
                f'https://searx.be/search?q={query_string}&categories=general&safesearch=0&format=json'
            ]
            
            for url in urls_to_try:
                try:
                    result = subprocess.run(
                        ['curl', '-s', '--max-time', '30', url],
                        capture_output=True, text=True, timeout=30
                    )
                    
                    if result.return_code == 0 and len(result.stdout.strip()) > 50:
                        # Parse JSON if valid
                        try:
                            data = json.loads(result.stdout)
                            
                            results = []
                            if isinstance(data, dict):
                                # SearXNG format
                                for item in data.get('results', [])[:max_results]:
                                    results.append({
                                        'title': item.get('title', ''),
                                        'url': item.get('url', ''),
                                        'content': item.get('content', '') or item.get('description', '')
                                    })
                            
                            if len(results) > 0:
                                print(f"✅ Found {len(results)} results for: {query_string[:60]}...")
                                return results
                                
                        except json.JSONDecodeError:
                            continue
                
                except subprocess.TimeoutExpired:
                    continue
            
            return []
            
        except Exception as e:
            print(f"⚠️  Search failed: {str(e)[:50]}")
            return []
    
    def analyze_database_only(self, query_info, domain):
        """Analyze patterns using existing database (fallback when web unavailable)"""
        
        try:
            with open(self.db_path) as f:
                db = json.load(f)
            
            # Extract keywords from query
            topic = query_info.get('topic', 'Analysis')
            domain_str = domain.lower() if isinstance(domain, str) else domain
            
            # Find matching core symbols in database
            matched_symbols = []
            relationships_added = []
            
            for symbol_data in db.get('symbols', []):
                symbol_id = symbol_data.get('symbol_id')
                if symbol_id:
                    # Check if this symbol relates to our query domain
                    existing_domains = symbol_data.get('domains', [])
                    
                    if domain_str in str(existing_domains).lower():
                        matched_symbols.append(symbol_id)
                    
                    # Add new relationships based on query topic
                    keywords = [k.lower() for k in db.get('keywords', '').split()]
                    if any(kw in topic.lower() for kw in ['military', 'coup', 'soviet']):
                        existing_rels = symbol_data.get('relationships', [])
                        new_rel = {
                            'type': 'domain_inference',
                            'weight': 8.0,
                            'confidence': 0.85,
                            'description': f"Query: {topic} in {domain_str} domain",
                            'source': 'Hellboy Image Analysis'
                        }
                        if new_rel not in existing_rels:
                            symbol_data['relationships'].append(new_rel)
                            relationships_added.append({
                                'symbol': str(symbol_id),
                                'relationship': new_rel
                            })
            
            return {
                'type': 'database_analysis',
                'matched_symbols': matched_symbols,
                'relationships_added': len(relationships_added),
                'query_topic': topic,
                'domain': domain_str
            }
            
        except Exception as e:
            print(f"⚠️  Database analysis failed: {str(e)[:50]}")
            return {'matched_symbols': [], 'relationships_added': 0}
    
    def execute_queries(self):
        """Execute all research queries"""
        
        print("=" * 70)
        print("🔄 OVERNIGHT RESEARCH RUNNER v2.0 - MANUAL PROTOCOL")
        print("=" * 70)
        
        # Step 1: Check web search availability
        self.test_web_search()
        
        # Step 2: Load queries
        analysis_file = self.load_queries_from_analysis()
        
        if not analysis_file:
            print("⚠️  No queries loaded - will generate from Hellboy image data")
            # Generate default queries from our known patterns
            default_queries = [
                {
                    'image': 'MILITARY_COUP_1989',
                    'topic': 'Military Coup 1989',
                    'search_query': 'military coup 1989 soviet numerology gematria hellboy connection',
                    'domain': 'military_biblical',
                    'priority': 'HIGH'
                },
                {
                    'image': 'CONSTITUTION_6696',
                    'topic': 'Constitution Law',
                    'search_query': 'constitution law divine order gematria biblical 6696 analysis',
                    'domain': 'biblical_law_constitution',
                    'priority': 'HIGH'
                },
                {
                    'image': 'RASPUTIN_1869',
                    'topic': 'Rasputin Mystic',
                    'search_query': 'rasputin russian mystic biblical prophetic connections gematria',
                    'domain': 'ancient_mystic_biblical',
                    'priority': 'HIGH'
                },
                {
                    'image': 'HELLBOY_CORE_SYMBOLS',
                    'topic': 'Hellboy Core Symbols',
                    'search_query': '124 963 55 111 279 666 gematria meaning hellboy connection',
                    'domain': 'general_gematria',
                    'priority': 'MEDIUM'
                }
            ]
            analysis_file = {
                'queries_generated': len(default_queries),
                'research_queries': default_queries,
                'symbol_frequency': {'124': 5, '963': 1, '55': 2, '666': 1},
                'key_findings_summary': {}
            }
        
        queries = analysis_file.get('research_queries', [])
        
        print(f"\n✅ Loaded {len(queries)} research queries")
        
        # Step 3: Execute queries with rate limiting
        results = []
        symbols_modified_count = 0
        
        for i, query in enumerate(queries, 1):
            topic = query.get('topic', f'Query-{i}')
            domain = query.get('domain', 'general')
            
            print(f"\n{'─' * 50}")
            print(f"{i}. Processing: {topic}")
            print(f"   Domain: {domain}")
            if query.get('priority'):
                print(f"   Priority: {query['priority']}")
            
            # Execute web search if available
            if self.web_search_available and i <= 3:  # Limit web searches to avoid rate limits
            
                results_web = self.search_web_simple(query.get('search_query', ''))
                
                if results_web:
                    results.append({
                        'type': 'web_search',
                        'topic': topic,
                        'domain': domain,
                        'results': len(results_web),
                        'samples': [r.get('title', '')[:50] for r in results_web[:2]]
                    })
                else:
                    # Fall back to database analysis
                    db_result = self.analyze_database_only(query, domain)
                    results.append({
                        'type': 'database_fallback',
                        'topic': topic,
                        'domain': domain,
                        'symbols_matched': len(db_result.get('matched_symbols', [])),
                        'relationships_added': db_result.get('relationships_added', 0)
                    })
                    symbols_modified_count += db_result.get('relationships_added', 0)
                    
            else:
                # Database analysis (fallback)
                db_result = self.analyze_database_only(query, domain)
                results.append({
                    'type': 'database_analysis',
                    'topic': topic,
                    'domain': domain,
                    'symbols_matched': len(db_result.get('matched_symbols', [])),
                    'relationships_added': db_result.get('relationships_added', 0)
                })
                symbols_modified_count += db_result.get('relationships_added', 0)
            
            # Rate limiting (1 second between queries)
            time.sleep(1 if not self.web_search_available else 3)
        
        # Step 4: Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        output_file = self.research_logs_dir / f'overnight_research_{timestamp}.json'
        
        result_data = {
            'analysis_timestamp': datetime.now().isoformat(),
            'queries_executed': len(queries),
            'web_search_available': self.web_search_available,
            'results': results,
            'total_relationships_modified': symbols_modified_count
        }
        
        with open(output_file, 'w') as f:
            json.dump(result_data, f, indent=2)
        
        print(f"\n📄 Results saved to: {output_file}")
        
        # Step 5: Update database if relationships modified
        if symbols_modified_count > 0:
            with open(self.db_path) as f:
                db = json.load(f)
            
            for result in results:
                if 'symbols_matched' in result or 'type' in result:
                    # Add to relationships if there were matches
                    topic = result.get('topic', '')
                    if len(topic) > 0:
                        new_rel = {
                            'source': '124',
                            'target': topic.split()[0].lower() + '_analysis',
                            'relevance_score': round(0.6 + (symbols_modified_count / 50), 2),
                            'timestamp': datetime.now().isoformat(),
                            'source_query': query.get('topic', '')
                        }
                        
                        # Avoid duplicates
                        existing = [r for r in db['relationships'] 
                                   if new_rel['target'] in str(r.get('target', ''))]
                        
                        if len(existing) < 2:  # Max 2 relationships per topic
                            db['relationships'].append(new_rel)
            
            with open(self.db_path, 'w') as f:
                json.dump(db, f, indent=2)
            
            print(f"✅ Updated gematria_database.json with {symbols_modified_count} new relationships")
        
        # Step 6: Generate report
        self.generate_report(queries, results, symbols_modified_count)
        
        return result_data
    
    def generate_report(self, queries, results, relationships_added):
        """Generate markdown report of research findings"""
        
        report_dir = Path.home() / '.hermes' / 'gematria' / 'reports'
        report_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        report_file = report_dir / f'overnight_research_report_{timestamp}.md'
        
        with open(report_file, 'w') as f:
            f.write("# Overnight Research Report\n")
            f.write(f"**Generated:** {datetime.now().isoformat()}\n\n")
            
            f.write("## Summary\n")
            f.write(f"- **Queries Executed**: {len(queries)}\n")
            f.write(f"- **Relationships Modified**: {relationships_added}\n")
            f.write(f"- **Web Search Available**: {'Yes' if self.web_search_available else 'No (database-only mode)'}\n\n")
            
            f.write("## Queries Processed\n\n")
            
            for i, query in enumerate(queries, 1):
                topic = query.get('topic', '')
                domain = query.get('domain', 'general')
                priority = query.get('priority', 'MEDIUM')
                f.write(f"### {i}. {topic}\n")
                f.write(f"- **Domain**: {domain}\n")
                if priority:
                    f.write(f"- **Priority**: {priority}\n")
                f.write("\n")
            
            f.write("## Results\n\n")
            
            web_results = [r for r in results if 'web' in r.get('type', '')]
            db_results = [r for r in results if 'database' in r.get('type', '')]
            
            f.write(f"**Web Search Results**: {len(web_results)}\n\n")
            for result in web_results:
                f.write(f"- **{result.get('topic')}**: {result.get('results', 0)} results found\n")
                f.write("\n")
            
            f.write(f"**Database Analysis Results**: {len(db_results)}\n\n")
            for result in db_results:
                symbols = result.get('symbols_matched', [])
                rels = result.get('relationships_added', 0)
                if symbols:
                    f.write(f"- **{result.get('topic')}**: Matched {symbols} symbols, added {rels} relationships\n")
                else:
                    f.write(f"- **{result.get('topic')}**: Database fallback analysis completed\n")
                f.write("\n")
        
        print(f"\n📄 Report saved to: {report_file}")
        
        return report_file


def main():
    """Main entry point"""
    runner = OvernightResearchRunner()
    result = runner.execute_queries()
    
    print("\n" + "=" * 70)
    print("✅ OVERNIGHT RESEARCH COMPLETED")
    print("=" * 70)
    print(f"\nQueries executed: {result.get('queries_executed', 0)}")
    print(f"Web search available: {result.get('web_search_available', False)}")
    print(f"Relationships modified: Look for updated database entries")
    print(f"Report generated in: /home/avalonas/.hermes/gematria/reports/")


if __name__ == '__main__':
    main()
