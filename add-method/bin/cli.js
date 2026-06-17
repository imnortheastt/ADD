#!/usr/bin/env node
"use strict";

/**
 * @pilotspace/add installer.
 *
 *   npx @pilotspace/add init [targetDir] [--force] [--stage <stage>] [--name <name>] [--yes|--non-interactive]
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
 * One lazy, optional dependency (@clack/prompts) powers the interactive flow on a real
 * terminal; it is dynamic-import()ed ONLY on that path, so a non-interactive / CI run
 * (and the `--yes` / `--non-interactive` path) never loads it and degrades to plain text
 * if it is missing. No Python needed at install time. Designed for failure: verifies
 * sources exist before copying, never clobbers an existing skill, never throws on a
 * non-TTY or a failed clack import.
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
  const args = { _: [], force: false, check: false, noSkill: false, stage: null, name: null,
                 yes: false, nonInteractive: false };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--force") args.force = true;
    else if (a === "--check") args.check = true;
    // --yes / --non-interactive: skip all prompts, take defaults — the explicit
    // non-interactive selector the interactive() gate honors (CI/pipes do this too).
    else if (a === "--yes" || a === "-y") args.yes = true;
    else if (a === "--non-interactive") args.nonInteractive = true;
    // --no-skill: drop the engine + book ONLY, not the skill. The Claude Code plugin
    // already provides the `add` skill, so a plugin bootstrap uses this to materialize
    // .add/tooling/ + .add/docs/ into the project without a duplicate .claude/skills/add.
    else if (a === "--no-skill") args.noSkill = true;
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

// --- interactive layer (clack on a real TTY; plain text everywhere else) -----
// Designed-for-failure: any doubt (non-TTY, CI, --yes, a failed import, an
// un-promptable stream) degrades to the EXACT plain-text path below. The clack
// import is dynamic + lazy (clack 1.x is ESM-only) so a non-interactive / CI run
// never loads it. A test seam (ADD_INSTALLER_FORCE_INTERACTIVE) reaches the branch
// without a PTY: "1" forces interactive, "fail" forces it but throws on import.

function interactive(args) {
  if (args.yes || args.nonInteractive) return false;       // explicit opt-out wins
  const seam = process.env.ADD_INSTALLER_FORCE_INTERACTIVE;
  if (seam === "1" || seam === "fail") return true;        // documented test seam
  return Boolean(process.stdout.isTTY && process.stdin.isTTY) && !process.env.CI;
}

async function loadClack() {
  // honors the "fail" seam so the clack_unavailable fallback is testable without
  // uninstalling the dependency.
  if (process.env.ADD_INSTALLER_FORCE_INTERACTIVE === "fail") {
    throw new Error("forced clack import failure (test seam)");
  }
  return import("@clack/prompts");
}

// Returns { cancelled, target }. A cancel happens BEFORE any file is written, so a
// cancelled run leaves the target untouched. Without a real TTY to read (the forced
// test seam), we cannot prompt — abort safely rather than hang.
async function runClackPreamble(clack, target) {
  clack.intro("ADD — AI-Driven Development");
  if (!process.stdin.isTTY) return { cancelled: true, target: target };
  const chosen = await clack.text({
    message: "Install ADD into which directory?",
    initialValue: target, defaultValue: target,
  });
  if (clack.isCancel(chosen)) return { cancelled: true, target: target };
  const ok = await clack.confirm({ message: "Write the ADD skill + tooling + book here?" });
  if (clack.isCancel(ok) || !ok) return { cancelled: true, target: target };
  return { cancelled: false, target: String(chosen || target) };
}

// The drop — now a RECONCILE: restore missing managed trees + refresh present ones
// (sweep orphans) + report per-tree status. Byte-compatible handoff with the prior
// installer. The interactive path resolves a target then calls straight into this.
function dropFiles(args, target) {
  log("Installing ADD into " + target);
  reconcile(args, target);

  // NO step 4: the installer DROPS FILES ONLY. Initialisation is deferred to the AI
  // (via `/add`) or a CLI user — a pre-run plain `add.py init` would grandfather-lock
  // the v12 lock-down gate before `/add` runs (see file header). So no Python is run here.
  log("\nDone. " + (args.noSkill ? "The engine + book are" : "The `add` skill + tooling are") +
      " installed (no project state yet — that's intentional).");
  log("Next:  open your AI Agent CLI (like Claude Code, Codex, etc.), then run `/add`, and say what you want to build — the agent");
  log("       sets up the foundation, sizes it into a milestone, and drives the build with you;");
  log("       you sign off once, at the lock-down.");
  log("");
}

async function cmdInit(args) {
  const target = path.resolve(args._[0] || ".");
  if (!fs.existsSync(target)) fail("target directory does not exist: " + target);

  let chosenTarget = target;
  if (interactive(args)) {
    let clack = null;
    try { clack = await loadClack(); }
    catch (_e) { warn("clack unavailable — falling back to plain-text install"); }
    if (clack) {
      const outcome = await runClackPreamble(clack, target);
      if (outcome.cancelled) {
        // the exit code IS the contract; a closed-pipe stdout (EPIPE) must not
        // mask the cancel — guard the courtesy message, never let it throw.
        try { clack.cancel("Installation cancelled — nothing was written."); }
        catch (_e) { /* stdout unavailable (e.g. closed pipe) — exit code carries it */ }
        process.exit(130);                // user_cancelled: nothing written
      }
      chosenTarget = path.resolve(outcome.target);
      if (!fs.existsSync(chosenTarget)) fail("target directory does not exist: " + chosenTarget);
    }
  }
  dropFiles(args, chosenTarget);
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

