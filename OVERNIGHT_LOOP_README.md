# 🌙 Overnight Research Loop System

Complete multi-phase pipeline for Steve's gematria database analysis with auto-restart capability.

## Overview

The overnight research loop runs every 3 hours (at :00 minute of hours 0, 3, 6, 9, 12, 15, 18, 21) and performs:

1. **Stability Test** - Enhanced cross-domain verification
2. **Correlation Heatmaps** - Symbol relationships and matrices
3. **Auto-Sync to Obsidian** - Export analyzed symbols and notes
4. **Elasticity Monitoring** - Multi-phase scheduling with intensity adjustment

## Quick Start

```bash
# Run overnight loop once:
cd /home/avalonas/.hermes/gematria
python3 run_overnight_loop.py

# Run in validation mode only:
python3 run_overnight_loop.py --validate

# Check system status:
python3 status_dashboard.py --check-healthy

# View current dashboard:
python3 status_dashboard.py
```

## Components

### Core Scripts

| Script | Purpose | Location |
|--------|---------|----------|
| `run_overnight_loop.py` | Master loop controller | `/home/avalonas/.hermes/gematria/run_overnight_loop.py` |
| `stability_test_enhanced_fixed.py` | Cross-domain stability checks | `/home/avalonas/.hermes/gematria/scripts/stability_test_enhanced_fixed.py` |
| `auto_obisidian_sync_v2.py` | Obsidian note export | `/home/avalonas/.hermes/gematria/scripts/auto_obisidian_sync_v2.py` |
| `loop_runner.py` | Additional processing | `/home/avalonas/.hermes/gematria/scripts/loop_runner.py` |
| `hybrid_scheduler.py` | Multi-phase elasticity monitoring | `/home/avalonas/.hermes/gematria/hybrid_scheduler.py` |
| `run_master_loop.py` | Alternative master runner | `/home/avalonas/.hermes/gematria/run_master_loop.py` |

### Scheduler Phases

The hybrid scheduler adjusts intensity across time slots:

| Slot (UTC) | Phase Name | Intensity | Operation Type |
|------------|------------|-----------|----------------|
| 00:00 | midnight_slow | 0.5x | Light |
| 03:00 | early_morning_normal | 1.0x | Normal |
| 06:00 | morning_speed_up | 1.5x | Optimized |
| 09:00 | business_start_intensify | 1.8x | Full |
| 12:00 | noon_speed_up | 1.3x | Optimized |
| 15:00 | afternoon_normal | 1.0x | Normal |
| 18:00 | evening_speed_up | 1.4x | Optimized |
| 21:00 | night_wrapup_slow | 0.7x | Light |

## Directory Structure

```
/home/avalonas/.hermes/gematria/
├── database/                    # Symbol and force data
│   ├── symbols.json            # Analyzed gematria symbols
│   └── forces.json             # Elemental force definitions
├── research/
│   └── heatmaps/               # Correlation matrices (generated)
├── obsidian_exports/           # Exported Obsidian notes
│   ├── symbol_*.md            # Individual symbol notes
│   └── relationships_matrix.md # Relationship matrix
├── stability_outputs/          # Stability test results
├── logs/                       # Execution logs
│   ├── overnight_loop.log      # Main loop log
│   ├── hybrid_scheduler.log    # Scheduler monitoring
│   └── errors.log              # Error tracking
├── scripts/                    # Processing scripts
├── hybrid_scheduler_status.json  # Current phase state
├── stability_last_result.json     # Last stability result
└── last_run_status.json         # Component status
```

## Cron Configuration

Add to crontab (`crontab -e`):

```bash
# Run overnight loop every 3 hours at :00
0 0,3,6,9,12,15,18,21 * * * cd /home/avalonas && \
    /usr/bin/python3 /home/avalonas/.hermes/gematria/run_overnight_loop.py >> /home/avalonas/.hermes/gematria/logs/cron_overnight.log 2>&1
```

Or use systemd service (create `/etc/systemd/system/gematria-overnight.service`):

