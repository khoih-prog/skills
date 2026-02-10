#!/usr/bin/env python3
"""
AI Video Notes - Query Task
Poll task status and retrieve generated notes.
"""

import os
import sys
import json
import requests
from typing import Dict, Any, List


STATUS_CODES = {
    10000: "processing",
    10002: "completed",
}


def query_note_task(api_key: str, task_id: str) -> Dict[str, Any]:
    """Query AI note generation task status.

    Args:
        api_key: Baidu API key
        task_id: Task ID

    Returns:
        Task data with status and notes

    Raises:
        RuntimeError: If API returns error
    """
    url = "https://qianfan.baidubce.com/v2/tools/ai_note/query"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "X-Appbuilder-From": "openclaw",
        "Content-Type": "application/json"
    }
    params = {"task_id": task_id}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        result = response.json()

        if "code" in result:
            raise RuntimeError(result.get("detail", "API error"))
        if "errno" in result and result["errno"] != 0:
            raise RuntimeError(result.get("errmsg", "Unknown error"))

        return result["data"]

    except requests.exceptions.Timeout:
        raise RuntimeError("Request timeout. Try again later.")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Network error: {str(e)}")


def format_status(status_code: int) -> str:
    """Get human-readable status."""
    return STATUS_CODES.get(status_code, f"unknown ({status_code})")


def format_notes(notes: List[Dict]) -> List[Dict]:
    """Format note results with type labels."""
    note_types = {
        1: "document",
        2: "outline",
        3: "graphic-text"
    }

    formatted = []
    for note in notes:
        tpl_no = note.get("tpl_no")
        formatted.append({
            "type": note_types.get(tpl_no, "unknown"),
            "content": note.get("content", ""),
            "tpl_no": tpl_no
        })
    return formatted


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "Missing task ID",
            "usage": "python ai_notes_task_query.py <task_id>"
        }, indent=2))
        sys.exit(1)

    task_id = sys.argv[1]
    api_key = os.getenv("BAIDU_API_KEY")

    if not api_key:
        print(json.dumps({
            "error": "BAIDU_API_KEY environment variable not set"
        }, indent=2))
        sys.exit(1)

    try:
        task_data = query_note_task(api_key, task_id)
        status_code = task_data.get("status")
        status = format_status(status_code)

        if status_code == 10002:
            notes = format_notes(task_data.get("notes", []))
            print(json.dumps({
                "status": "completed",
                "task_id": task_id,
                "message": "Notes generated successfully",
                "notes": notes
            }, indent=2, ensure_ascii=False))
        elif status_code == 10000:
            print(json.dumps({
                "status": "processing",
                "task_id": task_id,
                "message": "Video analysis in progress",
                "progress": task_data.get("progress", 0),
                "next_step": "Wait 3-5 seconds, then query again"
            }, indent=2))
        else:
            print(json.dumps({
                "status": "failed",
                "task_id": task_id,
                "message": "Task failed",
                "error": task_data.get("error", "Unknown error")
            }, indent=2))

    except RuntimeError as e:
        print(json.dumps({
            "status": "error",
            "task_id": task_id,
            "error": str(e)
        }, indent=2))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({
            "status": "error",
            "task_id": task_id,
            "error": f"Unexpected error: {str(e)}"
        }, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
