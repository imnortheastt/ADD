# MILESTONE: Delta Resolution Polish

goal: polish the delta-resolution machinery from the deltas the first milestone surfaced: a true multi-file commit primitive (all-or-nothing across N files), a --match selector to target a specific open SPEC delta, and a compact --force override for an unrelated open SPEC delta
rationale: <why this scope — the confirmed intake classification (bucket + reason)>
stage: mvp · status: active · created: 2026-06-17

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  <what this milestone delivers>
Out: <explicitly deferred — the anti-scope-creep list>

## Shared decisions & glossary deltas   (living — every task must honor these)
- <cross-cutting rule, named from GLOSSARY.md>

## Shared / risky contracts (freeze these first)
- <contract name> -> owning task <slug>

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] <slug>   depends-on: none     — <one line>
- [ ] <slug>   depends-on: <slug>   — <one line>

## Exit criteria (observable; map each to the task that delivers it)
- [ ] User can <observable behavior>        (← <slug>)
