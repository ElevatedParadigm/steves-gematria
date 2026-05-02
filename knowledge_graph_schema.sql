-- Steve's Gematria Knowledge Graph Schema
-- PostgreSQL 15 with pgvector for semantic similarity search

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- ================================
-- CORE ENTITIES TABLE
-- Stores unique entities (symbols, domains, concepts)
-- ================================
CREATE TABLE gematria_entities (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    
    -- Symbol attributes
    symbol_value VARCHAR(20),  -- e.g., '124', '963'
    elemental_force TEXT,       -- e.g., 'Fire', 'Water', 'Air', 'Earth'
    
    -- Domain classification
    primary_domain TEXT,        -- e.g., 'Political', 'Military', 'Elemental'
    secondary_domains TEXT[],   -- Array of additional domains
    
    -- Vector embedding for semantic similarity
    embedding VECTOR(384),      -- pgvector 384-dim embeddings
    
    -- Metadata & indexing
    source_url TEXT,
    relevance_score DECIMAL(5,2) DEFAULT 0.00,
    
    -- Temporal tracking
    first_seen TIMESTAMP DEFAULT NOW(),
    last_updated TIMESTAMP DEFAULT NOW(),
    
    -- Full-text search on searchable fields
    search_text TEXT
);

-- Indexes for efficient querying
CREATE INDEX idx_entities_symbol ON gematria_entities(symbol_value);
CREATE INDEX idx_entities_elemental ON gematria_entities(elemental_force);
CREATE INDEX idx_entities_domain ON gematria_entities(primary_domain);
CREATE INDEX idx_entities_search ON gematria_entities USING GIN(search_text) WHERE search_text IS NOT NULL;
CREATE INDEX idx_entities_embedding ON gematria_entities USING ivfflat (embedding cosine_cosine_ops) WITH (lists = 100);

-- ================================
-- RELATIONSHIPS TABLE
-- Stores all known connections between entities
-- ================================
CREATE TABLE gematria_relationships (
    id SERIAL PRIMARY KEY,
    
    -- Entity references
    entity_a_id INTEGER REFERENCES gematria_entities(id),
    entity_b_id INTEGER REFERENCES gematria_entities(id),
    
    -- Relationship type & semantics
    relationship_type TEXT NOT NULL,  -- e.g., 'cross_references', 'in_domain', 'elemental_connection'
    relationship_strength DECIMAL(5,2) DEFAULT 1.00,
    
    -- Description and context
    description TEXT,
    context_fields JSONB,  -- Additional contextual data
    
    -- Source & provenance
    source_url TEXT,
    
    -- Temporal tracking
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Indexes for efficient relationship queries
    CONSTRAINT unique_bidirectional UNIQUE (LEAST(entity_a_id, entity_b_id), GREATEST(entity_a_id, entity_b_id), relationship_type)
);

-- Composite indexes for common query patterns
CREATE INDEX idx_relationships_entity_a ON gematria_relationships(entity_a_id);
CREATE INDEX idx_relationships_entity_b ON gematria_relationships(entity_b_id);
CREATE INDEX idx_relationships_type ON gematria_relationships(relationship_type);
CREATE INDEX idx_relationships_strength ON gematria_relationships(relationship_strength DESC);

-- ================================
-- ANALYSIS METRICS TABLE
-- Stores computed metrics and convergence data
-- ================================
CREATE TABLE analysis_metrics (
    id SERIAL PRIMARY KEY,
    
    -- Time series
    timestamp TIMESTAMP DEFAULT NOW(),
    
    -- Symbol detection counts
    symbols_detected TEXT[],  -- Array of detected symbol values
    
    -- Domain convergence scores (normalized 0-1)
    domain_scores JSONB,  -- e.g., {"Political": 0.85, "Military": 0.92}
    
    -- Elemental force activations
    elemental_activations JSONB,
    
    -- Overall analysis results
    findings TEXT[],
    anomalies_detected BOOLEAN DEFAULT FALSE,
    
    -- Source reference
    source_batch_id TEXT
);

-- ================================
-- OVERNIGHT RESEARCH LOGS
-- Tracks scraping runs and their outcomes
-- ================================
CREATE TABLE overnight_research_logs (
    id SERIAL PRIMARY KEY,
    run_timestamp TIMESTAMP DEFAULT NOW(),
    url_scraped TEXT,
    scrape_success BOOLEAN,
    content_length INTEGER,
    symbols_found TEXT[],
    domains_identified TEXT[],
    error_message TEXT
);

CREATE INDEX idx_logs_timestamp ON overnight_research_logs(run_timestamp DESC);
CREATE INDEX idx_logs_url ON overnight_research_logs(url_scraped);
CREATE INDEX idx_logs_success ON overnight_research_logs(scrape_success);

-- ================================
-- VIEWS FOR COMMON QUERIES
-- ================================

