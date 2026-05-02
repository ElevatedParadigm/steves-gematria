# 🧿 Steve's Gematria Database - Initialize & Verify
# ============================================================================
# Purpose: Initial setup verification and health check
# Usage: Run once after installation to verify everything works

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GEMATRIA_ROOT="$(dirname "$SCRIPT_DIR")"
REPORTS_DIR="$GEMATRIA_ROOT/reports"
DATABASE_JSON="$GEMATRIA_ROOT/database/gematria_database.json"
LOG_DIR="$GEMATRIA_ROOT/logs"

mkdir -p "$LOG_DIR"

echo "=========================================="
echo "🧿 STEVE'S GEMATRIA DATABASE - INITIALIZATION"
echo "Run Date: $(date)"
echo "=========================================="

# ============================================================================
# Step 1: Verify all files are accessible
# ============================================================================

echo ""
echo "[Step 1/5] Verifying database files..."

FILES_OK=true

for file in \
    "$DATABASE_JSON" \
    "$REPORTS_DIR/gematria_complete_report.md" \
    "$REPORTS_DIR/gematria_analysis_part1.md" \
    "$REPORTS_DIR/GEMATRIA_INDEX.md" \
    "$REPORTS_DIR/README.md"; do

    if [[ -f "$file" ]]; then
        size=$(du -h "$file" | cut -f1)
        echo "   ✓ $(basename "$file") [$size]"
    else
        echo "   ⚠ Missing: $(basename "$file")"
        FILES_OK=false
    fi
done

if $FILES_OK; then
    echo ""
    echo "✅ All required files present and accessible!"
else
    echo ""
    echo "⚠ Some files are missing. Run maintenance scripts to initialize."
fi

# ============================================================================
# Step 2: Verify directory structure
# ============================================================================

echo ""
echo "[Step 2/5] Checking directory structure..."

for dir in \
    "$GEMATRIA_ROOT/reports" \
    "$GEMATRIA_ROOT/database" \
    "$GEMATRIA_ROOT/scripts" \
    "$GEMATRIA_ROOT/indices"; do
    
    if [[ -d "$dir" ]]; then
        count=$(find "$dir" -type f 2>/dev/null | wc -l)
        echo "   ✓ $(basename "$dir") [$count files]"
    else
        echo "   ⚠ Missing directory: $(basename "$dir")"
    fi
done

# ============================================================================
# Step 3: Display database metadata summary
# ============================================================================

echo ""
echo "[Step 3/5] Loading database metadata..."

if [[ -f "$DATABASE_JSON" ]]; then
    echo "   ✓ Database file accessible"
    
    # Get version and count entries (if available)
    if grep -q '"metadata"' "$DATABASE_JSON"; then
        metadata=$(python3 -c "import json; print(json.dumps(json.load(open('$DATABASE_JSON'))['metadata'], indent=2))" 2>/dev/null || echo "Version info not loaded")
        echo "   $metadata"
    fi
else
    echo "   ⚠ Database JSON not found (will be created by maintain_db.sh)"
fi

# ============================================================================
# Step 4: List all analysis reports
# ============================================================================

echo ""
echo "[Step 4/5] Analysis reports inventory:"

for file in "$REPORTS_DIR"/*.md; do
    if [[ -f "$file" ]]; then
        filename=$(basename "$file")
        size=$(du -h "$file" | cut -f1)
        lines=$(wc -l < "$file")
        echo "   • $filename [$lines lines, $size]"
    fi
done

# ============================================================================
# Step 5: Create version manifest
# ============================================================================

echo ""
echo "[Step 5/5] Creating initialization manifest..."

cat > "$GEMATRIA_ROOT/database/.initialization_complete" << EOF
{
    "initialized": true,
    "init_date": "$(date -Iseconds)",
    "init_by": "Avalon (co-maintainer with Steve)",
    "version_manifest_path": "$GEMATRIA_ROOT/database/.version_manifest.json",
    "reports_count": $(find "$REPORTS_DIR" -name "*.md" | wc -l),
    "database_json_path": "$DATABASE_JSON"
}
EOF

echo "   ✅ Initialization manifest created"

# ============================================================================
# Summary & Next Steps
# ============================================================================

echo ""
echo "=========================================="
echo "✅ INITIALIZATION COMPLETE!"
echo "=========================================="
echo ""
echo "Next actions:"
echo "  1. Run: bash $GEMATRIA_ROOT/scripts/search_patterns.py"
echo "     → For interactive pattern searching"
echo ""
echo "  2. Copy cron_config.cron to ~/.crontab for auto-maintenance:"
echo "     cp $GEMATRIA_ROOT/scripts/cron_config.cron ~/.crontab"
echo "     crontab ~/.crontab"
echo ""
echo "  3. Review files in: $(realpath "$REPORTS_DIR")"
echo ""
echo "Database structure is ready for use! 🧿"
echo ""
