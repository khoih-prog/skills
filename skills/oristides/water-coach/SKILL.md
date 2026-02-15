---
name: water-coach
description: "Hydration tracking and coaching skill. Use when user wants to track water intake, get reminders to drink water, log body metrics (weight, body fat, muscle %, water %), or get analytics on hydration habits. Triggers on: water, hydration, drink more water, body metrics, weight tracking, water goal"
---

# Water Coach v1.2

## Quick Start

This skill helps track daily water intake and provides adaptive reminders based on progress.

## First Run (One-Time Setup)

### Quick Start Flow
Don't ask everything at once. Ask minimal questions:

1. **First:** "What's your weight?" → Calculate goal, start tracking immediately
2. **Later (optional):** Ask height, body metrics, preferences gradually

### Config File
Create at `memory/water_config.json`:
```json
{
  "version": "1.2",
  "units": {
    "system": "metric",
    "weight": "kg",
    "height": "m",
    "volume": "ml"
  },
  "user": {
    "weight_kg": null,
    "height_m": null,
    "body_fat_pct": null,
    "muscle_pct": null,
    "water_pct": null
  },
  "settings": {
    "goal_multiplier": 35,
    "default_goal_ml": null,
    "cutoff_hour": 22,
    "reminder_slots": [
      {"name": "morning", "hour": 9, "default_ml": 500},
      {"name": "lunch", "hour": 12, "default_ml": 500},
      {"name": "afternoon", "hour": 15, "default_ml": 500},
      {"name": "predinner", "hour": 18, "default_ml": 500},
      {"name": "evening", "hour": 21, "default_ml": 500}
    ]
  },
  "status": {
    "snoozed_until": null,
    "skip_dates": []
  },
  "reports": {
    "weekly_enabled": false,
    "monthly_enabled": false
  }
}
```

### 2. Unit Detection & Conversion
```python
# Auto-detect from user input (first time)
KG_TO_LB = 2.20462
LB_TO_KG = 0.453592
ML_TO_OZ = 0.033814
OZ_TO_ML = 29.5735
M_TO_FT = 3.28084
FT_TO_M = 0.3048
CM_TO_M = 0.01

# Detect weight unit
def detect_weight(s):
    s = s.lower().strip()
    if 'lb' in s or 'pound' in s: return 'lb', extract_number(s)
    if 'kg' in s or 'kilo' in s: return 'kg', extract_number(s)
    # Number only - assume metric for now
    return 'kg', float(s)

# Detect height unit  
def detect_height(s):
    s = s.lower().strip()
    if "'" in s or '"' in s: return 'ft', parse_feet_inches(s)
    if 'cm' in s: return 'cm', extract_number(s)
    if 'm' in s: return 'm', extract_number(s)
    return 'm', float(s)  # assume meters

# Store detected system for future use
config['units']['system'] = 'imperial' if detected == 'lb' else 'metric'
```

### 3. Scripts (Create in memory/ or skills/water-coach/scripts/)

**calc_daily_goal.py** - Calculate goal from weight:
```python
#!/usr/bin/env python3
import json, os
CONFIG = 'memory/water_config.json'
def get_goal():
    with open(CONFIG) as f:
        w = json.load(f)['user']['weight_kg']
    return w * 35 if w else None
```

**log_water.py** - Log water intake to CSV:
```python
#!/usr/bin/env python3
import csv, json, sys, os
from datetime import datetime, date
CONFIG, LOG = 'memory/water_config.json', 'memory/water_log.csv'
# Reads config, calculates cumulative, appends to CSV
```

**log_body_metrics.py** - Log body metrics:
```python
#!/usr/bin/env python3
import csv, json, sys, os
from datetime import datetime, date
CONFIG, BODY = 'memory/water_config.json', 'memory/body_metrics.csv'
# Updates config + logs to body_metrics.csv
```

**weekly_report.py** / **monthly_report.py** - Analytics:
```python
#!/usr/bin/env python3
import csv, json, os
from datetime import datetime, date, timedelta
# Reads water_log.csv, calculates stats, returns report
```

## Configuration (First Run)

On first use, ask user for:

1. **Weight** (required): 
   - Let user type however they want ("95kg", "210 lbs", "95", etc.)
   - **Detect unit from input:**
     - Contains "kg" or "kilos" → metric
     - Contains "lb", "lbs", "pounds" → imperial
     - Number only: assume metric if user has history of metric, otherwise ask
   - Convert to kg internally