-- View: Top cross-references by symbol
CREATE OR REPLACE VIEW v_symbol_cross_references AS
SELECT 
    e.symbol_value,
    COUNT(r.id) as connection_count,
    STRING_AGG(DISTINCT r.entity_b_id::TEXT, ', ') as connected_entities
FROM gematria_entities e
JOIN gematria_relationships r ON (
    (r.entity_a_id = e.id AND r.relationship_type ILIKE '%cross_reference%') OR
    (r.entity_b_id = e.id AND r.relationship_type ILIKE '%cross_reference%')
)
GROUP BY e.symbol_value
ORDER BY connection_count DESC;

-- View: Domain convergence summary
CREATE OR REPLACE VIEW v_domain_convergence AS
SELECT 
    primary_domain,
    COUNT(*) as entity_count,
    AVG(relevance_score) as avg_relevance,
    ARRAY_AGG(DISTINCT elemental_force) as associated_elements
FROM gematria_entities
GROUP BY primary_domain;

-- ================================
-- FUNCTIONS & PROCEDURES
-- ================================

-- Function: Add entity to knowledge graph
CREATE OR REPLACE FUNCTION add_gematria_entity(
    p_name TEXT,
    p_symbol_value VARCHAR(20),
    p_elemental_force TEXT,
    p_primary_domain TEXT,
    p_secondary_domains TEXT[],
    p_embedding VECTOR(384),
    p_relevance_score DECIMAL(5,2) DEFAULT 0.00,
    p_search_text TEXT
)
RETURNS INTEGER AS $$
DECLARE
    v_id INTEGER;
BEGIN
    INSERT INTO gematria_entities (
        name, symbol_value, elemental_force, primary_domain,
        secondary_domains, embedding, relevance_score, search_text
    ) VALUES (
        p_name, p_symbol_value, p_elemental_force, p_primary_domain,
        p_secondary_domains, p_embedding, p_relevance_score, p_search_text
    ) RETURNING id INTO v_id;
    
    RETURN v_id;
END;
$$ LANGUAGE plpgsql;

-- Function: Add relationship between entities
CREATE OR REPLACE FUNCTION add_relationship(
    p_entity_a_id INTEGER,
    p_entity_b_id INTEGER,
    p_relationship_type TEXT,
    p_strength DECIMAL(5,2) DEFAULT 1.00,
    p_description TEXT,
    p_context_fields JSONB DEFAULT '{}',
    p_source_url TEXT
)
RETURNS INTEGER AS $$
DECLARE
    v_id INTEGER;
    v_min_id INTEGER;
    v_max_id INTEGER;
BEGIN
    SELECT LEAST(p_entity_a_id, p_entity_b_id), GREATEST(p_entity_a_id, p_entity_b_id)
    INTO v_min_id, v_max_id;
    
    INSERT INTO gematria_relationships (
        entity_a_id, entity_b_id, relationship_type, relationship_strength,
        description, context_fields, source_url
    ) VALUES (
        v_min_id, v_max_id, p_relationship_type, p_strength,
        p_description, p_context_fields, p_source_url
    ) ON CONFLICT (LEAST(entity_a_id, entity_b_id), GREATEST(entity_a_id, entity_b_id), relationship_type) DO UPDATE SET
        relationship_strength = EXCLUDED.relationship_strength::DECIMAL(5,2),
        description = EXCLUDED.description;
    
    RETURN LAST_INSERT_ID();
END;
$$ LANGUAGE plpgsql;

-- Function: Query similar entities by vector similarity
CREATE OR REPLACE FUNCTION find_similar_entities(
    p_embedding VECTOR(384),
    p_limit INTEGER DEFAULT 10,
    p_min_similarity DECIMAL(5,2) DEFAULT 0.70
)
RETURNS TABLE (
    id INTEGER,
    name TEXT,
    symbol_value VARCHAR(20),
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        e.id,
        e.name,
        e.symbol_value,
        1 - (e.embedding <=> p_embedding) as similarity
    FROM gematria_entities e
    WHERE (e.embedding <=> p_embedding) < (1 - p_min_similarity)
    ORDER BY (e.embedding <=> p_embedding)
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql STABLE PARALLEL RESTRICTED;

-- Function: Get all relationships for an entity
CREATE OR REPLACE FUNCTION get_entity_relationships(p_entity_id INTEGER)
RETURNS TABLE (
    relationship_type TEXT,
    target_id INTEGER,
    strength DECIMAL(5,2),
    description TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT r.relationship_type, e.id as target_id, r.relationship_strength, r.description
    FROM gematria_relationships r
    JOIN gematria_entities e ON (
        (r.entity_a_id = p_entity_id AND r.entity_b_id = e.id) OR
        (r.entity_b_id = p_entity_id AND r.entity_a_id = e.id)
    )
    ORDER BY r.relationship_strength DESC;
END;
$$ LANGUAGE plpgsql;
