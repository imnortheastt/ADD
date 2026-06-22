# MILESTONE: User Identity

goal: ADD resolves a git-native actor (whoami: git config user.name/email, OS-user fallback) and stamps WHO performed each human-owned action — contract freeze, verify gate, milestone-done, lock, release — as a structured actor field alongside today's free-text, giving a multi-user team an auditable who-decided-what trail. Descriptive only (no access enforcement); solo behavior unchanged; the byte-pinned engine edited in lockstep across all 3 copies.
rationale: sub-milestone of the **team-collaboration** major (confirmed intake 2026-06-22). Milestone 2 of 5: it opens the MULTI-USER half — milestone 1 (state-model-reshape) gave the engine N parallel-active milestones; this gives each human-owned action a git-native ACTOR so a team has an auditable trail. PREREQUISITE for the ownership-assignment sibling (you can't assign an owner without an identity to assign). EXTENDS the existing free-text actor stamps (`approved by <name>` · `Reviewed by:` · lock's `locked_by`) rather than inventing a new identity system. OVERLAPS nothing live. risk:high — it edits the byte-pinned engine, so lowered autonomy + the 3-copy + ENGINE_MD5 discipline carry over from milestone 1.
stage: mvp · status: active · created: 2026-06-22

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  A git-native ACTOR resolver — `_whoami` resolves the current actor from `git config user.name`/
     `user.email`, falling back to the existing `getpass.getuser()` OS user (the basis `lock` already
     uses). `add.py whoami` shows the resolved actor; an optional `--set` stores an ADD-level override.
     A single STAMP seam that records a STRUCTURED actor (name + email + source) on every human-owned
     seam — contract freeze, verify gate, milestone-done, lock, release — ALONGSIDE today's free-text
     line (additive; old stamps stay valid). All THREE byte-identical `add.py` copies edited in lockstep
     and ENGINE_MD5 re-established per task.
Out: OWNERSHIP / assignment fields (who OWNS a task/milestone) — sibling `ownership-assignment`. Any
     ACCESS ENFORCEMENT / permissions / separation-of-duties gate (the actor is DESCRIPTIVE, never an
     authorization check) — explicitly not this milestone. Git-merge conflict tooling — sibling
     `git-merge-safety`. Multi-active UX — sibling `multi-active-UX`. ANY server / hosted identity
     (decided: git-native only). NO change to the 0–7 phase flow or the existing free-text stamp
     format (the structured actor is ADDITIVE, never a replacement).

## Shared decisions & glossary deltas   (living — every task must honor these)
- actor (NEW term) — the git-native identity performing a human-owned action: `{name, email, source}`
  where source ∈ {git, os, override}. Resolved by `_whoami`. Add to GLOSSARY.
- identity source priority (confirmed) — `git config user.name`/`user.email` FIRST, then `getpass.getuser()`
  OS-user fallback; an optional `add.py whoami --set` override wins when present. Zero-config + git-native.
- additive stamping — the structured actor is recorded ALONGSIDE the existing free-text (`approved by <name>`,
  `Reviewed by:`, `locked_by`); the free-text format is byte-unchanged so every audit regex + the
  decide-digest extractor keep working. Backward-compatible: an un-stamped legacy record stays valid.
- descriptive, not enforcing — stamping records WHO; it NEVER blocks an action or checks permissions
  (no separation-of-duties gate this milestone). Solo behavior unchanged.
- engine-edit discipline — every task edits all THREE add.py copies byte-identically AND re-pins
  ENGINE_MD5 in the SAME commit (carried from state-model-reshape); parity/pin tests stay green.

## Shared / risky contracts (freeze these first)
- the `_whoami` RESOLUTION rule (source priority · the `{name,email,source}` shape · fail-soft when git
  config is absent/partial) -> owning task `actor-identity`
- the STAMP seam (where the structured actor is written on each human seam, and the additive-not-replace
  rule that keeps the free-text format byte-identical) -> owning task `actor-stamping`

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] actor-identity    depends-on: none            — `_whoami` resolver (git config → OS-user fallback, fail-soft) returning `{name,email,source}` + `add.py whoami` (show; `--set`/`--unset` override stored in state); freeze the resolution contract. risk:high.
- [ ] actor-stamping    depends-on: actor-identity   — one stamp seam records the structured actor on every human seam (contract freeze · verify gate · milestone-done · lock · release) ALONGSIDE the unchanged free-text; backward-compatible read. risk:high.
- [ ] identity-in-status depends-on: actor-stamping  — surface the resolved actor in `status` (a `you : <name> <email> (source)` line) + the structured actor in the relevant `--json` / report surfaces; additive, solo output byte-identical when unset. risk:high.

## Exit criteria (observable; map each to the task that delivers it)
- [ ] `add.py whoami` reports the current git-native actor (git config name/email, OS-user fallback); `--set`/`--unset` overrides it   (← actor-identity)
- [ ] a contract freeze, a verify gate, a milestone-done, a lock, and a release each record a STRUCTURED actor alongside the unchanged free-text stamp; a legacy un-stamped record stays valid   (← actor-stamping)
- [ ] `status` shows the current actor and the structured actor reaches the `--json`/report surface; with no actor configured the output degrades cleanly (solo unchanged)   (← identity-in-status)

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
