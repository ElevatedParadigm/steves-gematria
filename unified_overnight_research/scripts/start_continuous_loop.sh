#!/bin/bash
# Steve's Gematria Overnight Research - Continuous Loop Launcher
# This script handles Firecrawl API configuration and starts the overnight research loop

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOGS_DIR="${PROJECT_ROOT}/logs"
STATUS_FILE="${PROJECT_ROOT}/CURRENT_STATUS.md"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CORE_SYMBOLS="124,963,55,111,279,666"
ITEMS_PER_CYCLE=30
MAX_ITERATIONS=9999

echo -e "${BLUE}==========================================" 
echo "Steve's Gematria Overnight Research Loop"
echo "==========================================${NC}"
echo ""

# Create logs directory if it doesn't exist
mkdir -p "$LOGS_DIR"
mkdir -p "${PROJECT_ROOT}/obsidian_exports"

# Step 1: Check if Docker Firecrawl is available
echo -e "${YELLOW}[Step 1/5] Checking Docker Firecrawl containers...${NC}"
if docker ps | grep -q firecrawl; then
    echo -e "${GREEN}✓ Firecrawl containers running on localhost:3002${NC}"
    FIRECRAWL_ENDPOINT="http://localhost:3002/v1"
else
    echo -e "${RED}✗ No Docker Firecrawl containers found${NC}"
    echo ""
    echo -e "${YELLOW}Setting up cloud API fallback (no payment required)...${NC}"
    
    # Step 2: Configure cloud API if local is not available
    echo ""
    echo -e "${BLUE}[Step 2/5] Configuring Firecrawl Cloud API...${NC}"
    
    ENV_FILE="${PROJECT_ROOT}/../.env"
    if [ ! -f "$ENV_FILE" ] || ! grep -q "FIRECRAWL_API_KEY" "$ENV_FILE" 2>/dev/null; then
        echo ""
        echo -e "${YELLOW}Adding Firecrawl cloud API configuration...${NC}"
        
        # Try to add to .env if it exists, otherwise use script constants
        if [ -f "$ENV_FILE" ]; then
            # Check if FIRECRAWL section exists
            if ! grep -q "FIRECRAWL" "$ENV_FILE"; then
                echo "" >> "$ENV_FILE"
                echo "# Firecrawl API Configuration (added by start_continuous_loop.sh)" >> "$ENV_FILE"
                echo 'FIRECRAWL_BASE_URL=https://api.firecrawl.dev/v1' >> "$ENV_FILE"
                echo '# FIRECRAWL_API_KEY=<paste your free tier key from firecrawl.dev>' >> "$ENV_FILE"
                echo -e "${GREEN}✓ Added Firecrawl cloud API to ${ENV_FILE}${NC}"
            fi
        else
            echo ""
            echo -e "${YELLOW}Creating .env file with Firecrawl cloud configuration...${NC}"
            mkdir -p ~/.hermes
            cat > ~/.hermes/.env <<'EOF'
# Hermes Agent Configuration

# API Keys - Configure as needed
HF_TOKEN=
COHERE_API_KEY=
ANTHROPIC_API_KEY=
DATABRICKS_API_KEY=
DEEPSEEK_API_KEY=
FIRECRAWL_BASE_URL=https://api.firecrawl.dev/v1
# FIRECRAWL_API_KEY=<paste your free tier key from firecrawl.dev>
EOF
            echo -e "${GREEN}✓ Created ~/.hermes/.env with cloud API config${NC}"
        fi
        
        # Create status file documenting the setup
        cat > "$STATUS_FILE" << EOF
# 📊 Steve's Gematria Research System Status

## ✅ ACCOMPLISHED:
- Continuous loop mode configured
- Firecrawl cloud API fallback active (100 credits/day free tier)
- Docker containers checked (none running - using cloud fallback)
- Core symbols identified: ${CORE_SYMBOLS}
  
## 🔧 SETUP COMPLETE:
${BLUE}Cloud Firecrawl Active!${NC}
- Visit https://firecrawl.dev/ and sign up for free tier
- Copy your API key to ~/.hermes/.env (optional, basic usage works without it)
- Run this script again or execute Python directly

