require('dotenv').config();
const fs = require('fs');
const path = require('path');
const { execSync, exec } = require('child_process');
const { createCanvas, loadImage, registerFont } = require('canvas');
const https = require('https');

// Paths
const ASSETS_DIR = path.resolve(__dirname, '../assets/sprites');
const TEMP_DIR = path.resolve(__dirname, '../temp');
const OUTPUT_DIR = path.resolve(__dirname, '../output');

// Ensure dirs
if (!fs.existsSync(TEMP_DIR)) fs.mkdirSync(TEMP_DIR, { recursive: true });
if (!fs.existsSync(OUTPUT_DIR)) fs.mkdirSync(OUTPUT_DIR, { recursive: true });

// Configuration
const FONT_SIZE = 40;
const FONT_FAMILY = 'Arial'; // Fallback

// Helper: Run command async
function runCommand(command) {
  return new Promise((resolve, reject) => {
    exec(command, (error, stdout, stderr) => {
      if (error) {
        console.error(`exec error: ${error}`);
        reject(error);
        return;
      }
      resolve(stdout.trim());
    });
  });
}

// Helper: Generate Audio via Fish Audio
async function generateAudio(text, filename) {
  const wavPath = path.join(TEMP_DIR, `${filename}.wav`);
  const apiKey = process.env.FISH_AUDIO_KEY;
  // Use a specific reference ID for Shutiao if available, otherwise use env default
  const refId = process.env.FISH_AUDIO_REF_ID || "7f92f8afb8ec43bf81429cc1c9199cb1"; // Fallback ID if env missing

  if (!apiKey) {
    console.warn("⚠️ Fish Audio Key missing! Falling back to macOS 'say' command.");
    execSync(`say -o "${wavPath}" --data-format=LEF32@24000 "${text}"`);
  } else {
    // Clean text for TTS (remove content in brackets)
    const cleanText = text.replace(/[\(\（].*?[\)\）]/g, '').trim();
    console.log(`🐟 Fish Audio generating: "${cleanText.substring(0, 15)}..." (Ref: ${refId})`);
    
    const payload = JSON.stringify({
      text: cleanText,
      reference_id: refId, // Restored!
      format: "wav",
      normalize: true,
      latency: "normal"
    });
    
    // Use curl for robustness
    const curlCmd = `curl -s -X POST https://api.fish.audio/v1/tts \
      -H "Authorization: Bearer ${apiKey}" \
      -H "Content-Type: application/json" \
      -d '${payload.replace(/'/g, "'\\''")}' \
      --output "${wavPath}"`;
      
    try {
      execSync(curlCmd);
    } catch (e) {
      console.error("Fish Audio API failed:", e);
      // Fallback
      execSync(`say -o "${wavPath}" "${text}"`);
    }
  }

  // Get duration
  try {
    const durationCmd = `ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "${wavPath}"`;
    const durationStr = execSync(durationCmd).toString().trim();
    const duration = parseFloat(durationStr);
    return { path: wavPath, duration };
  } catch (e) {
    console.error('Duration check error:', e);
    return { path: wavPath, duration: 2 }; // Fallback duration
  }
}

