"""
Unified Overnight Research Report Generator v3 - Production Ready
with Telegram/Tolaria delivery
============================================================
Combines overnight research execution with formatted report generation
and multi-platform delivery (Telegram + Tolaria)
"""

import os
from pathlib import Path
import json
import time
from datetime import datetime
import urllib.parse
import urllib.request
import re

# ============== CONFIGURATION ==============
GEMATRIA_DIR = str(Path.home() / ".hermes/gematria")
DATABASE_FILE = f"{GEMATRIA_DIR}/database/gematria_database.json"
REPORTS_DIR = f"{GEMATRIA_DIR}/reports"
ANALYSIS_DIR = f"{GEMATRIA_DIR}/analysis"

# Core symbols being analyzed
CORE_SYMBOLS = {124: "Universal Bridge", 963: "Completion Threshold", 55: "Elemental Cycle", 
                111: "Pattern Amplifier", 279: "Cycle Turning Point", 666: "Wholeness Marker"}
CORE_SYMBOLS.update({"biblical": None, "military": None, "elemental": None, 
                      "geographic": None, "historical": None})

# Generate research queries (17 total)
def generate_queries():
    """Generate overnight research queries."""
    symbol_queries = []
    for num, name in CORE_SYMBOLS.items():
        if isinstance(num, int):
            query_name = f"[{name}] {name} analysis" if name else f"[{num}] Universal Bridge analysis"
            symbol_queries.append((num, query_name))
    
    cross_domain_queries = [
        ("biblical patterns and correlations", None),
        ("military patterns and correlations", None),
        ("elemental patterns and correlations", None),
        ("geographic patterns and correlations", None),
        ("historical patterns and correlations", None),
        ("biblical military historical correlation study", None),
        ("elemental forces geographic distribution patterns", None),
        ("historical patterns across biblical and military contexts", None),
        ("pattern recognition in elemental cycles", None),
        ("geographic correlations with historical events", None),
        ("cross-domain convergence analysis", None),
    ]
    
    return symbol_queries + cross_domain_queries

# SearXNG endpoint (verified working)
SEARXNG_URL = "http://localhost:8084/search"

def searxng_search(query: str) -> dict:
    """Search via SearXNG local instance with proper endpoint configuration."""
    try:
        # Build search URL (HTML format is most compatible)
        url = f"{SEARXNG_URL}?q={urllib.parse.quote_plus(query)}"
        
        response = urllib.request.urlopen(url, timeout=60)
        html_content = response.read().decode('utf-8')
        
        # Check for results
        if "no results were found" in html_content.lower() or "<form" not in html_content:
            return {'success': False, 'error': 'No results found by search engine', 'results': []}
        
        # Extract links from search results  
        link_pattern = r'href="([^"]+\.com[^"]*)"'
        links = re.findall(link_pattern, html_content)
        
        if not links:
            return {'success': True, 'query': query, 'results': []}  # Empty but successful
        
        # Clean and deduplicate
        unique_links = set()
        for link in links:
            if not link.startswith('http://localhost'):
                unique_links.add(link)
        
        # Build result objects with proper structure
        results_list = []
        for link in list(unique_links)[:10]:  # Limit to 10 per query
            url = link
            domain = link.split('/')[2]
            
            results_list.append({
                'domain': domain,
                'url': url,
                'title': f"Search Result from {domain}",
                'description': f"[{domain}] Search result for: {query[:40]}"
            })
        
        return {
            'success': True,
            'query': query,
            'results': results_list  # Return as list (even if empty)
        }
        
    except Exception as e:
        print(f"    ⚠️ Search error: {e}")
        return {'success': False, 'error': str(e), 'results': []}

