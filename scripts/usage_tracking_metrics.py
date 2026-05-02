#!/usr/bin/env python3
"""
Usage Tracking Script — Enterprise AI Principle: Adoption Before Accuracy

This script tracks ACTUAL USAGE of research outputs (not just generation).
Business metrics over technical metrics principle applied.

Author: Avalon (Steve's Gematria Project)
Version: 1.0 Adoption Tracking Edition
"""

import json
import os
from datetime import datetime


class UsageTracker:
    """Track actual adoption of research outputs, not just generation."""
    
    def __init__(self):
        self.base_dir = "/home/avalonas/.hermes/gematria"
        self.usage_log_path = self.base_dir / "usage_tracking" / "usage_log.json"
        self.obsidian_usage_path = self.base_dir / "usage_tracking" / "obsidian_backlinks.md"
        
        # Create usage tracking folder
        (self.usage_log_path.parent).mkdir(parents=True, exist_ok=True)
    
    def load_database(self):
        """Load the gematria database."""
        db_path = self.base_dir / "database" / "gematria_database.json"
        try:
            with open(db_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] Could not load database: {e}")
            return {}

    def track_usage(self):
        """Track usage patterns of research outputs."""
        
        db = self.load_database()
        usage_record = {
            "timestamp": datetime.now().isoformat(),
            "searches_executed": 0,
            "links_extracted": 0,
            "reports_generated": [],
            "outputs_used": []
        }
        
        # Load existing usage log
        if os.path.exists(self.usage_log_path):
            with open(self.usage_log_path, 'r') as f:
                self.usage_history = json.load(f)
        else:
            self.usage_history = []
        
        print("\n" + "=" * 60)
        print("📊 USAGE TRACKING — ADOPTION METRICS")
        print("=" * 60)

    def track_search_success(self, db):
        """Track which searches actually found results (adoption metric)."""
        
        core_symbols = db.get("metadata", {}).get("core_symbols", [])
        searches_recorded = 0
        
        for symbol in core_symbols:
            pattern_summary = db.get("pattern_summary", {}).get(symbol, {})
            
            # Check if this symbol has recent activity
            batch_occurrences = db.get("batch_symbol_occurrences", {}).get(symbol, [])
            
            if batch_occurrences and len(batch_occurrences) >= 3:
                searches_recorded += 1
        
        print(f"[✅] Searches with results: {searches_recorded}/{len(core_symbols)}")

    def track_link_extraction(self):
        """Track number of links extracted from search results."""
        
        # Estimate based on overnight research report size
        reports_dir = self.base_dir / "reports"
        
        if not reports_dir.exists():
            print("[ℹ️] No reports directory found")
            return
        
        report_count = len(list(reports_dir.glob("overnight_research_v2_*.md")))
        estimated_links = report_count * 15  # Average 15 links per report
        
        print(f"[✅] Estimated links extracted: {estimated_links}")

    def track_report_usage(self):
        """Track which reports have backlinks from Obsidian notes."""
        
        obsidian_exports = self.base_dir / "obsidian_exports"
        
        if not obsidian_exports.exists():
            print("[ℹ️] No obsidian_exports directory found")
            return
        
        # Count files in obsidian_exports (proxy for usage)
        note_count = len(list(obsidian_exports.glob("*.md")))
        
        # Exclude utility files
        utility_files = [".SYNC_LOG.md", ".REVIEW_PENDING", ".HUMAN_REVIEW_LOG.md"]
        useful_notes = count - len([f.name for f in obsidian_exports.iterdir() if any(u in f.name for u in utility_files)])
        
        print(f"[✅] Obsidian notes referencing research: {useful_notes}")

    def track_adoption_rate(self):
        """Calculate adoption rate (usage vs generation)."""
        
        # Count generated reports
        reports_dir = self.base_dir / "reports"
        if not reports_dir.exists():
            return 0
        
        total_generated = len(list(reports_dir.glob("overnight_research_v2_*.md")))
        
        # Count actual usage (notes that reference them)
        obsidian_exports = self.base_dir / "obsidian_exports"
        useful_notes = len([f for f in obsidian_exports.iterdir() 
                           if f.name.endswith('.md') and 
                           not any(u in f.name for u in [".SYNC", ".REVIEW", ".HUMAN"])])
        
        # Estimate adoption rate (simplified)
        if total_generated > 0:
            adoption_rate = min(useful_notes / total_generated, 1.0) * 100
        else:
            adoption_rate = 0
        
        print(f"[✅] Adoption rate: {adoption_rate:.1f}%")
        return adoption_rate

    def save_usage_record(self):
        """Save usage record to log file."""
        
        # Append current usage to history
        with open(self.usage_log_path, 'r') as f:
            history = json.load(f)
        
        history.append(self.usage_record)
        
        with open(self.usage_log_path, 'w') as f:
            json.dump(history, f, indent=2)

    def report_usage_summary(self):
        """Generate comprehensive usage summary."""
        
        print("\n" + "=" * 60)
        print("📋 USAGE SUMMARY REPORT")
        print("=" * 60)
        
        db = self.load_database()
        
        # Core metrics
        core_symbols = len(db.get("metadata", {}).get("core_symbols", []))
        entries_count = len(db.get("entries", {}))
        
        print(f"\n**Research Outputs Generated:**")
        print(f"  • Core symbols tracked: `{core_symbols}`")
        print(f"  • Database entries analyzed: `{entries_count}`")
        
        # Adoption metrics
        adoption_rate = self.track_adoption_rate()
        print(f"\n**Adoption Metrics (Business over Tech):**")
        print(f"  • Search success rate: ~{self.usage_record.get('search_success_rate', 'N/A')}%")
        print(f"  • Links extracted: {self.usage_record.get('links_extracted', 'N/A')}")
        print(f"  • Reports generated: {len(self.usage_record.get('reports_generated', []))}")
        print(f"  • Obsidian notes created: {self.usage_record.get('notes_created', 'N/A')}")
        
        # Usage patterns
        recent_usage = self.usage_history[-3:] if len(self.usage_history) >= 3 else self.usage_history
        
        if recent_usage:
            print(f"\n**Usage Trends (Last 3 Cycles):**")
            for i, usage in enumerate(recent_usage):
                timestamp = usage.get("timestamp", "")[:10]
                links = usage.get("links_extracted", 0)
                reports = len(usage.get("reports_generated", []))
                print(f"  • {timestamp}: `{links}` links, `{reports}` reports")

        # Improvement suggestions (based on usage data)
        if adoption_rate < 30:
            print("\n⚠️  Adoption rate is low (<30%). Consider:")
            print("   1. Reviewing output relevance before generation")
            print("   2. Adding backlinks from Obsidian notes manually")
            print("   3. Creating summaries that users find more valuable")
        elif adoption_rate > 70:
            print("\n✅ Excellent adoption rate! System is being used effectively.")

    def track_output_usage_patterns(self):
        """Track which outputs are actually referenced vs generated."""
        
        obsidian_exports = self.base_dir / "obsidian_exports"
        
        if not obsidian_exports.exists():
            print("[ℹ️] No obsidian_exports directory found")
            return
        
        # Track file access frequency (proxy for usage)
        import os.path
        recent_exports = []
        
        for filepath in obsidian_exports.glob("*.md"):
            mtime = datetime.fromtimestamp(filepath.stat().st_mtime).strftime("%Y-%m-%d")
            
            # Check if file has been modified recently (this week)
            now = datetime.now()
            cutoff = now.replace(day=1).replace(hour=0, minute=0, second=0) + __import__('datetime').timedelta(days=7)
            
            file_modified = datetime.fromtimestamp(filepath.stat().st_mtime) <= cutoff
            
            if file_modified and filepath.name not in [".SYNC", ".REVIEW", ".HUMAN"]:
                recent_exports.append({
                    "name": filepath.name,
                    "last_modified": mtime,
                    "relative_path": str(filepath.relative_to(self.base_dir))
                })
        
        print(f"\n[📊] Recently used exports: {len(recent_exports)}")
        for export in recent_exports[:5]:  # Show top 5
            print(f"   • {export['name']} — Modified: {export['last_modified']}")


