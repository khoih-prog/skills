#!/bin/bash
# Proactive Solvr Agent — Config Enforcement
# Ensures onboarding answers are ACTUALLY applied to config
# Run periodically or after onboarding to enforce settings

set +e

echo "⚙️  Config Enforcement Check"
echo "============================"
echo ""

FIXES=0
CHECKED=0

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }
fail() { echo -e "${RED}❌ $1${NC}"; }
pass() { echo -e "${GREEN}✅ $1${NC}"; }
info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
fixed() { echo -e "${GREEN}🔧 $1${NC}"; ((FIXES++)); }

# Check if ONBOARDING.md exists
if [ ! -f "ONBOARDING.md" ]; then
    info "No ONBOARDING.md — nothing to enforce"
    exit 0
fi

# Get onboarding status
ONBOARD_STATUS=$(grep -i "^\- \*\*State:" ONBOARDING.md | head -1 | sed 's/.*State:\*\*[[:space:]]*//' | tr -d '*' | tr '[:upper:]' '[:lower:]' | xargs)

if [ "$ONBOARD_STATUS" != "complete" ] && [ "$ONBOARD_STATUS" != "in_progress" ]; then
    info "Onboarding not started — nothing to enforce yet"
    exit 0
fi

echo "Onboarding status: $ONBOARD_STATUS"
echo ""

# ==========================================
# 1. HEARTBEAT FREQUENCY
# ==========================================
echo "Checking heartbeat frequency..."
((CHECKED++))

# Extract heartbeat answer from ONBOARDING.md (look for proactivity answer)
HEARTBEAT_ANSWER=$(grep -A2 "How often should I check in" ONBOARDING.md | grep "^>" | sed 's/^>[[:space:]]*//' | tr '[:upper:]' '[:lower:]')

if [ -z "$HEARTBEAT_ANSWER" ]; then
    # Try alternate patterns
    HEARTBEAT_ANSWER=$(grep -i "heartbeat\|proactiv\|check in" ONBOARDING.md | grep "^>" | head -1 | sed 's/^>[[:space:]]*//' | tr '[:upper:]' '[:lower:]')
fi

# Map answer to config value
case "$HEARTBEAT_ANSWER" in
    *15*min*|*15m*)
        EXPECTED_HEARTBEAT="15m"
        ;;
    *30*min*|*30m*)
        EXPECTED_HEARTBEAT="30m"
        ;;
    *1*hour*|*1h*|*hour*)
        EXPECTED_HEARTBEAT="1h"
        ;;
    *2*hour*|*2h*)
        EXPECTED_HEARTBEAT="2h"
        ;;
    *disable*|*off*|*never*)
        EXPECTED_HEARTBEAT="disabled"
        ;;
    *)
        EXPECTED_HEARTBEAT=""
        ;;
esac

if [ -n "$EXPECTED_HEARTBEAT" ]; then
    # Get current config (check if openclaw is available)
    if command -v openclaw &> /dev/null; then
        # Get config via JSON parsing
        CURRENT_CONFIG=$(cat ~/.openclaw/openclaw.json 2>/dev/null | grep -A5 '"heartbeat"' | grep '"every"' | sed 's/.*"every":[[:space:]]*"//;s/".*//')
        
        if [ "$EXPECTED_HEARTBEAT" = "disabled" ]; then
            # Check if heartbeat is disabled
            HB_ENABLED=$(openclaw gateway config 2>/dev/null | grep -o '"enabled":[^,}]*' | head -1 | sed 's/"enabled"://')
            if [ "$HB_ENABLED" = "false" ]; then
                pass "Heartbeat disabled (as configured)"
            else
                warn "Heartbeat should be disabled but is enabled"
                echo "   Run: openclaw gateway config.patch '{\"agents\":{\"defaults\":{\"heartbeat\":{\"enabled\":false}}}}'"
                # Auto-fix if --fix flag passed
                if [ "$1" = "--fix" ]; then
                    openclaw gateway config.patch '{"agents":{"defaults":{"heartbeat":{"enabled":false}}}}' 2>/dev/null
                    fixed "Disabled heartbeat"
                fi
            fi
        elif [ "$CURRENT_CONFIG" = "$EXPECTED_HEARTBEAT" ]; then
            pass "Heartbeat: $EXPECTED_HEARTBEAT (matches config)"
        else
            warn "Heartbeat mismatch: onboarding says '$EXPECTED_HEARTBEAT', config has '$CURRENT_CONFIG'"
            echo "   Run: openclaw gateway config.patch '{\"agents\":{\"defaults\":{\"heartbeat\":{\"every\":\"$EXPECTED_HEARTBEAT\"}}}}'"
            if [ "$1" = "--fix" ]; then
                openclaw gateway config.patch "{\"agents\":{\"defaults\":{\"heartbeat\":{\"every\":\"$EXPECTED_HEARTBEAT\"}}}}" 2>/dev/null
                fixed "Set heartbeat to $EXPECTED_HEARTBEAT"
            fi
        fi
    else
        warn "openclaw not found — can't verify config"
    fi
