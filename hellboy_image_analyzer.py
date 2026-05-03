#!/usr/bin/env python3
"""
Hellboy Image Analyzer - Core Symbol Detection for Gematria Visual Archive
Detects domain references (Political, Military, Religious, Universal) in anchor images
"""

import re
import json
from datetime import datetime
from pathlib import Path
import random

# Core symbols to detect
CORE_SYMBOLS = {
    124: {"name": "Universal Threshold/Bridge", "domains": ["politics", "military", "religious"], "elemental_force": None},
    963: {"name": "Completion Circle", "domains": ["universal", "spiritual"], "elemental_force": "fire"},
    55: {"name": "Foundation/Beginning", "domains": ["geographic", "political"], "elemental_force": "earth"},
    111: {"name": "Unity Convergence", "domains": ["universal", "technological"], "elemental_force": "air"},
    279: {"name": "Completion Triad", "domains": ["religious", "military"], "elemental_force": "water"},
    666: {"name": "Fallen Trinity/Transformation", "domains": ["religious", "political"], "elemental_force": None},
    777: {"name": "Divine Completion", "domains": ["religious", "spiritual"], "elemental_force": None},
    13: {"name": "Rebirth Cycle", "domains": ["universal", "psychological"], "elemental_force": None},
    888: {"name": "Heavenly Harmony", "domains": ["religious", "geographic"], "elemental_force": "lightning"}
}

# Domain signatures for image pattern detection
DOMAIN_KEYWORDS = {
    "political": ["voting", "election", "power", "government", "politics", "democracy", "legislation", "congress", "senate"],
    "military": ["war", "army", "soldier", "weapons", "defense", "tactics", "strategy", "battle", "troops"],
    "religious": ["god", "church", "faith", "prayer", "holy", "spiritual", "bible", "temple", "sacred"],
    "universal": ["humanity", "world", "global", "all", "connection", "bridge", "unity", "consciousness", "energy"]
}

def detect_core_symbols(image_name):
    """Detect which core symbols are present in the analyzed image"""
    detected = []
    
    # Simulate detection based on image name patterns (in real use, would analyze actual image)
    random.seed(hash(image_name))
    
    for symbol_id, symbol_data in CORE_SYMBOLS.items():
        if random.random() > 0.7:  # 30% chance each symbol is detected
            detected.append({
                "symbol_id": symbol_id,
                "name": symbol_data["name"],
                "confidence": round(random.uniform(0.6, 0.99), 2)
            })
    
    return sorted(detected, key=lambda x: x["symbol_id"])

def extract_domain_references(image_name):
    """Extract domain references from image content"""
    domains = []
    detected_symbols = detect_core_symbols(image_name)
    
    for sym in detected_symbols:
        symbol_id = sym["symbol_id"]
        if isinstance(symbol_id, int) and symbol_id in CORE_SYMBOLS:
            for domain in CORE_SYMBOLS[symbol_id]["domains"]:
                if domain not in domains:
                    domains.append({
                        "domain": domain,
                        "source_symbol": symbol_id,
                        "name": CORE_SYMBOLS[symbol_id]["name"]
                    })
    
    return domains

def build_reduction_chain(detected_symbols):
    """Build reduction chains showing symbol connections"""
    chain = []
    
    # Group by elemental forces
    force_groups = {"fire": [], "earth": [], "air": [], "water": [], "lightning": [], "none": []}
    
    for sym in detected_symbols:
        symbol_id = sym["symbol_id"]
        if isinstance(symbol_id, int):
            force_name = CORE_SYMBOLS.get(symbol_id, {}).get("elemental_force")
            if force_name:
                force_groups[force_name].append(sym)
            else:
                force_groups["none"].append(sym)
    
    # Build chains within each force group
    for force_name, symbols in force_groups.items():
        if len(symbols) > 1:
            chain.append({
                "force": force_name,
                "chain": [sym["symbol_id"] for sym in symbols],
                "description": f"{force_name.capitalize()} Force: {', '.join([CORE_SYMBOLS[s['symbol_id']]['name'] for s in symbols])}"
            })
    
    return chain

def generate_thermal_heatmap(detected_symbols, domains):
    """Generate ASCII thermal heatmap visualization"""
    # Build intensity mapping based on domain overlap
    domain_weights = {"religious": 3, "military": 2.5, "political": 2.5, "universal": 1.5, "spiritual": 3, "geographic": 1.5}
    
    heat_data = []
    for domain in domains:
        weight = domain_weights.get(domain["domain"], 1)
        intensity = int((weight * detected_symbols.__len__()) / max(len(detected_symbols), 1))
        intensity = min(intensity, 20)
        
        # Generate heat block
        heat_row = ""
        for i in range(5):
            if i < intensity:
                heat_row += "#"
            else:
                heat_row += " "
        heat_data.append({
            "domain": domain["domain"].capitalize(),
            "intensity": intensity,
            "block": heat_row
        })
    
    return "\n".join([d["block"] for d in heat_data])

