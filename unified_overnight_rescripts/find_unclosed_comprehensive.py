#!/usr/bin/env python3
"""Find all unclosed docstrings by line - comprehensive."""
with open("/home/avalonas/.hermes/gematria/unified_overnight_research/scripts/composer_tolaria.py", "r") as f:
    lines = f.readlines()

print("=== All lines with odd number of triple quotes (potential issues) ===\n")
for i, line in enumerate(lines, 1):
    count = line.count('"""')
    if count % 2 == 1:
        print(f"Line {i}: {count}x - {repr(line.rstrip()[:80])}")
