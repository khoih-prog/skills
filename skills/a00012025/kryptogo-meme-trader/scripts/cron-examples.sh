#!/usr/bin/env bash
# KryptoGO Meme Trader — OpenClaw Cron Configurations
#
# These are example cron setups for different trading strategies.
# Copy and adapt the commands that match your needs.
#
# Usage: Run individual `openclaw cron add` commands from this file.
#        This script is a reference — do NOT run the whole file at once.

# ============================================================================
# STRATEGY 1: Casual Monitoring (recommended starting point)
# ============================================================================
# Portfolio check every 30 min via heartbeat (already handled by HEARTBEAT.md)
# Daily summary at 9 AM local time

openclaw cron add \
  --cron "0 1 * * *" \
  --name "daily-portfolio-summary" \
  --prompt "Load the kryptogo-meme-trader skill. Call /agent/portfolio with the agent wallet address from .env. Send me a daily summary including: all open positions with current PnL (% and USD), total portfolio value, any positions that hit stop-loss or take-profit thresholds overnight. Format as a clean summary, not raw JSON."

# ============================================================================
# STRATEGY 2: Active Scanner (for users who want more frequent checks)
# ============================================================================
# Scan every 15 minutes for new opportunities

openclaw cron add \
  --every 15m \
  --name "trading-scan-15m" \
  --prompt "Load the kryptogo-meme-trader skill. Execute the full scan workflow:
1. Check portfolio — execute any triggered stop-loss or take-profit.
2. If Pro/Alpha tier: call /signal-dashboard (sort_by=signal_count, page_size=10) for curated accumulation signals. Otherwise: call /agent/trending-tokens with user preferences.
3. Run qualifying tokens through the 7-step analysis pipeline.
4. Execute trades that pass all criteria in autonomous mode.
5. Report ALL actions taken to the user. If nothing happened, stay silent."

# ============================================================================
# STRATEGY 3: Signal-Focused (Pro/Alpha subscribers)
# ============================================================================
# Dedicated signal dashboard monitoring every 10 minutes
# Separate from portfolio monitoring

openclaw cron add \
  --every 10m \
  --name "signal-monitor" \
  --prompt "Load the kryptogo-meme-trader skill. Call /signal-dashboard with sort_by=signal_count and page_size=5. For each token with new accumulation signals in the last 10 minutes, run the full analysis pipeline. If any token passes all criteria, execute the trade and report. Skip tokens already in portfolio."

# Portfolio monitoring every 30 minutes (separate job)
openclaw cron add \
  --every 30m \
  --name "portfolio-monitor" \
  --prompt "Load the kryptogo-meme-trader skill. Check /agent/portfolio. Execute stop-loss and take-profit orders automatically. Report any executed trades."

# ============================================================================
# STRATEGY 4: Conservative (ask before trading)
# ============================================================================
# Scan and analyze, but NEVER auto-trade — always ask first

openclaw cron add \
  --every 30m \
  --name "conservative-scan" \
  --prompt "Load the kryptogo-meme-trader skill. Scan trending tokens and run analysis. Do NOT execute any trades. Instead, if you find tokens that pass the bullish checklist, send me a summary with your recommendation and ask for confirmation before trading."

# ============================================================================
# UTILITY COMMANDS
# ============================================================================

# List all active cron jobs
# openclaw cron list

# Remove a specific cron
# openclaw cron remove trading-scan-15m

# Remove all trading crons
# openclaw cron remove daily-portfolio-summary
# openclaw cron remove trading-scan-15m
# openclaw cron remove signal-monitor
# openclaw cron remove portfolio-monitor
# openclaw cron remove conservative-scan