const TREE_LABEL = { "skill/add": "skill", "tooling": "tooling", "docs": "docs" };

// Per managed tree: "missing" (dest absent OR empty) or "present".
function managedStatus(target) {
  const status = {};
  for (const [sub, destParts] of MANAGED) {
    const dest = path.join(target, ...destParts);
    const present = fs.existsSync(dest) && fs.readdirSync(dest).length > 0;
    status[sub] = present ? "present" : "missing";
  }
  return status;
}

// reconcile: restore-missing + refresh-present (sweep orphans) across the managed trees,
// reporting per-tree status. Honors --no-skill (the plugin provides the skill). Touches
// ONLY managed trees — never user data. Prechecks ALL sources first (design-for-failure:
// a corrupt package leaves the target untouched).
function reconcile(args, target) {
  const trees = MANAGED.filter(([sub]) => !(sub === "skill/add" && args.noSkill));
  for (const [sub] of trees) {
    if (!fs.existsSync(path.join(PKG_ROOT, sub))) {
      fail("missing packaged source: " + path.join(PKG_ROOT, sub));
    }
  }
  const status = managedStatus(target);
  for (const [sub, destParts, stripTests] of trees) {
    cleanReplaceTree(path.join(PKG_ROOT, sub), path.join(target, ...destParts), stripTests);
    const dest = destParts.join("/");
    if (status[sub] === "missing") {
      log("  ✓ restored  " + TREE_LABEL[sub].padEnd(8) + "-> " + dest + "  (was missing)");
    } else {
      log("  ✓ refreshed " + TREE_LABEL[sub].padEnd(8) + "-> " + dest);
    }
  }
  return status;
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
  // same-version no-op ONLY when nothing is missing — a missing managed tree HEALS
  // even at the current version (heal-reconcile).
  const status = managedStatus(target);
  const missing = MANAGED.some(([sub]) => status[sub] === "missing");
  if (cur === version && !args.force && !missing) {
    log("ADD already at " + version + " — nothing to update (use --force to re-materialize).");
    return;
  }
  // design-for-failure: back up state BEFORE touching anything.
  const stateFile = path.join(addDir, "state.json");
  if (fs.existsSync(stateFile)) {
    fs.copyFileSync(stateFile, path.join(addDir, "pre-update-state.bak.json"));
  }
  reconcile(args, target);
  writeStamp(addDir, version);
  log("ADD updated " + (cur || "(unstamped)") + " -> " + version +
      " · managed layer reconciled · your project state untouched.");
}

async function main() {
  const argv = process.argv.slice(2);
  const cmd = argv[0] && !argv[0].startsWith("--") ? argv.shift() : "init";
  const args = parseArgs(argv);
  switch (cmd) {
    case "init":
      await cmdInit(args);
      break;
    case "update":
      cmdUpdate(args);
      break;
    case "help":
    case "--help":
      log("usage: npx @pilotspace/add <init|update> [targetDir] [--force] [--check] [--no-skill] [--yes|--non-interactive]");
      log("  init    install the ADD skill + tooling + book into a project");
      log("          (--no-skill drops the engine + book only — used by the Claude Code plugin)");
      log("          (interactive in a real terminal; --yes / --non-interactive force the plain path)");
      log("  update  re-materialize skill/tooling/docs to this package version (preserves your state)");
      break;
    default:
      fail("unknown command '" + cmd + "'. Try: npx @pilotspace/add init");
  }
}

main().catch((e) => fail(e && e.message ? e.message : String(e)));
