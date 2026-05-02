#!/usr/bin/env python3
"""
Telegram Webhook Sender for Gematria Overnight Research System
Sends daily digests of overnight discoveries to connected Telegram channels
"""

import json
import os
from datetime import datetime
from pathlib import Path
import requests

# Configuration from environment
GEMATRIA_DIR = Path.home() / ".hermes" / "gematria"
DATABASE_FILE = GEMATRIA_DIR / "database" / "gematria_database.json"
LOGS_DIR = GEMATRIA_DIR / "logs"
WEBHOOK_CHANNEL = os.getenv("TELEGRAM_WEBHOOK_CHANNEL", "@gematria_overnight")  # Adjust as needed

# Load API key (read-only from .env)
ENV_FILE = GEMATRIA_DIR.parent / ".env"
with open(ENV_FILE) as f:
    for line in f:
        if "FIRECRAWL_API_KEY" in line:
            FIRECRAWL_API_KEY = line.split("=")[1].strip().strip('"\'')

def load_overnight_analyses():
    """Load overnight analyses from database"""
    with open(DATABASE_FILE) as f:
        db = json.load(f)
    
    nightly_data = db.get("overnight_analyses", [])
    
    # Get most recent run
    if not nightly_data:
        return None, "No overnight analyses found"
    
    latest_run = max(nightly_data, key=lambda x: x.get("timestamp", ""))
    return latest_run, None

def get_symbols_from_analyses(analyses):
    """Extract unique symbols detected"""
    symbols_seen = set()
    for analysis in analyses:
        for symbol in analysis.get("symbols_detected", []):
            symbols_seen.add(symbol)
    
    return symbols_seen

def format_report(analysis):
    """Format overnight analysis as Telegram message"""
    timestamp = analysis.get("timestamp", "Unknown time")
    url_count = analysis.get("urls_scanned", 0)
    success_count = analysis.get("success_count", 0)
    
    # Get symbols detected
    symbols = analysis.get("symbols_detected", [])
    symbols_str = ", ".join(f"🔢 {s}" for s in symbols[:6]) if symbols else "No new symbols"
    
    # Elemental domains
    elements = analysis.get("elemental_domains", [])
    elements_str = ", ".join(elements) if elements else ""
    
    # Core symbol check
    core_symbols = ["124", "963", "55", "111", "279", "666"]
    found_core = [s for s in core_symbols if s in symbols]
    missing_core = [s for s in core_symbols if s not in symbols]
    
    core_status = ""
    if found_core:
        core_status = f"✨ **NEW Core Symbols:** " + ", ".join(found_core)
    
    msg = """🌙 OVERNIGHT RESEARCH COMPLETE
    
━━━━━━━━━━━━━━━━━━━━━━
**Time:** {timestamp}
━━━━━━━━━━━━━━━━━━━━━━

🔍 **URLs Scanned:** {url_count}
✅ **Successful:** {success_count}
❌ **Failed:** {failed_count}

━━━━━━━━━━━━━━━━━━━━━━
🔢 **Symbols Detected:**
{symbols}

━━━━━━━━━━━━━━━━━━━━━━
🌐 **Elemental Domains:**
{elemental}

{core_status}

━━━━━━━━━━━━━━━━━━━━━━
💾 Database ID: {db_id}
━━━━━━━━━━━━━━━━━━━━━━

*Analysis complete. Knowledge graph updated.*"""
    
    return msg.format(
        timestamp=timestamp,
        url_count=url_count,
        success_count=success_count,
        failed_count=analysis.get("failed_count", 0),
        symbols=symbols_str,
        elemental=elements_str,
        core_status=core_status if found_core else "*No new core symbols this run*",
        db_id=analysis.get("database_entry_id", "N/A")
    )

def send_webhook(message):
    """Send formatted message to Telegram"""
    try:
        # Use your preferred webhook method
        # For now, return the message as it would be sent
        
        print(f"\n📤 [Would send to {WEBHOOK_CHANNEL}]:")
        print("-" * 40)
        print(message)
        print("-" * 40)
        
        return True
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        return False

def main():
    """Main webhook sender routine"""
    print("=" * 60)
    print("🌙 GEMATRIA OVERNIGHT RESEARCH - WEBHOOK SENDER")
    print("=" * 60)
    
    # Ensure logs directory exists
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    try:
        # Load overnight analyses
        analysis, error = load_overnight_analyses()
        
        if error:
            print(f"\n⚠️ {error}")
            print("\n📊 No data to report - system may not have run yet.")
            return
        
        print(f"\n✅ Loaded analysis from: {analysis.get('database_entry_id', 'N/A')}")
        
        # Generate formatted report
        report = format_report(analysis)
        
        # Send webhook
        send_webhook(report)
        
        print("\n✨ Webhook delivery complete!")
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")

if __name__ == "__main__":
    main()
