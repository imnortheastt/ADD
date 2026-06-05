# Changelog

All notable changes to the ADD method (`@pilotspace/add` on npm,
`pilotspace-add` on PyPI) are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/); versions follow semver.

## [1.1.0] — 2026-06-05

Production-ready enforcement: the gates are now verified by machinery distinct
from the agent, and any AI agent can follow the method through the CLI alone.

### Added
- **`add.py audit [--json]`** — judgment-free, read-only verification that
  human seams left well-formed records: a named human at every contract freeze,
  exactly one gate outcome per done task, a human reviewer wherever the
  security line carries a `NOTE`/`⚠` marker, no waivers on security. Exit 0
  clean / exit 1 with `{task, code, detail}` findings.
- **Seam audit in CI** — a `seam-audit` job (this repo) plus a copy-paste
  workflow for consumer projects (GETTING-STARTED "Enforce the seams in CI"):
  a malformed seam record fails CI on a machine the agent does not control
  (*never self-gate*, enforced).
- **The mechanized high-risk guard** — declare `risk: high` in a TASK.md
  header and the engine refuses to complete the task (`PASS`/`RISK-ACCEPTED`)
  until the dial is lowered to `autonomy: conservative`; error and audit
  finding `unguarded_high_risk_auto`. Judging *what* is high-risk stays human;
  the declared combination is enforced. `HARD-STOP` is never blocked.
- **Agent portability** — `add.py guide` now names the exact phase-guide file
  to read (`guide  : .claude/skills/add/phases/<n>-<phase>.md`, never a dead
  pointer; additive `"guide"` key in `--json`), and the AGENTS.md/CLAUDE.md
  block routes any agent — Claude, Cursor, Copilot, Codex — through the CLI
  alone.
- **The freeze review checklist** — six ⚠-first lines inside the contract
  phase guide that aim the human's one approval (intent · cases · shape ·
  risk declaration · tests), never a second gate.

### Changed
- GitHub Actions bumped off the deprecated Node-20 runtimes
  (checkout v5, setup-python v6, setup-node v5).
- GETTING-STARTED: CI enforcement section + `guide  :` orientation.

## [1.0.0] — 2026-06-04

First public release: the seven-phase flow (specify → scenarios → contract →
tests → build → verify → observe) driven by one `TASK.md` per task, the
`add.py` state tracker (init · status · guide · report · check · gates ·
milestones · competency deltas · fold), the `add` skill for Claude Code, and
the full method book (`.add/docs/`). Installable via
`npx @pilotspace/add init` or `pip install pilotspace-add`.
