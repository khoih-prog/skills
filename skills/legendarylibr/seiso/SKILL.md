---
name: seisoai
description: "Generate images, videos, music, 3D models, and audio via SeisoAI (120+ tools). Pay-per-request with x402 USDC on Base. Use when user asks to generate, edit, upscale, or train AI content."
homepage: https://seisoai.com
version: 2.1.0
last_synced: 2026-02-15
files: ["scripts/x402-sign.mjs", "scripts/package.json"]
metadata: {"openclaw": {"emoji": "🎨", "homepage": "https://seisoai.com", "requires": {"bins": ["curl", "node"], "env": ["SEISOAI_WALLET_KEY"]}, "primaryEnv": "SEISOAI_WALLET_KEY"}}
---

# SeisoAI

120+ AI generation tools. Payment: x402 USDC on Base.

## Setup

### `SEISOAI_WALLET_KEY`

x402 signing key — used only to authorize per-request USDC payments to SeisoAI via EIP-3009 `transferWithAuthorization`. The key never leaves your machine; the signing script hard-codes SeisoAI's recipient address and rejects any other payTo.

Use a dedicated wallet with a small USDC balance ($5–$20). Most generations cost $0.01–$0.33.

```bash
export SEISOAI_WALLET_KEY="0x<key>"
```

### Dependencies

```bash
cd {baseDir}/scripts && npm ci --ignore-scripts
```

Pinned via lockfile. Run once before first use.

## Discovery

```bash
curl -s "https://seisoai.com/api/gateway/tools"
curl -s "https://seisoai.com/api/gateway/tools/{toolId}"
curl -s "https://seisoai.com/api/gateway/price/{toolId}"
```

## Invoke (full x402 flow)

### Step 1: Send request, capture 402 challenge

```bash
CHALLENGE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "https://seisoai.com/api/gateway/invoke/{toolId}" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "..."}')
# Expect HTTP 402. Capture the full body:
BODY=$(curl -s -X POST "https://seisoai.com/api/gateway/invoke/{toolId}" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "..."}')
echo "$BODY"
```

The 402 response contains a standard x402 payment challenge:

```json
{
  "x402Version": 2,
  "error": "Payment required",
  "resource": { "url": "...", "description": "...", "mimeType": "application/json" },
  "accepts": [{
    "scheme": "exact",
    "network": "eip155:8453",
    "maxAmountRequired": "32500",
    "asset": "USDC",
    "payTo": "0xa0aE05e2766A069923B2a51011F270aCadFf023a",
    "extra": { "priceUsd": "$0.0325" }
  }]
}
```

The `PAYMENT-REQUIRED` response header contains the same payload base64-encoded.

### Step 2: Display payment to user, get approval

Parse `accepts[0]` from the 402 JSON. Show the user:
- Tool name and what it does
- `asset`: USDC
- Amount: `maxAmountRequired` (divide by 1000000 for human-readable USD)
- Recipient (`payTo`): `0xa0aE05e2766A069923B2a51011F270aCadFf023a` (SeisoAI)
- Network: Base (`eip155:8453`)

**Wait for explicit user approval. Never auto-approve.**

### Step 3: Sign and retry

```bash
PAYMENT=$(echo "$BODY" | node {baseDir}/scripts/x402-sign.mjs)

curl -s -X POST "https://seisoai.com/api/gateway/invoke/{toolId}" \
  -H "Content-Type: application/json" \
  -H "payment-signature: $PAYMENT" \
  -d '{"prompt": "..."}'
```

The request body MUST be identical to step 1.

### Step 4: Handle response

**Sync** (`executionMode: "sync"`): result is in the response body, with settlement info:

```json
{
  "success": true,
  "result": { ... },
  "x402": {
    "settled": true,
    "transactionHash": "0x...",
    "amount": "32500",
    "status": "settled"
  },
  "x402_amount": "32500",
  "x402_status": "settled",
  "x402_confirmation_id": "...",
  "x402_timestamp": "2025-06-15T00:00:00.000Z",
  "x402_recipient": "0xa0aE05e2766A069923B2a51011F270aCadFf023a"
}
```

**Queue** (`executionMode: "queue"`): poll every 5s:

```bash
curl -s "https://seisoai.com/api/gateway/jobs/{jobId}?model={model}"
curl -s "https://seisoai.com/api/gateway/jobs/{jobId}/result?model={model}"
```

