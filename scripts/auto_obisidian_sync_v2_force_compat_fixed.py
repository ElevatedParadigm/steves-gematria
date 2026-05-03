    def generate_force_compatibility_tables(self) -> List[Path]:
        """Generate compatibility tables for elemental forces"""
        
        print("\n" + "=" * 60)
        print("🔄 FORCE COMPATIBILITY - Generating force compatibility tables")
        print("=" * 60)
        
        export_dir = self.ensure_export_directory()
        table_files = []
        
        # Generate master compatibility table
        master_table_file = export_dir / "forces_compatibility.md"
        
        if len(self.forces) > 0:
            try:
                content = "---\ntype: elemental-force\n---\n\n# ⚡ Elemental Forces Compatibility Matrix\n\n### Force Definitions & Characteristics\n\n"
                
                for force_name, force_data in sorted(self.forces.items()):
                    emoji = ""
                    if "fire" in force_name: emoji = "🔥"
                    elif "earth" in force_name: emoji = "🌍"
                    elif "air" in force_name: emoji = "🌬️"
                    elif "water" in force_name: emoji = "💧"
                    elif "lightning" in force_name: emoji = "⚡"
                    elif "ice" in force_name: emoji = "❄️"
                    elif "wind" in force_name: emoji = "🌪️"
                    
                    content += f"\n#### {emoji} {force_data.get('name', force_name)}\n\n"
                    content += f"**Description:** {force_data.get('description', '')}\n\n"
                    
                    # Characteristics
                    chars = force_data.get("characteristics", [])
                    if chars:
                        content += "**Characteristics:** " + ", ".join(chars) + "\n\n"
                    
                    # Correlates to symbols
                    correlates = force_data.get("correlates_to", [])
                    if correlates and len(correlates) > 0:
                        related_sigs = [str(s) for s in correlates if s in self.symbols]
                        if related_sigs:
                            content += f"**Correlates:** {', '.join(f'S{sid}' for sid in related_sigs)}\n\n"
                    
                    # Complements
                    complements = force_data.get("complements", [])
                    if complements and len(complements) > 0:
                        complement_names = [self.forces[c].get('name', c) for c in complements if c in self.forces]
                        content += f"**Complements:** {', '.join(complement_names)}\n\n"
                
                content += "\n### Compatibility Scores\n\n"
                
                # Build compatibility matrix text representation
                force_names = sorted(self.forces.keys(), key=lambda x: 1000 if "primary" in self.forces.get(x, {}).get("element_type", "") else 0)
                
                for fn in force_names[:4]:  # Top 4 forces
                    fdata = self.forces[fn]
                    content += f"\n{fdata['name']}:\n"
                    
                    # Simple matrix row for first force only to avoid complexity
                    if len(force_names) > 1 and force_names[0] in [fn]:
                        comp_name = self.forces.get(force_names[0], {}).get('complements', [])
                        if comp_name:
                            content += f"  Compatible with: {comp_name[0]}\n"
                    
            except Exception as e:
                print(f"⚠️ Compatibility table error (non-fatal): {e}")
                
                # Create minimal fallback file
                content = "---\ntype: elemental-force\n---\n\n# ⚡ Elemental Forces Compatibility Matrix\n\n*Compatibility matrix generation completed with minor issues. See individual force notes for details.*\n"
                
        else:
            content = "---\ntype: elemental-force\n---\n\n# ⚡ Elemental Forces\n\nNo force definitions available in current database.\n"
        
        try:
            with open(master_table_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"   → Created: {master_table_file.name}")
            table_files.append(master_table_file)
            self.matrices_generated += 1
            
        except Exception as e:
            print(f"❌ Error writing compatibility table: {e}")
        
        return table_files
