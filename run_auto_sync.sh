#!/bin/bash
# Auto-Obsidian Sync Runner Script
# Add this to crontab OR run manually anytime

cd /home/avalonas/.hermes/gematria
python scripts/auto_obisidian_sync_v2.py >> logs/auto_obsidian_sync.log 2>&1

echo "✅ Auto-sync completed at $(date)"
