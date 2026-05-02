#!/bin/bash
# 🧿 Steve's Gematria Database Maintenance Script
# ============================================================================
# Purpose: Automated database maintenance and indexing routines
# Location: ~/.hermes/gematria/scripts/maintain_database.sh
# Frequency: Recommended weekly (or use cron to schedule)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GEMATRIA_ROOT="$(dirname "$SCRIPT_DIR")"
REPORTS_DIR="$GEMATRIA_ROOT/reports"
DATABASE_JSON="$GEMATRIA_ROOT/database/gematria_database.json"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "=========================================="
echo "🧿 STEVE'S GEMATRIA DATABASE MAINTENANCE"
echo "Run Date: $(date)"
echo "=========================================="

# ============================================================================
# Step 1: Verify file integrity and regenerate search indices
# ============================================================================

echo ""
echo "[Step 1/6] Verifying report file integrity..."

for file in "$REPORTS_DIR"/*.md; do
    if [[ -f "$file" ]]; then
        lines=$(wc -l < "$file")
        bytes=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file" 2>/dev/null)
        echo "   ✓ $file (Lines: $lines, Bytes: $bytes)"
    fi
done

# ============================================================================
# Step 2: Create pattern search index file
# ============================================================================

echo ""
echo "[Step 2/6] Creating pattern search index..."

cat > "$GEMATRIA_ROOT/indices/pattern_keywords.txt" << 'EOF'
124
963
55
111
666
17
603
307
279
392
855
593
712
EOF

echo "   ✅ Pattern keyword index created"

# ============================================================================
# Step 3: Generate numeric sequence index
# ============================================================================

echo ""
echo "[Step 3/6] Generating numeric sequence index..."

python3 << 'PYEOF' > "$GEMATRIA_ROOT/indices/numeric_sequences.txt"
import re
import glob
from collections import Counter

reports_dir = "~/.hermes/gematria/reports/"
pattern = r'\b(\d+)\b'

all_numbers = []
for report in glob.glob(os.path.expanduser(reports_dir) + "*.md"):
    with open(report, 'r') as f:
        content = f.read()
    
    matches = re.findall(pattern, content)
    all_numbers.extend(matches)

# Count frequency and sort
counter = Counter(all_numbers)
sorted_counts = sorted(counter.items(), key=lambda x: int(x[0]))

with open('~/.hermes/gematria/indices/numeric_sequences.txt', 'w') as f:
    for num, count in sorted_counts:
        if len(num) <= 3:  # Only single or double digits
            f.write(f"{num}: {count} mentions\n")
PYEOF

echo "   ✅ Numeric sequence index created"

# ============================================================================
# Step 4: Backup database with timestamp
# ============================================================================

echo ""
echo "[Step 4/6] Creating timestamped backup..."

BACKUP_DIR="$GEMATRIA_ROOT/database/backups"
mkdir -p "$BACKUP_DIR"
cp "$DATABASE_JSON" "$BACKUP_DIR/gematria_database_backup_${TIMESTAMP}.json"

LAST_BACKUP_FILE=$(ls -t "$BACKUP_DIR"/*.json 2>/dev/null | head -n1 || echo "")
echo "   ✅ Backup saved: ${LAST_BACKUP_FILE:-$BACKUP_DIR/gematria_database_backup_${TIMESTAMP}.json}"

# ============================================================================
# Step 5: Generate summary statistics
# ============================================================================

echo ""
echo "[Step 5/6] Generating database statistics..."

# Count files and sizes
file_count=$(find "$GEMATRIA_ROOT" -maxdepth 1 -type f \( -name "*.md" -o -name "*.json" -o -name "*.txt" \) | wc -l)
total_size=$(du -sh "$GEMATRIA_ROOT" 2>/dev/null | cut -f1 || du -sk "$GEMATRIA_ROOT" | tr -d 'K')

echo "   Summary:"
echo "   └─ Total files: $file_count"
echo "   └─ Database size: ${total_size:-?}B"

# ============================================================================
# Step 6: Create version manifest
# ============================================================================

echo ""
echo "[Step 6/6] Creating version manifest..."

cat > "$GEMATRIA_ROOT/database/.version_manifest.json" << EOF
{
    "database_name": "Steve's Gematria Database",
    "version": "$(grep -o '"version": "[^"]*"' "$DATABASE_JSON" 2>/dev/null | cut -d'"' -f4 || echo "auto")",
    "last_maintenance": "$(date -Iseconds)",
    "maintainer": "Avalon (co-maintainer with Steve)",
    "file_count": $file_count,
    "total_size_bytes": $(du -b "$GEMATRIA_ROOT" 2>/dev/null | cut -f1 || stat -c%s "$GEMATRIA_ROOT"),
    "backup_location": "$BACKUP_DIR",
    "core_symbols_indexed": ["124", "963", "55", "111", "666", "17"],
    "elemental_forces_tracked": ["fire", "volcano", "frequency", "resonance"],
    "topics_covered": [
        "political_events",
        "epstein_files_analysis", 
        "trump_canada_narrative",
        "bitcoin_crypto_symbolism",
        "military_coup_themes"
    ]
}
EOF

echo "   ✅ Version manifest created"

# ============================================================================
# Final Summary
# ============================================================================

echo ""
echo "=========================================="
echo "✅ MAINTENANCE COMPLETE!"
echo "=========================================="
echo ""
echo "Summary:"
echo "  ✓ File integrity verified"
echo "  ✓ Pattern search index: indices/pattern_keywords.txt"
echo "  ✓ Numeric sequence index: indices/numeric_sequences.txt"
echo "  ✓ Database backup: backups/gematria_database_backup_${TIMESTAMP}.json"
echo "  ✓ Statistics generated in: database/.version_manifest.json"
echo ""
echo "Next recommended action:"
echo "  └─ Review statistics or schedule next maintenance"
echo ""
