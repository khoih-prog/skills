<h1 align="center">🔧 FLock Model Switcher</h1>
 
<p align="center">
  <strong>ClawHub Skill for OpenClaw</strong>
</p>

<p align="center">
  <a href="https://www.clawhub.ai"><img src="https://img.shields.io/badge/ClawHub-skill-orange" alt="ClawHub Skill"></a>
  <a href="https://github.com/createpjf/openclaw-flock-api-platform"><img src="https://img.shields.io/badge/FLock-Plugin-blue" alt="FLock Plugin"></a>
  <a href="https://docs.flock.io/flock-products/api-platform/api-endpoint"><img src="https://img.shields.io/badge/FLock-API%20Docs-green" alt="FLock API Docs"></a>
  <a href="./LICENSE"><img src="https://img.shields.io/badge/License-Apache%202.0-brightgreen" alt="License"></a>
</p>

<p align="center">
  Quickly switch between FLock API Platform models during agent conversations.<br/>
  No need to leave the chat — just pick the right model for the task.
</p>

---

## What is This?

A **ClawHub skill** that gives you a quick reference for all available [FLock API Platform](https://docs.flock.io/flock-products/api-platform/api-endpoint) models, with pricing, switching commands, and a selection guide — all accessible mid-conversation.

**Use it when you want to:**

- Switch to a different FLock model without leaving the chat
- Pick a reasoning model for complex tasks, or a fast instruct model for simple ones
- Compare outputs across different models
- Check which models are available and how much they cost

> **Requires:** [openclaw-flock-api-platform](https://github.com/createpjf/openclaw-flock-api-platform) plugin installed and configured.

---

## Available Models

### Reasoning / Thinking Models

Best for complex analysis, step-by-step reasoning, and deep thinking tasks.

| Model ID | Name | Input / Output (per 1M tokens) |
|---|---|---|
| `qwen3-235b-a22b-thinking-2507` | Qwen3 235B Thinking | $0.23 / $2.30 |
| `qwen3-235b-a22b-thinking-qwfin` | Qwen3 235B Thinking (Finance) | $0.23 / $2.30 |
| `kimi-k2-thinking` | Kimi K2 Thinking | $0.60 / $2.50 |

### Instruct / Chat Models

Best for general-purpose chat, coding, and instruction-following tasks.

| Model ID | Name | Input / Output (per 1M tokens) |
|---|---|---|
| `qwen3-30b-a3b-instruct-2507` | Qwen3 30B Instruct | $0.20 / $0.80 |
| `qwen3-235b-a22b-instruct-2507` | Qwen3 235B Instruct | $0.70 / $2.80 |
| `qwen3-30b-a3b-instruct-qmxai` | Qwen3 30B Instruct (QMX) | $0.20 / $0.80 |
| `qwen3-30b-a3b-instruct-coding` | Qwen3 30B Instruct (Coding) | $0.20 / $0.80 |
| `qwen3-30b-a3b-instruct-qmini` | Qwen3 30B Instruct (Mini) | $0.20 / $0.80 |

### Other Models

| Model ID | Name | Input / Output (per 1M tokens) |
|---|---|---|
| `deepseek-v3.2` | DeepSeek V3.2 | $0.28 / $0.42 |
| `deepseek-v3.2-dsikh` | DeepSeek V3.2 (DSIKH) | $0.28 / $0.42 |
| `minimax-m2.1` | MiniMax M2.1 | $0.30 / $1.20 |

> All models: **131,072** token context window · **8,192** max output tokens

---

## Quick Start

### 1. Install the FLock Plugin (if not already)

```bash
openclaw plugins install @openclawd/flock
openclaw plugins enable flock
openclaw models auth login --provider flock
```

### 2. Switch Models

```bash
# Reasoning model for complex analysis
openclaw agent --model flock/qwen3-235b-a22b-thinking-2507

# Fast & cheap for simple tasks
openclaw agent --model flock/qwen3-30b-a3b-instruct-2507

# Coding-optimized
openclaw agent --model flock/qwen3-30b-a3b-instruct-coding

# Cost-effective general use
openclaw agent --model flock/deepseek-v3.2
```

---

## Model Selection Guide

| Scenario | Recommended Model |
|---|---|
| Deep reasoning / step-by-step analysis | `flock/qwen3-235b-a22b-thinking-2507` |
| Financial analysis | `flock/qwen3-235b-a22b-thinking-qwfin` |
| General-purpose chat | `flock/qwen3-30b-a3b-instruct-2507` |
| Code generation / debugging | `flock/qwen3-30b-a3b-instruct-coding` |
| Most capable instruct model | `flock/qwen3-235b-a22b-instruct-2507` |
| Budget-friendly | `flock/deepseek-v3.2` ($0.28/$0.42) |

---

## Advanced Configuration

<details>
<summary><strong>Set default model in config</strong></summary>

Edit `~/.openclaw/config.yaml`:

```yaml
models:
  default: flock/qwen3-30b-a3b-instruct-2507
  providers:
    flock:
      baseUrl: https://api.flock.io/v1
      api: openai-completions
```

</details>

<details>
<summary><strong>Per-channel model override</strong></summary>

```yaml
channels:
  telegram:
    model: flock/qwen3-30b-a3b-instruct-2507
  discord:
    model: flock/qwen3-235b-a22b-thinking-2507
  whatsapp:
    model: flock/deepseek-v3.2
```

</details>

---

## Troubleshooting

| Problem | Solution |
|---|---|
| Model not found | Verify plugin enabled: `openclaw plugins list` |
| Auth error | Re-authenticate: `openclaw models auth login --provider flock` |
| Slow responses | Switch from 235B to 30B variant, or use DeepSeek V3.2 |
| API errors | Check API key validity and FLock platform status |

---

## Links

- **FLock Plugin:** [createpjf/openclaw-flock-api-platform](https://github.com/createpjf/openclaw-flock-api-platform)
- **FLock API Docs:** [docs.flock.io](https://docs.flock.io/flock-products/api-platform/api-endpoint)
- **ClawHub:** [clawhub.ai](https://www.clawhub.ai)

## License

Apache 2.0 — see [LICENSE](./LICENSE) for details.
