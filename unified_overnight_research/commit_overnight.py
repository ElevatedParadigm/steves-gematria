#!/usr/bin/env python3
"""Commit overnight research outputs for version tracking."""
import subprocess
import sys
from datetime import datetime

def main():
    repo = '/home/avalonas/.hermes/gematria/unified_overnight_research'
    
    print(f"Committing overnight research at {datetime.now()}...")
    
    # Stage all changes
    print("Staging all files...")
    result = subprocess.run(
        ['git', '-C', repo, 'add', '.'],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"Git add error: {result.stderr}")
        sys.exit(1)
    
    # Commit with comprehensive message
    today = datetime.now().strftime('%Y-%m-%d')
    commit_msg = f"""[Overnight Research] {today} - Cycles complete with symbol-keying & hidden layering analysis

Core symbols tracked: 124, 963, 55, 111, 279, 666
Analysis types:
- Symbol-keying strategies for web search inputs
- Hidden layering detection across major numerological patterns  
- Domain convergence tracking
- Pattern trail extraction and image seed analysis
- Cultural patterns, geographic overlays, military geopolitical assessment

Previous commit ref: 03c9be7 (Cycle 302 baseline)"""
    
    print(f"Committing with message:\n{commit_msg}")
    result = subprocess.run(
        ['git', '-C', repo, 'commit', '-m', commit_msg],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"Git commit error:\n{result.stderr}")
        sys.exit(1)
    
    # Show commit info
    result = subprocess.run(
        ['git', '-C', repo, 'log', '-1', '--format=%H %an %ad %s'],
        capture_output=True, text=True
    )
    print(f"\nLatest commit:\n{result.stdout.strip()}")
    
    # Show stats
    result = subprocess.run(
        ['git', '-C', repo, 'rev-parse', '--short', 'HEAD'],
        capture_output=True, text=True
    )
    short_hash = result.stdout.strip()
    print(f"Commit hash (short): {short_hash}")

if __name__ == '__main__':
    main()
