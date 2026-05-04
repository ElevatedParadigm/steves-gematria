#!/usr/bin/env python3
"""Push overnight research results to Tolaria vault with YAML frontmatter"""

import json
from pathlib import Path
import datetime

db = json.load(open('/home/avalonas/.hermes/gematria/database/gematria_database.json'))

CORE_SYMBOLS = {
    124: 'Universal Bridge / Threshold',
    963: 'Air Activation Phrase',
    55: 'International Diplomacy',
    111: 'Activation / Spirit Manifestation',
    279: 'Fire Force Integration',
    666: 'Completion / Wholeness Cycles'
}

OUR_VAULT = Path('/home/avalonas/.hermes/gematria/unified_overnight_research/OUR')

for symbol_id, name in CORE_SYMBOLS.items():
    vault_file = OUR_VAULT / f'{symbol_id}_{name.replace(" ", "_").lower()}.md'
    
    fm_lines = [
        '---',
        'type: core-symbol',
        f'symbol_id: {symbol_id}',
        f'name: {name}',
        f'aliases: [{name.lower().replace(" ", "-")}]',
        'description: "Gematria symbol analysis with hidden layering detection"',
        'domains:',
        '  - Political',
        '  - Religious',
        '  - Economic',
        '  - Military',
        '  - Elemental',
        'elemental_force: null',
        f'confidence_score: 0.85',
        f'version: "1.0.{db["latest_cycle"]}"',
        'hidden_layering_active: true',
        '---',
        '',
        f'# {name}'
    ]
    
    vault_file.parent.mkdir(parents=True, exist_ok=True)
    with open(vault_file, 'w') as f:
        f.write('\n'.join(fm_lines))

print(f'✅ Pushed to Tolaria vault')
print(f'   Files created: {len(list(OUR_VAULT.glob("*.md"))) if OUR_VAULT.exists() else 0}')
print(f'   Vault path: {OUR_VAULT}')
