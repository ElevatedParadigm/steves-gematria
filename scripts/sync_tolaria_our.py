#!/usr/bin/env python3
"""
Tolaria OUR Vault Auto-Sync Utility
Updates Tolaria's Obsidian Universal Repository vault after each overnight research report.

Usage:
    python sync_tolaria_our.py --force        # Force update even if no changes
    python sync_tolaria_our.py               # Normal incremental sync

This utility extracts recent findings from gematria search results and relationship tracking,
then creates/update files in the Tolaria OUR vault for easy reference.
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Configuration
GEMATRIA_DIR = Path.home() / ".hermes" / "gematria"
TOLARIA_EXPORTS = GEMATRIA_DIR / "tolaria_exports"
RELATIONS_FOLDER = TOLARIA_EXPORTS / "relations"
SEARCH_RESULTS_FILE = GEMATRIA_DIR / "search_results.json"
PATTERN_CONVERGENCE_FILE = GEMATRIA_DIR / "pattern_convergence_analysis.json"
CROSS_REF_INDEX = GEMATRIA_DIR / "obsidian_exports" / "CROSS_REFERENCE_INDEX.md"

# Vault structure
OUR_DAILY_REPORTS = TOLARIA_EXPORTS / "DAILY_REPORTS"
OUR_QUICK_REFS = TOLARIA_EXPORTS / "QUICK_REFS"
RELATIONS_FOLDER.mkdir(parents=True, exist_ok=True)


def extract_recent_findings(search_results: dict, convergence_analysis: dict | None = None):
    """Extract key findings from search results and convergence analysis."""
    findings = []
    
    # Get core symbols mentioned in search
    if "data" in search_results and "success" in search_results:
        data = search_results["data"]
        if isinstance(data, list):
            items = data
        else:
            items = data.get("scraped", [])
        
        for idx, item in enumerate(items[:5], 1):  # Top 5 items
            title = item.get("title", "N/A")[:80] if len(item.get("title", "")) <= 80 else str(item["title"])[:80] + "..."
            url = item.get("url", "N/A")[:60] if len(str(item.get("url", ""))) <= 60 else str(item["url"])[:60] + "..."
            desc = item.get("description", "")[:150] if item.get("description", "").strip() else "No description"
            
            findings.append({
                "id": idx,
                "title": title,
                "url": url,
                "description": desc[:200],
                "category": "Calculation Tool" if "calculator" in desc.lower() else "Pattern Analysis"
            })
    
    return findings


def generate_our_report(findings: list, cross_ref_data: dict | None = None):
    """Generate comprehensive Our vault report."""
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Extract core symbols from last query if available
    search_query = "gematria patterns 124 963 55 111"
    
    return f'''---
title: "Our Research Vault - Recent Findings {timestamp}"
tags: [gematria, overnight-research, pattern-convergence, calculation-tools]
date: {timestamp}
source: Steve\'s Gematria Composer Engine v1.9.0
location: /home/avalonas/.hermes/gematria/tolaria_exports/
---

# 🌙 Our Vault - Recent Findings

**Search Query:** `{search_query}`  
**Engine:** Steve\'s Gematria Composer (Local Firecrawl + SearXNG-Clean)  
**Status:** ✅ Completed  
**Report Generated:** {timestamp}

---

## 🔍 Search Results Summary

### Items Discovered: {len(findings)}

'''.strip() + '\n' + format_findings_table(findings)


def format_findings_table(findings: list):
    """Format findings as markdown table."""
    lines = []
    for item in findings:
        lines.append(f'''### Item #{item["id"]}: {item["title"]}
- **URL:** [{item["url"]}]({item["url"]})
- **Category:** {item["category"]}
- **Description:** {item["description"]}
''')
    return '\n'.join(lines)


def generate_our_quick_ref(findings: list):
    """Generate quick reference file."""
    timestamp = datetime.now().strftime("%Y-%m-%d")
    
    findings_summary = ""
    for item in findings[:5]:  # Top 5 items
        title_preview = item["title"][:70] if len(item["title"]) > 70 else item["title"]
        findings_summary += f"- [{item['id']}] {title_preview}\n"
    
    return f'''# 📜 OUR Vault Quick Reference - {timestamp}

**Last Updated:** {timestamp} UTC  
**Source:** Steve\'s Gematria Overnight Research Protocol v1.9.0  

---

## 🔍 Recent Findings ({len(findings)} items)

{findings_summary}

---

*Auto-updated by overnight research protocol*
'''.strip()


def main(force: bool = False):
    """Main sync function."""
    print("=" * 70)
    print("📁 TOLARIA OUR VAULT AUTO-SYNC")
    print("=" * 70)
    
    # Check if source files exist
    search_results = SEARCH_RESULTS_FILE if SEARCH_RESULTS_FILE.exists() else None
    convergence_file = PATTERN_CONVERGENCE_FILE if PATTERN_CONVERGENCE_FILE.exists() else None
    cross_ref_index = CROSS_REF_INDEX if CROSS_REF_INDEX.exists() else None
    
    if not any([search_results, convergence_file, cross_ref_index]):
        print("\n⚠️  No recent gematria search results found in:")
        print(f"   - {SEARCH_RESULTS_FILE}")
        print(f"   - {PATTERN_CONVERGENCE_FILE}")
        print(f"   - {CROSS_REF_INDEX}")
        print("\nRun composer.py first to generate search results!")
        return False
    
    # Extract findings from latest search
    if search_results:
        with open(search_results, 'r') as f:
            data = json.load(f)
        
        findings = extract_recent_findings(data, convergence_analysis=None)
        
        print(f"\n✅ Found {len(findings)} items in recent search results")
        
        # Generate OUR report
        our_report = generate_our_report(findings, convergence_file)
        
        # Create timestamped filename
        timestamp = datetime.now().strftime("%Y-%m-%d")
        report_file = OUR_DAILY_REPORTS / f"OUR_{timestamp}_recent_findings.md"
        
        # Write to vault
        with open(report_file, 'w') as f:
            f.write(our_report)
        
        print(f"📄 Written: {report_file}")
        
        # Generate quick reference
        quick_ref = generate_our_quick_ref(findings)
        
        # Also write as daily ref
        quick_ref_file = OUR_QUICK_REFS / f"OUR_QUICK_{timestamp}.md"
        with open(quick_ref_file, 'w') as f:
            f.write(quick_ref)
        
        print(f"📄 Written: {quick_ref_file}")
    
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Sync Tolaria OUR vault with recent gematria findings")
    parser.add_argument("--force", action="store_true", help="Force update even if no changes")
    args = parser.parse_args()
    
    success = main(force=args.force)
    sys.exit(0 if success else 1)
