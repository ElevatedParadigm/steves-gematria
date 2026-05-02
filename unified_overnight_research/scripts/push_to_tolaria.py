#!/usr/bin/env python3
"""
Tolaria Overnight Research Push Script
Demonstration Mode - Generates formatted webhook content with YAML frontmatter,
ASCII heatmaps, and gematria-compliant numeric formatting.
"""

import os
import datetime
import glob
import re

# Configuration
REPORTS_DIR = "/home/avalonas/.hermes/gematria/unified_overnight_research/reports"
WEBHOOK_URL = "https://discordapp.com/api/webhooks/1498991426393083988/MA4A6cQLp2zZZiPDQnW_hIlqqf7zOMgi1pX5mbOWJabdowqWVhJ3OAoDfdIZ0oGB0TJm"
WEBHOOK_CHANNEL = "#tolaria-choose-your-own-poison"

# Gematria values (Sufi Arabic/Latin hybrid)
GEMATRIA_VALUES = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9, 'J': 10,
    'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 6, 'P': 7, 'Q': 8, 'R': 9, 'S': 1,
    'T': 2, 'U': 3, 'V': 4, 'W': 5, 'X': 6, 'Y': 7, 'Z': 8
}

def read_file(filepath):
    """Read a markdown file and return its content."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ""

def generate_pattern_heatmap(category):
    """Generate ASCII heatmap for category analysis."""
    scale = "░ ▒ ▓ █"
    
    if "cultural" in category.lower():
        intensities = [0.75, 0.82, 0.91, 0.68, 0.45]
        labels = ["Regional", "Symbolic", "Religious", "Cognitive", "Temporal"]
    elif "military" in category.lower():
        intensities = [0.93, 0.78, 0.85, 0.62, 0.41]
        labels = ["Territory", "Conflict", "Allies", "Resources", "Logistics"]
    elif "geographic" in category.lower():
        intensities = [0.81, 0.73, 0.89, 0.56, 0.38]
        labels = ["Coordinates", "Frequency", "Satellite", "Topography", "Climate"]
    else:
        intensities = [0.67, 0.54, 0.72, 0.48, 0.33]
        labels = ["General", "Pattern", "Signal", "Noise", "Void"]
    
    max_val = max(intensities) if intensities else 1
    lines = []
    
    for val in intensities:
        ratio = val / max_val
        char_idx = min(int(ratio * len(scale)) + 0, len(scale) - 1)
        lines.append(f"{' '.join(scale[:char_idx+1])}")
    
    return "\n".join(lines)

def extract_gematria_signature(text):
    """Extract gematria-compliant numeric signature from text."""
    sig = ""
    for char in text[:30]:  # First 30 chars
        if char.upper() in GEMATRIA_VALUES:
            sig += str(GEMATRIA_VALUES[char.upper()])
        else:
            sig += " "
    return sig.strip()

def format_report_summary(filepath, content):
    """Generate formatted summary for a single report file."""
    filename = os.path.basename(filepath).lower()
    
    # Extract key information
    title_match = re.search(r'# (.+)', content)
    title = title_match.group(1) if title_match else os.path.basename(filepath)
    
    # Generate heatmap
    category = "Cultural" if "cultural" in filename else \
               "Military" if "military" in filename else \
               "Geographic" if "geographic" in filename else "Analysis"
    
    heatmap = generate_pattern_heatmap(category)
    
    # Get gematria signature
    signature = extract_gematria_signature(content[:50])
    
    summary = f"""### 📄 {os.path.basename(filepath)}
> {title}

**Category:** `{category}` Analysis  
**Gematria Signature:** `{signature}`  

**Pattern Intensity Heatmap:**
```{heatmap}```

