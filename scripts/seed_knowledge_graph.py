#!/usr/bin/env python3
"""
🧙‍♂️ Seed Knowledge Graph with Core Gematria Entities
============================================================
Populates PostgreSQL with fundamental gematria symbols, domains, 
and elemental forces for scalable relationship tracking.

© Steve's Gematria System - Maintained by Avalon & Steve
============================================================
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / ".hermes" / "gematria" / "scripts"))

from knowledge_graph_manager import GematriaKnowledgeGraph


def seed_core_symbols():
    """Seed fundamental gematria core symbols."""
    
    CORE_SYMBOLS = [
        {
            "name": "124 - Universal Bridge",
            "symbol_value": "124",
            "elemental_force": "Water",
            "primary_domain": "Universal",
            "description": "The Universal Threshold/Bridge that connects all domains; appears across political events, Epstein files analysis, and geopolitical patterns"
        },
        {
            "name": "963 - Frequency/Air", 
            "symbol_value": "963",
            "elemental_force": "Air",
            "primary_domain": "Frequency",
            "description": "Frequency/Air cycle variant; found in Epstein files analysis, Trump Canada narrative imagery; represents vibrational patterns"
        },
        {
            "name": "55 - Fire/Elemental Force",
            "symbol_value": "55",
            "elemental_force": "Fire",
            "primary_domain": "Elemental",
            "description": "Fire/Elemental force; multiple locations across political and military domains; represents transformation through fire"
        },
        {
            "name": "111 - Activation/Spirit",
            "symbol_value": "111",
            "elemental_force": "Spirit",
            "primary_domain": "Activation",
            "description": "Activation/Spirit; found in powerful men Epstein files overlay; represents spirit/activation forces"
        },
        {
            "name": "279 - Cycle Turning",
            "symbol_value": "279",
            "elemental_force": "Earth",
            "primary_domain": "Cyclic",
            "description": "Cycle Turning; Military Coup equation (49+39+21+97+36+37=279); Earth transformation through cycles"
        },
        {
            "name": "666 - Completion/Wholeness",
            "symbol_value": "666",
            "elemental_force": "Fire",
            "primary_domain": "Completion",
            "description": "Completion/Wholeness; transforms to 9 via reduction; represents wholeness and fire completion cycles"
        },
        {
            "name": "66 - Completion Reduced",
            "symbol_value": "66",
            "elemental_force": "Fire",
            "primary_domain": "Completion",
            "description": "666 reduced; represents wholeness/fire completion in condensed form"
        },
        {
            "name": "17 - Vessel/Holds Fire",
            "symbol_value": "17",
            "elemental_force": "Fire",
            "primary_domain": "Vessel",
            "description": "Vessel that holds the fire; reduces to 8 (structure/grounding); represents containment of elemental force"
        }
    ]
    
    print("🌱 Seeding Core Gematria Symbols...")
    print("=" * 80)
    
    kg = GematriaKnowledgeGraph()
    if not kg.connect():
        print("Cannot connect to database.")
        return
    
    for i, symbol in enumerate(CORE_SYMBOLS, 1):
        print(f"\n[{i}/{len(CORE_SYMBOLS)}] Seeding: {symbol['name']}")
        
        try:
            # Generate embedding with semantic context
            text = f"{symbol['name']} {symbol['description']}"
            embedding = kg.generate_embedding(text) if embedding is None else None
            
            entity_id = kg.add_entity(
                name=symbol["name"],
                symbol_value=symbol["symbol_value"],
                elemental_force=symbol["elemental_force"],
                primary_domain=symbol["primary_domain"],
                secondary_domains=[],
                embedding=embedding,
                relevance_score=1.0,  # Core symbols have maximum relevance
                search_text=f"{symbol['name']} {symbol['description']}",
                source_url="https://github.com/avalonas/.hermes"
            )
            
            print(f"    ✅ Added core symbol {symbol['symbol_value']} (ID: {entity_id})")
            
        except Exception as e:
            print(f"    ⚠️  Could not seed {symbol['name']}: {e}")
    
    kg.disconnect()
    
    print("\n" + "=" * 80)
    print("✅ Core gematria symbols seeded successfully!")


def seed_core_domains():
    """Seed core domains tracked in gematria system."""
    
    DOMAINS = [
        {
            "name": "Political",
            "primary_domain": "Political",
            "description": "Political events, elections, policy analysis, congressional activity, electoral processes"
        },
        {
            "name": "Military",
            "primary_domain": "Military", 
            "description": "Military operations, coups, deployments, armed forces, tactical operations, weapons systems"
        },
        {
            "name": "Elemental",
            "primary_domain": "Elemental",
            "description": "Elemental forces, fire phenomena, volcanic activity, atmospheric events, natural transformations"
        },
        {
            "name": "Religious",
            "primary_domain": "Religious",
            "description": "Religious symbolism, spiritual traditions, sacred texts, faith-based organizations, metaphysical concepts"
        },
        {
            "name": "Geopolitical",
            "primary_domain": "Geopolitical",
            "description": "International relations, border conflicts, sovereign states, geopolitical strategy, nation-state dynamics"
        }
    ]
    
    print("\n🌱 Seeding Core Domains...")
    print("=" * 80)
    
    kg = GematriaKnowledgeGraph()
    if not kg.connect():
        return
    
    for i, domain in enumerate(DOMAINS, 1):
        print(f"\n[{i}/{len(DOMAINS)}] Seeding: {domain['name']}")
        
        try:
            entity_id = kg.add_entity(
                name=f"Domain [{domain['primary_domain']}] - {domain['name']}",
                symbol_value=None,
                elemental_force=None,
                primary_domain=domain["primary_domain"],
                secondary_domains=[],
                embedding=None,  # Domain categories don't need vector embeddings initially
                relevance_score=0.95,
                search_text=f"{domain['name']} {domain['description']}",
                source_url="https://github.com/avalonas/.hermes"
            )
            
            print(f"    ✅ Added domain entity (ID: {entity_id})")
            
        except Exception as e:
            print(f"    ⚠️  Could not seed {domain['name']}: {e}")
    
    kg.disconnect()
    
    print("\n" + "=" * 80)
    print("✅ Core domains seeded successfully!")


def seed_elemental_forces():
    """Seed elemental forces for relationship tracking."""
    
    ELEMENTAL = [
        {
            "name": "Fire",
            "elemental_force": "Fire",
            "primary_domain": "Elemental",
            "description": "Transformation, combustion, volcanic activity, energetic manifestation"
        },
        {
            "name": "Water", 
            "elemental_force": "Water",
            "primary_domain": "Elemental",
            "description": "Flow, adaptation, emotional intelligence, universal connectivity"
        },
        {
            "name": "Air",
            "elemental_force": "Air",
            "primary_domain": "Elemental", 
            "description": "Frequency, vibration, thought patterns, information transmission"
        },
        {
            "name": "Earth",
            "elemental_force": "Earth",
            "primary_domain": "Elemental",
            "description": "Stability, cycles, grounding, material manifestation"
        }
    ]
    
    print("\n🌱 Seeding Elemental Forces...")
    print("=" * 80)
    
    kg = GematriaKnowledgeGraph()
    if not kg.connect():
        return
    
    for elemental in ELEMENTAL:
        try:
            entity_id = kg.add_entity(
                name=f"Elemental Force - {elemental['elemental_force']}",
                symbol_value=None,
                elemental_force=elemental["elemental_force"],
                primary_domain=elemental["primary_domain"],
                secondary_domains=[],
                embedding=None,
                relevance_score=0.90,
                search_text=f"{elemental['elemental_force']} elemental force {elemental['description']}",
                source_url="https://github.com/avalonas/.hermes"
            )
            
            print(f"    ✅ Added elemental force (ID: {entity_id})")
            
        except Exception as e:
            print(f"    ⚠️  Could not seed elemental force {elemental['elemental_force']}: {e}")
    
    kg.disconnect()
    
    print("\n" + "=" * 80)
    print("✅ Elemental forces seeded successfully!")


def create_core_symbol_relationships():
    """Create bidirectional relationships between core symbols."""
    
    # Symbol value indices for reference
    SYMBOLS = {
        "124": {"name": "124 - Universal Bridge"},
        "963": {"name": "963 - Frequency/Air"},
        "55": {"name": "55 - Fire/Elemental Force"},
        "111": {"name": "111 - Activation/Spirit"},
        "279": {"name": "279 - Cycle Turning"},
        "666": {"name": "666 - Completion/Wholeness"},
    }
    
    print("\n🔗 Creating Core Symbol Relationships...")
    print("=" * 80)
    
    kg = GematriaKnowledgeGraph()
    if not kg.connect():
        return
    
    # Create bidirectional relationships between all core symbols
    symbol_values = list(SYMBOLS.keys())
    
    for i, sym1 in enumerate(symbol_values):
        entity_a_id = None
        
        try:
            # Get entity A ID
            cursor = kg.pool.getconn().cursor()
            cursor.execute("SELECT id FROM gematria_entities WHERE symbol_value = %s", (sym1,))
            result = cursor.fetchone()
            if result:
                entity_a_id = result['id']
            
            for sym2 in symbol_values[i+1:]:
                # Create cross-reference relationship
                kg.add_relationship(
                    entity_a_id=entity_a_id,
                    entity_b_id=None,  # Will be looked up
                    relationship_type="cross_references",
                    strength=0.85,
                    description=f"Core symbol {sym1} connects to symbol {sym2}",
                    context_fields={"type": "symbol_to_symbol"}
                )
            
        except Exception as e:
            print(f"    ⚠️  Could not create relationships for {sym1}: {e}")
    
    kg.disconnect()
    
    print("\n" + "=" * 80)
    print("✅ Core symbol relationships created!")


def main():
    """Run complete seeding process."""
    
    print("=" * 80)
    print("🧙‍♂️  STEVE'S GEMATRIA KNOWLEDGE GRAPH - SEEDING INITIALIZATION")
    print("=" * 80)
    
    # Step 1: Seed core symbols
    seed_core_symbols()
    
    # Step 2: Seed core domains  
    seed_core_domains()
    
    # Step 3: Seed elemental forces
    seed_elemental_forces()
    
    # Step 4: Create symbol relationships (optional - can be skipped initially)
    print("\n📝 Note: Core symbol relationships are optional.")
    print("      They will be created automatically during overnight research.")
    print("=" * 80)
    
    # Get stats
    from knowledge_graph_manager import GematriaKnowledgeGraph
    kg = GematriaKnowledgeGraph()
    if kg.connect():
        stats = kg.get_stats()
        print(f"\n📊 Final Statistics:")
        print(f"   Total Entities: {stats.get('entity_count', 0)}")
        print(f"   Relationships: {stats.get('relationship_count', 0)}")
        print(f"   Core Symbols: {stats.get('core_symbols_count', 0)}")
        kg.disconnect()


if __name__ == "__main__":
    main()
