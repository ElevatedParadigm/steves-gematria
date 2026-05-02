#!/usr/bin/env python3
"""
Modular Analysis - Temporal Tracker Module
Responsible for: Tracking symbol frequency and evolution over time.
Single responsibility: Monitor discovery rates and temporal patterns in results.
"""

from typing import List, Dict


class TemporalTrackerModule:
    """
    Standalone temporal tracker for overnight research progression.
    
    Can be used independently:
        tracker = TemporalTrackerModule()
        temporal = tracker.track(query_sequence, results)
    """
    
    def __init__(self):
        self.normalization_factor = 10  # For normalized discovery rate
    
    def track(self, query_sequence: List[str], 
             results: List[Dict]) -> Dict:
        """
        Track temporal patterns in symbol appearances.
        
        Args:
            query_sequence: List of search queries executed
            results: List of result dicts from scraper
            
        Returns:
            TemporalPatternData with frequency counts and discovery rates
        """
        # Calculate results per query
        query_results_count = []
        for query_result in results:
            parsed = query_result.get("results", [])
            
            if "query" in query_result:
                query_results_count.append({
                    "query": query_result["query"][:40],
                    "count": len(parsed)
                })
        
        total_results = sum(len(r.get("results", [])) for r in results if "results" in r)
        
        temporal_data = {
            "query_sequence": [r.get("query", "")[:40] for r in results],
            "result_count_per_query": [len(r.get("results", [])) for r in results if "results" in r],
            "average_results_per_query": 0.0,
            "discovery_rate": 0.0,
            "symbol_mentions": {}
        }
        
        if len(results) > 0 and total_results > 0:
            temporal_data["average_results_per_query"] = round(
                total_results / len(results), 1
            )
            
            # Calculate normalized discovery rate
            temporal_data["discovery_rate"] = round(
                (total_results / len(results)) / self.normalization_factor * 100, 2
            )
        
        return temporal_data


if __name__ == "__main__":
    # Test standalone usage
    print("⏱️ Testing TemporalTrackerModule standalone...")
    
    tracker = TemporalTrackerModule()
    
    test_results = [
        {"query": "test query 1", "results": [{"url": "https://example.com"}]},
        {"query": "test query 2", "results": []}
    ]
    
    temporal = tracker.track(test_results)
    
    print(f"\n✅ Temporal tracking complete:")
    print(f"   Average results/query: {temporal['average_results_per_query']}")
    print(f"   Discovery rate (normalized): {temporal['discovery_rate']}%")
