#!/usr/bin/env python3
"""
Obsidian Sync Script for Steve's Gematria Database
Exports database findings to Obsidian-compatible markdown notes with graph links
"""

import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path.home() / ".hermes"
GEMATRIA_DB = BASE_DIR / "gematria_database.json"
OBSIDIAN_EXPORT_DIR = BASE_DIR / "gematria" / "obsidian_exports"

def load_database():
    """Load the main gematria database"""
    if GEMATRIA_DB.exists():
        with open(GEMATRIA_DB) as f:
            return json.load(f)
    return {"core_processing": [], "analyzed_items": {}}

def export_core_symbols_summary():
    """Export a summary note for all core symbols"""
    db = load_database()
    
    obsidian_dir = OBSIDIAN_EXPORT_DIR if OBSIDIAN_EXPORT_DIR.exists() else None
    obsidian_dir.mkdir(parents=True, exist_ok=True)
    
    export_file = obsidian_dir / "CORE_SYMBOLS_SUMMARY.md"
    
    # Get core symbols from database
    core_symbols = db.get("core_processing", {})
    
    report = f"""# Core Symbols - Summary Matrix

> **Created:** {datetime.now().strftime("%Y-%m-%d %H:%M")}  
> **Domain:** Universal / The Signal Manifesto  

---

## 🔢 CORE SYMBOL MATRIX

| Symbol | Reduction Value | Element/Domain | Name | Frequency in DB |
|--------|-----------------|----------------|------|-----------------|
"""
    
    for symbol_id, data in sorted(core_symbols.items()):
        name = data.get("name", "Unknown")
        element = data.get("element", "Unknown")
        occurrences = sum(1 for item in core_symbols.values() if item.get("id") == symbol_id)
        
        report += f"| {symbol_id} | {data.get('reduction', 'N/A')} | {element} | {name} | {occurrences} |\n"
    
    # Add high-impact occurrences
    report += f"""---

## 🌟 HIGH-IMPACT OCCURRENCES

Recent notable patterns detected:

"""
    
    recent_high_impact = core_symbols.get("666", {}).get("recent_high_impact_occurrences", [])
    for occ in recent_high_impact[:5]:  # Top 5
        report += f"### {occ.get('title', 'Pattern Found')}\n"
        report += f"**Location:** `{occ.get('source', 'N/A')}`\n"
        if occ.get("description"):
            short_desc = occ["description"][:200] + "..." if len(occ["description"]) > 200 else occ["description"]
            report += f"**Context:** {short_desc}\n"
        report += "\n---\n\n"
    
    # Add universal bridge tracker status
    ub = core_symbols.get("124", {})
    report += f"""---

## 🌉 UNIVERSAL BRIDGE TRACKER (124 km³)

**Status:** `{'Active' if ub.get('monitoring', True) else 'Inactive'}"  
**Water Domain:** {ub.get('water_domain_status', 'Monitored')}`

### Known Bridge Patterns:
"""
    
    bridge_events = []
    for symbol_data in core_symbols.values():
        events = symbol_data.get("bridge_connections", [])
        for event in events[:2]:  # Top 2 per symbol
            bridge_events.append(event)
    
    for i, event in enumerate(bridge_events[:5], 1):
        source = event.get("source", "N/A")
        report += f"{i}. **{source}**\n\n"
    
    report += """---

## 🔗 RELATED LINKS

- [Core Symbols Database](`/gematria_database.json`)
- [Analysis Log](`/logs/overnight_research.log`)
- [Pattern Matrix Visualization](`/gematria/pattern_matrix.md`)

"""
    
    with open(export_file, 'w') as f:
        f.write(report)
    
    print(f"✅ Exported core symbols summary to: {export_file}")
    return export_file

