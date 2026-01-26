# Plaud API Claude Skill

A Claude Code skill for accessing Plaud voice recorder data (recordings, transcripts, AI summaries).

## Installation

### Option 1: Symlink (Recommended for Development)

```bash
ln -s /path/to/plaud-api-reveng/skills/plaud-api ~/.claude/skills/plaud-api
```

### Option 2: Copy

```bash
cp -r /path/to/plaud-api-reveng/skills/plaud-api ~/.claude/skills/
```

## Quick Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Follow the credential tutorial in `SKILL.md` to obtain your Plaud API token

3. Update `.env` with your actual credentials

4. Test with:
   ```bash
   python plaud_client.py list
   ```

## Usage

In Claude Code, use:
- `/plaud-api` - Full skill with setup tutorial
- `/plaud` - Alias
- `/plaud-recordings` - Alias

## Requirements

The skill requires the `plaud_client.py` tool from the main repo. Make sure you have:
- Python 3.x
- `requests` and `python-dotenv` packages

Install dependencies:
```bash
pip install requests python-dotenv
```

## Related Resources

- [plaud-api-reveng repo](https://github.com/your-username/plaud-api-reveng) - Full tooling and API documentation
- `PLAUD_API.md` - Detailed API documentation
- `plaud_client.py` - CLI tool for Plaud API access
