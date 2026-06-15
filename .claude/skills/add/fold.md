# Consolidating deltas — how the foundation self-improves

This **closes the loop**. `deltas.md` lets a task EMIT learnings (`open` lessons learned in its
OBSERVE phase); the retrospective consolidation gathers the confirmed ones and writes them into a **versioned foundation**,
so `DDD · SDD · UDD · TDD · ADD` sharpen across milestones instead of drifting.

You (the AI) **gather and propose**; the **human confirms**; you then write the **append-only** consolidation.
You never self-approve a consolidation — consolidating is judgment (see the verify/observe decision point).

## When to consolidate

At **milestone close** (the natural "version bump to the foundation"), or **on demand** when open
deltas have piled up. This is a convention, not a command — there is no `add.py fold`; the consolidation
lives here so the engine stays judgment-free.

## The ritual

1. **Gather** — scan every task's §7 OBSERVE block for lesson-learned lines still `open` (`add.py deltas` reads them by the machine heading).
2. **Group** — bucket them by competency (`DDD · SDD · UDD · TDD · ADD`).
3. **Propose** — for each, draft the exact foundation edit (see routing) and show the human.
4. **Confirm** — the human accepts or declines each delta. No write happens without this.
5. **Write** — prepend the accepted edits at the top (newest-first), flip each delta's status, and bump the version.

## Consolidation routing (every competency has a home)

| competency | consolidates into | how |
|------------|-----------|-----|
| `DDD` | `PROJECT.md` §Domain (DDD) | refine/append a model bullet |
| `SDD` | `PROJECT.md` §Spec / Living Document (SDD) | refine/append a settled-vs-open line |
| `UDD` | `PROJECT.md` §Users (UDD) | refine/append a UX line |
| `TDD` | `CONVENTIONS.md` | append a testing convention (no PROJECT.md section — it is the engine) |
| `ADD` | `CONVENTIONS.md` | append a build/harness convention (likewise the engine) |

**Every** consolidation — whatever the competency — ALSO prepends one row at the TOP of `PROJECT.md` **§Key Decisions** (newest-first)
(date · decision · why · outcome): the universal, auditable trail of what the foundation learned.

## Status transitions & version

- on **confirm**: the delta moves `open` → `folded` (and its edit is prepended at the top of the routed target, newest-first).
- on **decline**: the delta moves `open` → `rejected` and is **left in place** — never deleted —
  so "we considered this and chose not to act" stays auditable.
- a consolidation is **append-only (newest-first)**: it PREPENDS new bullets/rows at the top and never silently rewrites existing foundation text — EXCEPT via the recorded **compaction door** (`compact-foundation.md`): eligible (shipped + zero open residues) stable entries collapse upward into a rolled-up settled line at the tail. Reject: `open-residue-version` · `trail-loss` · `wrong-order`.
- each consolidation session **bumps** the `foundation-version:` marker in `PROJECT.md` by one (monotonic int).

## Reject codes (the AI is first check, the human the backstop)

<reject_codes>
- `no_open_deltas` — nothing is `open` anywhere. The ritual is a no-op; do **not** bump the version.
- `unconfirmed_fold` — a write was attempted without recorded human confirmation. The AI proposes;
  it never self-approves one. Stop and get confirmation.
- `unroutable_delta` — a delta's competency is not one of the five, so it has no consolidation target. Fix the
  delta (it is malformed per `deltas.md`) before consolidating.
</reject_codes>

## Worked example (from this repo's own history)

The `competency-deltas` task closed its OBSERVE with two deltas — the homeless ones, `TDD`/`ADD`,
which have no PROJECT.md section:

```
- [ADD · open] dogfood .add/tooling template can silently diverge from canonical (evidence: md5 mismatch this build)
- [TDD · open] structural tests guard canonical artifacts but not their dogfood twins (evidence: scope-loop note + this build)
```

At the next consolidation the human confirms both. Routing sends each to `CONVENTIONS.md` (a "sync the dogfood
tree + assert md5 parity" convention), appends a §Key Decisions row for each, flips them to `folded`,
and bumps `foundation-version` 1 → 2. The two competencies the foundation never tracked before now
have a home — which is exactly why v5 routes TDD/ADD to `CONVENTIONS.md`.
