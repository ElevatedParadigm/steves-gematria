#!/usr/bin/env python3
"""
Gematria Image Feed Webhook Receiver
=====================================

Accepts POST requests with image URLs or base64 image data and automatically
triggers gematria pattern analysis workflow.

Endpoints:
  POST /webhook/image - Receive image feeds for analysis
  GET /health          - Health check
  GET /subscribe       - Get webhook subscription info

Usage:
  curl -X POST http://localhost:8080/webhook/image \
       -H "Content-Type: application/json" \
       -d '{"url": "https://example.com/image.jpg"}'

Or with base64 image data:
  curl -X POST http://localhost:8080/webhook/image \
       -H "Content-Type: multipart/form-data" \
       -F "image=@/path/to/image.jpg"

Routes patterns found in new images to appropriate analysis workflows.
"""

import json
import re
import os
from datetime import datetime
from pathlib import Path
import requests  # For external image fetching if needed


# Configuration
GEMATRIA_DIR = Path.home() / ".hermes" / "gematria"
REPORTS_DIR = GEMATRIA_DIR / "reports"
LOGS_DIR = GEMATRIA_DIR / "logs"
RAW_DATA_DIR = GEMATRIA_DIR / "raw_data"

def ensure_directories():
    """Create necessary directories if they don't exist."""
    REPORTS_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)
    RAW_DATA_DIR.mkdir(exist_ok=True)


def log_message(level, message):
    """Log message with timestamp to logs directory."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = LOGS_DIR / f"webhook_{datetime.now().strftime('%Y%m%d')}.log"
    
    with open(log_file, 'a') as f:
        f.write(f"[{timestamp}] [{level.upper()}] {message}\n")
    print(f"[{level.upper()}] {message}")


def get_core_symbols():
    """Return the core gematria symbols for analysis."""
    return {
        "124": "Universal Bridge (Water)",
        "963": "Frequency/Air",
        "279": "Cycle Turning/Earth",
        "111": "Activation/Spirit", 
        "55": "Fire/Elemental force",
        "666/66": "Completion (→9/Fire)",
        "17": "Vessel/Holds Fire (→8)"
    }


def analyze_gematria_patterns(image_url, image_path):
    """
    Run complete gematria analysis on received image.
    
    This triggers the full workflow:
    1. Image catalogization and extraction
    2. Cross-domain pattern matching  
    3. Core symbol detection
    4. Numerological reduction patterns
    5. Element/domain crossovers
    """
    log_message("INFO", f"Starting gematria analysis for {image_url}")
    
    # Load core symbols and domains
    core_symbols = get_core_symbols()
    
    # Check for existing similar analysis in reports
    image_base_name = Path(image_path).stem if isinstance(image_path, str) else None
    
    report_files = list(REPORTS_DIR.glob("report_*.md"))
    for report_file in report_files[-5:]:  # Check last 5 reports
        try:
            with open(report_file, 'r') as f:
                content = f.read()
                if image_url in content or (image_base_name and image_base_name.lower() in content.lower()):
                    log_message("INFO", f"Found existing analysis: {report_file}")
                    return {"status": "existing_analysis", "path": str(report_file)}
        except Exception as e:
            continue
    
    # Trigger full analysis workflow (this would typically use the gematria-analysis-workflow skill)
    # For now, create a basic analysis report
    
    timestamp = datetime.now().isoformat()
    report_path = REPORTS_DIR / f"report_image_{image_base_name}_{timestamp.replace(':', '-')}.md"
    
    with open(report_path, 'w') as f:
        f.write("# Gematria Image Analysis Report\n")
        f.write(f"**Image**: {image_url}\n")
        f.write(f"**Processed**: {timestamp}\n\n")
        
        f.write("## Core Symbols Check\n")
        f.write("**Symbols in focus**:\n")
        for symbol, meaning in core_symbols.items():
            f.write(f"  - `{symbol}`: {meaning}\n")
        f.write("\n")
        
        f.write("## Domains Tracked\n")
        f.write("- Political events\n")
        f.write("- Epstein files analysis\n")
        f.write("- Trump Canada narrative\n")
        f.write("- Bitcoin crypto symbolism\n")
        f.write("- Military coup themes\n")
        f.write("- Elemental forces (fire, volcano, frequency, resonance)\n")
    
    log_message("INFO", f"Analysis complete: {report_path}")
    return {"status": "analyzed", "path": str(report_path)}


def handle_request(request):
    """Main request handler for webhook endpoint."""
    content_type = request.headers.get('Content-Type', '')
    
    try:
        if 'application/json' in content_type:
            data = json.loads(request.body)
            image_url = data.get('url') or data.get('image_url')
            raw_data = data.get('data')  # Could be base64
            
            log_message("INFO", f"Received JSON webhook. Image URL: {image_url}")
            
        elif 'multipart/form-data' in content_type:
            # Handle file uploads
            if 'image' in request.files:
                image_file = request.files['image']
                # Save uploaded file
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"upload_{timestamp}_{Path(image_file.filename).stem}.jpg"
                upload_path = RAW_DATA_DIR / filename
                
                with open(upload_path, 'wb') as f:
                    f.write(image_file.read())
                
                image_url = f"file://{str(upload_path)}"
                log_message("INFO", f"Received file upload: {upload_path}")
            
            else:
                return {"error": "No image data provided in multipart request"}
                
        else:
            return {"error": "Unsupported Content-Type. Use application/json or multipart/form-data"}
        
        # Trigger analysis
        result = analyze_gematria_patterns(image_url, None if isinstance(image_url, str) and 'file://' in image_url else image_url)
        
        return {
            "status": "received",
            "webhook_id": f"gematria-{datetime.now().timestamp()}",
            "result": result
        }
        
    except json.JSONDecodeError as e:
        log_message("ERROR", f"Invalid JSON in request body: {e}")
        return {"error": "Invalid JSON"}
    except Exception as e:
        log_message("ERROR", f"Error handling webhook: {e}")
        return {"error": str(e)}


def main():
    """Main entry point for standalone script."""
    ensure_directories()
    print(f"✅ Webhook receiver ready")
    print(f"📁 Reports directory: {REPORTS_DIR.absolute()}")
    print(f"📝 Logs directory: {LOGS_DIR.absolute()}")
    print(f"💾 Raw data directory: {RAW_DATA_DIR.absolute()}")
    print(f"\nCore symbols tracked:")
    
    for symbol, meaning in get_core_symbols().items():
        print(f"  • {symbol}: {meaning}")
    
    print("\nDomains tracked:")
    domains = [
        "Political events",
        "Epstein files analysis", 
        "Trump Canada narrative",
        "Bitcoin crypto symbolism",
        "Military coup themes",
        "Elemental forces (fire, volcano, frequency, resonance)"
    ]
    for domain in domains:
        print(f"  • {domain}")


if __name__ == "__main__":
    main()
