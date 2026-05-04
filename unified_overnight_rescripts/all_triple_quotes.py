#!/usr/bin/env python3
"""Find all unclosed docstrings by line."""
with open("/home/avalonas/.hermes/gematria/unified_overnight_research/scripts/composer_tolaria.py", "r") as f:
    lines = f.readlines()

quote_count = 0
unclosed_start = None

for i, line in enumerate(lines, 1):
    opening = line.count('"""')
    if opening > 0 and opening % 2 != 0:
        print(f"Line {i}: Has {opening} opening triple-quote(s)")
        print(f"  Content preview: {repr(line[:80])}")

print("\n\nAll lines with triple quotes:")
for i, line in enumerate(lines, 1):
    count = line.count('"""')
    if count > 0:
        print(f"{i}: {count}x - {repr(line.rstrip()[:60])}")