2. **Height** (optional):
   - User may say "1.75m", "5'9"", "175cm", etc.
   - Detect and convert to meters internally

3. **Body fat %** (optional): Percentage
4. **Muscle %** (optional): Percentage
5. **Water %** (optional): Percentage

**Auto-detect examples:**
| User says | Detected | Stored |
|-----------|----------|--------|
| "95 kg" | metric | 95 kg |
| "210 lbs" | imperial | 95.25 kg |
| "1.75m" | metric | 1.75 m |
| "5'9"" | imperial | 1.75 m |
| "175cm" | metric | 1.75 m |

**Remember:** Once detected, use that system for all future communications with this user.

## Daily Tracking

### Reminder Slots (Base Schedule)
| Slot | Time | Default |
|------|------|---------|
| Morning | 09:00 | 500ml |
| Lunch | 12:00 | 500ml |
| Afternoon | 15:00 | 500ml |
| Pre-dinner | 18:00 | 500ml |
| Evening | 21:00 | 500ml |

### User Response Format
- `yes 500` → drank 500ml (metric)
- `yes 500ml` → drank 500ml
- `yes 16oz` → drank ~473ml (imperial)
- `yes 16` → drank based on user's preferred unit
- `no` → didn't drink
- `later` → remind again in 15-20 min

### User Input Parsing
Parse user input to detect units:
- Numbers only → use preferred unit from config
- "500ml" / "500" → ml (metric)
- "16oz" / "16 oz" → oz (imperial)
- "2L" / "2 liters" → convert to ml
- "8 glasses" → estimate ~500ml per glass

### Adaptive Logic
- Behind schedule (<50%): Add extra slots
- Ahead of schedule: Reduce triggers
- Cutoff: No reminders after 22:00

## Natural Language Intent Detection

Parse user messages to infer intent - don't expect exact commands.

### Skip Days / Rest Day

**User might say:**
- "taking a rest day"
- "won't track today"
- "sick today"
- "traveling"
- "not drinking water today"
- "skip today"
- "taking a few days off"
- "away this weekend"

**Action:** Mark date as skipped in `status.skip_dates`. Don't count against streak.

**Response:** "Got it! Rest up 💙 Skipped [date]"

### Adjust Goal (Temporary or Permanent)

**User might say:**
- "feeling bloated, less water today"
- "intense workout, need more water"
- "lighter day, 2L is enough"
- "can I lower my goal?"
- "increase goal tomorrow"

**Action:** 
- If temporary: Set `status.temp_goal_ml` for specific date
- If permanent: Update `settings.default_goal_ml`

**Response:** "Got it! [date] goal adjusted to X ml"

### Snooze (Pause Reminders)

**User might say:**
- "going on vacation"
- "busy week ahead"
- "don't disturb me"
- "snooze for X days"
- "pause reminders"

**Action:** Set `status.snoozed_until` date. Skip all reminders until then.

**Response:** "Enjoy! Reminders snoozed until [date]. Say 'I'm back' to resume."

### Resume (End Snooze)

**User might say:**
- "I'm back"
- "ready to track again"
- "resume"
- "stop snooze"
- "back to normal"

**Action:** Clear `status.snoozed_until`. Resume normal reminders.

**Response:** "Welcome back! 💧 Starting tracking again"

### Edge Cases
- At 22:00 cutoff → auto-log 0ml for missed slots
- Retroactive: "I drank 2L today" → log 2000ml for today
- Past day: "yesterday I drank 2L" → log for yesterday

## CSV Format

**water_log.csv:**
```
timestamp,date,slot,answer,ml_drank,cumulative_ml,daily_goal,goal_pct
```

**body_metrics.csv:**
```
date,weight_kg,height_m,bmi,body_fat_pct,muscle_pct,water_pct
```

## Natural Language Commands

No exact commands needed - infer intent from natural text:

**Start tracking:**
- "start water tracking"
- "track my water"
- "help me drink more water"

**Log water:**
- "drank 500ml"
- "had 2 liters"
- "yes 500"
- "I drank 2L today"

**Skip / Rest day:**
- "sick today"
- "taking a rest day"
- "skip today"

**Adjust goal:**
- "less water today"
- "need more water"
- "intense workout"

**Snooze:**
- "going on vacation"
- "don't disturb me"
- "pause reminders"

**Resume:**
- "I'm back"
- "resume tracking"
- "stop snooze"

**Reports:**
- "water report"
- "how did I do this week"
- "monthly stats"
