---
name: bamboohr
description: "BambooHR — manage employees, time-off, reports, and company info via REST API"
homepage: https://www.agxntsix.ai
license: MIT
compatibility: Python 3.10+ (stdlib only — no dependencies)
metadata: {"openclaw": {"emoji": "🎋", "requires": {"env": ["BAMBOOHR_API_KEY", "BAMBOOHR_SUBDOMAIN"]}, "primaryEnv": "BAMBOOHR_API_KEY", "homepage": "https://www.agxntsix.ai"}}
---

# 🎋 BambooHR

BambooHR — manage employees, time-off, reports, and company info via REST API

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `BAMBOOHR_API_KEY` | ✅ | API key |
| `BAMBOOHR_SUBDOMAIN` | ✅ | Company subdomain |

## Quick Start

```bash
# List employees
python3 {{baseDir}}/scripts/bamboohr.py employees

# Get employee
python3 {{baseDir}}/scripts/bamboohr.py employee-get id <value> --fields <value>

# Create employee
python3 {{baseDir}}/scripts/bamboohr.py employee-create --firstName <value> --lastName <value> --workEmail <value>

# Update employee
python3 {{baseDir}}/scripts/bamboohr.py employee-update id <value> --fields <value>

# List employee files
python3 {{baseDir}}/scripts/bamboohr.py employee-files id <value>

# List time-off requests
python3 {{baseDir}}/scripts/bamboohr.py time-off-requests --start <value> --end <value> --status <value>

# List time-off types
python3 {{baseDir}}/scripts/bamboohr.py time-off-types

# Who is out
python3 {{baseDir}}/scripts/bamboohr.py whois-out --start <value> --end <value>
```

## All Commands

| Command | Description |
|---------|-------------|
| `employees` | List employees |
| `employee-get` | Get employee |
| `employee-create` | Create employee |
| `employee-update` | Update employee |
| `employee-files` | List employee files |
| `time-off-requests` | List time-off requests |
| `time-off-types` | List time-off types |
| `whois-out` | Who is out |
| `reports` | Run report |
| `fields` | List fields |
| `tables` | List tables |
| `table-get` | Get table data |
| `changed` | Changed employees |

## Output Format

All commands output JSON by default. Add `--human` for readable formatted output.

```bash
python3 {{baseDir}}/scripts/bamboohr.py <command> --human
```

## Script Reference

| Script | Description |
|--------|-------------|
| `{{baseDir}}/scripts/bamboohr.py` | Main CLI — all commands in one tool |

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
