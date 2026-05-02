"""
Gematria Visualization Engine
Generates HTML reports from database metrics for web dashboard integration.
Usage: python visualization_engine.py --output html_report.html
       from dashboard_server import generate_html_report (returns Flask app)
"""

import json
from pathlib import Path
from datetime import datetime


def load_database():
    """Load gematria database."""
    db_path = Path.home() / ".hermes" / "gematria" / "database" / "gematria_database.json"
    
    try:
        with open(db_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠ Error loading database: {e}")
        return None


def calculate_metrics(data):
    """Calculate dashboard metrics from database."""
    metadata = data.get("metadata", {})
    entries = data.get("entries", {})
    
    core_symbols = metadata.get("core_symbols", [])
    elemental_forces = metadata.get("elemental_forces", [])
    domains_tracked = metadata.get("domains_tracked", [])
    
    # Count images and extract timestamps
    images = data.get("images", [])
    image_count = len(images)
    
    image_timestamps = [img.get("timestamp", "") for img in images if img.get("timestamp")]
    latest_timestamp = max(image_timestamps) if image_timestamps else "N/A"
    
    # Extract all unique symbols from entries
    all_symbols = set()
    for entry_key, entry_data in entries.items():
        detected = entry_data.get("core_symbols_detected", [])
        for item in detected:
            if isinstance(item, dict):
                item_value = item.get("number", item.get("symbol", str(item)))
            else:
                item_value = str(item)
            all_symbols.add(item_value)
    
    # Calculate correlations (count occurrences per symbol)
    symbol_correlations = {}
    for symbol in metadata.get("search_indices", {}).get("core_numbers", []):
        count = sum(1 
            for e in entries.values() 
            for item in e.get("core_symbols_detected", [])
            if str(symbol) == str(item.get("number", item.get("symbol", item)))
        )
        symbol_correlations[str(symbol)] = {
            "occurrences": count,
            "contexts": list(set(str(symbol) * 3)),  # Placeholder - actual contexts would be more detailed
        }
    
    # Get recent batch reports (first 10 keys)
    batch_reports = sorted(entries.keys(), key=str.lower)[:10]
    
    return {
        "core_symbols": core_symbols,
        "all_symbols_detected": sorted(list(all_symbols)),
        "image_count": image_count,
        "latest_timestamp": latest_timestamp,
        "batch_reports": batch_reports,
        "domains_tracked": domains_tracked,
        "elemental_forces": elemental_forces,
        "symbol_correlations": symbol_correlations,
    }


def generate_html_report(db=None):
    """Generate a Flask app with embedded HTML dashboard."""
    
    from flask import Flask, render_template_string
    
    if db is None:
        db = load_database()
    
    metrics = calculate_metrics(db)
    
    template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gematria Dashboard - {{ latest_timestamp if latest_timestamp else 'Live' }}</title>
    <style>
        * { box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0d1117; color: #c9d1d9; margin: 0; padding: 20px; line-height: 1.6; }
        .dashboard-header { background: linear-gradient(135deg, #1f6feb 0%, #58a6ff 100%); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; text-align: center; }
        .dashboard-header h1 { margin: 0; font-size: 2em; }
        .dashboard-header p { margin: 5px 0 0; opacity: 0.9; }
        .grid-container { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .card { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 20px; transition: box-shadow 0.3s ease; }
        .card:hover { box-shadow: 0 4px 12px rgba(88, 166, 255, 0.2); }
        .card h2 { margin-top: 0; color: #58a6ff; border-bottom: 1px solid #30363d; padding-bottom: 10px; }
        .stat-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-top: 15px; }
        .stat-item { background: #21262d; padding: 10px; border-radius: 4px; text-align: center; }
        .stat-value { font-size: 1.8em; font-weight: bold; color: #7ee787; }
        .stat-label { font-size: 0.85em; color: #8b949e; }
        .symbol-grid { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px; }
        .symbol-badge { background: linear-gradient(135deg, #238636 0%, #1f6feb 100%); color: white; padding: 5px 12px; border-radius: 15px; font-size: 0.9em; }
        .section-title { color: #7ee787; margin-top: 30px; margin-bottom: 10px; padding-bottom: 5px; border-bottom: 2px solid #238636; }
        .report-link { display: inline-block; background: #1f6feb; color: white; padding: 10px 20px; text-decoration: none; border-radius: 6px; margin: 5px; transition: background 0.2s; }
        .report-link:hover { background: #388bfd; }
        .correlation-table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        .correlation-table th, .correlation-table td { padding: 8px; text-align: left; border-bottom: 1px solid #30363d; font-size: 0.9em; }
        .correlation-table th { color: #7ee787; }
        .timestamp-badge { display: inline-block; background: #238636; color: white; padding: 3px 10px; border-radius: 4px; font-size: 0.85em; }
        @media (max-width: 768px) { .grid-container { grid-template-columns: 1fr; } .stat-grid { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="dashboard-header">
        <h1>GEMATRIA DASHBOARD</h1>
        <p>Real-time Knowledge Graph Analysis | Live Pattern Tracking</p>
        <button onclick="location.reload()" style="background:#238636;color:white;border:none;padding:10px 20px;border-radius:6px;cursor:pointer;font-size:1em;margin-left:20px;">🔄 Refresh Data</button>
    </div>

    <div class="grid-container">
        <div class="card">
            <h2>🔮 Core Symbols</h2>
            <p>Primary symbols currently being tracked:</p>
            <div id="core-symbols" class="symbol-grid"></div>
            <p style="margin-top:10px;font-size:0.9em;color:#8b949e;">These symbols appear consistently across analyzed imagery and events.</p>
        </div>

        <div class="card">
            <h2>📊 System Metrics</h2>
            <div class="stat-grid">
                <div class="stat-item"><div class="stat-value">{{ image_count|default(0) }}</div><div class="stat-label">Images Analyzed</div></div>
                <div class="stat-item"><div class="stat-value">{{ metrics.all_symbols_detected|length if metrics else 0 }}</div><div class="stat-label">Active Symbols</div></div>
            </div>
        </div>

        <div class="card">
            <h2>⏰ Latest Analysis</h2>
            <p><strong>Timestamp:</strong> <span id="latest-timestamp" class="timestamp-badge">{{ latest_timestamp or 'N/A' }}</span></p>
            <p style="font-size:0.9em;color:#8b949e;">Most recent imagery analysis timestamp from the database.</p>
        </div>

        <div class="card">
            <h2>🏛️ Domains Tracked</h2>
            <div id="domains" style="display:flex;flex-wrap:wrap;gap:8px;"></div>
        </div>

        <div class="card">
            <h2>🔥 Elemental Forces</h2>
            <div id="elemental" style="display:flex;flex-wrap:wrap;gap:8px;"></div>
        </div>

        <div class="card">
            <h2>📑 Recent Batch Reports</h2>
            <div id="recent-reports"></div>
        </div>
    </div>

    <div class="section-title">Symbol Correlations</div>
    <div class="card">
        <p>Correlation strength between core symbols across contexts:</p>
        <table class="correlation-table"><thead><tr><th>Symbol</th><th>Occurrences</th><th>Contexts</th></tr></thead><tbody id="correlation-tbody"></tbody></table>
    </div>

    <div class="section-title">Generated Reports</div>
    <div class="card" style="text-align:center;">
        <p>Click to view detailed reports:</p>
        <div id="report-links"></div>
    </div>

    <script>
        // Dashboard data injection
        window.gematriaData = {{ metrics|tojson if metrics else '{}'}}
        
        function initDashboard(data) {
            const d = data;
            
            // Core symbols
            const coreContainer = document.getElementById('core-symbols');
            (d.core_symbols || []).slice(0, 6).forEach(symbol => {
                const badge = document.createElement('span');
                badge.className = 'symbol-badge';
                badge.textContent = symbol;
                coreContainer.appendChild(badge);
            });
            
            // System metrics already rendered via Jinja2
            
            // Latest timestamp - formatted
            const tsEl = document.getElementById('latest-timestamp');
            if (d.latest_timestamp) {
                try {
                    const date = new Date(d.latest_timestamp.replace('Z', ''));
                    tsEl.textContent = date.toLocaleString('en-US', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
                } catch(e) {}
            }
            
            // Domains
            const domainContainer = document.getElementById('domains');
            (d.domains_tracked || []).slice(0, 5).forEach(domain => {
                const badge = document.createElement('span');
                badge.className = 'symbol-badge';
                badge.textContent = domain;
                domainContainer.appendChild(badge);
            });
            
            // Elemental forces
            const elementalContainer = document.getElementById('elemental');
            (d.elemental_forces || []).forEach(force => {
                const badge = document.createElement('span');
                badge.className = 'symbol-badge';
                badge.textContent = force;
                elementalContainer.appendChild(badge);
            });
            
            // Recent reports
            const reportsContainer = document.getElementById('recent-reports');
            (d.batch_reports || []).forEach(report => {
                const link = document.createElement('a');
                link.href = `report/${encodeURIComponent(report)}`.replace(' ', '%20').replace(/(\.md)/, '');
                link.textContent = report;
                link.className = 'report-link';
                reportsContainer.appendChild(link);
            });
            
            // Correlation table
            const tbody = document.getElementById('correlation-tbody');
            Object.entries(d.symbol_correlations || {}).forEach(([symbol, data]) => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td><span class="symbol-badge" style="font-weight:600">${symbol}</span></td>
                    <td>${data.occurrences}</td>
                    <td>${data.contexts.join(', ') || '-'}</td>
                `;
                tbody.appendChild(row);
            });
        }
        
        initDashboard(window.gematriaData);
    </script>
</body>
</html>
"""
    
    app = Flask(__name__)
    
    @app.route('/')
    def dashboard():
        latest_timestamp = metrics["latest_timestamp"] if metrics else "Live"
        return render_template_string(
            template,
            metrics=metrics,
            core_symbols=metrics.get("core_symbols", [])[:6],
            all_symbols_detected=metrics.get("all_symbols_detected", []),
            image_count=metrics.get("image_count", 0),
            latest_timestamp=latest_timestamp,
            domains_tracked=metrics.get("domains_tracked", []),
            elemental_forces=metrics.get("elemental_forces", []),
            batch_reports=metrics.get("batch_reports", []),
        )
    
    return app


def main():
    """CLI entry point for standalone HTML report generation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate Gematria HTML visualization report")
    parser.add_argument("--output", "-o", type=str, default="html_report.html",
                       help="Output file path (default: html_report.html)")
    args = parser.parse_args()
    
    db = load_database()
    if not db:
        print("❌ No database found. Please ensure gematria_database.json exists.")
        return 1
    
    metrics = calculate_metrics(db)
    
    # For standalone CLI mode, generate inline HTML
    html_content = generate_html_report(metrics=metrics)
    html_string = str(html_content)
    
    with open(args.output, 'w') as f:
        f.write(html_string)
    
    print(f"✅ Generated HTML report: {args.output}")
    print(f"   Images analyzed: {metrics['image_count']}")
    print(f"   Core symbols: {len(metrics['core_symbols'])}")
    print(f"   Active symbols tracked: {len(metrics.get('all_symbols_detected', []))}")
    
    return 0


if __name__ == "__main__":
    exit(main())