def export_analysis_timeline():
    """Export chronological analysis log"""
    db = load_database()
    
    obsidian_dir = OBSIDIAN_EXPORT_DIR if OBSIDIAN_EXPORT_DIR.exists() else None
    if not obsidian_dir:
        obsidian_dir.mkdir(parents=True, exist_ok=True)
    
    export_file = obsidian_dir / "ANALYSIS_TIMELINE.md"
    
    all_occurrences = db.get("core_processing", [])
    
    report = f"""# Analysis Timeline - {datetime.now().strftime("%Y-%m-%d")}

> **Generated:** {datetime.now().isoformat()}  
> **Source:** Steve's Gematria Database  

---

## ⏱️ CHRONOLOGICAL ANALYSIS LOG

"""
    
    for occurrence in all_occurrences[-100:]:  # Last 100 occurrences
        timestamp = occurrence.get("timestamp", "")
        source = occurrence.get("source", "Unknown")
        title = occurrence.get("title", "")
        domain = occurrence.get("domain", "")
        
        report += f"\n### {timestamp}\n"
        report += f"**Location:** `{source}`\n"
        report += f"**Title:** {title}\n"
        if domain:
            report += f"**Domain:** {domain}\n"
        
        symbols = occurrence.get("symbols_detected", [])
        if symbols:
            report += f"**Core Symbols:** `{' / '.join(symbols)}`\n"
        
        relevance = occurrence.get("relevance_score", 0.0)
        if relevance > 0.8:
            report += "⭐ **High Relevance**\n"
        
        report += "\n---\n\n"
    
    with open(export_file, 'w') as f:
        f.write(report)
    
    print(f"✅ Exported analysis timeline to: {export_file}")
    return export_file

def export_domain_convergence_report():
    """Export domain convergence patterns"""
    db = load_database()
    
    obsidian_dir = OBSIDIAN_EXPORT_DIR if OBSIDIAN_EXPORT_DIR.exists() else None
    if not obsidian_dir:
        obsidian_dir.mkdir(parents=True, exist_ok=True)
    
    export_file = obsidian_dir / "DOMAIN_CONVERGENCE_REPORT.md"
    
    core_symbols = db.get("core_processing", {})
    
    report = f"""# Domain Convergence Report

> **Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}  
> **Focus:** Multi-domain pattern convergence analysis  

---

## 🗺️ DOMAINS UNDER MONITORING

| Domain | Status | Last Activity | Core Symbols Tracked |
|--------|--------|---------------|----------------------|
"""
    
    domains = ["Volcanic", "Military", "Geographic", "Political", "Elemental"]
    for domain in domains:
        status = core_symbols.get(domain, {}).get("status", "Inactive")
        last_activity = core_symbols.get(domain, {}).get("last_activity", "Never")
        symbols_tracked = ", ".join(core_symbols.get(domain, {}).get("symbols", [])) or "N/A"
        report += f"| {domain} | {status} | {last_activity} | `{symbols_tracked}` |\n"
    
    # Add convergence events
    report += f"""---

## 🌉 CONVERGENCE EVENTS DETECTED

Events where multiple domains intersect:

"""
    
    convergence_events = core_symbols.get("convergence_events", [])
    for event in convergence_events[:10]:  # Top 10
        title = event.get("title", "Event")
        domains_involved = ", ".join(event.get("domains", []))
        timestamp = event.get("timestamp", "")
        
        report += f"### {timestamp}: {title}\n"
        report += f"**Domains:** `{domains_involved}`\n\n"
    
    # Add bridge connections by domain
    report += """---

## 🌉 BRIDGE CONNECTIONS BY DOMAIN

"""
    
    for symbol_id, data in sorted(core_symbols.items()):
        bridge_connections = data.get("bridge_connections", [])
        if bridge_connections:
            report += f"### Symbol {symbol_id}: {data.get('name', 'Unknown')}\n\n"
            report += "| Source | Status |\n"
            report += "|--------|--------|\n"
            for source in bridge_connections[:3]:  # Top 3 sources
                status = source.get("status", "Monitored") if isinstance(source, dict) else "N/A"
                report += f"| {source} | {status} |\n"
            report += "\n"
    
    with open(export_file, 'w') as f:
        f.write(report)
    
    print(f"✅ Exported domain convergence report to: {export_file}")
    return export_file

