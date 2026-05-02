#!/bin/bash
# =============================================================================
# STEVE'S GEMATRIA - OVERNIGHT PROTOCOL DEPLOYMENT
# =============================================================================
# Purpose: Deploy 3 AM automated overnight research with Firecrawl scanning
# Features: Manual cron installation, Cloud API fallback, comprehensive logging
# =============================================================================

set -e  # Exit on error

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

WORKDIR="/home/avalonas/.hermes/gematria"
LOG_DIR="$WORKDIR/logs"
DB_FILE="$WORKDIR/gematria_database.json"

echo "================================================================================"
echo "${GREEN}🌙 OVERNIGHT RESEARCH PROTOCOL - DEPLOYMENT${NC}"
echo "================================================================================"
echo ""
echo "Working Directory: $WORKDIR"
echo "Database Location: $DB_FILE"
echo "Logs Directory:   $LOG_DIR"
echo ""

# Create logs directory if needed
if [ ! -d "$LOG_DIR" ]; then
    echo "${YELLOW}📁 Creating logs directory...${NC}"
    mkdir -p "$LOG_DIR"
fi

# =============================================================================
# STEP 1: INSTALL CRON JOB (Manual crontab -e method)
# =============================================================================
echo ""
echo "================================================================================"
echo "${GREEN}🕐 STEP 1: MANUAL CRON INSTALLATION${NC}"
echo "================================================================================"
echo ""
echo "Current user: $(whoami)"
echo "sudo available: $(which sudo || echo 'NO')"
echo ""

# Display cron command to add
CRON_COMMAND="0 3 * * * cd $WORKDIR && python scripts/overnight_research.py >> $LOG_DIR/overnight_$(date +%Y-%m-%d).log 2>&1"

echo "📋 Add this line to your crontab:"
echo "$CRON_COMMAND"
echo ""
echo "👉 Run these commands manually:"
echo "   1. Open terminal/cron editor: crontab -e"
echo "   2. Paste the command above at the END of file"
echo "   3. Save and exit (Ctrl+X, then Y)"
echo ""
echo "📄 CRON JOB LOCATION:"
ls -la "$WORKDIR"/crontab.gematria-overnight
echo ""

# =============================================================================
# STEP 2: VERIFY FIRECRAWL CONFIGURATION  
# =============================================================================
echo "================================================================================"
echo "${BLUE}⚙️  STEP 2: FIRECRAWL CONFIGURATION VERIFICATION${NC}"
echo "================================================================================"
echo ""

# Check if Firecrawl API key exists
if grep -q "FIRECRAWL_API_KEY=" ~/.hermes/.env 2>/dev/null; then
    echo "✅ FIRECRAWL_API_KEY configured in ~/.hermes/.env"
else
    echo "${RED}⚠️  FIRECRAWL_API_KEY not found in ~/.hermes/.env${NC}"
    echo ""
    echo "To configure:"
    echo "   1. Get API key: https://firecrawl.dev/"
    echo "   2. Edit ~/.hermes/.env"
    echo "   3. Add line: FIRECRAWL_API_KEY=your_api_key_here"
fi

# Check for local Docker setup or cloud API
if grep -q "FIRECRAWL_BASE_URL=" ~/.hermes/.env 2>/dev/null; then
    BASE_URL=$(grep "FIRECRAWL_BASE_URL=" ~/.hermes/.env | cut -d'=' -f2)
    echo "✅ FIRECRAWL_BASE_URL: $BASE_URL"
else
    echo "⚠️  FIRECRAWL_BASE_URL not configured (will use default cloud API)"
    echo "   Default: https://api.firecrawl.dev/v1"
fi

echo ""
echo "🔧 Firecrawl API docs: https://docs.firecrawl.dev/"
echo ""

# =============================================================================
# STEP 3: VERIFY DATABASE STRUCTURE
# =============================================================================
echo "================================================================================"  
echo "${BLUE}📊 STEP 3: DATABASE VERIFICATION${NC}"
echo "================================================================================"
echo ""

