# MILESTONE: Multi-active state model + migration (team-collaboration foundation)

goal: ADD's engine tracks N truly-parallel active milestones — state.json holds a SET of active milestones, each with its own active task — with a backward-compatible migration from the single-active schema and the ENGINE_MD5 pin deliberately re-established.
rationale: new-major **team-collaboration** (git-native, multi-user, N parallel-active milestones — confirmed intake 2026-06-22). This is milestone 1 of that major: the engine-state foundation every later slice (user-identity · ownership-assignment · git-merge-safety · multi-active-UX) depends on. Relationship to the map: EXTENDS the v4-1 machine-state-json line (it reshapes the same state.json) and is a PREREQUISITE for the rest of the team-collaboration siblings; OVERLAPS nothing live (no active milestone's goal covers parallel activation). The rare major that intentionally edits the byte-pinned engine — so it carries risk:high + lowered autonomy.
stage: mvp · status: active · created: 2026-06-22

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  A multi-active state.json schema — `active_milestones` (a SET/list) replacing the scalar
     `active_milestone`, and a per-milestone `active_task` replacing the single global `active_task`.
     A forward, idempotent, fail-soft MIGRATION that upgrades any existing single-active state
     (the N=1 case) with zero data loss on first load. A single ACCESSOR seam (read/write helpers)
     that every one of the ~20 engine call sites routes through, so single-active behavior is just
     N=1 and stays byte-for-decision identical for solo users. Multi-active COMMANDS: activate /
     deactivate a milestone in the set, switch the active task within a milestone, and a `status`
     view that renders the active set as parallel streams. All THREE byte-identical `add.py` copies
     (tooling · .add/tooling · _bundled/tooling) edited in lockstep and the ENGINE_MD5 pin
     re-established (re-pinned, never bypassed).
Out: User IDENTITY / actor stamping (`whoami`) — sibling `user-identity`. Task/milestone OWNERSHIP
     or assignment fields — sibling `ownership-assignment`. Git-merge conflict tooling / state
     sharding / divergence guards — sibling `git-merge-safety`. Multi-active UX beyond a basic
     parallel `status` (waves spanning active milestones, "my work" filters) — sibling
     `multi-active-UX`. ANY server / daemon / hosted backend (decided: git-native only). NO change
     to the per-task 0–7 phase flow or any phase guide. NO change to release/graduation semantics
     beyond making them read the active SET through the accessor.

## Shared decisions & glossary deltas   (living — every task must honor these)
- active set (NEW term) — `active_milestones`: the list of milestones a project has activated at
  once; the scalar `active_milestone` becomes "the set with one member". Add to GLOSSARY.
- per-milestone active task (NEW term) — each active milestone carries its own `active_task`; the
  old global `active_task` migrates to the active task of the migrated single active milestone.
- superset migration — the upgrade is additive and idempotent: old single-active state loads as the
  N=1 case, never a destructive rewrite; re-running the migration is a no-op (design-for-failure:
  load stays fail-soft, a malformed/old state never crashes the engine).
- backward-compatible solo behavior — with exactly one active milestone, every command's decisions
  are identical to today (no regression for single-user projects); this is a verify check on each task.
- engine-edit discipline — this milestone INTENTIONALLY edits the pinned engine. Every task edits
  all THREE add.py copies byte-identically AND re-pins ENGINE_MD5 in the SAME commit, so the 3-tree
  parity + pin tests stay GREEN throughout the milestone (the pin tracks HEAD per task; it is never
  lifted or deferred). The final `engine-repin-parity` task is therefore a consolidated parity AUDIT
  + parity-test hardening (assert the new multi-active invariants), not a deferred re-pin.

## Shared / risky contracts (freeze these first)
- the multi-active state.json SCHEMA + migration rule (field shapes, the N=1 upgrade, idempotency,
  fail-soft load) -> owning task `state-schema-migration`
- the active-milestone / active-task ACCESSOR API (the single read/write seam every call site uses)
  -> owning task `active-accessors`

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] state-schema-migration  depends-on: none                   — Define the multi-active state.json schema + the idempotent, fail-soft forward migration from single-active (N=1); freeze the schema contract. risk:high.
- [ ] active-accessors        depends-on: state-schema-migration — Add the read/write accessor seam for active milestone(s)/task and route all ~20 engine call sites through it; single-active stays byte-for-decision identical. risk:high.
- [ ] multi-active-commands   depends-on: active-accessors       — `activate`/`deactivate`/`use` operate on the active SET: add/remove a milestone, switch the active task within one; refuse activating an unknown/done milestone. risk:high.
- [ ] parallel-status-view    depends-on: multi-active-commands  — `status` renders the active SET as parallel streams (per-milestone active task + phase), not a single active line. risk:high.
- [ ] engine-repin-parity     depends-on: parallel-status-view   — Consolidated parity AUDIT: assert all 3 add.py copies byte-identical, ENGINE_MD5 current, and harden the parity test to cover the new multi-active invariants. risk:high.

## Exit criteria (observable; map each to the task that delivers it)
- [ ] An existing single-active `.add/` project loads and auto-migrates to the multi-active schema with zero data loss; re-running the migration is a no-op   (← state-schema-migration)
- [ ] Every engine command reads/writes the active milestone(s) and active task through the accessor seam; with one active milestone the engine's decisions are identical to today   (← active-accessors)
- [ ] A user can activate ≥2 milestones at once and switch the active task within each; activating an unknown or done milestone is refused   (← multi-active-commands)
- [ ] `status` shows the active set as parallel streams, each with its own active task + phase   (← parallel-status-view)
- [ ] All THREE add.py copies stay byte-identical and ENGINE_MD5 is current and green; the parity test asserts the new multi-active invariants (the engine edit is pinned, not bypassed)   (← engine-repin-parity)

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
