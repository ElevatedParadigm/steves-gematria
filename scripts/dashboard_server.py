#!/usr/bin/env python3
"""
Multi-Agent Dashboard System — Steve's Gematria Knowledge Graph
Real-time monitoring of overnight research pipeline, agent status, and pattern correlations.
Serves HTML dashboard at http://localhost:8080 (no sudo required)
"""

from flask import Flask, render_template_string, jsonify, send_file
import os
import json
import yaml
from datetime import datetime
from pathlib import Path

app = Flask(__name__)

# Database paths
DB_PATH = "/home/avalonas/.hermes/gematria/database/gematria_database.json"
OBSIDIAN_EXPORTS = "/home/avalonas/.hermes/gematria/obsidian_exports"
CORN_LOGS = "/home/avalonas/.hermes/gematria/cron_logs"

# Core symbols
CORE_SYMBOLS = [124, 666, 963, 55, 111, 279]

def load_database():
    """Load gematria database and extract key metrics"""
    try:
        with open(DB_PATH, 'r') as f:
            db = json.load(f)
            
        symbols = db.get('symbols', {})
        domains = db.get('domains', {})
        
        # Extract symbol stats
        symbol_stats = {}
        for num, data in symbols.items():
            if isinstance(num, str):
                key = int(num)
            else:
                key = num
            
            relevant_items = len(data.get('relevant_items', []))
            analyzed_count = data.get('analyzed_count', 0)
            
            symbol_stats[key] = {
                'value': num,
                'name': data.get('name', 'Unknown'),
                'symbol_type': data.get('type', 'number'),
                'relevance_score': round(data.get('relevance_score', 0), 3),
                'active_connections': len(data.get('connections', [])),
                'analyzed_images': relevant_items,
                'last_updated': data.get('last_analyzed', 'never')
            }
            
        return {
            'symbols': symbol_stats,
            'domains': domains,
            'core_symbols': CORE_SYMBOLS
        }
    except Exception as e:
        print(f"Database load error: {e}")
        return {'symbols': {}, 'domains': {}, 'core_symbols': CORE_SYMBOLS}

def get_obsidian_files():
    """Get list of obsidian export files and their sizes/modification times"""
    try:
        files = []
        for filename in sorted(os.listdir(OBSIDIAN_EXPORTS)):
            if filename.endswith('.md'):
                filepath = os.path.join(OBSIDIAN_EXPORTS, filename)
                stat = os.stat(filepath)
                files.append({
                    'name': filename,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
                    'path': filepath
                })
        return files
    except Exception as e:
        print(f"Observatory load error: {e}")
        return []

def get_latest_cron_logs():
    """Get latest cron execution logs"""
    try:
        logs = []
        for filename in sorted(os.listdir(CORN_LOGS), reverse=True)[:5]:
            filepath = os.path.join(CORN_LOGS, filename)
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    content = f.read()[:2000]  # First 2KB of log
                stat = os.stat(filepath)
                logs.append({
                    'filename': filename,
                    'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
                    'size': stat.st_size,
                    'preview': content.strip()
                })
        return logs
    except Exception as e:
        print(f"Cron log load error: {e}")
        return []

@app.route('/')
def dashboard():
    """Main dashboard with live stats"""
    db = load_database()
    obsidian_files = get_obsidian_files()
    
    # Calculate total relationships and connections
    total_connections = sum(s.get('active_connections', 0) for s in db['symbols'].values())
    max_relevance = max((s['relevance_score'] for s in db['symbols'].values()), default=0)
    
    return render_template_string(DASHBOARD_TEMPLATE,
        symbols=db['symbols'],
        total_connections=total_connections,
        max_relevance=max_relevance,
        obsidian_files=obsidian_files,
        core_symbols=db['core_symbols']
    )

@app.route('/api/overview')
def api_overview():
    """API endpoint for real-time metrics"""
    db = load_database()
    obsidian_files = get_obsidian_files()
    cron_logs = get_latest_cron_logs()
    
    symbol_names = {k: v.get('name', 'Unknown') for k, v in db['symbols'].items()}
    symbol_stats = [{k: v for k, v in s.items() if k in ['value', 'name', 'type', 'relevance_score', 'active_connections']} 
                     for s in sorted(db['symbols'].values(), key=lambda x: x.get('relevance_score', 0), reverse=True)]
    
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'core_symbols': db['core_symbols'],
        'symbol_stats': symbol_stats,
        'total_connections': sum(s.get('active_connections', 0) for s in db['symbols'].values()),
        'obsidian_files_count': len(obsidian_files),
        'latest_runs': cron_logs[:3]
    })

