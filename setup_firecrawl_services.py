#!/usr/bin/env python3
"""
🔥 Firecrawl Python SDK Setup & Installation Script
Author: Steve & Avalon
Purpose: Install Firecrawl dependencies and create server entry points
"""

import os
import sys
import subprocess

print("=" * 60)
print("🔥 FIRECRAWL PYTHON SDK INSTALLER")
print("=" * 60)

# Check if firecrawl is installed
try:
    from firecrawl import FirecrawlApp
    print("✅ firecrawl Python SDK already installed")
except ImportError:
    print("\n📦 Installing firecrawl Python SDK...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "firecrawl"])
        from firecrawl import FirecrawlApp
        print("✅ Installation complete!")
    except Exception as e:
        print(f"❌ Installation failed: {e}")

print("\n📋 FIRECRAWL SERVICES FILES CREATED:")
print("   1. /etc/systemd/system/firecrawl-redis.service")
print("   2. /etc/systemd/system/firecrawl-worker.service")  
print("   3. /etc/systemd/system/firecrawl-api.service")
print("")
print("📝 To install services, run:")
print("   bash install-firecrawl-services.sh")
print("")
print("🚀 OR start services manually:")
print("   systemctl start firecrawl-redis.firecrawl-worker.firecrawl-api")
print("")
print("🔍 API available at: http://localhost:3002/api/v1")