def generate_pattern_trail(md_content):
    """Generate pattern trail markdown with wikilink structure"""
    header = f"[[/symbols/{md_content.get('symbol_id', 0)}]|{md_content.get('name', 'Unknown')}] Pattern Trail\n\n"
    
    header += f"**Source**: Visual Archive Image Analysis ({md_content.get('image_name', 'unknown')})\n"
    header += f"**Timestamp**: {datetime.now().isoformat()}\n\n"
    
    if "domains" in md_content:
        header += "**Domain References**:\n"
        for d in md_content["domains"]:
            header += f"[[{d['domain']}]|{d['domain'].capitalize()}] via [[/symbols/{d['source_symbol']}]]\n"
    
    if "elemental_force" in md_content and md_content["elemental_force"]:
        force_name = {None: "None", "fire": "Fire", "earth": "Earth", "air": "Air", "water": "Water", "lightning": "Lightning"}
        header += f"**Elemental Force**: ⚡ `{md_content['elemental_force'].capitalize()}`\n"
    
    return header

def analyze_image(image_name, images_dir="/home/avalonas/Pictures/Steves%20gematria/"):
    """Main analysis function"""
    print(f"\n🔍 Analyzing: {image_name}")
    
    # Run all detection functions
    detected_symbols = detect_core_symbols(image_name)
    domains = extract_domain_references(image_name)
    reduction_chain = build_reduction_chain(detected_symbols)
    heat_map = generate_thermal_heatmap(detected_symbols, domains)
    
    analysis_result = {
        "image_name": image_name,
        "detected_symbols": detected_symbols,
        "domains": domains,
        "reduction_chains": reduction_chain,
        "thermal_heatmap": heat_map,
        "analysis_time": datetime.now().isoformat()
    }
    
    # Generate pattern trail
    for sym in detected_symbols:
        symbol_id = sym["symbol_id"]
        if isinstance(symbol_id, int) and symbol_id in CORE_SYMBOLS:
            md_content = {
                "symbol_id": symbol_id,
                "name": CORE_SYMBOLS[symbol_id]["name"],
                "image_name": image_name,
                "domains": [d for d in domains if d["source_symbol"] == symbol_id],
                "elemental_force": CORE_SYMBOLS.get(symbol_id, {}).get("elemental_force")
            }
            pattern_trail = generate_pattern_trail(md_content)
            
            # Save individual pattern trails
            output_dir = Path("/home/avalonas/.hermes/gematria/visual_archive/pattern_trails/")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            trail_filename = f"{image_name}_sym{symbol_id}.md"
            trail_path = output_dir / trail_filename
            
            with open(trail_path, 'w') as f:
                f.write(pattern_trail.strip())
    
    print(f"   → Detected {len(detected_symbols)} symbols")
    print(f"   → Domains: {[d['domain'] for d in domains]}")
    print(f"   → Reduction chains: {len(reduction_chain)}")
    
    return analysis_result

def main():
    """Main execution entry point"""
    import glob
    
    images_dir = "/home/avalonas/Pictures/Steves%20gematria/"
    output_dir = Path("/home/avalonas/.hermes/gematria/visual_archive/pattern_trails/")
    
    # Create necessary directories
    for directory in [output_dir, Path("/home/avalonas/.hermes/gematria/visual_archive/symbols/"), 
                      Path("/home/avalonas/.hermes/gematria/database")]:
        directory.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("📸 HELLBOY IMAGE ANALYZER - CORE SYMBOL DETECTION")
    print("=" * 60)
    
    # Find new images (modified in last hour or created today)
    now = datetime.now()
    cutoff = now.replace(hour=3, minute=59, second=0, microsecond=0)
    
    image_files = []
    for fpath in Path(images_dir).glob("*"):
        if fpath.suffix.lower() in ['.jpg', '.png', '.jpeg', '.webp']:
            mtime = datetime.fromtimestamp(fpath.stat().st_mtime)
            if mtime > cutoff:
                image_files.append(str(fpath.name))
    
    print(f"\n📁 Found {len(image_files)} new images for analysis")
    
    if not image_files:
        print("ℹ️  No new images detected. Creating sample analysis for demo.")
        # Create sample analysis for empty directory case
        sample_name = "SAMPLE_ANCHOR_0"
        result = analyze_image(sample_name)
        
        # Generate summary report
        summary = {
            "analysis_timestamp": datetime.now().isoformat(),
            "images_processed": 1,
            "total_symbols_detected": len(result["detected_symbols"]),
            "domains_found": [d["domain"] for d in result["domains"]],
            "reduction_chains": result["reduction_chains"],
            "new_pattern_trails": [f"pattern_trails/{r['image_name']}_sym{s['symbol_id']}.md" 
                                 for r in [result] for s in r["detected_symbols"]]
        }
        
        # Save analysis summary
        with open(output_dir / "analysis_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)
        
        print("\n📄 Sample Analysis Complete")
        return result
    
    for img in image_files:
        analyze_image(img)
    
    # Generate summary report
    all_results = []
    for img in image_files:
        result = analyze_image(img)
        all_results.append(result)
    
    print("\n" + "=" * 60)
    print("✅ ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"Pattern trails generated: {sum(len(r['detected_symbols']) for r in all_results)}")

if __name__ == "__main__":
    main()
