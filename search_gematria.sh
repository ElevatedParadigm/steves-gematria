# 💧 STEVE'S GEMATRIA + TOLARIA INTEGRATION

## Quick Start Guide

Welcome to the integration of **Tolaria** (desktop markdown knowledge base) with Steve's Gematria system! 🚀

---

## 🎯 WHAT THIS ADDS

Tolaria provides a **powerful GUI editor** for your gematria vault while maintaining full compatibility with:
- ✅ Your existing Python CLI tools  
- ✅ Obsidian secondary viewing
- ✅ Git version control (your current workflow)
- ✅ All existing database structures

### Architecture:
```
┌─────────────────────────────────────────────┐
│  TOLARIA (Primary Editor - Desktop App)     │
│  ↔️                                         │
│  Python CLI Tools & Database                │
│  ↔️                                         │
│  OBSIDIAN (Secondary/Archive Viewer)        │
└─────────────────────────────────────────────┘
```

**All tools share the same Git-backed vault!**

---

## 📋 PREREQUISITES CHECKLIST

Before installing Tolaria, ensure you have:

- [ ] **Node.js v20+** ✅ (You have v25.9.0)
- [ ] **pnpm v8+** ❌ (Need to install)
- [ ] **Rust stable** ❌ (Need to install)  
- [ ] **WebKit2GTK 4.1** ❌ (Linux system dependency)

---

## 🔧 STEP-BY-STEP INSTALLATION

### Step 1: Enable Corepack (Built into Node.js)

```bash
# Enable corepack for pnpm access
corepack enable

# Prepare pnpm v8
corepack prepare pnpm@8 -r
```

**Verify:**
```bash
pnpm --version  # Should show v8.x.x
```

---

### Step 2: Install Rust

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Source cargo into your session (Linux)
source "$HOME/.cargo/env"

# Verify
cargo --version  # Should show rustc x.y.z
```

---

### Step 3: Install Linux System Dependencies

**Debian/Ubuntu (e.g., 22.04+):**

```bash
sudo apt update
sudo apt install -y \
  libwebkit2gtk-4.1-dev \
  build-essential \
  curl \
  wget \
  file \
  libxdo-dev \
  libssl-dev \
  libayatana-appindicator3-dev \
  librsvg2-dev \
  libsoup-3.0-dev \
  patchelf
```

**Arch/Manjaro:**

```bash
sudo pacman -S --needed \
  webkit2gtk-4.1 \
  base-devel \
  curl \
  wget \
  file \
  openssl \
  appmenu-gtk-module \
  libappindicator-gtk3 \
  librsvg
```

---

### Step 4: Install Tolaria (Official Release - Recommended)

```bash
# Download latest release
curl -L https://github.com/refactoringhq/tolaria/releases/latest/download/Tolaria.app.tar.gz \
  | tar xzC /opt/

# Create convenient symlink
sudo ln -s /opt/tolaria/Tolaria.app /usr/local/bin/tolaria

# Verify installation
tolaria --help
```

**Alternative: Run directly from release:**
```bash
cd /opt/tolaria/Tolaria.app/Contents/MacOS/
# For Linux, use the tar.gz contents appropriately
```

---

## 🗂️ VAULT STRUCTURE SETUP

The vault structure has already been created at:

```
/home/avalonas/.hermes/gematria/
├── symbols/           ← Core symbol definitions (YAML frontmatter)
├── forces/            ← Elemental force documentation
├── domains/           ← Domain-specific analysis
├── research/          ← Analysis results & heatmaps
├── observations/      ← Raw image/text analysis
├── scripts/           ← Python automation tools
├── obsidian_exports/  ← Legacy compatibility layer
└── database/          ← JSON database + registry files
```

**All existing content preserved!**

---

## 📝 MIGRATING TO YAML FRONTMATTER (Recommended)

### Why Frontmatter?

YAML frontmatter enables:
- ✅ Better Tolaria note organization
- ✅ Structured metadata for relationships
- ✅ AI agent queryability
- ✅ Consistent vault structure

### Run Migration Script:

```bash
# Add frontmatter to all symbols
cd /home/avalonas/.hermes/gematria
python scripts/add_frontmatter.py symbols --dry-run  # Preview changes first

# Then apply (remove DRY_RUN env var for actual changes)
unset DRY_RUN
python scripts/add_frontmatter.py symbols --recursive
```

### Manual Frontmatter Template:

For existing symbol notes, add this frontmatter:

```yaml
---
type: core-symbol
symbol_id: 124
name: Universal Threshold/Bridge
aliases: [universal, threshold, bridge]
description: "Universal threshold connecting all domains"
domains:
  - politics
  - military
  - religious
elemental_force: null
confidence_score: 0.95
created: "2026-04-27"
last_modified: "2026-04-27"
tags: [core, bridge, universal]
---

[Your existing content here...]
```

---

## 🚀 USING TOLARIA DAILY

### Launching:

```bash
# Method 1: Direct app launch
tolaria /home/avalonas/.hermes/gematria

