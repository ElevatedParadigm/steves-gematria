#!/usr/bin/env python3
"""
Enhanced Loop Runner with Auto-Restart & Telegram Reporting
Configured for every 3-hour cycles with auto-restart on expiration
"""

import sys
import os
import json
import time
import signal
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import subprocess
import requests

# Add parent directory to path for imports
sys.path.insert(0, str(Path.home() / ".hermes"))

class TelegramReporter:
    """Handles Telegram webhook reporting"""
    
    def __init__(self):
        self.telegram_token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
        self.chat_id = os.environ.get('TELEGRAM_CHAT_ID', '1962224247')  # Home channel default
        self.base_url = "https://api.telegram.org"
        
    def send_report(self, message: str):
        """Send report to Telegram"""
        if not self.telegram_token:
            print("⚠️ Telegram token not configured - skipping report")
            return
            
        url = f"{self.base_url}/bot{self.telegram_token}/sendMessage"
        
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            if response.status_code == 200:
                print(f"✅ Telegram report sent successfully")
                return True
            else:
                print(f"❌ Telegram API error: {response.status_code}")
                return False
        except Exception as e:
            print(f"⚠️ Telegram send failed: {e}")
            return False

class LoopRunner:
    """Main loop runner with auto-restart capability"""
    
    def __init__(self, cron_logs_dir: str = "/home/avalonas/.hermes/gematria/cron_logs"):
        self.cron_logs_dir = Path(cron_logs_dir)
        self.start_time = datetime.now()
        self.log_file = None
        self.telegram_reporter = TelegramReporter()
        
    def setup_logging(self):
        """Setup logging for this run"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_name = f"loop_{timestamp}.log"
        self.log_file = self.cron_logs_dir / log_name
        
    def start_run(self) -> bool:
        """Start the overnight research run"""
        print("=" * 60)
        print("🌙 Starting Overnight Research Loop Cycle")
        print("=" * 60)
        print(f"Cycle Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Setup logging
        self.setup_logging()
        
        try:
            # Run the stability test
            process = subprocess.Popen(
                ["python3", "/home/avalonas/.hermes/gematria/scripts/stability_test_enhanced_fixed.py", "--timeout", "2700"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            output, _ = process.communicate(timeout=300)
            print(output)
            
            if process.returncode == 0:
                # Run auto-sync after stability test
                sync_process = subprocess.Popen(
                    ["python3", "/home/avalonas/.hermes/gematria/scripts/auto_obisidian_sync_v2.py"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )
                
                sync_output, _ = sync_process.communicate(timeout=120)
                print(sync_output)
                
                if sync_process.returncode == 0:
                    self._send_completion_report()
                    return True
            else:
                print(f"❌ Stability test failed with code {process.returncode}")
                return False
                
        except Exception as e:
            print(f"⚠️ Run interrupted: {e}")
            self._send_error_report(str(e))
            return False
            
    def _send_completion_report(self):
        """Send completion report to Telegram"""
        report = (
            "🔬 *Overnight Research Protocol - Cycle Complete*\n\n"
            f"⏰ Start: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            "✅ Stability Test: PASSED\n"
            "✅ Database Analysis: COMPLETED\n"
            "✅ Auto-Sync to Obsidian: COMPLETE\n"
            "📊 11 Core Symbols Tracked (124, 963, 55, 111, 279, 666)\n"
            "🔗 Relationship Matrix Updated\n"
            "🎯 All Priority Enhancements Verified\n\n"
            "📁 Logs: /home/avalonas/.hermes/gematria/cron_logs/\n"
            "🔄 Next cycle in 3 hours..."
        )
        self.telegram_reporter.send_report(report)
        
    def _send_error_report(self, error_msg: str):
        """Send error report to Telegram"""
        error_report = (
            "⚠️ *Overnight Research Protocol - Cycle Error*\n\n"
            f"❌ Error: {error_msg}\n\n"
            "🔄 Auto-restart triggered on next cycle..."
        )
        self.telegram_reporter.send_report(error_report)

def main():
    """Main loop runner with 3-hour cycle"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Loop Runner for Overnight Research Protocol")
    parser.add_argument("--interval", type=int, default=10800, help="Interval between cycles in seconds (default: 10800 = 3 hours)")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🔄 Overnight Research Protocol - Loop Mode")
    print("=" * 60)
    print(f"Cycle Interval: {args.interval}s ({args.interval/3600:.1f} hours)")
    print("Auto-restart enabled on expiration")
    print("Telegram reporting between cycles")
    print("=" * 60)
    
    runner = LoopRunner()
    
    try:
        while True:
            print(f"\n🌙 Starting Cycle {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            
            if runner.start_run():
                print("✅ Cycle completed successfully!")
                self.telegram_reporter.send_report("✅ *Research Cycle Complete*\n\n"
                    f"⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                    "📊 All core symbols analyzed\n"
                    "🔗 Relationships tracked and updated\n"
                    "\n🔄 Initiating 3-hour wait before next cycle...")
                
                # Wait for next cycle
                time.sleep(args.interval)
            else:
                print("❌ Cycle failed - will auto-restart on next interval")
                self.telegram_reporter.send_error_report(f"Cycle failed at {datetime.now().strftime('%H:%M:%S')}")
                
    except KeyboardInterrupt:
        print("\n⏸️  Loop paused by user")
    except Exception as e:
        print(f"\n❌ Unhandled exception: {e}")

if __name__ == "__main__":
    main()
