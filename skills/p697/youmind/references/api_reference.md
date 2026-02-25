# Youmind Skill API Reference

All commands should be run with `run.py`:

```bash
python scripts/run.py [script].py [args...]
```

## `ask_question.py`

Ask a question to Youmind board chat.

```bash
python scripts/run.py ask_question.py --question "Your question"
python scripts/run.py ask_question.py --question "..." --board-id board-id
python scripts/run.py ask_question.py --question "..." --board-url "https://youmind.com/boards/..."
python scripts/run.py ask_question.py --question "..." --show-browser
```

Parameters:
- `--question` (required)
- `--board-id` (optional)
- `--board-url` (optional)
- `--show-browser` (optional)

## `board_manager.py`

Manage local board library.

```bash
python scripts/run.py board_manager.py add --url URL --name NAME --description DESC --topics TOPICS
python scripts/run.py board_manager.py smart-add --url URL
python scripts/run.py board_manager.py list
python scripts/run.py board_manager.py search --query QUERY
python scripts/run.py board_manager.py activate --id ID
python scripts/run.py board_manager.py remove --id ID
python scripts/run.py board_manager.py stats
```

`smart-add` options:
- `--url` (required)
- `--show-browser` (optional)
- `--prompt` (optional custom summary prompt, pass 1)
- `--json-prompt` (optional custom structured prompt, pass 2)
- `--single-pass` (optional; disable two-pass discovery)
- `--no-activate` (optional)
- `--allow-duplicate-url` (optional)

## `auth_manager.py`

Manage Youmind login state.

```bash
python scripts/run.py auth_manager.py setup
python scripts/run.py auth_manager.py status
python scripts/run.py auth_manager.py validate
python scripts/run.py auth_manager.py reauth
python scripts/run.py auth_manager.py clear
```

## `cleanup_manager.py`

Cleanup local state.

```bash
python scripts/run.py cleanup_manager.py
python scripts/run.py cleanup_manager.py --confirm
python scripts/run.py cleanup_manager.py --confirm --preserve-library
python scripts/run.py cleanup_manager.py --confirm --force
```

## Data Layout

```text
data/
├── library.json
├── auth_info.json
└── browser_state/
    └── state.json
```

## Python Usage

```python
import subprocess

result = subprocess.run([
    "python", "scripts/run.py", "ask_question.py",
    "--question", "Summarize this board",
    "--board-id", "product-notes"
], capture_output=True, text=True)

print(result.stdout)
```
