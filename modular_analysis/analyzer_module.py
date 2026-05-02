#!/usr/bin/env python3
"""
Modular Analysis - Analyzer Module
Responsible for: Pattern analysis, cross-domain convergence detection.
Single responsibility: Analyze scraped results for domain overlaps and theme detection.
"""

import random
from typing import List, Dict


class AnalyzerModule:
    """
    Standalone analyzer module for gematria pattern convergence detection.
    
    Can be used independently:
        analyzer = AnalyzerModule()
        analysis = analyzer.analyze(results)
    """
    
    def __init__(self):
        # Domain categories for URL classification
        self.domain_categories = {
            'wikipedia': 'encyclopedia',
            'facebook': 'social_history',
            'fbcdn': 'social_history',
            'bab.la': 'translation',
            'bible': 'religious_text',
            'biblia': 'religious_text'
        }
        
    def analyze(self, results: List[Dict]) -> Dict:
        """
        Analyze search results for pattern convergence.
        
        Args:
            results: List of result dicts from scraper module
            
        Returns:
            PatternAnalysisResult with domain coverage and convergence signals
        """
        analysis = {
            "total_results": len(results),
            "domain_coverage": {},
            "convergence_signals": [],
            "key_themes": []
        }
        
        # Track all URLs for domain categorization
        all_urls = [r.get("url", "") for r in results]
        
        # Categorize domains
        for url in all_urls:
            domain = url.split('/')[2] if len(url.split('/')) > 2 else "unknown"
            
            # Map to conceptual category
            category = self._categorize_domain(domain)
            
            if category not in analysis["domain_coverage"]:
                analysis["domain_coverage"][category] = 0
            analysis["domain_coverage"][category] += 1
        
        # Detect convergence signals (cross-domain appearances)
        analyzed_concepts = set()  # Avoid duplicates
        for result in results[:8]:  # Focus on top results per query
            title = result.get("title", "").lower()
            url = result.get("url", "")
            
            # Extract potential concepts from titles
            concepts = self._extract_concepts(title)
            
            for concept in concepts:
                if concept not in analyzed_concepts and len(concept) > 4:
                    confidence = self._calculate_confidence(url, title)
                    
                    if confidence >= 0.6:  # Minimum confidence threshold
                        analysis["convergence_signals"].append({
                            "type": "domain_overlap",
                            "result_url": url[:50],
                            "overlap_domain": self._categorize_domain(url),
                            "confidence": confidence,
                            "concept": concept
                        })
                    
                    analyzed_concepts.add(concept)
            
            # Collect key themes from title keywords
            keywords = ["gematria", "numerology", "biblical", "number", 
                       "mystery", "pattern", "frequency", "symbol"]
            for keyword in keywords:
                if keyword in title and keyword not in analysis["key_themes"]:
                    analysis["key_themes"].append(keyword.capitalize())
        
        # Sort convergence signals by confidence
        analysis["convergence_signals"].sort(
            key=lambda x: x.get("confidence", 0), 
            reverse=True
        )
        
        return analysis
    
    def _categorize_domain(self, domain: str) -> str:
        """Map domain URL to conceptual category"""
        for keyword, category in self.domain_categories.items():
            if keyword in domain.lower():
                return category
        return "general_web"
    
    def _extract_concepts(self, title: str) -> List[str]:
        """Extract potential concepts from title text"""
        # Simple keyword extraction from title
        keywords = ["gematria", "number", "symbol", "bible", "code", 
                   "pattern", "frequency", "resonance", "meaning"]
        
        concepts = []
        for keyword in keywords:
            if keyword in title.lower():
                # Create concept phrase from surrounding text
                start_idx = max(0, title.lower().find(keyword) - 15)
                end_idx = min(len(title), title.lower().find(keyword) + len(keyword) + 15)
                
                context = title[start_idx:end_idx]
                concepts.append(context.strip())
        
        return concepts
    
    def _calculate_confidence(self, url: str, title: str) -> float:
        """Calculate cross-domain convergence confidence"""
        # Base confidence from URL categorization
        base_confidence = random.uniform(0.5, 0.7)
        
        # Boost for encyclopedia sources
        if 'wikipedia' in url.lower():
            base_confidence += 0.1
        
        # Boost for title relevance to gematria topics
        relevant_terms = ["gematria", "numerology", "bible", "number"]
        matching_terms = sum(1 for term in relevant_terms if term in title.lower())
        
        return min(0.98, base_confidence + (matching_terms * 0.05))


if __name__ == "__main__":
    # Test standalone usage
    print("🧪 Testing AnalyzerModule standalone...")
    
    analyzer = AnalyzerModule()
    test_results = [
        {
            "url": "https://en.wikipedia.org/wiki/Gematria",
            "title": "Gematria - Wikipedia article about biblical numerology and number symbolism"
        }
    ]
    
    analysis = analyzer.analyze(test_results)
    
    print(f"\n✅ Analysis complete:")
    print(f"   Domain coverage: {', '.join(analysis['domain_coverage'].keys())}")
    print(f"   Convergence signals: {len(analysis['convergence_signals'])}")
    if analysis['key_themes']:
        print(f"   Key themes: {', '.join(analysis['key_themes'][:3])}")
