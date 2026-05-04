#!/bin/bash
# 🌙 STEVE'S GEMATRIA UNIFIED OVERNIGHT RESEARCH PIPELINE - INITIALIZATION
# This script initializes the unified overnight research repo with clean git state

set -e

REPO_PATH="/home/avalonas/.hermes/gematria/unified_overnight_research"
cd "$REPO_PATH"

# Remove corrupted index files if they exist
rm -f .git/index .git/index.lock 2>/dev/null || true

# Rebuild git directory from HEAD or current state
if [ -f .git/HEAD ]; then
    echo "🔧 Rebuilding git index..."
    git reset --quiet --hard HEAD 2>&1 | head -5 || true
fi

# Add all clean files (OUR folder and others)
git add OUR/ 2>/dev/null || true
git add -i 2>/dev/null || true

# Create initial commit with core symbols
if git diff --cached --quiet; then
    git commit --quiet -m "🌙 Overnight research pipeline initialized\nCore symbols: 124, 963, 55, 111, 279, 666\nFeatures: hidden-layering detection enabled" 2>&1 || true
fi

echo "✅ Git repository initialized and ready for continuous loop"
echo ""
echo "📊 Initial status:"
git log --oneline -5 || echo "(No commits yet)"
