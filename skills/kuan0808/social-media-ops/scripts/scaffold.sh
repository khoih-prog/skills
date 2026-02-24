#!/usr/bin/env bash
set -euo pipefail

# scaffold.sh — Social Media Ops Skill Scaffolding
# Creates directory structure, copies templates, and sets up symlinks.

# ── Defaults ──────────────────────────────────────────────────────────

BASE_DIR="${HOME}/.openclaw"
AGENTS="leader,researcher,content,designer,operator,engineer,reviewer"
SKILL_DIR=""
QUIET=false

# ── Usage ─────────────────────────────────────────────────────────────

usage() {
  cat <<'EOF'
Usage: scaffold.sh [OPTIONS]

Options:
  --base-dir DIR      OpenClaw root directory (default: ~/.openclaw)
  --agents LIST       Comma-separated agent list (default: all 7)
                      Minimal: leader,content,designer,engineer
  --skill-dir DIR     Path to this skill's directory (required)
  --quiet             Suppress progress messages
  -h, --help          Show this help

Examples:
  scaffold.sh --skill-dir /path/to/social-media-ops
  scaffold.sh --skill-dir /path/to/social-media-ops --agents leader,content,designer,engineer
  scaffold.sh --base-dir /custom/openclaw --skill-dir /path/to/social-media-ops
EOF
  exit 0
}

# ── Argument Parsing ──────────────────────────────────────────────────

while [[ $# -gt 0 ]]; do
  case "$1" in
    --base-dir)   BASE_DIR="$2";   shift 2 ;;
    --agents)     AGENTS="$2";     shift 2 ;;
    --skill-dir)  SKILL_DIR="$2";  shift 2 ;;
    --quiet)      QUIET=true;      shift   ;;
    -h|--help)    usage ;;
    *)            echo "[ERROR] Unknown option: $1"; exit 1 ;;
  esac
done

if [[ -z "$SKILL_DIR" ]]; then
  echo "[ERROR] --skill-dir is required"
  exit 1
fi

if [[ ! -d "$SKILL_DIR/assets" ]]; then
  echo "[ERROR] Skill directory does not contain assets/: $SKILL_DIR"
  exit 1
fi

# ── Helpers ───────────────────────────────────────────────────────────

log() {
  if [[ "$QUIET" != true ]]; then
    echo "$1"
  fi
}

ok()   { log "[OK]   $1"; }
skip() { log "[SKIP] $1"; }
info() { log "[INFO] $1"; }

ASSETS="$SKILL_DIR/assets"

# Parse agent list into array
IFS=',' read -ra AGENT_LIST <<< "$AGENTS"

# Validate that leader is always included
LEADER_FOUND=false
for agent in "${AGENT_LIST[@]}"; do
  if [[ "$agent" == "leader" ]]; then
    LEADER_FOUND=true
    break
  fi
done

if [[ "$LEADER_FOUND" != true ]]; then
  echo "[ERROR] Leader agent is required and must be in the agent list"
  exit 1
fi

# Map agent IDs to workspace directory names
agent_workspace_dir() {
  local agent="$1"
  if [[ "$agent" == "leader" ]]; then
    echo "workspace"
  else
    echo "workspace-${agent}"
  fi
}

# Map agent IDs to asset source directory names
agent_asset_dir() {
  local agent="$1"
  if [[ "$agent" == "leader" ]]; then
    echo "workspace"
  else
    echo "workspace-${agent}"
  fi
}

# ── Step 1: Verify Base Directory ─────────────────────────────────────

info "Base directory: $BASE_DIR"

if [[ ! -d "$BASE_DIR" ]]; then
  echo "[ERROR] Base directory does not exist: $BASE_DIR"
  echo "        Run 'openclaw onboard' first."
  exit 1
fi

# ── Step 2: Create Agent Workspaces ───────────────────────────────────

info "Setting up agent workspaces..."