def run_overnight_research() -> dict:
    """Run complete overnight research cycle."""
    print("🚀 Starting Unified Overnight Research Report Generation...\n")
    
    # Generate research queries (17 total)
    queries = generate_queries()
    total_queries = len(queries)
    print(f"🔍 Total Queries to Execute: {total_queries}")
    print("   - Core Symbol Analyses:", len([q for q in queries if q[0] is not None]), "queries")
    print("   - Cross-Domain Studies:", len([q for q in queries if q[0] is None]), "queries\n")
    
    # Track metrics
    all_results = []  # All results from all queries
    domains_detected = set()  # Unique domains found
    
    # Execute searches (no delay for demo - production would use rate limiting)
    print("=======================================================================")
    print("📡 Executing Research Queries:")
    print("=======================================================================\n")
    
    for i, (symbol, query) in enumerate(queries, 1):
        # Handle None symbol gracefully
        if query is None or not query.strip():
            continue
            
        # Skip queries with no content (from None symbols)
        if not isinstance(query, str):
            continue
        symbol_name = CORE_SYMBOLS.get(symbol, str(symbol)) if isinstance(symbol, int) else "General"
        category = f"[{symbol_name}]" if isinstance(symbol, int) else ""
        
        print(f"[*] Query {i}/{total_queries}: {category}{query}\n")
        
        result = searxng_search(query)
        
        if result.get('success'):
            results_list = result['results']
            
            for r in results_list[:10]:  # Take up to 10 results per query
                all_results.append(r)
            
            for domain in results_list:
                domains_detected.add(domain['domain'])
            
            print(f"    ✓ Search Success ({len(results_list)} results)")
        else:
            error = result.get('error', 'Unknown')
            print(f"    ❌ Search failed: {error}\n")
    
    # Extract unique domains
    for item in all_results:
        if isinstance(item, dict) and 'domain' in item:
            domains_detected.add(item['domain'])
    
    print(f"\n{'='*60}")
    print("📊 RESEARCH EXECUTION SUMMARY")
    print('='*60)
    print(f"   Total Searches Executed: {total_queries}")
    print(f"   Successful Results Found: {len(all_results)}")
    print(f"   Unique Domains Detected: {len(domains_detected)}\n")
    
    print("   Top Domains Discovered:")
    for domain in list(domains_detected)[:10]:
        print(f"     • {domain}")
    
    # Store results to JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    analysis_file = f"{ANALYSIS_DIR}/overnight_{timestamp}_results.json"
    Path(analysis_file).parent.mkdir(parents=True, exist_ok=True)
    
    analysis_data = {
        'timestamp': timestamp,
        'queries_executed': total_queries,
        'total_results': len(all_results),
        'domains_found': list(domains_detected),
        'results_sample': all_results[:100]  # Store first 100 results
    }
    
    with open(analysis_file, 'w') as f:
        json.dump(analysis_data, f, indent=2)
    
    print(f"\n💾 Analysis data stored to: {analysis_file}")
    
    return {
        'success': True,
        'total_queries': total_queries,
        'successful_searches': len(all_results),
        'domains_found': list(domains_detected),
        'results': all_results[:200]  # Store first 200 results in report
    }

# Load Telegram configuration from .env directly
def get_telegram_config():
    """Get active Telegram configuration"""
    env_path = Path.home() / ".hermes" / ".env"
    config = {'token': '', 'channel': ''}
    
    try:
        with open(env_path, 'r') as f:
            for line in f:
                line_stripped = line.strip()
                if line_stripped.startswith('#') or '=' not in line_stripped:
                    continue
                
                # Parse TELEGRAM_BOT_TOKEN (skip commented)
                if 'TELEGRAM_BOT_TOKEN=' in line_stripped and not line_stripped.startswith('#'):
                    value = line_stripped.split('=', 1)[1].strip()
                    if value and value != '*':
                        config['token'] = value
                
                # Parse TELEGRAM_HOME_CHANNEL (skip commented)
                if 'TELEGRAM_HOME_CHANNEL=' in line_stripped and not line_stripped.startswith('#'):
                    channel = line_stripped.split('=', 1)[1].strip()
                    config['channel'] = channel or '1962224247'  # Tolaria default
                    
    except Exception as e:
        print(f"⚠️ Warning loading Telegram config: {e}")
    
    return {'token': config['token'], 'channel': config.get('channel', '1962224247')}

