#!/usr/bin/env node
"use strict";

/**
 * @pilotspace/add installer.
 *
 *   npx @pilotspace/add init [targetDir] [--force] [--stage <stage>] [--name <name>]
 *
 * Installs the ADD skill + tooling + book into a target project:
 *   <target>/.claude/skills/add/   (the skill Claude loads)
 *   <target>/.add/tooling/         (add.py scaffolder + state tracker)
 *   <target>/.add/docs/            (the AIDD book — the trust layer)
 * It DROPS FILES ONLY — it does NOT run `add.py init`. Initialisation is deferred to
 * the AI (via `/add`, which runs `init --await-lock` to arm the v12 lock-down gate) or
 * to a CLI user. A pre-run plain init would grandfather-lock the gate before `/add` runs
 * AND consume the brownfield signal in the terminal, where the AI never sees it.
 *
 * Zero npm dependencies, no Python needed at install time. Designed for failure:
 * verifies sources exist before copying, never clobbers an existing skill.
 */

const fs = require("fs");
const path = require("path");

const PKG_ROOT = path.resolve(__dirname, "..");

function log(msg) { process.stdout.write(msg + "\n"); }
function warn(msg) { process.stderr.write("warn: " + msg + "\n"); }
function fail(msg) { process.stderr.write("error: " + msg + "\n"); process.exit(1); }

function parseArgs(argv) {
  // stage/name stay null unless EXPLICITLY passed — the engine's own `init`
  // defaults the stage and infers the name from the folder, so the manual-init
  // hint only echoes flags the user actually chose (shortest true command).
  const args = { _: [], force: false, check: false, stage: null, name: null };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--force") args.force = true;
    else if (a === "--check") args.check = true;
    else if (a === "--stage" || a === "--name") {
      const v = argv[++i];
      // fail loudly on a trailing/abutting flag — never silently drop a value
      // the user tried to pass (parity with the pip twin's argparse error)
      if (v == null || v.startsWith("--")) fail(a + " requires a value");
      if (a === "--stage") args.stage = v; else args.name = v;
    }
    else if (a.startsWith("--")) warn("ignoring unknown flag " + a);
    else args._.push(a);
  }
  return args;
}

function copyDir(src, dest, { skipIfExists, cleanReplace } = {}) {
  if (!fs.existsSync(src)) fail("missing packaged source: " + src);
  if (skipIfExists && fs.existsSync(dest)) {
    warn(dest + " exists — leaving it untouched");
    return;
  }
  // Clean replace: drop a stale dest before copying so a `--force` re-install can
  // never leave orphaned files from a previous version behind. fs.cpSync merges
  // (it never removes), so without this `--force` is a merge, not a replace. Mirrors
  // _installer.py's `shutil.rmtree(skill_dest)` so npm and pip behave identically.
  if (cleanReplace && fs.existsSync(dest)) {
    fs.rmSync(dest, { recursive: true, force: true });
  }
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.cpSync(src, dest, { recursive: true });
}

function cmdInit(args) {
  const target = path.resolve(args._[0] || ".");
  if (!fs.existsSync(target)) fail("target directory does not exist: " + target);
  log("Installing ADD into " + target);

  // 1. skill -> .claude/skills/add
  copyDir(
    path.join(PKG_ROOT, "skill", "add"),
    path.join(target, ".claude", "skills", "add"),
    { skipIfExists: !args.force, cleanReplace: args.force }
  );
  log("  ✓ skill      -> .claude/skills/add/");

  // 2. tooling -> .add/tooling  (exclude tests from the installed copy)
  const toolingDest = path.join(target, ".add", "tooling");
  copyDir(path.join(PKG_ROOT, "tooling"), toolingDest, { skipIfExists: false });
  // installed copy is runtime-only: drop ALL test files and any compiled cache
  // (glob test_*.py — not just test_add.py — so no test leaks into installs)
  fs.rmSync(path.join(toolingDest, "__pycache__"), { recursive: true, force: true });
  for (const entry of fs.readdirSync(toolingDest)) {
    if (/^test_.*\.py$/.test(entry)) {
      fs.rmSync(path.join(toolingDest, entry), { force: true });
    }
  }
  log("  ✓ tooling    -> .add/tooling/add.py (+ templates)");

  // 3. docs (the book / trust layer) -> .add/docs
  copyDir(path.join(PKG_ROOT, "docs"), path.join(target, ".add", "docs"),
    { skipIfExists: false });
  log("  ✓ trust docs -> .add/docs/ (the AIDD book)");

  // NO step 4: the installer DROPS FILES ONLY. Initialisation is deferred to the AI
  // (via `/add`) or a CLI user — a pre-run plain `add.py init` would grandfather-lock
  // the v12 lock-down gate before `/add` runs (see file header). So no Python is run here.
  log("\nDone. The `add` skill + tooling are installed (no project state yet — that's intentional).");
  log("Next:  open your AI Agent CLI (like Claude Code, Codex, etc.), then run `/add`, and say what you want to build — the agent");
  log("       sets up the foundation, sizes it into a milestone, and drives the build with you;");
  log("       you sign off once, at the lock-down.");
  log("");
}