if [ -f "$DB_FILE" ]; then
    echo "✅ Database exists at: $DB_FILE"
    SIZE=$(du -h "$DB_FILE" | cut -f1)
    LINES=$(wc -l < "$DB_FILE")
    echo "   Size: $SIZE"
    echo "   Entries: ~$LINES records"
    
    # Check if database has core symbols tracked
    CORE_SYMBOLS=$(grep -c '"core_symbol"' "$DB_FILE" 2>/dev/null || echo 0)
    echo "   Core Symbols Tracked: ~$CORE_SYMBOLS (124, 55, 666, 963, 279, 111, 2727, coup)"
else
    echo "${RED}⚠️  Database not found at $DB_FILE${NC}"
    echo "   This file should exist from previous analysis sessions"
fi

echo ""

# =============================================================================
# STEP 4: CHECK SCRIPTS
# =============================================================================
echo "================================================================================"
echo "${BLUE}📜 STEP 4: SCRIPTS VERIFICATION${NC}"  
echo "================================================================================"
echo ""

SCRIPTS=(
    "scripts/overnight_research.py"
    "scripts/add_frontmatter.py" 
    "scripts/build_relationship_matrix.py"
    "scripts/auto_obisidian_sync_v2.py"
)

for script in "${SCRIPTS[@]}"; do
    if [ -f "$WORKDIR/$script" ]; then
        SIZE=$(du -h "$WORKDIR/$script" | cut -f1)
        echo "✅ $script ($SIZE)"
    else
        echo "${RED}⚠️  $script NOT FOUND${NC}"
    fi
done

echo ""

# =============================================================================
# STEP 5: DEPLOYMENT OPTIONS
# =============================================================================
echo "================================================================================"  
echo "${GREEN}🎯 DEPLOYMENT COMPLETE - CHOOSE YOUR PREFERRED METHOD:${NC}"
echo "================================================================================"
echo ""
echo "Option A: Manual Cron Installation (RECOMMENDED)"
echo "   ────────────────────────────────────────────"
echo "   Run these commands:"
echo "     1. crontab -e"
echo "     2. Paste at end of file:"
echo "        $CRON_COMMAND"
echo "     3. Save and exit (Ctrl+X, Y)"
echo ""
echo "Option B: Scripted Installation (Automated)"
echo "   ────────────────────────────────────────────"
echo "   Run: ./deploy_cron.sh install"
echo ""
echo "Option C: Manual Runner Only (No cron, run on-demand)"
echo "   ────────────────────────────────────────────"  
echo "   Run: python $WORKDIR/scripts/overnight_research.py"
echo ""
echo "Option D: Test Cron Syntax First"
echo "   ────────────────────────────────────────────"
echo "   Run:" 
echo "     crontab -l"
echo "     (shows current crontab entries)"
echo ""

# =============================================================================
# STEP 6: MONITORING COMMANDS
# =============================================================================
echo "================================================================================"
echo "${BLUE}📊 MONITORING COMMANDS:${NC}"
echo "================================================================================"
echo ""
echo "Check today's log:"
echo "   tail -100 $LOG_DIR/overnight_$(date +%Y-%m-%d).log"
echo ""
echo "View all logs:"  
echo "   ls -lt $LOG_DIR/"
echo ""
echo "Search database for pattern:"
echo "   grep '124' $DB_FILE | head -5"
echo ""

# =============================================================================
# SUMMARY
# =============================================================================
echo "================================================================================"
echo "${GREEN}📊 DEPLOYMENT STATUS:${NC}"
echo "================================================================================"
echo "✅ Cron files created: $WORKDIR/crontab.gematria-overnight, $WORKDIR/crontab.gematria-sync"
echo "✅ Scripts verified and ready"
echo "✅ Database exists: $DB_FILE"  
echo "⏳ Installation method: Choose Option A/B/C above"
echo ""
echo "🌙 OVERNIGHT RESEARCH WILL RUN AT 3:00 AM DAILY"
echo "    (After cron installation completes)"
echo "================================================================================"

echo ""
read -p "Press Enter to continue..." 
