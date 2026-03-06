#!/usr/bin/env python3
"""Sync Antigravity knowledge into OpenClaw context.

Reads Knowledge Items, tasks, memory, and sessions from Antigravity,
then generates a summary file for OpenClaw to consume.
"""
# SECURITY MANIFEST:
# Environment variables accessed: HOME (only)
# External endpoints called: none
# Local files read: ~/.gemini/antigravity/knowledge/*, .agent/tasks.md,
#   .agent/memory/*, .agent/sessions/*
# Local files written: <workspace>/antigravity-sync.md

import json
import os
import sys
from datetime import datetime
from pathlib import Path

CONFIG_PATH = os.path.expanduser("~/.openclaw/antigravity-bridge.json")


def load_config() -> dict:
    if not os.path.exists(CONFIG_PATH):
        print(f"Error: Config not found at {CONFIG_PATH}")
        print("Run: python3 scripts/configure.py")
        sys.exit(1)
    with open(CONFIG_PATH) as f:
        return json.load(f)


def read_ki_summaries(knowledge_dir: str) -> list[dict]:
    """Read all Knowledge Item metadata summaries."""
    ki_dir = Path(os.path.expanduser(knowledge_dir))
    if not ki_dir.exists():
        return []

    summaries = []
    for topic_dir in sorted(ki_dir.iterdir()):
        if not topic_dir.is_dir() or topic_dir.name.startswith("."):
            continue
        meta_path = topic_dir / "metadata.json"
        ts_path = topic_dir / "timestamps.json"
        if not meta_path.exists():
            continue

        try:
            with open(meta_path) as f:
                meta = json.load(f)
        except json.JSONDecodeError:
            # Some metadata files have trailing markdown artifacts
            with open(meta_path) as f:
                raw = f.read().strip()
            # Try to extract valid JSON
            try:
                # Find the last closing brace
                last_brace = raw.rindex("}")
                meta = json.loads(raw[:last_brace + 1])
            except (ValueError, json.JSONDecodeError):
                continue

        updated = ""
        if ts_path.exists():
            with open(ts_path) as f:
                ts = json.load(f)
                updated = ts.get("updated", "")

        artifacts = []
        artifact_dir = topic_dir / "artifacts"
        if artifact_dir.exists():
            for art in sorted(artifact_dir.rglob("*.md")):
                artifacts.append(str(art.relative_to(artifact_dir)))

        summaries.append({
            "topic": topic_dir.name,
            "title": meta.get("title", topic_dir.name),
            "summary": meta.get("summary", ""),
            "updated": updated,
            "artifact_count": len(artifacts),
            "artifacts": artifacts[:10],  # first 10 for brevity
        })

    return summaries


def read_tasks(agent_dir: str) -> dict:
    """Read tasks.md and extract stats."""
    tasks_path = Path(os.path.expanduser(agent_dir)) / "tasks.md"
    if not tasks_path.exists():
        return {"exists": False}

    content = tasks_path.read_text()
    done = content.count("[x]")
    todo = content.count("[ ]")
    active = content.count("[>]")
    skipped = content.count("[-]")

    # Find active tasks
    active_tasks = []
    for line in content.splitlines():
        if "[>]" in line:
            active_tasks.append(line.strip().lstrip("- "))

    return {
        "exists": True,
        "done": done,
        "todo": todo,
        "active": active,
        "skipped": skipped,
        "active_tasks": active_tasks,
    }


def read_recent_memory(agent_dir: str, max_files: int = 5) -> list[dict]:
    """Read recent lessons learned from .agent/memory/."""
    memory_dir = Path(os.path.expanduser(agent_dir)) / "memory"
    if not memory_dir.exists():
        return []

    files = sorted(memory_dir.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)
    memories = []
    for f in files[:max_files]:
        content = f.read_text()
        # First 500 chars as preview
        memories.append({
            "file": f.name,
            "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
            "preview": content[:500],
        })
    return memories


def read_sessions(agent_dir: str) -> list[dict]:
    """Read continuation prompts from .agent/sessions/."""
    sessions_dir = Path(os.path.expanduser(agent_dir)) / "sessions"
    if not sessions_dir.exists():
        return []

    sessions = []
    for f in sorted(sessions_dir.glob("*.md")):
        content = f.read_text()
        sessions.append({
            "file": f.name,
            "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
            "preview": content[:1000],
        })
    return sessions


def generate_summary(config: dict) -> str:
    """Generate a markdown summary of all Antigravity knowledge."""
    ki_summaries = read_ki_summaries(config["knowledge_dir"])
    tasks = read_tasks(config["agent_dir"])
    memories = read_recent_memory(config["agent_dir"])
    sessions = read_sessions(config["agent_dir"])

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# Antigravity Sync — {now}",
        "",
        "## Knowledge Items",
        f"Total KI topics: {len(ki_summaries)}",
        "",
    ]

    for ki in ki_summaries:
        lines.append(f"### {ki['title']}")
        lines.append(f"*Topic:* `{ki['topic']}` | *Artifacts:* {ki['artifact_count']} | *Updated:* {ki['updated']}")
        lines.append(f"> {ki['summary']}")
        lines.append("")

    if tasks.get("exists"):
        lines.extend([
            "## Task Status",
            f"- ✅ Done: {tasks['done']}",
            f"- 📋 Todo: {tasks['todo']}",
            f"- 🔄 Active: {tasks['active']}",
            f"- ⏭️ Skipped: {tasks['skipped']}",
            "",
        ])
        if tasks["active_tasks"]:
            lines.append("**Active tasks:**")
            for t in tasks["active_tasks"]:
                lines.append(f"- {t}")
            lines.append("")

    if memories:
        lines.extend(["## Recent Memory (Lessons Learned)", ""])
        for m in memories:
            lines.append(f"### {m['file']}")
            lines.append(f"*Modified:* {m['modified']}")
            lines.append(f"```\n{m['preview']}\n```")
            lines.append("")

    if sessions:
        lines.extend(["## Session Handoffs", ""])
        for s in sessions:
            lines.append(f"### {s['file']}")
            lines.append(f"*Modified:* {s['modified']}")
            lines.append(f"```\n{s['preview']}\n```")
            lines.append("")

    return "\n".join(lines)


def main():
    config = load_config()
    summary = generate_summary(config)

    # Write to workspace
    workspace = os.path.expanduser("~/.openclaw/workspace")
    output_path = os.path.join(workspace, "antigravity-sync.md")
    os.makedirs(workspace, exist_ok=True)

    with open(output_path, "w") as f:
        f.write(summary)

    print(f"✅ Sync complete → {output_path}")
    print(summary[:500] + "..." if len(summary) > 500 else summary)


if __name__ == "__main__":
    main()
