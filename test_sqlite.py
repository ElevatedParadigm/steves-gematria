#!/usr/bin/env python3
import sqlite3

# Try each CREATE TABLE individually
tables = [
    ("entities", """
        CREATE TABLE test_entities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            symbol_value TEXT,
            elemental_force TEXT,
            primary_domain TEXT,
            secondary_domains TEXT,
            embedding TEXT,
            relevance_score REAL DEFAULT 0.0,
            source_url TEXT,
            first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """),
    ("relationships", """
        CREATE TABLE test_relationships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_a_id INTEGER,
            entity_b_id INTEGER,
            relationship_type TEXT NOT NULL,
            relationship_strength REAL DEFAULT 1.0,
            description TEXT,
            context_fields TEXT,
            source_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (entity_a_id) REFERENCES test_entities(id),
            FOREIGN KEY (entity_b_id) REFERENCES test_entities(id)
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
