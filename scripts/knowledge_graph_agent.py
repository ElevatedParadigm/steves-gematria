#!/usr/bin/env python3
"""
Knowledge Graph Agent
======================

Specialized agent for managing knowledge graph relationships,
database updates, and relationship tracking.

Capabilities:
- Relationship extraction from analysis results
- Database schema management
- Obsidian export synchronization  
- Graph integrity maintenance
- Relationship scoring and relevance tracking
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import json
from pydantic import BaseModel, Field

# Add parent to path for imports
sys.path.insert(0, str(Path.home()))
sys.path.insert(0, str(Path.home() / ".hermes"))
sys.path.insert(0, str(Path.home() / ".hermes/gematria/scripts"))

class Relationship(BaseModel):
    """Represents a relationship in the knowledge graph"""
    id: int
    source: str
    target: str
    type: str  # "created", "updated", "deleted"
    domain1: Optional[str] = None
    domain2: Optional[str] = None
    symbol: Optional[int] = None
    relevance_score: float
    confidence: float
    timestamp: str
    context: Optional[str] = None

class KnowledgeGraphAgent:
    """
    Agent responsible for knowledge graph maintenance and relationship tracking.
    
    Routes:
    • Relationship extraction → Domain convergence parsing
    • Database updates → Schema management
    • Obsidian sync → Export generation
    
    Dependencies:
    • JSON database structure
    • Obsidian export templates
    • Relationship scoring algorithms
    """
    
    def __init__(self):
        self.agent_id = "knowledge-graph"
        self.agent_type = "maintenance"
        self.name = f"[{self.agent_id}] Knowledge Graph Agent"
        self.relationships: List[Dict] = []
        self.domain_relationships: Dict[str, set] = {}
        self.symbol_relationships: Dict[int, set] = {}
        self.relevance_threshold = 0.75
        self.db_path = Path.home() / ".hermes/gematria/database.json"
        
    async def initialize(self):
        """Initialize knowledge graph from database"""
        self.log("INFO", "Initializing knowledge graph from database")
        
        try:
            if self.db_path.exists():
                with open(self.db_path, 'r') as f:
                    db = json.load(f)
                
                # Extract existing relationships
                relationships_count = len(db.get("relationships", []))
                self.log("INFO", f"Loaded {relationships_count} existing relationships")
                
            # Initialize domain relationship tracking
            self.domain_relationships = {
                "politics": set(),
                "crypto": set(),
                "military": set(),
                "religious": set(),
                "cultural": set()
            }
            
            self.log("INFO", "Knowledge graph initialized")
            
        except Exception as e:
            self.log("ERROR", f"Initialization failed: {str(e)}")
        
    async def execute_task(self, task_payload: Dict) -> Dict:
        """Execute specific knowledge graph task"""
        task_name = task_payload.get("type", "unknown")
        
        if task_name == "extract_relationships":
            return await self.extract_domain_relationships(task_payload)
        elif task_name == "update_database":
            return await self.update_database(task_payload)
        elif task_name == "sync_obsidian":
            return await self.sync_to_obsidian()
        else:
            return {"error": f"Unknown task type: {task_name}"}
            
    async def execute_workflow(self) -> Dict:
        """Run daily knowledge graph maintenance workflow"""
        self.log("INFO", "Starting knowledge graph sync workflow")
        
        # Import get_database directly
        from overnight_research import get_database
        
        db = await get_database()
        
        # Run relationship extraction
        relationships_result = await self.extract_domain_relationships(db)
        
        if relationships_result and "relationships" in relationships_result:
            new_relationships = relationships_result["relationships"]
            
            # Update internal tracking
            for rel in new_relationships:
                rel_type = rel.get("type")
                if rel_type == "created":
                    self.relationships.append(rel)
                elif rel_type == "updated":
                    # Update existing relationship
                    existing_idx = None
                    for i, r in enumerate(self.relationships):
                        if r.get("source") == rel["source"] and r.get("target") == rel["target"]:
                            existing_idx = i
                            break
                    if existing_idx is not None:
                        self.relationships[existing_idx] = rel
            
            # Track domain relationships
            for rel in new_relationships:
                domain1 = rel.get("domain1")
                domain2 = rel.get("domain2")
                
                if domain1:
                    self.domain_relationships[domain1].add(rel.get("target", ""))
                if domain2:
                    self.domain_relationships[domain2].add(rel.get("source", ""))
            
            relationship_count = len(self.relationships)
            self.log("INFO", f"Knowledge graph now contains {relationship_count} relationships")
        
        # Summary
        summary = {
            "workflow_completed": True,
            "timestamp": datetime.now().isoformat(),
            "relationships_total": len(self.relationships),
            "relationships_by_type": {
                "created": sum(1 for r in self.relationships if r.get("type") == "created"),
                "updated": sum(1 for r in self.relationships if r.get("type") == "updated"),
                "deleted": sum(1 for r in self.relationships if r.get("type") == "deleted")
            },
            "domains_tracked": list(self.domain_relationships.keys()),
            "relationships_per_domain": {
                domain: len(domains) 
                for domain, domains in self.domain_relationships.items()
            }
        }
        
        self.log("INFO", f"Workflow complete: {len(self.relationships)} total relationships")
        
        return summary

    async def extract_domain_relationships(self, db) -> Dict:
        """Extract relationships from domain convergence analysis"""
        
        relationships_created = []
        domains_analyzed = set()
        
        # Check each symbol's occurrences for relationship patterns
        for symbol_data in db.get("symbols", []):
            number = symbol_data.get("number")
            domains_with_occurrences = symbol_data.get("occurrences", {}).get("by_domain", {})
            
            if not domains_with_occurrences:
                continue
                
            # Each domain occurrence creates potential relationships
            for domain, data in domains_with_occurrences.items():
                item_type = "analysis" if data.get("type") == "analysis" else "image"
                
                try:
                    item_id = str(data["id"]) if isinstance(data.get("id"), int) else data.get("id")
                    
                    # Create relationship entry
                    rel_id = hash(f"{number}_{domain}") % 100000
                    
                    relationship = {
                        "id": rel_id,
                        "source": f"symbol_{number}",
                        "target": f"domain_{domain}",
                        "type": "created" if len(domains_with_occurrences) < 3 else "updated",
                        "domain1": domain[:20] if len(domain) > 20 else domain,  # Truncate long names
                        "domain2": None,  # Could be used for bidirectional tracking
                        "symbol": number,
                        "occurrence_count": data.get("count", 0),
                        "relevance_score": min(1.0, len(domains_with_occurrences) / 3 + 0.5),  # Score based on domain count
                        "confidence": min(1.0, data.get("convergence_index", 0) / 2 + 0.75 if isinstance(data.get("convergence_index"), (int, float)) else 0.75),
                        "timestamp": datetime.now().isoformat(),
                        "context": f"Symbol {number} appears in {domain}",
                        "item_type": item_type,
                        "analysis_id": data.get("analysis_id", "")[:50] if isinstance(data.get("analysis_id"), str) else ""
                    }
                    
                    relationships_created.append(relationship)
                    domains_analyzed.add(domain)
                    
                except Exception as e:
                    self.log("WARN", f"Relationship creation failed for {number}×{domain}: {str(e)}")
        
        # Add cross-domain relationships (where symbols appear in multiple domains)
        cross_domain_rels = await self._extract_cross_domain_relationships(db)
        relationships_created.extend(cross_domain_rels)
        
        return {
            "relationships": relationships_created,
            "domains_analyzed": list(domains_analyzed)[:20],  # Top 20
            "total_new_relationships": len(relationships_created),
            "workflow_completed": True
        }

    async def _extract_cross_domain_relationships(self, db) -> List[Dict]:
        """Extract relationships between symbols appearing in multiple domains"""
        
        cross_domain_rels = []
        
        for symbol_data in db.get("symbols", []):
            number = symbol_data.get("number")
            occurrences = symbol_data.get("occurrences", {}).get("by_domain", {})
            
            if len(occurrences) < 2:
                continue
            
            # Get domain names (truncate long ones)
            domains_with_occurrence_counts = [
                {d: data.get("count", 0) for d, data in occurrences.items()[:5]}
            ][0]
            
            domain_count = len(domains_with_occurrence_counts)
            
            if domain_count >= 2:
                # Create cross-domain relationship
                rel_id = hash(f"cross_{number}") % 100000
                
                relationship = {
                    "id": rel_id,
                    "source": f"symbol_{number}",
                    "target": "multi_domain_presence",
                    "type": "created",
                    "domain1": list(domains_with_occurrence_counts.keys())[0][:20] if len(domains_with_occurrence_counts) > 0 else "",
                    "domain2": None,
                    "symbol": number,
                    "occurrence_count": sum(domains_with_occurrence_counts.values()),
                    "relevance_score": min(1.0, domain_count / 3 + 0.5),
                    "confidence": min(1.0, len(domains_with_occurrence_counts) / 5 + 0.8),
                    "timestamp": datetime.now().isoformat(),
                    "context": f"Symbol {number} spans {domain_count} domains",
                    "item_type": "analysis",
                    "cross_domain_indicator": True
                }
                
                cross_domain_rels.append(relationship)
        
        return cross_domain_rels

    async def update_database(self, payload: Dict) -> Dict:
        """Update database with new relationships"""
        
        db_path = self.db_path
        
        try:
            # Load existing database
            if not db_path.exists():
                return {"success": False, "error": "Database not found"}
            
            with open(db_path, 'r') as f:
                db = json.load(f)
            
            # Add new relationships to relationships array
            existing_rels = set(r["id"] for r in db.get("relationships", []))
            new_relationships = payload.get("relationships", [])
            
            updated = 0
            added = 0
            
            for rel in new_relationships:
                rel_id = rel.get("id")
                
                if rel_id not in existing_rels:
                    db.setdefault("relationships", []).append(rel)
                    added += 1
                else:
                    # Update existing relationship
                    for i, r in enumerate(db["relationships"]):
                        if r["id"] == rel_id:
                            updated_fields = {
                                k: v for k, v in rel.items() 
                                if k != "id" and r.get(k) != v
                            }
                            if updated_fields:
                                db["relationships"][i].update(updated_fields)
                                updated += 1
                                break
            
            # Save updated database
            with open(db_path, 'w') as f:
                json.dump(db, f, indent=2, default=str)
            
            return {
                "success": True,
                "relationships_added": added,
                "relationships_updated": updated,
                "database_size_kb": Path(db_path).stat().st_size / 1024 if db_path.exists() else 0
            }
            
        except Exception as e:
            self.log("ERROR", f"Database update failed: {str(e)}")
            return {"success": False, "error": str(e)}

    async def sync_to_obsidian(self) -> Dict:
        """Export relationships to Obsidian format"""
        
        export_dir = Path.home() / ".hermes/gematria/obsidian_exports"
        
        try:
            # Create relationships markdown file
            rel_path = export_dir / "RELATIONSHIP_MATRIX.md"
            
            with open(rel_path, 'w') as f:
                f.write("# Knowledge Graph Relationship Matrix\n\n")
                f.write(f"**Generated:** {datetime.now().isoformat()}\n\n")
                f.write(f"**Total Relationships:** {len(self.relationships)}\n\n")
                
                # Group by source
                by_source = {}
                for rel in self.relationships:
                    source = rel.get("source", "unknown")
                    if source not in by_source:
                        by_source[source] = []
                    by_source[source].append(rel)
                
                for source, relations in sorted(by_source.items(), key=lambda x: len(x[1]), reverse=True)[:20]:
                    f.write(f"## {source}\n\n")
                    f.write(f"*{len(relations)} relationships*\n\n")
                    
                    for rel in relations[:30]:  # Limit per source
                        type_label = rel.get("type", "unknown").upper()
                        sym = rel.get("symbol", "?")
                        dom = rel.get("domain1", "")[:40] if rel.get("domain1") else ""
                        
                        f.write(f"- **{sym}** → {dom}\n")
                        f.write(f"  - Type: {type_label}\n")
                        f.write(f"  - Confidence: {rel.get('confidence', 0):.2f}\n")
                        f.write(f"  - Relevance: {rel.get('relevance_score', 0):.2f}\n\n")
                
                # Add relationship statistics
                f.write("## Relationship Statistics\n\n")
                
                type_counts = {}
                confidence_sum = 0
                
                for rel in self.relationships:
                    t = rel.get("type", "unknown")
                    type_counts[t] = type_counts.get(t, 0) + 1
                    confidence_sum += rel.get("confidence", 0)
                
                f.write(f"- Created: {type_counts.get('created', 0)}\n")
                f.write(f"- Updated: {type_counts.get('updated', 0)}\n\n")
                
                if type_counts:
                    avg_confidence = confidence_sum / len(self.relationships)
                    f.write(f"- Average Confidence: {avg_confidence:.2f}\n")
            
            self.log("INFO", f"Exported {len(self.relationships)} relationships to {rel_path}")
            
            return {
                "success": True,
                "export_path": str(rel_path),
                "relationships_exported": len(self.relationships)
            }
            
        except Exception as e:
            self.log("ERROR", f"Obsidian export failed: {str(e)}")
            return {"success": False, "error": str(e)}

    def log(self, level: str, message: str):
        print(f"[{self.name}] [{level}] {message}")
