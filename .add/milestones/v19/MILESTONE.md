# MILESTONE: Guard hygiene — single-source pins, fence-aware slicing

goal: tooling guards become single-source and truncation-proof — shipped as ADD's first real parallel wave (WAVE.md proof-in-anger)
rationale: sub-milestone — two independent tooling tasks under one versioned goal with a shared exit criterion (the wave lifecycle itself); both close [TDD] deltas from the wave-ledger / wave-status-hint loop
stage: mvp · status: active · created: 2026-06-07

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  shared-engine-pin — one ENGINE_MD5 source (`engine_pin.py`), 5 importers; a
     legitimate engine change re-aims ONE line, not five (closes the [TDD] delta
     from wave-status-hint; second stale-sweep was dd5b665).
     fence-aware-section — one fence-aware section slicer (`md_section.py`); the
     4 guard files that slice prose at "\n## " import it, so a fenced template
     containing "## " can no longer silently truncate a words-exist guard
     (closes the [TDD] delta from wave-ledger).
Out: any add.py change (engine untouched — both tasks are test-infrastructure
     only); bundle/dogfood trees (tooling tests are canonical-only — bundle
     ships add.py + templates, no tests); fixture-writer files
     (test_planned_hint.py, test_report.py write "## " fixtures, they do not
     slice — not the hazard).

## Shared decisions & glossary deltas   (living — every task must honor these)
- run as ONE wave of 2 workers (worktree isolation; WAVE.md lifecycle end-to-end:
  open → consume → digest → delete)
- KNOWN integration point: `test_review_checklist.py` is touched by BOTH tasks
  (ENGINE_MD5 pin ~line 24 · section slicer ~line 32) — merge order
  shared-engine-pin → fence-aware-section; integration Verify watches that file
  explicitly
- new helper modules use distinct names (`engine_pin.py` · `md_section.py`) — no
  file-level overlap beyond the declared one
- "pin" keeps its established meaning (an absolute recorded constant a guard
  asserts against) — no new glossary terms

## Shared / risky contracts (freeze these first)
- engine_pin.ENGINE_MD5 (the single source) -> owning task shared-engine-pin
- md_section section-slicing semantics -> owning task fence-aware-section

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] shared-engine-pin    depends-on: none — one ENGINE_MD5 source, five importers
- [ ] fence-aware-section  depends-on: none — fence-aware slicer, four importers

## Exit criteria (observable; map each to the task that delivers it)
- [ ] an engine change re-aims exactly ONE pin line; no test file holds its own
      hash literal                                          (← shared-engine-pin)
- [ ] a fenced "## " inside a guarded section no longer truncates the slice —
      proven by a red-first test                            (← fence-aware-section)
- [ ] WAVE.md lifecycle completed end-to-end and digested into ## Wave log here;
      integration Verify recorded on the declared overlap   (← wave close)