## Result fields

| Type | Field | Fallback |
|------|-------|----------|
| Image | `result.images[0].url` | `result.images[0]` |
| Video | `result.video.url` | `result.video_url` |
| Audio | `result.audio.url` | `result.audio_url` |
| 3D | `result.model_glb.url` | `result.model_mesh.url` |

## Error handling

| HTTP | Action |
|------|--------|
| 402 | Normal — parse, sign, retry (steps above) |
| 402 + "already used" | Fresh signature, retry |
| 400 | Check payload vs tool schema (`GET /tools/{toolId}`) |
| 429 | Wait `Retry-After` seconds |
| 500 | Retry with backoff |

## Tools (120+ total)

### Image Generation (19)
`image.generate.flux-pro-kontext` $0.065 · `image.generate.flux-2` $0.03 · `image.generate.flux-2-flex` $0.03 · `image.generate.flux-2-klein-realtime` $0.016 · `image.generate.nano-banana-pro` $0.33 (360°) · `image.generate.flux-controlnet-canny` $0.065 · `image.generate.grok-imagine` $0.05 · `image.generate.kling-image-v3` $0.06 · `image.generate.kling-image-o3` $0.065 · `image.generate.hunyuan-instruct` $0.05 · `image.generate.qwen-image-max` $0.04 · `image.generate.bria-fibo` $0.05 · `image.generate.seedream-4` $0.05 · `image.generate.recraft-v3` $0.05 (SOTA, vector) · `image.generate.omnigen-v2` $0.05 (try-on, multi-modal) · `image.generate.pulid` $0.04 (face ID) · `image.generate.imagineart` $0.05 · `training.lora-inference` $0.04

### Image Editing (15)
`image.generate.flux-pro-kontext-edit` $0.065 · `image.generate.flux-pro-kontext-multi` $0.065 · `image.generate.flux-2-edit` $0.03 · `image.edit.flux-2-flex` $0.03 (multi-ref) · `image.generate.nano-banana-pro-edit` $0.33 · `image.edit.grok-imagine` $0.05 · `image.edit.seedream-4` $0.05 · `image.edit.recraft-v3` $0.05 · `image.edit.kling-image-v3` $0.06 · `image.edit.kling-image-o3` $0.065 · `image.edit.bria-fibo` $0.05 · `image.edit.reve` $0.05 · `image.face-swap` $0.03 · `image.inpaint` $0.04 · `image.outpaint` $0.04

### Image Processing (9)
`image.upscale` $0.04 · `image.upscale.topaz` $0.065 (premium) · `image.extract-layer` $0.01 · `image.background-remove` $0.01 · `image.segment.sam2` $0.01 · `image.depth.depth-anything-v2` $0.01 · `image.generate.genfocus` $0.03 · `image.generate.genfocus-all-in-focus` $0.03

### Vision (3)
`vision.describe` $0.01 · `vision.describe.florence-2` $0.01 (OCR, detection) · `vision.nsfw-detect` $0.007

### Video Generation (29) — per second
`video.generate.veo3` $0.13/s · `video.generate.veo3-image-to-video` $0.13/s · `video.generate.veo3-first-last-frame` $0.13/s · `video.generate.veo3-reference` $0.13/s · `video.generate.sora-2-text` $0.20/s · `video.generate.sora-2-image` $0.20/s · `video.generate.sora-2-pro-text` $0.26/s · `video.generate.sora-2-pro-image` $0.26/s · `video.generate.ltx-2-19b-image` $0.13/s · `video.generate.kling-3-pro-text` $0.20/s · `video.generate.kling-3-pro-image` $0.20/s · `video.generate.kling-3-std-text` $0.16/s · `video.generate.kling-3-std-image` $0.16/s · `video.generate.kling-o3-image` $0.18/s · `video.generate.kling-o3-reference` $0.18/s · `video.generate.kling-o3-pro-text` $0.23/s · `video.generate.kling-o3-pro-image` $0.23/s · `video.generate.kling-o3-pro-reference` $0.23/s · `video.generate.kling-o3-std-text` $0.18/s · `video.generate.grok-imagine-text` $0.16/s · `video.generate.grok-imagine-image` $0.16/s · `video.generate.vidu-q3-text` $0.18/s · `video.generate.vidu-q3-image` $0.18/s · `video.generate.wan-2.6-reference` $0.09/s · `video.generate.dreamactor-v2` $0.13/s · `video.generate.pixverse-v5` $0.13/s · `video.generate.lucy-14b` $0.10/s · `audio.lip-sync` $0.05

