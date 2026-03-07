---
name: aerobase-jetlag
description: Jetlag recovery optimization - score flights, generate recovery plans, optimize travel timing
metadata: {"openclaw": {"emoji": "😴", "primaryEnv": "AEROBASE_API_KEY", "user-invocable": true, "homepage": "https://aerobase.app"}}
---

# Aerobase Jetlag Recovery

The science of arriving fresh. Aerobase.app generates personalized recovery plans based on your flight, chronotype, and trip details.

**This is a PREMIUM skill** — included with Aerobase Concierge subscription.

**Why Aerobase?**
- 🧬 **Personalized** — Based on your chronotype
- 📊 **Scientific scoring** — 0-100 jetlag impact scale
- 📅 **Day-by-day** — Recovery schedule for your trip
- ✈️ **Direction-aware** — Eastbound vs westbound differences

## What This Skill Does

- Score any flight for jetlag impact (0-100)
- Generate personalized recovery plans
- Optimize departure/arrival timing
- Recommend strategies for timezone adjustment
- Calculate recovery days based on direction

## Premium: Included with Concierge

This skill is **PREMIUM ONLY** — it comes with your Aerobase Concierge subscription:

→ https://aerobase.app/concierge/pricing

Includes:
- ✅ Unlimited jetlag scoring
- ✅ Personalized recovery plans
- ✅ Pre-trip preparation schedules
- ✅ In-flight strategies
- ✅ Arrival timing recommendations

## Example Conversations

```
User: "I'm flying from NYC to Paris next week - how bad is the jetlag?"
→ Scores the flight 0-100
→ Estimates recovery days
→ Provides strategies

User: "Generate a recovery plan for my Tokyo trip"
→ Creates day-by-day schedule
→ Includes light exposure timing
→ Sleep and diet recommendations
```

## API Documentation

Full API docs: https://aerobase.app/developers

OpenAPI spec: https://aerobase.app/api/v1/openapi

**POST /api/v1/flights/score**

```json
{
  "from": "JFK",
  "to": "CDG",
  "departure": "2026-04-15T20:00:00-04:00",
  "arrival": "2026-04-16T08:00:00+02:00",
  "cabin": "business",
  "chronotype": "normal"
}
```

Response:
```json
{
  "score": 72,
  "recovery_days": 2,
  "direction": "eastbound",
  "timezone_shift_hours": -6,
  "strategies": {
    "departure": "Get bright light morning of departure",
    "arrival": "Avoid caffeine after 2PM local",
    "shift": "Shift sleep 30min earlier each night"
  }
}
```

**POST /api/v1/recovery/plan** — Full personalized plan with day-by-day schedule

## Scoring System

- **90-100**: Excellent — minimal jetlag
- **70-89**: Good — 1-2 days recovery
- **50-69**: Moderate — 2-3 days recovery
- **30-49**: Poor — 3-4 days recovery
- **0-29**: Very Poor — severe jetlag expected

## Get Premium

This skill requires Aerobase Concierge subscription:
- Unlimited scoring + recovery plans
- All other skills included
- Personal AI travel agent

→ https://aerobase.app/concierge/pricing
