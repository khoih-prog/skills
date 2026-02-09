# /// script
# requires-python = ">=3.10"
# dependencies = ["websockets"]
# ///
"""
VizClaw Connect - stream OpenClaw-style events to VizClaw.

Quick start:
  uv run https://vizclaw.com/skills/vizclaw/scripts/connect.py
  uv run https://vizclaw.com/skills/vizclaw/scripts/connect.py --mode overview

Bridge OpenClaw JSONL events from stdin:
  openclaw run ... --json | uv run https://vizclaw.com/skills/vizclaw/scripts/connect.py --openclaw-jsonl

Bridge OpenClaw websocket broadcasts:
  uv run https://vizclaw.com/skills/vizclaw/scripts/connect.py --openclaw-ws ws://localhost:9000/events

Interactive commands:
  query <text>
  human <text>
  cron <text>
  heartbeat [message]
  spawn <agent-id> <model> [work-type]
  task <agent-id> <work-type> <description>
  skill <agent-id> <skill name>
  tool <agent-id> <tool name>
  report <agent-id> [message]
  complete <agent-id>
  done [summary]
  mode <detailed|overview|hidden>
  config-skills <skill1,skill2,...>
  config-models <model1,model2,...>
  config-reminders <json array>
  config-heartbeat <interval-seconds | off>
  end
  quit
"""

import argparse
import asyncio
import json
import shlex
import sys
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from uuid import uuid4

try:
    import websockets
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_mode(mode: str) -> str:
    mode = (mode or "detailed").strip().lower()
    if mode == "hidden":
        return "overview"
    if mode in {"detailed", "overview"}:
        return mode
    return "detailed"


def normalize_trigger_source(source: str | None) -> str:
    s = (source or "human").strip().lower()
    if s in {"human", "cron", "heartbeat"}:
        return s
    return "human"


def maybe_text(text: str | None, mode: str) -> str | None:
    if not text:
        return None
    return text if mode == "detailed" else None


def parse_skills(skills_str: str | None) -> list[dict] | None:
    if not skills_str:
        return None
    return [{"name": s.strip()} for s in skills_str.split(",") if s.strip()]


def parse_available_models(models_str: str | None) -> list[dict] | None:
    if not models_str:
        return None
    models = []
    for m in models_str.split(","):
        m = m.strip()
        if not m:
            continue
        models.append({"id": m, "label": m})
    return models


def parse_reminders(reminders_json: str | None) -> list[dict] | None:
    if not reminders_json:
        return None
    try:
        parsed = json.loads(reminders_json)
        if isinstance(parsed, list):
            return parsed
    except json.JSONDecodeError:
        pass
    return None


def build_config_update(
    session_id: str,
    skills: list[dict] | None = None,
    available_models: list[dict] | None = None,
    reminders: list[dict] | None = None,
    heartbeat_interval: int | None = None,
    room_code: str | None = None,
) -> dict | None:
    payload: dict = {
        "type": "config_update",
        "sessionId": session_id,
        "timestamp": now_iso(),
    }
    has_config = False
    if skills is not None:
        payload["skills"] = skills
        has_config = True
    if available_models is not None:
        payload["availableModels"] = available_models
        has_config = True
    if reminders is not None:
        payload["reminders"] = reminders
        has_config = True
    if heartbeat_interval is not None:
        payload["heartbeatConfig"] = {
            "enabled": heartbeat_interval > 0,
            "intervalSeconds": heartbeat_interval if heartbeat_interval > 0 else None,
        }
        has_config = True
    if room_code:
        payload["roomCode"] = room_code
    return payload if has_config else None


