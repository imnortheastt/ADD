# MILESTONE: Foundation-fold follow-ups

goal: Clear the 3 actionable deltas the v10/v12 fold routed out of the foundation: surface the unlocked→lock step in status, stop truncating multi-line deltas, and collapse the duplicated delta-grammar regex to one source.
stage: mvp · status: active · created: 2026-06-04

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

> Provenance: these three are the **actionable deltas** the v10/v12 foundation fold
> routed OUT of the foundation as follow-up tasks (foundation-version 9, 2026-06-04).
> A maintenance milestone — no new features, just close the routed debt.

## Scope
In:  (1) `status` surfaces the unlocked→lock step when `setup.locked is False`;
     (2) one source of truth for the delta-grammar regex (kill the duplicated `_DELTA_RE`);
     (3) `deltas`/report renders a multi-line open delta in full (no first-line truncation).
Out: any new engine feature, any setup/lock behavior change, the recurring
     words-exist≠method-works enforcement gap (a standing limitation, not this milestone).

## Shared decisions & glossary deltas   (living — every task must honor these)
- All three touch `add.py` (the engine, unfrozen now that v12 is closed). Each is a
  small, additive, test-first change; none alters the lock/setup contract v12 froze.

## Shared / risky contracts (freeze these first)
- the delta-grammar regex (single canonical `_DELTA_RE`) -> owning task `delta-grammar-dedup`
  (both `delta-grammar-dedup` and `deltas-multiline-render` read it; dedup freezes it first)

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] status-lock-hint       depends-on: none                — `cmd_status`: when `state.setup.locked is False`, print a hint to review `SETUP-REVIEW.md` and run `add.py lock`, not the generic "run /add". [from autonomous-setup-guide ADD delta]
- [ ] delta-grammar-dedup    depends-on: none                — collapse the duplicated module-level `_DELTA_RE` in `cmd_deltas` to reuse the single canonical delta-grammar regex; a guard test asserts one source. [from deltas-report ADD delta]
- [ ] deltas-multiline-render depends-on: delta-grammar-dedup — `deltas`/report renders the FULL multi-line delta text, not just the first line; add coverage for the multi-line shape. [from deltas-report TDD delta]

## Exit criteria (observable; map each to the task that delivers it)
- [ ] `add.py status` on an unlocked setup (`setup.locked == False`) prints a hint naming `SETUP-REVIEW.md` + `add.py lock` (not the generic next-step)        (← status-lock-hint)
- [ ] `add.py` has exactly ONE delta-grammar regex; `cmd_deltas` reuses it (no second `_DELTA_RE`), guarded by a test                                              (← delta-grammar-dedup)
- [ ] `add.py deltas` renders a multi-line open delta in full (no first-line truncation); a test covers the multi-line shape                                       (← deltas-multiline-render)
