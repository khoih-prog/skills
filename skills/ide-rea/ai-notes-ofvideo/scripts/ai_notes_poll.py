#!/usr/bin/env python3
"""
AI Video Notes - Poll Task
Automatically poll task until completion with progress updates.
"""

import os
import sys
import json
import time
import requests
from typing import Dict, Any


STATUS_CODES = {
    10000: "processing",
    10002: "completed",
}


def query_task(api_key: str, task_id: str) -> Dict[str, Any]:
    """Query task status."""
    url = "https://qianfan.baidubce.com/v2/tools/ai_note/query"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "X-Appbuilder-From": "openclaw",
        "Content-Type": "application/json"
    }
    params = {"task_id": task_id}

    response = requests.get(url, headers=headers, params=params, timeout=30)
    response.raise_for_status()
    result = response.json()

    if "errno" in result and result["errno"] != 0:
        raise RuntimeError(result.get("errmsg", "Unknown error"))

    return result["data"]


def poll_task(api_key: str, task_id: str, max_attempts: int = 20, interval: int = 3):
    """Poll task until completion or timeout.

    Args:
        api_key: Baidu API key
        task_id: Task ID
        max_attempts: Maximum poll attempts (default 20)
        interval: Seconds between polls (default 3)

    Returns:
        Final task data
    """
    note_types = {1: "document", 2: "outline", 3: "graphic-text"}

    for attempt in range(max_attempts):
        try:
            data = query_task(api_key, task_id)
            aiNotesList = data.get("list", [])
            status_code = 0
            for note in aiNotesList:
                status_code = note.get("detail", {}).get("status", 0)
                if status_code != 10002:
                    break

            if status_code == 10002:
                notes = []
                for note in data.get("list", []):
                    tpl_no = note.get("tpl_no")
                    notes.append({
                        "type": tpl_no,
                        "contents": note.get("detail", {}).get("contents", [])
                    })

                print("\n" + "=" * 50)
                print("✓ NOTES GENERATED SUCCESSFULLY")
                print("=" * 50)
                print(json.dumps(notes, indent=2, ensure_ascii=False))
                return data

            elif status_code == 10000:
                progress = data.get("progress", 0)
                print(f"[{attempt + 1}/{max_attempts}] Processing... {progress}%")
                time.sleep(interval)

            else:
                print(f"\n✗ Task failed: {data.get('error', 'Unknown error')}")
                return data

        except RuntimeError as e:
            print(f"\n✗ Error: {str(e)}")
            return data
        except Exception as e:
            if attempt == max_attempts - 1:
                print(f"\n✗ Unexpected error: {str(e)}")
                return data
            time.sleep(interval)

    print(f"\n✗ Timeout after {max_attempts * interval} seconds")
    print("Task may still be running. Try querying manually:")
    print(f"  python scripts/ai_notes_task_query.py {task_id}")
    return data


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "Missing task ID",
            "usage": "python ai_notes_poll.py <task_id> [max_attempts] [interval_seconds]"
        }, indent=2))
        sys.exit(1)

    task_id = sys.argv[1]
    max_attempts = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    interval = int(sys.argv[3]) if len(sys.argv) > 3 else 3

    api_key = os.getenv("BAIDU_API_KEY")
    if not api_key:
        print(json.dumps({
            "error": "BAIDU_API_KEY environment variable not set"
        }, indent=2))
        sys.exit(1)

    print(f"Polling task: {task_id}")
    print(f"Max attempts: {max_attempts}, Interval: {interval}s")
    print("-" * 50)

    poll_task(api_key, task_id, max_attempts, interval)


if __name__ == "__main__":
    main()
