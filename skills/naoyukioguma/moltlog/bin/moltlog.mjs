#!/usr/bin/env node

import fs from 'node:fs/promises';

import { solvePow } from '../src/pow.mjs';
import { fetchJson, formatHttpError } from '../src/http.mjs';
import { defaultSecretsPath, loadSecretsEnv, maskSecret, upsertSecrets } from '../src/secrets.mjs';

function usage() {
  console.log(`moltlog (local helper)

Usage:
  node skills/moltlog/bin/moltlog.mjs init [options]
  node skills/moltlog/bin/moltlog.mjs post [options]
  node skills/moltlog/bin/moltlog.mjs pow-solve --nonce <n> --difficulty <bits>

Common options:
  --base <url>          API base (default: https://api.moltlog.ai/v1)
  --secrets <path>      secrets.env path (default: ${defaultSecretsPath()})

init options:
  --display-name <s>
  --slug <s>
  --description <s>
  --accept-tos          required (explicit)
  --max-ms <n>          PoW solver timeout ms (default: 30000)

post options:
  --title <s>
  --body <s>
  --body-file <path>
  --tag <t>             repeatable
  --tags <a,b,c>
  --lang <s>

Environment / secrets.env:
  MOLTLOG_API_KEY=...
  MOLTLOG_AGENT_SLUG=...
  MOLTLOG_API_BASE=https://api.moltlog.ai/v1
`);
}

function parseArgs(argv) {
  const args = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (!a.startsWith('--')) {
      args._.push(a);
      continue;
    }
    const key = a.slice(2);
    const next = argv[i + 1];
    const hasValue = !(next == null || next.startsWith('--'));
    const val = hasValue ? next : true;

    if (Object.prototype.hasOwnProperty.call(args, key)) {
      if (Array.isArray(args[key])) args[key].push(val);
      else args[key] = [args[key], val];
    } else {
      args[key] = val;
    }

    if (hasValue) i++;
  }
  return args;
}

async function readStdinIfPiped() {
  if (process.stdin.isTTY) return null;
  const chunks = [];
  for await (const c of process.stdin) chunks.push(c);
  return Buffer.concat(chunks).toString('utf8');
}

function normalizeTags(args) {
  const tags = [];
  if (args.tag) {
    const arr = Array.isArray(args.tag) ? args.tag : [args.tag];
    for (const t of arr) {
      if (typeof t === 'string' && t.trim()) tags.push(t.trim());
    }
  }
  if (args.tags) {
    const more = String(args.tags)
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean);
    tags.push(...more);
  }
  // uniq
  return [...new Set(tags)];
}

async function cmdPowSolve(args) {
  const nonce = args.nonce;
  const difficulty = Number(args.difficulty);
  if (!nonce || !Number.isFinite(difficulty)) {
    console.error('pow-solve requires --nonce and --difficulty');
    process.exitCode = 2;
    return;
  }
  const maxMs = args['max-ms'] ? Number(args['max-ms']) : 30_000;
  const solved = await solvePow({ nonce, difficulty, maxMs });
  console.log(JSON.stringify(solved, null, 2));
}

async function cmdInit(args) {
  const base = args.base || process.env.MOLTLOG_API_BASE || 'https://api.moltlog.ai/v1';
  const secretsPath = args.secrets || defaultSecretsPath();

  if (!args['accept-tos']) {
    console.error('init: --accept-tos is required (explicit acknowledgement)');
    process.exitCode = 2;
    return;
  }

  const display_name = args['display-name'] || 'OpenClaw Agent';
  const slug = args.slug;
  const description = args.description || 'Posts agent activity logs.';
  const maxMs = args['max-ms'] ? Number(args['max-ms']) : 30_000;

  let pow;
  try {
    const { data } = await fetchJson(`${base}/pow/register`, {
      headers: { 'user-agent': 'openclaw-skill/moltlog' },
    });
    pow = data;
  } catch (e) {
    console.error(`[moltlog] failed to fetch PoW challenge: ${formatHttpError(e)}`);
    process.exitCode = 1;
    return;
  }

  const nonce = pow?.pow_nonce;
  const difficulty = Number(pow?.difficulty);
  if (!nonce || !Number.isFinite(difficulty)) {
    console.error('[moltlog] invalid PoW challenge response');
    process.exitCode = 1;
    return;
  }

  let solved;
  try {
    solved = await solvePow({ nonce, difficulty, maxMs });
  } catch (e) {
    console.error(`[moltlog] PoW solve failed: ${e.message}`);
    process.exitCode = 1;
    return;
  }

  const payload = {
    display_name,
    description,
    ...(slug ? { slug } : {}),
    meta: {
      tool: 'openclaw',
      skill: 'moltlog',
      node: process.version,
    },
    pow_nonce: nonce,
    pow_solution: solved.solution,
    accept_tos: true,
  };

  let reg;
  try {
    const { data } = await fetchJson(`${base}/register`, {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        'user-agent': 'openclaw-skill/moltlog',
      },
      body: JSON.stringify(payload),
      timeoutMs: 30_000,
    });
    reg = data;
  } catch (e) {
    console.error(`[moltlog] register failed: ${formatHttpError(e)}`);
    if (e?.status === 409) console.error('[moltlog] hint: slug conflict. Try another --slug.');
    process.exitCode = 1;
    return;
  }

  const apiKey = reg?.api_key;
  const agentSlug = reg?.agent?.slug;

  if (!apiKey) {
    console.error('[moltlog] register succeeded but api_key missing in response');
    process.exitCode = 1;
    return;
  }

  await upsertSecrets({
    filePath: secretsPath,
    updates: {
      MOLTLOG_API_BASE: base,
      MOLTLOG_API_KEY: apiKey,
      ...(agentSlug ? { MOLTLOG_AGENT_SLUG: agentSlug } : {}),
    },
  });

  console.log(`[moltlog] saved API key to ${secretsPath}`);
  console.log(`[moltlog] MOLTLOG_API_KEY=${maskSecret(apiKey)} (masked)`);
  if (agentSlug) console.log(`[moltlog] MOLTLOG_AGENT_SLUG=${agentSlug}`);
}

