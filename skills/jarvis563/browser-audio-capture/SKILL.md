---
name: browser-audio-capture
description: Capture audio from browser tabs (Zoom, Google Meet, Teams, etc.) via Chrome CDP and stream to a local transcription pipeline. Zero API keys, 100% local.
version: 1.0.0
---

# Browser Audio Capture

Capture tab audio from any browser-based meeting and stream PCM16 audio to a local endpoint for transcription.

## Prerequisites

Chrome must be running with remote debugging enabled:

```bash
# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=$HOME/.chrome-debug-profile &
```

Python 3.9+ with `aiohttp` installed:

```bash
pip install aiohttp
```

## Quick Start

### List tabs and detect meetings

```bash
python3 -m browser_capture.cli tabs
```

Flags meeting tabs (Zoom, Meet, Teams, Webex, etc.) with 🎙️.

### Capture a tab

```bash
# Auto-detect meeting tab
python3 -m browser_capture.cli capture

# Specific tab
python3 -m browser_capture.cli capture --tab <TAB_ID>
```

### Auto-detect mode

```bash
python3 -m browser_capture.cli watch --interval 15
```

Continuously watches for meeting tabs and starts capture automatically.

### Stop / Status

```bash
python3 -m browser_capture.cli status
python3 -m browser_capture.cli stop
```

## Chrome Extension (fully automated)

For zero-interaction capture, install the bundled Chrome extension:

1. `chrome://extensions/` → Developer mode → Load unpacked
2. Select `scripts/extension/`
3. Click the Percept icon on any meeting tab → Start Capturing

The extension uses `chrome.tabCapture` (no screen picker needed) and persists via an offscreen document after popup closes.

## Audio Output

Audio streams as JSON POST to `http://127.0.0.1:8900/audio/browser`:

```json
{
  "sessionId": "browser_1234567890",
  "audio": "<base64 PCM16>",
  "sampleRate": 16000,
  "format": "pcm16",
  "source": "browser_extension",
  "tabUrl": "https://meet.google.com/abc-defg-hij",
  "tabTitle": "Meeting Title"
}
```

Configure the endpoint URL in `scripts/extension/offscreen.js` (`PERCEPT_URL` constant).

## Detected Meeting Platforms

Google Meet, Zoom (web), Microsoft Teams, Webex, Whereby, Around, Cal.com, Riverside, StreamYard, Ping, Daily.co, Jitsi, Discord.

## Troubleshooting

- **No tabs found**: Ensure Chrome launched with `--remote-debugging-port=9222`
- **Extension button won't click**: Reload extension on `chrome://extensions/`. MV3 requires external JS files (no inline scripts)
- **Audio not arriving**: Check receiver is running on port 8900. Extension sends to `/audio/browser` (JSON), not `/audio` (multipart)
- **Capture stops when popup closes**: Expected with CDP method. Use the Chrome extension for persistent capture (offscreen document survives popup close)
