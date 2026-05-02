#!/bin/bash
# Gematria Research Loop - Runs Every 3 Hours
# Auto-restart capability and Telegram reporting

SCRIPTS_DIR="/home/avalonas/.hermes/gematria/scripts"
INTERVAL=10800  # 3 hours in seconds

echo "🔬 Starting Gematria Research Protocol Loop..."
echo "Interval: $INTERVAL seconds ($(python3 -c "print(f'{self.INTERVAL/3600:.1f}')") hours)"
echo ""

# Main loop - runs continuously
while true; do
    echo "🌙 Starting research cycle at $(date '+%Y-%m-%d %H:%M:%S')"
    
    # Run the stability test (research cycle)
    python3 "${SCRIPTS_DIR}/stability_test_enhanced_fixed.py" --timeout 2700
    
    if [ $? -eq 0 ]; then
        # Run auto-sync
        python3 "${SCRIPTS_DIR}/auto_obisidian_sync_v2.py"
        
        if [ $? -eq 0 ]; then
            echo "✅ Research cycle completed successfully!"
            
            # Send Telegram report (if configured)
            python3 /home/avalonas/.hermes/gematria/scripts/webhook_reporter.py --mode "cycle-complete" || true
            
            echo "🔄 Waiting $INTERVAL seconds before next cycle..."
        fi
    else
        echo "⚠️ Research cycle failed, will retry on next interval"
    fi
    
    echo ""
    
    # Wait for next cycle (3 hours)
    sleep "$INTERVAL"
done