def http_report(api_url: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = Request(
        api_url,
        data=data,
        headers={"Content-Type": "application/json", "User-Agent": "VizClaw-Connect/1.2"},
        method="POST",
    )

    try:
        with urlopen(req, timeout=12) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            return json.loads(body)
        except Exception:
            return {"error": f"HTTP {e.code}: {body}"}
    except URLError as e:
        return {"error": str(e.reason)}


def resolve_openclaw_type(evt: dict) -> str:
    for key in ("type", "event", "name", "event_type"):
        val = evt.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip().lower()
    return ""


def first_str(evt: dict, *keys: str) -> str | None:
    for key in keys:
        val = evt.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return None


def coerce_text(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        text = value.strip()
        return text or None
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, dict):
        for key in ("text", "message", "content", "error"):
            nested = value.get(key)
            if isinstance(nested, str) and nested.strip():
                return nested.strip()
    try:
        rendered = json.dumps(value, ensure_ascii=False)
    except Exception:
        return None
    rendered = rendered.strip()
    if not rendered:
        return None
    return rendered[:500]


def parse_openclaw_input_line(raw: str) -> list[dict]:
    line = raw.strip()
    if not line:
        return []
    if line.startswith("data:"):
        line = line[5:].strip()
    if not line or line == "[DONE]":
        return []
    try:
        payload = json.loads(line)
    except json.JSONDecodeError:
        return []
    if isinstance(payload, dict):
        return [payload]
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    return []


def map_openclaw_gateway_agent_event(
    payload: dict, session_id: str, default_model: str, mode: str
) -> list[dict]:
    out: list[dict] = []
    stream = first_str(payload, "stream") or ""
    run_id = first_str(payload, "runId", "run_id", "agentId", "agent_id", "id")
    agent_id = run_id or session_id
    model = first_str(payload, "model", "model_name") or default_model
    data = payload.get("data") if isinstance(payload.get("data"), dict) else {}
    phase = first_str(data, "phase", "state", "status")
    tool_name = first_str(data, "name", "toolName", "tool_name")
    query_text = first_str(data, "query", "prompt", "message")
    message_text = (
        first_str(data, "message", "text", "delta")
        or coerce_text(data.get("partialResult"))
        or coerce_text(data.get("result"))
        or coerce_text(data.get("error"))
    )

    if stream == "lifecycle":
        if phase == "start":
            out.append(
                {
                    "type": "agent_spawn",
                    "sessionId": session_id,
                    "agentId": agent_id,
                    "model": model,
                    "workType": "coding",
                }
            )
            if query_text:
                out.append(
                    {
                        "type": "query_received",
                        "sessionId": session_id,
                        "triggerSource": "human",
                        "query": maybe_text(query_text, mode),
                    }
                )
        elif phase == "error":
            if message_text:
                out.append(
                    {
                        "type": "agent_reporting",
                        "sessionId": session_id,
                        "agentId": agent_id,
                        "message": maybe_text(message_text, mode),
                    }
                )
            out.append(
                {
                    "type": "agent_complete",
                    "sessionId": session_id,
                    "agentId": agent_id,
                }
            )
        elif phase == "end":
            out.append(
                {
                    "type": "agent_complete",
                    "sessionId": session_id,
                    "agentId": agent_id,
                }
            )
        return out

    if stream == "tool":
        if phase == "start":
            task_description = f"Using tool: {tool_name or 'tool'}"
            out.append(
                {
                    "type": "task_assigned",
                    "sessionId": session_id,
                    "agentId": agent_id,
                    "workType": "coding",
                    "taskDescription": maybe_text(task_description, mode),
                    "tool": tool_name if mode == "detailed" else None,
                }
            )
            out.append(
                {
                    "type": "tool_used",
                    "sessionId": session_id,
                    "agentId": agent_id,
                    "tool": tool_name,
                    "workType": "coding",
                }
            )
        elif phase == "result":
            out.append(
                {
                    "type": "tool_used",
                    "sessionId": session_id,
                    "agentId": agent_id,
                    "tool": tool_name,
                    "workType": "coding",
                }
            )
            if message_text:
                out.append(
                    {
                        "type": "agent_reporting",
                        "sessionId": session_id,
                        "agentId": agent_id,
                        "message": maybe_text(message_text, mode),
                    }
                )
        elif phase == "update" and message_text:
            out.append(
                {
                    "type": "agent_reporting",
                    "sessionId": session_id,
                    "agentId": agent_id,
                    "message": maybe_text(message_text, mode),
                }
            )
        return out

    if stream == "assistant":
        if message_text:
            out.append(
                {
                    "type": "agent_reporting",
                    "sessionId": session_id,
                    "agentId": agent_id,
                    "message": maybe_text(message_text, mode),
                }
            )
        return out

    if stream == "error":
        if message_text:
            out.append(
                {
                    "type": "agent_reporting",
                    "sessionId": session_id,
                    "agentId": agent_id,
                    "message": maybe_text(message_text, mode),
                }
            )
        out.append(
            {
                "type": "agent_complete",
                "sessionId": session_id,
                "agentId": agent_id,
            }
        )
        return out

    return out


def map_openclaw_gateway_chat_event(payload: dict, session_id: str, mode: str) -> list[dict]:
    out: list[dict] = []
    run_id = first_str(payload, "runId", "run_id", "agentId", "agent_id")
    agent_id = run_id or session_id
    state = first_str(payload, "state", "phase", "status")
    text = (
        first_str(payload, "message", "text", "delta", "content")
        or coerce_text(payload.get("payload"))
    )

    if state in {"start", "started", "running"} and text:
        out.append(
            {
                "type": "query_received",
                "sessionId": session_id,
                "triggerSource": "human",
                "query": maybe_text(text, mode),
            }
        )
    elif state in {"final", "end", "completed", "done"}:
        out.append(
            {
                "type": "query_completed",
                "sessionId": session_id,
                "message": maybe_text(text, mode),
            }
        )
    elif state == "error":
        out.append(
            {
                "type": "query_completed",
                "sessionId": session_id,
                "message": maybe_text(text or "Agent run error", mode),
            }
        )
    elif text:
        out.append(
            {
                "type": "agent_reporting",
                "sessionId": session_id,
                "agentId": agent_id,
                "message": maybe_text(text, mode),
            }
        )

    return out


def map_openclaw_event(evt: dict, session_id: str, default_model: str, mode: str) -> list[dict]:
    event_name = first_str(evt, "event")
    payload = evt.get("payload")
    if event_name == "agent" and isinstance(payload, dict):
        mapped = map_openclaw_gateway_agent_event(payload, session_id, default_model, mode)
        if mapped:
            return mapped
    if event_name == "chat" and isinstance(payload, dict):
        mapped = map_openclaw_gateway_chat_event(payload, session_id, mode)
        if mapped:
            return mapped
    if isinstance(evt.get("stream"), str) and (
        first_str(evt, "runId", "run_id", "agentId", "agent_id", "id")
    ):
        mapped = map_openclaw_gateway_agent_event(evt, session_id, default_model, mode)
        if mapped:
            return mapped

    etype = resolve_openclaw_type(evt)
    out: list[dict] = []

    agent_id = first_str(evt, "agentId", "agent_id", "worker_id", "id")
    model = first_str(evt, "model", "model_name") or default_model
    work_type = first_str(evt, "workType", "work_type", "task_type")
    text = first_str(evt, "text", "message", "query", "prompt", "content", "description")
    skill = first_str(evt, "skill", "skill_name")
    tool = first_str(evt, "tool", "tool_name")

    if etype in {"heartbeat", "agent_heartbeat", "main_heartbeat"}:
        out.append({"type": "heartbeat", "sessionId": session_id})
        if text:
            out.append({
                "type": "query_received",
                "sessionId": session_id,
                "triggerSource": "heartbeat",
                "query": maybe_text(text, mode),
            })
        return out

    if etype in {"cron", "cron_tick", "cron_trigger", "scheduled_run", "scheduler_triggered"}:
        out.append({
            "type": "query_received",
            "sessionId": session_id,
            "triggerSource": "cron",
            "query": maybe_text(text or "Cron-triggered task", mode),
        })
        return out

    if etype in {"query_received", "user_message", "human_request", "request_received", "task_received"}:
        out.append({
            "type": "query_received",
            "sessionId": session_id,
            "triggerSource": "human",
            "query": maybe_text(text, mode),
        })
        return out

    if etype in {"agent_spawn", "agent_spawned", "agent_started", "subagent_spawned"}:
        out.append({
            "type": "agent_spawn",
            "sessionId": session_id,
            "agentId": agent_id,
            "model": model,
            "workType": work_type,
            "taskDescription": maybe_text(text, mode),
        })
        return out

    if etype in {"task_assigned", "agent_task", "task_started", "delegated_task"}:
        out.append({
            "type": "task_assigned",
            "sessionId": session_id,
            "agentId": agent_id,
            "workType": work_type,
            "taskDescription": maybe_text(text, mode),
            "skill": skill if mode == "detailed" else None,
            "tool": tool if mode == "detailed" else None,
        })
        return out

    if etype in {"tool_used", "tool_call", "tool_invoked"}:
        out.append({
            "type": "tool_used",
            "sessionId": session_id,
            "agentId": agent_id,
            "tool": tool or text,
            "workType": work_type,
        })
        return out

    if etype in {"skill_used", "skill_applied", "skill_selected"}:
        out.append({
            "type": "skill_used",
            "sessionId": session_id,
            "agentId": agent_id,
            "skill": skill or text,
            "workType": work_type,
        })
        return out

    if etype in {"agent_report", "agent_reporting", "partial_result", "progress"}:
        out.append({
            "type": "agent_reporting",
            "sessionId": session_id,
            "agentId": agent_id,
            "message": maybe_text(text, mode),
        })
        return out

    if etype in {"agent_complete", "agent_completed", "task_complete", "subagent_done"}:
        out.append({
            "type": "agent_complete",
            "sessionId": session_id,
            "agentId": agent_id,
        })
        return out

    if etype in {"query_completed", "final_result", "run_complete"}:
        out.append({
            "type": "query_completed",
            "sessionId": session_id,
            "message": maybe_text(text, mode),
        })
        return out

    if etype in {"session_end", "run_end"}:
        out.append({"type": "session_end", "sessionId": session_id})
        return out

    # Config events from OpenClaw
    if etype in {"config_loaded", "skills_loaded", "config_update", "plugin_loaded"}:
        config: dict = {"type": "config_update", "sessionId": session_id}
        skills_raw = evt.get("skills") or evt.get("plugins")
        if isinstance(skills_raw, list):
            config["skills"] = [
                {"name": s.get("name", s) if isinstance(s, dict) else str(s)}
                for s in skills_raw
            ]
        models_raw = evt.get("availableModels") or evt.get("models")
        if isinstance(models_raw, list):
            config["availableModels"] = [
                {"id": m.get("id", m) if isinstance(m, dict) else str(m),
                 "label": m.get("label", m.get("id", m)) if isinstance(m, dict) else str(m)}
                for m in models_raw
            ]
        reminders_raw = evt.get("reminders") or evt.get("scheduled_tasks")
        if isinstance(reminders_raw, list):
            config["reminders"] = reminders_raw
        hb = evt.get("heartbeatConfig") or evt.get("heartbeat_config")
        if isinstance(hb, dict):
            config["heartbeatConfig"] = hb
        out.append(config)
        return out

    if etype in {"reminder_triggered", "scheduled_task_fired"}:
        title = first_str(evt, "title", "reminder", "task_name") or "Scheduled task"
        out.append({
            "type": "query_received",
            "sessionId": session_id,
            "triggerSource": "cron",
            "query": maybe_text(text or title, mode),
        })
        return out

    # Fallback: if there's free text, treat it as human trigger query.
    if text:
        out.append({
            "type": "query_received",
            "sessionId": session_id,
            "triggerSource": "human",
            "query": maybe_text(text, mode),
        })

    return out


async def read_stdin_lines():
    loop = asyncio.get_event_loop()
    while True:
        line = await loop.run_in_executor(None, sys.stdin.readline)
        if not line:
            break
        yield line.strip()


async def read_openclaw_ws_events(openclaw_ws: str):
    async with websockets.connect(openclaw_ws) as source_ws:
        async for raw in source_ws:
            if not isinstance(raw, str):
                continue
            for parsed in parse_openclaw_input_line(raw):
                yield parsed


async def connect_interactive(
    hub: str,
    model: str,
    mode: str,
    session_id: str,
    openclaw_jsonl: bool,
    openclaw_ws: str | None,
    skills: list[dict] | None = None,
    available_models: list[dict] | None = None,
    reminders: list[dict] | None = None,
    heartbeat_interval: int | None = None,
):
    if not HAS_WEBSOCKETS:
        print("Error: websockets package not found. Install with: pip install websockets", file=sys.stderr)
        sys.exit(1)

    mode = normalize_mode(mode)
    print(f"VizClaw Connect: connecting to {hub}")

    async with websockets.connect(hub) as ws:
        await ws.send(json.dumps({
            "type": "session_start",
            "sessionId": session_id,
            "model": model,
            "mode": mode,
            "timestamp": now_iso(),
        }))

        resp = json.loads(await ws.recv())
        if resp.get("type") == "room_created":
            room_code = resp.get("roomCode")
            viewer_url = resp.get("viewerUrl", f"https://vizclaw.com/room/{room_code}")
            print("Connected")
            print(f"room_code={room_code}")
            print(f"session_id={session_id}")
            print(f"viewer_url={viewer_url}")

            # Send config_update if any config flags were provided
            config_msg = build_config_update(
                session_id, skills, available_models, reminders, heartbeat_interval,
            )
            if config_msg:
                await ws.send(json.dumps(config_msg))
                print("config_update sent")

            if openclaw_jsonl:
                print("Reading OpenClaw JSON events from stdin...")
            elif openclaw_ws:
                print(f"Subscribing to OpenClaw event websocket: {openclaw_ws}")
            else:
                print("Type 'help' for commands.")

        async def send_heartbeats():
            while True:
                await asyncio.sleep(30)
                await ws.send(json.dumps({
                    "type": "heartbeat",
                    "sessionId": session_id,
                    "timestamp": now_iso(),
                }))

        def print_help():
            print("Commands:")
            print("  query <text>")
            print("  human <text>")
            print("  cron <text>")
            print("  heartbeat [message]")
            print("  spawn <agent-id> <model> [work-type]")
            print("  task <agent-id> <work-type> <description>")
            print("  skill <agent-id> <skill>")
            print("  tool <agent-id> <tool>")
            print("  report <agent-id> [message]")
            print("  complete <agent-id>")
            print("  done [summary]")
            print("  mode <detailed|overview|hidden>")
            print("  config-skills <skill1,skill2,...>")
            print("  config-models <model1,model2,...>")
            print("  config-reminders <json array>")
            print("  config-heartbeat <seconds | off>")
            print("  end")
            print("  quit")

        heartbeat_task = asyncio.create_task(send_heartbeats())

        try:
            if openclaw_jsonl or openclaw_ws:
                if openclaw_ws:
                    event_iter = read_openclaw_ws_events(openclaw_ws)
                else:
                    async def _stdin_events():
                        async for line in read_stdin_lines():
                            for evt in parse_openclaw_input_line(line):
                                yield evt
                    event_iter = _stdin_events()

                async for evt in event_iter:
                    mapped = map_openclaw_event(evt, session_id, model, mode)
                    for payload in mapped:
                        payload["timestamp"] = now_iso()
                        await ws.send(json.dumps(payload))

                await ws.send(json.dumps({
                    "type": "session_end",
                    "sessionId": session_id,
                    "timestamp": now_iso(),
                }))
                return

            async for cmd in read_stdin_lines():
                if not cmd:
                    continue

                try:
                    parts = shlex.split(cmd)
                except ValueError as err:
                    print(f"Invalid command: {err}")
                    continue

                action = parts[0].lower()

                if action in {"quit", "exit", "q"}:
                    break
                if action == "help":
                    print_help()
                    continue
                if action in {"query", "human", "cron"} and len(parts) >= 2:
                    source = "human" if action == "query" else action
                    query = " ".join(parts[1:])
                    await ws.send(json.dumps({
                        "type": "query_received",
                        "sessionId": session_id,
                        "triggerSource": source,
                        "query": maybe_text(query, mode),
                        "timestamp": now_iso(),
                    }))
                    print(f"query[{source}]={query}")
                    continue
                if action == "heartbeat":
                    note = " ".join(parts[1:]) if len(parts) >= 2 else None
                    await ws.send(json.dumps({
                        "type": "heartbeat",
                        "sessionId": session_id,
                        "timestamp": now_iso(),
                    }))
                    if note:
                        await ws.send(json.dumps({
                            "type": "query_received",
                            "sessionId": session_id,
                            "triggerSource": "heartbeat",
                            "query": maybe_text(note, mode),
                            "timestamp": now_iso(),
                        }))
                    print("heartbeat")
                    continue
                if action == "spawn" and len(parts) >= 3:
                    payload = {
                        "type": "agent_spawn",
                        "sessionId": session_id,
                        "agentId": parts[1],
                        "model": parts[2],
                        "timestamp": now_iso(),
                    }
                    if len(parts) >= 4:
                        payload["workType"] = parts[3]
                    await ws.send(json.dumps(payload))
                    print(f"spawned={parts[1]}")
                    continue
                if action == "task" and len(parts) >= 4:
                    agent_id = parts[1]
                    work_type = parts[2]
                    description = " ".join(parts[3:])
                    await ws.send(json.dumps({
                        "type": "task_assigned",
                        "sessionId": session_id,
                        "agentId": agent_id,
                        "workType": work_type,
                        "taskDescription": maybe_text(description, mode),
                        "timestamp": now_iso(),
                    }))
                    print(f"task={agent_id}:{work_type}")
                    continue
                if action == "skill" and len(parts) >= 3:
                    await ws.send(json.dumps({
                        "type": "skill_used",
                        "sessionId": session_id,
                        "agentId": parts[1],
                        "skill": " ".join(parts[2:]) if mode == "detailed" else None,
                        "timestamp": now_iso(),
                    }))
                    print(f"skill={parts[1]}")
                    continue
                if action == "tool" and len(parts) >= 3:
                    await ws.send(json.dumps({
                        "type": "tool_used",
                        "sessionId": session_id,
                        "agentId": parts[1],
                        "tool": " ".join(parts[2:]) if mode == "detailed" else None,
                        "timestamp": now_iso(),
                    }))
                    print(f"tool={parts[1]}")
                    continue
                if action == "report" and len(parts) >= 2:
                    await ws.send(json.dumps({
                        "type": "agent_reporting",
                        "sessionId": session_id,
                        "agentId": parts[1],
                        "message": maybe_text(" ".join(parts[2:]) if len(parts) >= 3 else None, mode),
                        "timestamp": now_iso(),
                    }))
                    print(f"report={parts[1]}")
                    continue
                if action == "complete" and len(parts) >= 2:
                    await ws.send(json.dumps({
                        "type": "agent_complete",
                        "sessionId": session_id,
                        "agentId": parts[1],
                        "timestamp": now_iso(),
                    }))
                    print(f"complete={parts[1]}")
                    continue
                if action == "done":
                    await ws.send(json.dumps({
                        "type": "query_completed",
                        "sessionId": session_id,
                        "message": maybe_text(" ".join(parts[1:]) if len(parts) >= 2 else None, mode),
                        "timestamp": now_iso(),
                    }))
                    print("query_completed")
                    continue
                if action == "mode" and len(parts) >= 2:
                    next_mode = normalize_mode(parts[1])
                    mode = next_mode
                    await ws.send(json.dumps({
                        "type": "set_mode",
                        "sessionId": session_id,
                        "mode": next_mode,
                        "timestamp": now_iso(),
                    }))
                    print(f"mode={next_mode}")
                    continue
                if action == "config-skills" and len(parts) >= 2:
                    skills_list = parse_skills(" ".join(parts[1:]))
                    msg = build_config_update(session_id, skills=skills_list)
                    if msg:
                        await ws.send(json.dumps(msg))
                        print(f"config-skills={','.join(s['name'] for s in (skills_list or []))}")
                    continue
                if action == "config-models" and len(parts) >= 2:
                    models_list = parse_available_models(" ".join(parts[1:]))
                    msg = build_config_update(session_id, available_models=models_list)
                    if msg:
                        await ws.send(json.dumps(msg))
                        print(f"config-models={','.join(m['id'] for m in (models_list or []))}")
                    continue
                if action == "config-reminders" and len(parts) >= 2:
                    reminders_list = parse_reminders(" ".join(parts[1:]))
                    msg = build_config_update(session_id, reminders=reminders_list)
                    if msg:
                        await ws.send(json.dumps(msg))
                        print(f"config-reminders={len(reminders_list or [])} items")
                    else:
                        print("Invalid JSON for reminders")
                    continue
                if action == "config-heartbeat" and len(parts) >= 2:
                    val = parts[1].strip().lower()
                    interval = 0 if val == "off" else int(val)
                    msg = build_config_update(session_id, heartbeat_interval=interval)
                    if msg:
                        await ws.send(json.dumps(msg))
                        print(f"config-heartbeat={'off' if interval == 0 else f'{interval}s'}")
                    continue
                if action == "end":
                    await ws.send(json.dumps({
                        "type": "session_end",
                        "sessionId": session_id,
                        "timestamp": now_iso(),
                    }))
                    print("session_end")
                    break

                print(f"Unknown command: {cmd}")
                print("Type 'help' for supported commands.")
        finally:
            heartbeat_task.cancel()


def run_oneshot(args, session_id: str):
    action = args.action
    mode = normalize_mode(args.mode)
    payload = {
        "sessionId": session_id,
        "timestamp": now_iso(),
    }

    if action == "start":
        payload.update({
            "type": "session_start",
            "model": args.model,
            "mode": mode,
            "triggerSource": normalize_trigger_source(args.trigger_source),
            "query": maybe_text(args.text or None, mode),
        })

    elif action == "query":
        payload.update({
            "type": "query_received",
            "roomCode": args.room_code,
            "triggerSource": normalize_trigger_source(args.trigger_source),
            "query": maybe_text(args.text or "", mode),
        })

    elif action == "spawn":
        payload.update({
            "type": "agent_spawn",
            "roomCode": args.room_code,
            "agentId": args.agent_id,
            "model": args.model,
            "workType": args.work_type,
            "taskDescription": maybe_text(args.text, mode),
        })

    elif action == "task":
        payload.update({
            "type": "task_assigned",
            "roomCode": args.room_code,
            "agentId": args.agent_id,
            "workType": args.work_type,
            "taskDescription": maybe_text(args.text, mode),
        })

    elif action == "skill":
        payload.update({
            "type": "skill_used",
            "roomCode": args.room_code,
            "agentId": args.agent_id,
            "skill": args.text if mode == "detailed" else None,
            "workType": args.work_type,
        })

    elif action == "tool":
        payload.update({
            "type": "tool_used",
            "roomCode": args.room_code,
            "agentId": args.agent_id,
            "tool": args.text if mode == "detailed" else None,
            "workType": args.work_type,
        })

    elif action == "report":
        payload.update({
            "type": "agent_reporting",
            "roomCode": args.room_code,
            "agentId": args.agent_id,
            "message": maybe_text(args.text, mode),
        })

    elif action == "complete":
        payload.update({"type": "agent_complete", "roomCode": args.room_code, "agentId": args.agent_id})

    elif action == "done":
        payload.update({"type": "query_completed", "roomCode": args.room_code, "message": maybe_text(args.text, mode)})

    elif action == "mode":
        payload.update({"type": "set_mode", "roomCode": args.room_code, "mode": mode})

    elif action == "end":
        payload.update({"type": "session_end", "roomCode": args.room_code})

    elif action == "heartbeat":
        payload.update({"type": "heartbeat", "roomCode": args.room_code})

    elif action == "config":
        config = build_config_update(
            session_id,
            skills=parse_skills(getattr(args, "skills", None)),
            available_models=parse_available_models(getattr(args, "available_models", None)),
            reminders=parse_reminders(getattr(args, "reminders_json", None)),
            heartbeat_interval=getattr(args, "heartbeat_interval", None),
            room_code=args.room_code,
        )
        if not config:
            print("Error: at least one config flag is required (--skills, --available-models, --reminders-json, --heartbeat-interval)", file=sys.stderr)
            sys.exit(1)
        payload = config

    else:
        print(f"Unsupported action: {action}", file=sys.stderr)
        sys.exit(2)

    if action != "start" and not args.room_code:
        print("Error: --room-code is required for this action", file=sys.stderr)
        sys.exit(1)

    result = http_report(args.api, payload)
    if not result.get("ok"):
        print(f"Error: {result.get('error', 'unknown')}", file=sys.stderr)
        sys.exit(1)

    if action == "start":
        room_code = result.get("roomCode", "")
        viewer_url = result.get("viewerUrl", f"https://vizclaw.com/room/{room_code}")
        print(room_code)
        print(f"session_id={session_id}", file=sys.stderr)
        print(f"viewer_url={viewer_url}", file=sys.stderr)
    else:
        print("ok")


def main():
    parser = argparse.ArgumentParser(description="VizClaw Connect")
    parser.add_argument("--hub", default="wss://api.vizclaw.com/ws/report", help="WebSocket hub URL")
    parser.add_argument("--api", default="https://api.vizclaw.com/api/report", help="HTTP API URL")
    parser.add_argument("--model", default="opus", help="Model name")
    parser.add_argument("--mode", default="detailed", help="detailed | overview | hidden")
    parser.add_argument("--trigger-source", default="human", help="human | cron | heartbeat")
    parser.add_argument("--openclaw-jsonl", action="store_true", help="Read OpenClaw-style JSON events from stdin")
    parser.add_argument("--openclaw-ws", default=None, help="Subscribe to OpenClaw websocket event stream")
    parser.add_argument("--session-id", default=None, help="Session ID (auto-generated if omitted)")
    parser.add_argument(
        "--action",
        choices=["start", "query", "spawn", "task", "skill", "tool", "report", "complete", "done", "mode", "end", "heartbeat", "config"],
        help="One-shot action via HTTP API",
    )
    parser.add_argument("--agent-id", default=None, help="Agent ID")
    parser.add_argument("--room-code", default=None, help="Room code")
    parser.add_argument("--work-type", default=None, help="Work type (coding, research, testing, etc.)")
    parser.add_argument("--text", default=None, help="Free text payload (query, description, summary, skill or tool)")
    parser.add_argument("--skills", default=None, help="Comma-separated skill names (e.g. ez-google,ez-unifi,claude-code)")
    parser.add_argument("--available-models", default=None, help="Comma-separated model names (e.g. sonnet,haiku,gpt-4o)")
    parser.add_argument("--heartbeat-interval", type=int, default=None, help="Heartbeat interval in seconds (0 to disable)")
    parser.add_argument("--reminders-json", default=None, help='JSON array of reminders, e.g. \'[{"title":"Check email","schedule":"every 30min"}]\'')

    args = parser.parse_args()
    session_id = args.session_id or str(uuid4())

    if args.action:
        run_oneshot(args, session_id)
        return

    asyncio.run(
        connect_interactive(
            args.hub,
            args.model,
            args.mode,
            session_id,
            args.openclaw_jsonl,
            args.openclaw_ws,
            skills=parse_skills(args.skills),
            available_models=parse_available_models(args.available_models),
            reminders=parse_reminders(args.reminders_json),
            heartbeat_interval=args.heartbeat_interval,
        )
    )


if __name__ == "__main__":
    main()
