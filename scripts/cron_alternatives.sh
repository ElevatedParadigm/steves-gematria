#!/bin/bash
# ============================================
# STEVE'S GEMATRIA - MANUAL CRON ALTERNATIVES
# Source this file into your shell config (~/.bashrc or ~/.zshrc)
# ============================================

# Color codes for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Base directory
GEMATRIA_DIR="/home/avalonas/.hermes/gematria"

# ============================================
# OVERNIGHT RESEARCH PIPELINE
# ============================================
run_overnight_research() {
    cd "$GEMATRIA_DIR" 2>/dev/null || { echo -e "${RED}❌ Must be in gematria directory${NC}"; return 1; }
    
    echo -e "\n${CYAN}${'=' * 70}${NC}"
    echo -e "${BLUE}🌙 STEVE'S GEMATRIA — Overnight Research Pipeline${NC}"
    echo -e "Started at: $(date '+%Y-%m-%d %H:%M:%S')${NC}"
    echo -e "${'=' * 70}${NC}\n"
    
    python scripts/orchestrator.py --mode overnight 2>&1 | tee cron_logs/overnight_$(date +\%Y\%m\%d).log
    
    if [ $? -eq 0 ]; then
        echo -e "\n${GREEN}✅ Overnight research completed successfully!${NC}"
        echo -e "📊 Logs saved to: ${GEMATRIA_DIR}/cron_logs/overnight_$(date +\%Y\%m\%d).log${NC}"
    else
        echo -e "\n${RED}❌ Overnight research pipeline failed!${NC}"
    fi
    
    echo -e "${'=' * 70}\n"
}