for agent in "${AGENT_LIST[@]}"; do
  ws_dir=$(agent_workspace_dir "$agent")
  ws_path="$BASE_DIR/$ws_dir"
  asset_src=$(agent_asset_dir "$agent")

  # Create workspace directory
  mkdir -p "$ws_path"
  mkdir -p "$ws_path/memory"

  # Copy SOUL.md
  if [[ -f "$ASSETS/$asset_src/SOUL.md" ]]; then
    if [[ ! -f "$ws_path/SOUL.md" ]]; then
      cp "$ASSETS/$asset_src/SOUL.md" "$ws_path/SOUL.md"
      ok "$ws_dir/SOUL.md"
    else
      skip "$ws_dir/SOUL.md (already exists)"
    fi
  fi

  # Copy SECURITY.md
  if [[ -f "$ASSETS/$asset_src/SECURITY.md" ]]; then
    if [[ ! -f "$ws_path/SECURITY.md" ]]; then
      cp "$ASSETS/$asset_src/SECURITY.md" "$ws_path/SECURITY.md"
      ok "$ws_dir/SECURITY.md"
    else
      skip "$ws_dir/SECURITY.md (already exists)"
    fi
  fi

  # Leader-specific files
  if [[ "$agent" == "leader" ]]; then
    for file in AGENTS.md HEARTBEAT.md IDENTITY.md; do
      if [[ -f "$ASSETS/workspace/$file" ]]; then
        if [[ ! -f "$ws_path/$file" ]]; then
          cp "$ASSETS/workspace/$file" "$ws_path/$file"
          ok "$ws_dir/$file"
        else
          skip "$ws_dir/$file (already exists)"
        fi
      fi
    done

    # Create skills directory for leader
    mkdir -p "$ws_path/skills"

    # Create assets directory structure
    mkdir -p "$ws_path/assets/shared"
  fi

  # Create skills directory for non-leader agents
  if [[ "$agent" != "leader" ]]; then
    mkdir -p "$ws_path/skills"
  fi

  # Create MEMORY.md if it doesn't exist (skip for reviewer)
  if [[ "$agent" != "reviewer" && ! -f "$ws_path/MEMORY.md" ]]; then
    echo "# MEMORY.md — $(echo "$agent" | sed 's/./\U&/')" > "$ws_path/MEMORY.md"
    echo "" >> "$ws_path/MEMORY.md"
    echo "_Curated long-term memory. Updated during daily consolidation and significant events._" >> "$ws_path/MEMORY.md"
    ok "$ws_dir/MEMORY.md (initialized)"
  fi
done

# ── Step 3: Create Shared Knowledge Base ──────────────────────────────

info "Setting up shared knowledge base..."

SHARED="$BASE_DIR/shared"
mkdir -p "$SHARED/brands/_template"
mkdir -p "$SHARED/domain/_template"
mkdir -p "$SHARED/operations"
mkdir -p "$SHARED/errors"

# Copy shared KB templates (only if they don't exist)
shared_files=(
  "system-guide.md"
  "brand-guide.md"
  "compliance-guide.md"
  "team-roster.md"
  "brand-registry.md"
)

for file in "${shared_files[@]}"; do
  if [[ -f "$ASSETS/shared/$file" && ! -f "$SHARED/$file" ]]; then
    cp "$ASSETS/shared/$file" "$SHARED/$file"
    ok "shared/$file"
  elif [[ -f "$SHARED/$file" ]]; then
    skip "shared/$file (already exists)"
  fi
done

# Copy brand templates
for file in profile.md content-guidelines.md; do
  if [[ -f "$ASSETS/shared/brands/_template/$file" && ! -f "$SHARED/brands/_template/$file" ]]; then
    cp "$ASSETS/shared/brands/_template/$file" "$SHARED/brands/_template/$file"
    ok "shared/brands/_template/$file"
  elif [[ -f "$SHARED/brands/_template/$file" ]]; then
    skip "shared/brands/_template/$file (already exists)"
  fi
done

# Copy domain template
if [[ -f "$ASSETS/shared/domain/_template/industry.md" && ! -f "$SHARED/domain/_template/industry.md" ]]; then
  cp "$ASSETS/shared/domain/_template/industry.md" "$SHARED/domain/_template/industry.md"
  ok "shared/domain/_template/industry.md"
