# Hermes → Tolaria MCP Integration Setup Guide ✅

## What This Does

Enables your Hermes Agent to automatically use [Tolaria](https://tolaria.app/) as a note-taking vault during gematria research. The integration stores analysis notes, tracks pattern discussions, and maintains knowledge via Model Context Protocol (MCP).

---

## Architecture

```
┌─────────────────────┐      ws://localhost:9710      ┌─────────────────────┐
│  Hermes Agent       │   ←→   WebSocket Connection   │  Tolaria MCP Server  │
│  (MCP Client)       │                              │  (MCP Server)        │
│                     │   Note Creation, Search,      │                     │
│  Core Symbols:      │   Metadata Editing            │                     │
│  • 124              │                              │  User Vault          │
│  • 963              │                              └───────────────────────┘
│  • 55                │                              Knowledge Graph
│  • 111               │                              
│  • 279               │                          
│  • 666                                                       
└─────────────────────┘
```

---

## Files Modified

### Primary Configuration
**`/home/avalonas/.hermes/config.yaml`** (Line 195)

Added `mcp_sources:` section:
```yaml
mcp_sources:
  - /home/avalonas/.hermes/mcp-tolaria-config.yaml
```

---

## How to Use

### Automatic Integration (Current Setup) ✅
With the config added to `config.yaml`, Hermes will **automatically connect** to Tolaria whenever you run research workflows. No flags needed!

### Alternative: CLI Flag
If you prefer explicit control, you can also use:
```bash
hermes --mcp-sources ~/.hermes/mcp-tolaria-config.yaml
```

---

## Available Tools

When connected, Hermes can use these Tolaria MCP tools:

| Tool | Purpose |
|------|---------|
| `create_note()` | Auto-create notes for gematria analysis (e.g., "124 Bridge Pattern: Geographic + Elemental") |
| `search_notes()` | Find related discussions about specific symbols/domains |
| `edit_note_frontmatter()` | Add YAML metadata (tags, timestamps, relevance scores) |
| `delete_note()` | Clean up duplicate notes or superseded analysis |
| `list_tags()` | Browse categories: `[geographic] [elemental] [military]` etc. |

---

## Example Workflow

When you trigger overnight research:

```bash
# Run overnight research (from previous session)
python /home/avalonas/.hermes/gematria/scripts/overnight_research.py
```

**Hermes will now:**
1. ✅ Connect to Tolaria automatically via WebSocket `ws://localhost:9710`
2. ✅ Create note with findings like "Domain Convergence Report - 4 AM"
3. ✅ Tag notes appropriately (`[core-symbols] [cross-reference]`)
4. ✅ Link related symbols (e.g., connect "124 Bridge" to its elemental forces)

---

## Verification

### Check Tolaria Server Status
```bash
# Should show running PIDs
ps aux | grep node | grep server.js
```

### Check Hermes Config Loaded
```bash
grep -A 2 "mcp_sources:" /home/avalonas/.hermes/config.yaml
```

Expected output:
```yaml
mcp_sources:
  - /home/avalonas/.hermes/mcp-tolaria-config.yaml
```

---

## Knowledge Vault Location

Tolaria notes are stored in your user directory. The exact path depends on your Tolaria installation, but they're accessible via the MCP server and linked to your gematria research folder at:

**`/home/avalonas/.hermes/gematria/`**

---

## Related Files

- **Configuration**: `/home/avalonas/.hermes/config.yaml` (line 195)
- **MCP Source**: `/home/avalonas/.hermes/mcp-tolaria-config.yaml`
- **Summary Documentation**: `/home/avalonas/.hermes/gematria/TOLARIA_MCP_INTEGRATION_SUMMARY.md`

---

## Support Commands

### Test Connection
```bash
# Check Tolaria is running
curl -s ws://localhost:9710 2>&1 | head -3
```

### View Config
```bash
cat /home/avalonas/.hermes/mcp-tolaria-config.yaml
```

---

## Integration Points

This MCP integration works with all your existing workflows:

- ✅ Overnight research protocol (`overnight_research.py`)
- ✅ Auto-Obsidian sync (`auto_obisidian_sync_v2.py`)  
- ✅ Domain convergence analysis
- ✅ Cross-reference pattern tracking
- ✅ Core symbol relationship mapping

---

## Notes About MCP

**MCP (Model Context Protocol)** is a standard for connecting AI agents to tools and data sources. In this setup:

- **Hermes = MCP Client** (the agent that uses tools)
- **Tolaria = MCP Server** (the service providing tools/data)
- **Connection**: WebSocket at `ws://localhost:9710`

This is similar to how APIs work, but with a standardized protocol for AI agents.

---

## Status: ✅ ACTIVE & AUTOMATIC

The Tolaria MCP source is now permanently configured in your Hermes config.yaml. It will automatically connect whenever you run research workflows or use Hermes for gematria analysis.

Last updated: **April 29, 2026** by Avalon co-maintainer
