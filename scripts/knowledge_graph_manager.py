#!/usr/bin/env python3
"""
🧙‍♂️ STEVE'S GEMATRIA KNOWLEDGE GRAPH MANAGER
============================================================
PostgreSQL + pgvector implementation for scalable, precise relationship tracking.

© Steve's Gematria System - Maintained by Avalon & Steve
============================================================
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
import psycopg2
from psycopg2.extras import RealDictCursor

# Try to import pgvector for vector similarity
try:
    import psycopg2.pool
except ImportError:
    print("⚠️  psycopg2 not installed. Run: pip install psycopg2-binary")
    
try:
    from sentence_transformers import SentenceTransformer
    VECTOR_AVAILABLE = True
except ImportError:
    VECTOR_AVAILABLE = False
    print("⚠️  SentenceTransformers not available for embeddings. Using placeholder vectors.")


# Database configuration (adjust as needed)
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "gematria_db",
    "user": "gematria",
    "password": "gematria123"
}

KG_DIR = Path.home() / ".hermes" / "gematria"


class GematriaKnowledgeGraph:
    """
    🧙‍♂️ PostgreSQL-based knowledge graph for gematria pattern scaling.
    
    Features:
    - Entity CRUD with vector embeddings for semantic similarity
    - Relationship tracking between symbols, domains, concepts
    - Efficient indexing for sub-millisecond lookups
    - Full-text search via GIN indexes
    - Batch operations for overnight research data
    
    © Steve's Gematria System
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the knowledge graph manager."""
        self.config = {**DB_CONFIG, **(config or {})}
        self.pool = None  # Will be initialized with connection
    
    def connect(self) -> bool:
        """Establish database connection pool."""
        try:
            self.pool = psycopg2.pool.SimplePoolingPool(
                minconn=1,
                maxconn=20,
                host=self.config["host"],
                port=self.config["port"],
                dbname=self.config["dbname"],
                user=self.config["user"],
                password=self.config["password"]
            )
            print(f"✅ Knowledge Graph connected to PostgreSQL at {self.config['host']}:{self.config['port']}")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def disconnect(self):
        """Close database connection pool."""
        if self.pool:
            self.pool.closeall()
    
    # ================================
    # ENTITY OPERATIONS
    # ================================
    
    def add_entity(
        self,
        name: str,
        symbol_value: Optional[str] = None,
        elemental_force: Optional[str] = None,
        primary_domain: Optional[str] = None,
        secondary_domains: Optional[List[str]] = None,
        embedding: Optional[Any] = None,
        relevance_score: float = 0.0,
        search_text: Optional[str] = None,
        source_url: Optional[str] = None
    ) -> int:
        """
        Add a new entity to the knowledge graph.
        
        Args:
            name: Entity name (e.g., "124 Universal Bridge")
            symbol_value: Core symbol value (e.g., '124', '963')
            elemental_force: Elemental classification (Fire, Water, Air, Earth)
            primary_domain: Primary domain (Political, Military, etc.)
            secondary_domains: List of additional domains
            embedding: Vector embedding for semantic similarity (optional)
            relevance_score: Relevance score 0-1
            search_text: Full-text searchable content
        
        Returns:
            Entity ID (SERIAL primary key)
        """
        try:
            with self.pool.getconn() as conn:
                cursor = conn.cursor()
                
                # Insert entity
                cursor.execute("""
                    INSERT INTO gematria_entities (
                        name, symbol_value, elemental_force, primary_domain,
                        secondary_domains, embedding, relevance_score, search_text, source_url
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (name, symbol_value, elemental_force, primary_domain, 
                      json.dumps(secondary_domains) if secondary_domains else None,
                      embedding, relevance_score, search_text, source_url))
                
                conn.commit()
                entity_id = cursor.fetchone()[0]
                
                print(f"  ➕ Added entity: {name} (ID: {entity_id})")
                return entity_id
                
        except Exception as e:
            print(f"  ❌ Error adding entity: {e}")
            raise
    
    def add_entities_batch(
        self,
        entities: List[Dict[str, Any]],
        batch_size: int = 100
    ) -> int:
        """
        Add multiple entities in a single batch operation.
        
        Args:
            entities: List of entity dicts with keys matching add_entity() parameters
            batch_size: Maximum entities per INSERT statement
        
        Returns:
            Number of entities added
        """
        total_added = 0
        
        for i in range(0, len(entities), batch_size):
            batch = entities[i:i + batch_size]
            
            try:
                with self.pool.getconn() as conn:
                    placeholders = ','.join(['%s'] * len(batch))
                    columns = [
                        'name', 'symbol_value', 'elemental_force', 'primary_domain',
                        'secondary_domains', 'embedding', 'relevance_score', 
                        'search_text', 'source_url'
                    ]
                    
                    query = f"""
                        INSERT INTO gematria_entities ({', '.join(columns)})
                        VALUES ({placeholders})
                        RETURNING id
                    """
                    
                    cursor = conn.cursor()
                    data = []
                    for entity in batch:
                        record = (
                            entity['name'],
                            entity.get('symbol_value'),
                            entity.get('elemental_force'),
                            entity.get('primary_domain'),
                            json.dumps(entity.get('secondary_domains')) if entity.get('secondary_domains') else None,
                            entity.get('embedding'),
                            entity.get('relevance_score', 0.0),
                            entity.get('search_text'),
                            entity.get('source_url')
                        )
                        data.append(record)
                    
                    cursor.executemany(query, data)
                    conn.commit()
                    
                    total_added += len(batch)
                    print(f"  ➕ Batch inserted {len(batch)} entities")
                    
            except Exception as e:
                print(f"  ❌ Batch insert failed: {e}")
        
        return total_added
    
    def update_entity(self, entity_id: int, **kwargs) -> bool:
        """Update an existing entity's fields."""
        set_clause = ', '.join([f"{k}=%s" for k in kwargs.keys()])
        values = list(kwargs.values()) + [entity_id]
        
        try:
            with self.pool.getconn() as conn:
                cursor = conn.cursor()
                cursor.execute(f"""
                    UPDATE gematria_entities 
                    SET {set_clause}, last_updated = NOW()
                    WHERE id = %s
                """, values)
                conn.commit()
                
                if cursor.rowcount > 0:
                    print(f"  ✏️  Updated entity {entity_id}")
                    return True
                return False
                
        except Exception as e:
            print(f"  ❌ Error updating entity: {e}")
            return False
    
    def get_entity(self, entity_id: int) -> Optional[Dict[str, Any]]:
        """Get a single entity by ID."""
        try:
            with self.pool.getconn() as conn:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute("SELECT * FROM gematria_entities WHERE id = %s", (entity_id,))
                result = cursor.fetchone()
                
                if result:
                    # Convert JSON array back to Python list
                    if 'secondary_domains' in result and result['secondary_domains']:
                        result['secondary_domains'] = json.loads(result['secondary_domains'])
                    return dict(result)
                return None
                
        except Exception as e:
            print(f"  ❌ Error getting entity: {e}")
            return None
    
    def get_entities_by_symbol(self, symbol_value: str) -> List[Dict[str, Any]]:
        """Get all entities with a specific core symbol value."""
        try:
            with self.pool.getconn() as conn:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute("SELECT * FROM gematria_entities WHERE symbol_value = %s", (symbol_value,))
                results = cursor.fetchall()
                
                # Convert JSON arrays and objects
                for row in results:
                    if 'secondary_domains' in row and row['secondary_domains']:
                        row['secondary_domains'] = json.loads(row['secondary_domains'])
                
                return list(results)
                
        except Exception as e:
            print(f"  ❌ Error querying entities by symbol: {e}")
            return []
    
    # ================================
    # RELATIONSHIP OPERATIONS
    # ================================
    
    def add_relationship(
        self,
        entity_a_id: int,
        entity_b_id: int,
        relationship_type: str,
        strength: float = 1.0,
        description: Optional[str] = None,
        context_fields: Optional[Dict[str, Any]] = None,
        source_url: Optional[str] = None
    ) -> bool:
        """
        Add a relationship between two entities.
        
        Ensures bidirectional relationships are stored correctly and avoids duplicates.
        """
        try:
            with self.pool.getconn() as conn:
                cursor = conn.cursor()
                
                # Use the add_relationship function
                cursor.execute("""
                    SELECT add_relationship(%s, %s, %s, %s, %s, %s, %s)
                """, (entity_a_id, entity_b_id, relationship_type, strength,
                      description, json.dumps(context_fields) if context_fields else '{}', source_url))
                
                relationship_id = cursor.fetchone()[0]
                conn.commit()
                
                print(f"  ➕ Added relationship: {relationship_type} ({entity_a_id} ↔ {entity_b_id})")
                return True
                
        except Exception as e:
            print(f"  ❌ Error adding relationship: {e}")
            return False
    
    def add_relationships_batch(
        self,
        relationships: List[Dict[str, Any]],
        batch_size: int = 50
    ) -> int:
        """Add multiple relationships in a batch."""
        total_added = 0
        
        for i in range(0, len(relationships), batch_size):
            batch = relationships[i:i + batch_size]
            
            try:
                with self.pool.getconn() as conn:
                    placeholders = ','.join(['%s'] * len(batch))
                    columns = [
                        'entity_a_id', 'entity_b_id', 'relationship_type',
                        'relationship_strength', 'description', 'context_fields', 'source_url'
                    ]
                    
                    query = f"""
                        INSERT INTO gematria_relationships ({', '.join(columns)})
                        VALUES ({placeholders})
                        ON CONFLICT (LEAST(entity_a_id, entity_b_id), GREATEST(entity_a_id, entity_b_id), relationship_type)
                        DO UPDATE SET
                            relationship_strength = EXCLUDED.relationship_strength::DECIMAL(5,2),
                            description = EXCLUDED.description
                    """
                    
                    cursor = conn.cursor()
                    data = []
                    for rel in batch:
                        record = (
                            rel['entity_a_id'],
                            rel['entity_b_id'],
                            rel['relationship_type'],
                            rel.get('strength', 1.0),
                            rel.get('description'),
                            json.dumps(rel.get('context_fields')) if rel.get('context_fields') else '{}',
                            rel.get('source_url')
                        )
                        data.append(record)
                    
                    cursor.executemany(query, data)
                    conn.commit()
                    
                    total_added += len(batch)
                    print(f"  ➕ Batch inserted {len(batch)} relationships")
                    
            except Exception as e:
                print(f"  ❌ Batch relationship insert failed: {e}")
        
        return total_added
    
    def get_relationships_for_entity(self, entity_id: int) -> List[Dict[str, Any]]:
        """Get all relationships connected to an entity."""
        try:
            with self.pool.getconn() as conn:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute("""
                    SELECT r.relationship_type, e.id as target_id, r.relationship_strength, r.description
                    FROM gematria_relationships r
                    JOIN gematria_entities e ON (
                        (r.entity_a_id = %s AND r.entity_b_id = e.id) OR
                        (r.entity_b_id = %s AND r.entity_a_id = e.id)
                    )
                    ORDER BY r.relationship_strength DESC
                """, (entity_id, entity_id))
                
                results = cursor.fetchall()
                return list(results)
                
        except Exception as e:
            print(f"  ❌ Error getting entity relationships: {e}")
            return []
    
    def get_relationships_between(self, entity_a_id: int, entity_b_id: int) -> List[Dict[str, Any]]:
        """Get all relationships between two specific entities."""
        try:
            with self.pool.getconn() as conn:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                min_id = min(entity_a_id, entity_b_id)
                max_id = max(entity_a_id, entity_b_id)
                
                cursor.execute("""
                    SELECT relationship_type, relationship_strength, description, source_url
                    FROM gematria_relationships
                    WHERE (entity_a_id = %s AND entity_b_id = %s) OR 
                          (entity_b_id = %s AND entity_a_id = %s)
                """, (entity_a_id, entity_b_id, entity_b_id, entity_a_id))
                
                return list(cursor.fetchall())
                
        except Exception as e:
            print(f"  ❌ Error getting relationships between entities: {e}")
            return []
    
    # ================================
    # SIMILARITY SEARCH (Vector)
    # ================================
    
    def find_similar_entities(
        self,
        query_embedding: Any,
        limit: int = 10,
        min_similarity: float = 0.70
    ) -> List[Tuple[int, str, float]]:
        """
        Find entities semantically similar to a query embedding.
        
        Args:
            query_embedding: Vector embedding (list of floats or numpy array)
            limit: Maximum number of results
            min_similarity: Minimum cosine similarity threshold
        
        Returns:
            List of tuples: (entity_id, name, similarity_score)
        """
        try:
            with self.pool.getconn() as conn:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                
                query = f"""
                    SELECT id, name, symbol_value, 
                           1 - (%s <=> embedding) as similarity
                    FROM gematria_entities
                    WHERE (embedding <=> %s) < (1 - {min_similarity})
                    ORDER BY (embedding <=> %s)
                    LIMIT %s
                """
                
                cursor.execute(query, (query_embedding, query_embedding, query_embedding, limit))
                return list(cursor.fetchall())
                
        except Exception as e:
            print(f"  ❌ Error in similarity search: {e}")
            return []
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate a vector embedding for text using SentenceTransformers.
        
        Args:
            text: Text to embed
        
        Returns:
            List of floats (384-dimensional) or None if embedding not available
        """
        if not VECTOR_AVAILABLE:
            print("  ⚠️  Vector embeddings disabled. Using placeholder vectors.")
            # Generate a deterministic but non-matching placeholder
            return [0.5] * 384
        
        try:
            model = SentenceTransformer('all-MiniLM-L6-v2')
            embedding = model.encode(text)
            
            # Normalize to cosine similarity space (L2 norm)
            import numpy as np
            normalized = embedding / np.linalg.norm(embedding)
            
            return normalized.tolist()
            
        except Exception as e:
            print(f"  ⚠️  Embedding generation failed: {e}")
            return None
    
    # ================================
    # QUERIES & ANALYSIS
    # ================================
    
    def get_symbol_cross_references(self, symbol_value: str) -> List[Dict[str, Any]]:
        """Get all cross-references for a specific symbol."""
        try:
            with self.pool.getconn() as conn:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                
                min_id = 1
                max_id = 999999999  # Large number for LEAST/GREATEST
                
                query = f"""
                    SELECT r.relationship_type, e.id as target_id, 
                           e.name, e.symbol_value, r.description, r.source_url
                    FROM gematria_relationships r
                    JOIN gematria_entities e ON (
                        (r.entity_a_id = {min_id} AND r.entity_b_id = e.id) OR
                        (r.entity_b_id = {min_id} AND r.entity_a_id = e.id)
                    )
                    WHERE r.relationship_type ILIKE '%cross_reference%'
                """
                
                # Need to use a subquery or CTE for actual symbol filtering
                cursor.execute(f"""
                    SELECT 
                        r.relationship_type,
                        e2.id as target_id,
                        e2.name,
                        e2.symbol_value,
                        r.description,
                        r.source_url
                    FROM gematria_relationships r
                    JOIN gematria_entities e1 ON r.entity_a_id = e1.id OR r.entity_b_id = e1.id
                    JOIN gematria_entities e2 ON (
                        (r.entity_a_id = e1.id AND r.entity_b_id = e2.id) OR
                        (r.entity_b_id = e1.id AND r.entity_a_id = e2.id)
                    )
                    WHERE e1.symbol_value = %s AND r.relationship_type ILIKE 'cross_reference%'
                """, (symbol_value,))
                
                results = cursor.fetchall()
                return list(results)
                
        except Exception as e:
            print(f"  ❌ Error getting cross-references: {e}")
            return []
    
    def get_domain_summary(self) -> List[Dict[str, Any]]:
        """Get domain convergence summary."""
        try:
            with self.pool.getconn() as conn:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute("SELECT * FROM v_domain_convergence")
                return list(cursor.fetchall())
                
        except Exception as e:
            print(f"  ❌ Error getting domain summary: {e}")
            return []
    
    def get_top_cross_references(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get top cross-references by connection count."""
        try:
            with self.pool.getconn() as conn:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                
                query = f"""
                    SELECT 
                        e.symbol_value,
                        COUNT(r.id) as connection_count,
                        STRING_AGG(DISTINCT r.entity_b_id::TEXT, ', ') as connected_entities
                    FROM gematria_entities e
                    JOIN gematria_relationships r ON (
                        (r.entity_a_id = e.id AND r.relationship_type ILIKE 'cross_reference%') OR
                        (r.entity_b_id = e.id AND r.relationship_type ILIKE 'cross_reference%')
                    )
                    GROUP BY e.symbol_value
                    ORDER BY connection_count DESC
                    LIMIT %s
                """
                
                cursor.execute(query, (limit,))
                return list(cursor.fetchall())
                
        except Exception as e:
            print(f"  ❌ Error getting top cross-references: {e}")
            return []
    
    # ================================
    # UTILITIES
    # ================================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge graph statistics."""
        try:
            with self.pool.getconn() as conn:
                cursor = conn.cursor()
                
                # Count entities
                cursor.execute("SELECT COUNT(*) FROM gematria_entities")
                entity_count = cursor.fetchone()[0]
                
                # Count relationships
                cursor.execute("SELECT COUNT(*) FROM gematria_relationships")
                relationship_count = cursor.fetchone()[0]
                
                # Core symbols count
                cursor.execute("SELECT COUNT(DISTINCT symbol_value) FROM gematria_entities WHERE symbol_value IS NOT NULL")
                core_symbols_count = cursor.fetchone()[0]
                
                return {
                    "entity_count": entity_count,
                    "relationship_count": relationship_count,
                    "core_symbols_count": core_symbols_count
                }
                
        except Exception as e:
            print(f"  ❌ Error getting stats: {e}")
            return {}
    
    def export_entities_to_json(self, filepath: str) -> bool:
        """Export all entities to a JSON file."""
        try:
            with self.pool.getconn() as conn:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute("SELECT * FROM gematria_entities")
                entities = list(cursor.fetchall())
                
                # Convert for JSON serialization
                json_entities = []
                for e in entities:
                    row = dict(e)
                    if 'secondary_domains' in row and row['secondary_domains']:
                        row['secondary_domains'] = json.loads(row['secondary_domains'])
                    json_entities.append(row)
                
                with open(filepath, 'w') as f:
                    json.dump(json_entities, f, indent=2)
                
                print(f"  ✅ Exported {len(json_entities)} entities to {filepath}")
                return True
                
        except Exception as e:
            print(f"  ❌ Error exporting entities: {e}")
            return False


# ================================
# MAIN / DEMO USAGE
# ================================

def main():
    """Demonstrate knowledge graph usage."""
    
    # Initialize and connect
    kg = GematriaKnowledgeGraph()
    if not kg.connect():
        print("Cannot proceed without database connection.")
        return
    
    # Get stats
    stats = kg.get_stats()
    print(f"\n📊 Knowledge Graph Statistics:")
    print(f"   Entities: {stats.get('entity_count', 0)}")
    print(f"   Relationships: {stats.get('relationship_count', 0)}")
    print(f"   Core Symbols: {stats.get('core_symbols_count', 0)}")
    
    # Show domains
    domains = kg.get_domain_summary()
    print(f"\n📈 Domain Summary:")
    for d in domains:
        print(f"   • {d['primary_domain']}: {d['entity_count']} entities, avg relevance: {d['avg_relevance']}")
    
    # Show top cross-references
    top_crs = kg.get_top_cross_references(limit=5)
    print(f"\n🔗 Top Cross-References:")
    for cr in top_crs:
        print(f"   • {cr['symbol_value']}: {cr['connection_count']} connections")
    
    # Disconnect
    kg.disconnect()


if __name__ == "__main__":
    main()