```ini
[Unit]
Description=Overnight Research Loop for Gematria Database
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /home/avalonas/.hermes/gematria/run_overnight_loop.py
WorkingDirectory=/home/avalonas/.hermes/gematria
Restart=on-failure
RestartSec=30

[Install]
WantedBy=multi-user.target
```

Then enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable gematria-overnight.service
sudo systemctl start gematria-overnight.service
```

## Health Check

Run diagnostic checks before starting:

```bash
python3 status_dashboard.py --check-healthy
```

Expected output:
```
✅ HEALTH CHECK PASSED
All components are present and configured correctly.
```

## Auto-Restart on Failure

The system automatically handles failures:

1. **Detection**: Monitors exit codes and error patterns
2. **Logging**: Writes to `logs/errors.log` with timestamps
3. **State Tracking**: Persists `last_run_status.json` for state replay
4. **Retry Logic**: Implements exponential backoff (10s, 30s, 60s)
5. **Continuation**: Proceeds with remaining phases even if one fails

## Monitoring Commands

```bash
# Check last run status:
cat /home/avalonas/.hermes/gematria/last_run_status.json

# View latest loop output:
tail -100 /home/avalonas/.hermes/gematria/logs/overnight_loop.log

# Monitor scheduler phase:
python3 /home/avalonas/.hermes/gematria/hybrid_scheduler.py --status

# Quick health status:
python3 status_dashboard.py --check-healthy

# View all output files:
ls -la /home/avalonas/.hermes/gematria/obsidian_exports/
```

## Usage Examples

### Run Full Pipeline (Production)
```bash
cd /home/avalonas/.hermes/gematria
python3 run_overnight_loop.py --verbose
```

### Validation Mode Only
```bash
python3 run_overnight_loop.py --validate
```

### Check Scheduler Status
```bash
python3 hybrid_scheduler.py --status
```

### View Complete Dashboard
```bash
python3 status_dashboard.py --verbose
```

## Phase Rotation Monitoring

The hybrid scheduler manages phase rotation across timezones:

- **Speed Up Slots** (06:00, 12:00, 18:00): Optimized processing
- **Intensify Slots** (09:00): Full analysis intensity
- **Slow Wrap-up** (00:00, 21:00): Light operations

Status file at: `/home/avalonas/.hermes/gematria/hybrid_scheduler_status.json`

## Troubleshooting

### Stability Test Fails
```bash
# Check last stability result
cat /home/avalonas/.hermes/gematria/stability_outputs/last_stability_result.json

# Run with detailed output
python3 scripts/stability_test_enhanced_fixed.py --verbose
```

### No Files Generated
```bash
# Verify database exists
ls -la database/*.json

# Check permissions
sudo chmod 755 /home/avalonas/.hermes/gematria/obsidian_exports
```

### Auto-Restart Not Working
```bash
# Clear state and restart fresh
rm -f last_run_status.json stability_outputs/*

# Run manual loop
python3 run_overnight_loop.py
```

## Configuration Options

| Option | Description | Example |
|--------|-------------|---------|
| `--validate` | Validation mode only | Check integrity without full sync |
| `--verbose` | Verbose output | Show detailed logs |
| `--phase PHASE_NAME` | Specific phase | `--phase stability_test` |

## Notes

- All scripts are Python 3 compatible
- JSON outputs use UTF-8 encoding
- YAML frontmatter for Obsidian compatibility
- Phase markers enable elasticity monitoring integration
- Auto-restart on failure is automatic and non-blocking

## Support

For issues or questions:
1. Check `logs/overnight_loop.log` for phase details
2. Review `status_dashboard.py --check-healthy` for diagnostics
3. Examine `logs/errors.log` for failures
4. Inspect `research/heatmaps/` and `obsidian_exports/` for outputs

---

**Built for Steve's Gematria Research**
*Multi-phase elasticity monitoring enabled*\
*Auto-restart on failure enabled*\
*Hybrid scheduler integrated*
