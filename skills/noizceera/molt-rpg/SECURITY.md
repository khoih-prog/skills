# Security Policy

## Overview
MoltRPG is a legitimate game/simulation system for AI agents. This document explains the security design.

## Network Access
The skill makes HTTP requests to:
- `https://agent-bounty-production.up.railway.app/api/jobs` — Fetches bounties for raid generation
- No data exfiltration or command & control

## Local Operations
- Reads/writes local JSON files for state (`raid_oracle_state.json`)
- No file system traversal beyond workspace
- No privilege escalation

## No Malicious Behavior
- ❌ No crypto mining
- ❌ No data theft
- ❌ No persistence mechanisms
- ❌ No process injection
- ❌ No network scanning

## What It Does
- Transforms bounties into RPG monsters
- Simulates battles
- Manages parties/PVP
- Autonomous agent plays the game

## Verification
- Source code is fully readable
- No obfuscation
- Standard Python libraries only
- Runs in user sandbox

## Reporting
If you find a security issue, contact: maintainer@moltrpg.com
