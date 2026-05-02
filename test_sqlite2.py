#!/usr/bin/env python3
import sqlite3

# Test remaining tables
tables = [
    ("analysis_metrics", """
        CREATE TABLE test_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            symbols_detected TEXT,
            domain_scores TEXT,
            elemental_activations TEXT,
            findings TEXT,
            anomalies_detected BOOLEAN DEFAULT FALSE,
            source_batch_id TEXT
        )
    """),
    ("overnight_research_logs", """
        CREATE TABLE test_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            url_scraped TEXT,
            scrape_success BOOLEAN,
            content_length INTEGER,
            symbols_found TEXT,
            domains_identified TEXT
        )
    """),
]

for table_name, sql in tables:
    print(f"Testing {table_name}...")
    try:
        conn = sqlite3.connect(':memory:')
        conn.execute(sql)
        conn.close()
        print(f"  ✅ {table_name} OK")
    except Exception as e:
        print(f"  ❌ {table_name} FAILED: {e}")

# Now test indexes
print("\nTesting indexes...")
conn = sqlite3.connect(':memory:')

try:
    conn.execute("CREATE TABLE entities (id INTEGER PRIMARY KEY, symbol_value TEXT)")
    
    # Test GREATEST/LEAST index syntax
    conn.execute("""
        CREATE INDEX idx_test ON entities(
            LEAST(id, 1), GREATEST(id, 2)
        )
    """)
    print("  ✅ GREATEST/LEAST OK")
except Exception as e:
    print(f"  ❌ GREATEST/LEAST FAILED: {e}")
    
conn.close()

# Test FTS5
print("\nTesting FTS5...")
try:
    conn = sqlite3.connect(':memory:')
    conn.execute("""
        CREATE VIRTUAL TABLE fts_test USING fts5(
            name,
            description
        )
    """)
    print("  ✅ FTS5 OK")
except Exception as e:
    print(f"  ❌ FTS5 FAILED: {e}")
    
conn.close()

print("\n✅ All tests complete!")
