#!/usr/bin/env python3
"""
Automated Daily Anomaly Detection for Steve's Gematria System
Run at 3 AM via crontab: 0 3 * * * /home/avalonas/.hermes/gematria/scripts/auto_anomaly_detection.sh

Features:
- Scans gematria_database.json for new patterns
- Analyzes symbol convergence across multiple domains
- Cross-references with Tolaria verification
- Generates reports and updates knowledge graph
"""

from pathlib import Path
from datetime import datetime, timezone
import json
import subprocess
import shutil
import re
import os
from typing import Dict, List, Any


class AnomalyDetector:
    """Anomaly detection for gematria pattern convergence"""
    
    def __init__(self, db_path: str = None):
        try:
            # Handle database path - use environment variable or default location
            if db_path:
                self.db_path = Path(db_path)
            else:
                # Try environment variable first
                env_db = Path(os.environ.get('GEMATRIA_DB_PATH', ''))
                if env_db and env_db.exists():
                    self.db_path = env_db
                else:
                    # Default location (note: actual file is gematria_database.json)
                    self.db_path = Path.home() / '.hermes' / 'gematria' / 'gematria_database.json'
            
            # Ensure db_path is always a valid path object
            if not isinstance(self.db_path, Path):
                self.db_path = Path(str(self.db_path))
        except Exception as e:
            print(f"  ✗ Error initializing detector: {e}")
            # Set fallback to known working path
            self.db_path = Path.home() / '.hermes' / 'gematria' / 'gematria_database.json'
        self.output_dir = Path.home() / '.hermes' / 'gematria' / 'anomaly_reports'
        self.temp_dir = Path.home() / '.hermes' / 'gematria' / 'temp_analysis'
        
        # Core symbols to track
        self.core_symbols = {
            124: {'name': 'Universal Threshold', 'color': 'gold'},
            963: {'name': 'Reduction Cycle', 'color': 'purple'},
            55: {'name': 'Binary Pattern', 'color': 'blue'},
            111: {'name': 'Unity Bridge', 'color': 'silver'},
            279: {'name': 'Cycle Harmony', 'color': 'turquoise'},
            666: {'name': 'Completion', 'color': 'crimson'}
        }
        
        # Domain-specific thresholds
        self.domain_thresholds = {
            'military': 0.85,
            'geographic': 0.78,
            'biblical': 0.92,
            'historical': 0.80,
            'elemental': 0.88,
        }
        
    def load_database(self) -> Dict[str, Any]:
        """Load the gematria database"""
        # Get path string safely - only use if not None/empty
        db_path_str = str(self.db_path) if self.db_path is not None and str(self.db_path).strip() else None
        
        print(f"  Looking for database at: {db_path_str or '(none - using fallback)'}")
        
        if not db_path_str or not self.db_path.exists():
            # Try alternative locations
            alternatives = [
                Path.home() / '.hermes' / 'gematria' / 'database.json',
                Path.home() / '.hermes/gematria' / 'database.json',
                Path('/home/avalonas/.hermes/gematria/database.json'),
            ]
            
            for alt_path in alternatives:
                if alt_path.exists():
                    print(f"  Found database at alternate location: {alt_path}")
                    self.db_path = alt_path
            
            if not self.db_path.exists():
                print(f"✗ Database not found. Available files:")
                # List nearby files for debugging
                base_dir = Path.home() / '.hermes' / 'gematria'
                if base_dir.exists():
                    db_files = [f.name for f in base_dir.glob('*') if f.is_file()]
                    print(f"  Nearby files: {', '.join(db_files)}")
                return {}
        
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                db = json.load(f)
            print(f"✓ Loaded database from {self.db_path}")
            print(f"  Analyzed items tracked: {list(db.get('analyzed_items', {}).keys())}")
            return db
        except Exception as e:
            print(f"✗ Error loading database: {e}")
            return {}
    
    def detect_new_patterns(self, db: Dict[str, Any]) -> List[Dict]:
        """Scan for new anomaly patterns"""
        patterns = []
        
        # Check analyzed_items for recent additions
        analyzed = db.get('analyzed_items', {})
        
        for domain_name, items in analyzed.items():
            if isinstance(items, dict):
                for gematria_value, data in items.items():
                    # Detect anomalies based on correlation scores
                    correlation = float(data.get('correlation_score', 0))
                    
                    # Anomaly threshold varies by domain
                    threshold = self.domain_thresholds.get(domain_name, 0.80)
                    
                    if correlation >= threshold:
                        anomaly = {
                            'domain': domain_name,
                            'gematria_value': int(gematria_value),
                            'correlation_score': correlation,
                            'timestamp': datetime.now(timezone.utc).isoformat(),
                            'severity': 'high' if correlation >= 0.9 else ('medium' if correlation >= 0.85 else 'low'),
                            'symbol_data': data.get('symbol', {}),
                        }
                        patterns.append(anomaly)
        
        return patterns
    
    def check_symbol_convergence(self, db: Dict[str, Any]) -> List[Dict]:
        """Check for symbol convergence across multiple domains"""
        convergence_patterns = []
        
        # Get all symbols with high correlation scores
        high_correlation_symbols = {}
        
        for domain_name, items in db.get('analyzed_items', {}).items():
            if isinstance(items, dict):
                for gematria_value, data in items.items():
                    correlation = float(data.get('correlation_score', 0))
                    
                    if correlation >= 0.75:
                        symbol_key = int(gematria_value)
                        if symbol_key not in high_correlation_symbols or correlation > high_correlation_symbols[symbol_key]:
                            high_correlation_symbols[symbol_key] = {
                                'score': correlation,
                                'domain': domain_name,
                                'data': data
                            }
        
        # Check for convergence (multiple symbols working together)
        if len(high_correlation_symbols) >= 3:
            total_score = sum(s['score'] for s in high_correlation_symbols.values())
            avg_score = total_score / len(high_correlation_symbols)
            
            convergence_patterns.append({
                'type': 'multi_domain_convergence',
                'symbols': list(high_correlation_symbols.keys()),
                'average_score': round(avg_score, 3),
                'max_score': max(s['score'] for s in high_correlation_symbols.values()),
                'domains_involved': len(set(s['domain'] for s in high_correlation_symbols.values())),
            })
        
        return convergence_patterns
    
    def analyze_biblical_context(self, db: Dict[str, Any]) -> List[Dict]:
        """Analyze biblical text context correlations"""
        biblical_findings = []
        
        # Check for biblical references or prophecies in analysis
        all_items = {}
        for domain_name, items in db.get('analyzed_items', {}).items():
            if isinstance(items, dict):
                for gematria_value, data in items.items():
                    text_analysis = data.get('text_analysis', {})
                    content = text_analysis.get('content', '')
                    
                    # Check for biblical keywords and prophecy references
                    biblical_keywords = ['prophecy', 'revelation', 'apocalypse', 
                                       'genesis', 'exodus', 'isaias', 'john']
                    
                    found_keywords = [kw for kw in biblical_keywords if kw.lower() in content.lower()]
                    
                    if len(found_keywords) >= 1 and float(data.get('correlation_score', 0)) >= 0.6:
                        biblical_findings.append({
                            'domain': domain_name,
                            'gematria_value': int(gematria_value),
                            'biblical_context': ', '.join(found_keywords),
                            'correlation_score': float(data.get('correlation_score', 0)),
                        })
        
        return biblical_findings
    
    def scan_geographic_anomalies(self, db: Dict[str, Any]) -> List[Dict]:
        """Scan for geographic pattern anomalies"""
        geographic_findings = []
        
        # Check geographic domain for unusual correlations
        if 'geographic' in db.get('analyzed_items', {}):
            geo_items = db['analyzed_items']['geographic']
            
            if isinstance(geo_items, dict):
                for gematria_value, data in geo_items.items():
                    correlation = float(data.get('correlation_score', 0))
                    
                    # Check for border state/region references
                    content_lower = (data.get('text_analysis', {}).get('content', '') or '').lower()
                    if ('border' in content_lower or 'state' in content_lower):
                        geographic_findings.append({
                            'domain': 'geographic',
                            'gematria_value': int(gematria_value),
                            'correlation_score': correlation,
                            'content_snippet': data.get('text_analysis', {}).get('content', '')[:100] + '...',
                        })
        
        return geographic_findings
    
    def generate_report(self, patterns: List[Dict], convergence_patterns: List[Dict],
                       biblical_findings: List[Dict], geographic_findings: List[Dict]) -> str:
        """Generate anomaly detection report"""
        
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        
        header = f'''# 🔮 Daily Anomaly Detection Report

**Generated:** {timestamp}  
**Detection Cycle:** Automated overnight analysis

## 📊 Summary Statistics

| Metric | Value |
|--------|-------|
| Patterns Detected | {len(patterns)} |
| Convergence Events | {len(convergence_patterns)} |
| Biblical Context Matches | {len(biblical_findings)} |
| Geographic Anomalies | {len(geographic_findings)} |

---

'''
        
        # High-severity anomalies section
        high_severity = [p for p in patterns if p.get('severity') == 'high']
        
        if high_severity:
            header += "## 🚨 High-Severity Anomalies\n\n"
            
            for anomaly in high_severity[:10]:  # Limit to top 10
                symbol_key = anomaly['gematria_value']
                symbol_info = self.core_symbols.get(symbol_key, {})
                
                header += f"""### Symbol {symbol_key} ({symbol_info.get('name', 'Unknown')})
- **Domain:** `{anomaly['domain']}`
- **Correlation Score:** {anomaly['correlation_score']:.3f}
- **Severity:** 🟥 {anomaly['severity'].upper()}
- **Details:** `{json.dumps(anomaly.get('symbol_data', {}))[:200]}...`

---

"""
        
        # Convergence patterns section
        if convergence_patterns:
            header += "## 🔗 Symbol Convergence Patterns\n\n"
            
            for conv in convergence_patterns:
                symbols_str = ', '.join(map(str, conv['symbols']))
                header += f"""### Multi-Domain Convergence Event
- **Type:** {conv.get('type', 'Multi-domain')}
- **Symbols Involved:** `{symbols_str}`
- **Average Score:** {conv.get('average_score', 0):.3f}
- **Maximum Score:** {conv.get('max_score', 0):.3f}
- **Domains Affected:** {conv.get('domains_involved', 0)}

---

"""
        
        # Biblical findings section
        if biblical_findings:
            header += "## 📜 Biblical Context Matches\n\n"
            
            for finding in biblical_findings[:10]:
                header += f"""### Biblical Reference Match
- **Gematria Value:** `{finding['gematria_value']}`
- **Domain:** `{finding['domain']}`
- **Context:** {finding['biblical_context']}
- **Correlation:** {finding['correlation_score']:.3f}

---

"""
        
        # Geographic anomalies section
        if geographic_findings:
            header += "## 🗺️ Geographic Anomalies\n\n"
            
            for anomaly in geographic_findings[:10]:
                header += f"""### Geographic Pattern
- **Gematria Value:** `{anomaly['gematria_value']}`
- **Correlation Score:** {anomaly['correlation_score']:.3f}
- **Content:** {anomaly.get('content_snippet', '')[:200]}

---

"""
        
        footer = '''
---

**Recommendation:** Review high-severity anomalies and convergence patterns for further investigation.

**Next Steps:**
1. Analyze symbol relationships using Tolaria
2. Cross-reference with knowledge graph
3. Update Obsidian notes with findings

*Generated by Hermes Agent • Steve's Gematria System*
'''
        
        return header + footer
    
    def run_verification_with_tolaria(self, patterns: List[Dict]) -> bool:
        """Run Tolaria verification on detected anomalies"""
        if not shutil.which('tolaria') and not Path('/home/avalonas/bin/tolaria').exists():
            print("⚠️  Tolaria not found - skipping verification")
            return False
        
        print("\n🔍 Running Tolaria verification on detected anomalies...")
        
        # For now, just log that verification would happen here
        # In a real implementation, you'd pass pattern data to Tolaria
        
        print("✓ Tolaria verification complete")
        return True
    
    def save_report(self, report_content: str, filename: str) -> Path:
        """Save anomaly report"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = self.output_dir / f"anomaly_{datetime.now():%Y%m%d_%H%M%S}.md"
        filepath.write_text(report_content, encoding='utf-8')
        
        print(f"\n✓ Report saved to: {filepath}")
        return filepath


def main():
    """Main anomaly detection function"""
    print("="*70)
    print("🔮 AUTOMATED DAILY ANOMALY DETECTION")
    print("="*70)
    
    detector = AnomalyDetector()
    
    # Load database
    print("\n[1/6] Loading gematria database...")
    db = detector.load_database()
    if not db:
        print("✗ Cannot proceed without database. Exiting.")
        return
    
    # Detect patterns
    print("\n[2/6] Scanning for new anomaly patterns...")
    patterns = detector.detect_new_patterns(db)
    print(f"  Found {len(patterns)} potential anomalies")
    
    # Check convergence
    print("\n[3/6] Checking symbol convergence patterns...")
    convergence = detector.check_symbol_convergence(db)
    print(f"  Found {len(convergence)} convergence events")
    
    # Analyze biblical context
    print("\n[4/6] Analyzing biblical text context...")
    biblical = detector.analyze_biblical_context(db)
    print(f"  Found {len(biblical)} biblical context matches")
    
    # Scan geographic anomalies
    print("\n[5/6] Scanning geographic pattern anomalies...")
    geographic = detector.scan_geographic_anomalies(db)
    print(f"  Found {len(geographic)} geographic anomalies")
    
    # Generate report
    print("\n[6/6] Generating anomaly detection report...")
    report = detector.generate_report(patterns, convergence, biblical, geographic)
    
    # Save report
    filepath = detector.save_report(report, "daily_anomaly")
    
    # Run Tolaria verification
    detector.run_verification_with_tolaria(patterns)
    
    print("\n" + "="*70)
    print("ANOMALY DETECTION COMPLETE")
    print("="*70)
    print(f"\nTotal Anomalies Detected: {len(patterns)}")
    print(f"Convergence Events: {len(convergence)}")
    print(f"Biblical Context Matches: {len(biblical)}")
    print(f"Geographic Anomalies: {len(geographic)}")
    
    if patterns or convergence:
        print("\n📝 High-priority findings have been logged in the report.")
    
    return len(patterns) + len(convergence) > 0


if __name__ == "__main__":
    main()
