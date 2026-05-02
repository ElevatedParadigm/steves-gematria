#!/usr/bin/env python3
"""
Steve's Gematria Tools - Hybrid Local/CI Implementation
================================================================================

This module provides tool functions that work in BOTH environments:
  • LOCAL (your setup): Loads your actual gematria analysis code
  • CI (GitHub builds): Provides mock/stub implementations

Usage:
    From local scripts, import as usual:
        from gematria.tools import search_symbols
        # Locally resolves to your actual implementation via __init__.py
    
    From GitHub Actions:
        from gematria.tools import search_symbols
        # Resolves to this stub file for CI compatibility
"""

import sys
from pathlib import Path
import os
import logging
import json
from typing import Any, Dict, List, Optional, Union


def _load_local_implementation():
    """
    Try to load the local gematria.tools implementation.
    Falls back to stubs if not available (CI mode).
    """
    local_path = Path.home() / ".hermes" / "gematria" / "tools.py"
    
    if local_path.exists():
        # Local implementation exists - we're in Steve's environment
        try:
            import gematria.tools as tools_module
            return tools_module
        except ImportError:
            pass
    
    # No local implementation - use stubs (CI mode)
    logging.debug("Using stub implementations (CI or no local tools)")
    return None


# Initialize once
_local_tools = _load_local_implementation()

if _local_tools is not None:
    # Delegate to local implementation
    search_symbols = _local_tools.search_symbols
    search_web = _local_tools.search_web
    search_duckduckgo = _local_tools.search_duckduckgo
    get_db = _local_tools.get_db
else:
    # --- STUB IMPLEMENTATIONS FOR CI BUILD ---
    
    def search_symbols(query: str, *, domain_law: bool = False, 
                      max_results: int = 10) -> Dict[str, Any]:
        """
        Stub implementation for local symbol searching.
        
        Args:
            query: Term to search (e.g., "mountains", "battalion")
            domain_law: Whether to apply gematria domain laws
            max_results: Maximum results to return
            
        Returns:
            Mock result structure with no actual data
        """
        logging.info(f"[STUB] search_symbols called with: {query}")
        logging.warning("This is a CI build - using mock results")
        
        # Create a realistic-looking mock response
        return {
            "status": "CI_MODE",
            "message": f"Search for '{query}' requires local gematria database",
            "results": [],
            "core_symbols_triggered": [124, 963, 55],
            "domains": ["geographic", "military", "elemental"],
            "note": "Run in Steve's local environment with Firecrawl+Database"
        }
    
    def search_web(query: str, *, depth: int = 1, max_results: int = 5) -> List[Dict]:
        """Stub web search for CI mode"""
        logging.info(f"[STUB] search_web called")
        return [{"url": "example.com", "title": "[CI MODE]", "content": ""}]
    
    def search_duckduckgo(query: str, max_results: int = 3) -> Dict:
        """Stub DuckDuckGo search"""
        logging.info(f"[STUB] duckduckgo search")
        return {"results": []}
    
    # For database access (needed by falsification_engine.py)
    def get_db():
        """Return None - will fail gracefully in CI mode"""
        logging.warning("Database unavailable - CI build mode")
        return {}

# Export all functions
__all__ = [
    'search_symbols',
    'search_web', 
    'search_duckduckgo',
    'get_db'
]


if __name__ == "__main__":
    # Self-test
    print("Testing gematria.tools module...")
    result = search_symbols("test")
    print(f"search_symbols('test') returned: {result}")