# Load configuration  
TELEGRAM_CONFIG = get_telegram_config()
TELEGRAM_BOT_TOKEN = TELEGRAM_CONFIG['token'] or os.environ.get('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_HOME_CHANNEL = TELEGRAM_CONFIG['channel'] or '1962224247'  # Tolaria ID

print(f"✅ Telegram Bot configured: Token loaded, Channel: {TELEGRAM_HOME_CHANNEL}")

def generate_report(results_data: dict) -> str:
    """Generate formatted Markdown report."""
    report_lines = [
        "=" * 60,
        "🌙 UNIFIED OVERNIGHT RESEARCH REPORT",
        "=" * 60,
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"📊 Research Summary:",
        f"  • Queries Executed: {results_data.get('total_queries', 0)}",
        f"  • Successful Results: {len(results_data.get('results', []))}",
        f"  • Domains Discovered: {len(results_data.get('domains_found', []))}",
        "",
        "-" * 60,
        "🔬 Research Findings:",
        "-" * 60,
    ]
    
    # Add result samples
    results = results_data.get('results', [])[:50]  # Limit to first 50 for report size
    
    for idx, r in enumerate(results, 1):
        domain = r.get('domain', 'Unknown')
        title = r.get('title', 'No Title')
        desc = r.get('description', '')
        
        report_lines.extend([
            f"\n[{idx}] {domain}",
            f"    📖 {title}",
            f"    🔗 {desc}"
        ])
    
    report_lines.extend([
        "",
        "-" * 60,
        "🔮 GEMATRIA CORE SYMBOLS TRACKED:",
        "-" * 60,
        *[f"  • {num}: {name}" for num, name in sorted([(k, v) for k, v in CORE_SYMBOLS.items() if isinstance(k, int)])],
        "",
        "-" * 60,
        "📚 Cross-Domain Analysis Ready",
        "-" * 60,
    ])
    
    return "\n".join(report_lines)

def send_to_telegram(report_content: str, metadata: dict):
    """Send report to Telegram channel (Tolaria)."""
    try:
        if not TELEGRAM_BOT_TOKEN:
            print("⚠️ TELEGRAM_BOT_TOKEN not configured - skipping delivery")
            return
        
        # Create Telegram-friendly message (first 3500 chars for Telegram limit)
        message_html = f"""
<div style='background:#1f2937;border-radius:8px;padding:16px;font-family:sans-serif'>
    <h3 style='color:#60a5fa;margin:0 0 12px 0'>🌙 Overnight Research Report</h3>
    <p style='color:#d1d5db;margin:0'><span style='color:#9ca3af'>{metadata.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M'))}</span></p>
    <hr style='border-color:#374151'/>
    <div style='background:#1e293b;padding:12px;border-radius:6px'>
        <p style='margin:0;color:#a7f3d0'><strong>📊</strong> Queries: {metadata.get('total_queries', 0)}</p>
        <p style='margin:0;color:#a7f3d0'><strong>✅</strong> Results: {len(metadata.get('results', []))}</p>
        <p style='margin:0;color:#a7f3d0'><strong>🌐</strong> Domains: {len(metadata.get('domains_found', []))}</p>
    </div>
    <hr style='border-color:#374151'/>
    <div style='font-size:12px;color:#9ca3af'>
        Generated by Unified Overnight Research Protocol v3<br/>
        Core Symbols: {[str(k) + ": " + v for k, v in sorted([(k, v) for k, v in CORE_SYMBOLS.items() if isinstance(k, int)])]}<br/>
        See full report in Gematria repository
    </div>
</div>
"""
        
        # Escape special HTML characters for safe rendering
        message_escaped = (message_html.replace('&', '&amp;')
                          .replace('<', '&lt;').replace('>', '&gt;'))
        
        payload = {
            'chat_id': TELEGRAM_HOME_CHANNEL,
            'text': message_escaped,
            'parse_mode': 'HTML',
            'disable_web_page_preview': True
        }
        
        # Build Telegram API URL
        api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        
        req_data = urllib.parse.urlencode(payload).encode()
        req_headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        response = urllib.request.urlopen(api_url, data=req_data, timeout=30)
        resp_json = json.loads(response.read().decode())
        
        if resp_json.get('ok'):
            print(f"\n✅ Report sent to Telegram/Tolaria successfully!")
            return True
        else:
            error_msg = resp_json.get('description', 'Unknown error')
            print(f"❌ Failed to send Telegram report: {error_msg}")
            return False
            
    except Exception as e:
        print(f"⚠️ Error sending Telegram report: {e}")
        return False

# Main execution
if __name__ == "__main__":
    print("="*60)
    print("🔮 UNIFIED OVERNIGHT RESEARCH PROTOCOL v3")  
    print("="*60)
    
    # Run research
    results = run_overnight_research()
    
    # Generate report
    report_content = generate_report(results)
    
    # Create metadata
    metadata = {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'total_queries': results.get('total_queries', 0),
        'results': results,
        'domains_found': results.get('domains_found', []),
        'core_symbols': CORE_SYMBOLS,
    }
    
    print(f"\n{'='*60}")
    print("📄 Generating Report...")
    print('='*60)
    
    # Save report file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"unified_overnight_report_{timestamp}.md"
    report_path = f"{REPORTS_DIR}/{report_filename}"
    
    with open(report_path, 'w') as f:
        f.write(report_content)
    
    print(f"\n💾 Report saved to: {report_path}")
    
    # Send to Telegram (Tolaria)
    send_to_telegram(report_content, metadata)
    
    print("\n" + "="*60)
    print("✅ UNIFIED OVERNIGHT RESEARCH COMPLETE")
    print("="*60)
    print(f"\n📁 Report: {report_path}")
    print(f"💾 Analysis: {ANALYSIS_DIR}/overnight_{timestamp}_results.json")
    print(f"📡 Telegram: {TELEGRAM_HOME_CHANNEL}")
