# openclaw-deck-tracker

An [OpenClaw](https://openclaw.ai) skill to track tasks on a NextCloud Deck board.

## Features

- **Queue -> In Progress -> Done** workflow
- Move cards between stacks easily
- Auto-fail-safe API calls (handles server timeout/downtime)

## Installation

1.  Clone this repo into your OpenClaw skills directory:
    ```bash
    cd ~/.openclaw/workspace/skills
    git clone https://github.com/SkanderHelali/openclaw-deck-tracker.git deck-tracker
    ```

2.  Make the script executable:
    ```bash
    chmod +x deck-tracker/bin/deck
    ```

3.  Configure your environment variables (see below).

## Configuration

Add these to your shell profile or OpenClaw service config:

```bash
export DECK_URL="https://your-nextcloud.com/index.php/apps/deck/api/v1.0"
export DECK_USER="your_username"
export DECK_PASS="your_app_password" # Use an App Password!
export BOARD_ID=1
```

### Optional Stack ID Overrides

If your board stacks aren't 1, 2, 3, 4:

```bash
export STACK_QUEUE=10
export STACK_PROGRESS=11
export STACK_WAITING=12
export STACK_DONE=13
```

## Usage

Use inside OpenClaw:

```bash
deck list
deck add "New Task"
deck move <id> progress
deck move <id> done
```
