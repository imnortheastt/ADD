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
  const args = { _: [], force: false, stage: null, name: null };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--force") args.force = true;
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
  log("Next:  open Claude Code, run `/add`, and say what you want to build — the agent");
  log("       sets up the foundation, sizes it into a milestone, and drives the build with you;");
  log("       you sign off once, at the lock-down.");
  log("");
  log("Prefer the CLI / not using Claude Code? Initialise it yourself (this arms the lock-down):");
  const launcher = process.platform === "win32" ? "py" : "python3";
  log(`  ${launcher} .add/tooling/add.py init --await-lock` +
      (args.stage ? ` --stage ${args.stage}` : "") +
      (args.name ? ` --name "${args.name}"` : ""));
}

function main() {
  const argv = process.argv.slice(2);
  const cmd = argv[0] && !argv[0].startsWith("--") ? argv.shift() : "init";
  const args = parseArgs(argv);
  switch (cmd) {
    case "init":
      cmdInit(args);
      break;
    case "help":
    case "--help":
      log("usage: npx @pilotspace/add init [targetDir] [--force] [--stage <s>] [--name <n>]");
      break;
    default:
      fail("unknown command '" + cmd + "'. Try: npx @pilotspace/add init");
  }
}

main();
