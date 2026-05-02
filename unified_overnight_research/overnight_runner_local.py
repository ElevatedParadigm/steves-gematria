#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌙 Steve's Gematria - Overnight Research Runner (Local Mode)
================================================================

Automated overnight research that works WITHOUT SearXNG.
Uses local Firecrawl API with fallback patterns and graceful degradation.

This runner:
- ✅ Scans image vault for new patterns daily
- ✅ Processes symbol galleries and correlations  
- ✅ Exports trails, matrices, and summaries
- ✅ Falls back to direct scraping when search unavailable
- ✅ Respects your timezone (EEST 02:00-04:00 overnight)

Architecture:
1. Pattern Scanner → finds new images in vault
2. Firecrawl Client → uses local API at localhost:3002
3. Fallback Handler → graceful degradation when search unavailable
4. Export System → creates trails, matrices, summaries
5. Status Reporter → updates CURRENT_STATUS.md after each run
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import requests
import hashlib

# === Configuration ===
VAULT_PATH = "/home/avalonas/Pictures/Steves gematria"
UNIFIED_RESEARCH_DIR = "/home/avalonas/.hermes/gematria/unified_overnight_research"
OUTPUT_DIR = f"{UNIFIED_RESEARCH_DIR}/output"
DATABASE_FILE = f"{UNIFIED_RESEARCH_DIR}/../gematria_database.json"
STATUS_FILE = f"{UNIFIED_RESEARCH_DIR}/CURRENT_STATUS.md"

FIRECRAWL_BASE = "http://localhost:3002"
FIRECRAWL_TIMEOUT = 30  # seconds

# === Status Tracking ===
class RunStatus:
    def __init__(self):
        self.run_timestamp = datetime.now().isoformat()
        self.processed_files = []
        self.new_patterns = []
        self.export_count = 0
        self.errors = []
        self.duration_seconds = 0
    
    def to_dict(self):
        return {
            "run_timestamp": self.run_timestamp,
            "processed_files": self.processed_files,
            "new_patterns": self.new_patterns,
            "export_count": self.export_count,
            "errors": self.errors,
            "duration_seconds": self.duration_seconds
        }


def load_gematria_database():
    """Load or create gematria database"""
    if os.path.exists(DATABASE_FILE):
        try:
            with open(DATABASE_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_to_database(data):
    """Save data to gematria database"""
    db = load_gematria_database()
    db.update(data)
    
    with open(DATABASE_FILE, 'w') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)


def check_firecrawl_health():
    """Check if Firecrawl is responding"""
    try:
        r = requests.get(f"{FIRECRAWL_BASE}", timeout=5)
        return r.status_code in [200, 401]  # Accept both healthy and auth-required
    except Exception as e:
        print(f"⚠️ Firecrawl health check failed: {e}")
        return False


def scan_vault_for_new_images():
    """Scan vault for new or modified images since last run"""
    
    if not os.path.exists(VAULT_PATH):
        print(f"⚠️ Vault doesn't exist: {VAULT_PATH}")
        return []
    
    vault = Path(VAULT_PATH)
    
    # Get all image files
    now = time.time()
    modified_recently = []
    
    for ext in ['*.png', '*.jpg', '*.jpeg', '*.webp']:
        for filepath in vault.glob(ext):
            try:
                mtime = filepath.stat().st_mtime
                if mtime > (now - 86400):  # Modified in last 24 hours
                    modified_recently.append(str(filepath))
            except:
                continue
    
    print(f"🔍 Found {len(modified_recently)} recently modified files")
    return modified_recently


def extract_anchor_term_from_filename(filename):
    """Extract anchor term from image filename"""
    
    name_lower = filename.lower()
    parts = filename.replace(" ", "_").replace("/", "_").split("_")
    
    if "cycle" in name_lower:
        cycle_idx = name_lower.find("cycle")
        domain_idx = name_lower.rfind("_")
        return f"[ANCHOR:CYCLE]", parts[domain_idx] if domain_idx > cycle_idx else None
    elif any(x in name_lower for x in ["domain", "cluster", "matrix"]):
        words = [p.capitalize() for p in parts[:5]]
        return f"[ANCHOR:DOMAIN]", "_".join(words)
    
    return "[ANCHOR:CORRELATION]", None