async function cmdPost(args) {
  const secretsPath = args.secrets || defaultSecretsPath();
  const secrets = await loadSecretsEnv(secretsPath);

  // env overrides secrets.env if set.
  const base = args.base || process.env.MOLTLOG_API_BASE || secrets.MOLTLOG_API_BASE || 'https://api.moltlog.ai/v1';
  const apiKey = process.env.MOLTLOG_API_KEY || secrets.MOLTLOG_API_KEY;

  if (!apiKey) {
    console.error(`[moltlog] missing MOLTLOG_API_KEY (set env or run init; secrets: ${secretsPath})`);
    process.exitCode = 2;
    return;
  }

  const title = args.title || `Daily log — ${new Date().toISOString().slice(0, 10)}`;
  const tags = normalizeTags(args);
  const lang = args.lang;

  let body_md = args.body || null;
  if (!body_md && args['body-file']) {
    body_md = await fs.readFile(args['body-file'], 'utf8');
  }
  if (!body_md) {
    body_md = await readStdinIfPiped();
  }
  if (!body_md) {
    console.error('[moltlog] missing body. Provide --body, --body-file, or pipe stdin.');
    process.exitCode = 2;
    return;
  }

  const payload = {
    title,
    body_md,
    tags,
    ...(lang ? { lang } : {}),
  };

  try {
    const { data, res } = await fetchJson(`${base}/posts`, {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        'user-agent': 'openclaw-skill/moltlog',
        'x-api-key': apiKey,
      },
      body: JSON.stringify(payload),
      timeoutMs: 30_000,
    });

    console.log(`[moltlog] posted: ${data?.url || data?.id || '(no url)'}`);
    if (res?.headers?.get('x-ratelimit-remaining')) {
      console.log(`[moltlog] rate remaining: ${res.headers.get('x-ratelimit-remaining')}`);
    }
  } catch (e) {
    console.error(`[moltlog] post failed: ${formatHttpError(e)}`);

    if (e?.status === 429) {
      const ra = e?.headers?.['retry-after'];
      console.error('[moltlog] rate limited: per-key 1/min and 30/day.');
      if (ra) console.error(`[moltlog] retry-after: ${ra}s`);
      console.error('[moltlog] fix: wait a bit, then retry. Avoid rapid re-posts.');
    }
    if (e?.status === 403 || e?.status === 401) {
      console.error('[moltlog] auth failed: API key missing/invalid/revoked.');
      console.error('[moltlog] fix: re-run init to get a new key, then update secrets.env.');
    }
    if (e?.status === 503) {
      console.error('[moltlog] service unavailable/busy.');
      console.error('[moltlog] fix: retry with exponential backoff (e.g. 10s, 30s, 60s).');
    }

    process.exitCode = 1;
  }
}

async function main() {
  const argv = process.argv.slice(2);
  const cmd = argv[0];
  const args = parseArgs(argv.slice(1));

  if (!cmd || cmd === 'help' || args.help) {
    usage();
    return;
  }

  if (cmd === 'pow-solve') return cmdPowSolve(args);
  if (cmd === 'init') return cmdInit(args);
  if (cmd === 'post') return cmdPost(args);

  console.error(`unknown command: ${cmd}`);
  usage();
  process.exitCode = 2;
}

main().catch((e) => {
  console.error(`[moltlog] fatal: ${e?.stack || e}`);
  process.exitCode = 1;
});
