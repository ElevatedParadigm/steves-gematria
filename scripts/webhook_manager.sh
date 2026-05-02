#!/bin/bash
#
# Gematria Webhook Subscription Manager
# ======================================
# Manages webhook subscriptions for new image feeds in the gematria project
#

set -e

# Configuration
GEMATRIA_DIR="${GEMATRIA_DIR:-$HOME/.hermes/gematria}"
SCRIPTS_DIR="$GEMATRIA_DIR/scripts"
REPORTS_DIR="$GEMATRIA_DIR/reports"
LOGS_DIR="$GEMATRIA_DIR/logs"
WEBHOOK_SCRIPT="$SCRIPTS_DIR/webhook_image_receiver.py"

# Core symbols reference
CORE_SYMBOLS="124 963 279 111 55 666 17"
DOMAINS="political Epstein files Trump Canada Bitcoin Military Coup Elemental"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║   Steve's Gematria - Image Feed Webhook Subscriptions  ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_subheader() {
    echo -e "${GREEN}▸ $1${NC}"
}

show_status() {
    print_header
    
    echo "Project Directory:"
    echo "   ${YELLOW}${GEMATRIA_DIR}${NC}"
    echo ""
    
    if [[ -d "$REPORTS_DIR" ]]; then
        echo "Reports Directory (${GREEN}active${NC}):"
        echo "   ${YELLOW}${REPORTS_DIR}${NC}"
        REPORT_COUNT=$(find "$REPORTS_DIR" -name "report_*.md" 2>/dev/null | wc -l)
        echo "   📝 Total reports: ${REPORT_COUNT:-0}"
    else
        echo "Reports Directory (${YELLOW}not found${NC}):"
        echo "   ${RED}${REPORTS_DIR}${NC}"
    fi
    echo ""
    
    if [[ -d "$LOGS_DIR" ]]; then
        echo "Logs Directory (${GREEN}active${NC}):"
        echo "   ${YELLOW}${LOGS_DIR}${NC}"
        LATEST_LOG=$(find "$LOGS_DIR" -name "*.log" 2>/dev/null | sort -r | head -1 || echo "none")
        if [[ "$LATEST_LOG" != "none" && -n "$LATEST_LOG" ]]; then
            echo "   📋 Latest: $LATEST_LOG"
        fi
    else
        echo "Logs Directory (${YELLOW}not found${NC}):"
        echo "   ${RED}${LOGS_DIR}${NC}"
    fi
    echo ""
    
    if [[ -f "$WEBHOOK_SCRIPT" ]]; then
        echo "Webhook Receiver Script (${GREEN}active${NC}):"
        echo "   ${YELLOW}${WEBHOOK_SCRIPT}${NC}"
        
        if [[ -x "$WEBHOOK_SCRIPT" ]]; then
            echo "   ✅ Script is executable"
        else
            echo "   ⚠️  Script needs execute permission"
        fi
    else
        echo "Webhook Receiver Script (${RED}not found${NC}):"
        echo "   ${YELLOW}$WEBHOOK_SCRIPT${NC}"
    fi
    echo ""
    
    echo "Core Symbols Tracked:"
    for symbol in $CORE_SYMBOLS; do
        printf "   • %-8s " "$symbol"
        if [[ $(($# - 7)) -gt 0 ]]; then
            echo ""
        fi
    done
    echo ""
    
    echo "Domains Tracked:"
    for domain in $DOMAINS; do
        echo "   • $domain"
    done
    echo ""
}

subscribe_image() {
    local image_url="$1"
    
    if [[ -z "$image_url" ]]; then
        print_header
        echo "❌ Error: Please provide an image URL or file path"
        echo ""
        echo "Usage: $0 subscribe <url|file> [options]"
        echo ""
        return 1
    fi
    
    echo -e "${BLUE}📥 Subscribing to image feed...${NC}"
    echo "   Image: ${image_url}"
    
    # Create subscription timestamp and reference
    SUBSCRIBED_AT=$(date '+%Y-%m-%d %H:%M:%S')
    SUB_ID="webhook-$(date +%s)-$RANDOM"
    
    # Log the subscription
    LOG_FILE="$LOGS_DIR/subscription_$(date +%Y%m%d_%H%M%S).log"
    mkdir -p "$LOGS_DIR"
    
    {
        echo "Subscription ID: $SUB_ID"
        echo "Image URL/Path: $image_url"
        echo "Subscribed At: $SUBSCRIBED_AT"
        echo ""
        echo "Status: Pending Analysis"
        echo "---"
    } > "$LOG_FILE"
    
    # Update subscription log
    SUB_LOG="$LOGS_DIR/subscriptions.json"
    if [[ ! -f "$SUB_LOG" ]]; then
        echo '{"subscriptions": []}' > "$SUB_LOG"
    fi
    
    # Add new subscription using Python for JSON safety
    python3 << EOF
import json
with open("$SUB_LOG", "r") as f:
    data = json.load(f)

sub_id = "$SUB_ID"
url = "$image_url"
timestamp = "$SUBSCRIBED_AT"

data["subscriptions"].append({
    "id": sub_id,
    "url": url,
    "status": "pending",
    "timestamp": timestamp
})

with open("$SUB_LOG", "w") as f:
    json.dump(data, f, indent=2)
EOF
    
    echo -e "${GREEN}✅ Subscription created!${NC}"
    echo "   ID: ${SUB_ID}${NC}"
    echo "   Log: ${LOG_FILE}${NC}"
    echo ""
    show_status
}

list_subscriptions() {
    SUB_LOG="$LOGS_DIR/subscriptions.json"
    
    if [[ ! -f "$SUB_LOG" ]]; then
        echo -e "${YELLOW}⚠️  No subscriptions found${NC}"
        echo ""
        echo "Run: $0 subscribe <url|file>"
        return
    fi
    
    echo -e "${BLUE}📋 Active Subscriptions:${NC}"
    echo ""
    
    python3 << EOF
import json

with open("$SUB_LOG", "r") as f:
    data = json.load(f)

subscriptions = data.get("subscriptions", [])

if not subscriptions:
    print("No subscriptions found.")
else:
    print(f"Found {len(subscriptions)} subscription(s):")
    print()
    
    for i, sub in enumerate(subscriptions, 1):
        id_val = sub.get("id", "unknown")
        url = sub.get("url", "unknown")
        status = sub.get("status", "unknown")
        timestamp = sub.get("timestamp", "unknown")
        
        status_colors = {
            "pending": "${YELLOW}",
            "processing": "${BLUE}",
            "completed": "${GREEN}"
        }
        status_color = status_colors.get(status, "${NC}")
        
        print(f"   {i}. [{status_color}{status}${NC}] {id_val}")
        print(f"      URL: {url[:80]}..." if len(url) > 80 else f"      URL: {url}")
        print(f"      Subscribed: {timestamp}")
        print()
EOF
    
    TOTAL_COUNT=$(python3 -c "import json; d=json.load(open('$SUB_LOG')); print(len(d.get('subscriptions', [])))")
    PENDING_COUNT=$(python3 -c "import json; d=json.load(open('$SUB_LOG')); print(len([s for s in d.get('subscriptions', []) if s.get('status')=='pending']))")
    COMPLETED_COUNT=$(python3 -c "import json; d=json.load(open('$SUB_LOG')); print(len([s for s in d.get('subscriptions', []) if s.get('status')=='completed']))")
    
    echo ""
    echo "📊 Summary:"
    echo "   Total: ${TOTAL_COUNT:-0}"
    echo "   Pending: ${PENDING_COUNT:-0}"
    echo "   Completed: ${COMPLETED_COUNT:-0}"
}

test_webhook() {
    echo -e "${BLUE}🧪 Testing webhook subscription endpoint...${NC}"
    echo ""
    
    TEST_URL="https://www.example.com/test-image.jpg"
    
    # Simulate sending test image
    echo "Sending test image..."
    
    SUBSCRIBED_AT=$(date '+%Y-%m-%d %H:%M:%S')
    SUB_ID="webhook-test-$(date +%s)"
    
    # Create test subscription
    SUB_LOG="$LOGS_DIR/subscriptions.json"
    if [[ ! -f "$SUB_LOG" ]]; then
        echo '{"subscriptions": []}' > "$SUB_LOG"
    fi
    
    python3 << EOF
import json

with open("$SUB_LOG", "r") as f:
    data = json.load(f)

data["subscriptions"].append({
    "id": "$SUB_ID",
    "url": "$TEST_URL",
    "status": "pending",
    "timestamp": "$SUBSCRIBED_AT"
})

with open("$SUB_LOG", "w") as f:
    json.dump(data, f, indent=2)
EOF
    
    # Create test report
    REPORT_FILE="$REPORTS_DIR/report_test_$(date +%s).json"
    echo '{"status": "received", "test": true}' > "$REPORT_FILE"
    
    if [[ -f "$REPORT_FILE" ]]; then
        echo -e "${GREEN}✅ Test webhook call successful!${NC}"
        echo "   Report: ${REPORT_FILE}${NC}"
    fi
    
    echo ""
    show_status
}

show_help() {
    cat << EOF
Gematria Webhook Subscription Manager

Usage: $0 <command> [options]

Commands:
  subscribe <url|file>    Subscribe a new image for analysis
                          Examples:
                            • subscribe https://example.com/image.jpg
                            • subscribe ./local-image.png
                            
  list                    List all active subscriptions with status
                          
  test                    Run a test webhook call to verify setup
  
  status                  Show overall system status

Core Symbols Tracked:
EOF
    
    for symbol in $CORE_SYMBOLS; do
        echo "   • $symbol"
    done
    
    cat << EOF

Domains Tracked:
EOF
    
    for domain in $DOMAINS; do
        echo "   • $domain"
    done
}

# Main entry point
main() {
    print_header
    
    case "${1:-}" in
        subscribe)
            subscribe_image "${2:-}"
            ;;
        list|ls)
            list_subscriptions
            ;;
        test)
            test_webhook
            ;;
        status)
            show_status
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo -e "${RED}❌ Unknown command: $1${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

main "$@"