// Helper: Draw Frame (Image + Text Box)
async function drawFrame(spriteName, text, outputFilename) {
  const width = 1920;
  const height = 1080;
  const canvas = createCanvas(width, height);
  const ctx = canvas.getContext('2d');

  // 1. Load Sprite (Background is already fused)
  const spritePath = path.join(ASSETS_DIR, `shutiao_${spriteName}.png`);
  const image = await loadImage(spritePath);
  ctx.drawImage(image, 0, 0, width, height);

  // 2. Draw Text Box (Sleek UI)
  const boxHeight = 280;
  const boxY = height - boxHeight - 60;
  const boxX = 150;
  const boxWidth = width - 300;
  const radius = 20;

  // Gradient Background
  const gradient = ctx.createLinearGradient(boxX, boxY, boxX, boxY + boxHeight);
  gradient.addColorStop(0, 'rgba(20, 20, 35, 0.85)'); // Dark Blue-Grey Top
  gradient.addColorStop(1, 'rgba(10, 10, 20, 0.95)'); // Darker Bottom
  ctx.fillStyle = gradient;

  // Draw Rounded Rect
  ctx.beginPath();
  ctx.moveTo(boxX + radius, boxY);
  ctx.lineTo(boxX + boxWidth - radius, boxY);
  ctx.quadraticCurveTo(boxX + boxWidth, boxY, boxX + boxWidth, boxY + radius);
  ctx.lineTo(boxX + boxWidth, boxY + boxHeight - radius);
  ctx.quadraticCurveTo(boxX + boxWidth, boxY + boxHeight, boxX + boxWidth - radius, boxY + boxHeight);
  ctx.lineTo(boxX + radius, boxY + boxHeight);
  ctx.quadraticCurveTo(boxX, boxY + boxHeight, boxX, boxY + boxHeight - radius);
  ctx.lineTo(boxX, boxY + radius);
  ctx.quadraticCurveTo(boxX, boxY, boxX + radius, boxY);
  ctx.closePath();
  ctx.fill();

  // Subtle Border (Inner Glow effect)
  ctx.lineWidth = 2;
  ctx.strokeStyle = 'rgba(255, 215, 0, 0.3)'; // Faint Gold
  ctx.stroke();

  // 3. Draw Name Tag (No Emoji, Elegant)
  ctx.fillStyle = '#FFD700'; // Gold
  ctx.font = 'bold 36px Arial'; 
  ctx.fillText('薯条', boxX + 40, boxY + 60); // Emoji removed!

  // 4. Draw Text (Body)
  ctx.fillStyle = '#FFFFFF';
  ctx.font = '32px Arial'; // Slightly smaller for elegance
  const maxLineWidth = boxWidth - 80;
  const words = text.split('');
  let line = '';
  let y = boxY + 120;
  
  for (let i = 0; i < words.length; i++) {
    const testLine = line + words[i];
    const metrics = ctx.measureText(testLine);
    if (metrics.width > maxLineWidth && i > 0) {
      ctx.fillText(line, boxX + 30, y);
      line = words[i];
      y += 50;
    } else {
      line = testLine;
    }
  }
  ctx.fillText(line, boxX + 30, y);

  // Save
  const buffer = canvas.toBuffer('image/png');
  const outPath = path.join(TEMP_DIR, outputFilename);
  fs.writeFileSync(outPath, buffer);
  return outPath;
}

// Helper: Make Video Clip
function makeClip(imagePath, audioPath, duration, outputFilename) {
  const outPath = path.join(TEMP_DIR, outputFilename);
  // ffmpeg loop image for duration, add audio
  const cmd = `ffmpeg -y -loop 1 -i "${imagePath}" -i "${audioPath}" -c:v libx264 -t ${duration} -pix_fmt yuv420p -shortest "${outPath}"`;
  execSync(cmd);
  return outPath;
}

// Helper: Load Sprites from CSV
const CSV_PATH = path.resolve(__dirname, '../assets/production_plan.csv');
let SPRITE_DB = {};

function loadSprites() {
  try {
    const content = fs.readFileSync(CSV_PATH, 'utf8');
    const lines = content.trim().split('\n');
    // Skip header
    for (let i = 1; i < lines.length; i++) {
      const parts = lines[i].split(',');
      if (parts.length < 5) continue;
      // Schema: ID,Emotion,Variant,Description,Filename,...
      const emotion = parts[1].trim(); // e.g. "Happy"
      const filename = parts[4].trim(); // e.g. "shutiao_happy_v2.png"
      const status = parts[6] ? parts[6].trim() : 'Done';
      
      const fullPath = path.join(ASSETS_DIR, filename);
      if (status === 'Done' && fs.existsSync(fullPath)) {
        if (!SPRITE_DB[emotion]) SPRITE_DB[emotion] = [];
        SPRITE_DB[emotion].push(filename);
      }
    }
    console.log(`📚 Sprite DB Loaded: ${Object.keys(SPRITE_DB).map(k => `${k}(${SPRITE_DB[k].length})`).join(', ')}`);
  } catch (e) {
    console.error("Failed to load sprite CSV:", e);
  }
}

