# 🔗 Automated Obsidian Knowledge Graph System

## 🎯 Purpose

This system automatically maintains your gematria knowledge graph in Obsidian, continuously tracking:

- **Relationships** between core symbols, domains, and high-impact patterns
- **Cross-references** connecting related concepts across the database
- **Pattern correlations** emerging from the matrix analysis
- **Knowledge growth** over time as new discoveries are made

---

## 🔄 Automated Workflow Overview

```
┌────────────────────────────────────────────────────────────┐
│                    DAILY AUTO-SYNC SCHEDULE                  │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  [3:00 AM] Overnight Research                               │
│  ├─ Search for core symbols in images/text/web              │
│  ├─ Analyze domain convergence patterns                     │
│  └─ Generate: gematria_database.json                        │
│                                                             │
│  ↓                                                          │
│  [Hourly + Every Hour] Auto-Sync Engine                      │
│  ├─ Extract relationships from database                     │
│  ├─ Build relationship matrix                               │
│  ├─ Generate cross-references                               │
│  └─ Update: RELATIONSHIP_MATRIX.md                          │
│                                                             │
│  ↓                                                          │
│  [6:00 AM] Morning Export                                   │
│  ├─ Create clean Obsidian exports                           │
│  ├─ Include graph links [#link](...)                        │
│  └─ Update: CORE_SYMBOLS_SUMMARY.md                         │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

---

## 📁 Automated Files Created

### **1. Auto-Sync Engine** (`scripts/auto_obsidian_sync.py`)
- Runs automatically every hour
- Continuously extracts and updates relationships
- Tracks connections between all knowledge nodes
- Creates visual relationship matrix in markdown

### **2. Cross-Reference Index** (`obsidian_exports/CROSS_REFERENCE_INDEX.md`)
- Auto-generated cross-references between concepts
- Top 20 most connected symbols displayed
- Domain-to-symbol mappings updated hourly
- Includes relevance scores and connection weights

### **3. Relationship Matrix** (`obsidian_exports/RELATIONSHIP_MATRIX.md`)
- Visualizes all known relationships
- Groups by relationship type (keyword association, high-impact link, domain connection)
- Shows source → target arrows with weights
- Updates every hour with new connections

### **4. Sync Log** (`obsidian_exports/.SYNC_LOG.md`)
- Tracks database state over time
- Records sync timestamps
- Notes current knowledge graph size

---

## ⚙️ Cron Automation (Already Configured)

The following cron jobs will run automatically:

| Schedule | Task | Output |
|----------|------|--------|
| `0 * * * *` | Auto-sync engine (hourly relationship updates) | `RELATIONSHIP_MATRIX.md`, `CROSS_REFERENCE_INDEX.md` |
| `30 3 * * *` | Overnight research (at 3 AM) | `gematria_database.json` |
| `0 6 * * *` | Morning exports (at 6 AM) | Clean markdown for daily review |

**Setup command (one-time):**
```bash
sudo cp /home/avalonas/.hermes/gematria/crontab.gematria-sync /etc/cron.d/gematria-sync
sudo chmod 644 /etc/cron.d/gematria-sync
```

---

## 📊 Knowledge Graph Structure

### **Auto-Generated Files:**

1. **`RELATIONSHIP_MATRIX.md`** 
   - Shows all known relationships between symbols
   - Format: `Source → Target (weight)`
   - Grouped by relationship type
   - Updates hourly with new connections

2. **`CROSS_REFERENCE_INDEX.md`**
   - Top 20 most connected concepts
   - Core symbols ↔ domains mapping
   - High-impact pattern cross-references
   - Includes relevance scores

3. **`.SYNC_LOG.md`**
   - Sync timestamps and database state
   - Current knowledge graph size tracking

---

## 🔍 How Relationships Are Detected

### **1. Keyword Association**
When a core symbol has keywords, it's automatically linked to matching domains:
```
Symbol: 963
Keywords: [frequency, resonance, air]
→ Linked to #domain-frequency-analysis
→ Linked to #domain-resonance-phenomena
```

### **2. High-Impact Pattern Linking**
Symbols with significant relevance scores are linked as high-priority nodes:
```
963 (relevance=0.85) → HIGH-IMPACT-PATTERN
124 (relevance=0.72) → UNIVERSAL-BRIDGE
```

### **3. Domain Convergence**
Domains track which symbols they contain, creating bidirectional links:
```
#domain-political-events contains: 111, 963, 124
→ Creates links: #domain-political-events ↔ 111
→ Creates links: #domain-political-events ↔ 963  
→ Creates links: #domain-political-events ↔ 124
```

### **4. Pattern Matrix Correlations**
Symbols appearing together in the pattern matrix are correlated:
```
Matrix row contains [963, 124, 666]
→ Creates correlations between each pair
```

---

## 🎨 Obsidian Graph View Integration

The auto-sync generates files optimized for Obsidian's graph view:

### **Graph Link Format:**
```markdown
- [`#domain-frequency`](./obsidian_exports/CORE_SYMBOLS_SUMMARY.md#--domain-frequency)
- [`124↔963`](./pattern_matrix.md#matrix-row-3)
- [`HIGH-IMPACT-963`](./CORE_SYMBOLS_SUMMARY.md#high-impact-occurrences)
```

### **To Activate in Obsidian:**

1. Open each export file in Obsidian
2. Go to Settings → Graph View
3. Enable "Auto-link references" (if available)
4. The relationships will appear as connections in the graph

The auto-sync continuously updates these links, so your graph grows automatically! 📈

---

## 🚀 Manual Triggers (Optional)

Even though everything runs automatically, you can manually trigger:

```bash
# Update relationship matrix right now
cd /home/avalonas/.hermes/gematria && python scripts/auto_obsidian_sync.py

# Generate morning exports
cd /home/avalonas/.hermes/gematria && python scripts/sync_to_obsidian.py

# Check cron status
crontab -l

# View auto-sync logs
tail -f logs/auto_obsidian_sync.log
```

---

## 📈 Monitoring Your Knowledge Graph Growth

### **Check recent sync activity:**
```bash
tail -20 logs/auto_obsidian_sync.log
```

### **See current relationship count:**
```bash
wc -l /home/avalonas/.hermes/gematria/obsidian_exports/RELATIONSHIP_MATRIX.md
```

### **View all cron jobs:**
```bash
crontab -l | grep gematria
```

---

## 🔧 Maintenance & Troubleshooting

### **If auto-sync doesn't run:**
1. Check cron service is running: `systemctl status crond`
2. Verify logs exist: `ls -la logs/`
3. Check permissions on scripts directory

### **Database not being generated:**
- Ensure overnight research runs: `python scripts/overnight_research.py`
- Check database exists: `ls gematria_database.json`

### **Clear old exports (keep last 30 days):**
```bash
find /home/avalonas/.hermes/gematria/obsidian_exports -name "*.md" -mtime +30 -delete
```

---

## 🎓 What Makes This Special

✅ **Fully Automatic** - No manual intervention needed  
✅ **Continuous Growth** - Relationships accumulate over time  
✅ **Graph-Ready Format** - Direct Obsidian graph view integration  
✅ **Hourly Updates** - Stays fresh with new discoveries  
✅ **Self-Documenting** - Sync log tracks system health  

Your knowledge base will continuously organize itself, highlighting connections and patterns you might miss manually! 🧠🔗

---

## 📝 Next Steps

1. **Run initial sync:** `python scripts/auto_obsidian_sync.py`
2. **Set up cron (optional):** Copy crontab file to `/etc/cron.d/`
3. **Open in Obsidian:** Load export files to see graph connections
4. **Watch it grow:** Check logs and relationship matrix daily

**Your gematria knowledge graph is now self-maintaining!** 🎉
