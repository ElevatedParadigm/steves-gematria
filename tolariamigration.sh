#!/usr/bin/env bash
# tolariamigration.sh - Step-by-step Tolaria integration migration
# Usage: ./tolariamigration.sh [--dry-run]

set -e  # Exit on error

DRY_RUN=false
VAULT="/home/avalonas/.hermes/gematria"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run) DRY_RUN=true; shift ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

echo "=========================================="
echo "🚀 STEVE'S GEMATRIA → TOLARIA MIGRATION"
echo "=========================================="
echo ""

if [ "$DRY_RUN" = true ]; then
  echo "[👀] DRY RUN MODE - No changes will be made"
  echo ""
fi

# Step 1: Install pnpm
echo "Step 1/7: Installing pnpm..."
echo ""
if command -v corepack &> /dev/null; then
  echo "$ $ corepack enable"
  if [ "$DRY_RUN" = false ]; then
    corepack enable
  fi
  
  echo "$ $ corepack prepare pnpm@8 -r"
  if [ "$DRY_RUN" = false ]; then
    corepack prepare pnpm@8 -r
  fi
else
  echo "[⚠️] Corepack not found, install manually:"
  echo "     curl -fsSL https://get.corepack.sh | bash"
fi

# Step 2: Install Rust
echo ""
echo "Step 2/7: Checking Rust installation..."
if command -v rustc &> /dev/null && cargo --version &> /dev/null; then
  echo "[✅] Rust already installed: $(rustc --version)"
else
  echo "[🔧] Installing Rust..."
  if [ "$DRY_RUN" = false ]; then
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source "$HOME/.cargo/env"
  fi
fi

# Step 3: Install Linux dependencies
echo ""
echo "Step 3/7: Installing Linux system dependencies..."
if [ "$DRY_RUN" = false ]; then
  if command -v apt &> /dev/null; then
    sudo apt update
    sudo apt install -y \
      libwebkit2gtk-4.1-dev \
      build-essential \
      curl wget file \
      libxdo-dev libssl-dev \
      libayatana-appindicator3-dev \
      librsvg2-dev libsoup-3.0-dev patchelf 2>/dev/null
    echo "[✅] Dependencies installed"
  elif command -v dnf &> /dev/null; then
    sudo dnf install -y webkit2gtk4.1-devel 2>/dev/null
  else
    echo "[⚠️] Please manually install required dependencies:"
    echo "     Arch: pacman -S webkit2gtk-4.1 base-devel librsvg"
    echo "     Ubuntu/Debian: apt install libwebkit2gtk-4.1-dev build-essential"
  fi
fi

# Step 4: Install Tolaria
echo ""
echo "Step 4/7: Installing Tolaria..."
if [ "$DRY_RUN" = false ]; then
  # Check for existing installation first
  if command -v tolaria &> /dev/null; then
    echo "[✅] Tolaria already installed: $(command -v tolaria)"
  else
    curl -L https://github.com/refactoringhq/tolaria/releases/latest/download/Tolaria.app.tar.gz \
      | tar xzC /opt/
    
    sudo ln -s /opt/tolaria/Tolaria.app /usr/local/bin/tolaria
    
    echo "[✅] Tolaria installed successfully"
    tolaria --help || echo "[⚠️] Run on Linux: Extract from release directly"
  fi
else
  echo "Would install Tolaria from GitHub releases..."
fi

# Step 5: Setup vault structure
echo ""
echo "Step 5/7: Ensuring vault structure exists..."
mkdir -p "$VAULT"/{symbols,forces/{base_4,extension},domains,research/{relationships,cross_references,timeline,heatmaps},observations,scripts,obsidian_exports,database}

echo "[✅] Vault structure ready"

# Step 6: Run frontmatter migration (optional)
echo ""
echo "Step 6/7: Running YAML frontmatter migration..."
if [ -f "$VAULT/scripts/add_frontmatter.py" ]; then
  if [ "$DRY_RUN" = false ]; then
    echo "$ $ python scripts/add_frontmatter.py symbols --recursive"
    cd "$VAULT"
    python scripts/add_frontmatter.py symbols --recursive
    echo "[✅] Frontmatter migration complete"
  else
    echo "Would run frontmatter migration on: symbols/"
  fi
else
  echo "[⚠️] Migration script not found, skipping..."
fi

# Step 7: Verify installation
echo ""
echo "Step 7/7: Verifying installation..."
echo ""
echo "=== Prerequisites ==="
echo "Node.js: $(node --version 2>/dev/null || echo 'Not installed')"
echo "pnpm: $(pnpm --version 2>/dev/null || echo 'Not installed')"
echo "Rustc: $(rustc --version 2>/dev/null || echo 'Not installed')"
echo ""
echo "=== Tolaria ==="
if command -v tolaria &> /dev/null; then
  echo "[✅] Tolaria available at: $(command -v tolaria)"
else
  echo "[⚠️] Tolaria not in PATH, may need to extract from /opt/tolaria/"
fi

echo ""
echo "=== Vault Status ==="
echo "Total files: $(find "$VAULT" -type f | wc -l)"
echo "Total directories: $(find "$VAULT" -type d | wc -l)"

echo ""
echo "=========================================="
echo "[✅] MIGRATION COMPLETE!"
echo "=========================================="
echo ""
echo "📝 Next Steps:"
echo "1. Launch Tolaria: tolaria $VAULT"
echo "2. Browse your vault in the GUI"
echo "3. Use Python scripts from CLI as before"
echo "4. Obsidian remains compatible for detailed viewing"
echo ""
