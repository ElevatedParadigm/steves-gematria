#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Demo: Overnight Research Engine with Image Seed Foundation
============================================

This script demonstrates how to initialize overnight research 
with actual gematria patterns extracted from Pictures/Steves gematria folder.
"""

from pathlib import Path

# Paths
image_seed_path = Path('/home/avalonas/.hermes/gematria/database/gematria_database_image_seed.json')

print("=" * 80)
print("🔬 OVERNIGHT RESEARCH ENGINE - IMAGE-SEED FOUNDATION DEMO")
print("=" * 80)

# Check if image seed exists
if image_seed_path.exists():
    print(f"\n✅ Image seed file found: {image_seed_path}")
    
    # Load and display summary
    import json
    with open(image_seed_path) as f:
        seed_data = json.load(f)
    
    symbols_count = len(seed_data.get('symbols', {}))
    rels_count = len(seed_data.get('relationships', []))
    
    print(f"\n📊 Image-derived foundation loaded:")
    print(f"   • Symbols extracted: {symbols_count}")
    print(f"   • Relationships tracked: {rels_count}")
    print(f"   • Keywords collected: {len(seed_data.get('keywords', '').split())} words")
    
    print(f"\n📋 Top symbols from image analysis:")
    for i, (symbol_id, data) in enumerate(list(seed_data['symbols'].items())[:3], 1):
        print(f"   {i}. {symbol_id}: {data.get('context', 'N/A')[:50]}...")
    
    print(f"\n🔗 Key relationships:")
    for rel in seed_data['relationships'][:3]:
        source = rel.get('source', 'Unknown')[len('Owl Image Analysis'):60] if len(rel.get('source', '')) > 20 else rel.get('source', 'Unknown')
        target = rel.get('target', 'Unknown')[len('Religious Materialism Critique'):45] if len(rel.get('target', '')) > 20 else rel.get('target', 'Unknown')
        print(f"   • {source} → {target}")

    print(f"\n🚀 To run overnight research with this foundation:")
    print("   cd ~/.hermes/gematria")
    print("   python scripts/overnight_research_iterative_v4.py --image-seed")
else:
    print("\n⚠️  Image seed file not found. Creating...")
    
# Create sample query list from image foundation
initial_queries = [
    "124 universal bridge natural disaster divine prophecy multi-domain convergence",
    "IN GOD WE TRUST dollar sign substitution materialistic faith critique gematria",
    "JESUS 15131 Hebrew English gematria calculation method analysis",
    "Hurricane Sandy November 17 date volume 124 cubic kilometers gematria connection",
    "MAGMA LUCY stock market cryptic agents conspiracy numerology",
    "THE OWL SEES THE DARK prophecy wise observer symbolism gematria number"
]

print(f"\n📝 These queries will be used as foundation for initial research cycle!")
