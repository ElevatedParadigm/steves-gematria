#!/usr/bin/env bash
# =========================================================
# 🔄 Gematria Overnight Research Loop - Cron Installation Script
# =========================================================
# Creates scheduled overnight research loop with auto-restart capability
# 
# Schedule: Every 3 hours at :00 minute (hours 0,3,6,9,12,15,18,21 UTC)
# Logs to: /home/avalonas/.hermes/gematria/cron_logs/
# Script: /home/avalonas/.hermes/gematria/scripts/loop_runner_enhanced.py
# =========================================================

set -euo pipefail

GEMATRIA_DIR="${GEMATRIA_DIR:-/home/avalonas/.hermes/gematria}"
LOGS_DIR="$GEMATRIA_DIR/cron_logs"
CRON_CONFIG="$GEMATRIA_DIR/cron_job_config.txt"
SCRIPTS_DIR="$GEMATRIA_DIR/scripts"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "============================================================"
echo "🔄 Gematria Overnight Research Loop - Cron Installer"
echo "============================================================"

# Check if directory exists
if [ ! -d "$GEMATRIA_DIR" ]; then
    echo -e "${RED}❌ Error: Gematria directory not found at $GEMATRIA_DIR${NC}"
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p "$LOGS_DIR"

# Verify required scripts exist
echo ""
echo "🔍 Verifying required scripts..."
echo "============================================================"

REQUIRED_SCRIPTS=(
    "$SCRIPTS_DIR/loop_runner_enhanced.py"
    "$SCRIPTS_DIR/stability_test_enhanced_fixed.py"
    "$SCRIPTS_DIR/auto_obisidian_sync_v2.py"
)

ALL_EXIST=true
for script in "${REQUIRED_SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        size=$(stat -c%s "$script" 2>/dev/null || stat -f%z "$script" 2>/dev/null)
        echo -e "  ${GREEN}✅${NC} $script ($((size / 1024))KB)"
    else
        echo -e "  ${RED}❌${NC} $script (MISSING)"
        ALL_EXIST=false
    fi
done

if [ "$ALL_EXIST" = false ]; then
    echo ""
    echo -e "${YELLOW}⚠️  Some required scripts are missing.${NC}"
    echo "Run the installation script or create them manually."
    exit 1
fi

# Check if hybrid_scheduler.py exists (creates it if not)
if [ ! -f "$SCRIPTS_DIR/hybrid_scheduler.py" ]; then
    echo ""
    echo "📄 Creating hybrid_scheduler.py for elasticity monitoring..."
    
    cat > "$SCRIPTS_DIR/hybrid_scheduler.py" << 'HERMITEOF'
