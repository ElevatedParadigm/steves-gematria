#!/usr/bin/env python3
"""
Obsidian Auto-Sync — Human-in-Loop Review Edition
Enterprise AI Principle: "Human-in-loop is a feature, not a bug"

This script adds review gates to the auto-obisidian sync engine for:
1. Anomaly reports (high-priority findings need human validation)
2. Temporal analysis patterns (review before linking)
3. Relationship quality scoring (flag uncertain connections)

Author: Avalon (Steve's Gematria Project)
Version: 3.0 Human-in-Loop Edition
"""

import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path


class HumanReviewGate:
    """Human-in-loop review gate for auto-sync outputs."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.sync_dir = Path("/home/avalonas/.hermes/gematria/obsidian_exports")
        self.review_pending = self.sync_dir / ".REVIEW_PENDING"
        self.review_log = self.sync_dir / ".HUMAN_REVIEW_LOG.md"
        
        # Create review folder structure
        self.review_pending.mkdir(parents=True, exist_ok=True)
        (self.review_pending / "HIGH_PRIORITY").mkdir(exist_ok=True)  # Anomalies
        (self.review_pending / "MODERATE_PRIORITY").mkdir(exist_ok=True)  # Temporal
        (self.review_pending / "LOW_PRIORITY").mkdir(exist_ok=True)      # General
        
        self.sync_dir.mkdir(parents=True, exist_ok=True)

    def load_database(self):
        """Load the gematria database."""
        try:
            with open(self.db_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] Database load failed: {e}")
            return {}

    def review_anomaly_report(self, db, priority="high"):
        """Create review-ready anomaly report."""
        engine = GematriaEventDetectorV3(db_path=self.db_path)
        
        events = engine.detect_symbol_events(db)
        anomalies = engine.detect_keyword_anomalies(db)
        elemental_patterns = engine.detect_elemental_patterns(db)
        
        # Create HIGH_PRIORITY review folder entry
        review_file = self.review_pending / f"HIGH_PRIORITY/CORE_SYMBOL_ANOMALIES_{datetime.now().strftime('%Y%m%d')}.md"
        
        with open(review_file, 'w') as f:
            f.write("# 🚨 CORE SYMBOL ANOMALY REPORT — HUMAN REVIEW REQUIRED\n\n")
            f.write(f"**Generated:** {datetime.now().isoformat()}\n")
            f.write(f"**Priority Level:** HIGH (requires human validation)\n\n")
            
            # Executive summary for reviewer
            f.write("## 👤 Reviewer Checklist\n\n")
            f.write("[ ] **Understand the findings** — Read through all anomaly reports\n")
            f.write("[ ] **Verify domain context** — Check that anomalies make sense in research context\n")
            f.write("[ ] **Flag false positives** — Mark any patterns that appear coincidental\n")
            f.write("[ ] **Approve for merge** — Confirm which findings to integrate into main docs\n\n")
            
            # Active symbols section
            if events:
                f.write("## 🔴 Active Symbols (Overnight Monitoring)\n\n")
                for event in events:
                    symbol = event["symbol"]
                    event_type = event["event_type"]
                    occurrences = event["recent_occurrences"]
                    meaning = event["meanings"]
                    contexts = event["contexts"]
                    
                    status_marker = "🟢" if occurrences < 3 else "🟡" if occurrences < 5 else "🔴"
                    
                    f.write(f"**{status_marker} `{symbol}`**\n")
                    f.write(f"- **Event Type:** {event_type}\n")
                    f.write(f"- **Recent Activity:** `{occurrences}` occurrences\n")
                    f.write(f"- **Meaning:** {meaning}\n")
                    f.write(f"- **Key Contexts:** {contexts}\n\n")
            
            # Keyword anomalies
            if anomalies:
                f.write("## 🔍 Keyword Frequency Anomalies\n\n")
                for anomaly in anomalies:
                    anomaly_type = anomaly["anomaly_type"]
                    description = anomaly["description"]
                    keywords = anomaly.get("keywords", [])
                    counts = anomaly.get("counts", {})
                    
                    f.write(f"### {anomaly_type}\n\n")
                    f.write(f"> {description}\n\n")
                    
                    if keywords:
                        f.write("| Keyword | Count |\n")
                        f.write("|---------|-------|\n")
                        for kw in keywords[:10]:
                            count = counts.get(kw, 0)
                            bars = "█" * min(count, 20)
                            f.write(f"| `{kw}` | `{bars} ({count})` |\n")
                f.write("\n---\n\n")
            
            # Elemental patterns
            if elemental_patterns:
                f.write("## 🔥 Elemental Force Patterns\n\n")
                for pattern in elemental_patterns:
                    element = pattern["element"]
                    active_symbols = pattern["active_symbols"]
                    context_count = pattern["context_count"]
                    
                    status_marker = "🟢" if context_count > 3 else "🟡"
                    
                    f.write(f"{status_marker} **{element.title()}**\n")
                    f.write(f"- **Active Symbols:** `', '.join(active_symbols)}`\n")
                    f.write(f"- **Context Frequency:** {context_count}\n\n")
            
            if not events and not anomalies and not elemental_patterns:
                f.write("ℹ️ No significant anomalies detected in current dataset.\n\n")
            
            # Merge instructions
            f.write("## ✅ Merge Instructions\n\n")
            f.write("[ ] **Review each HIGH_PRIORITY finding** (above)\n")
            f.write("[ ] **Copy to main ANOMALY_REPORT.md** (remove .REVIEW_PENDING prefix)\n")
            f.write("[ ] **Delete processed review files** from .REVIEW_PENDING/\n")
            f.write("[ ] **Update .HUMAN_REVIEW_LOG.md** with approval timestamp\n\n")
            
            f.write("---\n\n")
            f.write("> *Human-in-loop gate engaged. Do not merge without manual review.*\n")

    def review_temporal_analysis(self, db):
        """Create review-ready temporal analysis."""
        engine = GematriaEventDetectorV3(db_path=self.db_path)
        
        temporal_analysis = engine.analyze_temporal_correlation(db)
        
        # Create MODERATE_PRIORITY entry
        review_file = self.review_pending / f"MODERATE_PRIORITY/TEMPORAL_ANALYSIS_{datetime.now().strftime('%Y%m%d')}.md"
        
        with open(review_file, 'w') as f:
            f.write("# ⏳ TEMPORAL PATTERN ANALYSIS — HUMAN REVIEW\n\n")
            f.write(f"**Generated:** {datetime.now().isoformat()}\n")
            f.write(f"**Priority Level:** MODERATE (review before linking to main docs)\n\n")
            
            f.write("## 👤 Reviewer Checklist\n\n")
            f.write("[ ] **Verify timeline data accuracy** — Check year/month extractions\n")
            f.write("[ ] **Assess pattern significance** — Determine if correlations are meaningful\n")
            f.write("[ ] **Approve for integration** — Confirm to merge into TEMPORAL_PATTERN_ANALYSIS.md\n\n")

    def update_review_log(self, review_file: str, approved: bool, notes: str = ""):
        """Update human review log."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(self.review_log, 'a') as f:
            if approved:
                status = "✅ APPROVED"
            else:
                status = "❌ REJECTED"
            
            f.write(f"\n## [{status}] {review_file}\n")
            f.write(f"- **Timestamp:** {timestamp}\n")
            f.write(f"- **Notes:** {notes if notes else 'No additional notes'}\n")

    def approve_review(self, review_file: str, output_file: str, notes: str = ""):
        """Approve a review file and merge it to main output."""
        # Read review content
        with open(review_file, 'r') as f:
            content = f.read()
        
        # Remove review-specific headers
        content = re.sub(r'^#\s*.*?HUMAN REVIEW.*?\n', '', content, flags=re.MULTILINE)
        content = re.sub(r'## 👤 Reviewer Checklist\n.*?(?=#|\n\Z)', '', content, flags=re.DOTALL)
        content = re.sub(r'## ✅ Merge Instructions\n.*?\*', '', content, flags=re.DOTALL)
        
        # Write to main output
        with open(output_file, 'w') as f:
            f.write(content)
        
        self.update_review_log(review_file, approved=True, notes=notes)

    def reject_review(self, review_file: str, notes: str = ""):
        """Reject a review file and keep it in pending."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create rejection marker
        rejection_file = self.review_pending / f"{review_file.stem}_REJECTED.md"
        
        with open(rejection_file, 'w') as f:
            f.write(f"# ❌ REJECTED: {review_file.name}\n\n")
            f.write(f"**Rejection Timestamp:** {timestamp}\n")
            f.write(f"**Reason:** {notes}\n\n")

    def run_review_pipeline(self):
        """Run full review pipeline for anomaly reports and temporal analysis."""
        print("\n" + "="*60)
        print("👤 HUMAN-IN-LOOP REVIEW GATE ENGAGED")
        print("="*60)
        
        db = self.load_database()
        if not db:
            print("[ERROR] Could not load database. Exiting.")
            return
        
        print(f"[INFO] Database loaded:")
        print(f"  - Core symbols: {len(db.get('metadata', {}).get('core_symbols', []))}")
        
        # Step 1: Create anomaly review file (HIGH_PRIORITY)
        print("\n[🔍] Creating anomaly report for human review...")
        self.review_anomaly_report(db, priority="high")
        print(f"[✅] High-priority anomalies saved to .REVIEW_PENDING/HIGH_PRIORITY/")
        
        # Step 2: Create temporal analysis review file (MODERATE_PRIORITY)
        print("[🔍] Creating temporal analysis for human review...")
        self.review_temporal_analysis(db)
        print(f"[✅] Temporal patterns saved to .REVIEW_PENDING/MODERATE_PRIORITY/")
        
        print("\n" + "="*60)
        print("📋 REVIEW FILES READY FOR MANUAL APPROVAL")
        print("="*60)
        print("\nPlease review files in .REVIEW_PENDING/ and run:")
        print("  • approve_anomalies.py — Merge anomaly findings")
        print("  • approve_temporal.py — Merge temporal patterns")
        print("  • OR manually copy/move files as needed\n")


# ============== Review Approval Scripts (Simplified) ==============

def approve_anomalies(output_file: str):
    """Manually approve anomalies for merge."""
    print("\n🔴 APPROVING ANOMALY REPORT FOR MERGE")
    print("="*60)
    
    db_path = "/home/avalonas/.hermes/gematria/database/gematria_database.json"
    with open(db_path, 'r') as f:
        db = json.load(f)
    
    # Create engine to extract data
    class GematriaEventDetectorV3:
        def __init__(self, db_path: str):
            self.db_path = db_path
            self.sync_dir = Path("/home/avalonas/.hermes/gematria/obsidian_exports")
            
        def load_database(self):
            try:
                with open(self.db_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[ERROR] Database load failed: {e}")
                return {}
        
        def detect_symbol_events(self, db):
            events_detected = []
            core_symbols = db.get("metadata", {}).get("core_symbols", [])
            
            for symbol in core_symbols:
                pattern_summary = db.get("pattern_summary", {}).get(symbol, {})
                batch_occurrences = db.get("batch_symbol_occurrences", {}).get(symbol, [])
                
                if batch_occurrences:
                    recent_activity = batch_occurrences[-3:] if len(batch_occurrences) >= 3 else batch_occurrences
                    
                    events_detected.append({
                        "symbol": symbol,
                        "event_type": "symbol_activation",
                        "recent_occurrences": len(recent_activity),
                        "meanings": pattern_summary.get("meaning", ""),
                        "contexts": ", ".join(pattern_summary.get("contexts", [])[:2])
                    })
            
            return events_detected
        
        def detect_keyword_anomalies(self, db):
            anomalies_detected = []
            keyword_counts = {}
            domains = db.get("metadata", {}).get("domains_tracked", [])
            
            for entry_key, entry_data in db.get("entries", {}).items():
                title = entry_data.get("title", "")
                keywords = re.findall(r'\b[A-Z]{2,10}\b', title)[:5]
                
                for kw in keywords:
                    if len(kw) <= 10 and len(kw) >= 2:
                        if kw not in keyword_counts:
                            keyword_counts[kw] = 0
                        keyword_counts[kw] += 1
            
            if keyword_counts:
                max_count = max(keyword_counts.values())
                significant_keywords = {kw: count for kw, count in keyword_counts.items() 
                                       if count >= max_count * 0.3}
                
                anomalies_detected.append({
                    "anomaly_type": "keyword_frequency_spike",
                    "keywords": list(significant_keywords.keys())[:10],
                    "counts": {kw: significant_keywords[kw] for kw in significant_keywords.keys()[:10]},
                    "description": f"Detected {len(significant_keywords)} keywords with elevated frequency"
                })
            
            return anomalies_detected
        
        def detect_elemental_patterns(self, db):
            elemental = db.get("metadata", {}).get("elemental_forces", [])
            pattern_summary = db.get("pattern_summary", {})
            
            elemental_patterns = []
            
            for element in elemental:
                matching_symbols = [sym for sym, info in pattern_summary.items() 
                                  if element.lower() in str(info).lower()]
                
                if matching_symbols:
                    elemental_patterns.append({
                        "element": element,
                        "active_symbols": matching_symbols[:5],
                        "context_count": sum(1 for info in pattern_summary.values() 
                                          if element.lower() in str(info).lower())
                    })
            
            return elemental_patterns
        
        def create_anomaly_report(self, db):
            events = self.detect_symbol_events(db)
            anomalies = self.detect_keyword_anomalies(db)
            elemental_patterns = self.detect_elemental_patterns(db)
            
            with open(output_file, 'w') as f:
                f.write("# 🚨 Core Symbol Anomaly Detection\n\n")
                f.write(f"**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Active symbols report
                if events:
                    f.write("## 🔴 Active Symbols (Overnight Monitoring)\n\n")
                    for event in events:
                        symbol = event["symbol"]
                        event_type = event["event_type"]
                        occurrences = event["recent_occurrences"]
                        meaning = event["meanings"]
                        contexts = event["contexts"]
                        
                        status_marker = "🟢" if occurrences < 3 else "🟡" if occurrences < 5 else "🔴"
                        
                        f.write(f"**{status_marker} `{symbol}`**\n")
                        f.write(f"- **Event Type:** {event_type}\n")
                        f.write(f"- **Recent Activity:** `{occurrences}` occurrences\n")
                        f.write(f"- **Meaning:** {meaning}\n")
                        f.write(f"- **Key Contexts:** {contexts}\n\n")
                
                # Keyword anomalies
                if anomalies:
                    f.write("## 🔍 Keyword Frequency Anomalies\n\n")
                    for anomaly in anomalies:
                        anomaly_type = anomaly["anomaly_type"]
                        description = anomaly["description"]
                        keywords = anomaly.get("keywords", [])
                        counts = anomaly.get("counts", {})
                        
                        f.write(f"### {anomaly_type}\n\n")
                        f.write(f"> {description}\n\n")
                        
                        if keywords:
                            f.write("| Keyword | Count |\n")
                            f.write("|---------|-------|\n")
                            for kw in keywords[:10]:
                                count = counts.get(kw, 0)
                                bars = "█" * min(count, 20)
                                f.write(f"| `{kw}` | `{bars} ({count})` |\n")
                        f.write("\n---\n\n")
                
                # Elemental patterns
                if elemental_patterns:
                    f.write("## 🔥 Elemental Force Patterns\n\n")
                    for pattern in elemental_patterns:
                        element = pattern["element"]
                        active_symbols = pattern["active_symbols"]
                        context_count = pattern["context_count"]
                        
                        status_marker = "🟢" if context_count > 3 else "🟡"
                        
                        f.write(f"{status_marker} **{element.title()}**\n")
                        f.write(f"- **Active Symbols:** `{', '.join(active_symbols)}`\n")
                        f.write(f"- **Context Frequency:** {context_count}\n\n")

    db = GematriaEventDetectorV3.load_database()
    
    # Create main anomaly file
    engine = GematriaEventDetectorV3(db_path=db_path)
    approve_anomalies(engine.create_anomaly_report, output_file)
    
    print(f"[✅] Anomaly report approved and saved to: {output_file}")


def approve_temporal(output_file: str):
    """Manually approve temporal analysis for merge."""
    print("\n⏳ APPROVING TEMPORAL ANALYSIS FOR MERGE")
    print("="*60)
    
    db_path = "/home/avalonas/.hermes/gematria/database/gematria_database.json"
    with open(db_path, 'r') as f:
        db = json.load(f)
    
    class GematriaEventDetectorV3:
        def __init__(self, db_path: str):
            self.db_path = db_path
        
        def load_database(self):
            try:
                with open(self.db_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[ERROR] Database load failed: {e}")
                return {}
        
        def analyze_temporal_correlation(self, db):
            entries = db.get("entries", {})
            timeline_entries = [(k, v) for k, v in entries.items() 
                               if v.get("timeline_range")]
            
            if not timeline_entries:
                return {
                    "analysis_type": "temporal_correlation",
                    "status": "no_timeline_data",
                    "description": "No timeline data found in entries"
                }
            
            # Group by year and month
            year_counts = {}
            month_counts = {}
            
            for entry_key, entry_data in timeline_entries:
                timeline = entry_data.get("timeline_range", "")
                
                years_in_timeline = re.findall(r'\b\d{4}\b', timeline)
                months_in_timeline = re.findall(r'(\w+)?\s*\d{1,2}', timeline.lower())
                
                for year in years_in_timeline:
                    year_counts[year] = year_counts.get(year, 0) + 1
                
                for month_name in [m.capitalize() for m in months_in_timeline]:
                    if month_name in month_counts:
                        month_counts[month_name] += 1
                    else:
                        month_counts[month_name] = 1
            
            # Find most active year and month
            top_year = max(year_counts.items(), key=lambda x: x[1]) if year_counts else None
            top_month = max(month_counts.items(), key=lambda x: x[1]) if month_counts else None
            
            return {
                "analysis_type": "temporal_correlation",
                "status": "detected",
                "total_entries_with_timelines": len(timeline_entries),
                "unique_years_covered": len(year_counts),
                "year_distribution": dict(sorted(year_counts.items())),
                "most_active_year": top_year[0] if top_year else None,
                "year_count": top_year[1] if top_year else 0,
                "months_observed": list(month_counts.keys()),
                "description": f"Analyzed {len(timeline_entries)} entries with timeline data across {len(year_counts)} unique years"
            }

    engine = GematriaEventDetectorV3(db_path=db_path)
    temporal_analysis = engine.analyze_temporal_correlation(db)
    
    # Create main temporal file
    with open(output_file, 'w') as f:
        f.write("# ⏳ Temporal Pattern Analysis\n\n")
        f.write(f"**Analysis Type:** {temporal_analysis.get('analysis_type', 'N/A')}\n\n")
        
        if temporal_analysis.get("status") == "detected":
            f.write(f"## 📈 Results\n\n")
            f.write(f"- **Entries Analyzed:** `{temporal_analysis.get('total_entries_with_timelines', 0)}`\n")
            f.write(f"- **Years Covered:** {temporal_analysis.get('unique_years_covered', 0)}\n")
            f.write(f"- **Most Active Year:** `{temporal_analysis.get('most_active_year', 'N/A')}` (events: {temporal_analysis.get('year_count', 0)})\n\n")
            
            f.write("## 📅 Year Distribution\n\n")
            for year, count in temporal_analysis.get("year_distribution", {}).items():
                bars = "■" * min(count, 20)
                f.write(f"- **{year}**: {bars} ({count})\n")
            f.write("\n")
            
            f.write("## 🗓️ Months Observed\n\n")
            for month in temporal_analysis.get("months_observed", [])[:6]:
                f.write(f"- **{month.capitalize()}**\n")
        else:
            f.write(f"⚠️ {temporal_analysis.get('description', 'No temporal data available')}\n")
        
        f.write("\n---\n\n")
        f.write("> *Temporal analysis for overnight monitoring. Run daily.*\n")

    print(f"[✅] Temporal analysis approved and saved to: {output_file}")


def main():
    """Review approval menu."""
    db_path = "/home/avalonas/.hermes/gematria/database/gematria_database.json"
    
    if not os.path.exists(db_path):
        print("[ERROR] Database not found at:", db_path)
        return
    
    print("\n👤 HUMAN-IN-LOOP REVIEW GATE")
    print("="*60)
    print("\nAvailable commands:")
    print("  • approve_anomalies.py output_file=obsidian_exports/CORE_SYMBOL_ANOMALIES.md")
    print("  • approve_temporal.py output_file=obsidian_exports/TEMPORAL_PATTERN_ANALYSIS.md")
    print("  • review_pipeline.py — Run full review pipeline\n")


if __name__ == "__main__":
    main()