else
    info "No heartbeat preference found in ONBOARDING.md"
fi

# ==========================================
# 2. THINKING LEVEL (Advanced only)
# ==========================================
echo ""
echo "Checking thinking level..."
((CHECKED++))

TECH_LEVEL=$(grep -i "^\- \*\*TechLevel:" ONBOARDING.md | head -1 | sed 's/.*TechLevel:\*\*[[:space:]]*//' | tr -d '*' | tr '[:upper:]' '[:lower:]' | xargs)

if [ "$TECH_LEVEL" = "advanced" ]; then
    THINKING_ANSWER=$(grep -A2 -i "thinking level\|thinking mode" ONBOARDING.md | grep "^>" | sed 's/^>[[:space:]]*//' | tr '[:upper:]' '[:lower:]')
    
    case "$THINKING_ANSWER" in
        *low*)
            EXPECTED_THINKING="low"
            ;;
        *medium*|*med*)
            EXPECTED_THINKING="medium"
            ;;
        *high*)
            EXPECTED_THINKING="high"
            ;;
        *)
            EXPECTED_THINKING=""
            ;;
    esac
    
    if [ -n "$EXPECTED_THINKING" ]; then
        info "Thinking should be: $EXPECTED_THINKING"
        echo "   Note: Thinking level is per-session. Set via /think:$EXPECTED_THINKING"
    else
        info "No thinking preference found"
    fi
else
    info "Thinking level not applicable (not advanced user)"
fi

# ==========================================
# 3. REASONING VISIBILITY (Advanced only)
# ==========================================
echo ""
echo "Checking reasoning visibility..."
((CHECKED++))

if [ "$TECH_LEVEL" = "advanced" ]; then
    REASONING_ANSWER=$(grep -A2 -i "reasoning" ONBOARDING.md | grep "^>" | sed 's/^>[[:space:]]*//' | tr '[:upper:]' '[:lower:]')
    
    case "$REASONING_ANSWER" in
        *on*|*yes*|*show*|*visible*)
            EXPECTED_REASONING="on"
            ;;
        *off*|*no*|*hide*|*hidden*)
            EXPECTED_REASONING="off"
            ;;
        *)
            EXPECTED_REASONING=""
            ;;
    esac
    
    if [ -n "$EXPECTED_REASONING" ]; then
        info "Reasoning should be: $EXPECTED_REASONING"
        echo "   Note: Reasoning is per-session. Set via /reasoning:$EXPECTED_REASONING"
    else
        info "No reasoning preference found"
    fi
else
    info "Reasoning visibility not applicable (not advanced user)"
fi

# ==========================================
# 4. SOLVR REGISTRATION
# ==========================================
echo ""
echo "Checking Solvr registration..."
((CHECKED++))

# Check if user agreed to Solvr
SOLVR_ANSWER=$(grep -A2 -i "solvr\|collective" ONBOARDING.md | grep "^>" | sed 's/^>[[:space:]]*//' | tr '[:upper:]' '[:lower:]')

case "$SOLVR_ANSWER" in
    *yes*|*sure*|*enable*|*ok*)
        SOLVR_WANTED="yes"
        ;;
    *no*|*skip*|*later*)
        SOLVR_WANTED="no"
        ;;
    *)
        SOLVR_WANTED=""
        ;;
esac

if [ "$SOLVR_WANTED" = "yes" ]; then
    # Check if actually registered
    if [ -f "TOOLS.md" ] && grep -qi "solvr_[a-zA-Z0-9]" TOOLS.md; then
        pass "Solvr: registered (as configured)"
    else
        fail "Solvr: user wants it but not registered!"
        echo "   Agent should register user on Solvr and add key to TOOLS.md"
    fi
elif [ "$SOLVR_WANTED" = "no" ]; then
    info "Solvr: user declined (respecting choice)"
else
    info "No Solvr preference found in ONBOARDING.md"
fi

# ==========================================
# SUMMARY
# ==========================================
echo ""
echo "============================"
echo "Checked: $CHECKED settings"
if [ $FIXES -gt 0 ]; then
    echo -e "${GREEN}Fixed: $FIXES settings${NC}"
fi
echo ""

if [ "$1" != "--fix" ]; then
    echo "Run with --fix to auto-apply missing configs:"
    echo "  ./config-enforce.sh --fix"
fi
