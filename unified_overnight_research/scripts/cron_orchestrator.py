#!/usr/bin/env python3
"""
Cron Orchestrator - Gematria Research Automation

This script uses the built-in cronjob tool to manage scheduled research jobs,
including overnight analysis, symbol discovery cycles, and domain monitoring.

Usage:
    python cron_orchestrator.py --list          # List all cron jobs
    python cron_orchestrator.py --pause-all     # Pause all research jobs
    python cron_orchestrator.py --resume-all    # Resume all research jobs
    python cron_orchestrator.py --create-job ...  # Create new scheduled job

Cron Job Types:
- Overnight Symbol Analysis
- Domain Monitoring (Epstein files, news feeds, etc.)
- Weekly Research Syncs
- Tolaria Webhook Pushes
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Hermes Agent tools
from hermes_tools import cronjob, terminal


def list_active_research_jobs() -> list:
    """List all research-related cron jobs."""
    
    print("📋 Research Cron Jobs:")
    print("=" * 70)
    
    result = cronjob(action="list")
    
    for job in result.get("jobs", []):
        name = job.get("name", "Unknown")
        enabled = "✅" if job.get("enabled") else "❌"
        schedule = job.get("schedule", "manual")
        next_run = job.get("next_run_at", "N/A")
        
        print(f"\n  [{enabled}] {name}")
        print(f"      Schedule: {schedule}")
        print(f"      Next Run: {next_run[:20]}...")
        
        if job.get("skill"):
            skill = job.get("skill", "")
            tools = ", ".join(job.get("enabled_toolsets", []))
            print(f"      Skill: {skill}")
            print(f"      Tools: {tools}")
    
    return result


def pause_all_research_jobs():
    """Pause all active research cron jobs."""
    
    print("🛑 Pausing all research cron jobs...")
    result = cronjob(action="list")
    
    paused_count = 0
    
    for job in result.get("jobs", []):
        if job.get("enabled"):
            # Skip system-essential jobs (check by name pattern)
            job_name = job.get("name", "")
            
            # Identify research-related jobs to pause
            if any(pattern in job_name.lower() 
                   for pattern in ["overnight", "research", "analysis", 
                                  "gematria", "discovery", "monitor"]):
                
                job_id = job.get("job_id")
                name = job.get("name")
                
                print(f"   Pausing: {name} (ID: {job_id[:8]}...)")
                
                pause_result = cronjob(action="pause", job_id=job_id)
                
                if pause_result.get("success"):
                    paused_count += 1
    
    print(f"\n✅ Paused {paused_count} research jobs!")
    
    return result


def resume_all_research_jobs():
    """Resume previously paused research cron jobs."""
    
    print("▶️  Resuming all research cron jobs...")
    result = cronjob(action="list")
    
    resumed_count = 0
    
    for job in result.get("jobs", []):
        if not job.get("enabled"):
            # Skip system-essential jobs
            job_name = job.get("name", "")
            
            # Identify research-related jobs to resume
            if any(pattern in job_name.lower() 
                   for pattern in ["overnight", "research", "analysis", 
                                  "gematria", "discovery", "monitor"]):
                
                job_id = job.get("job_id")
                name = job.get("name")
                
                print(f"   Resuming: {name} (ID: {job_id[:8]}...)")
                
                resume_result = cronjob(action="resume", job_id=job_id)
                
                if resume_result.get("success"):
                    resumed_count += 1
    
    print(f"\n✅ Resumed {resumed_count} research jobs!")
    
    return result


def create_overnight_research_job(schedule: str = "0 2 * * *", 
                                   domains: list = None,
                                   symbol_list: list = None) -> dict:
    """
    Create an overnight research analysis job.
    
    Args:
        schedule: Cron schedule (default: daily at 2am)
        domains: List of domains to monitor
        symbol_list: List of symbols to analyze
    
    Returns:
        Job creation result
    """
    
    if not domains:
        domains = ["Mathematics", "Molecular Biology", "Astronomy",
                   "Geography", "Physics", "Chemistry"]
    
    prompt = f"""Overnight Research Analysis for Domains: {', '.join(domains)}

## Schedule Configuration:
Run overnight to avoid interrupting research sessions.
Default schedule: Daily at 2:00 AM ({schedule})

## Analysis Requirements:

1. **Domain Monitoring**: Monitor news feeds, research databases, and repositories
   in the specified domains for new developments.

2. **Symbol Pattern Detection**: Look for emerging patterns related to 
   recently analyzed symbols (from recent cycles).

3. **Cross-Domain Correlations**: Identify connections between domains that 
   may indicate threshold phenomena or bridge structures.

4. **Report Generation**: Create summary reports of overnight findings,
   including:
   - New pattern detections
   - Domain overlap discoveries
   - Potential new symbol candidates
   
5. **Database Updates**: Update research database with new findings and
   correlation insights.

## Deliver Output To: telegram (or configured webhook)

