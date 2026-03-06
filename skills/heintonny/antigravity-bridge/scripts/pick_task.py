#!/usr/bin/env python3
"""Pick the next available task from .agent/tasks.md and prepare a coding brief."""
# SECURITY MANIFEST:
# Environment variables accessed: HOME (only)
# External endpoints called: none
# Local files read: .agent/tasks.md, .agent/rules/*.md, .agent/memory/*.md,
#   ~/.gemini/antigravity/knowledge/*/metadata.json
# Local files written: .agent/tasks.md (marks [>]), stdout (task brief)

import json
import os
import re
import sys
from pathlib import Path

CONFIG_PATH = os.path.expanduser("~/.openclaw/antigravity-bridge.json")


def load_config() -> dict:
    if not os.path.exists(CONFIG_PATH):
        print(f"Error: Config not found at {CONFIG_PATH}")
        sys.exit(1)
    with open(CONFIG_PATH) as f:
        return json.load(f)


def find_next_task(content: str) -> tuple[str | None, str | None, int | None]:
    """Find the first [ ] task. Returns (task_name, full_line, line_number)."""
    for i, line in enumerate(content.splitlines()):
        m = re.search(r"- \[ \] \*\*(.+?)\*\*", line)
        if m:
            return m.group(1), line, i
    return None, None, None


def mark_active(content: str, line_num: int) -> str:
    """Mark a task as [>] active."""
    lines = content.splitlines()
    lines[line_num] = lines[line_num].replace("[ ]", "[>]", 1)
    return "\n".join(lines) + "\n"


def collect_rules(agent_dir: str) -> list[str]:
    """List available rules."""
    rules_dir = Path(os.path.expanduser(agent_dir)) / "rules"
    if not rules_dir.exists():
        return []
    return sorted(f.name for f in rules_dir.glob("*.md"))


def collect_relevant_memory(agent_dir: str, task_name: str, max_files: int = 5) -> list[str]:
    """Find memory files potentially relevant to the task."""
    memory_dir = Path(os.path.expanduser(agent_dir)) / "memory"
    if not memory_dir.exists():
        return []

    # Simple keyword matching
    keywords = set(task_name.lower().split())
    scored = []
    for f in memory_dir.glob("*.md"):
        content = f.read_text().lower()
        score = sum(1 for kw in keywords if kw in content)
        if score > 0:
            scored.append((score, f.name))

    scored.sort(reverse=True)
    return [name for _, name in scored[:max_files]]


def collect_ki_topics(knowledge_dir: str) -> list[str]:
    """List KI topic names with summaries."""
    ki_dir = Path(os.path.expanduser(knowledge_dir))
    if not ki_dir.exists():
        return []

    topics = []
    for topic_dir in sorted(ki_dir.iterdir()):
        if not topic_dir.is_dir() or topic_dir.name.startswith("."):
            continue
        meta_path = topic_dir / "metadata.json"
        if meta_path.exists():
            try:
                with open(meta_path) as f:
                    meta = json.load(f)
            except json.JSONDecodeError:
                with open(meta_path) as f:
                    raw = f.read().strip()
                try:
                    meta = json.loads(raw[:raw.rindex("}") + 1])
                except (ValueError, json.JSONDecodeError):
                    continue
            topics.append(f"{topic_dir.name}: {meta.get('title', '')}")
    return topics


def main():
    config = load_config()
    agent_dir = config["agent_dir"]
    tasks_path = Path(os.path.expanduser(agent_dir)) / "tasks.md"

    if not tasks_path.exists():
        print("Error: .agent/tasks.md not found")
        sys.exit(1)

    content = tasks_path.read_text()
    task_name, task_line, line_num = find_next_task(content)

    if task_name is None:
        print("🎉 No remaining tasks! All done.")
        sys.exit(0)

    # Mark as active
    if "--dry-run" not in sys.argv:
        updated = mark_active(content, line_num)
        tasks_path.write_text(updated)
        print(f"✅ Marked as active: {task_name}")
    else:
        print(f"🔍 Would pick: {task_name}")

    # Collect context
    rules = collect_rules(agent_dir)
    memories = collect_relevant_memory(agent_dir, task_name)
    ki_topics = collect_ki_topics(config["knowledge_dir"])

    # Generate task brief
    brief = [
        "# Task Brief for Coding Sub-Agent",
        "",
        f"## Task: {task_name}",
        f"Line: {task_line}",
        "",
        "## Available Rules (load ALL before coding)",
        *[f"- .agent/rules/{r}" for r in rules],
        "",
        "## Relevant Memory Files",
        *(([f"- .agent/memory/{m}" for m in memories]) if memories else ["- (none found)"]),
        "",
        "## Knowledge Items Available",
        *[f"- {t}" for t in ki_topics],
        "",
        "## Instructions",
        "1. Read ALL rules in .agent/rules/",
        "2. Read relevant memory files listed above",
        "3. Read relevant KI artifacts for this task's domain",
        "4. Create a feature branch: `clawd/<task-kebab-name>`",
        "5. Implement the task following project standards",
        "6. Run tests (vitest for frontend, go test for backend)",
        "7. Commit with conventional commit message",
        "8. Mark task [x] in .agent/tasks.md when done",
        "9. Write a lesson learned to .agent/memory/ if applicable",
    ]

    output = "\n".join(brief)
    print("\n" + output)

    # Also write to stdout-friendly file
    brief_path = Path(os.path.expanduser(agent_dir)) / "sessions" / "current-task-brief.md"
    brief_path.parent.mkdir(parents=True, exist_ok=True)
    brief_path.write_text(output)
    print(f"\n📄 Brief saved to: {brief_path}")


if __name__ == "__main__":
    main()
