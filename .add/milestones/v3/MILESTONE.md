# MILESTONE: Correct · Shippable

goal: Make ADD correct under misuse and safe to publish: refuse unsafe gates, guard the docs/build invariants, ship clean
stage: mvp · status: active · created: 2026-05-29

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  the correctness gaps v2 named but deferred — the gate refuses an already-expired
     waiver (not just `check` later); a guard fails on non-English text in the book; the
     guideline block re-syncs off a stable token, not fragile prose; the npm package
     cannot be published from a dirty/incomplete tree; and a newcomer can open the
     foundation with one command (`add.py project`). Theme: the engine refuses unsafe
     states, guards its own invariants, and the package ships clean.
Out: pure ergonomics — `archived`/restore, a `--depends-on` editor, `guide --verbose`
     (a later adoption milestone); the 3-diagram re-render through the pipeline +
     `render.sh` (low-priority provenance, deferred); the FINDING-C boundary (engine
     grades structure, human grades section content — revisit only if it ever feels
     wrong); Vietnamese onboarding (descoped in v1-1).

## Shared decisions & glossary deltas   (living — every task must honor these)
- **Fail-closed, read-only stays the rule** (carried from v2): a new guard FAILS on a
  missing/unparseable/ambiguous input, never silently passes; `check` and guards never
  mutate state.
- **Every new guard is a behavioral proof, not a source-grep** (v2 circularity bar): the
  test must go red for a REAL regression (an actual non-ASCII char, an actual past-dated
  waiver), not merely because a file was edited.
- **Engine guards cheap structural invariants; the human owns judgement** (v2 boundary):
  the ASCII guard checks bytes, not meaning; it does not read the Story for content.
- All design forks are decided with the human (AskUserQuestion) before a contract freezes.

## Shared / risky contracts (freeze these first)
- the gate-time waiver rule: refuse-vs-warn, and whether `gate` reuses `check`'s expiry
  predicate so the two can never diverge -> gate-time-waiver
- the ASCII-guard scope: which paths it covers (docs/ only? tooling too?) and the exact
  allowed set (printable ASCII + newline) -> ascii-docs-guard

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] gate-time-waiver         depends-on: none   — `gate RISK-ACCEPTED --expires <past>` is refused at sign time (defense in depth)
- [ ] ascii-docs-guard         depends-on: none   — a test fails on any non-ASCII byte in the book (English-only: assert → prove)
- [ ] stable-guideline-markers depends-on: none   — `sync-guidelines` matches on an `ADD:BEGIN`/`ADD:END` token, not surrounding prose
- [ ] prepublish-guard         depends-on: none   — `prepublishOnly` runs the manifest guard so a dirty/incomplete tree cannot publish
- [ ] project-cmd              depends-on: none   — `add.py project` prints/opens `.add/PROJECT.md` (the "read first" foundation)

## Exit criteria (observable; map each to the task that delivers it)
- [ ] `gate RISK-ACCEPTED` with an already-past `--expires` is refused, not stored        (← gate-time-waiver)
- [ ] A non-ASCII character in any book file turns the suite red                          (← ascii-docs-guard)
- [ ] Editing prose adjacent to the guideline markers does not break `sync-guidelines`    (← stable-guideline-markers)
- [ ] `npm publish` from a dirty/incomplete tree is blocked by the guard                  (← prepublish-guard)
- [ ] `add.py project` prints (or opens) the foundation in one command                    (← project-cmd)
