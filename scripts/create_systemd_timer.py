#!/usr/bin/env python3
"""Create systemd timer for overnight gematria research pipeline."""

import os
import sys

# Paths
timer_dir = "/home/avalonas/.hermes/gematria/systemd"
service_file_path = f"{timer_dir}/gematria-overnight.service"
timer_file_path = f"{timer_dir}/gematria-overnight.timer"

print("🔍 Creating systemd timer for overnight gematria research...")

# Create the systemd service unit file
service_content = """[Unit]
Description=Steve's Gematria - Overnight Research Pipeline
Documentation=https://github.com/avalonas/gematria/wiki/Architecture

[Service]
Type=oneshot
ExecStart=/home/avalonas/.hermes/venv/bin/python /home/avalonas/.hermes/gematria/scripts/orchestrator.py --mode overnight
TimeoutSec=3600
StandardOutput=syslog
StandardError=syslog
RemainAfterExit=no

[Install]
WantedBy=multi-user.target
"""

# Create the systemd timer unit file
timer_content = """[Unit]
Description=Steve's Gematria - Overnight Research Timer
Documentation=https://github.com/avalonas/gematria/wiki/Architecture

[Timer]
OnCalendar=*-*-* 03:00:00
RandomizeDelaySec=180
AccuracySec=1h
Persistent=true
Unit=gematria-overnight.service

[Install]
WantedBy=timers.target
"""

# Create directories and write files
os.makedirs(timer_dir, exist_ok=True)

print("📝 Creating service file...")
with open(service_file_path, 'w') as f:
    f.write(service_content)

print(f"✅ Service file created: {service_file_path}")

print("\n📝 Creating timer file...")
with open(timer_file_path, 'w') as f:
    f.write(timer_content)

print(f"✅ Timer file created: {timer_file_path}")

# Display the files
print("\n" + "=" * 70)
print("📄 CREATED FILES:")
print("=" * 70)

print("\n--- SERVICE FILE (gematria-overnight.service) ---")
with open(service_file_path, 'r') as f:
    print(f.read())

print("\n--- TIMER FILE (gematria-overnight.timer) ---")
with open(timer_file_path, 'r') as f:
    print(f.read())

print("=" * 70)
print("✅ Timer files created!")
print("\n📌 TO ACTIVATE (requires sudo):")
print("=" * 70)
print("""
ln -sf /home/avalonas/.hermes/gematria/systemd/gematria-overnight.service /etc/systemd/system/
ln -sf /home/avalonas/.hermes/gematria/systemd/gematria-overnight.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable gematria-overnight.timer
systemctl list-timers | grep gematria
""")
print("\n💡 This runs your overnight pipeline automatically at 3:00 AM daily.")