// Helper: Get Random Sprite by Emotion
function getSprite(emotion) {
  const list = SPRITE_DB[emotion];
  if (!list || list.length === 0) {
    // Fallback logic
    if (emotion === 'Base') return 'shutiao_base.png';
    console.warn(`⚠️ No sprites found for emotion: ${emotion}, using Base.`);
    return 'shutiao_base.png';
  }
  // Random pick
  const pick = list[Math.floor(Math.random() * list.length)];
  // Remove "shutiao_" prefix and ".png" suffix because drawFrame expects "spriteName"
  // Wait, drawFrame uses: path.join(ASSETS_DIR, `shutiao_${spriteName}.png`);
  // But our CSV has full filenames like "shutiao_happy_v2.png".
  // We need to adapt either drawFrame or this return.
  // Let's adapt this return to match drawFrame's expectation: 
  // It expects "happy_v2" if file is "shutiao_happy_v2.png".
  return pick.replace(/^shutiao_/, '').replace(/\.png$/, '');
}

// Main
async function main() {
  loadSprites(); // Init DB
  console.log('🎬 Action!');
  
  // The Grand Demo Script
  const script = [
    { text: "老板老板！新年快乐！(比心) 祝您在新的一年里...", emotion: "Happy" }, 
    { text: "财源滚滚，代码无 Bug，身体倍儿棒！(兴奋)", emotion: "Happy" },
    { text: "对了，新的一年也要记得给薯条加鸡腿哦！(灵光)", emotion: "Think" }, 
    { text: "愛你哟！Happy New Year! (招手)", emotion: "Action" }
  ];

  // Parallel Processing with Concurrency Limit (Max 3)
  console.log('🚀 Starting parallel rendering (Max 3 concurrent)...');
  const CONCURRENCY = 3;
  const results = [];

  // Helper to process a single line
  const processLine = async (line, i) => {
    const spriteName = getSprite(line.emotion);
    console.log(`Processing line ${i+1}: [${line.emotion}] -> ${spriteName}`);
    const audioPromise = generateAudio(line.text, `line_${i}`);
    const imagePromise = drawFrame(spriteName, line.text, `frame_${i}.png`);
    const [audio, imagePath] = await Promise.all([audioPromise, imagePromise]);
    const clipPath = makeClip(imagePath, audio.path, audio.duration + 0.3, `clip_${i}.mp4`);
    return { index: i, path: clipPath };
  };

  // Execution Queue
  for (let i = 0; i < script.length; i += CONCURRENCY) {
    const chunk = script.slice(i, i + CONCURRENCY);
    console.log(`--- Processing Chunk ${i/CONCURRENCY + 1} (${chunk.length} items) ---`);
    const chunkPromises = chunk.map((line, idx) => processLine(line, i + idx));
    const chunkResults = await Promise.all(chunkPromises);
    results.push(...chunkResults);
  }

  // Sort by index to ensure order
  const clips = results.sort((a, b) => a.index - b.index).map(r => r.path);

  // 4. Concat
  console.log('Merging clips...');
  const listPath = path.join(TEMP_DIR, 'list.txt');
  const fileContent = clips.map(c => `file '${c}'`).join('\n');
  fs.writeFileSync(listPath, fileContent);

  const finalPath = path.join(OUTPUT_DIR, 'final_mvp.mp4');
  execSync(`ffmpeg -y -f concat -safe 0 -i "${listPath}" -c copy "${finalPath}"`);

  console.log('🎉 Cut! Video is ready:', finalPath);
}

main();
