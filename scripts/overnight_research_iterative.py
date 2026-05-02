#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Overnight Research Engine - Iterative Knowledge Graph Mode v3.0
===================

Purpose: Build knowledge graph progressively through iterative research cycles
         - Feeds existing database relationships INTO new queries
         - Uses web search results TO GENERATE additional queries
         - Produces detailed analysis with confidence scores and relationship tracking
         - Integrates gematria database continuously across all analyses

Architecture:
┌─────────────────────────────────────────────┐
│              INPUT                          │
│  • Hellboy Image Analysis Data (previous)   │
│  • Existing Database Relationships          │
│  • Core Symbols (124, 963, 55, 111, 279, 666)│
└─────────────────────────────────────────────┘
                ▼
┌─────────────────────────────────────────────┐
│           RESEARCH CYCLE                    │
│  • Generate Queries from Knowledge State    │
│  • Execute Web Search (Firecrawl/SearXNG)   │
│  • Extract Patterns & Relationships         │
│  • Feed Results Back into Query Generator   │
└─────────────────────────────────────────────┘
                ▼
┌─────────────────────────────────────────────┐
│          OUTPUT                             │
│  • Updated gematria_database.json           │
│  • Detailed Analysis Report                 │
│  • Relationship Matrix Update               │
│  • New Query Suggestions for Next Cycle     │
└─────────────────────────────────────────────┘

Key Features:
- Knowledge Accumulation: Each run builds on previous discoveries
- Self-Generating Queries: Results create new research directions
- Detailed Analysis: Confidence scores, relationship weights, pattern detection
- Domain Integration: Cross-references across military_biblical, geography_elemental, 
  ancient_hero_journey, elemental domains

Usage:
    cd ~/.hermes/gematria && python scripts/overnight_research_iterative.py

Cron Example (3 AM):
    0 3 * * * cd ~/.hermes/gematria && python scripts/overnight_research_iterative.py >> research_logs/cron_iterative_$(date +\%Y\%m\%d).log 2>&1