// --- update: re-materialize the managed layer without a re-install -----------
// The managed trees (ship-controlled). `update` clean-replaces each, so a file removed
// upstream leaves no orphan — and never touches .add/state.json, PROJECT.md, milestones,
// tasks, or archive (user data). Pure file-copy (npm <-> pip parity with _installer.py).
const MANAGED = [
  ["skill/add", [".claude", "skills", "add"], false],
  ["tooling", [".add", "tooling"], true],
  ["docs", [".add", "docs"], false],
];
const STAMP_FILE = ".add-version";

function pkgVersion() {
  try { return require(path.join(PKG_ROOT, "package.json")).version; }
  catch (_e) { return "0.0.0"; }
}

function readStamp(addDir) {
  const p = path.join(addDir, STAMP_FILE);
  if (!fs.existsSync(p)) return null;
  try { return JSON.parse(fs.readFileSync(p, "utf8")); } catch (_e) { return null; }
}

function writeStamp(addDir, version) {
  fs.mkdirSync(addDir, { recursive: true });
  fs.writeFileSync(
    path.join(addDir, STAMP_FILE),
    JSON.stringify({ version: version, channel: "npm", installed_at: new Date().toISOString() }, null, 2) + "\n"
  );
}

function cleanReplaceTree(src, dest, stripTests) {
  if (!fs.existsSync(src)) fail("missing packaged source: " + src);
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  if (fs.existsSync(dest)) fs.rmSync(dest, { recursive: true, force: true });
  fs.cpSync(src, dest, { recursive: true });
  if (stripTests) {
    fs.rmSync(path.join(dest, "__pycache__"), { recursive: true, force: true });
    for (const entry of fs.readdirSync(dest)) {
      if (/^test_.*\.py$/.test(entry)) fs.rmSync(path.join(dest, entry), { force: true });
    }
  }
}

function cmdUpdate(args) {
  const target = path.resolve(args._[0] || ".");
  const addDir = path.join(target, ".add");
  if (!fs.existsSync(path.join(addDir, "tooling")) && !fs.existsSync(path.join(addDir, "state.json"))) {
    fail("no ADD project at " + target + " (.add/ not found) — run `init` first");
  }
  const version = pkgVersion();
  const stamp = readStamp(addDir);
  const cur = stamp && stamp.version ? stamp.version : null;

  if (args.check) {
    if (cur === version) log("ADD is current: project and package both at " + version + ".");
    else if (cur === null) log("ADD project is unstamped; installed package is " + version + ". Run `update`.");
    else log("ADD update available: project on " + cur + ", package is " + version + ". Run `update`.");
    return;
  }
  if (cur === version && !args.force) {
    log("ADD already at " + version + " — nothing to update (use --force to re-materialize).");
    return;
  }
  // design-for-failure: back up state BEFORE touching anything.
  const stateFile = path.join(addDir, "state.json");
  if (fs.existsSync(stateFile)) {
    fs.copyFileSync(stateFile, path.join(addDir, "pre-update-state.bak.json"));
  }
  for (const [sub, destParts, stripTests] of MANAGED) {
    cleanReplaceTree(path.join(PKG_ROOT, sub), path.join(target, ...destParts), stripTests);
  }
  writeStamp(addDir, version);
  log("ADD updated " + (cur || "(unstamped)") + " -> " + version +
      " · skill · tooling · docs refreshed · your project state untouched.");
}

function main() {
  const argv = process.argv.slice(2);
  const cmd = argv[0] && !argv[0].startsWith("--") ? argv.shift() : "init";
  const args = parseArgs(argv);
  switch (cmd) {
    case "init":
      cmdInit(args);
      break;
    case "update":
      cmdUpdate(args);
      break;
    case "help":
    case "--help":
      log("usage: npx @pilotspace/add <init|update> [targetDir] [--force] [--check]");
      log("  init    install the ADD skill + tooling + book into a project");
      log("  update  re-materialize skill/tooling/docs to this package version (preserves your state)");
      break;
    default:
      fail("unknown command '" + cmd + "'. Try: npx @pilotspace/add init");
  }
}

main();
