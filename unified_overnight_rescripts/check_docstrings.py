#!/usr/bin/env python3
"""Check composer_tolaria.py for unclosed docstrings."""

with open("/home/avalonas/.hermes/gematria/unified_overnight_research/scripts/composer_tolaria.py", "r") as f:
    lines = f.readlines()

# Count quotes on each line to find problematic ones
problematic_lines = []
for i, line in enumerate(lines, 1):
    # Count occurrences of triple quote marker
    opening = line.count('"""')
    if opening >= 1:
        closing_count = 3 - opening
        if closing_count != 0 and not '"""' in line[opening*3:]:
            # Need to check if it's properly closed on this line or continued
            print(f"Line {i}: Has opening but may need closing")
            
# Count total triple quotes per line across entire file  
total_counts = {}
for i, line in enumerate(lines, 1):
    count = line.count('"""')
    if count > 0:
        total_counts[i] = count

print(f"\nLines with multiple occurrences: {[(k,v) for k,v in sorted(total_counts.items()) if v > 1]}")
