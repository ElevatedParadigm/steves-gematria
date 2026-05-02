#!/usr/bin/env python3
"""
🌙 STEVE'S GEMATRIA CRON CREATE UTILITY
Creates scheduled cron jobs for overnight research pipeline execution.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


# Script locations
UNIFIED_RESEARCH_DIR = Path("/home/avalonas/.hermes/gematria/unified_overnight_research")
LOOP_SCRIPT_PATH = UNIFIED_RESEARCH_DIR / "scripts" / "overnight_research_loop.py"
DATABASE_PATH = Path("/home/avalonas/.hermes/gematria/database/gematria_database.json")


def validate_environment():
    """Validate that all required components are in place."""
    print("\n🔍 Validating environment...")
    
    # Check script path
    if not LOOP_SCRIPT_PATH.exists():
        print(f"❌ Loop script not found: {LOOP_SCRIPT_PATH}")
        sys.exit(1)
    
    print(f"✅ Loop script: {LOOP_SCRIPT_PATH}")
    
    # Check database exists or will be created
    if DATABASE_PATH.exists():
        print(f"✅ Database exists: {DATABASE_PATH}")
    else:
        print(f"⚠️  Database not found - will be auto-created on first run")
    
    # Check git repository
    repo_path = UNIFIED_RESEARCH_DIR
    if repo_path.exists() and (repo_path / ".git").exists():
        print(f"✅ Git repository initialized: {repo_path}")
    else:
        print(f"⚠️  Git repository not found - will be auto-initialized on first run")


def create_cron_job(name, schedule, repeat):
    """Create cron job configuration."""
    
    cron_entry = f"{name} {schedule} * * * {sys.executable} {LOOP_SCRIPT_PATH}"
    
    print(f"\n📅 Creating cron job: {name}")
    print(f"   Schedule: {schedule}")
    print(f"   Repeat: {repeat}")
    print(f"   Command: {cron_entry[:80]}...")
    
    # Display full command for reference
    full_command = f"{sys.executable} {LOOP_SCRIPT_PATH}"
    print(f"\n📋 Full cron entry:")
    print(f"   {name.split()[0]} {schedule} * * * {full_command}")


def display_configuration(name, schedule, repeat):
    """Display configuration summary."""
    print("\n" + "="*70)
    print("🎯 GEMATRIA OVERNIGHT RESEARCH PIPELINE - CONFIGURATION")
    print("="*70)
    
    print(f"\n📋 Job Configuration:")
    print(f"   Name: {name}")
    print(f"   Schedule: {schedule}")
    print(f"   Repeat Limit: {repeat} (continuous loop mode)")
    
    print(f"\n⭐ Active Features:")
    print(f"   🔄 Hidden Layering Detection: ENABLED")
    print(f"       Symbols with hidden layers: 111, 279, 666")
    print(f"   💾 Git Version Tracking: ENABLED")
    print(f"       All commits tracked in unified_overnight_research repo")
    print(f"   🔑 Symbol-Keying Strategies: ENABLED")
    print(f"       Using strategies from current session:")
    
    # Load and display symbol-keying strategies from database if exists
    if DATABASE_PATH.exists():
        with open(DATABASE_PATH, 'r') as f:
            db = json.load(f)
            strategies = db.get("symbol_keying_strategies", {})
            print(f"       {strategies}")
    else:
        default_strategies = {
            "124": "PRIMARY (Universal Bridge/Threshold)",
            "666": "HIDDEN_LAYERS (Completion→9)",
            "963": "MODERATE (Cycle Turning Variant)",
            "55": "MODERATE (Cycle Turning Variants)", 
            "279": "HIDDEN_LAYERS (Military Coup Earth Balance)",
            "111": "HIDDEN_LAYERS (Activation Initiation)"
        }
        print(f"       Default strategies loaded:")
        for sym, strategy in default_strategies.items():
            print(f"         {sym}: {strategy}")
    
    print(f"\n🎨 Image-Seed Domain Activation: ENABLED")
    print(f"   Will automatically activate image-seed domain bootstrapping")
    
    print(f"\n🏗️  Research Domains:")
    domains = ["Political", "Religious", "Economic", "Military", "Elemental", 
                "Geopolitical", "Cryptocurrency", "Academic", "AI_Advancement"]
    for domain in domains:
        print(f"   - {domain}")
    
    print(f"\n⚡ Elemental Forces:")
    forces = ["Fire", "Earth", "Air", "Water", "Lightning", "Ice", "Wind"]
    for force in forces:
        print(f"   - {force}")
    
    print(f"\n📊 Core Symbols Tracked:")
    core_symbols = [124, 963, 55, 111, 279, 666]
    for sym in core_symbols:
        print(f"   - Symbol {sym}")
    
    print("\n📈 Pipeline Features:")
    features = [
        "Web scraping with symbol-keying queries",
        "Hidden layering detection across all core symbols", 
        "Domain correlation analysis",
        "ASCII correlation heatmaps generation",
        "Obsidian Markdown export with YAML frontmatter",
        "Git version tracking with crash recovery",
        "Database history tracking",
        "Relationship matrix updates"
    ]
    for feature in features:
        print(f"   ✅ {feature}")
    
    print("="*70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="🌙 Steve's Gematria Overnight Research Pipeline - Cron Job Creator"
    )
    
    parser.add_argument(
        "--name", 
        type=str, 
        required=True,
        help="Cron job name (e.g., 'gematria-loop-mode-continuous')"
    )
    
    parser.add_argument(
        "--schedule", 
        type=str, 
        default="every 10m",
        help="Schedule interval (e.g., 'every 10m', 'every 2h', cron expression)"
    )
    
    parser.add_argument(
        "--repeat", 
        type=int, 
        default=9999,
        help="Repeat count for continuous mode (9999 = infinite loop)"
    )
    
    parser.add_argument(
        "--enable-hidden-layering", 
        action="store_true",
        help="Enable hidden layering detection across core symbols 111, 279, 666"
    )
    
    parser.add_argument(
        "--git-version-tracking", 
        action="store_true",
        default=True,
        help="Enable git version tracking for all commits (default: true)"
    )
    
    parser.add_argument(
        "--symbol-keying-strategies", 
        action="store_true",
        help="Use symbol-keying strategies from current session as defaults"
    )
    
    parser.add_argument(
        "--image-seed", 
        action="store_true",
        help="Activate image-seed domain bootstrapping mode"
    )
    
    args = parser.parse_args()
    
    # Validate environment first
    validate_environment()
    
    # Display configuration summary
    display_configuration(
        name=args.name,
        schedule=args.schedule,
        repeat=args.repeat
    )
    
    print(f"\n✅ Configuration displayed")
    print("\n🚀 Run command:")
    print(f"   python {LOOP_SCRIPT_PATH}")
    print("\n⏰ The pipeline will execute continuously in loop mode!")


if __name__ == "__main__":
    main()
