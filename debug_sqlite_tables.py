#!/usr/bin/env python3
import re
import sqlite3

# Read the script and extract each CREATE TABLE definition
with open('/home/avalonas/.hermes/gematria/scripts/sqlite_knowledge_graph.py', 'r') as f:
    content = f.read()

print("Extracting table definitions from script...\n")

# Simple extraction - find each CREATE TABLE block
table_names = []
current_table = None
brace_depth = 0
table_start = -1

for i, char in enumerate(content):
    if 'CREATE TABLE IF NOT EXISTS' in content[max(0,i-20):i+50]:
        match = re.search(r'CREATE TABLE IF NOT EXISTS (\w+)\s*\(', content[i:])
        if match:
            table_name = match.group(1)
            table_names.append(table_name)
            table_start = i
            
print(f"Found {len(table_names)} tables:")
for t in table_names:
    print(f"  - {t}")

# Now try creating each one
conn = sqlite3.connect(':memory:')
created = 0
failed = 0

for table_name in table_names:
    # Find this table's CREATE statement up to the next table or end of block
    start = content.find(f'CREATE TABLE IF NOT EXISTS {table_name}')
    if start == -1:
        continue
        
    # Find matching closing parenthesis for this table definition
    # Count brackets to find proper end
    paren_count = 0
    found_open = False
    
    for j in range(start, min(start + 2000, len(content))):
        if content[j] == '(':
            paren_count += 1
            found_open = True
        elif content[j] == ')':
            paren_count -= 1
            if found_open and paren_count == 0:
                # End of this table definition
                sql = content[start:j+2]
                break
    
    try:
        conn.execute(sql)
        print(f"  ✅ {table_name}")
        created += 1
    except Exception as e:
        print(f"  ❌ {table_name}: {str(e)[:80]}")
        failed += 1

conn.close()

print(f"\nSummary: {created} created, {failed} failed")