## Notes:
- This is an overnight job - avoid aggressive scraping that could
  trigger rate limits or CAPTCHAs.
- Focus on high-signal sources: academic papers, official filings, 
  verified research databases.
- Report only significant findings (>3 patterns per domain).
"""
    
    # Use terminal to run cronjob create command
    cmd = f"hermes cronjob create --prompt {prompt.replace('\"', '\\\\')} --schedule {schedule} --name 'Overnight Research Analysis - {', '.join(domains)}'"
    
    print(f"📅 Creating overnight research job...")
    print(f"   Schedule: {schedule}")
    print(f"   Domains: {', '.join(domains)}")
    print(f"\nCommand: {cmd[:100]}...")
    
    # Execute cron creation (this would use Hermes CLI)
    try:
        result = terminal(command=cmd, timeout=60)
        
        if result.get("exit_code") == 0:
            print("\n✅ Overnight research job created!")
            return {"success": True, "job_id": result.get("job_id", "unknown")}
        else:
            print(f"\n❌ Job creation failed (exit code {result.get('exit_code')})")
            return {"success": False}
            
    except Exception as e:
        print(f"\n⚠️  Error creating job: {str(e)}")
        return {"success": False, "error": str(e)}


def create_symbol_discovery_cycle_job(cycle_number: int, symbols: list = None,
                                       prompt_template: str = None) -> dict:
    """
    Create a scheduled symbol discovery cycle job.
    
    Args:
        cycle_number: Research cycle number (e.g., 438, 439)
        symbols: List of symbols to analyze in this cycle
        prompt_template: Custom prompt template for the analysis
    
    Returns:
        Job creation result
    """
    
    if not symbols:
        # Default symbols for discovery cycle
        symbols = [666, 111, 963, 55, 279]  # Exclude already analyzed 124
    
    # Build symbol list string for prompt
    symbols_str = ", ".join([str(s) for s in sorted(symbols)])
    
    prompt = f"""Symbol Discovery Cycle #{cycle_number}

## Analysis Symbols:
{symbols_str}

## Research Context:
Analyze these symbols using the Gematria unified overnight research protocol.
Each symbol should be analyzed across primary and secondary domains, with
cross-references to previously analyzed symbols.

## Required Skills/Tools:
- delegate_task (for subagent orchestration)
- web_search / web_extract (for domain research)
- file operations (for report generation)
- terminal (for database updates and visualizations)

## Deliverables:
1. Markdown reports for each symbol (research-cycle-{cycle_number:03d}-{symbol}-report.md)
2. ASCII visualizations and correlation heatmaps
3. Knowledge graph YAML entries
4. Summary report with integration insights

## Schedule Suggestion:
Run overnight or when researcher is not actively working on the project.
Default: Daily at 1:00 AM (avoid interrupting active sessions).

## Notes:
- Use delegate_symbol_analysis.py script for symbol analysis
- Integrate findings into main research database
- Generate ASCII visualizations compatible with terminal/Obsidian
"""
    
    print(f"🔬 Creating symbol discovery cycle #{cycle_number}...")
    print(f"   Symbols: {symbols_str}")
    
    # Execute cron creation
    try:
        result = terminal(command=f"hermes cronjob create --prompt '{prompt[:500]}...' --schedule '0 1 * * *' --name 'Symbol Discovery Cycle #{cycle_number}'", timeout=60)
        
        if result.get("exit_code") == 0:
            print(f"\n✅ Discovery cycle #{cycle_number} job created!")
            return {"success": True, "cycle": cycle_number}
        else:
            print(f"\n❌ Job creation failed")
            return {"success": False}
            
    except Exception as e:
        print(f"\n⚠️  Error creating job: {str(e)}")
        return {"success": False, "error": str(e)}


def create_tolaria_webhook_job(webhook_url: str, schedule: str = "0 3 * * *") -> dict:
    """
    Create a job to push research results to Tolaria webhook.
    
    Args:
        webhook_url: URL of the Tolaria webhook endpoint
        schedule: Cron schedule (default: daily at 3am)
    
    Returns:
        Job creation result
    """
    
    prompt = f"""Push Research Results to Tolaria Webhook

## Webhook Configuration:
URL: {webhook_url}

## Push Schedule:
{schedule} (default: Daily at 3:00 AM)

## What to Push:
1. Recent symbol analysis reports
2. Domain overlap discoveries
3. Pattern correlation summaries
4. Knowledge graph updates

## Format:
- Send markdown-formatted content
- Include file attachments for visualizations (ASCII art, heatmaps)
- Use structured YAML for database entries

