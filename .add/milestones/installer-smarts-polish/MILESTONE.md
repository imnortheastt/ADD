# MILESTONE: Installer Smarts Polish

goal: Close the PTY-only-reachable interactive-coverage gaps the installer-smarts gates disclosed: a reusable PTY test helper that drives clack select/confirm so the agent-select step and the clack happy-path prompts are exercised in CI (today they are node-syntax-checked + logic-unit-tested only).
rationale: sub-milestone — the forward-seed bucket for installer-smarts (mirrors how delta-resolution-polish homes delta-resolution's seeds). Holds the one deduped PTY-helper task that installer-smarts' gates disclosed as PTY-only-reachable; the other 13 archived SPEC deltas stay open as documented backlog.
stage: mvp · status: active · created: 2026-06-18

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  A reusable PTY test helper (committed, shared by both twins) that drives clack
     select/confirm with real keystrokes, plus the CI tests that use it to exercise the
     installer's interactive TUI paths — the agent-select step (D8) and the clack
     happy-path sequence (intro → target → scope → agent → intent).
Out: No change to installer BEHAVIOR (the twins are frozen — this is test-harness only);
     no new runtime dependency (test-only PTY); no engine (add.py) edits; the other 13
     archived SPEC deltas (Cursor/Copilot registry, global-data restore/prune, etc.) stay
     open backlog, not pulled into this milestone.

## Shared decisions & glossary deltas   (living — every task must honor these)
- PTY harness — a test-only helper that allocates a pseudo-terminal so clack enters raw mode
  and the test can send keystrokes; it exercises the EXISTING interactive flow, never changes it.
- backlog seed — this milestone homes a seeded forward delta; tasks here are picked up
  just-in-time, not all built at once.

## Shared / risky contracts (freeze these first)
- PTY-helper API (how a test drives select/confirm + asserts the rendered flow) -> owning task pty-clack-harness

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] pty-clack-harness   depends-on: none   — Reusable PTY test helper driving clack select/confirm; CI-covers the agent-select step + the clack happy-path prompts. (seeded backlog — at ground)

## Exit criteria (observable; map each to the task that delivers it)
- [ ] The clack agent-select step and the happy-path prompt sequence are exercised by a committed CI test (no longer PTY-manual-only)   (verify: python3 -m unittest discover add-method/tooling)   (← pty-clack-harness)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : <add.py / state.json / templates — what shipped, or "untouched">
- skill   : <SKILL.md / phases/* / guides — what shipped, or "untouched">
- book    : <docs/* — what shipped, or "untouched">

### Cross-task evidence   (one row per task)
- <slug> : gate=<PASS|RISK-ACCEPTED> · tests=<n green> · residue=<none|note>

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [ ] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (cite which)
- goal: <restate the milestone goal — and the one evidence line that proves the ship meets it>

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] <step — e.g. open a PR from the Close ship-review above; the human reviews + merges>
- [ ] <step — e.g. export the ship-review to a hand-off doc, e.g. `pandoc CLOSE.md -o close.docx`>
- [ ] <step — e.g. tag / publish / deploy  (human-run, per release.md)>
