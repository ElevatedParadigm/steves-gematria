#!/usr/bin/env python3
"""Find unclosed docstrings by checking line by line."""

with open("/home/avalonas/.hermes/gematria/unified_overnight_research/scripts/composer_tolaria.py", "r") as f:
    lines = f.readlines()

print("Checking for problematic lines with just opening triple quotes:\n")

for i, line in enumerate(lines, 1):
    stripped = line.strip()
    if stripped.startswith('"""') and not stripped.endswith('"""'):
        # This is an unclosed docstring on the same line
        content_between = stripped[len('"""'):stripped.rfind('"""')]
        print(f"Line {i}: STARTS with opening but doesn't close")
        print(f"  Raw: {repr(line[:60])}")
        print()

# Now check lines that are just """ followed by newline (opening marker)
print("\nChecking continuation lines (just opening marker):")
for i, line in enumerate(lines, 1):
    stripped = line.rstrip()
    if stripped == '"""':
        next_line_content = ""
        if i < len(lines):
            next_line_content = lines[i].rstrip()[:80]
        print(f"Line {i}: Just opening marker")
        print(f"  Next line preview: {repr(next_line_content[:50])}")
        print()