"""

import json
import re
import json
import re
import time  # Required for rate limiting between research cycles
from datetime import datetime
from pathlib import Path
from urllib.parse import quote as urlquote
import subprocess
    """
    Overnight Research Engine with iterative knowledge accumulation.
    
    Each research cycle:
    1. Reads existing database relationships and core symbols
    2. Generates queries based on accumulated knowledge
    3. Executes web searches (Firecrawl or SearXNG fallback)
    4. Extracts detailed patterns, relationships, confidence scores
    5. Feeds results back into query generation for next cycle
    
    This creates a self-improving research loop where each run 
    builds on previous discoveries and generates new research directions.
    """
    
    def __init__(self):
        # Database paths - using absolute path to avoid directory mismatch issues
        self.db_path = Path('/home/avalonas/.hermes/gematria/database/gematria_database.json')
        self.research_logs_dir = Path('/home/avalonas/.hermes/gematria/research_logs')
        self.reports_dir = Path('/home/avalonas/.hermes/gematria/reports')
        self.obsidian_exports_dir = Path('/home/avalonas/.hermes/gematria/obsidian_exports')
        
        # Core symbols and domains (from gematria_database.json structure)
        self.core_symbols = ['124', '963', '55', '111', '279', '666']
        self.domains = ['military_biblical', 'geography_elemental', 
                       'ancient_hero_journey', 'elemental', 'biblical_law_constitution',
                       'ancient_mystic_biblical', 'general_gematria']
        
        # Track relationships across cycles
        self.knowledge_accumulation = {
            'symbols_found': {},  # Track symbol frequency and context
            'relationships_tracked': [],  # All extracted relationships
            'domains_analyzed': set(),  # Domains we've covered
            'queries_run': []  # Query history for continuity
        }
        
    def load_existing_knowledge(self):
        """
        Load existing knowledge from database to use as seed for queries.
        This creates CONTINUITY across research cycles.
        """
        try:
            with open(self.db_path) as f:
                db = json.load(f)
            
            print("=" * 70)
            print("📚 LOADING EXISTING KNOWLEDGE FROM DATABASE")
            print("=" * 70)
            
            # Extract core symbols and their properties from database
            for key, symbol_data in db.get('symbols', {}).items():
                symbol_id = str(key)
                if symbol_id in self.core_symbols or symbol_id != '0':
                    context = symbol_data.get('context', '')
                    domains = symbol_data.get('domains', [])
                    keywords = symbol_data.get('keywords', '')
                    
                    # Track in knowledge accumulation
                    if symbol_id not in self.knowledge_accumulation['symbols_found']:
                        self.knowledge_accumulation['symbols_found'][symbol_id] = {
                            'context': context,
                            'domains': list(domains),
                            'keywords': keywords,
                            'occurrences': 0
                        }
                    
                    # Increment occurrence count
                    if symbol_id not in str(self.knowledge_accumulation['symbols_found'][symbol_id]['domains']):
                        self.knowledge_accumulation['symbols_found'][symbol_id]['occurrences'] += 1
            
            # Extract relationships from database
            for rel in db.get('relationships', []):
                rel_summary = f"{rel.get('source', '')} → {rel.get('target', '')}"
                if rel_summary not in self.knowledge_accumulation['relationships_tracked']:
                    self.knowledge_accumulation['relationships_tracked'].append(rel)
            
            # Track domains
            for domain in self.domains:
                self.knowledge_accumulation['domains_analyzed'].add(domain)
            
            print(f"✅ Loaded {len(self.knowledge_accumulation['symbols_found'])} core symbols")
            print(f"✅ Tracked {len(self.knowledge_accumulation['relationships_tracked'])} relationships")
            print(f"✅ Known domains: {', '.join(self.knowledge_accumulation['domains_analyzed'])}")
            
            return True
            
        except Exception as e:
            print(f"⚠️  Could not load database: {str(e)[:60]}...")
            # Create minimal database if it doesn't exist
            try:
                with open(self.db_path, 'w') as f:
                    json.dump({'symbols': {'1': {}, '0': {}}, 'relationships': []}, f)
                print("✅ Created new database file")
                return True
            except Exception as e2:
                print(f"⚠️  Could not create database: {str(e2)[:60]}...")
            return False
    
    def generate_queries_from_knowledge(self):
        """
        Generate research queries FROM EXISTING KNOWLEDGE.
        
        Instead of isolated queries, each new query builds on:
        - Previously found symbols and their contexts
        - Existing relationships that need further investigation
        - Domains we've partially explored (for deeper analysis)
        - Web search results from previous runs (via history)
        """
        
        print("\n" + "=" * 70)
        print("🔬 GENERATING QUERIES FROM KNOWLEDGE STATE")
        print("=" * 70)
        
        queries = []
        query_counter = 0
        
        # Strategy 1: Deepen analysis of high-occurrence symbols
        for symbol_id, data in self.knowledge_accumulation['symbols_found'].items():
            if data.get('occurrences', 0) >= 2:
                contexts = [c.strip().strip('"\'') for c in data.get('context', '').split('|') if c.strip()]
                primary_context = contexts[0] if contexts else f"gematria pattern {symbol_id}"
                
                query_counter += 1
                queries.append({
                    'id': query_counter,
                    'strategy': 'symbol_deepening',
                    'target_symbol': symbol_id,
                    'primary_context': primary_context,
                    # Generate search query that incorporates existing knowledge
                    'search_query': f'{symbol_id} {primary_context.lower()} gematria pattern cross-reference {data.get("domains", [0])}'[:60],
                    'domain': data.get('domains', ['general_gematria'])[0] if data.get('domains') else 'general_gematria',
                    'priority': 'HIGH' if data['occurrences'] >= 2 else 'MEDIUM',
                    'builds_on_relationships': len(self.knowledge_accumulation['relationships_tracked']) > 10,
                    'knowledge_source': f"Symbol {symbol_id} found in: {primary_context}"
                })
        
        # Strategy 2: Investigate relationships that need cross-domain verification
        if len(self.knowledge_accumulation['relationships_tracked']) > 5:
            for rel in self.knowledge_accumulation['relationships_tracked'][-3:]:  # Last 3 relationships
                query_counter += 1
                sources = rel.get('source', 'unknown')
                targets = rel.get('target', 'unknown')
                
                queries.append({
                    'id': query_counter,
                    'strategy': 'relationship_verification',
                    'source': sources,
                    'target': targets,
                    # Generate cross-domain search query
                    'search_query': f'{sources} → {targets} connection verification across domains gematria'[:60],
                    'domain': 'general_gematria',
                    'priority': 'MEDIUM',
                    'builds_on_relationships': True,
                    'knowledge_source': f"Relationship chain: {sources} to {targets}"
                })
        
        # Strategy 3: Expand into unexplored domains using known symbols
        explored_domains = self.knowledge_accumulation['domains_analyzed']
        for domain in self.domains:
            if domain not in explored_domains and len(self.knowledge_accumulation['symbols_found']) > 0:
                query_counter += 1
                # Use most frequent symbol as anchor for new domain exploration
                most_frequent_symbol = max(
                    self.knowledge_accumulation['symbols_found'].items(),
                    key=lambda x: x[1].get('occurrences', 0)
                )[0]
                
                queries.append({
                    'id': query_counter,
                    'strategy': 'domain_expansion',
                    'target_domain': domain,
                    'anchor_symbol': most_frequent_symbol,
                    # Generate domain-specific search query
                    'search_query': f'{most_frequent_symbol} in {domain.lower()} domain symbolic analysis'[:60],
                    'domain': domain,
                    'priority': 'MEDIUM',
                    'builds_on_relationships': False,
                    'knowledge_source': f"Exploring new domain: {domain}"
                })
        
        # Strategy 4: Cross-reference military-biblical connections (highest priority domain)
        if self.knowledge_accumulation['symbols_found']:
            query_counter += 1
            symbols_list = ', '.join([s[0] for s in list(self.knowledge_accumulation['symbols_found'].items())[:2]])
            
            queries.append({
                'id': query_counter,
                'strategy': 'domain_cross_reference',
                'source_domains': ['military_biblical'],
                'target_domains': [d for d in self.domains if d != 'military_biblical'][:2],
                # Generate cross-domain verification query
                'search_query': f'{symbols_list} military_biblical ↔ geography_elemental cross-reference analysis'[:60],
                'domain': 'military_biblical',
                'priority': 'HIGH',
                'builds_on_relationships': len(self.knowledge_accumulation['relationships_tracked']) > 3,
                'knowledge_source': "Cross-domain relationship verification between military and geography domains"
            })
        
        # Strategy 5: Analyze specific equation patterns detected in images
        detected_equations = [
            "49+39+21+97+36+37=360°",  # Military coup pattern
            "124 km³",  # Universal bridge occurrence
            "6696 contains 666"  # Completion number pattern
        ]
        
        for i, equation in enumerate(detected_equations, query_counter + 1):
            queries.append({
                'id': i,
                'strategy': 'equation_analysis',
                'pattern': equation,
                # Generate search query about detected patterns
                'search_query': f'{equation} gematria numerical pattern meaning historical context'[:60],
                'domain': 'general_gematria',
                'priority': 'HIGH' if i == 1 else 'MEDIUM',  # Military coup equation highest priority
                'builds_on_relationships': False,
                'knowledge_source': f"Detected pattern: {equation}"
            })
        
        # Strategy 6: Generate queries based on recent database relationships (feedback loop)
        if len(self.knowledge_accumulation['relationships_tracked']) > 15:
            query_counter += 1
            recent_relationships = self.knowledge_accumulation['relationships_tracked'][-5:]
            
            # Extract unique sources and targets for cross-reference query
            unique_sources = list(set([rel.get('source', '') for rel in recent_relationships]))[:3]
            unique_targets = list(set([rel.get('target', '') for rel in recent_relationships]))[:3]
            
            queries.append({
                'id': query_counter,
                'strategy': 'feedback_loop_generation',
                'sources': unique_sources,
                'targets': unique_targets,
                # Generate relationship graph exploration query
                'search_query': f'{unique_sources[0] if unique_sources else "unknown"} ↔ {unique_targets[0] if unique_targets else "unknown"} knowledge graph expansion'[:60],
                'domain': 'general_gematria',
                'priority': 'MEDIUM',
                'builds_on_relationships': len(self.knowledge_accumulation['relationships_tracked']) > 15,
                'knowledge_source': f"Feedback loop: generating query from recent relationship patterns (last {len(recent_relationships)} relationships)"
            })
        
        if not queries:
            # Fallback to core symbol analysis if knowledge base is too empty
            print("⚠️  Knowledge accumulation insufficient for strategy-based query generation")
            queries = self._generate_fallback_queries()
        
        print(f"✅ Generated {len(queries)} research queries from accumulated knowledge")
        print(f"   • Symbol deepening: {[q['strategy'] for q in queries if 'symbol' in q['strategy']]}"[:60])
        print(f"   • Relationship verification: {[q['strategy'] for q in queries if 'relationship' in q['strategy']]}"[:50] if any('relationship' in q['strategy'] for q in queries) else "")
        print(f"   • Domain expansion: {[q['strategy'] for q in queries if 'domain' in q['strategy']]}"[:50] if any('domain' in q['strategy'] for q in queries) else "")
        print(f"   • Equation analysis: {[q['strategy'] for q in queries if 'equation' in q['strategy']]}"[:50] if any('equation' in q['strategy'] for q in queries) else "")
        
        return queries
    
    def _generate_fallback_queries(self):
        """Generate fallback queries if knowledge base is too sparse."""
        print("⚠️  Generating fallback queries (will improve with accumulated knowledge)")
        
        return [
            {
                'id': 1,
                'strategy': 'core_symbol_analysis',
                'target_symbol': '124',
                'search_query': '124 universal bridge gematria meaning pattern cross-reference',
                'domain': 'general_gematria',
                'priority': 'HIGH',
                'builds_on_relationships': False,
                'knowledge_source': 'Core symbol analysis (fallback)'
            },
            {
                'id': 2,
                'strategy': 'core_symbol_analysis',
                'target_symbol': '963',
                'search_query': '963 gematria pattern meaning biblical military connections',
                'domain': 'biblical_law_constitution',
                'priority': 'MEDIUM',
                'builds_on_relationships': False,
                'knowledge_source': 'Core symbol analysis (fallback)'
            },
            {
                'id': 3,
                'strategy': 'military_biblical_focus',
                'search_query': '1989 Soviet military coup gematria numerology pattern Hellboy connection',
                'domain': 'military_biblical',
                'priority': 'HIGH',
                'builds_on_relationships': False,
                'knowledge_source': 'Military-biblical domain focus (fallback)'
            },
            {
                'id': 4,
                'strategy': 'biblical_law_focus',
                'search_query': 'constitute law divine order gematria pattern 6696 analysis',
                'domain': 'biblical_law_constitution',
                'priority': 'HIGH',
                'builds_on_relationships': False,
                'knowledge_source': 'Biblical law domain focus (fallback)'
            }
        ]
    
    def test_web_connectivity(self):
        """Test web search availability (Firecrawl primary, SearXNG fallback)."""
        print("\n🔍 Testing web connectivity...")
        
        # Check environment for Firecrawl API key
        try:
            env_file = Path.home() / '.hermes' / '.env'
            if env_file.exists():
                with open(env_file) as f:
                    for line in f:
                        if 'FIRECRAWL_API_KEY' in line.upper():
                            match = re.search(r'FIRECRAWL_API_KEY\s*[=:]?\s*"([^"]*)"', line, re.IGNORECASE)
                            if match:
                                api_key = match.group(1).strip()
                                break
                        else:
                            api_key = "test-key"
        except Exception as e:
            api_key = "test-key"
        
        # Test Firecrawl Cloud API
        try:
            import requests
            
            response = requests.get(
                "https://api.firecrawl.dev/v1/scrape",
                params={
                    'url': 'https://en.wikipedia.org/wiki/Numerology',
                    'formats': ['markdown']
                },
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                }
            )
            
            if response.status_code in [200, 206]:
                self.web_search_available = True
                print("✅ Web search available via Firecrawl Cloud API")
                return True
            
        except Exception as e:
            print(f"⚠️  Firecrawl test failed: {str(e)[:70]}...")
        
        # Fallback to SearXNG if available
        try:
            import subprocess
            
            result = subprocess.run(
                ['curl', '-s', 'http://localhost:8084/search?q=test&format=json'],
                capture_output=True, text=True, timeout=10
            )
            
            if result.return_code == 0 and len(result.stdout.strip()) > 20:
                self.web_search_available = True
                print("✅ Web search available via SearXNG localhost:8084")
                return True
                
        except Exception as e:
            pass
        
        self.web_search_available = False
        print("⚠️  No web search available - will use database-only + internal knowledge graph mode")
        return False
    
    def execute_queries_with_detailed_analysis(self, queries):
        """
        Execute queries with DETAILED ANALYSIS and relationship extraction.
        
        Each query execution:
        - Searches web (or uses database fallback)
        - Extracts specific patterns (symbols, relationships, equations)
        - Calculates confidence scores for each finding
        - Generates sub-queries from results (feedback loop)
        - Tracks knowledge accumulation
        """
        
        print("\n" + "=" * 70)
        print("🔬 EXECUTING QUERIES WITH DETAILED ANALYSIS")
        print("=" * 70)
        
        results = []
        symbols_modified_count = 0
        new_relationships_extracted = 0
        
        for query in queries:
            topic = query.get('search_query', f"Query-{query['id']}")[:60]
            domain = query.get('domain', 'general')
            priority = query.get('priority', 'MEDIUM')
            strategy = query.get('strategy', 'unknown')
            
            print(f"\n{'─' * 50}")
            print(f"Query #{query['id']}: {topic[:50]}...")
            print(f"   Domain: {domain} | Priority: {priority}")
            print(f"   Strategy: {strategy.replace('_', ' ').title()}")
            
            # Execute search (web or database fallback)
            if self.web_search_available and query['id'] <= len(queries):  # Limit web searches
                try:
                    import subprocess
                    
                    import sleep_module as sleep_module
                    
                    results_web = self.search_web_simple(query.get('search_query', ''))
                    
                    if results_web:
                        analysis_result = self._analyze_web_results(results_web, topic, domain)
                        
                        # Extract relationships and patterns from results
                        for result in results_web[:2]:  # Analyze first 2 results deeply
                            title = result.get('title', '')
                            content = result.get('content', '') or result.get('description', '')
                            
                            # Extract gematria patterns (numbers, equations)
                            extracted_patterns = self._extract_gematric_patterns(content)
                            
                            # Extract relationships from content
                            extracted_relationships = self._extract_relationships_from_text(content)
                            
                            analysis_result['web_source_titles'].append(title[:60])
                            analysis_result['extracted_patterns'].extend(extracted_patterns)
                            analysis_result['extracted_relationships'].extend(extracted_relationships)
                        
                        results.append(analysis_result)
                        print(f"✅ Web search returned {len(results_web)} results")
                        print(f"   • Extracted patterns: {len(analysis_result.get('extracted_patterns', []))}")
                        print(f"   • Extracted relationships: {len(analysis_result.get('extracted_relationships', []))}")
                        
                        # Update knowledge accumulation
                        for pattern in analysis_result.get('extracted_patterns', []):
                            symbol_id = pattern.get('symbol_id')
                            if symbol_id and symbol_id not in self.knowledge_accumulation['symbols_found']:
                                self.knowledge_accumulation['symbols_found'][symbol_id] = {
                                    'context': f"Web search: {topic}",
                                    'domains': [domain],
                                    'keywords': topic,
                                    'occurrences': 1
                                }
                            elif symbol_id:
                                if domain not in str(self.knowledge_accumulation['symbols_found'][symbol_id]['domains']):
                                    self.knowledge_accumulation['symbols_found'][symbol_id]['occurrences'] += 1
                        
                        new_relationships_extracted += len(analysis_result.get('extracted_relationships', []))
                        
                    else:
                        # Fallback to database analysis
                        db_result = self._database_only_analysis(topic, domain)
                        analysis_result = self._create_analysis_result_from_database(db_result, topic, domain)
                        results.append(analysis_result)
                        
                except Exception as e:
                    print(f"⚠️  Web search error: {str(e)[:50]}...")
                    # Fall back to database analysis
                    db_result = self._database_only_analysis(topic, domain)
                    analysis_result = self._create_analysis_result_from_database(db_result, topic, domain)
                    results.append(analysis_result)
            else:
                # Database-only mode
                db_result = self._database_only_analysis(topic, domain)
                analysis_result = self._create_analysis_result_from_database(db_result, topic, domain)
                results.append(analysis_result)
            
            rels = analysis_result.get('relationships_added', [])
            if isinstance(rels, int):
                symbols_modified_count += 0
            else:
                symbols_modified_count += len([r for r in rels if r])
            
            # Rate limiting
            sleep_module.sleep(2 if not self.web_search_available else 5)
        
        print(f"\n✅ Queries executed: {len(results)}")
        print(f"📊 Total symbols modified: {symbols_modified_count}")
        print(f"🔗 New relationships extracted: {new_relationships_extracted}")
        
        return results, symbols_modified_count, new_relationships_extracted
    
    def _analyze_web_results(self, results, topic, domain):
        """Analyze web search results with detailed pattern extraction."""
        
        analysis_result = {
            'type': 'web_search',
            'topic': topic[:60],
            'domain': domain,
            'web_source_titles': [],
            'web_source_urls': [],
            'content_extracted': False,
            'confidence_score': 0.85 if len(results) > 0 else 0.5,
            'extracted_patterns': [],
            'extracted_relationships': [],
            'keywords_found': [],
            'symbols_detected': [],
            'query_verification_status': 'complete'
        }
        
        for result in results:
            title = result.get('title', '')
            url = result.get('url', '')
            content = result.get('content', '') or result.get('description', '')
            
            analysis_result['web_source_titles'].append(title[:60])
            analysis_result['web_source_urls'].append(url[:60])
            
            # Extract gematria patterns (numbers, equations) from content
            extracted_patterns = self._extract_gematric_patterns(content)
            if extracted_patterns:
                analysis_result['extracted_patterns'].extend(extracted_patterns)
                for pattern in extracted_patterns:
                    symbol_id = pattern.get('symbol_id')
                    if symbol_id:
                        analysis_result['symbols_detected'].append(symbol_id)
            
            # Extract relationships from content
            extracted_rels = self._extract_relationships_from_text(content)
            if extracted_rels:
                analysis_result['extracted_relationships'].extend(extracted_rels)
        
        # Calculate keywords found
        all_content = ' '.join([r.get('content', '') or r.get('description', '') for r in results])
        keywords_found = self._extract_keywords_from_text(all_content)
        analysis_result['keywords_found'] = keywords_found
        
        # Determine overall confidence
        if len(results) >= 3:
            analysis_result['confidence_score'] = max(analysis_result['confidence_score'], 0.9)
        
        return analysis_result
    
    def _extract_gematric_patterns(self, text):
        """Extract gematria-related patterns from text (numbers, equations, symbolic references)."""
        
        patterns = []
        
        # Pattern 1: Look for number sequences that might be symbols (e.g., "124", "666")
        number_sequences = re.findall(r'\b(\d{1,3})(?:\s*\+\s*(\d{1,3}))?\b', text)
        for match in number_sequences:
            seq_num = int(match[0])
            # Check if this is a core symbol
            for sym in self.core_symbols:
                if str(seq_num) == sym or seq_num == int(sym):
                    patterns.append({
                        'pattern_type': 'symbol_reference',
                        'symbol_id': str(seq_num),
                        'context': match[1] if len(match) > 1 else 'standalone number',
                        'confidence': 0.85 if match[1] else 0.7,
                        'description': f"Core symbol {seq_num} detected in: '{match[0]}{match[1]}'"
                    })
        
        # Pattern 2: Look for equations (e.g., "49+39=88")
        equation_matches = re.findall(r'(\d+)\s*\+\s*(\d+)\s*=\s*(\d+)', text)
        for match in equation_matches:
            num1, num2, result = map(int, match)
            total = sum(map(int, match))
            patterns.append({
                'pattern_type': 'numerical_equation',
                'equation': f"{num1}+{num2}={total}",
                'components': [str(num1), str(num2)],
                'result': str(total),
                'confidence': 0.9,
                'description': f"Equation detected: {match[0]} + {match[1]} = {match[2]}"
            })
        
        # Pattern 3: Look for symbolic phrases (e.g., "universal bridge", "completion number")
        symbolic_phrases = [
            ('universal bridge', '124'),
            ('completion number', '666'),
            ('cycle turning', '963'),
            ('vessel', '17'),
            ('threshold', '124')
        ]
        
        for phrase, symbol_id in symbolic_phrases:
            if phrase.lower() in text.lower():
                patterns.append({
                    'pattern_type': 'symbolic_reference',
                    'symbol_id': symbol_id,
                    'phrase': phrase,
                    'confidence': 0.75,
                    'description': f"Symbolic reference to {symbol_id}: '{phrase}'"
                })
        
        return patterns
    
    def _extract_relationships_from_text(self, text):
        """Extract relationship patterns from text content."""
        
        relationships = []
        
        # Pattern 1: Look for directional language (e.g., "leads to", "connects to", "transforms into")
        directional_patterns = [
            (r'(\w+(?:\s+\w+)*?)\s*(leads|connects|transforms|evolves|reduces)\s*(into|to|as)\s*(\w+(?:\s+\w+)*)',
             'transformation'),
            (r'(\w+(?:\s+\w+)*?)\s*is\s*a\s*(variant|form|aspect|manifestation)\s*of\s*(\w+(?:\s+\w+)*)',
             'equivalence'),
            (r'(\w+(?:\s+\w+)*?)\s*appears\s*across\s*(all|multiple)\s*(domains|contexts)',
             'universal_pattern')
        ]
        
        for pattern, rel_type in directional_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches[:3]:  # Limit to 3 per pattern type
                relationships.append({
                    'source': match[0] if len(match) > 0 else '',
                    'target': match[-1] if len(match) > -1 else '',
                    'relationship_type': rel_type,
                    'confidence': 0.75,
                    'context': text[:200]
                })
        
        # Pattern 2: Look for domain references
        domain_matches = re.findall(r'(\w+(?:\s+\w+)*)\s*(?:domain|field|area)', text, re.IGNORECASE)
        if domain_matches:
            relationships.append({
                'source': '',
                'target': ', '.join(domain_matches[:3]),
                'relationship_type': 'domain_reference',
                'confidence': 0.6,
                'context': f"Text references domains: {', '.join(domain_matches[:3])}"
            })
        
        return relationships
    
    def _extract_keywords_from_text(self, text):
        """Extract meaningful keywords from text."""
        
        # Remove punctuation and get words
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter to meaningful terms (length 4+ and common gematria/biblical/military terms)
        keyword_terms = [
            'gematria', 'numerology', 'biblical', 'military', 'constitute', 'law', 
            'divine', 'order', 'symbol', 'pattern', 'universal', 'bridge', 'completion',
            'threshold', 'cycle', 'elemental', 'ancient', 'hero', 'journey'
        ]
        
        keywords_found = []
        for word in words:
            if len(word) >= 3 and word.lower() in keyword_terms:
                keywords_found.append(word)
        
        return keywords_found[:10]  # Limit to top 10
    
    def _database_only_analysis(self, topic, domain):
        """Perform database-only analysis using existing knowledge graph."""
        
        try:
            with open(self.db_path) as f:
                db = json.load(f)
            
            # Find symbols relevant to our query
            keywords = [k.lower() for k in topic.split()][:5]  # First few words
            
            matched_symbols = []
            relationships_to_add = []
            
            # Check each core symbol
            for key, symbol_data in db.get('symbols', {}).items():
                if key == '0':
                    continue
                
                existing_domains = symbol_data.get('domains', [])
                keywords_in_symbol = [k.lower() for k in symbol_data.get('keywords', '').split()]
                
                # Check domain match
                domain_match = any(d.lower() in str(existing_domains).lower() for d in keywords) or \
                               any(d.lower() in str(existing_domains).lower() for d in self.core_symbols)
                
                if not domain_match and len(existing_domains) > 0:
                    continue
                
                # Add relationship based on query topic
                if keywords_in_symbol and any(kw in ' '.join(keywords) for kw in keywords_in_symbol):
                    symbol_id = str(key)
                    if symbol_id not in matched_symbols:
                        matched_symbols.append(symbol_id)
                        
                        # Create new relationship
                        rel = {
                            'source': 'query_analyzer',
                            'target': topic.split()[0].lower() + '_analysis',
                            'relevance_score': round(0.6 + (len(matched_symbols) / 10), 2),
                            'timestamp': datesleep_module.now().isoformat(),
                            'source_query': topic[:50],
                            'confidence': 0.75,
                            'knowledge_accumulation_context': f"Query builds on previous symbol findings: {', '.join(matched_symbols)}"
                        }
                        
                        # Add to database if not exists
                        new_rel = {'source': rel['source'], 'target': rel['target']}
                        if new_rel not in relationships_to_add:
                            relationships_to_add.append(new_rel)
            
            return {
                'matched_symbols': matched_symbols,
                'relationships_added': len(relationships_to_add),
                'topic': topic[:60],
                'domain': domain
            }
            
        except Exception as e:
            print(f"⚠️  Database analysis error: {str(e)[:50]}...")
            return {'matched_symbols': [], 'relationships_added': 0}
    
    def _create_analysis_result_from_database(self, db_result, topic, domain):
        """Create structured analysis result from database-only mode."""
        
        return {
            'type': 'database_fallback',
            'topic': topic[:60],
            'domain': domain,
            'matched_symbols': db_result.get('matched_symbols', []),
            'relationships_added': db_result.get('relationships_added', 0),
            'confidence_score': 0.75,
            'query_verification_status': 'database_mode'
        }
    
    def update_database_with_findings(self, results, relationships_extracted):
        """Update gematria database with new findings and relationships."""
        
        try:
            with open(self.db_path) as f:
                db = json.load(f)
            
            # Track new symbols found in web results
            all_symbols_found = set()
            for result in results:
                for symbol_id in result.get('symbols_detected', []):
                    if symbol_id not in self.core_symbols:  # Only add non-core symbols as context
                        # Store in appropriate key (use first available)
                        first_key = next((k for k in db['symbols'] if k != '0'), '1')
                        if symbol_id not in [str(k) for k in db['symbols'].keys()]:
                            db['symbols'][str(symbol_id)] = {
                                'context': f"Found during overnight research on: {result.get('topic', '')}",
                                'domains': result.get('domain', 'general'),
                                'keywords': ', '.join(result.get('keywords_found', []))[:50],
                                'confidence_score': result.get('confidence_score', 0.0)
                            }
            
            # Add new relationships
            for rel in relationships_extracted:
                rel_key = f"{rel['source']}_{rel['target']}"
                
                existing_rels = [r for r in db['relationships'] 
                               if rel_key in str(r.get('source', '')) and 
                                  rel_key in str(r.get('target', ''))]
                
                if len(existing_rels) < 3:  # Max 3 relationships per source-target pair
                    db['relationships'].append({
                        'source': rel.get('source', ''),
                        'target': rel.get('target', ''),
                        'relevance_score': rel.get('relevance_score', 0.65),
                        'timestamp': datesleep_module.now().isoformat(),
                        'confidence': rel.get('confidence', 0.7),
                        'context': f"Extracted from: {results[0].get('topic', '')}" if results else ""
                    })
            
            # Update knowledge accumulation tracking
            self.knowledge_accumulation['relationships_tracked'].extend(relationships_extracted)
            
            # Save updated database
            with open(self.db_path, 'w') as f:
                json.dump(db, f, indent=2)
            
            print(f"\n✅ Database updated successfully")
            print(f"   • New symbols added: {len(set(s for r in results for s in r.get('symbols_detected', [])))}")
            print(f"   • New relationships added: {len(relationships_extracted)}")
            
            return True
            
        except Exception as e:
            print(f"⚠️  Database update error: {str(e)[:50]}...")
            return False
    
    def generate_detailed_report(self, results, queries_run):
        """Generate detailed markdown report with analysis findings."""
        
        timestamp = datesleep_module.now().strftime('%Y%m%d_%H%M')
        
        # Create directories if needed
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        report_path = self.reports_dir / f'overnight_research_report_{timestamp}.md'
        
        with open(report_path, 'w') as f:
            f.write("# Overnight Research Report (Iterative Knowledge Graph Mode)\n")
            f.write(f"**Generated**: {datesleep_module.now().isoformat()}\n\n")
            
            # Executive Summary
            f.write("## Executive Summary\n")
            f.write(f"- **Queries Executed**: {len(queries_run)}\n")
            f.write(f"- **Web Search Mode**: {'Yes' if self.web_search_available else 'No (database-only)'}\n")
            f.write(f"- **Relationships Extracted**: {sum(len(r.get('extracted_relationships', [])) for r in results)}\n")
            f.write(f"- **Symbols Detected**: {len(set(s for r in results for s in r.get('symbols_detected', [])))}\n\n")
            
            # Detailed Query Results
            f.write("## Detailed Query Analysis\n\n")
            
            web_results = [r for r in results if r.get('type') == 'web_search']
            db_results = [r for r in results if r.get('type') == 'database_fallback']
            
            f.write(f"### Web Search Results ({len(web_results)})\n\n")
            for i, result in enumerate(web_results[:5], 1):  # Top 5 web results
                f.write(f"#### {i}. {result.get('topic', '')[:60]}\n")
                f.write(f"- **Confidence Score**: {result.get('confidence_score', 0.0)}\n")
                
                if result.get('web_source_titles'):
                    f.write(f"- **Sources**: {len(result['web_source_titles'])} URLs\n")
                    for title in result['web_source_titles'][:3]:
                        f.write(f"    - {title}\n")
                
                # Extracted patterns
                patterns = result.get('extracted_patterns', [])
                if patterns:
                    f.write(f"- **Patterns Detected**: {len(patterns)}\n")
                    for pattern in patterns[:3]:  # Show first 3 patterns
                        p_type = pattern.get('pattern_type', 'unknown')
                        pattern_info = str(pattern)
                        if len(pattern_info) > 100:
                            pattern_info = pattern_info[:97] + "..."
                        f.write(f"    - [{p_type}] {pattern_info}\n")
                
                # Extracted relationships
                rels = result.get('extracted_relationships', [])
                if rels:
                    f.write(f"- **Relationships**: {len(rels)}\n")
                    for rel in rels[:2]:  # Show first 2 relationships
                        s = rel.get('source', 'N/A')
                        t = rel.get('target', 'N/A')
                        conf = rel.get('confidence', 0.0)
                        f.write(f"    - {s} → {t} (confidence: {conf})\n")
                
                f.write("\n")
            
            f.write(f"### Database-Only Results ({len(db_results)})\n\n")
            for i, result in enumerate(db_results[:3], 1):
                f.write(f"#### {i}. {result.get('topic', '')[:60]}\n")
                f.write(f"- **Matched Symbols**: {result.get('matched_symbols', [])}\n")
                f.write(f"- **Relationships Added**: {result.get('relationships_added', 0)}\n\n")
            
            # Knowledge Graph Evolution
            f.write("## Knowledge Graph Evolution\n\n")
            f.write("### Symbols Accumulated\n")
            for symbol_id, data in self.knowledge_accumulation['symbols_found'].items():
                contexts = [c.strip().strip('"\'') for c in data.get('context', '').split('|') if c.strip()]
                primary_context = contexts[0] if contexts else f"gematria pattern {symbol_id}"
                
                f.write(f"**{symbol_id}**: `{data.get('keywords', '')[:50]}`\n")
                f.write(f"  - Context: {primary_context}\n")
                f.write(f"  - Domains: {', '.join(data.get('domains', []))}\n\n")
            
            # Relationship Matrix Update
            f.write("### Updated Relationships\n")
            recent_rels = self.knowledge_accumulation['relationships_tracked'][-10:]
            for rel in recent_rels[:10]:
                source = rel.get('source', 'N/A')
                target = rel.get('target', 'N/A')
                conf = rel.get('confidence', 0.0)
                
                # Abbreviate long names
                short_source = source[:30] + "..." if len(source) > 30 else source
                short_target = target[:30] + "..." if len(target) > 30 else target
                
                f.write(f"- {short_source} → {short_target} (confidence: {conf})\n")
            
            f.write("\n---\n")
            f.write("*Report generated by IterativeResearchEngine v3.0*\n")
            f.write("*Knowledge accumulation enabled for progressive research*\n")
        
        print(f"\n📄 Report saved to: {report_path}")
        
        return report_path
    
    def save_query_history_for_continuity(self):
        """Save current query results for continuity in next research cycle."""
        
        timestamp = datesleep_module.now().strftime('%Y%m%d_%H%M')
        history_file = self.research_logs_dir / f'query_history_{timestamp}.json'
        
        with open(history_file, 'w') as f:
            json.dump({
                'knowledge_accumulation': self.knowledge_accumulation,
                'queries_run_count': len(self.knowledge_accumulation['queries_run']),
                'last_execution': datesleep_module.now().isoformat()
            }, f, indent=2)
        
        print(f"✅ Query history saved for continuity: {history_file}")


def main():
    """Main entry point."""
    print("=" * 70)
    print("🌙 OVERNIGHT RESEARCH ENGINE v3.0 - ITERATIVE KNOWLEDGE GRAPH MODE")
    print("=" * 70)
    
    # Initialize engine
    engine = IterativeResearchEngine()
    
    # Step 1: Load existing knowledge
    print("\n📂 STEP 1: Loading existing knowledge...")
    if not engine.load_existing_knowledge():
        print("⚠️  Could not load database - using minimal structure")
    
    # Step 2: Test web connectivity
    print("\n🔌 STEP 2: Testing web connectivity...")
    engine.test_web_connectivity()
    
    # Step 3: Generate queries from accumulated knowledge
    print("\n🧪 STEP 3: Generating queries from knowledge state...")
    queries = engine.generate_queries_from_knowledge()
    
    if not queries:
        print("⚠️  No queries generated - exiting gracefully")
        return
    
    # Step 4: Execute queries with detailed analysis
    print("\n🔬 STEP 4: Executing queries with detailed analysis...")
    results, symbols_modified_count, new_relationships_extracted = \
        engine.execute_queries_with_detailed_analysis(queries)
    
    # Step 5: Update database with findings
    print("\n💾 STEP 5: Updating database with findings...")
    all_relationships_extracted = []
    for result in results:
        all_relationships_extracted.extend(result.get('extracted_relationships', []))
    engine.update_database_with_findings(results, all_relationships_extracted)
    
    # Step 6: Generate detailed report
    print("\n📊 STEP 6: Generating detailed report...")
    engine.generate_detailed_report(results, queries)
    
    # Step 7: Save query history for continuity
    print("\n📜 STEP 7: Saving query history for next cycle...")
    engine.save_query_history_for_continuity()
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ OVERNIGHT RESEARCH COMPLETED SUCCESSFULLY")
    print("=" * 70)
    print(f"\nSummary:")
    print(f"  • Queries executed: {len(queries)}")
    print(f"  • Symbols modified: {symbols_modified_count}")
    print(f"  • Relationships extracted: {new_relationships_extracted}")
    print(f"  • Knowledge accumulated for next cycle")
    print(f"\nDatabase updated at: {engine.db_path}")
    print(f"Reports generated in: {engine.reports_dir}/")


if __name__ == '__main__':
    main()