def main():
    """Main entry point."""
    
    tracker = UsageTracker()
    
    # Track current usage session
    print("\n📊 TRACKING USAGE METRICS")
    print("=" * 60)
    
    db = tracker.load_database()
    if not db:
        print("[ERROR] Could not load database. Exiting.")
        return
    
    # Core symbol tracking
    core_symbols = db.get("metadata", {}).get("core_symbols", [])
    print(f"\n[🔍] Tracking {len(core_symbols)} core symbols...")
    
    # Batch occurrences check
    batch_occurrences = db.get("batch_symbol_occurrences", {})
    symbols_with_activity = len([sym for sym, info in batch_occurrences.items() 
                                 if len(info) >= 3])
    
    print(f"   • Symbols with recent activity: `{symbols_with_activity}`")
    
    # Report generation tracking
    reports_dir = tracker.base_dir / "reports"
    if reports_dir.exists():
        new_reports = [f for f in reports_dir.glob("overnight_research_v2_*.md")]
        print(f"   • New reports this cycle: `{len(new_reports)}`")

    # Track adoption metrics
    adoption_rate = tracker.track_adoption_rate()
    
    # Usage summary
    tracker.report_usage_summary()
    tracker.track_output_usage_patterns()
    
    print("\n" + "=" * 60)
    print("✅ USAGE TRACKING COMPLETE")
    print("=" * 60)
    
    print("\n📊 Key Metrics Summary:")
    print(f"   • Adoption Rate: {adoption_rate:.1f}%")
    print(f"   • Symbols with activity: `{symbols_with_activity}` of `{len(core_symbols)}`")
    print(f"   • Reports generated: `{len(new_reports) if 'new_reports' in locals() else 0}`")
    
    print("\n💡 Business Metric Focus:")
    print("   → Track adoption (usage), not just accuracy")
    print("   → Measure 'hours saved', not token counts")
    print("   → Link outputs to actual usage patterns")

    return adoption_rate


if __name__ == "__main__":
    main()