elif [[ -f "$SHARED/domain/_template/industry.md" ]]; then
  skip "shared/domain/_template/industry.md (already exists)"
fi

# Copy operations templates
ops_files=(
  "communication-signals.md"
  "approval-workflow.md"
  "posting-schedule.md"
  "content-guidelines.md"
  "channel-map.md"
)

for file in "${ops_files[@]}"; do
  if [[ -f "$ASSETS/shared/operations/$file" && ! -f "$SHARED/operations/$file" ]]; then
    cp "$ASSETS/shared/operations/$file" "$SHARED/operations/$file"
    ok "shared/operations/$file"
  elif [[ -f "$SHARED/operations/$file" ]]; then
    skip "shared/operations/$file (already exists)"
  fi
done

# Copy errors template
if [[ -f "$ASSETS/shared/errors/solutions.md" && ! -f "$SHARED/errors/solutions.md" ]]; then
  cp "$ASSETS/shared/errors/solutions.md" "$SHARED/errors/solutions.md"
  ok "shared/errors/solutions.md"
elif [[ -f "$SHARED/errors/solutions.md" ]]; then
  skip "shared/errors/solutions.md (already exists)"
fi

# ── Step 4: Create Symlinks to shared/ ────────────────────────────────

info "Creating symlinks to shared knowledge base..."

for agent in "${AGENT_LIST[@]}"; do
  ws_dir=$(agent_workspace_dir "$agent")
  ws_path="$BASE_DIR/$ws_dir"
  link_path="$ws_path/shared"

  if [[ -L "$link_path" ]]; then
    skip "$ws_dir/shared (symlink already exists)"
  elif [[ -d "$link_path" ]]; then
    skip "$ws_dir/shared (directory exists — not overwriting)"
  else
    ln -s "$SHARED" "$link_path"
    ok "$ws_dir/shared -> ../shared/"
  fi
done

# ── Step 5: Copy Sub-Skills ───────────────────────────────────────────

info "Installing sub-skills..."

LEADER_SKILLS="$BASE_DIR/workspace/skills"
mkdir -p "$LEADER_SKILLS"

# instance-setup
if [[ -d "$ASSETS/skills/instance-setup" ]]; then
  if [[ ! -d "$LEADER_SKILLS/instance-setup" ]]; then
    cp -r "$ASSETS/skills/instance-setup" "$LEADER_SKILLS/instance-setup"
    ok "skills/instance-setup"
  else
    skip "skills/instance-setup (already exists)"
  fi
fi

# brand-manager
if [[ -d "$ASSETS/skills/brand-manager" ]]; then
  if [[ ! -d "$LEADER_SKILLS/brand-manager" ]]; then
    cp -r "$ASSETS/skills/brand-manager" "$LEADER_SKILLS/brand-manager"
    ok "skills/brand-manager"
  else
    skip "skills/brand-manager (already exists)"
  fi
fi

# ── Step 6: Copy Cron Jobs ────────────────────────────────────────────

info "Setting up cron jobs..."

CRON_DIR="$BASE_DIR/cron"
mkdir -p "$CRON_DIR"

if [[ -f "$ASSETS/config/cron-jobs.json" ]]; then
  if [[ ! -f "$CRON_DIR/jobs.json" ]]; then
    cp "$ASSETS/config/cron-jobs.json" "$CRON_DIR/jobs.json"
    ok "cron/jobs.json"
  else
    skip "cron/jobs.json (already exists — will be merged by patch-config)"
  fi
fi

# ── Summary ───────────────────────────────────────────────────────────

info ""
info "=== Scaffold Complete ==="
info ""
info "Agents set up: ${AGENTS}"
info "Base directory: ${BASE_DIR}"
info ""
info "Next steps:"
info "  1. Run patch-config.js to update openclaw.json"
info "  2. Run instance-setup to configure owner and platform"
info "  3. Run brand-manager add to create your first brand"
info "  4. Restart gateway: openclaw gateway restart"