## Notes:
- Only push after overnight research jobs complete
- Compress multiple reports into single ZIP if needed
- Track webhook delivery success/failure
"""
    
    print(f"📡 Creating Tolaria webhook push job...")
    print(f"   URL: {webhook_url}")
    print(f"   Schedule: {schedule}")
    
    try:
        result = terminal(command=f"hermes cronjob create --prompt '{prompt[:500]}...' --schedule '{schedule}' --name 'Tolaria Webhook Push'", timeout=60)
        
        if result.get("exit_code") == 0:
            print(f"\n✅ Tolaria webhook job created!")
            return {"success": True}
        else:
            print(f"\n❌ Job creation failed")
            return {"success": False}
            
    except Exception as e:
        print(f"\n⚠️  Error creating job: {str(e)}")
        return {"success": False, "error": str(e)}


def create_weekly_sync_job(sync_days: list = None) -> dict:
    """
    Create weekly synchronization jobs.
    
    Args:
        sync_days: List of days to run (0=Sunday, 6=Saturday). Default: all Sundays.
    
    Returns:
        Job creation result
    """
    
    if not sync_days:
        sync_days = [0]  # Default: Sunday
    
    prompt = f"""Weekly Gematria Repository Sync

## Synchronization Schedule:
Run on days: {', '.join([str(d) for d in sync_days])} at 3:00 AM

## Tasks:
1. Sync with latest image analysis reports (OUR/Vault/Steves gematria/)
2. Update research database with new findings
3. Generate ASCII correlation heatmaps for terminal/Obsidian display
4. Archive weekly analysis summaries
5. Update README documentation

## Deliverables:
- Weekly summary report (markdown)
- Updated knowledge graph entries
- Correlation heatmap visualizations
- Documentation updates

## Notes:
- This is a maintenance job - can run without interrupting research
- Focus on repository health and data freshness
"""
    
    print(f"🔄 Creating weekly sync job...")
    print(f"   Days: {', '.join([str(d) for d in sync_days])}")
    
    try:
        result = terminal(command=f"hermes cronjob create --prompt '{prompt[:500]}...' --schedule '0 3 * {','.join([str(d-1) for d in sync_days])} *' --name 'Weekly Sync'", timeout=60)
        
        if result.get("exit_code") == 0:
            print(f"\n✅ Weekly sync job created!")
            return {"success": True}
        else:
            print(f"\n❌ Job creation failed")
            return {"success": False}
            
    except Exception as e:
        print(f"\n⚠️  Error creating job: {str(e)}")
        return {"success": False, "error": str(e)}


def main():
    """Main entry point for cron orchestrator."""
    
    parser = argparse.ArgumentParser(
        description="Cron Orchestrator for Gematria Research Automation"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # List jobs command
    list_parser = subparsers.add_parser("list", help="List all research cron jobs")
    
    # Pause all jobs command
    pause_parser = subparsers.add_parser("pause-all", help="Pause all research jobs")
    
    # Resume all jobs command  
    resume_parser = subparsers.add_parser("resume-all", help="Resume all research jobs")
    
    # Create overnight analysis job
    overnight_parser = subparsers.add_parser("create-overnight", 
                                              help="Create overnight research job")
    overnight_parser.add_argument("--schedule", default="0 2 * * *",
                                  help="Cron schedule (default: daily at 2am)")
    overnight_parser.add_argument("--domains", nargs="+",
                                  default=["Mathematics", "Molecular Biology", 
                                         "Astronomy"],
                                  help="Domains to monitor")
    
    # Create symbol discovery cycle
    discovery_parser = subparsers.add_parser("create-discovery",
                                             help="Create symbol discovery cycle job")
    discovery_parser.add_argument("--cycle", type=int, required=True,
                                  help="Research cycle number")
    discovery_parser.add_argument("--symbols", nargs="+", default=None,
                                  help="Symbols to analyze (default: 666,111,963,55,279)")
    
    # Create Tolaria webhook job
    webhook_parser = subparsers.add_parser("create-webhook",
                                           help="Create Tolaria webhook push job")
    webhook_parser.add_argument("--url", required=True,
                                help="Webhook URL")
    webhook_parser.add_argument("--schedule", default="0 3 * * *",
                                help="Cron schedule")
    
    # Create weekly sync job
    sync_parser = subparsers.add_parser("create-sync",
                                        help="Create weekly sync job")
    sync_parser.add_argument("--days", nargs="+", type=int, default=[0],
                            help="Days of week (0=Sunday, 6=Saturday)")
    
    args = parser.parse_args()
    
    # Handle commands
    if args.command == "list":
        list_active_research_jobs()
        
    elif args.command == "pause-all":
        pause_all_research_jobs()
        
    elif args.command == "resume-all":
        resume_all_research_jobs()
        
    elif args.command == "create-overnight":
        result = create_overnight_research_job(
            schedule=args.schedule,
            domains=args.domains
        )
        
    elif args.command == "create-discovery":
        symbols = args.symbols or [666, 111, 963, 55, 279]
        result = create_symbol_discovery_cycle_job(
            cycle_number=args.cycle,
            symbols=symbols
        )
        
    elif args.command == "create-webhook":
        result = create_tolaria_webhook_job(webhook_url=args.url)
        
    elif args.command == "create-sync":
        result = create_weekly_sync_job(sync_days=args.days)
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
