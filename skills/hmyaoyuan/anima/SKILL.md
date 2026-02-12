---
description: Anima Avatar - Interactive Video Generation Engine. Generates 16:9 videos with dynamic character sprites (Shutiao), synced audio (Fish Audio), and text overlay.
---

# Anima Avatar (Project Anima)

Generates high-quality interactive videos where Shutiao speaks the text with appropriate expressions, gestures, and voice.

## 🌟 Capabilities
- **True Voice**: Uses Fish Audio API (custom model `aa88...`) for realistic speech.
- **Dynamic Sprites**: Auto-selects from a library of 30+ sprites (Happy, Angry, Shy, Think, Action) based on emotion tags.
- **Smart Director**: Handles parallel generation, audio-sync, and video composition (FFmpeg).
- **Pro Delivery**: Uploads as native stream to Feishu for direct playback (with correct duration).

## 📂 Structure
- `src/director.js`: The core engine. Edits script here to generate video.
- `src/send_video_pro.js`: Delivery script. Handles transcoding, duration calculation, and Feishu upload.
- `assets/sprites/`: The sprite library (1K resolution).
- `assets/production_plan.csv`: The asset registry and generation prompts.
- `output/`: Generated videos (`final_mvp.mp4`).

## 🛠️ Setup & Requirements

### 1. System Dependencies
This skill requires `ffmpeg` for video processing.
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg`
- **Windows**: Download/Install FFmpeg and add to PATH.

### 2. Node Dependencies
Install package dependencies inside the skill folder:
```bash
cd skills/anima
npm install
```

### 3. Environment Configuration
Create a `.env` file in your workspace root (or parent directory):
```ini
# Fish Audio (Required for default TTS)
# Get Key: https://fish.audio/dashboard/api
FISH_AUDIO_KEY=your_sk_key_here
FISH_AUDIO_REF_ID=your_model_id_here

# Feishu/Lark (Required for Pro Delivery)
FEISHU_APP_ID=cli_...
FEISHU_APP_SECRET=...
```

## 🧩 Extension: Custom TTS

To use a different TTS provider (e.g., OpenAI, ElevenLabs):

1.  Open `src/director.js`.
2.  Locate the `generateAudio(text, filename)` function.
3.  Replace the Fish Audio API call with your provider's logic.
4.  **Contract**: The function must return an object: `{ path: "/path/to/audio.wav", duration: 1.5 }` (duration in seconds).

Example (Pseudocode):
```javascript
async function generateAudio(text, filename) {
  // Call OpenAI TTS...
  // Save to skills/anima/temp/${filename}.mp3
  // Convert to WAV if needed
  return { path: wavPath, duration: audioDuration };
}
```

## 🔄 Advanced: How to Change Character / Background
Modify the `script` array in `skills/anima/src/director.js`:
```javascript
const script = [
  { text: "Boss! Happy New Year! (Heart)", emotion: "Happy" },
  { text: "I am working hard! (Fist)", emotion: "Action" }
];
```

### 3. Generate & Send
Run the one-liner workflow:
```bash
node skills/anima/src/director.js && \
ffmpeg -y -i skills/anima/output/final_mvp.mp4 -c:v libx264 -c:a aac -movflags +faststart skills/anima/output/final_fixed_voice.mp4 && \
node skills/anima/src/send_video_pro.js
```

## 🔄 Advanced: How to Change Character / Background

To create a new avatar (e.g., "Maimai"):

1.  **Prepare Base Image**:
    *   Create a 1920x1080 (1K) image of the new character in the desired background.
    *   Save it as `assets/sprites/maimai_base_1k.png`.

2.  **Update CSV Plan**:
    *   Open `assets/production_plan.csv`.
    *   **Option A (Replace)**: Delete all rows except header, and write new rows for "Maimai".
    *   **Option B (Append)**: Add new rows with `Filename` like `maimai_happy.png`.
    *   **Important**: Update the `Base Image (Input)` column to point to `maimai_base_1k.png`.

3.  **Run Batch Generator**:
    *   Edit `src/batch_generator.js` to point `BASE_IMG` to the new base image.
    *   Run `node src/batch_generator.js`.
    *   It will generate all variants for the new character.

4.  **Director Usage**:
    *   In `director.js`, update `loadSprites` logic or simply use the new filenames in your script logic if manually specifying, or ensure `production_plan.csv` is clean (only contains current character) for auto-selection to work correctly.

## 🎨 Asset Management
To add new sprites:
1. Update `assets/production_plan.csv` with new prompts.
2. Run `src/batch_generator.js` (or manual `uv run` command).
3. Ensure file naming follows `shutiao_<emotion>_<variant>.png`.

## 🛠 Troubleshooting
- **Duration 00:00**: Ensure `send_video_pro.js` calculates duration in **ms** and passes it to both upload and message payload.
- **Fish Audio 400**: Check Ref ID matches API Key owner.
- **Video Black**: Check `ffmpeg` transcoding logs.
