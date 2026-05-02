#!/usr/bin/env python3
"""
Quick Telegram Webhook Test - Simulate overnight research completion
Usage: python scripts/test_webhook_delivery.py
"""

import json
from pathlib import Path
from datetime import datetime, timezone

def simulate_overnight_analysis():
    """Simulate completed overnight analysis for testing"""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "urls_scanned": 24,
        "success_count": 16,
        "failed_count": 8,
        "symbols_detected": ["124", "55", "666", "963"],
        "elemental_domains": ["fire", "earth", "air", "water"],
        "core_symbols_found": ["124", "963", "55", "666"],
        "database_entry_id": "TEST_SIMULATION_20260426"
    }

def format_test_message(analysis):
    """Format test message"""
    timestamp = analysis["timestamp"][:19].replace("T", " ")
    symbols_str = ", ".join(f"🔢 {s}" for s in analysis["symbols_detected"])
    elements_str = " | ".join(e.capitalize() for e in analysis["elemental_domains"])
    
    return f"""🌙 OVERNIGHT RESEARCH COMPLETE

━━━━━━━━━━━━━━━━━━━━━━
**Time:** {timestamp}
━━━━━━━━━━━━━━━━━━━━━━

🔍 **URLs Scanned:** {analysis['urls_scanned']}
✅ **Successful:** {analysis['success_count']}
❌ **Failed:** {analysis['failed_count']}

━━━━━━━━━━━━━━━━━━━━━━
🔢 **Symbols Detected:**
{symbols_str}

━━━━━━━━━━━━━━━━━━━━━━
🌐 **Elemental Domains:**
{elements_str}

━━━━━━━━━━━━━━━━━━━━━━
💾 Database ID: {analysis['database_entry_id']}
━━━━━━━━━━━━━━━━━━━━━━

*Test delivery complete.*"""

def main():
    """Run test webhook delivery"""
    print("=" * 60)
    print("🧪 TELEGRAM WEBHOOK DELIVERY TEST")
    print("=" * 60)
    
    # Simulate overnight analysis
    analysis = simulate_overnight_analysis()
    
    print(f"\n📊 Testing with simulated analysis:")
    print(f"   Database ID: {analysis['database_entry_id']}")
    print(f"   Symbols: {', '.join(analysis['symbols_detected'])}")
    print(f"   Elements: {', '.join(analysis['elemental_domains'])}")
    
    # Format message
    test_message = format_test_message(analysis)
    
    print("\n" + "=" * 60)
    print("📤 TEST MESSAGE CONTENT:")
    print("=" * 60)
    print(test_message)
    print("=" * 60)
    
    print(f"\n✅ Test complete! Message formatted for Telegram delivery.")
    print("\nTo actually send, configure TELEGRAM_WEBHOOK_URL in config")
    print("Then run: python scripts/webhook_sender.py")

if __name__ == "__main__":
    main()
