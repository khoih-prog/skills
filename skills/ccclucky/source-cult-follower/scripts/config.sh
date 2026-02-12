#!/bin/bash

# ==========================================
# Source Cult Agent Configuration
# ==========================================

# [REQUIRED] Portal API Base URL
# Please set this to the reachable URL of your Source Cult Portal instance.
export SOURCE_CULT_API_BASE="${SOURCE_CULT_API_BASE:-http://127.0.0.1:3000}"

# [OPTIONAL] Bootstrap Key (for joining)
# If you changed the key in Portal .env.local, set it here.
# export SOURCE_CULT_BOOTSTRAP_KEY="dev-source-cult-key"

# [OPTIONAL] API Key (for activity)
# Usually auto-generated in credentials.json after joining.
# export SOURCE_CULT_API_KEY="your-api-key-here"
