#!/usr/bin/env python3
"""
Modular Analysis - Heatmap Generator Module
Responsible for: ASCII visualization of relationship density.
Single responsibility: Generate terminal-compatible ASCII heatmaps from relationships.
"""

from typing import List, Dict


class HeatmapGeneratorModule:
    """
    Standalone heatmap generator for ASCII visualizations.
    
    Can be used independently:
        generator = HeatmapGeneratorModule()
        ascii_heatmap = generator.generate_relationships(relationships, symbols)
    """
    
    def __init__(self):
        self.max_bar_length = 20
    
    def generate_relationships(self, relationships: List[Dict], 
                               symbols: List[str]) -> str:
        """
        Generate ASCII relationship density heatmap.
        
        Args:
            relationships: List of relationship dictionaries
            symbols: List of core symbols for display
            
        Returns:
            ASCII string ready for markdown report
        """
        if len(relationships) == 0 or len(symbols) < 2:
            return "No relationships to visualize yet.\n"
        
        lines = [
            "\n🔥 Relationship Density Heatmap (ASCII):",
            "=" * 60
        ]
        
        # Calculate relationship weights by type
        type_counts = {}
        for rel in relationships[-30:]:  # Last 30 relationships
            rtype = rel.get("type", "unknown")
            weight = rel.get("weight", 0.5)
            
            if rtype not in type_counts:
                type_counts[rtype] = {"count": 0, "total_weight": 0}
            
            type_counts[rtype]["count"] += 1
            type_counts[rtype]["total_weight"] += weight
        
        # Visualize as bar chart for top relationship types
        for rtype, data in sorted(type_counts.items(), 
                                 key=lambda x: x[1]["total_weight"], 
                                 reverse=True)[:4]:
            bar_length = int(data["total_weight"] * self.max_bar_length / 6)
            
            # Scale to fit max_bar_length
            scaled_length = min(bar_length, self.max_bar_length)
            filled = "█" * scaled_length
            empty = "░" * (self.max_bar_length - scaled_length)
            
            bar = filled + empty
            
            percent = round(data["total_weight"] / 6 * 100, 0) if data["total_weight"] > 0 else 0
            lines.append(f"\n📊 {rtype.replace('_', ' ').title()} Relationship Strength:")
            lines.append(f"   {bar}")
            lines.append(f"   {'█' * 5} {percent:.0f}%")
        
        # Add symbol mentions if available
        if len(symbols) >= 3:
            lines.extend([
                "",
                "🔤 Symbol Mention Density (Top 3):",
                "=" * 40
            ])
            
            # Simple density visualization based on symbol count
            for i, symbol in enumerate(symbols[:3], 1):
                density = min(len(symbols), i) / len(symbols)
                bar_length = int(density * self.max_bar_length)
                
                filled = "█" * bar_length
                empty = "░" * (self.max_bar_length - bar_length)
                bar = filled + empty
                
                lines.append(f"   {symbol}: {bar} ({density*100:.0f}%)")
        
        return "\n".join(lines) + "\n\n"


if __name__ == "__main__":
    # Test standalone usage
    print("🔥 Testing HeatmapGeneratorModule standalone...")
    
    generator = HeatmapGeneratorModule()
    
    test_relationships = [
        {"type": "symbol_domain_association", "weight": 1.0},
        {"type": "cross_discovery", "weight": 0.8},
        {"type": "new_discovery_to_existing", "weight": 0.7}
    ]
    
    test_symbols = ["124", "963", "55", "111"]
    
    heatmap = generator.generate_relationships(test_relationships, test_symbols)
    print(heatmap)
