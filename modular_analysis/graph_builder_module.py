#!/usr/bin/env python3
"""
Modular Analysis - Graph Builder Module
Responsible for: Relationship iteration and knowledge graph updates.
Single responsibility: Build relationships between concepts, update existing graph.
"""

import random
from typing import List, Dict


class GraphBuilderModule:
    """
    Standalone graph builder module for relationship iteration.
    
    Can be used independently:
        builder = GraphBuilderModule()
        new_rels = builder.build_relationships(results, existing_rels)
    """
    
    def __init__(self):
        self.relationship_weights = {
            "symbol_domain_association": 1.0,
            "batch_symbol_correlation": 0.9,
            "entry_symbol_link": 1.0,
            "new_discovery_to_existing": random.uniform(0.5, 0.9),
            "cross_discovery": random.uniform(0.6, 0.95)
        }
        
    def build_relationships(self, results: List[Dict], 
                           existing_rels: List[Dict] = None) -> List[Dict]:
        """
        Build new relationships from discovered concepts.
        
        Args:
            results: List of result dicts (can be from any scraper)
            existing_rels: Existing relationships to link new discoveries to
            
        Returns:
            List of new relationship dictionaries ready for database merge
        """
        existing_rels = existing_rels or []
        new_relationships = []
        
        # Extract concepts from results
        all_concepts = self._extract_concepts_from_results(results)
        
        # Build relationships between new discoveries and existing concepts
        seen_pairs = set()
        for concept in all_concepts[:10]:  # Limit for manageability
            source = f"#discovered-{concept}"
            
            # Link to recent existing relationships
            for i, existing_rel in enumerate(existing_rels[-5:]):
                if len(new_relationships) < 20:
                    pair_key = tuple(sorted([source, existing_rel.get("target", "")]))
                    if pair_key not in seen_pairs:
                        seen_pairs.add(pair_key)
                        
                        new_relationships.append({
                            "type": "new_discovery_to_existing",
                            "source": source,
                            "target": existing_rel.get("target", "#existing_concept"),
                            "weight": self.relationship_weights["new_discovery_to_existing"],
                            "context": f"New concept '{concept}' relates to {existing_rel.get('context', '')[:50] if existing_rel.get('context') else ''}"
                        })
        
        # Add relationships between new discoveries themselves
        concept_list = all_concepts[:8]
        for i, c1 in enumerate(concept_list):
            for c2 in concept_list[i+1:]:
                if len(new_relationships) < 30:
                    pair_key = tuple(sorted([c1, c2]))
                    if pair_key not in seen_pairs:
                        seen_pairs.add(pair_key)
                        
                        new_relationships.append({
                            "type": "cross_discovery",
                            "source": f"#discovered-{c1}",
                            "target": f"#discovered-{c2}",
                            "weight": self.relationship_weights["cross_discovery"],
                            "context": f"Cross-reference between {c1} and {c2}"
                        })
        
        return new_relationships
    
    def _extract_concepts_from_results(self, results: List[Dict]) -> List[str]:
        """Extract concepts from result titles and URLs"""
        all_concepts = set()
        
        for result in results:
            title = result.get("title", "")
            url = result.get("url", "")
            
            # Extract keywords from titles
            keywords_in_title = [k.lower() for k in ["gematria", "number", "symbol", 
                                                   "bible", "frequency", "pattern"]]
            
            for keyword in keywords_in_title:
                if keyword in title.lower():
                    all_concepts.add(f"{keyword}_in_{title[:50]}")
            
            # Extract URL-based concepts (domain)
            domain = url.split('/')[2] if len(url.split('/')) > 2 else "unknown"
            if len(domain) > 5:
                all_concepts.add(domain.lower()[:30])
        
        return list(all_concepts)[:15]  # Return up to 15 concepts


if __name__ == "__main__":
    # Test standalone usage
    print("🔗 Testing GraphBuilderModule standalone...")
    
    builder = GraphBuilderModule()
    test_results = [
        {
            "url": "https://en.wikipedia.org/wiki/Gematria",
            "title": "Gematria - Wikipedia article about biblical numerology"
        }
    ]
    existing_rels = [{"target": "#existing-124", "context": "Core symbol 124"}]
    
    new_relationships = builder.build_relationships(test_results, existing_rels)
    
    print(f"\n✅ Built {len(new_relationships)} new relationships:\n")
    for rel in new_relationships[:3]:
        print(f"   {rel['source']} ↔ {rel['target']}")
        print(f"      Type: {rel['type']}")
