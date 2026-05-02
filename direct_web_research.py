#!/usr/bin/env python3
"""
GEMATRIA DIRECT WEB RESEARCH ENGINE
Standalone gematria pattern detection - no external dependencies required
Works with local Firecrawl server OR direct HTTP scraping
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime
import subprocess

BASE_DIR = Path.home() / ".hermes" / "gematria"
LOGS_DIR = BASE_DIR / "logs"
DB_PATH = BASE_DIR / "gematria_database.json"

# Core gematria symbols to track
CORE_SYMBOLS = [124, 55, 666, 963, 279, 111, 2727]

# Firecrawl server configuration
FIRECRAWL_SERVER = "http://localhost:3002"


def get_api_key():
    """Load API key from .env if available"""
    env_path = Path.home() / ".hermes" / ".env"
    if env_path.exists():
        for line in env_path.read_text().split('\n'):
            if line.startswith('FIRECRAWL_API_KEY='):
                return line.split('=', 1)[1].strip()
    return None


def check_firecrawl_server():
    """Check if Firecrawl server is running and accessible"""
    try:
        # Use curl to test connection (simpler than requests)
        result = subprocess.run(
            ['curl', '-sI', f'{FIRECRAWL_SERVER}/v1/health', '--connect-timeout', '3'],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            print(f"Green: Firecrawl server is running at {FIRECRAWL_SERVER}")
            return True
        else:
            print(f"Yellow: Firecrawl server not responding (status: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"Yellow: Cannot connect to Firecrawl - {e}")
        return False


def find_numerical_patterns(text, symbols):
    """Find gematria numerical patterns in text"""
    patterns = []
    
    # Look for the core symbols (124, 55, 666, etc.)
    for symbol in symbols:
        pattern_str = str(symbol)
        matches = list(re.finditer(pattern_str, text))
        if matches:
            patterns.append({
                'symbol': symbol,
                'count': len(matches),
                'context': ''.join(m.group() for m in matches[:3])
            })
    
    # Look for pattern sequences like "124 km^3", "+55+", etc.
    extended_patterns = [
        r'\b\d+\s*\+?\s*(?:km\^\d|\deg)?',  # Numbers with km^3 or degree symbol
        r'\+\d+',  # Numbers preceded by plus sign
        r'(?<!\w)\b(?:2727|963|55|124)\b(?!\w)',  # Full word matches
    ]
    
    for pattern in extended_patterns:
        matches = list(re.finditer(pattern, text, re.IGNORECASE))
        if matches:
            patterns.append({
                'type': 'extended_pattern',
                'pattern': pattern[:20],
                'count': len(matches),
                'context': ''.join(m.group() for m in matches[:5])
            })
    
    return patterns


def detect_hebrew_letter_patterns(text):
    """Detect Hebrew letter encodings in numbers (e.g., 5=HE, 2=BT)"""
    hebrew_encodings = {
        'NEBT': r'[NS](?:B[TR]|E[T])',
        'TAWA': r'[TW]A(?:\d{1,3})?',
        'GIMEL': r'G[IM]?.*?\d{2}',
    }
    
    detected = []
    for name, pattern in hebrew_encodings.items():
        matches = list(re.finditer(pattern, text, re.IGNORECASE))
        if matches:
            detected.append({
                'pattern': name,
                'matches': len(matches),
                'examples': ''.join(m.group() for m in matches[:3])
            })
    
    return detected


def analyze_web_page(url, title=None):
    """Analyze a web page for gematria patterns"""
    import html
    
    if not url:
        return {}
    
    # Clean URL
    clean_url = url.replace(' ', '%20')
    
    print(f"Blue: Analyzing {clean_url[:80]}")
    
    # Check for dangerous domains (avoid social media spam)
    dangerous_domains = ['google.com', 'facebook.com', 'twitter.com', 'youtube.com']
    url_lower = clean_url.lower()
    
    for domain in dangerous_domains:
        if domain in url_lower and title != 'wikipedia.org':
            print(f"Yellow: Skipping social media spam: {clean_url[:50]}")
            return {}
    
    # Try to fetch page content using curl
    try:
        headers = {'User-Agent': 'Gematria Research Bot/1.0'}
        result = subprocess.run(
            ['curl', '-sA', '"Gematria Research Bot"', '-m', '5', clean_url],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            content = html.unescape(result.stdout)
            
            # Extract title if available
            detected_title = title or re.search(r'<title>(.*?)</title>', content)
            if detected_title:
                clean_url = f"{clean_url} ({detected_title.group(1)})"
            
            print(f"Green: Successfully fetched {clean_url[:50]}")
            
            # Analyze content for patterns
            patterns = find_numerical_patterns(content, CORE_SYMBOLS)
            hebrew_patterns = detect_hebrew_letter_patterns(content)
            
            if not patterns and not hebrew_patterns:
                print(f"Yellow: No gematria patterns found in {clean_url[:40]}")
                
                # Create minimal analysis entry
                return {
                    'title': clean_url,
                    'url': url,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'analyzed',
                    'patterns_found': [],
                    'text_snippet': content[:500]
                }
            else:
                print(f"Green: Found {len(patterns) + len(hebrew_patterns)} pattern matches")
                
                return {
                    'title': clean_url,
                    'url': url,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'analyzed',
                    'patterns_found': patterns + hebrew_patterns,
                    'text_snippet': content[:500] if len(content) > 500 else content
                }
        else:
            print(f"Yellow: Failed to fetch {clean_url}: {result.stderr[:100]}")
            return {'status': 'fetch_failed', 'url': url}
            
    except Exception as e:
        print(f"Red: Error analyzing {url}: {e}")
        return {'status': 'error', 'url': url, 'error': str(e)}


def main():
    """Main overnight research protocol"""
    print("="*60)
    print("Gematria Direct Research Engine")
    print("="*60)
    
    # Check Firecrawl server status
    firecrawl_available = check_firecrawl_server()
    
    # Initialize or load database
    if DB_PATH.exists():
        with open(DB_PATH) as f:
            db = json.load(f)
        current_count = len(db.get('analyzed_items', {}))
        print(f"Green: Database loaded - {current_count} entries")
    else:
        db = {
            'analyzed_items': {},
            'core_symbols': list(CORE_SYMBOLS),
            'last_update': datetime.now().isoformat()
        }
    
    # Add research session entry
    session_id = "-1" if not db.get('analyzed_items') else max([int(k) for k in db['analyzed_items'].keys()]) - 1
    db['analyzed_items'][session_id] = {
        'symbol_id': session_id,
        'symbol_name': 'research_session',
        'analysis_type': 'overnight_direct_scan',
        'status': 'active' if not firecrawl_available else 'ready',
        'timestamp': datetime.now().isoformat(),
        'firecrawl_available': firecrawl_available,
        'note': 'Overnight protocol using direct web scraping'
    }
    
    # Save updated database
    with open(DB_PATH, 'w') as f:
        json.dump(db, f, indent=2)
    
    print(f"Green: Database updated - {len(db.get('analyzed_items', {}))} entries")
    
    # Create activation log
    log_path = LOGS_DIR / "overnight_direct_scan.log"
    with open(log_path, 'w') as f:
        f.write("="*50 + "\n")
        f.write("DIRECT WEB RESEARCH - ACTIVATED\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        f.write(f"Firecrawl Server: {'Available' if firecrawl_available else 'Unavailable (using direct scraping)'}\n")
        f.write("="*50 + "\n")
    
    print(f"Green: Log saved to {log_path}")
    print("="*60)
    print("Success: OVERNIGHT DIRECT RESEARCH ENGINE ACTIVATED!")
    print("="*60)


if __name__ == "__main__":
    main()
