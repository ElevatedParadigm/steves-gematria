#!/bin/bash
cd /home/avalonas/.hermes/gematria
python scripts/orchestrator.py --mode overnight 2>&1 | tee cron_logs/overnight_$(date +\%Y\%m\%d).log