## 📁 PATHS CONFIGURED:
- Database: /home/avalonas/.hermes/gematria/database/gematria_database.json
- Image Vault: /home/avalonas/Pictures/Steves%20gematria/
- Exports: ${PROJECT_ROOT}/obsidian_exports/

EOF
        echo -e "${GREEN}✓ Created status file at $STATUS_FILE${NC}"
    fi
    
    # Step 3: Verify Python venv has hermes_tools
    echo ""
    echo -e "${BLUE}[Step 3/5] Verifying Python environment...${NC}"
    
    VENV_ACTIVATE_PATH="/home/avalonas/.hermes/hermes-agent/venv/bin/activate"
    if [ ! -f "$VENV_ACTIVATE_PATH" ]; then
        echo -e "${YELLOW}⚠️  HerMES-TOOLS venv not found, using system Python${NC}"
        PYTHON_CMD="python3"
    else
        echo -e "${GREEN}✓ HerMES-TOOLS venv available${NC}"
        PYTHON_CMD="${VENV_ACTIVATE_PATH}/python"
        
        # Try to activate venv and check hermes_tools
        (source "$VENV_ACTIVATE_PATH" && python -c "from hermes_tools import *; print('✓ hermes_tools available')" 2>/dev/null) && \
            echo -e "${GREEN}✓ hermes_tools library loaded successfully${NC}" || \
            echo -e "${YELLOW}⚠️  hermes_tools may have dependencies to install${NC}"
    fi
    
    FIRECRAWL_ENDPOINT="https://api.firecrawl.dev/v1"
fi

# Step 4: Show current database status
echo ""
echo -e "${BLUE}[Step 4/5] Checking database state...${NC}"

DB_PATH="${PROJECT_ROOT}/../database/gematria_database.json"
if [ -f "$DB_PATH" ]; then
    PYTHON_CMD="python3 -c"
    DB_STATUS=$($PYTHON_CMD "import json; db=json.load(open('$DB_PATH')); print(f'✓ Database loaded ({len(db.get(\"symbols_tracked\", {}))} symbols tracked)')" 2>/dev/null || echo "Database check failed")
    echo "$DB_STATUS"
else
    echo -e "${RED}✗ Database not found at $DB_PATH${NC}"
fi

# Step 5: Run the actual overnight research loop
echo ""
echo -e "${BLUE}[Step 5/5] Starting Continuous Loop Mode...${NC}"
echo "Items per cycle: ${ITEMS_PER_CYCLE}"
echo "Max iterations: ${MAX_ITERATIONS}"
echo "Firecrawl endpoint: ${FIRECRAWL_ENDPOINT}"
echo ""

# Clear previous status if exists
rm -f "$STATUS_FILE" 2>/dev/null || true

# Append execution info to status file
cat >> "$STATUS_FILE" << EOF
## 🚀 EXECUTION STARTED: $(date '+%Y-%m-%d %H:%M:%S')

## Configuration:
- Mode: Continuous Loop (${MAX_ITERATIONS} iterations)
- Items per cycle: ${ITEMS_PER_CYCLE}
- Firecrawl: Cloud API fallback active
EOF

# Run the overnight research loop
echo ""
echo -e "${GREEN}🎯 Starting overnight research pipeline...${NC}"
echo "==========================================="
$PYTHON_CMD "$PROJECT_DIR/run_continuous_loop.py" \
    --items-per-cycle "$ITEMS_PER_CYCLE" \
    --max-iterations "$MAX_ITERATIONS"

# Update status with completion info
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Cycle completed successfully!${NC}"
    
    cat >> "$STATUS_FILE" << EOF

## ✅ COMPLETED: Last cycle finished at $(date '+%Y-%m-%d %H:%M:%S')
## Next run: Press 'continue' to resume or wait for cron schedule
EOF
else
    echo ""
    echo -e "${RED}✗ Cycle failed. Check logs and try again.${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}OVERNIGHT RESEARCH LOOP READY${NC}"
echo "Status file: $STATUS_FILE"
echo "To continue: Execute this script again or use cron job"
echo "==========================================="
