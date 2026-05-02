#!/bin/bash
# STEVE'S GEMATRIA — MANUAL CRON ALTERNATIVES (Simplified Version)
# ============================================

# Paths and configurations
GEMATRIA_DIR="/home/avalonas/.hermes/gematria"
LOG_DIR="$GEMATRIA_DIR/cron_logs"

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# ============================================
# OVERNIGHT RESEARCH PIPELINE
# ============================================
run_overnight_research() {
    cd "$GEMATRIA_DIR" || return
    
    echo "=== Overnight Research Pipeline ==="
    echo "Started at: $(date '+%Y-%m-%d %H:%M:%S')"
    python scripts/orchestrator.py --mode overnight 2>&1 | tee "$LOG_DIR/overnight_$(date +\%Y\%m\%d).log"
    
    if [ $? -eq 0 ]; then
        echo "✅ Overnight research completed successfully!"
    else
        echo "❌ Overnight research pipeline failed!"
    fi
    echo ""
}

# ============================================
# HOURLY RELATIONSHIP SYNC
# ============================================
run_hourly_sync() {
    cd "$GEMATRIA_DIR" || return
    
    echo "=== Hourly Relationship Sync ==="
    echo "Started at: $(date '+%Y-%m-%d %H:%M:%S')"
    python scripts/auto_obisidian_sync_v2.py 2>&1 >> "$LOG_DIR/hourly_sync.log"
    
    if [ $? -eq 0 ]; then
        echo "✅ Hourly sync completed!"
        
        # Show latest file count in obsidian_exports
        if [ -d "$GEMATRIA_DIR/obsidian_exports" ]; then
            FILE_COUNT=$(ls -1 "$GEMATRIA_DIR/obsidian_exports"/*.md 2>/dev/null | wc -l)
            echo "📂 Current exports: $FILE_COUNT files in obsidian_exports"
        fi
    else
        echo "❌ Hourly sync failed!"
    fi
    echo ""
}

# ============================================
# PATTERN CONVERGENCE SCAN (Every 6 Hours)
# ============================================
run_pattern_scan() {
    cd "$GEMATRIA_DIR" || return
    
    echo "=== Pattern Convergence Scan ==="
    echo "Started at: $(date '+%Y-%m-%d %H:%M:%S')"
    python scripts/auto_obisidian_sync_v2.py --mode convergence 2>&1 >> "$LOG_DIR/pattern_scan.log"
    
    if [ $? -eq 0 ]; then
        echo "✅ Pattern scan completed!"
        
        # Show relationships tracked if available
        if [ -f "$GEMATRIA_DIR/obsidian_exports/RELATIONSHIP_MATRIX.md" ]; then
            LINE_COUNT=$(grep -c "🔗" "$GEMATRIA_DIR/obsidian_exports/RELATIONSHIP_MATRIX.md" 2>/dev/null || echo "0")
            echo "📊 Relationships tracked: $LINE_COUNT"
        fi
    else
        echo "❌ Pattern scan failed!"
    fi
    echo ""
}

# ============================================
# SYSTEM HEALTH CHECK
# ============================================
check_system_health() {
    cd "$GEMATRIA_DIR" || return
    
    echo "=== System Health Check ==="
    echo "Started at: $(date '+%Y-%m-%d %H:%M:%S')"
    python scripts/health_check.py 2>&1 >> "$LOG_DIR/health_check.log"
    
    if [ $? -eq 0 ]; then
        echo "✅ System health check passed!"
    else
        echo "⚠️  System health check completed with warnings"
    fi
    echo ""
}

# ============================================
# DISPLAY AVAILABLE TASKS
# ============================================
list_available_tasks() {
    cat << 'EOF'
Available Multi-Agent Tasks:

   overnight  — Full overnight research pipeline (3 AM equivalent)
   hourly     — Hourly relationship tracking sync  
   pattern    — Every 6 hours pattern convergence scan
   health     — System integrity health check

Usage examples:
   bash scripts/cron_alternatives.sh overnight
   bash scripts/cron_alternatives.sh hourly
   bash scripts/cron_alternatives.sh pattern
   bash scripts/cron_alternatives.sh health
EOF
}

# ============================================
# MAIN ENTRY POINT
# ============================================
case "${1:-}" in
    overnight) run_overnight_research ;;
    hourly) run_hourly_sync ;;
    pattern) run_pattern_scan ;;
    health) check_system_health ;;
    list|"") list_available_tasks ;;
    *) echo "Usage: $0 [overnight|hourly|pattern|health]" ;;
esac