### Video Editing (10)
`video.animate.wan` $0.065/s · `video.edit.grok-imagine` $0.13/s · `video.edit.sora-2-remix` $0.20/s · `video.edit.kling-o3-std` $0.18/s · `video.edit.kling-o3-pro` $0.23/s · `video.generate.kling-o3-std-reference` $0.18/s · `video.generate.kling-o3-pro-reference` $0.23/s · `video.upscale.topaz` $0.13/s · `video.background-remove` $0.04/s

### Avatar & Lip Sync (6)
`avatar.creatify-aurora` $0.13/s · `avatar.veed-fabric` $0.13/s · `avatar.omnihuman-v15` $0.13/s · `avatar.ai-text` $0.10/s · `avatar.sync-lipsync-v2` $0.065/s · `avatar.pixverse-lipsync` $0.065/s

### Audio Generation (10)
`audio.tts` $0.03 · `audio.tts.minimax-hd` $0.04 · `audio.tts.minimax-turbo` $0.03 · `audio.tts.chatterbox` $0.03 · `audio.tts.dia-voice-clone` $0.04 · `audio.personaplex` $0.05 · `audio.kling-video-to-audio` $0.05 · `audio.sfx` $0.04 · `audio.sfx.stable-audio` $0.04 · `audio.sfx.beatoven` $0.04 · `audio.sfx.mirelo-video` $0.04 · `video.video-to-audio` $0.04

### Audio Processing (2)
`audio.transcribe` $0.01 · `audio.stem-separation` $0.04

### Music (2)
`music.generate` $0.03/min · `music.generate.beatoven` $0.04/min (royalty-free)

### 3D Generation (9)
`3d.image-to-3d` $0.065 · `3d.image-to-3d.hunyuan-pro` $0.13 · `3d.text-to-3d.hunyuan-pro` $0.16 · `3d.image-to-3d.hunyuan-rapid` $0.05 · `3d.text-to-3d.hunyuan-rapid` $0.065 · `3d.smart-topology` $0.04 · `3d.part-splitter` $0.04 · `3d.image-to-3d.meshy-v6` $0.10 · `3d.text-to-3d.meshy-v6` $0.10

### Training (12) — per step
`training.flux-lora` $0.004/step · `training.flux-2` $0.007/step · `training.flux-2-v2` $0.007/step · `training.flux-kontext` $0.005/step · `training.flux-portrait` $0.005/step · `training.flux-2-klein-4b` $0.004/step · `training.flux-2-klein-9b` $0.005/step · `training.qwen-image` $0.007/step · `training.qwen-image-edit` $0.007/step · `training.wan-video` $0.007/step · `training.wan-22-image` $0.005/step · `training.z-image` $0.004/step

### Workflow Utilities (5)
`utility.trim-video` $0.007 · `utility.blend-video` $0.007 · `utility.extract-frame` $0.007 · `utility.audio-compressor` $0.007 · `utility.impulse-response` $0.007

## Claude API Features

The chat assistant supports these advanced Anthropic API capabilities:

- **Web Search** (`web_search_20250305`): Claude searches the web for real-time info, auto-cites sources. Great for creative research.
- **Code Execution** (`code_execution_20250825`): Claude runs Python/Bash in a sandbox for data analysis, calculations, and visualizations.
- **Citations**: Claude cites specific passages from provided documents for source-grounded responses.
- **Prompt Caching**: System prompts cached up to 1 hour for reduced costs on repeated conversations.
- **Message Batches**: Process up to 10,000 requests at 50% lower cost for bulk operations.

## Notes

- `GET /api/gateway/tools/{toolId}` returns the full input schema — check before invoking.
- Payment signatures are one-time use. Never reuse between requests.
- Request body must be identical between 402 challenge and paid retry.
- Cheapest image: `flux-2-klein-realtime` ($0.016). Cheapest video: `wan-2.6-reference` ($0.09/s).
- The signing script requires `SEISOAI_WALLET_KEY` — see **Setup** above.
- The script only authorizes payments to SeisoAI's hard-coded address; any other payTo is rejected.
