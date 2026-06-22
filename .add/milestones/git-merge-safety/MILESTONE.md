# MILESTONE: Git-merge safety

goal: a team merging parallel branches never silently corrupts .add/state.json — ADD recognizes a conflicted or inconsistent state at load and via a doctor command, and guides reconciliation instead of crashing or proceeding on bad data
rationale: sub-milestone of the **team-collaboration** major (confirmed intake 2026-06-22). Milestone 4 of 5. The major is git-native multi-user with NO server, so the #1 failure mode is two users writing `.add/state.json` on parallel branches → a merge that either crashes ADD (conflict markers = invalid JSON) or silently proceeds on inconsistent data. This milestone is the SAFETY NET for exactly that — it is the direct answer to the live parallel-writer clobber we hit during M2/M3. Relationship to the map: DEPENDS-ON the multi-active state model (M1, the schema it validates); ORTHOGONAL to user-identity (M2) + ownership-assignment (M3); OVERLAPS nothing live. Scope altitude confirmed with the human (2026-06-22): GUARD + DOCTOR (lean safety net) — NOT merge-friendly reformat, NOT a custom git merge driver (both deferred, see Out). risk:high — it edits the byte-pinned engine (the load path), so the 3-copy + ENGINE_MD5 + lowered-autonomy discipline carries over.
stage: mvp · status: active · created: 2026-06-22

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  A merge-AWARE load guard — when `.add/state.json` carries git conflict markers
     (`<<<<<<<` / `=======` / `>>>>>>>`) or is otherwise unparseable, ADD fails LOUD with a
     merge-SPECIFIC, actionable message (`state_conflicted` — name the markers + how to reconcile),
     distinct from the existing generic `state_invalid`. A `doctor` command that PROACTIVELY
     validates state mergeability + integrity (parseable · conflict-marker-free · referential:
     every active_milestone/active_task points to a real record, every task's `milestone` exists)
     and reports PASS or each specific problem + its fix — the check a user runs after a merge.
     All THREE byte-identical `add.py` copies edited in lockstep + ENGINE_MD5 re-established per task.
Out: MERGE-FRIENDLY SERIALIZATION (sort_keys / deterministic reorder so independent adds merge
     line-cleanly) — deferred (human-chosen lean scope; a future task/milestone, seeded as a delta).
     A CUSTOM GIT MERGE DRIVER / `.gitattributes` semantic 3-way merge — deferred (per-clone config,
     brittle; over-engineered for a no-server MVP). State SHARDING (per-milestone/per-task files) —
     deferred. AUTO-REPAIR / auto-reconcile of a conflicted state — OUT (doctor REPORTS + guides; the
     human resolves — never an engine auto-mutate of a diverged state). ANY server / hosted backend.
     NO change to the 0–7 phase flow, the state schema, or existing decision semantics.

## Shared decisions & glossary deltas   (living — every task must honor these)
- state_conflicted (NEW reject code) — a load-time failure raised when state.json contains git
  conflict markers: distinct from `state_invalid` (generic parse/IO failure) so the message can be
  merge-SPECIFIC. Add to the reject-code vocabulary.
- doctor (NEW command) — a read-only diagnostic that validates state integrity + mergeability and
  reports; it NEVER mutates state (no auto-repair). Add to GLOSSARY.
- detect, never auto-resolve — every check REPORTS and guides; reconciliation is the human's (mirrors
  the major's descriptive-not-enforcing posture). A diverged state is surfaced, never silently fixed.
- fail-loud + actionable — a guard message NAMES the file + the concrete next step (resolve markers /
  `git checkout --ours`/`--theirs` / `add.py doctor`), never a raw traceback (design-for-failure).
- engine-edit discipline — every task edits all THREE add.py copies byte-identically AND re-pins
  ENGINE_MD5 in the SAME commit; parity/pin tests stay green.

## Shared / risky contracts (freeze these first)
- the CONFLICT-DETECTION rule + `state_conflicted` message contract — what byte pattern counts as a
  git conflict marker, where the check sits in the load path (BEFORE the JSON parse so a marker'd file
  is recognized as a conflict, not generic corruption), and the exact actionable message -> owning task `merge-guard`

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] merge-guard    depends-on: none           — detect git conflict markers in state.json at load → fail with a merge-specific `state_conflicted` message (markers + reconciliation steps), distinct from generic `state_invalid`; the load-time safety net. risk:high.
- [ ] state-doctor   depends-on: merge-guard     — a read-only `add.py doctor` command that validates state integrity + referential consistency (parseable · conflict-free · active refs → real records · task.milestone exists) and reports PASS or each problem + its fix; never mutates state. risk:high.

## Exit criteria (observable; map each to the task that delivers it)
- [ ] a state.json with git conflict markers makes every state-loading command fail with a clear `state_conflicted` message (file + how to reconcile), not a crash or a generic "corrupt"   (← merge-guard)
- [ ] `add.py doctor` validates a healthy state as PASS and reports each specific problem + fix on a conflicted/inconsistent state, mutating nothing   (← state-doctor)

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
