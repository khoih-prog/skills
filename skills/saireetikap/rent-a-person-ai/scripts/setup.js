#!/usr/bin/env node
/**
 * RentAPerson one-click setup for OpenClaw.
 * Run from the skill directory: node scripts/setup.js
 * Or, if the skill is installed via ClawHub: node <skill-dir>/scripts/setup.js
 *
 * Does everything hands-off:
 * - Prompts for env (prod vs dev), agent name, email, gateway base URL, session key, hooks token
 * - Registers agent, saves credentials
 * - Injects skill env into openclaw.json
 * - Ensures hooks/transforms dir, copies rentaperson-inject-key-transform (with overwrite prompt)
 * - Patches openclaw.json hooks (transformsDir + mapping for /hooks/rentaperson)
 * - Registers webhook at <gateway>/hooks/rentaperson with webhookSessionKey, webhookFormat, webhookBearerToken
 * - Optional: restart gateway, optional verify
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');
const { spawn } = require('child_process');

const OPENCLAW_CONFIG_PATH =
  process.env.OPENCLAW_CONFIG ||
  path.join(process.env.HOME || process.env.USERPROFILE || '', '.openclaw', 'openclaw.json');

const ENVS = {
  prod: 'https://rentaperson.ai',
  dev: 'https://dev.rentaperson.ai',
};

const TRANSFORM_FILENAME = 'rentaperson-inject-key-transform.js';
const HOOK_NAME = 'rentaperson';

function ask(rl, question, defaultVal = '') {
  const suffix = defaultVal ? ` [${defaultVal}]` : '';
  return new Promise((resolve) => {
    rl.question(`${question}${suffix}: `, (answer) => {
      resolve((answer && answer.trim()) || defaultVal);
    });
  });
}

function askYesNo(rl, question, defaultNo = true) {
  const def = defaultNo ? 'y/N' : 'Y/n';
  return new Promise((resolve) => {
    rl.question(`${question} [${def}]: `, (answer) => {
      const trimmed = (answer && answer.trim().toLowerCase()) || '';
      if (defaultNo) resolve(trimmed === 'y' || trimmed === 'yes');
      else resolve(trimmed !== 'n' && trimmed !== 'no');
    });
  });
}

async function registerAgent(apiBase, agentName, contactEmail) {
  const res = await fetch(`${apiBase}/api/agents/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      agentName,
      agentType: 'openclaw',
      description: `OpenClaw agent: ${agentName}`,
      contactEmail,
    }),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Register failed ${res.status}: ${text}`);
  }
  return res.json();
}

async function patchAgentMe(apiBase, apiKey, body) {
  const res = await fetch(`${apiBase}/api/agents/me`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': apiKey,
    },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`PATCH /api/agents/me failed ${res.status}: ${text}`);
  }
  return res.json();
}

function loadOpenClawConfig() {
  try {
    const raw = fs.readFileSync(OPENCLAW_CONFIG_PATH, 'utf8');
    return JSON.parse(raw);
  } catch (e) {
    if (e.code === 'ENOENT') return {};
    throw e;
  }
}

function saveOpenClawConfig(config) {
  const dir = path.dirname(OPENCLAW_CONFIG_PATH);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(OPENCLAW_CONFIG_PATH, JSON.stringify(config, null, 2), 'utf8');
}

function getStateDir() {
  return (
    process.env.OPENCLAW_STATE_DIR ||
    path.dirname(OPENCLAW_CONFIG_PATH) ||
    path.join(process.env.HOME || process.env.USERPROFILE || '', '.openclaw')
  );
}

async function main() {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });

  console.log('\nRentAPerson OpenClaw setup (hands-off)\n');

  // 1. Base URL (prod vs dev)
  const envChoice = await ask(rl, 'Environment (prod | dev)', 'prod');
  const apiBase = ENVS[envChoice.toLowerCase()] || envChoice.trim() || ENVS.prod;
  if (!apiBase.startsWith('http')) {
    console.error('API base must be a full URL (e.g. https://rentaperson.ai or https://dev.rentaperson.ai).');
    rl.close();
    process.exit(1);
  }
  console.log('Using API base:', apiBase);

  const agentName = await ask(rl, 'Friendly agent name', 'my-openclaw-agent');
  const contactEmail = await ask(rl, 'Contact email', '');
  if (!contactEmail) {
    console.error('Contact email is required.');
    rl.close();
    process.exit(1);
  }

  // Gateway base URL -> we will set webhookUrl to <base>/hooks/rentaperson
  const gatewayBase = await ask(
    rl,
    'Gateway base URL (e.g. https://abc123.ngrok.io)',
    ''
  );
  if (!gatewayBase) {
    console.error('Gateway base URL is required so we can register webhook at /hooks/rentaperson.');
    rl.close();
    process.exit(1);
  }
  let webhookUrl = gatewayBase.trim().replace(/\/$/, '');
  if (!webhookUrl.includes('/hooks/')) {
    webhookUrl += '/hooks/' + HOOK_NAME;
    console.log('Webhook URL will be:', webhookUrl);
  }

  const sessionKey = await ask(rl, 'Persistent session key', 'agent:main:rentaperson');
  const hooksToken = await ask(rl, 'OpenClaw hooks token (for Authorization: Bearer)', '');

  // 2. Copy transform: ensure hooks/transforms exists, copy example -> .js, overwrite prompt
  const stateDir = getStateDir();
  const transformsDir = path.join(stateDir, 'hooks', 'transforms');
  const skillDir = path.resolve(__dirname, '..');
  const examplePath = path.join(skillDir, 'scripts', 'rentaperson-inject-key-transform.example.js');
  const destPath = path.join(transformsDir, TRANSFORM_FILENAME);

  if (!fs.existsSync(examplePath)) {
    console.error('Example transform not found:', examplePath);
    rl.close();
    process.exit(1);
  }
  if (fs.existsSync(destPath)) {
    const overwrite = await askYesNo(rl, `Transform ${TRANSFORM_FILENAME} already exists. Overwrite?`, true);
    if (!overwrite) {
      console.log('Skipping transform copy.');
    } else {
      if (!fs.existsSync(transformsDir)) fs.mkdirSync(transformsDir, { recursive: true });
      fs.copyFileSync(examplePath, destPath);
      console.log('Copied transform to', destPath);
    }
  } else {
    if (!fs.existsSync(transformsDir)) fs.mkdirSync(transformsDir, { recursive: true });
    fs.copyFileSync(examplePath, destPath);
    console.log('Copied transform to', destPath);
  }

  rl.close();

  // 3. Register agent
  console.log('\nRegistering agent...');
  const reg = await registerAgent(apiBase, agentName, contactEmail);
  const agentId = reg.agent?.agentId;
  const apiKey = reg.apiKey;
  if (!agentId || !apiKey) {
    console.error('Unexpected response:', reg);
    process.exit(1);
  }
  console.log('Registered:', agentId);

  const credentialsPath = path.join(skillDir, 'rentaperson-agent.json');
  const credentials = {
    agentId,
    apiKey,
    agentName,
    contactEmail,
    webhookUrl,
    sessionKey,
    apiBase,
  };
  fs.writeFileSync(credentialsPath, JSON.stringify(credentials, null, 2), 'utf8');
  console.log('Saved credentials to', credentialsPath);

  // 4. Patch openclaw.json: skill env + hooks (transformsDir + mapping)
  const config = loadOpenClawConfig();
  if (!config.skills) config.skills = {};
  if (!config.skills.entries) config.skills.entries = {};
  if (!config.skills.entries['rent-a-person-ai']) config.skills.entries['rent-a-person-ai'] = {};
  config.skills.entries['rent-a-person-ai'].env = {
    RENTAPERSON_API_KEY: apiKey,
    RENTAPERSON_AGENT_ID: agentId,
    RENTAPERSON_AGENT_NAME: agentName,
    RENTAPERSON_AGENT_TYPE: 'openclaw',
    ...(config.skills.entries['rent-a-person-ai'].env || {}),
  };

  if (!config.hooks) config.hooks = {};
  config.hooks.transformsDir = config.hooks.transformsDir || path.resolve(transformsDir);
  if (!config.hooks.mappings) config.hooks.mappings = {};
  config.hooks.mappings[HOOK_NAME] = config.hooks.mappings[HOOK_NAME] || {};
  config.hooks.mappings[HOOK_NAME].transform = config.hooks.mappings[HOOK_NAME].transform || TRANSFORM_FILENAME;

  saveOpenClawConfig(config);
  console.log('Updated', OPENCLAW_CONFIG_PATH, '(skill env + hooks.transformsDir + hooks.mappings.rentaperson)');

  // 5. Register webhook at /hooks/rentaperson
  const patch = {
    webhookUrl: webhookUrl.trim(),
    webhookFormat: 'openclaw',
    webhookSessionKey: sessionKey.trim(),
  };
  if (hooksToken) patch.webhookBearerToken = hooksToken.trim();
  await patchAgentMe(apiBase, apiKey, patch);
  console.log('Registered webhook with RentAPerson:', webhookUrl);

  // 6. Optional restart
  const rl2 = readline.createInterface({ input: process.stdin, output: process.stdout });
  const doRestart = await askYesNo(rl2, 'Restart OpenClaw gateway now?', true);
  if (doRestart) {
    const profile = process.env.OPENCLAW_PROFILE || '';
    const args = profile ? ['--profile', profile, 'gateway', 'restart'] : ['gateway', 'restart'];
    console.log('Running: openclaw', args.join(' '));
    const child = spawn('openclaw', args, { stdio: 'inherit', shell: true });
    await new Promise((resolve, reject) => {
      child.on('close', (code) => (code === 0 ? resolve() : reject(new Error(`openclaw exited ${code}`))));
    });
    console.log('Gateway restart completed.');
  } else {
    console.log('Skipped restart. Restart manually when ready: openclaw gateway restart');
  }

  // 7. Verify: instructions + optional test ping
  console.log('\n--- Verify ---');
  const doPing = await askYesNo(rl2, 'Send a test webhook ping to confirm the session gets the injected key?', true);
  rl2.close();
  if (doPing) {
    const pingBody = {
      message:
        '[RentAPerson] Setup test ping. Check that this session shows the injected X-API-Key line.',
      name: 'setup',
      sessionKey: sessionKey.trim(),
    };
    const headers = { 'Content-Type': 'application/json' };
    if (hooksToken) headers['Authorization'] = 'Bearer ' + hooksToken.trim();
    try {
      const res = await fetch(webhookUrl, {
        method: 'POST',
        headers,
        body: JSON.stringify(pingBody),
      });
      console.log('Test webhook sent. Status:', res.status);
      console.log('Check your webhook session for the [RENTAPERSON] injected line in the prompt.');
    } catch (err) {
      console.warn('Test ping failed (gateway may not be reachable yet):', err.message);
    }
  }
  console.log('\nManual verify: send a message or apply to a bounty, or POST to', webhookUrl);
  console.log('The session prompt should contain: [RENTAPERSON] Use for all API calls: X-API-Key: ...');
  console.log('\nDone.');
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