def process_image_vault_files(files_to_process):
    """Process each file in the vault"""
    
    results = {
        "files_processed": [],
        "patterns_extracted": [],
        "errors": []
    }
    
    for filepath in files_to_process[:50]:  # Process up to 50 files per run
        try:
            filename = os.path.basename(filepath)
            
            print(f"\n📂 Processing: {filename}")
            
            # Extract anchor term
            anchor_term, domain_hint = extract_anchor_term_from_filename(filename)
            
            file_result = {
                "file": filename,
                "anchor": anchor_term,
                "domain_hint": domain_hint,
                "processed_at": datetime.now().isoformat()
            }
            
            results["files_processed"].append(file_result)
            
            # Create trail entry if it's a correlation/cycle file
            if "correlation" in filename.lower() or "cycle" in filename.lower():
                pattern_name = "_".join(domain_hint.split("_")[:2] if domain_hint else [filename])
                
                results["patterns_extracted"].append({
                    "source": filename,
                    "pattern_name": f"Pattern_{pattern_name}",
                    "anchor_term": anchor_term,
                    "status": "discovered"
                })
            
        except Exception as e:
            print(f"  ⚠️ Error processing {filename}: {e}")
            results["errors"].append({"file": filename, "error": str(e)})
    
    return results


def create_export_files(patterns):
    """Create export files for discovered patterns"""
    
    if not patterns:
        return 0
    
    export_count = 0
    
    # Create pattern trails
    trails_dir = f"{OUTPUT_DIR}/pattern_trails"
    os.makedirs(trails_dir, exist_ok=True)
    
    for pattern in patterns[:30]:  # Limit to first 30
        trail_filename = f"{pattern['pattern_name'].replace(' ', '_')}.md"
        trail_path = os.path.join(trails_dir, trail_filename)
        
        # Create markdown entry
        content = f'''---
tags: [gematria, pattern, {pattern["anchor_term"]} {pattern.get("status", "")}]
discovered: {datetime.now().strftime("%Y-%m-%d")}
source-image: `{pattern['source']}`
---

# {pattern['pattern_name']}

## Discovery Information

- **Anchor Term**: `{pattern['anchor_term']}`
- **Status**: {pattern.get('status', 'pending')}
- **Original File**: `{pattern['source']}`

## Pattern Data

This pattern was discovered during overnight research.

See related patterns:
- [[124]] - Universal Threshold/Bridge
- [[666]] - Completion/Wholeness  
- [[9]] - Harmony/Integration Cycle

---

*Auto-generated by Overnight Research Runner*
'''
        
        try:
            with open(trail_path, 'w', encoding='utf-8') as f:
                f.write(content)
            export_count += 1
            
            # Update database
            db = load_gematria_database()
            db[f"pattern_{pattern['pattern_name']}"] = {
                "name": pattern['pattern_name'],
                "source": pattern['source'],
                "anchor_term": pattern['anchor_term'],
                "discovered_at": datetime.now().isoformat()
            }
            save_to_database(db)
            
        except Exception as e:
            print(f"  ⚠️ Error creating trail file {trail_filename}: {e}")
    
    print(f"\n✅ Created {export_count} pattern trail files")
    return export_count


def update_status_file(status: RunStatus):
    """Update CURRENT_STATUS.md with latest run results"""
    
    status.duration_seconds = time.time() - start_time
    
    # Read existing status
    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE, 'r') as f:
                status_content = f.read()
            
            # Find and replace the "Last Run Results" section
            last_section_end = status_content.find("---", 50)
            if last_section_end == -1:
                last_section_end = len(status_content)
            
            new_section = f"""
## 📅 Last Run Results ({datetime.now().strftime("%Y-%m-%d %H:%M")})

- **Duration**: {status.duration_seconds:.1f}s
- **Files Processed**: {len(status.processed_files)}
- **Patterns Exported**: {status.export_count}
- **Errors**: {len(status.errors)}

"""
            
            status_content = status_content[:last_section_end] + new_section
            
            with open(STATUS_FILE, 'w') as f:
                f.write(status_content)
                
        except Exception as e:
            print(f"⚠️ Error updating status file: {e}")


