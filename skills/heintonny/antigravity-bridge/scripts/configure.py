#!/usr/bin/env python3
"""Configure antigravity-bridge paths interactively."""
# SECURITY MANIFEST:
# Environment variables accessed: HOME (only)
# External endpoints called: none
# Local files read: ~/.openclaw/antigravity-bridge.json (if exists)
# Local files written: ~/.openclaw/antigravity-bridge.json

import json
import os
import sys

CONFIG_PATH = os.path.expanduser("~/.openclaw/antigravity-bridge.json")
DEFAULT_KNOWLEDGE = "~/.gemini/antigravity/knowledge"


def prompt(msg: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    val = input(f"{msg}{suffix}: ").strip()
    return val if val else default


def main():
    print("🌉 Antigravity Bridge — Configuration\n")

    existing = {}
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            existing = json.load(f)
        print(f"Existing config found at {CONFIG_PATH}\n")

    knowledge_dir = prompt(
        "Antigravity knowledge directory",
        existing.get("knowledge_dir", DEFAULT_KNOWLEDGE),
    )
    project_dir = prompt(
        "Project directory (with .agent/)",
        existing.get("project_dir", ""),
    )
    if not project_dir:
        print("Error: project directory is required.")
        sys.exit(1)

    agent_dir = os.path.join(project_dir, ".agent")
    gemini_md = os.path.join(project_dir, ".gemini", "GEMINI.md")

    auto_commit = prompt(
        "Auto-commit changes to git? (yes/no)",
        "yes" if existing.get("auto_commit") else "no",
    )

    config = {
        "knowledge_dir": knowledge_dir,
        "project_dir": project_dir,
        "agent_dir": agent_dir,
        "gemini_md": gemini_md,
        "auto_commit": auto_commit.lower() in ("yes", "y", "true"),
    }

    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)

    print(f"\n✅ Config saved to {CONFIG_PATH}")
    print(json.dumps(config, indent=2))


if __name__ == "__main__":
    main()
