#!/usr/bin/env python3
"""Simple fix: replace only line 133 in .env file."""

path = "/home/avalonas/.hermes/.env"
api_key = "fc-31c6892b44ba42e9aa8013ccd4ac5a6a"

# Read all lines
with open(path, 'r') as f:
    lines = f.readlines()

# Find and replace line 133 (index 132) - specifically the commented FIRECRAWL_API_KEY line
new_lines = []
for i, line in enumerate(lines):
    if i == 132 and line.strip() == "# FIRECRAWL_API_KEY=***":
        # Replace with actual key
        new_lines.append(f"FIRECRAWL_API_KEY={api_key}\n")
        print(f"✓ Replaced line {i+1}: removed comment, added key")
    else:
        new_lines.append(line)

# Write back
with open(path, 'w') as f:
    f.writelines(new_lines)

print(f"✓ API key configured in {path}")
print(f"  FIRECRAWL_API_KEY={api_key[:3]}***{api_key[-4:]}")
