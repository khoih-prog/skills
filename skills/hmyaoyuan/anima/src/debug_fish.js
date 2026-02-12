require('dotenv').config({ path: require('path').resolve(__dirname, '../../../.env') });
const { execSync } = require('child_process');

const KEY = process.env.FISH_AUDIO_KEY;
const REF_ID = "987d788609404c7497a26b5fe7c0184d";

console.log("Testing Ref ID:", REF_ID);
console.log("Using Key:", KEY ? KEY.substring(0, 5) + "..." : "MISSING");

const payload = JSON.stringify({
  text: "测试音频，如果不响就是 ID 错了。",
  reference_id: REF_ID,
  format: "wav"
});

try {
  const cmd = `curl -s -X POST https://api.fish.audio/v1/tts \
    -H "Authorization: Bearer ${KEY}" \
    -H "Content-Type: application/json" \
    -d '${payload}'`;
    
  const res = execSync(cmd).toString();
  console.log("API Response:", res);
} catch (e) {
  console.error("Exec Error:", e);
}
