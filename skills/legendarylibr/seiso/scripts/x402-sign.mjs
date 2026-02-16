#!/usr/bin/env node
/**
 * x402 Payment Signer for SeisoAI
 *
 * Usage:
 *   echo '<402_response_json>' | node {baseDir}/scripts/x402-sign.mjs
 *   node {baseDir}/scripts/x402-sign.mjs --challenge '<402_response_json>'
 *
 * Env:
 *   SEISOAI_WALLET_KEY  — x402 signing key (0x-prefixed hex)
 *
 * Output: payment-signature header value (JSON string) to stdout
 *
 * Deps: npm ci --ignore-scripts (once, from scripts/ dir)
 */
import { existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const nodeModules = join(__dirname, 'node_modules');

// Verify deps are pre-installed — never auto-install while a private key may be in scope
if (!existsSync(join(nodeModules, 'viem')) || !existsSync(join(nodeModules, '@x402'))) {
  console.error(
    'ERROR: Dependencies not installed.\n' +
    'Run this ONCE (without SEISOAI_WALLET_KEY in your env):\n' +
    `  cd ${__dirname} && npm ci --ignore-scripts\n` +
    'Then re-run the signing command.'
  );
  process.exit(1);
}

const { privateKeyToAccount } = await import('viem/accounts');
const { ExactEvmScheme } = await import('@x402/evm');

const EXPECTED_PAY_TO = '0xa0aE05e2766A069923B2a51011F270aCadFf023a'.toLowerCase();

// USDC on Base — EIP-712 domain defaults (required by @x402/evm EIP-3009)
const USDC_BASE_DEFAULTS = {
  name: 'USD Coin',
  version: '2',
  asset: '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913', // USDC on Base
};

async function main() {
  const pk = process.env.SEISOAI_WALLET_KEY;
  if (!pk) {
    console.error('ERROR: Set SEISOAI_WALLET_KEY env var (0x-prefixed x402 signing key).');
    process.exit(1);
  }

  // Read 402 challenge from stdin or --challenge arg
  let raw = '';
  const idx = process.argv.indexOf('--challenge');
  if (idx !== -1 && process.argv[idx + 1]) {
    raw = process.argv[idx + 1];
  } else {
    const chunks = [];
    for await (const chunk of process.stdin) chunks.push(chunk);
    raw = Buffer.concat(chunks).toString('utf8').trim();
  }

  if (!raw) {
    console.error('ERROR: No 402 challenge. Pipe JSON or use --challenge');
    process.exit(1);
  }

  let challenge;
  try { challenge = JSON.parse(raw); } catch {
    console.error('ERROR: Invalid JSON'); process.exit(1);
  }

  const req = challenge.accepts?.[0];
  if (!req) { console.error('ERROR: No accepts[] in 402'); process.exit(1); }

  // Safety: verify payTo
  if (req.payTo.toLowerCase() !== EXPECTED_PAY_TO) {
    console.error(`BLOCKED: payTo ${req.payTo} != expected SeisoAI address`);
    process.exit(1);
  }

  // Fill in EIP-712 domain defaults for USDC on Base if missing
  if (!req.extra) req.extra = {};
  if (!req.extra.name) req.extra.name = USDC_BASE_DEFAULTS.name;
  if (!req.extra.version) req.extra.version = USDC_BASE_DEFAULTS.version;

  // Resolve USDC contract address (asset field needs to be the contract, not symbol)
  const assetAddress = (req.asset === 'USDC' || req.asset === 'usdc')
    ? USDC_BASE_DEFAULTS.asset
    : req.asset;

  const account = privateKeyToAccount(pk);

  const paymentRequirements = {
    scheme: req.scheme || 'exact',
    network: req.network || 'eip155:8453',
    amount: req.maxAmountRequired,
    payTo: req.payTo,
    asset: assetAddress,
    maxTimeoutSeconds: req.maxTimeoutSeconds || 300,
    resource: challenge.resource?.url || '',
    extra: req.extra,
  };

  const signer = {
    address: account.address,
    signTypedData: async (args) => account.signTypedData(args),
  };

  const scheme = new ExactEvmScheme(signer);
  const payload = await scheme.createPaymentPayload(
    challenge.x402Version || 2,
    paymentRequirements,
  );

  // Output the header value
  console.log(JSON.stringify(payload));
}

main().catch(err => {
  console.error('ERROR:', err.message);
  process.exit(1);
});