@app.route('/api/symbols')
def api_symbols():
    """API endpoint for detailed symbol data"""
    db = load_database()
    return jsonify({
        'symbols': {str(k): v for k, v in db['symbols'].items()},
        'core_symbols': db['core_symbols']
    })

@app.route('/api/domains')
def api_domains():
    """API endpoint for domain convergence data"""
    try:
        with open(DB_PATH, 'r') as f:
            db = json.load(f)
        
        domains = db.get('domains', {})
        return jsonify({'domains': {k: v for k, v in domains.items()}})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🌉 STEVE'S GEMATRIA - Multi-Agent Dashboard")
    print("=" * 60)
    print("Dashboard URL: http://localhost:8080")
    print("API endpoint: http://localhost:8080/api/overview")
    print("=" * 60)
    print("\nStarting dashboard server (Ctrl+C to stop)...\n")
    app.run(host='0.0.0.0', port=8080, debug=True)

DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multi-Agent Orchestrator — Steve\'s Gematria Knowledge Graph</title>
    <style>
        :root {
            --bg-primary: #0d1117;
            --bg-secondary: #161b22;
            --accent-blue: #58a6ff;
            --accent-green: #3fb950;
            --accent-purple: #d2a8ff;
            --accent-orange: #f28f49;
            --text-primary: #c9d1d9;
            --border-color: #30363a;
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: \'Segoe UI\', Consolas, Monaco, monospace;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            padding: 20px;
        }
        
        .container { max-width: 1600px; margin: 0 auto; }
        
        header {
            text-align: center;
            padding: 30px 0;
            border-bottom: 2px solid var(--border-color);
            margin-bottom: 30px;
        }
        
        h1 {
            font-size: 2.5rem;
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        
        .subtitle { color: #8b949e; font-size: 1.1rem; }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 20px;
            text-align: center;
        }
        
        .stat-value {
            font-size: 2.5rem;
            font-weight: bold;
            color: var(--accent-blue);
        }
        
        .stat-label { color: #8b949e; font-size: 0.9rem; }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 25px;
        }
        
        .card-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 15px;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 15px;
        }
        
        .card-title {
            font-size: 1.3rem;
            font-weight: 600;
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-orange));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .symbol-list { list-style: none; }
        
        .symbol-item {
            margin-bottom: 12px;
            padding: 15px;
            background: var(--bg-primary);
            border-radius: 6px;
            border-left: 4px solid var(--accent-blue);
        }
        
        .symbol-value { font-weight: bold; color: var(--accent-blue); font-size: 1.2rem; }
        .symbol-name { color: #8b949e; font-size: 0.95rem; margin-top: 4px; }
        .stat-line { display: flex; justify-content: space-between; margin-top: 8px; font-size: 0.85rem; }
        .stat-line span:first-child { color: #8b949e; }
        .stat-line span:last-child { color: var(--accent-green); font-weight: bold; }
        
        .file-list { list-style: none; }
        .file-item {
            margin-bottom: 10px;
            padding: 12px;
            background: var(--bg-primary);
            border-radius: 6px;
            border-left: 4px solid var(--accent-purple);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .file-name { font-family: monospace; font-size: 0.9rem; color: var(--accent-purple); }
        .file-meta { text-align: right; font-size: 0.8rem; color: #8b949e; }
        
        .cron-log-item {
            margin-bottom: 15px;
            padding: 15px;
            background: var(--bg-primary);
            border-radius: 6px;
            border-left: 4px solid var(--accent-green);
        }
        
        .log-meta { font-size: 0.8rem; color: #8b949e; margin-bottom: 10px; display: flex; gap: 20px; }
        .log-preview { font-family: monospace; font-size: 0.85rem; color: #c9d1d9; white-space: pre-wrap; max-height: 100px; overflow-y: auto; }
        
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-active { background-color: var(--accent-green); }
        .status-idle { background-color: #8b949e; }
        
        @media (max-width: 768px) {
            h1 { font-size: 2rem; }
            .stats-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🌉 STEVE\'S GEMATRIA KNOWLEDGE GRAPH</h1>
            <p class="subtitle">Multi-Agent Orchestrator Dashboard — Real-time Pattern Monitoring</p>
            <p style="margin-top: 10px; color: var(--accent-blue);">Core Symbols Tracked: {{ core_symbols | join(", ") }}</p>
        </header>
        
        <!-- Live Stats -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="status-indicator status-active"></div>
                <div class="stat-value">{{ total_connections }}</div>
                <div class="stat-label">Active Connections</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ max_relevance | round(2) }}</div>
                <div class="stat-label">Max Relevance Score</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ obsidian_files | length }}</div>
                <div class="stat-label">Obsidian Export Files</div>
            </div>
        </div>
        
        <!-- Core Symbols -->
        <div class="card">
            <div class="card-header">
                <span style="font-size: 1.8rem;">🔮</span>
                <h2 class="card-title">Core Symbols Status</h2>
            </div>
            <ul class="symbol-list">
                {% for num, data in symbols.items() | sort(attribute='relevance_score', reverse=True) %}
                <li class="symbol-item">
                    <div>{{ data.value }} ({{ data.name }})</div>
                    <div class="symbol-name">{{ data.type }}</div>
                    <div class="stat-line">
                        <span>Relevance Score:</span>
                        <span style="color: var(--accent-blue);">{{ "%.3f"|format(data.relevance_score) }}</span>
                    </div>
                    <div class="stat-line">
                        <span>Active Connections:</span>
                        <span>{{ data.active_connections }}</span>
                    </div>
                    <div class="stat-line">
                        <span>Image Analysis Results:</span>
                        <span style="color: var(--accent-green);">{{ data.analyzed_images }}</span>
                    </div>
                </li>
                {% endfor %}
            </ul>
        </div>
        
        <!-- Obsidian Exports -->
        <div class="card">
            <div class="card-header">
                <span style="font-size: 1.8rem;">📝</span>
                <h2 class="card-title">Obsidian Export Files</h2>
            </div>
            <ul class="file-list">
                {% for file in obsidian_files %}
                <li class="file-item">
                    <span class="file-name">{{ file.name }}</span>
                    <div class="file-meta">
                        {{ "%.1f"|format(file.size / 1024) }}KB | {{ file.modified }}
                    </div>
                </li>
                {% endfor %}
            </ul>
        </div>
        
        <!-- Latest Cron Runs -->
        <div class="card">
            <div class="card-header">
                <span style="font-size: 1.8rem;">⏰</span>
                <h2 class="card-title">Latest Overnight Research Logs</h2>
            </div>
            {% for log in logs | default([]) %}
            <div class="cron-log-item">
                <div class="log-meta">
                    <span><strong>{{ log.filename }}</strong></span>
                    <span>{{ log.modified }}</span>
                    <span>{{ "%.1f"|format(log.size / 1024) }}KB</span>
                </div>
                <div class="log-preview">{{ log.preview }}</div>
            </div>
            {% else %}
            <p style="color: #8b949e; padding: 20px;">No cron execution logs available</p>
            {% endfor %}
        </div>
        
        <!-- API Endpoints -->
        <div class="card">
            <div class="card-header">
                <span style="font-size: 1.8rem;">🔌</span>
                <h2 class="card-title">API Endpoints</h2>
            </div>
            <div style="font-family: monospace; padding: 15px; background: var(--bg-primary); border-radius: 6px;">
                <p style="margin-bottom: 8px;"><span style="color: #8b949e;">GET</span> /<strong>/api/overview</strong> — Real-time metrics and stats</p>
                <p style="margin-bottom: 8px;"><span style="color: #8b949e;">GET</span> /<strong>/api/symbols</strong> — Detailed symbol data</p>
                <p style="margin-bottom: 8px;"><span style="color: #8b949e;">GET</span> /<strong>/api/domains</strong> — Domain convergence analysis</p>
            </div>
        </div>
        
        <footer style="text-align: center; padding: 30px; border-top: 1px solid var(--border-color); color: #8b949e;">
            <p><strong>🌉 STEVE\'S GEMATRIA KNOWLEDGE GRAPH</strong></p>
            <p style="font-size: 0.9rem; margin-top: 8px;">Multi-Agent Architecture | Overnight Research Pipeline | Pattern Correlation Engine</p>
        </footer>
    </div>
</body>
</html>
'''

if __name__ == '__main__':
    # First, ensure logs directory exists
    Path(CORN_LOGS).mkdir(parents=True, exist_ok=True)
    
    print("🌉 STEVE'S GEMATRIA - Multi-Agent Dashboard")
    print("=" * 60)
    print("Dashboard URL: http://localhost:8080")
    print("API endpoint: http://localhost:8080/api/overview")
    print("=" * 60)
    print("\nStarting dashboard server (Ctrl+C to stop)...\n")
    app.run(host='0.0.0.0', port=8080, debug=True)
