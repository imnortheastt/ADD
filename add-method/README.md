# ADD — AI-Driven Development

**One skill. Eight steps. Five disciplines. Every feature ships through the loop.**

> A minimal, state-tracked Claude Code skill for building software when the AI
> writes the code and **you** own the two things it cannot do alone: decide *what*
> to build, and *verify* it is correct.

ADD is the **orchestration engine** of the AIDD method. It sits on top of a
context foundation (DDD → SDD → UDD) and runs as a red/green TDD ↔ AI-build loop.
The full reasoning — *why* every rule exists — is the AIDD book bundled in
[`docs/`](./docs/README.md). Read it once; keep it open beside you.

```
  Foundation (context):  DDD  ·  SDD  ·  UDD
  Engine (this skill):   TDD  ⇄  ADD
  Flow per feature:  Specify → Scenarios → Contract → Tests → Build → Verify → Observe ↻
```

## Why ADD (and why it is minimal)

Heavy doc-first methods burn your time writing documents and lose the thread
across sessions (context rot). ADD fixes both:

- **One file per feature.** Spec, scenarios, contract, test-plan, and gate record
  all live inline in a single `TASK.md`. No sprawling doc tree.
- **State on disk, not in chat.** A Python tool tracks where you are in
  `.add/state.json`, so a fresh session resumes with one command instead of
  re-reading the repo.
- **Progressive disclosure.** The skill loads only the guide for the phase you are
  in — the context window stays lean.

## Install

Pick your ecosystem — all three install the same skill, tooling, and book:

```bash
# Node / npm
npx @pilotspace/add init
```

```bash
# Python / pip
pip install pilotspace-add
pilotspace-add init
```

```text
# Claude Code plugin — no npm or pip needed
/plugin marketplace add pilotspace/ADD
/plugin install add@add-method
```

The plugin carries the engine and the book. On first `/add`, the skill materializes them
into the project (`node "${CLAUDE_PLUGIN_ROOT}/bin/cli.js" init --no-skill`) and scaffolds
`.add/` — a self-contained, portable result identical to the npm/pip flow. The skill stays
in the plugin, so nothing is duplicated.

No flags needed — the project name is inferred from your folder and the stage
defaults to `prototype` (pass `--name "My App" --stage mvp` to choose up front).

**Already installed?** Refresh to the latest without a re-install —
`npx @pilotspace/add@latest update` (or `pipx run pilotspace-add update`)
re-materializes the skill, tooling, and book while leaving your project work
(`.add/state.json`, `PROJECT.md`, milestones, tasks) untouched; add `--check` to
see whether a project is behind the installed package.

**New here?** Follow the [10-minute Quickstart](./GETTING-STARTED.md) — it walks
your first feature end to end.

This installs:

| Path | What |
|------|------|
| `.claude/skills/add/` | the `add` skill Claude loads (thin router + per-phase guides) |
| `.add/tooling/add.py` | scaffolder + state tracker (Python, stdlib only) |
| `.add/docs/` | the AIDD book — the method rationale |
| `.add/DESIGN.md` | (UI projects) the prose front-door to the **render-ready UDD foundation** — delete it if your project has no UI |

On a UI project, UDD gives the AI a frozen design ground to draft from: `DESIGN.md`
plus a lintable JSON foundation under `.add/design/` (design tokens · component
catalog · prototype trees). `add.py check` lints that foundation, going red with a
named code on any layer, catalog, tree, or cross-file violation — and staying
silent when a project has no design set.

Project state (`.add/state.json`) and the living-documentation files (`CONVENTIONS.md`,
`GLOSSARY.md`, `MODEL_REGISTRY.md`, `dependencies.allowlist`, `SOUL.md` — the AI's
human-owned voice) are *not* created here — the installer drops files only;
initialisation is the agent's first move when you run `/add`.

## What this plugin does, writes, and runs (boundaries)

ADD is a development methodology, so by design it works *inside your project* — here is
exactly what that means, so there are no surprises:

- **Runs only when you ask.** Nothing executes on install. The skill acts when you run
  `/add` (or another agent follows the guideline block). It is user-initiated, every time.
- **What it runs:** the bundled engine and bootstrapper only — `node bin/cli.js` and
  `python3 .add/tooling/add.py`. No downloaded or remote code is executed; everything it
  runs ships in the package.
- **What it writes:** files under your project's `.add/` (state, milestones, tasks, the
  book) and the managed guideline block in `CLAUDE.md` / `AGENTS.md`. On a plugin install
  it also materializes the engine + book into `.add/` on first run. It writes nowhere
  outside the project working directory; it never touches files above the project root.
- **Network:** one optional, advisory update check. On `status` / `guide` the engine may
  make a single HTTPS GET to `https://registry.npmjs.org/@pilotspace/add/latest` to see if
  a newer version exists — at most once per 24h (cached in `.update-cache.json`), 1.5s
  timeout, fail-open (offline ⇒ silent no-op). It only writes a one-line note to **stderr**
  and never changes a command's output or exit code. Disable it entirely with
  `ADD_NO_UPDATE_CHECK=1`. No other network access, no telemetry, no analytics.
- **No secrets, no credentials, no privileged access.** Pure local file orchestration.

## Use it

ADD is AI-first: you talk to the agent; it drives the method. In Claude Code, run
**`/add`** and say what you want to build:

> `/add` — *"I want to let users transfer money between their own accounts."*

**Works with your agent.** The installer detects which coding agent you're in and
drops the context file it reads — so ADD drives through the CLI under **Claude Code,
Codex, OpenCode, Cursor, Windsurf, Trae, Gemini CLI, GitHub Copilot, Cline, and
Aider** (anything else falls back to a generic `AGENTS.md`). Only Claude Code runs
the `/add` skill natively; every other agent follows the same loop through the
phase guides via `add.py status` / `guide`.

The agent orients from `state.json`, **sizes your request into a milestone** (you
confirm the shape), then drafts each feature's **specification bundle** — Spec +
Scenarios + Contract + Tests as one bundle — and you give **one approval at the
frozen contract**. A self-driving build→verify run takes it to green; security
findings always stop back to you.

Under the hood the agent runs the CLI as its hands — and you can hand-drive it too:

```bash
python3 .add/tooling/add.py status      # where am I? (resume point)
```

## The non-negotiables

1. **Direction before speed** — no Build until spec, scenarios, contract, and *red*
   tests exist.
2. **Trust evidence, not inspection** — a feature is trusted because its tests pass
   and the non-functional risks (concurrency, security, architecture) were checked.
3. **Never weaken a test or edit a frozen contract** to make the build pass.
4. **No silent skips** — every Verify records `PASS`, `RISK-ACCEPTED`, or
   `HARD-STOP`. Security findings are always `HARD-STOP`.
5. **Ask, don't guess.**

## The artifacts survive; the code is disposable

The durable asset is the decisions — spec, scenarios, contract, tests. The code is
one implementation that satisfies them and can be regenerated. If the thing you'd
be upset to lose is "the code," you're still working the old way.

## Read the method

Start at [`docs/README.md`](./docs/README.md) — Foundations → the six steps →
operating it across a team → templates, prompts, and a full worked example.

## What's next

**Dynamic Agent Skills** — the next scope: skills that adapt at runtime to the
project's current state, stage, and active phase rather than loading a static
guide. The agent picks the right depth and tooling automatically as the project
evolves.

## Develop

```bash
npm test     # runs the Python tests for the tooling (red/green)
```

License: MIT.