# Method 2: From GUI (on desktop)
Tolaria.app  # If installed as .app or appropriate executable
```

### Recommended Workflow:

**Morning Routine:**
1. Launch Tolaria
2. Browse recent observations in `/observations/`
3. Check overnight research results from scripts
4. Review relationship matrices in `/research/relationships/`

**During Research:**
1. Open symbol note (e.g., `symbols/124_universal_threshold.md`)
2. Use Tolaria's file-first approach to edit
3. Link related notes via [[wikilinks]]
4. Frontmatter auto-saves on save

**Evening Synthesis:**
1. Run correlation heatmap generator:
   ```bash
   python scripts/heatmap_generator.py
   ```
2. Review results in `/research/heatmaps/`
3. Update symbol notes with new findings in Tolaria

---

## 🤖 MULTI-AGENT INTEGRATION

Tolaria is designed for AI agent workflows! Here's how to use it:

### Creating Agent Notes:

```markdown
# Research Task: Cross-Domain Pattern Synthesis

---
type: research-task
agent_id: cross-domain-synthesizer-v1
created: "2026-04-27"
status: pending
priority: high
---

**Objective:** Synthesize patterns between Politics and Military domains

**Approach:**
1. Read all notes in `/domains/politics/`
2. Extract symbols with ≥3 domain associations
3. Generate synthesis report to `/research/cross_references/`

**Tools Available:**
- `/scripts/auto_obisidian_sync_v2.py` for relationship extraction
- Database at `database/gematria_database.json`
```

### Agent Guidance:

Agents should read **AGENTS.md** for:
- ✅ Vault structure overview
- ✅ Research task definitions
- ✅ Available scripts and tools
- ✅ Data structure specifications

---

## 🔗 OBSIDIAN COMPATIBILITY

Your existing Obsidian setup remains fully compatible! Tolaria and Obsidian can coexist:

```bash
# Export from Tolaria to Obsidian vault format (if needed)
cd /home/avalonas/.hermes/gematria
tolaria --export obsidian /path/to/obsidian-vault  # Future feature

# Or simply share the same Git-backed folder between both apps
```

**Obsidian users:**
- Keep using Obsidian for detailed note-taking
- Tolaria for high-level browsing and relationship mapping
- Both read/write from same Git repository

---

## 📊 KEY FILES & DIRECTORIES

| Path | Purpose | Primary Tool |
|------|---------|--------------|
| `symbols/` | Core symbol definitions (YAML frontmatter) | Tolaria ↔️ Python scripts |
| `forces/` | Elemental force documentation | Tolaria |
| `domains/` | Domain analysis and synthesis | Tolaria |
| `research/relationships/` | Relationship matrices | Python auto_sync script |
| `research/cross_references/` | Cross-domain synthesis reports | Python heatmap script |
| `database/gematria_database.json` | Core database (JSON format) | Python CLI tools |
| `AGENTS.md` | Multi-agent instructions | AI agents + humans |

---

## 🛠️ AVAILABLE COMMANDS

### Tolaria Desktop App:
```bash
tolaria /home/avalonas/.hermes/gematria  # Open vault
```

### Python CLI Tools:
```bash
# Overnight research protocol
python scripts/overnight_research.py

# Relationship extraction & Obsidian sync
python scripts/auto_obisidian_sync_v2.py

# Generate ASCII correlation heatmap
python scripts/heatmap_generator.py

# Add YAML frontmatter to notes
python scripts/add_frontmatter.py symbols --recursive
```

### Git Commands (Shared with Tolaria):
```bash
git add symbols/ forces/ domains/
git commit -m "Add new symbol analysis"
git push origin main
```

---

## 🔍 SEARCHING THE VAULT

**Option 1: Tolaria GUI**
- Use built-in command palette (keyboard-first design)
- Navigate via type filters and tags

**Option 2: Terminal CLI (Power-user approach):**
```bash
# Search all symbols by name pattern
grep -r "symbol_id:" symbols/ | grep -i "777"

# Find all notes mentioning a specific domain
grep -l "political" domains/ research/ observations/

# Count notes by type
find symbols/ forces/ domains/ -name "*.md" -exec grep -l "^type:" {} \;
```

**Option 3: Custom Script:**

<tool_call>
<function=write_file>
<parameter=content>
#!/bin/bash
# search_gematria.sh - Quick vault search tool
# Usage: ./search_gematria.sh "search query" [scope]

SCOPE="symbols forces domains research observations"
QUERY="$1"

echo "🔍 Searching: '$QUERY'"
echo ""

for dir in $SCOPE; do
  result=$(grep -ri --include="*.md" "$QUERY" "/home/avalonas/.hermes/gematria/$dir/" 2>/dev/null | \
           grep -v "^Binary file" | \
           head -10)
  
  if [ -n "$result" ]; then
    echo "--- $dir/ ---"
    echo "$result"
    echo ""
  fi
done

echo "📝 Search complete!"
