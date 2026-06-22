# MILESTONE: Ownership & assignment

goal: a user can assign an owner and assignee to any task or milestone (to self or a named actor) and SEE who owns and works what in status and report — descriptive only, unassigned records unchanged
rationale: sub-milestone of the **team-collaboration** major (confirmed intake 2026-06-22). Milestone 3 of 5. DEPENDS-ON `user-identity` (milestone 2, just shipped) — you cannot assign an owner without a resolved identity to assign; this milestone REUSES that milestone's actor `{name,email,source}` shape and `_whoami` resolver. Relationship to the map: EXTENDS the actor concept from an IMMUTABLE who-DID-it stamp (gate_actor/done_actor — descriptive, historical) to a MUTABLE who-is-RESPONSIBLE assignment (owner/assignee — directive, prospective; reassignable). OVERLAPS nothing live: the cross-milestone "my work" filter + waves-across-active-milestones belong to the sibling `multi-active-UX` and are explicitly OUT here. risk:high — it edits the byte-pinned engine, so the 3-copy + ENGINE_MD5 + lowered-autonomy discipline carries over from milestones 1–2.
stage: mvp · status: active · created: 2026-06-22

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  TWO mutable ownership fields on a task AND a milestone record — `owner` (the actor ACCOUNTABLE
     for the work) and `assignee` (the actor currently WORKING it), each the same `{name,email,source}`
     shape `_whoami` already returns (the two roles MAY differ; either may be absent). Write commands:
     `add.py assign <slug> [--owner "Name <email>"] [--assignee "Name <email>"]` (a bare flag, or a
     bare `assign <slug>` with neither, defaults to the resolved self via `_whoami`) and
     `add.py unassign <slug> [--owner] [--assignee]` (bare `unassign` clears BOTH). Surfacing the
     owner/assignee present-only in `status`, `report`, and the `--json`/report-data machine surfaces.
     All THREE byte-identical `add.py` copies edited in lockstep and ENGINE_MD5 re-established per task.
Out: ACCESS ENFORCEMENT / owner-only gates / separation-of-duties — the assignment is DESCRIPTIVE,
     it NEVER blocks an action (the major's standing rule; same as the actor stamp). The cross-milestone
     "my work" filter + waves spanning active milestones — sibling `multi-active-UX`. A reassignment
     HISTORY / audit log — out (we record the CURRENT owner/assignee, not a changelog; the actor STAMPS
     already give the historical who-did-what). Auto-assignment / load-balancing / notifications — out.
     Owner/assignee on a RELEASE or any record other than task/milestone — out. NO change to the 0–7
     phase flow, the existing actor-stamp format, or any reject/decision semantics (assignment is purely
     additive state).

## Shared decisions & glossary deltas   (living — every task must honor these)
- owner (NEW term) — the actor ACCOUNTABLE for a task/milestone going forward: `{name,email,source}`.
  MUTABLE + directive (reassignable), in contrast to the actor STAMP (gate_actor/done_actor), which is
  immutable + historical. Add to GLOSSARY.
- assignee (NEW term) — the actor currently DOING the work; same shape as owner; MAY differ from owner
  (delegation). Either field may be absent (unassigned). Add to GLOSSARY.
- assign resolution (confirmed) — `assign <slug>` with no role flag defaults BOTH owner+assignee to the
  resolved `_whoami` self (assign-to-self); `--owner`/`--assignee "Name <email>"` set a named actor for
  that role only; `source` of a `--to`-named actor is `"assigned"` (it was neither git-resolved nor an
  override). `unassign <slug>` with no flag clears BOTH; `--owner`/`--assignee` clears one.
- descriptive, not enforcing — assignment records WHO; it NEVER gates an action or checks permissions
  (no owner-only verify). Solo behavior unchanged.
- additive + back-compat — owner/assignee are new OPTIONAL fields; a record without them is valid and
  renders no owner/assignee line (never a placeholder, never a crash); solo/unassigned output is
  byte-identical except for the always-absent-when-unset fields.
- engine-edit discipline — every task edits all THREE add.py copies byte-identically AND re-pins
  ENGINE_MD5 in the SAME commit; parity/pin tests stay green.

## Shared / risky contracts (freeze these first)
- the OWNERSHIP DATA MODEL — the `owner`/`assignee` field shape + WHERE they live (task record AND
  milestone record), the `assign`/`unassign` write grammar (default-self vs `--owner`/`--assignee`
  named, `source: "assigned"` for a named actor), and the additive-not-enforcing rule that keeps every
  existing decision untouched -> owning task `ownership-model`

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] ownership-model    depends-on: none              — the `owner`/`assignee` fields on task + milestone records + `assign`/`unassign` write commands (default-self or `--owner`/`--assignee` named; bare `unassign` clears both); freeze the data-model contract. risk:high.
- [ ] ownership-surface  depends-on: ownership-model   — surface owner/assignee present-only in `status` (current focus) + `report` (per-task + milestone) + the `--json`/report-data machine facts; additive, unassigned output byte-identical. risk:high.

## Exit criteria (observable; map each to the task that delivers it)
- [ ] `add.py assign <task|milestone>` records owner+assignee (default self, or `--owner`/`--assignee "Name <email>"`); `unassign` clears them (bare = both); a record with neither stays valid   (← ownership-model)
- [ ] `status`, `report`, and `--json` surface the owner/assignee present-only; a record with neither renders no owner/assignee (solo/unassigned output unchanged)   (← ownership-surface)

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
