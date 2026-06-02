# CONVENTIONS  (survivor layer — set once, kept for the whole project)

Language/framework:
  - Tooling: Python 3.12+ (standard library only — no third-party packages).
  - Installer: Node.js >= 16 (built-in modules only).
  - Method content: Markdown (the skill + the AIDD book).

Folders:
  - `add-method/`            the shippable npm package (`@mrq/add`)
    - `skill/add/`           thin router SKILL.md + `phases/*.md` (progressive disclosure)
    - `tooling/`             `add.py` (scaffolder + state tracker) + `templates/` + `test_add.py`
    - `bin/cli.js`           the `npx @mrq/add init` installer
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