#!/usr/bin/env python3
"""
🔄 Hybrid Scheduler - Multi-Phase Elasticity Monitoring
=========================================================

Provides elasticity phase rotation (baseline/speed_up/slow_down/intensify)
across different timezones for overnight research operations.

Usage:
    python3 hybrid_scheduler.py [--interval N] [--domain DOMAIN_NAME]
    
Default interval: 1800 seconds (30 minutes)
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path.home()))

class HybridScheduler:
    """Elasticity scheduler for multi-phase research operations"""
    
    def __init__(self):
        self.config_path = Path.home() / ".hermes" / "gematria" / "config.yaml"
        self.state_file = Path.home() / ".hermes" / "gematria" / "elasticity_state.json"
        
    def load_config(self):
        """Load elasticity configuration from config.yaml"""
        if not self.config_path.exists():
            return {}
        
        with open(self.config_path, 'r') as f:
            content = f.read()
        
        # Simple YAML parsing
        config = {
            "elasticity_rules": {},
            "domains": {},
            "phases": {}
        }
        
        in_section = None
        
        for line in content.split('\n'):
            line = line.rstrip()
            
            if line.strip().startswith('#') or not line.strip():
                continue
            
            if ':' in line:
                key_parts = line.split(':', 1)
                key = key_parts[0].strip()
                value = key_parts[1].strip() if len(key_parts) > 1 else ''
                
                if key in ['elasticity_rules', 'domains', 'phases']:
                    in_section = key
                    continue
                
                elif not in_section:
                    config['domains'][key.rstrip('/')] = {}
        
        return config
    
    def load_state(self):
        """Load last known state"""
        if not self.state_file.exists():
            return {"current_phase": "baseline"}
        
        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except:
            return {"current_phase": "baseline"}
    
    def print_status(self):
        """Print current elasticity phase with status markers"""
        
        now = datetime.utcnow()
        state = self.load_state()
        config = self.load_config()
        
        # Get observer mapping from config
        phase = "baseline"
        if 'domains' in config:
            for dname, domain_info in config['domains'].items():
                if 'phase_rotation_schedule' in domain_info:
                    schedule = domain_info.get("phase_rotation_schedule", {})
                    
                    eest_hour = now.astimezone('Europe/EEST').hour
                    est_hour = now.astimezone('America/EST').hour
                    
                    if schedule.get("speed_up_observer", "null") != "null":
                        if eest_hour in range(8, 18):
                            phase = "speed_up"
                            
                    elif schedule.get("slow_down_observer", "null") != "null":
                        if est_hour in range(4, 12):
                            phase = "slow_down"
        
        # Update state
        state["current_phase"] = phase
        state["last_change"] = now.strftime('%Y-%m-%d %H:%M:%S')
        
        self.save_state(state)
        
        # Determine phase emoji and description
        phase_info = {
            "baseline": ("⏱️", "BASELINE - Standard operations at normal pace"),
            "speed_up": ("🚀", "SPEED UP - +20% faster, larger batches enabled"),
            "slow_down": ("🐢", "SLOW DOWN - -15% slower, focused verification mode"),
            "intensify": ("⚡", "INTENSIFY - Deep analysis with parallel depth")
        }
        
        emoji, description = phase_info.get(phase, ("📊", f"PHASE: {phase}"))
        
        print(f"\n{'='*50}")
        print("🔄 HYBRID SCHEDULER STATUS")
        print(f"{'='*50}")
        print(f"\nCurrent Elasticity Phase: [{emoji}] {phase.upper()}")
        print(f"\n{description}")
        
        now_str = now.strftime('%Y-%m-%d %H:%M:%S UTC')
        print(f"\nTimestamp: {now_str}")
        
        print(f"\n{'='*50}\n")
    
    def save_state(self, state):
        """Save scheduler state for phase continuity"""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)


def main():
    """Main entry point"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Hybrid Scheduler for Elasticity Monitoring")
    parser.add_argument('--interval', type=int, default=1800, help='Check interval in seconds')
    parser.add_argument('--domain', type=str, default=None, help='Specific domain to check phase for')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    
    args = parser.parse_args()
    
    scheduler = HybridScheduler()
    
    if args.once:
        scheduler.print_status()
    else:
        print("🔄 Hybrid Scheduler started")
        print(f"   Interval: {args.interval} seconds")
        print(f"   Domain: {args.domain or 'All domains'}\n")
        
        last_check = datetime.now()
        
        try:
            while True:
                scheduler.print_status()
                
                state = scheduler.load_state()
                state["last_check"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                scheduler.save_state(state)
                
                if not args.once:
                    time.sleep(args.interval)
                    
        except KeyboardInterrupt:
            print("\n👋 Scheduler stopped by user")


if __name__ == "__main__":
    main()
HERMITEOF
    
    echo -e "  ${GREEN}✅${NC} Created hybrid_scheduler.py"
fi

echo ""
echo "📝 Checking existing cron configuration..."
echo "============================================================"

# Check if we can run crontab -v (for user-specific cron)
if command -v crontab &> /dev/null; then
    echo -e "${GREEN}✅${NC} crontab command available"
    
    # Try to read existing crontab
    if [ "$(crontab -l 2>/dev/null || true)" != "" ]; then
        echo -e "   Existing crontab entries found"
    else
        echo -e "   ${YELLOW}⚠️${NC} No existing crontab entries"
    fi
    
    # Write the cron job to a config file for manual review
    cat > "$CRON_CONFIG" << 'CRONEOF'
# Gematria Overnight Research Loop - Cron Job Configuration
# =========================================================
# Schedule: Every 3 hours at :00 minute (hours 0,3,6,9,12,15,18,21 UTC)
# =========================================================

# CRON JOB LINE (add this to crontab with: crontab -e)
0 0,3,6,9,12,15,18,21 * * * cd /home/avalonas/.hermes/gematria && python scripts/loop_runner_enhanced.py >> cron_logs/cron_job.log 2>&1

# Alternative: Add this entire block to crontab
CRONEOF
    
    echo -e "  ${GREEN}✅${NC} Cron configuration written to $CRON_CONFIG"
else
    echo -e "${YELLOW}⚠️${NC} crontab command not found - manual installation required"
fi

echo ""
echo "🔧 Verifying log directory permissions..."
echo "============================================================"

if [ -w "$LOGS_DIR" ]; then
    echo -e "  ${GREEN}✅${NC} Log directory is writable"
else
    echo -e "${RED}❌${NC} Log directory is not writable (fix permissions)"
fi

echo ""
echo "📋 Phase Marker Format Example:"
echo "============================================================"
cat << 'MARKEREOF'
[2026-05-01 03:00:00 UTC] === PHASE: STABILITY_TEST ===
   → Action: Running enhanced stability test on database
   → Timestamp: 2026-05-01 03:00:00 UTC

[2026-05-01 03:03:00 UTC] === PHASE: AUTO_SYNC ===
   → Action: Relationship matrices and cross-references exported to Obsidian
   → Timestamp: 2026-05-01 03:03:00 UTC

[2026-05-01 03:04:00 UTC] === PHASE: HEATMAP_GENERATION ===
   → Action: Correlation heatmaps and relationship matrices generated
   → Timestamp: 2026-05-01 03:04:00 UTC

[2026-05-01 03:05:00 UTC] === PHASE: HYBRID_SCHEDULER ===
   → Action: Elasticity phase rotation active - current phase: baseline
   → Timestamp: 2026-05-01 03:05:00 UTC
MARKEREOF

echo ""
echo "============================================================"
echo "🎯 Cron Installation Complete!"
echo "============================================================"
echo ""
echo "To activate the cron job, add this line to your crontab:"
echo ""
echo '   0 0,3,6,9,12,15,18,21 * * * cd /home/avalonas/.hermes/gematria && python scripts/loop_runner_enhanced.py >> cron_logs/cron_job.log 2>&1'
echo ""
echo "Edit crontab with: crontab -e"
echo "============================================================"
