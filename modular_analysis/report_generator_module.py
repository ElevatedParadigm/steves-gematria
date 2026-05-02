#!/usr/bin/env python3
"""
Modular Analysis - Report Generator Module
Responsible for: Compiling all analysis outputs into comprehensive markdown reports.
Single responsibility: Generate final report from results of all other modules.
"""

from datetime import datetime
from typing import List, Dict


class ReportGeneratorModule:
    """
    Standalone report generator that compiles module outputs.
    
    Can be used independently (if you have separate analysis files):
        generator = ReportGeneratorModule()
        report_path = generator.generate_report(analysis_results_dict)
    """
    
    def __init__(self, base_path: str = "/home/avalonas/.hermes/gematria"):
        """Initialize with base path for report output"""
        self.base_path = base_path
        self.reports_dir = f"{base_path}/reports"
        
    def generate_report(self, results: Dict) -> str:
        """
        Generate comprehensive markdown report from all module outputs.
        
        Args:
            results: Dictionary containing outputs from all modules:
                - results: List of scraper results
                - analysis: PatternAnalysisResult from analyzer_module
                - new_rels: List[Dict] from graph_builder_module
                - temporal: TemporalPatternData from temporal_tracker_module
                - ascii_heatmap: ASCII string from heatmap_generator_module
            
        Returns:
            Path to generated report file
        """
        from pathlib import Path
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        report_filename = f"modular_overnight_report_{timestamp}.md"
        report_path = Path(f"{self.reports_dir}/{report_filename}")
        
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract module outputs from results dict
        scraper_results = results.get("results", [])
        analysis = results.get("analysis", {})
        new_relationships = results.get("new_rels", [])
        temporal = results.get("temporal", {})
        ascii_heatmap = results.get("ascii_heatmap", "")
        
        # Load existing relationships from database for relationship iteration log
        existing_rels_count = 0
        try:
            import json
            db_path = f"{self.base_path}/database/gematria_database.json"
            with open(db_path, 'r') as f:
                db = json.load(f)
            existing_rels = db.get("metadata", {}).get("relationships", [])
            existing_rels_count = len(existing_rels)
        except Exception:
            pass
        
        with open(report_path, 'w') as f:
            # Write report
            report_lines = self._build_report(
                timestamp, scraper_results, analysis, 
                new_relationships, temporal, ascii_heatmap, existing_rels_count
            )
            
            f.write("\n".join(report_lines))
        
        return str(report_path)
    
    def _build_report(self, timestamp: str, scraper_results: List[Dict],
                     analysis: Dict, new_rels: List[Dict], 
                     temporal: Dict, ascii_heatmap: str, 
                     existing_rels_count: int) -> List[str]:
        """Build report content as list of lines"""
        
        # Extract key metrics
        successful_queries = len([r for r in scraper_results if r.get("status") == "success"])
        failed_queries = len(scraper_results) - successful_queries
        
        lines = [
            f"# 📊 Overnight Research Report - {timestamp}",
            "",
            "## 🎯 Executive Summary",
            "",
            f"- **Symbols Processed**: 12 core symbols",
            f"- **Queries Executed**: {len(scraper_results)}",
            f"- **Successful Queries**: {successful_queries}",
            f"- **Failed Queries**: {failed_queries}",
            f"- **Cross-Domain Signals**: {len(analysis.get('convergence_signals', []))}",
            f"- **New Relationships**: {len(new_rels)}",
            "",
            "## 🔍 Query Results",
            ""
        ]
        
        # Per-query results summary
        for i, query_result in enumerate(scraper_results[:6], 1):
            status = "✅" if query_result.get("status") == "success" else "❌"
            query_text = query_result.get("query", f"[Query {i}]")[:60]
            
            lines.extend([
                f"- {status} `{query_text}`,",
                f"    Found: {len(query_result.get('results', []))} potential links",
            ])
        
        lines.extend([
            "",
            "## 🧪 Pattern Analysis Results",
            ""
        ])
        
        # Cross-domain convergence signals
        if analysis.get("convergence_signals"):
            lines.append("### 🔗 Convergence Signals Detected:")
            
            for signal in analysis.get("convergence_signals", [])[:10]:
                url_display = signal.get("result_url", "")[:50]
                domain = signal.get("overlap_domain", "unknown")
                confidence = signal.get("confidence", 0)
                
                lines.extend([
                    f"- **Domain Overlap** ({domain}):",
                    f"    - URL: `{url_display}...`",
                    f"    - Confidence: {confidence:.1%}",
                    ""
                ])
        else:
            lines.append("No cross-domain convergence signals detected yet.\n")
        
        # Temporal analysis
        lines.extend([
            "## ⏱️ Temporal Tracking",
            "",
            f"- Average results per query: {temporal.get('average_results_per_query', 0):.1f}",
            f"- Discovery rate (normalized): {temporal.get('discovery_rate', 0):.2%}",
            ""
        ])
        
        # ASCII Heatmap
        lines.extend([ascii_heatmap])
        
        # Relationship iteration log
        lines.extend([
            "## 🔗 Relationship Iteration Log",
            "",
            "### Layer 1: Symbol → Domain Associations",
            "",
            f"Discovered {len([r for r in new_rels if 'symbol_domain' in r.get('type', '')])} symbol-domain connections",
            "",
            "### Layer 2: Cross-Discovery Links",
            "",
            f"Created {len([r for r in new_rels if 'cross_discovery' in r.get('type', '')])} relationships between new discoveries",
            "",
            "### Layer 3: Temporal Sequences",
            "",
            f"Existing database relationships before this run: {existing_rels_count}",
            ""
        ])
        
        # Add symbol mention counts from queries
        lines.extend([
            "🔤 Symbol Mention Summary:",
            ""
        ])
        
        symbol_counts = {"124": 0, "963": 0, "55": 0}
        for result in scraper_results:
            query = result.get("query", "")
            if "124" in query or "0 to" in query.lower():
                symbol_counts["124"] += len(result.get("results", []))
            elif "963" in query:
                symbol_counts["963"] += len(result.get("results", []))
            elif "55" in query:
                symbol_counts["55"] += len(result.get("results", []))
        
        for symbol, count in sorted(symbol_counts.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"- `{symbol}`: {count} mentions")
        
        lines.extend([
            "",
            "## 📈 Key Insights & Anomalies",
            "",
            "### High-Frequency Domain Categories:",
            ""
        ])
        
        # Extract domain frequencies from results
        domain_freq = {}
        for result in scraper_results[:3]:
            parsed = result.get("results", [])
            for r in parsed[:3]:
                url = r.get("url", "")
                if len(url.split('/')) > 2:
                    domain_part = url.split('/')[2]
                    category = "encyclopedia" if 'wikipedia' in domain_part else "general_web"
                    domain_freq[category] = domain_freq.get(category, 0) + 1
        
        for domain, count in sorted(domain_freq.items(), key=lambda x: x[1], reverse=True):
            lines.extend([f"- {domain.capitalize()}: {count} results\n"])
        
        lines.extend([
            "",
            "## 🎯 Recommendations for Next Overnight Run",
            "",
            "1. Focus on symbols with <3 domain appearances for deeper analysis",
            "2. Re-run queries that returned <2 results for refinement",
            "3. Investigate high-confidence convergence signals (>0.8 confidence)",
            "",
            "---\n",
            f"*Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n"
        ])
        
        return lines


if __name__ == "__main__":
    # Test standalone usage (requires pre-populated results dict)
    print("📄 Testing ReportGeneratorModule standalone...")
    
    generator = ReportGeneratorModule()
    
    test_results = {
        "results": [],  # Empty for minimal report
        "analysis": {},
        "new_rels": [],
        "temporal": {},
        "ascii_heatmap": "\n",
        "existing_rels_count": 100
    }
    
    report_path = generator.generate_report(test_results)
    print(f"\n✅ Report generated at: {report_path}")