# ============================================
# HOURLY RELATIONSHIP SYNC
# ============================================
run_hourly_sync() {
    cd "$GEMATRIA_DIR" 2>/dev/null || { echo -e "${RED}❌ Must be in gematria directory${NC}"; return 1; }
    
    echo -e "\n${CYAN}${'=' * 70}${NC}"
    echo -e "${BLUE}🕐 STEVE'S GEMATRIA — Hourly Relationship Sync${NC}"
    echo -e "Started at: $(date '+%Y-%m-%d %H:%M:%S')${NC}"
    echo -e "${'=' * 70}${NC}\n"
    
    python scripts/auto_obisidian_sync_v2.py 2>&1 >> cron_logs/hourly_sync.log
    
    if [ $? -eq 0 ]; then
        echo -e "\n${GREEN}✅ Hourly sync completed!${NC}"
        echo -e "📊 Logs saved to: ${GEMATRIA_DIR}/cron_logs/hourly_sync.log${NC}"
        
        # Show latest file count in obsidian_exports
        if [ -d "$GEMATRIA_DIR/obsidian_exports" ]; then
            FILE_COUNT=$(ls -1 "$GEMATRIA_DIR/obsidian_exports"/*.md 2>/dev/null | wc -l)
            echo -e "${CYAN}📂 Current exports: $FILE_COUNT files in obsidian_exports/${NC}"
        fi
    else
        echo -e "\n${RED}❌ Hourly sync failed!${NC}"
    fi
    
    echo -e "${'=' * 70}\n"
}

# ============================================
# PATTERN CONVERGENCE SCAN (Every 6 Hours)
# ============================================
run_pattern_scan() {
    cd "$GEMATRIA_DIR" 2>/dev/null || { echo -e "${RED}❌ Must be in gematria directory${NC}"; return 1; }
    
    echo -e "\n${CYAN}${'=' * 70}${NC}"
    echo -e "${BLUE}🔍 STEVE'S GEMATRIA — Pattern Convergence Scan${NC}"
    echo -e "Started at: $(date '+%Y-%m-%d %H:%M:%S')${NC}"
    echo -e "${'=' * 70}${NC}\n"
    
    python scripts/auto_obisidian_sync_v2.py --mode convergence 2>&1 >> cron_logs/pattern_scan.log
    
    if [ $? -eq 0 ]; then
        echo -e "\n${GREEN}✅ Pattern scan completed!${NC}"
        echo -e "📊 Logs saved to: ${GEMATRIA_DIR}/cron_logs/pattern_scan.log${NC}"
        
        # Show top correlations from relationship matrix if available
        if [ -f "$GEMATRIA_DIR/obsidian_exports/RELATIONSHIP_MATRIX.md" ]; then
            LINE_COUNT=$(grep -c "🔗" "$GEMATRIA_DIR/obsidian_exports/RELATIONSHIP_MATRIX.md" 2>/dev/null || echo "0")
            echo -e "${CYAN}📊 Relationships tracked: $LINE_COUNT${NC}"
        fi
    else
        echo -e "\n${RED}❌ Pattern scan failed!${NC}"
    fi
    
    echo -e "${'=' * 70}\n"
}

# ============================================
# SYSTEM HEALTH CHECK
# ============================================
check_system_health() {
    cd "$GEMATRIA_DIR" 2>/dev/null || { echo -e "${RED}❌ Must be in gematria directory${NC}"; return 1; }
    
    echo -e "\n${CYAN}${'=' * 70}${NC}"
    echo -e "${BLUE}💚 STEVE'S GEMATRIA — System Health Check${NC}"
    echo -e "Started at: $(date '+%Y-%m-%d %H:%M:%S')${NC}"
    echo -e "${'=' * 70}${NC}\n"
    
    python scripts/health_check.py 2>&1 >> cron_logs/health_check.log
    
    if [ $? -eq 0 ]; then
        echo -e "\n${GREEN}✅ System health check passed!${NC}"
        echo -e "📊 Logs saved to: ${GEMATRIA_DIR}/cron_logs/health_check.log${NC}"
    else
        echo -e "\n${RED}⚠️  System health check completed with warnings.${NC}"
        echo -e "📊 Logs saved to: ${GEMATRIA_DIR}/cron_logs/health_check.log${NC}"
    fi
    
    echo -e "${'=' * 70}\n"
}

# ============================================
# DISPLAY AVAILABLE TASKS
# ============================================
list_available_tasks() {
    cat << 'EOF'
📦 STEVE'S GEMATRIA — Available Multi-Agent Tasks
==================================================

   run_overnight_research — Full overnight research pipeline (3 AM equivalent)
   run_hourly_sync        — Hourly relationship tracking sync  
   run_pattern_scan       — Every 6 hours pattern convergence scan
   check_system_health    — System integrity health check

🌙 Recommended alias: Add 'alias overnight='run_overnight_research'' to your shell config

Examples:
   run_overnight_research    # Run the full pipeline
   run_hourly_sync           # Sync relationships now
   run_pattern_scan          # Scan for pattern convergence
   check_system_health       # Check system integrity

EOF
}

# ============================================
# DISPLAY VERSION/STATUS
# ============================================
show_status() {
    cd "$GEMATRIA_DIR" 2>/dev/null || return
    
    echo -e "\n${CYAN}${'=' * 70}${NC}"
    echo -e "${BLUE}📊 STEVE'S GEMATRIA — System Status${NC}"
    echo -e "Time: $(date '+%Y-%m-%d %H:%M:%S')${NC}"
    echo -e "${'=' * 70}${NC}\n"
    
    # Check Python scripts exist
    if [ -f "$GEMATRIA_DIR/scripts/orchestrator.py" ]; then
        echo -e "${GREEN}✅ orchestrator.py${NC}"
    else
        echo -e "${RED}❌ orchestrator.py${NC}"
    fi
    
    if [ -f "$GEMATRIA_DIR/scripts/auto_obisidian_sync_v2.py" ]; then
        echo -e "${GREEN}✅ auto_obisidian_sync_v2.py${NC}"
    else
        echo -e "${RED}❌ auto_obisidian_sync_v2.py${NC}"
    fi
    
    if [ -f "$GEMATRIA_DIR/scripts/health_check.py" ]; then
        echo -e "${GREEN}✅ health_check.py${NC}"
    else
        echo -e "${RED}❌ health_check.py${NC}"
    fi
    
    # Show obsidian_exports stats
    if [ -d "$GEMATRIA_DIR/obsidian_exports" ]; then
        export_count=$(ls -1 "$GEMATRIA_DIR/obsidian_exports"/*.md 2>/dev/null | wc -l)
        echo -e "\n${CYAN}📂 Export files: $export_count in obsidian_exports/${NC}"
    fi
    
    echo -e "\n${'=' * 70}\n"
}

# ============================================
# AUTO-SHOW HELPER FUNCTIONS (Optional)
# ============================================
auto_complete() {
    case "$1" in
        overnight*) echo "run_overnight_research" ;;
        hourly*) echo "run_hourly_sync" ;;
        pattern*) echo "run_pattern_scan" ;;
        health*) echo "check_system_health" ;;
        *) echo "No matching command found" ;;
    esac
}

# ============================================
# MAIN ENTRY POINT
# ============================================
case "${1:-}" in
    overnight) run_overnight_research ;;
    hourly) run_hourly_sync ;;
    pattern) run_pattern_scan ;;
    health) check_system_health ;;
    status|stats) show_status ;;
    list|help|--help|-h|"") list_available_tasks ;;
    *) echo "Usage: $0 [overnight|hourly|pattern|health|status|list]" ;;
esac
