#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Overnight Research Protocol v2.0 (Database Analysis Mode)
Uses existing gematria_database.json for analysis
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class OvernightResearcher:
    """Overnight research protocol with database analysis mode"""
    
    def __init__(self):
        self.core_symbols = [124, 963, 55, 111, 279, 666]
        self.domains = ['military', 'geography', 'elemental', 'biblical', 'ancient']
        self.research_dir = Path.home() / ".hermes" / "gematria" / "research_logs"
        self.research_dir.mkdir(parents=True, exist_ok=True)
        
        # Load the ACTUAL gematria database
        self.db_path = Path.home() / ".hermes" / "gematria" / "gematria_database.json"
        
        if not self.db_path.exists():
            print(f"✗ Database not found at {self.db_path}")
            sys.exit(1)
        
        try:
            with open(self.db_path, 'r') as f:
                self.data = json.load(f)
            print("✓ Loaded gematria knowledge graph database")
        except Exception as e:
            print(f"✗ Could not load database: {type(e).__name__}: {str(e)[:100]}")
            sys.exit(1)
        
        # Handle nested dictionary structure for analyzed_items
        if 'analyzed_items' in self.data and isinstance(self.data['analyzed_items'], dict):
            # Convert to list, sorting by numeric key
            items = []
            for key in sorted(self.data['analyzed_items'].keys(), key=lambda x: int(x) if x.isdigit() else 0):
                items.append(self.data['analyzed_items'][key])
            self.analyzed_items = items
        
        # If analyzed_items is already a list, use it
        elif 'analyzed_items' in self.data and isinstance(self.data['analyzed_items'], list):
            self.analyzed_items = self.data['analyzed_items']
        
        else:
            print("  No analyzed_items found, initializing empty list")
            self.analyzed_items = []
        
        print(f"✓ Found {len(self.analyzed_items)} analyzed items")
    
    def analyze_symbol_connections(self) -> List[Dict]:
        """Analyze connections between core symbols in the knowledge graph"""
        
        print("\n🔗 Analyzing symbol relationship network...")
        print("=" * 60)
        
        connections = []
        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
        
        # Get all analyzed items text for cross-reference
        all_items_text = []
        for item in self.analyzed_items:
            # Handle both dict and string-keyed nested structures
            if isinstance(item, str):
                continue
            
            title = item.get('title', '') or item.get('symbol_name', '') or ''
            content = item.get('content', '') or item.get('text', '') or item.get('pattern_text', '')
            
            # Extract symbol from item
            symbol_id = item.get('symbol_id') or item.get('symbol', 0)
            
            full_text = f"{title} {content}".lower()
            if full_text:
                all_items_text.append((str(symbol_id), full_text))
        
        print(f"  Scanning {len(all_items_text)} items for symbol mentions")
        
        # Find which symbols appear in which items
        symbol_item_mapping = {s: set() for s in self.core_symbols}
        
        for symbol_str, item_text in all_items_text:
            symbol_num = int(symbol_str) if symbol_str.isdigit() else 0
            
            for target_symbol in self.core_symbols:
                target_str = str(target_symbol)
                if target_str.lower() in item_text and symbol_num != target_symbol:
                    symbol_item_mapping[target_symbol].add(symbol_str)
        
        # Build connection list from co-occurrence
        processed_pairs = set()
        for s1, items in symbol_item_mapping.items():
            for s2 in sorted(items):  # Use symbols as they appear in text
                try:
                    s2_num = int(s2) if s2.isdigit() else 0
                except:
                    continue
                
                pair = tuple(sorted([s1, str(s2_num)]))
                if pair not in processed_pairs:
                    processed_pairs.add(pair)
                    
                    connection = {
                        'timestamp': now,
                        'source_type': 'symbol_co_occurrence',
                        'symbol_a': s1,
                        'symbol_b': str(s2_num),
                        'co_occurrences': len([t for t in items]),
                        'weight': round(min(len(items) * 0.5 + 1.0, 10.0), 2),
                        'confidence': round(min(0.95, 0.3 + len(items) * 0.1), 2)
                    }
                    connections.append(connection)
        
        # Add domain-based connections from context knowledge
        domain_connections = {
            'military_biblical': {
                'symbols': ['124', '963'],
                'domain_overlap': True,
                'context_note': 'Military history documents often contain biblical references'
            },
            'geography_elemental': {
                'symbols': ['55', '279'],
                'domain_overlap': True,
                'context_note': 'Geographic locations frequently associated with elemental forces'
            },
            'ancient_hero_journey': {
                'symbols': ['111', '666'],
                'domain_overlap': True,
                'context_note': 'Ancient traditions parallel hero narrative structures'
            }
        }
        
        for domain_key, conn_data in domain_connections.items():
            connection = {
                'timestamp': now,
                'source_type': 'domain_inference',
                'symbol_a': '/'.join(conn_data['symbols']),
                'symbol_b': domain_key,
                'co_occurrences': len(conn_data['symbols']),
                'weight': 8.0,
                'confidence': 0.85,
                'context_note': conn_data.get('context_note', '')
            }
            connections.append(connection)
        
        print(f"✓ Found {len(connections)} significant symbol connections")
        return connections
    
    def find_domain_patterns(self) -> List[Dict]:
        """Find patterns within each domain"""
        
        print("\n📊 Analyzing domain-specific patterns...")
        print("=" * 60)
        
        patterns = []
        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
        
        for domain in self.domains:
            # Count items related to this domain
            domain_items = []
            
            for item in self.analyzed_items:
                if isinstance(item, str):
                    continue
                
                title = (item.get('title', '') + ' ' + 
                         item.get('content', '') + ' ').lower()
                
                # Also check symbol domains array
                domains = item.get('domains', []) or []
                
                if domain.lower() in title:
                    domain_items.append(item)
                elif domain.lower() in [d.lower() for d in domains]:
                    domain_items.append(item)
            
            if domain_items:
                pattern = {
                    'timestamp': now,
                    'domain': domain,
                    'items_found': len(domain_items),
                    'pattern_type': 'domain_analysis',
                    'sample_item': domain_items[0].get('title', '')[:100] if domain_items else '',
                    'sample_content': (domain_items[0].get('content', '') or 
                                     domain_items[0].get('text', ''))[:200] if domain_items else ''
                }
                patterns.append(pattern)
                print(f"  ✓ {domain}: {len(domain_items)} items")
            else:
                pattern = {
                    'timestamp': now,
                    'domain': domain,
                    'items_found': 0,
                    'pattern_type': 'domain_analysis',
                    'sample_item': None,
                    'note': f'No new items from {domain} domain this cycle'
                }
                patterns.append(pattern)
        
        return patterns
    
    def identify_emerging_patterns(self) -> List[Dict]:
        """Identify emerging patterns in the knowledge graph"""
        
        print("\n🎯 Identifying emerging patterns...")
        print("=" * 60)
        
        emerging = []
        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
        
        # Pattern 1: Symbol frequency analysis
        symbol_mentions = {s: 0 for s in self.core_symbols}
        
        for item in self.analyzed_items:
            if isinstance(item, str):
                continue
            
            text = (item.get('title', '') + ' ' + 
                    item.get('content', '') + ' ' +
                    item.get('text', '')).lower()
            
            for symbol in self.core_symbols:
                count = text.count(str(symbol).lower())
                if count > 0:
                    symbol_mentions[symbol] += count
        
        # High-mention symbols (threshold: 2+ mentions)
        high_mention_symbols = [s for s, count in symbol_mentions.items() 
                                if count >= 2]
        
        if high_mention_symbols:
            emerging.append({
                'timestamp': now,
                'pattern_type': 'high_frequency_symbols',
                'description': f"Symbols {', '.join(high_mention_symbols)} show elevated mention frequency",
                'symbols': high_mention_symbols,
                'total_mentions': sum(symbol_mentions.values()),
                'confidence': 0.75
            })
        
        # Pattern 2: Domain convergence
        domain_counts = {domain: 0 for domain in self.domains}
        
        for item in self.analyzed_items:
            if isinstance(item, str):
                continue
            
            title = (item.get('title', '') + ' ' + 
                     item.get('content', '') + ' ').lower()
            
            for domain in self.domains:
                if domain.lower() in title:
                    domain_counts[domain] += 1
        
        # Domains with multiple items
        multi_domain_items = {d: c for d, c in domain_counts.items() if c >= 2}
        
        if multi_domain_items:
            emerging.append({
                'timestamp': now,
                'pattern_type': 'domain_convergence',
                'description': f"Domains {', '.join(multi_domain_items.keys())} show convergence patterns",
                'domains': list(multi_domain_items.keys()),
                'total_items': sum(multi_domain_items.values()),
                'confidence': 0.70
            })
        
        # Pattern 3: Recent activity detection
        recent_count = 0
        
        for item in self.analyzed_items:
            if isinstance(item, str):
                continue
            
            timestamp = item.get('timestamp_utc', '') or item.get('timestamp', '')
            if timestamp and '-' not in timestamp:
                recent_count += 1
        
        emerging.append({
            'timestamp': now,
            'pattern_type': 'recent_activity',
            'description': f"Analysis cycle tracking {len(self.analyzed_items)} total items",
            'item_count': len(self.analyzed_items),
            'confidence': 0.65
        })
        
        # Pattern 4: Cross-reference density
        connection_density = len(self.data.get('connections', [])) / max(len([i for i in self.analyzed_items if isinstance(i, dict)]), 1) * 100
        
        emerging.append({
            'timestamp': now,
            'pattern_type': 'cross_reference_density',
            'description': f"Current cross-reference coverage: {connection_density:.1f}% of items linked",
            'density_percentage': round(connection_density, 2),
            'confidence': 0.60
        })
        
        return emerging
    
    def analyze_relationship_evolution(self) -> Dict:
        """Analyze how relationships evolve over time"""
        
        print("\n📈 Analyzing relationship evolution...")
        print("=" * 60)
        
        # Filter only dict items for analysis
        dict_items = [i for i in self.analyzed_items if isinstance(i, dict)]
        
        evolution = {
            'timestamp': datetime.utcnow().isoformat(),
            'metrics': {}
        }
        
        # Count items by source type
        sources = {}
        for item in dict_items:
            source = item.get('source', 'database')
            sources[source] = sources.get(source, 0) + 1
        
        evolution['metrics']['items_per_source'] = dict(sorted(sources.items(), key=lambda x: x[1], reverse=True)[:5])
        
        # Count connections by type
        connection_types = {}
        for conn in self.data.get('connections', []):
            conn_type = conn.get('source_type', 'unknown')
            connection_types[conn_type] = connection_types.get(conn_type, 0) + 1
        
        evolution['metrics']['connection_types'] = dict(sorted(connection_types.items(), key=lambda x: x[1], reverse=True))
        
        # Average item length (quality indicator)
        lengths = []
        for item in dict_items:
            content = item.get('content', '') or item.get('text', '') or ''
            lengths.append(len(content))
        
        evolution['metrics']['average_item_length'] = round(sum(lengths) / len(lengths), 2) if lengths else 0
        
        # Symbol definition coverage
        symbol_coverage = [str(s) for s in self.core_symbols]
        defined_symbols = list(self.data.get('core_symbols', {}).keys()) if isinstance(self.data.get('core_symbols'), dict) else []
        
        evolution['metrics']['symbol_coverage'] = f"{len(set(defined_symbols))}/{len(symbol_coverage)} core symbols defined"
        
        print(f"  Items by source: {evolution['metrics']['items_per_source']}")
        print(f"  Connections by type: {evolution['metrics']['connection_types']}")
        print(f"  Avg item length: ~{evolution['metrics']['average_item_length'] if evolution['metrics']['average_item_length'] > 0 else 'N/A'} chars")
        print(f"  Symbol coverage: {evolution['metrics']['symbol_coverage']}")
        
        return evolution
    
    def generate_summary_report(self, 
                                connections: List[Dict], 
                                patterns: List[Dict],
                                emerging: List[Dict],
                                evolution: Dict) -> str:
        """Generate comprehensive summary report"""
        
        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
        
        report = f"""# Overnight Analysis Report - {now}

## Executive Summary
- **Analysis Mode**: Internal Knowledge Graph (gematria_database.json)
- **Core Symbols Tracked**: {', '.join(map(str, self.core_symbols))}
- **Symbols Defined**: {len(self.data.get('core_symbols', {})) if isinstance(self.data.get('core_symbols'), dict) else 0} core symbols
- **Items Analyzed**: {len([i for i in self.analyzed_items if isinstance(i, dict)])}
- **Relationship Connections**: {len(connections)}

## Connection Analysis Results
"""
        
        # Show top connections by weight
        sorted_connections = sorted(connections, 
                                     key=lambda x: x.get('weight', 0), 
                                     reverse=True)[:15]
        
        for i, conn in enumerate(sorted_connections, 1):
            report += f"""
### {i}. `{conn['symbol_a']}` ↔ `{conn.get('symbol_b', 'domain: ' + conn['source_type'])}`
- **Weight**: {conn.get('weight', 0)}/10.0
- **Confidence**: {conn.get('confidence', 0):.2f}
- **Type**: {conn.get('source_type', 'unknown')}
"""
        
        report += f"""
## Domain Pattern Analysis
"""
        
        for pattern in patterns:
            if pattern.get('items_found', 0) > 0 or 'note' not in pattern:
                sample = pattern.get('sample_item', '')[:80] + '...' if len(str(pattern.get('sample_item', ''))) > 80 else pattern.get('sample_item', '')
                report += f"✓ **{pattern['domain']}:** {len(pattern.get('items_found', 0))} items\n"
            else:
                report += f"⚠️ {pattern['domain']}: {pattern.get('note', 'no data')}\n"
        
        if not any(p for p in patterns):
            report += "No domain-specific patterns detected this cycle.\n"
        
        report += """
## Emerging Patterns Identified
"""
        
        for pattern in emerging:
            report += f"""
### {pattern['pattern_type'].replace('_', ' ').title()}
- **Description**: {pattern.get('description', 'N/A')}
- **Confidence**: {pattern.get('confidence', 0):.2f}
"""
        
        if not emerging:
            report += "No significant emerging patterns detected this cycle.\n"
        
        report += """
## Relationship Evolution Metrics
"""
        
        for metric, value in evolution['metrics'].items():
            if isinstance(value, float) and abs(int(value) - value) < 0.01:
                report += f"- **{metric.replace('_', ' ').title()}**: {int(value)}\n"
            else:
                report += f"- **{metric.replace('_', ' ').title()}**: {value}\n"
        
        report += """

---
*Generated by Overnight Research Protocol v2.0 (Internal Knowledge Graph Analysis)*

## Methodology
This analysis operates on the existing gematria knowledge graph database to:
- Track symbol co-occurrence patterns across domains
- Identify domain convergence and cross-reference density
- Detect emerging trends in symbolic relationships
- Monitor relationship evolution over time

The system continues to track core symbols: {', '.join(map(str, self.core_symbols))}

## Next Steps
- New web research results are automatically integrated via `auto_obisidian_sync_v2.py`
- Pattern analysis runs overnight at 3 AM (crontab scheduled)
- Results are exported to Obsidian for relationship tracking
"""
        
        return report
    
    def update_database(self, connections: List[Dict], patterns: List[Dict]):
        """Update database with new analysis results"""
        
        print(f"\n💾 Updating knowledge graph with {len(connections)} connections and {len(patterns)} patterns...")
        
        try:
            # Add connections to database if it has a connections list
            if 'connections' not in self.data or not isinstance(self.data['connections'], list):
                self.data['connections'] = []
            
            for conn in connections:
                self.data['connections'].append(conn)
            
            # Add domain analysis as analyzed_items (nested dict style)
            now = datetime.utcnow().strftime('%Y-%m-%d %H:%M')
            
            # Count existing items to get next key
            if 'analyzed_items' in self.data and isinstance(self.data['analyzed_items'], dict):
                existing_keys = [int(k) for k in self.data['analyzed_items'].keys() if k.isdigit()]
                next_key = max(existing_keys, default=-1) + 1
                
                for pattern in patterns:
                    if 'note' not in pattern or pattern.get('items_found', 0) > 0:
                        # Add to nested dict with numeric string key
                        self.data['analyzed_items'][str(next_key)] = {
                            'type': 'analysis_pattern',
                            **pattern,
                            'timestamp': now
                        }
                        next_key += 1
            
            # Save updated database
            db_path = Path.home() / ".hermes" / "gematria" / "gematria_database.json"
            with open(db_path, 'w') as f:
                json.dump(self.data, f, indent=2)
            
            print(f"✓ Updated gematria_database.json with analysis results")
            return True
            
        except Exception as e:
            print(f"✗ Database update failed: {type(e).__name__}: {str(e)[:100]}")
            import traceback
            traceback.print_exc()
            return False
    
    def run(self) -> Dict:
        """Execute overnight research protocol"""
        
        print("=" * 60)
        print("🌙 OVERNIGHT RESEARCH PROTOCOL (Internal Database Mode)")
        print("=" * 60)
        
        try:
            # Phase 1: Analyze symbol connections
            connections = self.analyze_symbol_connections()
            
            # Phase 2: Find domain patterns
            patterns = self.find_domain_patterns()
            
            # Phase 3: Identify emerging patterns
            emerging = self.identify_emerging_patterns()
            
            # Phase 4: Analyze relationship evolution
            evolution = self.analyze_relationship_evolution()
            
            # Phase 5: Generate and save report
            report = self.generate_summary_report(connections, patterns, emerging, evolution)
            report_path = self.research_dir / f"overnight_analysis_{datetime.utcnow().strftime('%Y%m%d_%H%M')}.md"
            Path(report_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(report_path, 'w') as f:
                f.write(report)
            
            print(f"\n✓ Report saved to: {report_path}")
            
            # Phase 6: Update database
            self.update_database(connections, patterns)
            
            return {
                'connections': connections,
                'patterns': patterns,
                'emerging': emerging,
                'evolution': evolution,
                'report_path': str(report_path),
                'success': True
            }
            
        except Exception as e:
            print(f"\n✗ Overnight analysis failed: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return {
                'connections': [],
                'patterns': [],
                'emerging': [],
                'error': str(e),
                'success': False
            }


def main():
    """Main entry point"""
    
    print("\n" + "=" * 60)
    print("🔄 OVERNIGHT RESEARCH PROTOCOL v2.0")
    print("=" * 60 + "\n")
    
    researcher = OvernightResearcher()
    result = researcher.run()
    
    if result['success']:
        print("\n" + "=" * 60)
        print("✅ OVERNIGHT ANALYSIS COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print(f"Connections: {len(result['connections'])}")
        print(f"Patterns: {len(result['patterns'])}")
        print(f"Emerging Patterns: {len(result['emerging'])}")
        print(f"Report: {result['report_path']}")
    else:
        print("\n" + "=" * 60)
        print("❌ OVERNIGHT ANALYSIS FAILED")
        print("=" * 60)
        if 'error' in result:
            print(f"Error: {result['error']}")
    
    return result


if __name__ == '__main__':
    result = main()
    sys.exit(0 if result['success'] else 1)
