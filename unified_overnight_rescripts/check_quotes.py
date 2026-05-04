#!/usr/bin/env python3
with open("/home/avalonas/.hermes/gematria/unified_overnight_research/scripts/composer_tolaria.py", "r") as f:
    content = f.read()

# Count triple-quote occurrences  
opens = content.count('"""')
print(f"Total \"\"\" occurrences: {opens}")
print(f"If all balanced: {opens % 2 == 0}")
