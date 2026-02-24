#!/usr/bin/env node
/**
 * patch-config.js — Merge social-media-ops agent configuration into openclaw.json
 *
 * Usage:
 *   node patch-config.js --config ~/.openclaw/openclaw.json --agents all --models '{...}'
 *   node patch-config.js --config ~/.openclaw/openclaw.json --agents leader,content,designer,engineer
 *   node patch-config.js --dry-run --config ~/.openclaw/openclaw.json
 *
 * Options:
 *   --config PATH     Path to openclaw.json (required)
 *   --agents LIST     Comma-separated agent list (default: all)
 *   --models JSON     Model mapping as JSON string
 *   --base-dir DIR    OpenClaw root directory (default: ~/.openclaw)
 *   --dry-run         Print changes without writing
 *   --help            Show help
 */

const fs = require("fs");
const path = require("path");

// ── Defaults ──────────────────────────────────────────────────────────

const DEFAULT_AGENTS = [
  "leader",
  "researcher",
  "content",
  "designer",
  "operator",
  "engineer",
  "reviewer",
];

const DEFAULT_MODELS = {
  leader: "anthropic/claude-opus-4-6",
  researcher: "anthropic/claude-opus-4-6",
  content: "anthropic/claude-sonnet-4-5-20250514",
  designer: "anthropic/claude-sonnet-4-5-20250514",
  operator: "anthropic/claude-sonnet-4-5-20250514",
  engineer: "anthropic/claude-sonnet-4-5-20250514",
  reviewer: "anthropic/claude-sonnet-4-5-20250514",
};

const DEFAULT_FALLBACK = "anthropic/claude-sonnet-4-5-20250514";

const AGENT_TOOL_DENY = {
  leader: ["exec", "browser"],
  researcher: ["exec", "browser"],
  content: ["exec", "apply_patch", "browser"],
  designer: ["exec", "apply_patch", "browser"],
  operator: ["exec", "edit", "apply_patch"],
  engineer: ["browser"],
  reviewer: ["exec", "edit", "apply_patch", "write", "browser"],
};

const AGENT_NAMES = {
  leader: "Leader",
  researcher: "Researcher",
  content: "Content",
  designer: "Designer",
  operator: "Operator",
  engineer: "Engineer",
  reviewer: "Reviewer",
};

// ── Argument Parsing ──────────────────────────────────────────────────

function parseArgs(argv) {
  const args = {
    config: null,
    agents: DEFAULT_AGENTS,
    models: { ...DEFAULT_MODELS },
    baseDir: path.join(process.env.HOME || "~", ".openclaw"),
    dryRun: false,
  };

  for (let i = 2; i < argv.length; i++) {
    switch (argv[i]) {
      case "--config":
        args.config = argv[++i];
        break;
      case "--agents":
        args.agents = argv[++i].split(",").map((s) => s.trim());
        break;
      case "--models":
        Object.assign(args.models, JSON.parse(argv[++i]));
        break;
      case "--base-dir":
        args.baseDir = argv[++i];
        break;
      case "--dry-run":
        args.dryRun = true;
        break;
      case "--help":
      case "-h":
        console.log(
          "Usage: node patch-config.js --config <path> [--agents <list>] [--models <json>] [--base-dir <dir>] [--dry-run]"
        );
        process.exit(0);
      default:
        console.error(`[ERROR] Unknown option: ${argv[i]}`);
        process.exit(1);
    }
  }

  if (!args.config) {
    console.error("[ERROR] --config is required");
    process.exit(1);
  }

  // Validate leader is included
  if (!args.agents.includes("leader")) {
    console.error("[ERROR] Leader agent is required");
    process.exit(1);
  }

  return args;
}

// ── Deep Merge ────────────────────────────────────────────────────────

function deepMerge(target, source) {
  const result = { ...target };
  for (const key of Object.keys(source)) {
    if (
      source[key] &&
      typeof source[key] === "object" &&
      !Array.isArray(source[key]) &&
      target[key] &&
      typeof target[key] === "object" &&
      !Array.isArray(target[key])
    ) {
      result[key] = deepMerge(target[key], source[key]);
    } else {
      result[key] = source[key];
    }
  }
  return result;
}

// ── Build Agent Entry ─────────────────────────────────────────────────

function buildAgentEntry(agentId, args) {
  const wsDir =
    agentId === "leader" ? "workspace" : `workspace-${agentId}`;
  const entry = {
    id: agentId,
    name: AGENT_NAMES[agentId] || agentId,
    workspace: path.join(args.baseDir, wsDir),
    model: {
      primary: args.models[agentId] || DEFAULT_MODELS[agentId] || DEFAULT_FALLBACK,
      fallbacks: [DEFAULT_FALLBACK],
    },
    tools: {
      deny: AGENT_TOOL_DENY[agentId] || [],
    },
  };

  // Leader is the default agent
  if (agentId === "leader") {
    entry.default = true;
    // Identity will be filled during instance-setup
    entry.identity = { name: "Assistant", emoji: "🤖" };
  }

  // Reviewer gets sandbox
  if (agentId === "reviewer") {
    entry.sandbox = { mode: "non-main", scope: "session" };
  }

  // Remove fallback if it's the same as primary
  if (entry.model.fallbacks[0] === entry.model.primary) {
    entry.model.fallbacks = [];
  }

  return entry;
}

