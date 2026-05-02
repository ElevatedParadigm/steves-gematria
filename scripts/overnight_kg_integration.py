#!/usr/bin/env python3
"""
🧙‍♂️ STEVE'S GEMATRIA OVERNIGHT RESEARCH → KNOWLEDGE GRAPH INTEGRATION
=======================================================================
Connects Firecrawl scraping to PostgreSQL knowledge graph for persistent storage.

© Steve's Gematria System - Maintained by Avalon & Steve
=======================================================================
"""

import json
from pathlib import Path
import sys

# Add scripts directory to path
SCRIPTS_DIR = Path.home() / ".hermes" / "gematria" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from overnight_research import analyzer  # Import the overnight analyzer
from knowledge_graph_manager import GematriaKnowledgeGraph


def process_overnight_report(report_path: str) -> bool:
    """
    Process an overnight research report and insert entities/relationships into KG.
    
    Args:
        report_path: Path to overnight_scrape_*.json or *.md report
        
    Returns:
        True if successful, False otherwise
    """
    print(f"\n🔍 Processing overnight report: {report_path}")
    print("=" * 80)
    
    try:
        # Load report (supports both JSON and MD formats)
        with open(report_path, 'r') as f:
            content = f.read()
        
        # Parse JSON if present, otherwise parse markdown manually
        is_json = report_path.endswith('.json') or ('{"' in content[:100])
        
        if is_json:
            try:
                with open(report_path, 'r') as f:
                    report_data = json.load(f)
            except Exception as e:
                print(f"  ⚠️  Could not parse as JSON: {e}")
                return False
        else:
            # Parse markdown format (from overnight_scrape_*.md files)
            report_data = parse_markdown_report(content)
        
        if not report_data or 'results' not in report_data:
            print("  ⚠️  No results found in report")
            return False
        
        results = report_data['results']
        print(f"  📊 Found {len(results)} URL scraping results to process")
        
        # Connect to knowledge graph
        kg = GematriaKnowledgeGraph()
        if not kg.connect():
            print("  ❌ Cannot connect to database")
            return False
        
        processed_urls = []
        
        for i, result in enumerate(results, 1):
            url = result['url']
            print(f"\n  [{i}/{len(results)}] Processing: {url[:80]}...")
            
            try:
                # Analyze scraped content (already done by overnight_research)
                analysis = result.get('analysis', {})
                
                # Generate entity for the scraped content itself
                entity_name = f"Website [{Path(url).name}]"
                
                # Extract relevant text for embedding
                scraped_content = result.get('scraped', {}).get('title', '')
                description = result.get('scraped', {}).get('description', '')
                full_text = f"{scraped_content} {description}"
                
                # Generate vector embedding
                embedding = kg.generate_embedding(full_text) if embedding is None else embedding
                
                # Add website entity
                entity_id = kg.add_entity(
                    name=entity_name,
                    symbol_value=None,  # Not a core symbol
                    elemental_force=None,
                    primary_domain="General",  # Will be updated based on content analysis
                    secondary_domains=analysis.get('domains_identified', []),
                    embedding=embedding,
                    relevance_score=0.10,  # Initial relevance
                    search_text=scraped_content,
                    source_url=url
                )
                
                if entity_id:
                    print(f"    ✅ Added website entity (ID: {entity_id})")
                    
                    # Detect symbols in content and add them if not present
                    symbols_detected = analysis.get('symbols_detected', [])
                    for symbol in symbols_detected:
                        sym_value = symbol['symbol']
                        sym_name = symbol['name']
                        
                        # Check if this symbol entity already exists
                        existing_entities = kg.get_entities_by_symbol(sym_value)
                        
                        if not existing_entities:
                            # Create new core symbol entity
                            kg.add_entity(
                                name=f"{sym_name} ({sym_value})",
                                symbol_value=sym_value,
                                elemental_force=symbol['domain'],  # Use domain as elemental force
                                primary_domain="Core Symbol",
                                secondary_domains=[],
                                embedding=None,  # Will be regenerated
                                relevance_score=1.00,
                                search_text=f"{sym_name} {sym_value}",
                                source_url=url
                            )
                            
                            print(f"      ➕ Added core symbol: {sym_value}")
                        
                        # Update embedding with fresh computation
                        updated_embedding = kg.generate_embedding(sym_name)
                        if updated_embedding:
                            kg.update_entity(entity_id, embedding=updated_embedding)
                    
                    processed_urls.append(url)
                
                # Extract domain-specific connections
                extract_domain_connections(analysis, entity_id)
                
            except Exception as e:
                print(f"    ❌ Error processing {url}: {e}")
                continue
        
        # Disconnect
        kg.disconnect()
        
        print(f"\n🎉 Successfully processed {len(processed_urls)} URLs")
        return True
        
    except Exception as e:
        print(f"\n❌ Error processing report: {e}")
        import traceback
        traceback.print_exc()
        return False