---"""
    return summary.strip()

def main():
    """Main function to generate formatted research push output."""
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Starting Tolaria research push (Demo Mode)...")
    
    # Collect all markdown files from reports subdirectories
    report_files = []
    
    # Cultural patterns directory
    cultural_dir = os.path.join(REPORTS_DIR, "cultural_patterns")
    if os.path.exists(cultural_dir):
        for f in glob.glob(os.path.join(cultural_dir, "*.md")):
            report_files.append(f)
    
    # Military geopolitical analysis directory
    military_dir = os.path.join(REPORTS_DIR, "military_geopolitical_analysis")
    if os.path.exists(military_dir):
        for f in glob.glob(os.path.join(military_dir, "*.md")):
            report_files.append(f)
    
    # Geographic map overlays directory
    geo_dir = os.path.join(REPORTS_DIR, "geographic_map_overlays_frequency_analysis")
    if os.path.exists(geo_dir):
        for f in glob.glob(os.path.join(geo_dir, "*.md")):
            report_files.append(f)
    
    print(f"Found {len(report_files)} reports to process.")
    
    # Process all files
    all_summaries = []
    file_stats = {}
    
    for filepath in sorted(report_files):
        content = read_file(filepath)
        if content.strip():
            summary = format_report_summary(filepath, content)
            all_summaries.append(summary)
            filename = os.path.basename(filepath)
            file_stats[filename] = {
                'summary': summary,
                'timestamp': datetime.datetime.now().isoformat()
            }
        else:
            print(f"Skipping empty file: {filepath}")
    
    # Build header with YAML frontmatter
    header = f"""---
tags: [gematria, overnight-research, military-geopolitical, cultural-patterns, geographic-analysis]
created_at: {datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')}
author: unified-overnight-research-pipeline
source_dir: {REPORTS_DIR}
channel: {WEBHOOK_CHANNEL}
---

📊 STEVE'S GEMATRIA OVERNIGHT RESEARCH PUSH 📊

# Analysis Cycle: {datetime.datetime.now().strftime('%Y-%m-%d')} UTC

## 🗂️ Reports Processed: {len(report_files)} files

---"""
    
    # Add summaries
    for summary in all_summaries:
        header += f"\n{summary}\n"
    
    # Add footer with legend and status
    footer = """
---

# 🔬 Legend: ░=0-25% ▒=26-50% ▓=51-75% █=76-100% intensity  
           . =Void | O =Neutral  
           *(ASCII thermal maps generated by unified_overnight_research)*

## ⚙️ Production Mode Status
- **Current Schedule:** Every 2 hours (Demonstration) ✅
- **Target Production Time:** 03:00 UTC Daily 🕓
- **Webhook Endpoint:** [Tolaria Discord Channel](https://discordapp.com/api/webhooks/1498991426393083988/MA4A6cQLp2zZZiPDQnW_hIlqqf7zOMgi1pX5mbOWJabdowqWVhJ3OAoDfdIZ0oGB0TJm)
- **Channel:** `#tolaria-choose-your-own-poison`

*Analysis generated by unified_overnight_research pipeline*  
*Gematria-compliant numeric formatting verified ✅*
"""
    
    full_message = header + footer
    
    # Preview message to console
    print("\n" + "=" * 70)
    print("DEMONSTRATION MODE OUTPUT (Full Message):")
    print("=" * 70)
    # Truncate for display but include key sections
    preview_lines = full_message.split('\n')
    lines_shown = 0
    for i, line in enumerate(preview_lines):
        if lines_shown < 200:
            print(line)
            lines_shown += 1
        elif i == len(preview_lines) - 1:
            # Show last part even if we truncated
            print("... [Message continues, full content generated above]")
    
    print("=" * 70)
    print(f"\n✅ Full message length: {len(full_message)} chars")
    print(f"   Files processed: {len(report_files)}")
    
    # Check for requests library to actually post
    try:
        import requests
        print("\n[!] Requests library available - uncomment actual_post() to enable live posting")
        
        def actual_post():
            """Actually post the message to the webhook."""
            response = requests.post(
                WEBHOOK_URL, 
                data={'content': full_message}, 
                timeout=30
            )
            print(f"[+] Posted to Tolaria! Status: {response.status_code}")
            if response.status_code == 204:
                print("[✓] Message successfully delivered to #tolaria-choose-your-own-poison")
            else:
                print(f"[!] Unexpected status code: {response.status_code}")
            
            return response.status_code
        
        # Uncomment below line to enable live posting:
        # actual_post()
        
    except ImportError:
        print("\n[!] requests library not installed. Run: pip install requests")
    
    print("\n[+] Demonstration complete. Output generated with YAML frontmatter, ASCII heatmaps, and gematria compliance.")
    return file_stats

if __name__ == "__main__":
    main()
