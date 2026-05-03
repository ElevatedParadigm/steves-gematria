#!/usr/bin/env python3
"""Simple foreground commit for overnight research version tracking."""
import subprocess
import sys
from datetime import datetime

def main():
    repo = '/home/avalonas/.hermes/gematria/unified_overnight_research'
    
    # Set environment to avoid pager issues
    env = dict(__import__('os').environ)
    env['PAGER'] = 'cat'  # Don't use pager for long output
    
    print(f"Creating commit at {datetime.now()}\n")
    
    # Create commit using shell -c to run in subshell (avoids terminal() timeout issues)
    date_str = datetime.now().strftime('%Y-%m-%d')
    commit_msg = f"""Overnight research [{date_str}]: Symbol-keying & hidden layering analysis cycles complete

Core symbols (124,963,55,111,279,666) with HIDDEN_LAYERING ACTIVE
Web scraping via Wikipedia REST API - 2 sources per cycle
Domain convergence tracking and pattern trail extraction
Obsidian exports generated in cycle directories"""
    
    # Run git commit in foreground mode
    print("Committing changes...")
    result = subprocess.run(
        ['git', '-C', repo, 'commit', '-m', commit_msg],
        capture_output=False,  # Show output directly
        text=True
    )
    
    if result.returncode != 0:
        print(f"Git commit failed with exit code {result.returncode}")
        print(result.stderr)
        sys.exit(1)
    
    print("\nCommit successful!")
    
    # Show latest commit hash
    result = subprocess.run(
        ['git', '-C', repo, 'rev-parse', '--short', 'HEAD'],
        capture_output=True, text=True
    )
    short_hash = result.stdout.strip()
    print(f"Latest commit: {short_hash}")
    
    # Show commit message
    result = subprocess.run(
        ['git', '-C', repo, 'log', '-1', '--format=%B'],
        capture_output=True, text=True
    )
    print(f"\nCommit message:\n{result.stdout.strip()}")

if __name__ == '__main__':
    main()
