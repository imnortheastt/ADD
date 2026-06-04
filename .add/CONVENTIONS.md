# CONVENTIONS  (survivor layer — set once, kept for the whole project)

Language/framework:
  - Tooling: Python 3.12+ (standard library only — no third-party packages).
  - Installer: Node.js >= 16 (built-in modules only).
  - Method content: Markdown (the skill + the AIDD book).

Folders:
  - `add-method/`            the shippable npm package (`@pilotspace/add`)
    - `skill/add/`           thin router SKILL.md + `phases/*.md` (progressive disclosure)
    - `tooling/`             `add.py` (scaffolder + state tracker) + `templates/` + `test_add.py`
    - `bin/cli.js`           the `npx @pilotspace/add init` installer
    - `docs/`                the AIDD book bundled as the trust layer
  - `*.md` (repo root)       the AIDD book source chapters
  - `.add/`                  ADD runtime for THIS repo (dogfooding): state, tasks, survivor files

Naming: kebab-case files; snake_case Python; lowerCamelCase JS; task slugs alphanumeric + - _.

Lint/format: keep Python stdlib-idiomatic and type-hinted; no formatter enforced yet (add ruff in CI later).

Errors: machine-readable, never free text. The Python tool exits non-zero with `add: error: <msg>`.

Architecture:
  - The skill is thin and stateless; ALL state lives in `.add/state.json` (anti-context-rot).
  - The Python tool is the only writer of state; writes are atomic (temp + os.replace) and never clobber.
  - The method is tool-agnostic: gates are enforced by process/CI, not inside the agent.

## Method learnings (folded from OBSERVE deltas)

- (ADD) **Never self-gate a human-led gate.** The agent that built a change cannot also approve it —
  Verify has no AI role. Trust-layer/method edits especially require a separate human sign-off, and a
  run's prose guardrails (touch-boundary, autonomy dial) are not enforcement until a CI gate distinct
  from the agent exists. [v6 dogfood: 6 self-gated PASSes, none human-verified — folded foundation-version 2]
- (ADD) **Dogfood parity.** The `.add/` runtime mirror and the canonical `add-method/` tree must stay
  md5-identical for every synced artifact (SKILL.md, run.md, fold.md, …); a structural test asserts it.
- (TDD) **Words-exist ≠ method-works.** Structural/string tests prove an artifact reads as worded, not
  that the behavior works or is enforced (recurring gap). Where behavior matters — md5 parity, an
  enforced default, real convergence — add a behavioral test, not a presence assertion.
- (ADD) **Stale-guard sweep at milestone close.** Shipping a milestone can falsify a *sibling* task's
  frozen test — a guard may encode a world-state the ship just changed. At close, run the full suite and
  re-aim or retire any guard the ship invalidated, as an explicit change-request (human-approved), never
  a silent weakening to make the suite green. [v7 ship broke test_v8_docs (it required the now-removed
  v6/v7 caveat); re-aimed → test_docs_post_ship_honesty — folded foundation-version 4]
- (ADD/SDD) **Docs must not outrun their gate.** A surface may not describe a flow whose verify gate is
  not yet recorded PASS. The v6/v7 onboarding drift existed precisely because three surfaces claimed v7
  before its tasks passed. Claim only what the gate has earned. [folded foundation-version 4]
- (ADD) **Co-specify at every altitude.** The brainstorm move — Diverge (framings + open questions) →
  Converge (draft the whole artifact) → Validate (show the ranked least-sure flag first) — is not
  task-only; it drives foundation (0-setup → PROJECT.md) and milestone (scope.md → MILESTONE.md)
  drafting too. One flag grammar across all three; each guide self-contained (progressive disclosure).
  Elicit before drafting; never draft from thin input. [cospecify-lift — folded foundation-version 7]
- (TDD) **Prose-guide tasks are red→green-testable.** A docs/guideline change is TDD-able by asserting
  content anchors (required section present + ordering) + cross-tree byte-identity (canonical ==
  bundled == dogfood mirror), not behavior. Write the assertion red before the edit; a parity test
  backstops drift. [cospecify-lift: test_cospecify_lift red→green + test_bundle_parity — folded foundation-version 7]
- (ADD) **Verify a gap against the shipped path.** A finding seen through the wrong entry point isn't
  real — bare `add.py init` bypasses `bin/cli.js` (which does the bundling), so "init doesn't bundle the
  skill+book" was a test artifact. Reproduce a gap on the SHIPPED path before scoping a fix.
  [install-onramp — folded foundation-version 8]
- (ADD) **A frozen guard that fails mid-build is fixed in the BUILD output, never the matcher.** Widening
  a frozen matcher inline — even to fix a real false-negative — is self-ratifying a frozen-contract change;
  route it as a human-ratified change-request at test-design time (Rule 3, phase 4), not a silent inline
  edit logged as "no test weakened". [milestone-onboarding-docs — folded foundation-version 8]
- (TDD) **Assert a message-specific phrase, not an ambient token.** A substring that paths/scaffold/harness
  can also contain false-GREENs (a `/add` match off the tmpdir name); assert a phrase only the real
  behavior emits ("not attached to a milestone"). [orphan-task-guard — folded foundation-version 8]
- (TDD) **Prove a publish-time hook without publishing.** Run the hook command as a subprocess and assert
  it executed the guard and exited 0 — it reds on broken/misspelled wiring but cannot prove the registry
  (npm/PyPI) honours the hook; name that wiring-vs-live limit explicitly. [ship-clean — folded foundation-version 9]
- (TDD) **Lint a grammar with two regexes, not one.** A broad attempt-detector ("does this line *try* to be
  a tag/delta?") and a strict valid-shape matcher are distinct abstractions; conflating them either misses
  malformed attempts or false-skips them. [deltas-lint — folded foundation-version 9]
- (ADD) **Spawn a worker's worktree from current HEAD, never a stale base.** A worktree forked off an old
  commit forces the worker to recreate the frozen front byte-identically; after committing the front, verify
  `worktree base == HEAD` before spawning. [deltas-report — folded foundation-version 9]
- (ADD) **Close an unscaffolded milestone by a scope audit, not by building its task list.** A planned-but-
  never-scaffolded milestone (0 TASK.md) may have tasks already superseded/delivered/obsolete by later work;
  audit each against shipped code and keep only the real residue. [ship-clean — folded foundation-version 9]
