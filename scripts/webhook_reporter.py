#!/usr/bin/env python3
"""
Telegram Webhook Integration for Gematria Research Protocol
Sends report summaries between runs automatically
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / ".hermes"))

class TelegramReporter:
    """Handles Telegram webhook reporting"""
    
    def __init__(self):
        self.telegram_token = ""
        self.chat_id = "1962224247"  # Home channel default
        
    def send_summary(self, title: str, content: str, attachments: list = None):
        """Send summary report to Telegram"""
        
        # Load config
        try:
            env_path = Path.home() / ".hermes" / ".env"
            if env_path.exists():
                with open(env_path) as f:
                    lines = f.readlines()
                    
                for line in lines:
                    if line.strip().startswith("TELEGRAM_BOT_TOKEN="):
                        self.telegram_token = line.split("=", 1)[1].strip().strip('"\'')
                        break
            
            if not self.telegram_token:
                return None
                
        except Exception as e:
            print(f"⚠️ Could not load Telegram config: {e}")
            return None
        
        # Build report message
        markdown_msg = (
            f"{title}\n\n"
            f"```{content}```"
        )
        
        if attachments and attachments[0]:
            markdown_msg += f"\n📁 *Generated Files:*\n"
            for file in attachments[0]:
                markdown_msg += f"- 📄 `{file}`\n"
            
            # Include screenshots if available
            screenshots = [f for f in attachments[0] if "screenshot" in f.lower()]
            if screenshots:
                markdown_msg += f"\n📸 *Screenshots Available:* {len(screenshots)} files\n"
        
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        
        payload = {
            "chat_id": self.chat_id,
            "text": markdown_msg,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }
        
        import requests
        try:
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                print(f"✅ Sent to Telegram: {self.chat_id}")
                return {"status": "success", "url": f"{url}?chat_id={self.chat_id}", "response": response.json()}
            else:
                print(f"❌ Telegram API error ({response.status_code}): {response.text[:200]}")
                return None
                
        except Exception as e:
            print(f"⚠️ Send failed: {e}")
            return None

# Example usage for manual reporting
if __name__ == "__main__":
    reporter = TelegramReporter()
    
    # This would be called from the loop runner
    pass