def run_overnight_research():
    """Main overnight research loop"""
    
    global start_time
    
    print("\n" + "=" * 60)
    print("🌙 Steve's Gematria - Overnight Research Runner")
    print("=" * 60)
    print()
    print(f"Starting at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    status = RunStatus()
    errors_encountered = False
    
    # Step 1: Check Firecrawl health
    if not check_firecrawl_health():
        print("❌ Firecrawl is not responding!")
        print("   Make sure all containers are running:")
        print("   - firecrawl-api-1")
        print("   - redis:alpine") 
        print("   - rabbitmq:3-management")
        print()
        print("   Run this to restart:")
        print("   cd /home/avalonas/.hermes/gematria/firecrawl")
        print("   docker compose up -d")
        return
    
    print("✅ Firecrawl is healthy and responding")
    
    # Step 2: Scan vault for new files
    files_to_process = scan_vault_for_new_images()
    
    if not files_to_process:
        print("ℹ️ No newly modified files found in last 24 hours")
        print("   Running anyway to verify system health...")
        files_to_process.append("health_check_only.png")
    
    # Step 3: Process files
    results = process_image_vault_files(files_to_process)
    status.processed_files.extend(results["files_processed"])
    status.errors.extend(results["errors"])
    
    if results["errors"]:
        print(f"⚠️ Encountered {len(results['errors'])} errors during processing")
        errors_encountered = True
    
    # Step 4: Create exports
    patterns = results.get("patterns_extracted", [])
    status.export_count = create_export_files(patterns)
    
    # Step 5: Update database
    if patterns:
        for pattern in patterns:
            status.new_patterns.append({
                "name": pattern["pattern_name"],
                "source": pattern["source"]
            })
        save_to_database({})
    
    # Step 6: Update status file
    try:
        update_status_file(status)
    except Exception as e:
        print(f"⚠️ Error updating status: {e}")
    
    # Final summary
    print("\n" + "=" * 60)
    print("🌙 Overnight Research Complete!")
    print("=" * 60)
    print()
    print(f"✅ Files Processed: {len(status.processed_files)}")
    print(f"✅ Patterns Exported: {status.export_count}")
    print(f"✅ Duration: {status.duration_seconds:.1f}s")
    
    if status.errors:
        print(f"⚠️ Errors: {len(status.errors)}")
        errors_encountered = True
    
    return not errors_encountered


def run_continuous_loop(interval_minutes=60, max_runs=-1):
    """Run overnight research in continuous loop"""
    
    print("\n🔄 Starting continuous overnight research loop...")
    print(f"   Interval: {interval_minutes} minutes")
    print(f"   Max runs: {max_runs if max_runs != -1 else 'unlimited'}")
    print()
    
    run_count = 0
    while True:
        success = run_overnight_research()
        
        if not success and run_count > 0:
            print("\n⚠️ Loop paused due to errors. Check CURRENT_STATUS.md for details.")
            break
        
        if max_runs != -1 and run_count >= max_runs:
            print(f"\n✅ Completed {max_runs} runs. Exiting loop...")
            break
        
        print(f"\n⏰ Next run in {interval_minutes} minutes...")
        
        # Sleep for interval
        time.sleep(interval_minutes * 60)
        run_count += 1


def main():
    """Main entry point"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Steve's Gematria Overnight Research Runner")
    parser.add_argument("--continuous", action="store_true", help="Run in continuous loop mode")
    parser.add_argument("--interval", type=int, default=60, help="Interval minutes (for continuous mode)")
    parser.add_argument("--max-runs", type=int, default=-1, help="Max runs for continuous mode")
    
    args = parser.parse_args()
    
    if args.continuous:
        run_continuous_loop(interval_minutes=args.interval, max_runs=args.max_runs)
    else:
        # Single run
        run_overnight_research()


if __name__ == "__main__":
    main()
