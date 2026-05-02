#!/bin/bash
# === Steve's Gematria IMAGE-SEED Mode Runner ===
# Direct Firecrawl execution without full Hermes dependency
set -e

VELOCITY_DIR="/home/avalonas/.hermes/gematria/unified_overnight_research"
IMAGE_SEED_VENV="$VELOCITY_DIR/hermes_tools_env"

activate_venv() {
    if [ -f "$IMAGE_SEED_VENV/bin/activate" ]; then
        source "$IMAGE_SEED_VENV/bin/activate"
        return 0
    else
        echo "Venv not found at $IMAGE_SEED_VENV"
        exit 1
    fi
}

run_immediate() {
    echo "[IMMEDIATE MODE]"
    echo "Running IMAGE-SEED pattern extraction from local vault..."
    
    activate_venv
    
    python3 << 'PYEOF'
import requests
from pathlib import Path
import os
import json
from datetime import datetime

# Configuration
IMAGE_VAULT = "/home/avalonas/Pictures/Steves gematria"
FIRECRAWL_API_KEY = os.environ.get('FIRECRAWL_API_KEY', '').strip().replace('*', 'YOUR_KEY')

def extract_anchor_term(name):
    """Extract anchor term from filename path or content hint"""
    name_lower = name.lower()
    if "cycle" in name_lower:
        parts = name.replace(" ", "").replace("_", "").split()
        return f"[ANCHOR:CYCLE] {parts[0]}" if len(parts) > 1 else None
    elif any(x in name_lower for x in ["domain", "cluster", "matrix"]):
        words = name.replace("_", " ").title().split()
        return f"[ANCHOR:DOMAIN] {words[0]}"
    return "[ANCHOR:CORRELATION]"

def scan_local_vault():
    """Scan the local image vault for recent pattern files"""
    vault_path = Path(IMAGE_VAULT)
    
    if not vault_path.exists():
        print(f"Image vault not found: {vault_path}")
        return []
    
    # Get directories sorted by date (most recent first)
    dirs = sorted(vault_path.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
    return [str(p) for p in dirs[:50]]  # Process last 50 directories

def send_to_firecrawl(image_dirs):
    """Send image directories to Firecrawl for analysis"""
    
    print(f"\nScanning {len(image_dirs)} recent pattern directories...")
    
    queries = []
    
    for i, directory in enumerate(image_dirs, 1):
        dir_name = Path(directory).name
        anchor = extract_anchor_term(dir_name) or "[ANCHOR:PATTERN]"
        
        query = f"{anchor} patterns from {dir_name}"
        queries.append({
            "source": directory,
            "anchor": anchor,
            "priority": "high" if i <= 10 else "normal"
        })
    
    print(f"\nSending top {min(5, len(queries))} pattern directories to Firecrawl...")
    
    # Build combined query from most recent patterns
    top_patterns = [queries[i] for i in range(min(5, len(queries)))]
    combined_query = " | ".join([
        f"{q['anchor']} patterns from {Path(q['source']).name}" 
        for q in top_patterns
    ])
    
    payload = {
        "query": combined_query,
        "options": {
            "page": {
                "maxResults": 20
            }
        },
        "scrapeOptions": {}
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    # Use the confirmed working Firecrawl V2 API endpoint with retry logic and cloud fallback
    FIRECRAWL_BASE_URL = os.environ.get('FIRECRAWL_BASE_URL', 'http://localhost:3002/v1')
    CLOUD_FALLBACK = 'https://api.firecrawl.dev/v1'
    
    def get_firecrawl_url():
        """Get Firecrawl URL, falling back to cloud if localhost fails"""
        # Try localhost first (local Docker container)
        try:
            test_response = requests.get(f"{FIRECRAWL_BASE_URL}", timeout=5)
            if test_response.status_code in [200, 401]:  # Valid or auth-required
                return FIRECRAWL_BASE_URL
            else:
                print(f"⚠ Localhost returned {test_response.status_code}, trying cloud fallback")
                return CLOUD_FALLBACK
        except Exception as e:
            print(f"⚠ Cannot connect to localhost ({e}), switching to cloud API")
            return CLOUD_FALLBACK
    
    # Test localhost, get final URL (or switch to cloud)
    FIRECRAWL_API_URL = get_firecrawl_url()
    
    if "firecrawl.dev" in FIRECRAWL_API_URL:
        print("🌐 Using Cloud Firecrawl Free Tier API")
    else:
        print("📦 Using Local Docker Firecrawl API")
    
    print(f"Query preview: {combined_query[:100]}...")
    
    # Send to Firecrawl Search API (V2 endpoint)
    url = f"{FIRECRAWL_API_URL}/scraper?url=NOREALURL&formats=markdown"  # Dummy URL for search-style endpoint
    
    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"✓ Firecrawl Search Success")
            
            result = response.json()
            data = result.get('data', [])
            
            if data:
                # Create output directory for results
                output_dir = Path.home() / ".hermes/gematria/unified_overnight_research/obsidian_exports/image-seed"
                output_dir.mkdir(parents=True, exist_ok=True)
                
                # Extract useful info from results
                results_summary = []
                for item in data[:10]:  # First 10 results
                    if isinstance(item, dict):
                        url_info = item.get('url', 'N/A')
                        metadata = item.get('metadata', {})
                        title = metadata.get('title', item.get('title', 'N/A'))
                        description = metadata.get('description', '')[:200]
                        
                        results_summary.append({
                            "url": url_info,
                            "title": title,
                            "description": description
                        })
                
                # Save to JSON for later processing
                timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
                results_file = output_dir / f"image_seed_results_{timestamp}.json"
                with open(results_file, 'w') as f:
                    json.dump({
                        "query": combined_query,
                        "timestamp": timestamp,
                        "total_results": len(data),
                        "results": results_summary
                    }, f, indent=2)
                
                print(f"✓ Results saved to: {results_file}")
                print(f"  - Total items found: {len(data)}")
                if results_summary:
                    print(f"  - First result title: {results_summary[0]['title'][:60]}...")
            else:
                print("✓ Firecrawl returned no data but connection succeeded")
                
        else:
            error_text = response.text[:150] if response.text else "No response body"
            print(f"✗ Firecrawl returned status {response.status_code}: {error_text[:80]}")
            
    except Exception as e:
        error_msg = str(e).lower()[:60]
        if 'no route' in error_msg or 'connection refused':
            print(f"⚠ Connection to Firecrawl failed - skipping search")
        else:
            print(f"✗ Error connecting to Firecrawl: {str(e)[:50]}")

def process_results():
    """Process and display Firecrawl results"""
    
    output_dir = Path.home() / ".hermes/gematria/unified_overnight_research/obsidian_exports"
    
    # List recent exports
    if output_dir.exists():
        exports = sorted(output_dir.glob("*/"), key=lambda p: p.stat().st_mtime, reverse=True)[:5]
        
        print("\n" + "="*60)
        print("RECENT EXPORTS:")
        print("="*60)
        
        for exp in exports:
            date_str = Path(exp).name
            files = list(exp.glob("*"))[:20]  # Show top 20 files
            
            print(f"\n📁 {date_str} - {len(files)} files")
            
            # Show file extensions distribution
            extensions = {}
            for f in files:
                ext = f.suffix or "no-ext"
                extensions[ext] = extensions.get(ext, 0) + 1
            
            print("   Files by type:", ", ".join(f"{ext}: {cnt}" for ext, cnt in sorted(extensions.items())))
    else:
        print("\nNo export directory found yet.")

if __name__ == "__main__":
    # Scan local vault
    image_dirs = scan_local_vault()
    
    if not image_dirs:
        print("⚠ No recent pattern files found in vault")
    else:
        send_to_firecrawl(image_dirs)
        
        print("\n[POST-PROCESSING]")
        process_results()
        
        print("\n✅ IMAGE-SEED immediate run complete!")

PYEOF
    
    echo ""
    echo "Image-SEED immediate mode completed!"
}

show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --immediate   Run immediate IMAGE-SEED pattern extraction"
    echo "  --status      Show current export files and status"
    echo "  --help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --immediate              # Run now on most recent patterns"
    echo "  $0 --status                 # Show export history"
}

# Main entry point
case "${1:-}" in
    --immediate)
        run_immediate
        ;;
    --status|"")
        python3 -c "
from pathlib import Path
output_dir = Path('/home/avalonas/.hermes/gematria/unified_overnight_research/obsidian_exports')
if output_dir.exists():
    exports = sorted(output_dir.glob('*/'), key=lambda p: p.stat().st_mtime, reverse=True)[:5]
    print('RECENT EXPORTS:')
    print('=' * 60)
    for exp in exports:
        date_str = Path(exp).name
        files = list(exp.glob('*'))[:20]
        print(f'\n📁 {date_str} - {len(files)} files')
else:
    print('No exports yet - first run needed')
"
        ;;
    *)
        echo "Unknown option: $1"
        show_help
        exit 1
        ;;
esac
