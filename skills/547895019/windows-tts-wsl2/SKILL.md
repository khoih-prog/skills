---
name: windows-tts
description: Speak text out loud on Windows 11 from inside WSL2/TUI using Windows built-in TTS (System.Speech). Use when the user asks for Chinese voice playback, wants the assistant to "directly play sound" on the PC, or when OpenClaw's built-in tts voice does not support Chinese.
---

# Windows TTS (WSL2)

Use Windows built-in TTS via `powershell.exe` so audio plays through the Windows sound device (WSLg PulseAudio is not required).

## Quick start (speak Chinese)

Run from WSL:

```bash
bash {baseDir}/scripts/saycn.sh "你好，我是你的助手。"
```

## List installed voices

```bash
bash {baseDir}/scripts/list_voices.sh
```

## Speak with a specific voice

```bash
bash {baseDir}/scripts/saycn.sh --voice "VOICE_NAME" "你好，我以后会用这个声音说话。"
```

## Notes

- If you embed PowerShell directly in bash, remember: **escape `$`** or use outer single quotes; otherwise bash expands `$s` and breaks the command.
- If the user reports errors like `=New-Object` or `TypeName:` prompts, prefer the provided scripts instead of ad-hoc quoting.
