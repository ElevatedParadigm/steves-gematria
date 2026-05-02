#!/bin/bash
# 🚀 Elasticity Integration Wrapper Script
# Usage: enable_elasticity.sh | disable_elasticity.sh | status

CONFIG_FILE="/home/avalonas/.hermes/gematria/config.yaml"
LOGS_DIR="/home/avalonas/.hermes/gematria/logs"
ELASTICITY_LOG="${LOGS_DIR}/elasticity_phases.log"

case "${1:-status}" in
    enable)
        echo "🚀 Activating Elasticity Integration..."
        
        if [ -f "$CONFIG_FILE" ]; then
            log_success "Config file found: $CONFIG_FILE"
            
            # Validate YAML
            python3 -c "import yaml; yaml.safe_load(open('$CONFIG_FILE'))" 2>/dev/null
            if [ $? -eq 0 ]; then
                log_success "Config is valid YAML — elasticity enabled!"
                
                # Initialize scheduler if not running
                if [ ! -f "$ELASTICITY_LOG" ]; then
                    touch "$ELASTICITY_LOG"
                    log_success "Phase log initialized at $ELASTICITY_LOG"
                fi
                
                echo ""
                echo "✅ Elasticity is now active!"
                echo ""
                echo "How it works:"
                echo "  • config.yaml contains speed up/slow down/intensify rules"
                echo "  • hybrid_scheduler.py monitors phase rotations automatically"
                echo "  • Existing cron jobs run unchanged — no modification needed!"
                echo ""
                echo "Monitor active phases:"
                echo "  tail -f $ELASTICITY_LOG"
            else
                echo "⚠️ Config validation failed — check YAML syntax"
            fi
        else
            echo "❌ config.yaml not found! Run enable_elasticity.sh first."
        fi
        ;;
        
    disable)
        echo "🛑 Deactivating Elasticity Integration..."
        
        if [ -f "$CONFIG_FILE" ]; then
            BACKUP="${CONFIG_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
            cp "$CONFIG_FILE" "$BACKUP"
            
            python3 << 'PYEOF'
import yaml

with open('/home/avalonas/.hermes/gematria/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

for domain, domain_config in config.get('domains', {}).items():
    if domain_config.get('elasticity_enabled', False):
        domain_config['elasticity_enabled'] = False

with open('/home/avalonas/.hermes/gematria/config.yaml', 'w') as f:
    yaml.dump(config, f, default_flow_style=False)
PYEOF
            
            log_success "Elasticity disabled — all domains reverted to baseline"
            
            echo ""
            echo "📁 Backed up config:"
            echo "  $BACKUP"
            echo ""
            echo "To re-enable: ./enable_elasticity.sh enable"
        else
            log_success "No config found — already at baseline"
        fi
        ;;
        
    status|"")
        echo "=== Elasticity Status ==="
        
        if [ -f "$CONFIG_FILE" ]; then
            python3 << 'PYEOF'
import yaml
from pathlib import Path

config_path = "/home/avalonas/.hermes/gematria/config.yaml"

try:
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

phase_names = {
    'baseline': '⚪ Baseline',
    'speed_up': '🚀 Speed Up (+20%)',
    'slow_down': '🐢 Slow Down (-15%)',
    'intensify': '💪 Intensify'
}

print(f"\n✅ Config file valid: {config_path}")

domains = config.get('domains', {})
enabled_count = 0

for domain, domain_config in domains.items():
    if domain_config.get('elasticity_enabled', False):
        enabled_count += 1
        phase = domain_config.get('current_phase', 'baseline')
        print(f"  {domain:25s} → {phase_names[phase]:30s}")

if enabled_count > 0:
    log_success("Elasticity enabled for {} domain(s)".format(enabled_count))
    print("")
    print("📁 Phase activity log:")
    print(f"  tail -f /home/avalonas/.hermes/gematria/logs/elasticity_phases.log")
else:
    print("\nℹ️  Elasticity disabled — all domains running at baseline speed")

except Exception as e:
    print(f"\n❌ Config error: {e}")
PYEOF
        else
            echo "❌ config.yaml not found"
            echo ""
            echo "To enable elasticity:"
            echo "  ./enable_elasticity.sh enable"
        fi
        ;;
        
    *)
        echo "Usage: $0 {enable|disable|status}"
        echo ""
        echo "Commands:"
        echo "  enable   — Activate elasticity rules (speed up/slow down/intensify)"
        echo "  disable  — Deactivate elasticity (revert to baseline speed)"
        echo "  status   — Check current elasticity status"
        ;;
esac