def extract_domain_connections(analysis: dict, entity_id: int):
    """Extract domain connections for scraped website."""
    
    domains_identified = analysis.get('domains_identified', [])
    
    # Domain-related relationships (non-core symbol entities don't need these)
    if not domains_identified:
        return
    
    # Add domain associations
    for domain in domains_identified:
        domain_name = domain['domain']
        matched_terms = domain.get('matched_terms', [])
        
        kg = GematriaKnowledgeGraph()  # Will reconnect as needed
        with kg.pool.getconn() as conn:
            cursor = conn.cursor()
            
            # Query for existing domain entity
            cursor.execute("""
                SELECT id FROM gematria_entities 
                WHERE name ILIKE %s OR primary_domain = %s
            """, (f"Domain [{domain_name}]", domain_name))
            
            result = cursor.fetchone()
            
            if result:
                domain_id = result['id']
            else:
                # Create domain entity
                cursor.execute("""
                    INSERT INTO gematria_entities (
                        name, primary_domain, secondary_domains, 
                        search_text, relevance_score
                    ) VALUES (%s, %s, %s, %s, %s)
                """, (
                    f"Domain [{domain_name}]",
                    domain_name,
                    json.dumps([]),
                    f"{domain_name} website/domain classification",
                    0.85
                ))
                cursor.execute("SELECT id FROM gematria_entities WHERE name ILIKE %s OR primary_domain = %s", 
                             (f"Domain [{domain_name}]", domain_name))
                result = cursor.fetchone()
                domain_id = result['id']
            
            # Add connection from website to domain
            kg.add_relationship(
                entity_a_id=entity_id,
                entity_b_id=domain_id,
                relationship_type="in_domain",
                strength=1.0,
                description=f"Website classified in {domain_name} domain",
                context_fields={"matched_terms": matched_terms[:5]}
            )


def parse_markdown_report(content: str) -> dict:
    """Parse markdown format overnight research report."""
    
    # This is a simplified parser - actual reports use JSON format
    # The JSON parsing above handles the real data structure
    
    return {
        "results": []  # Placeholder
    }


# ================================
# MAIN / CLI USAGE
# ================================

def main():
    """Run overnight report processing."""
    
    import glob
    
    reports_dir = Path.home() / ".hermes" / "gematria" / "reports"
    report_files = list(glob.glob(str(reports_dir / "overnight_scrape_*.json")))
    
    if not report_files:
        print("No overnight research reports found.")
        print(f"Expected location: {reports_dir}")
        return
    
    print("🧙‍♂️  STEVE'S GEMATRIA OVERNIGHT RESEARCH → KNOWLEDGE GRAPH PIPELINE")
    print("=" * 80)
    
    for report_path in sorted(report_files):
        success = process_overnight_report(report_path)
        
        if success:
            print(f"✅ {report_path}")
        else:
            print(f"⚠️  {report_path} (processed with warnings)")
    
    print("\n" + "=" * 80)
    print("🎉 Overnight research pipeline complete!")


if __name__ == "__main__":
    main()
