#!/bin/bash

echo "=========================================="
echo "🧙‍♂️ STEVE'S GEMATRIA - CRON INSTALLATION"
echo "=========================================="
echo ""

# Check if crontab exists
if [ ! -z "$(crontab -l 2>/dev/null)" ]; then
    echo "📋 Current crontab content:"
    crontab -l
    echo ""
else
    echo "📝 No existing crontab found. Creating new one..."
fi

echo ""
echo "📋 Proposed cron configuration:"
cat /home/avalonas/.hermes/gematria/crontab_gematria.txt
echo ""

echo "=========================================="
echo "⏰ TO ACTIVATE - Choose One Option:  "
echo "=========================================="
echo ""
echo "Option 1: Interactive installation"
echo "----------------------------------------"
echo "Run these commands:"
echo "  1. crontab -e"
echo "  2. Paste the content from /home/avalonas/.hermes/gematria/crontab_gematria.txt"
echo "  3. Press Ctrl+D or :wq and save"
echo "     (Save as :wq in vim/nano)"
echo ""
echo "Option 2: Direct replacement (if you trust the content)"
echo "----------------------------------------"
echo "Run this command:"
echo "  cat /home/avalonas/.hermes/gematria/crontab_gematria.txt | crontab -"
echo ""

echo "=========================================="
echo "✅ AFTER ACTIVATION:  "
echo "=========================================="
echo ""
echo "📋 To check status:"
echo "  crontab -l"
echo ""
echo "📅 The system will automatically run at 4:15 AM daily."
echo "   It will scan web sources and update the database."
echo ""
echo "🔍 Recent runs are logged to:"
echo "   /home/avalonas/.hermes/gematria/cron_logs/"
echo ""
echo "=========================================="