def export_pattern_matrix():
    """Export pattern matrix visualization"""
    db = load_database()
    
    obsidian_dir = OBSIDIAN_EXPORT_DIR if OBSIDIAN_EXPORT_DIR.exists() else None
    if not obsidian_dir:
        obsidian_dir.mkdir(parents=True, exist_ok=True)
    
    export_file = obsidian_dir / "PATTERN_MATRIX.md"
    
    core_symbols = db.get("core_processing", {})
    
    report = f"""# Pattern Matrix - Steve's Gematria System

> **Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}  
> **System Version:** 1.0  

---

## 🔢 SYMBOL MATRIX VISUALIZATION

```
┌─────────────────────────────────────────────────────────────────────┐
│                           PATTERN MATRIX                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│    WATER          AIR         EARTH        FIRE           SPIRIT     │
│   ──────          ◀───      ●───          ▲───       ✧───          │
│  [124]  ← Bridge ←              ↓↻                  →→             │
│    ──────         ───────     (279)        (55)            (111)    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

Key:
  ◀─── = Air/Frequency domain
  ●─── = Earth/Cycle domain  
  ▲─── = Fire/Transformation domain
  ✧─── = Spirit/Activation domain
```

---

## 📊 CORE SYMBOL METRICS

"""
    
    total_occurrences = sum(1 for s in core_symbols.values() if s)
    
    report += f"| Symbol | ID | Element | Total Occurrences | Bridge Connections |\n"
    report += "|--------|-----|---------|-------------------|--------------------|\n"
    
    for symbol_id, data in sorted(core_symbols.items()):
        if not data:
            continue
        
        name = data.get("name", "Unknown")
        element = data.get("element", "Unknown")
        total = sum(1 for item in core_symbols.values() if item.get("id") == symbol_id)
        
        bridge_count = len(data.get("bridge_connections", []))
        report += f"| {symbol_id} | {symbol_id} | {element} | {total} | {bridge_count} |\n"
    
    # Add convergence tracking section
    report += f"""---

## 🗺️ DOMAIN CONVERGENCE TRACKING

### Volcanic Domain:
- **Status:** `{core_symbols.get("Volcanic", {}).get('status', 'Inactive')}`
- **Core Symbols:** `{" / ".join(core_symbols.get("Volcanic", {}).get("symbols", [])) or "N/A"}`
- **Last Detection:** `{core_symbols.get("Volcanic", {}).get("last_activity", 'Never')}`

### Military Domain:
- **Status:** `{core_symbols.get("Military", {}).get('status', 'Inactive')}`  
- **Core Symbols:** `{" / ".join(core_symbols.get("Military", {}).get("symbols", [])) or "N/A"}`
- **Last Detection:** `{core_symbols.get("Military", {}).get("last_activity", 'Never')}`

### Geographic Domain:
- **Status:** `{core_symbols.get("Geographic", {}).get('status', 'Inactive')}`
- **Core Symbols:** `{" / ".join(core_symbols.get("Geographic", {}).get("symbols", [])) or "N/A"}`
- **Last Detection:** `{core_symbols.get("Geographic", {}).get("last_activity", 'Never')}`

---

## 🔗 GRAPH LINKS (for Obsidian Knowledge Graph)

### High-Priority Connections:

"""
    
    high_priority = core_symbols.get("666", {}).get("recent_high_impact_occurrences", [])[:5]
    for occ in high_priority:
        source = occ.get("source", "")
        title = occ.get("title", "")
        
        report += f"- [{source}](#{source.replace(' ', '-').lower()}) → `{title}`\n"
    
    # Add universal bridge tracker
    ub = core_symbols.get("124", {})
    report += f"""---

## 🌉 UNIVERSAL BRIDGE TRACKER (124 km³)

**Monitoring Active:** `{"✅ Yes" if ub.get('monitoring', True) else '❌ No'}`  
**Water Domain Status:** `{ub.get('water_domain_status', 'Not Monitored')}`

### Bridge Pattern Sources:
"""
    
    for source in [s.get("source") for s in core_symbols.values() for sub in s.get("bridge_connections", []) if isinstance(sub, str)][:10]:
        report += f"- `•` **{source}**\n"
    
    with open(export_file, 'w') as f:
        f.write(report)
    
    print(f"✅ Exported pattern matrix to: {export_file}")
    return export_file

def main():
    """Export all observations to Obsidian-compatible markdown"""
    print("=" * 60)
    print("🧬 STEVE'S GEMATRIA OBSIDIAN SYNC SCRIPT")
    print("=" * 60)
    
    exports = []
    
    try:
        # Export core symbols summary
        export_file = export_core_symbols_summary()
        exports.append(export_file)
        
        # Export analysis timeline
        export_file = export_analysis_timeline()
        exports.append(export_file)
        
        # Export domain convergence report
        export_file = export_domain_convergence_report()
        exports.append(export_file)
        
        # Export pattern matrix
        export_file = export_pattern_matrix()
        exports.append(export_file)
        
        print(f"\n✅ Total exports created: {len(exports)}")
        for f in exports:
            print(f"  - {f}")
            
    except Exception as e:
        print(f"❌ Export failed: {e}")
    
    return exports

if __name__ == "__main__":
    main()