const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Simple CSV Parser/Writer
const CSV_PATH = path.resolve(__dirname, '../assets/production_plan.csv');
const BASE_IMG = path.resolve(__dirname, '../assets/sprites/shutiao_base_1k.png'); // Use 1K base for stability

function readCSV() {
  const content = fs.readFileSync(CSV_PATH, 'utf8');
  const lines = content.trim().split('\n');
  const headers = lines[0].split(',');
  return lines.slice(1).map(line => {
    const values = line.split(',');
    return headers.reduce((obj, header, index) => {
      obj[header] = values[index] ? values[index].trim() : ''; // Basic trim safety
      return obj;
    }, {});
  });
}

function writeCSV(data) {
  const headers = ['ID','Emotion','Variant','Description','Filename','Prompt','Status'];
  const content = [headers.join(',')].concat(data.map(row => headers.map(h => row[h]).join(','))).join('\n');
  fs.writeFileSync(CSV_PATH, content);
}

function generate(row) {
  const output = path.resolve(__dirname, '../assets/sprites', row.Filename);
  // Using the exact prompt logic requested
  const prompt = `Same image, change facial expression to ${row.Prompt}. Keep clothes and background exactly same.`;
  
  console.log(`Generating ${row.ID}: ${row.Description}...`);
  try {
    // Ensure the output directory exists
    const outputDir = path.dirname(output);
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    const cmd = `uv run skills/nano-banana-ultra/scripts/generate_image.py --prompt "${prompt}" --filename "${output}" --input-image "${BASE_IMG}" --resolution 1K`;
    execSync(cmd, { stdio: 'inherit' });
    return true;
  } catch (e) {
    console.error(`Failed to generate ${row.ID}`);
    return false;
  }
}

async function main() {
  if (!fs.existsSync(CSV_PATH)) {
    console.error(`CSV file not found at ${CSV_PATH}`);
    process.exit(1);
  }

  const data = readCSV();
  let pending = data.filter(r => r.Status === 'Pending');
  
  console.log(`Found ${pending.length} pending tasks.`);
  
  for (const row of pending) {
    const success = generate(row);
    if (success) {
      row.Status = 'Done';
      writeCSV(data); // Save progress immediately
      console.log(`${row.Filename} DONE! Waiting 10s...`);
      execSync('sleep 10'); // Cooldown
    } else {
      console.log(`Skipping ${row.Filename} due to error. Waiting 20s...`);
      execSync('sleep 20');
    }
  }
  console.log('Batch run complete.');
}

main();
