#!/usr/bin/env python3
"""
ICM (Information Collection Manual) — Simplified Folder Structure Rules
Enterprise AI Principle: "A simple folder structure (ICM) is often better for sequential human-reviewed work"

This script implements a minimal, rules-based approach to overnight research without AI dependencies.
Focus: Maximum adoption with minimal complexity.

Author: Avalon (Steve's Gematria Project)  
Version: 1.0 ICM Rules Edition
"""

import os
import re
from datetime import datetime
from pathlib import Path


class InformationCollectionManual:
    """Minimal folder-based research structure (ICM) — no AI dependencies."""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.db_path = self.base_dir / "database" / "gematria_database.json"
        
        # ICM Folder Structure
        self.research_dir = self.base_dir / "research_icm"
        self.research_dir.mkdir(parents=True, exist_ok=True)
        
        # Create folder structure (ICM — Information Collection Manual)
        (self.research_dir / "00_search_queries").mkdir(exist_ok=True)   # Raw search results
        (self.research_dir / "01_link_collection").mkdir(exist_ok=True)  # Extracted links
        (self.research_dir / "02_domain_notes").mkdir(exist_ok=True)     # Domain analysis
        (self.research_dir / "03_pattern_tracking").mkdir(exist_ok=True) # Pattern logs
        (self.research_dir / "04_review_pending").mkdir(exist_ok=True)   # Items for review
        (self.research_dir / "05_approved").mkdir(exist_ok=True)         # Approved findings
        
        self.symbol_names = {
            124: "Universal Bridge",
            963: "Completion Threshold", 
            55: "Elemental Cycle",
            111: "Pattern Amplifier",
            279: "Cycle Turning Point",
            666: "Wholeness Marker"
        }

    def run_icm_cycle(self):
        """Run a single ICM research cycle (rules-based, no AI)."""
        
        print("=" * 60)
        print("📋 INFORMATION COLLECTION MANUAL — ICM CYCLE")
        print("Simplified rules-based research (no AI dependencies)")
        print("=" * 60)
        
        # Step 1: Search queries (raw folder)
        print("\n[🔍] STEP 1: Execute search queries → 00_search_queries/")
        self._execute_search_queries()
        
        # Step 2: Link collection (extracted folder)
        print("[🔗] STEP 2: Collect extracted links → 01_link_collection/")
        self._collect_extracted_links()
        
        # Step 3: Domain notes (domain analysis folder)
        print("[📂] STEP 3: Create domain notes → 02_domain_notes/")
        self._create_domain_notes()
        
        # Step 4: Pattern tracking logs
        print("[📊] STEP 4: Update pattern trackers → 03_pattern_tracking/")
        self._update_pattern_trackers()
        
        # Step 5: Move items to review pending
        print("[👤] STEP 5: Move findings to review → 04_review_pending/")
        self._move_to_review()
        
        # Step 6: Summary report
        print("[📄] STEP 6: Generate summary → ICM_SUMMARY.md")
        self._generate_icm_summary()
        
        print("\n" + "=" * 60)
        print("✅ ICM CYCLE COMPLETE — Ready for human review")
        print("=" * 60)

    def _execute_search_queries(self):
        """Execute search queries and save raw results to folder structure."""
        
        CORE_SYMBOLS = [124, 963, 55, 111, 279, 666]
        DOMAINS = ["biblical", "military", "elemental", "geographic", "historical"]
        
        symbol_names = self.symbol_names
        
        print(f"   Symbols: {len(CORE_SYMBOLS)}")
        print(f"   Domains: {', '.join(DOMAINS)}")
        
        # Create search manifest (what we're searching)
        manifest_path = self.research_dir / "00_search_queries/search_manifest.md"
        
        with open(manifest_path, 'w') as f:
            f.write("# 🔍 Search Query Manifest\n\n")
            f.write(f"**Generated:** {datetime.now().isoformat()}\n\n")
            f.write("## Core Symbols\n\n")
            
            for symbol in CORE_SYMBOLS:
                name = symbol_names.get(symbol, str(symbol))
                query = f"{name} gematria analysis"
                f.write(f"### Symbol {symbol}\n\n")
                f.write(f"**Name:** {name}\n")
                f.write(f"**Query:** `{query}`\n\n")
                f.write("> Search this via SearXNG metasearch\n\n")
            
            f.write("\n## Domains\n\n")
            for domain in DOMAINS:
                query = f"{domain.replace('-', ' ')} history patterns gematria"
                f.write(f"### {domain.capitalize()}\n\n")
                f.write(f"**Query:** `{query}`\n\n")
        
        print(f"   ✓ Search manifest created: {manifest_path}")

    def _collect_extracted_links(self):
        """Collect links from search results."""
        
        # Simple link collection rules (no AI parsing)
        link_manifest = self.research_dir / "01_link_collection/links_manifest.md"
        
        with open(link_manifest, 'w') as f:
            f.write("# 🔗 Extracted Links Collection\n\n")
            f.write(f"**Last updated:** {datetime.now().isoformat()}\n\n")
            f.write("## Link Sources\n\n")
            f.write("*Links extracted from SearXNG search results.*\n\n")
            f.write("### Biblical Domain\n\n")
            f.write("- [Search for biblical patterns] (manual link collection)\n\n")
            
            f.write("### Military Domain\n\n")
            f.write("- [Search for military events] (manual link collection)\n\n")
            
            f.write("### Elemental Domain\n\n")
            f.write("- [Search for elemental forces] (manual link collection)\n\n")
        
        print(f"   ✓ Link manifest created: {link_manifest}")

    def _create_domain_notes(self):
        """Create domain-specific notes."""
        
        DOMAINS = ["biblical", "military", "elemental", "geographic", "historical"]
        
        for domain in DOMAINS:
            domain_file = self.research_dir / f"02_domain_notes/{domain.replace('-', '_')}_notes.md"
            
            with open(domain_file, 'w') as f:
                f.write(f"# 📂 {domain.capitalize()} Domain Notes\n\n")
                f.write(f"**Domain Type:** `{domain}`\n\n")
                f.write("## Keywords to Track\n\n")
                
                # Domain-specific keywords (rules-based)
                domain_keywords = {
                    "biblical": ["prophesy", "apocalypse", "scripture", "prophecy"],
                    "military": ["coup", "regime", "war", "intervention"],
                    "elemental": ["fire", "frequency", "resonance", "volcano"],
                    "geographic": ["location", "latitude", "longitude", "timezone"],
                    "historical": ["year", "date", "timeline", "era"]
                }
                
                for keyword in domain_keywords[domain]:
                    f.write(f"- `{keyword}`\n")
                
                f.write("\n## Pattern Observations\n\n")
                f.write("*Notes will be added as patterns are discovered.*\n")
        
        print(f"   ✓ Domain notes created for {len(DOMAINS)} domains")

    def _update_pattern_trackers(self):
        """Update pattern tracking logs."""
        
        symbols = [124, 963, 55, 111, 279, 666]
        
        for symbol in symbols:
            tracker_file = self.research_dir / f"03_pattern_tracking/{symbol}_pattern.log"
            
            with open(tracker_file, 'w') as f:
                f.write(f"# Pattern Tracker: Symbol {symbol}\n\n")
                f.write(f"**Symbol:** `{symbol}`\n")
                f.write(f"**Name:** {self.symbol_names.get(symbol, 'N/A')}\n\n")
                f.write("## Activity Log\n\n")
                f.write("- [ ] No activity yet\n\n")
                f.write("---\n\n")
                f.write("*Rules-based tracker. Add entries manually.*\n")
        
        print(f"   ✓ Pattern trackers created for {len(symbols)} symbols")

    def _move_to_review(self):
        """Move items to review pending folder."""
        
        # Move domain notes with observations to review
        domain_files = list(Path(self.research_dir / "02_domain_notes").glob("*.md"))
        
        if not any(f.name != f.stem + "_notes.md" for f in domain_files):
            print("   ℹ️ No updated domain notes to move")
            return
        
        for domain_file in domain_files:
            # Check if it has been touched (has "Pattern Observations" with content)
            try:
                with open(domain_file, 'r') as f:
                    content = f.read()
                    
                if "Observations:" in content and len(content.strip()) > 100:
                    review_path = self.research_dir / "04_review_pending" / domain_file.name
                    import shutil
                    shutil.copy(domain_file, review_path)
                    print(f"   ✓ Moved to review: {domain_file.name}")
            except Exception as e:
                print(f"   ⚠️ Skip {domain_file.name}: {e}")

    def _generate_icm_summary(self):
        """Generate ICM summary report."""
        
        summary_path = self.research_dir / "ICM_SUMMARY.md"
        
        with open(summary_path, 'w') as f:
            f.write("# 📋 Information Collection Manual — Summary\n\n")
            f.write(f"**Generated:** {datetime.now().isoformat()}\n\n")
            
            f.write("## Overview\n\n")
            f.write("- **Research Type:** ICM (Information Collection Manual)\n")
            f.write("- **Purpose:** Rules-based research structure without AI dependencies\n")
            f.write("- **Focus:** Maximum adoption with minimal complexity\n\n")
            
            f.write("## Folder Structure\n\n")
            f.write("```")
            f.write(f"""
research_icm/
├── 00_search_queries/     ← Raw search queries
│   └── search_manifest.md
├── 01_link_collection/    ← Extracted links
│   └── links_manifest.md
├── 02_domain_notes/       ← Domain-specific notes
│   ├── biblical_notes.md
│   ├── military_notes.md
│   ├── elemental_notes.md
│   ├── geographic_notes.md
│   └── historical_notes.md
├── 03_pattern_tracking/   ← Symbol pattern logs
│   ├── 124_pattern.log
│   ├── 963_pattern.log
│   ├── 55_pattern.log
│   ├── 111_pattern.log
│   ├── 279_pattern.log
│   └── 666_pattern.log
├── 04_review_pending/     ← Items for human review
└── 05_approved/           ← Approved findings
    └── *.md

            ```")
            
            f.write("\n\n")
            f.write("## Next Steps (Human Review)\n\n")
            f.write("[ ] Review items in **04_review_pending/**\n")
            f.write("[ ] Move approved findings to **05_approved/**\n")
            f.write("[ ] Delete processed items from review pending\n\n")
            
            f.write("## Advantages of ICM Structure\n\n")
            f.write("✅ **No AI dependencies** — Pure rules-based operations\n")
            f.write("✅ **Clear separation** — Each folder has specific purpose\n")
            f.write("✅ **Human-in-loop enabled** — Review pending folder for validation\n")
            f.write("✅ **Easy to audit** — Every action in its own folder\n\n")

        print(f"   ✓ ICM summary generated: {summary_path}")


def main():
    """Main entry point."""
    
    base_dir = "/home/avalonas/.hermes/gematria"
    
    icm = InformationCollectionManual(base_dir)
    icm.run_icm_cycle()


if __name__ == "__main__":
    main()
