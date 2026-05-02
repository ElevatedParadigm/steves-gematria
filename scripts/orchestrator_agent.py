#!/usr/bin/env python3
"""
Multi-Agent Cooperation Architecture for Steve's Gematria
===================

Orchestrates specialized AI agents for:
- Pattern discovery and web scanning
- Cross-domain analysis
- Knowledge graph maintenance
- Convergence monitoring
- Alert management

Agent Types:
├── Orchestrator Agent (main coordinator)
├── Pattern Discovery Agent (Firecrawl scans)
├── Cross-Domain Analysis Agent (pattern correlation)
├── Knowledge Graph Agent (relationship tracking)
└── Convergence Monitor Agent (elemental/cycle convergence)
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
import aiohttp
import aiofiles

# Add parent to path for imports
sys.path.insert(0, str(Path.home() / ".hermes"))

class AgentBase:
    """Base class for all gematria agents"""
    
    def __init__(self, name: str, agent_type: str, description: str):
        self.name = name
        self.agent_type = agent_type
        self.description = description
        self.id = hash(name) % 10000
        self.last_active = datetime.now()
        self.task_count = 0
        self.success_rate = 0.0
        self.logs: List[Dict] = []
        
    def log(self, level: str, message: str):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message
        }
        self.logs.append(entry)
        print(f"[{self.name}] [{level}] {message}")
        
    def _log(self, level: str, message: str):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message
        }
        self.logs.append(entry)
        
    @property
    def status(self) -> str:
        if self.success_rate >= 0.95:
            return "EXCELLENT"
        elif self.success_rate >= 0.85:
            return "GOOD"
        elif self.success_rate >= 0.70:
            return "FAIR"
        else:
            return "POOR"

class OrchestratorAgent(AgentBase):
    """Main orchestrator agent that coordinates all other agents"""
    
    def __init__(self, database_path: str = "/home/avalonas/.hermes/gematria/database.json"):
        super().__init__("orchestrator", "orchestrator", "Main coordination agent")
        self.database_path = database_path
        self.agents: List[AgentBase] = []
        self.workflow_cache: Dict[str, Any] = {}
        
    async def initialize(self) -> None:
        """Initialize the orchestrator and all agents"""
        
        # Import agent classes from their modules - using relative paths within gematria directory
        import sys
        sys.path.insert(0, str(Path.home() / ".hermes/gematria/scripts"))
        
        from pattern_discovery_agent import PatternDiscoveryAgent
        from cross_domain_analysis_agent import CrossDomainAnalysisAgent
        from knowledge_graph_agent import KnowledgeGraphAgent
        from convergence_monitor_agent import ConvergenceMonitorAgent
        
        # Initialize specialized agents
        self.agents = [
            PatternDiscoveryAgent(),
            CrossDomainAnalysisAgent(),
            KnowledgeGraphAgent(),
            ConvergenceMonitorAgent()
        ]
        
        self.log("INFO", f"Orchestrator initialized with {len(self.agents)} agents")
        for agent in self.agents:
            await agent.initialize()
            
    async def task_registry(self, task_name: str, task_payload: Dict) -> Dict:
        """Route tasks to appropriate agents"""
        
        # Simple routing logic based on task type
        if "scan" in task_name.lower() or "search" in task_name.lower():
            target = self.agents[0]  # Pattern Discovery
        elif "analyze" in task_name.lower() or "correlate" in task_name.lower():
            target = self.agents[1]  # Cross-Domain Analysis  
        elif "graph" in task_name.lower() or "relationship" in task_name.lower():
            target = self.agents[2]  # Knowledge Graph
        elif "convergence" in task_name.lower() or "elemental" in task_name.lower():
            target = self.agents[3]  # Convergence Monitor
        else:
            target = self.agents[1]  # Default to analysis
            
        try:
            result = await asyncio.wait_for(
                target.execute_task(task_payload),
                timeout=300  # 5 minute timeout per task
            )
            self.log("INFO", f"Task '{task_name}' completed via {target.name}")
            return {"success": True, "result": result, "agent": target.name}
        except asyncio.TimeoutError:
            self.log("ERROR", f"Task '{task_name}' timed out after 5 minutes")
            return {"success": False, "error": "timeout"}
        except Exception as e:
            self.log("ERROR", f"Task '{task_name}' failed: {str(e)}")
            return {"success": False, "error": str(e)}
            
    async def daily_workflows(self) -> Dict:
        """Run all agents through their primary workflows"""
        
        workflow = {
            "timestamp": datetime.now().isoformat(),
            "agents": {},
            "summary": {}
        }
        
        for agent in self.agents:
            try:
                result = await asyncio.wait_for(
                    agent.execute_workflow(),
                    timeout=120  # 2 minute per workflow
                )
                workflow["agents"][agent.name] = {
                    "status": "completed",
                    "result": result,
                    "success": True
                }
                self.log("INFO", f"Agent {agent.name} workflow completed")
            except asyncio.TimeoutError:
                workflow["agents"][agent.name] = {
                    "status": "timeout",
                    "success": False
                }
                self.log("WARN", f"Agent {agent.name} workflow timed out")
            except Exception as e:
                workflow["agents"][agent.name] = {
                    "status": "failed",
                    "error": str(e),
                    "success": False
                }
                self.log("ERROR", f"Agent {agent.name} workflow failed: {str(e)}")
        
        # Update summary statistics
        successful = sum(1 for a in workflow["agents"].values() if a.get("success"))
        workflow["summary"] = {
            "total_agents": len(self.agents),
            "successful": successful,
            "success_rate": successful / len(self.agents) if self.agents else 0
        }
        
        return workflow

class PatternDiscoveryAgent(AgentBase):
    """Scans web for core gematria patterns using Firecrawl"""
    
    def __init__(self, name: str = "pattern-discovery", agent_type: str = "discovery"):
        super().__init__(name, agent_type, "Web pattern discovery via Firecrawl")
        
    async def execute_workflow(self) -> Dict:
        """Run daily web scanning for core symbols"""
        self.log("INFO", "Starting pattern discovery workflow")
        
        from scripts.overnight_research import search_for_pattern
        
        # Search for each core symbol
        core_symbols = [124, 963, 55, 111, 279, 666]
        
        all_results = {f"symbol_{s}": [] for s in core_symbols}
        
        for symbol in core_symbols:
            try:
                results = await search_for_pattern(str(symbol))
                all_results[f"symbol_{symbol}"] = results
                
                self.log("INFO", f"Found {len(results)} occurrences of symbol {symbol}")
                
                # Update database
                if results and "items" in results:
                    for item in results["items"]:
                        await KnowledgeGraphAgent.register_observed_item(item)
                        
            except Exception as e:
                self.log("WARN", f"Symbol {symbol} search failed: {str(e)}")
                all_results[f"symbol_{symbol}"] = []
        
        summary = {
            "symbols_searched": core_symbols,
            "total_occurrences": sum(len(r) for r in all_results.values()),
            "by_symbol": {k: len(v) for k, v in all_results.items()}
        }
        
        self.log("INFO", f"Discovery complete. Total occurrences: {summary['total_occurrences']}")
        return summary

class CrossDomainAnalysisAgent(AgentBase):
    """Analyzes patterns across multiple domains"""
    
    def __init__(self, name: str = "cross-domain-analysis", agent_type: str = "analysis"):
        super().__init__(name, agent_type, "Cross-domain pattern correlation")
        
    async def execute_workflow(self) -> Dict:
        """Run cross-domain convergence analysis"""
        self.log("INFO", "Starting cross-domain analysis workflow")
        
        from scripts.overnight_research import analyze_domain_convergence
        
        result = await analyze_domain_convergence()
        
        if result and "convergences" in result:
            top_convergences = sorted(
                result["convergences"],
                key=lambda x: x.get("convergence_score", 0),
                reverse=True
            )[:10]
            
            self.log("INFO", f"Found {len(result['convergences'])} convergences")
            self.log("INFO", f"Top convergence: {' × '.join(top_convergences[0].get('symbols', [])) if top_convergences else 'None'}")
        
        return result

class KnowledgeGraphAgent(AgentBase):
    """Manages knowledge graph relationships and database updates"""
    
    def __init__(self, name: str = "knowledge-graph", agent_type: str = "maintenance"):
        super().__init__(name, agent_type, "Knowledge graph maintenance")
        
    async def execute_workflow(self) -> Dict:
        """Run relationship extraction and database sync"""
        self.log("INFO", "Starting knowledge graph sync workflow")
        
        from scripts.overnight_research import extract_domain_relationships
        
        result = await extract_domain_relationships()
        
        if result:
            relationships_created = sum(
                1 for r in result.get("relationships", [])
                if r.get("type") == "created" or r.get("type") == "updated"
            )
            
            self.log("INFO", f"Created/Updated {relationships_created} relationships")
        else:
            self.log("WARN", "No relationships found or extraction failed")
        
        return result

class ConvergenceMonitorAgent(AgentBase):
    """Monitors elemental and cycle convergence patterns"""
    
    def __init__(self, name: str = "convergence-monitor", agent_type: str = "monitoring"):
        super().__init__(name, agent_type, "Elemental/cycle convergence monitoring")
        
    async def execute_workflow(self) -> Dict:
        """Run elemental force tracking and cycle analysis"""
        self.log("INFO", "Starting convergence monitoring workflow")
        
        from scripts.overnight_research import find_elemental_patterns
        
        result = await find_elemental_patterns()
        
        if result:
            fire_count = sum(1 for p in result.get("patterns", []) if "fire" in str(p.get("force", "")).lower())
            
            self.log("INFO", f"Fire patterns detected: {fire_count}")
            self.log("INFO", f"Total elemental patterns found: {len(result.get('patterns', []))}")
        
        return result

# Agent Factory Pattern for easy agent creation
async def create_orchestrator():
    """Factory method to create and initialize orchestrator"""
    orchestrator = OrchestratorAgent()
    await orchestrator.initialize()
    return orchestrator

async def run_agents_in_sequence(orchestrator: OrchestratorAgent) -> List[Dict]:
    """Run all agents in sequence with result collection"""
    
    results = []
    
    for agent in orchestrator.agents:
        self.log("INFO", f"Executing workflow for {agent.name}")
        result = await agent.execute_workflow()
        results.append({
            "agent": agent.name,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
    return results

async def run_agents_parallel(orchestrator: OrchestratorAgent) -> Dict:
    """Run all agents in parallel for maximum throughput"""
    
    tasks = [agent.execute_workflow() for agent in orchestrator.agents]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return {
        "results": [
            {"agent": agent.name, "result": r, "error": None} 
            if isinstance(r, dict) else {"agent": agent.name, "result": None, "error": str(r)}
            for agent, r in zip(orchestrator.agents, results)
        ],
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import asyncio
    
    print("🤖 Multi-Agent Orchestrator Starting...")
    
    try:
        # Create and initialize orchestrator
        orchestrator = asyncio.run(create_orchestrator())
        
        print(f"✅ Initialized {len(orchestrator.agents)} agents")
        for agent in orchestrator.agents:
            print(f"   • {agent.name}")
        
        print("\n📋 Running daily workflow...")
        workflow = asyncio.run(orchestrator.daily_workflows())
        
        # Print results
        print("\n📊 Workflow Results:")
        for agent_name, data in workflow["agents"].items():
            status = "✅" if data.get("success") else "❌"
            print(f"{status} {agent_name}: {data.get('status', 'N/A')}")
        
    except KeyboardInterrupt:
        print("\n⚠️  Orchestrator stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