// ── Patch Config ──────────────────────────────────────────────────────

function patchConfig(config, args) {
  const patched = { ...config };

  // ── Ensure agents section exists ──
  if (!patched.agents) {
    patched.agents = {};
  }

  // ── Set agent defaults ──
  patched.agents.defaults = deepMerge(patched.agents.defaults || {}, {
    compaction: { mode: "safeguard" },
    maxConcurrent: 4,
    subagents: { maxConcurrent: 8 },
  });

  // ── Build agent list ──
  const existingList = patched.agents.list || [];
  const existingIds = new Set(existingList.map((a) => a.id));
  const newEntries = [];

  for (const agentId of args.agents) {
    if (!existingIds.has(agentId)) {
      newEntries.push(buildAgentEntry(agentId, args));
      console.log(`[ADD]  Agent: ${agentId}`);
    } else {
      console.log(`[SKIP] Agent: ${agentId} (already exists)`);
    }
  }

  patched.agents.list = [...existingList, ...newEntries];

  // ── Set A2A configuration ──
  if (!patched.tools) patched.tools = {};
  patched.tools.agentToAgent = {
    enabled: true,
    allow: [...args.agents],
  };
  patched.tools.sessions = { visibility: "all" };
  console.log("[SET]  tools.agentToAgent");

  // ── Set session configuration ──
  if (!patched.session) patched.session = {};
  patched.session.agentToAgent = { maxPingPongTurns: 3 };
  console.log("[SET]  session.agentToAgent.maxPingPongTurns: 3");

  // ── Set memory / QMD paths ──
  patched.memory = deepMerge(patched.memory || {}, {
    backend: "qmd",
    qmd: {
      includeDefaultMemory: true,
      paths: [
        { path: "memory", name: "daily-notes", pattern: "**/*.md" },
        { path: "skills", name: "agent-skills", pattern: "**/*.md" },
        { path: "shared", name: "shared-knowledge", pattern: "**/*.md" },
      ],
      update: { interval: "5m" },
    },
  });
  console.log("[SET]  memory.qmd paths");

  // ── Set hooks ──
  patched.hooks = deepMerge(patched.hooks || {}, {
    internal: {
      enabled: true,
      entries: {
        "boot-md": { enabled: true },
        "bootstrap-extra-files": { enabled: true },
        "command-logger": { enabled: true },
        "session-memory": { enabled: true },
      },
    },
  });
  console.log("[SET]  hooks.internal entries");

  // ── Set message settings ──
  if (!patched.messages) patched.messages = {};
  if (!patched.messages.ackReactionScope) {
    patched.messages.ackReactionScope = "all";
    console.log("[SET]  messages.ackReactionScope: all");
  }

  // ── Set commands ──
  patched.commands = deepMerge(patched.commands || {}, {
    native: "auto",
    nativeSkills: "auto",
    restart: true,
  });

  return patched;
}

// ── Main ──────────────────────────────────────────────────────────────

function main() {
  const args = parseArgs(process.argv);

  console.log(`[INFO] Config: ${args.config}`);
  console.log(`[INFO] Agents: ${args.agents.join(", ")}`);
  console.log(`[INFO] Base dir: ${args.baseDir}`);
  if (args.dryRun) console.log("[INFO] DRY RUN — no changes will be written");
  console.log("");

  // Read existing config
  let config = {};
  if (fs.existsSync(args.config)) {
    const raw = fs.readFileSync(args.config, "utf8");
    config = JSON.parse(raw);
    console.log("[OK]   Read existing openclaw.json");
  } else {
    console.log("[INFO] No existing openclaw.json — creating new");
  }

  // Apply patches
  const patched = patchConfig(config, args);

  // Write result
  if (args.dryRun) {
    console.log("\n[DRY RUN] Would write:");
    console.log(JSON.stringify(patched, null, 2));
  } else {
    // Backup original
    if (fs.existsSync(args.config)) {
      const backupPath = args.config + ".backup-" + Date.now();
      fs.copyFileSync(args.config, backupPath);
      console.log(`\n[OK]   Backup: ${backupPath}`);
    }

    fs.writeFileSync(args.config, JSON.stringify(patched, null, 2) + "\n");
    console.log(`[OK]   Written: ${args.config}`);
  }

  console.log("\n[OK]   Config patching complete");
  console.log("\nNext: openclaw gateway restart");
}

main();
