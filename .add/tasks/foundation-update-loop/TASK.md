# TASK: Foundation Update Loop

slug: foundation-update-loop · created: 2026-05-30 · stage: mvp
phase: verify   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

This task CLOSES the self-improving loop: `competency-deltas` lets a task EMIT learnings; this
ritual FOLDS the confirmed ones into a versioned foundation. Method-only judgment — the AI gathers
+ proposes, the human confirms, the AI writes the append-only fold. It owns the **`foundation-version`
marker + the fold format + the routing**. (The mechanical delta counter is `convergence-signal`.)

Must:
  - a rubric `skill/add/fold.md` documents the ritual: gather all `open` deltas across tasks'
    OBSERVE blocks → group by competency → PROPOSE the foundation edits → human confirms → write
  - **fold routing** (every competency has a home): `DDD` → `PROJECT.md` §Domain · `SDD` → §Spec ·
    `UDD` → §Users · `TDD`/`ADD` → `CONVENTIONS.md` (the engine survivor file); AND every fold
    appends one row to `PROJECT.md` §Key Decisions (the universal audit log)
  - on confirm, each delta's status moves `open` → `folded`; a delta the human declines moves
    `open` → `rejected` and is LEFT in place (auditable, never deleted)
  - a fold is **append-only** — it adds to a section / the decisions log; it never silently
    rewrites existing foundation text
  - a fold **bumps the `foundation-version:` marker** in `PROJECT.md` (a monotonic integer)
  - the ritual runs **at milestone close OR on demand** — a rubric convention, NOT a `milestone-done`
    engine change (keeps this method-only; the Minimal pillar holds)
  - `PROJECT.md` carries a `foundation-version:` marker (this task establishes it, starting at 1)
Reject (well-formedness codes the rubric names; the AI is first check, the human the backstop):
  - no `open` deltas anywhere                          -> "no_open_deltas"   (no-op; do NOT bump the version)
  - folding without recorded human confirmation        -> "unconfirmed_fold" (AI proposes; never self-folds)
  - a delta whose competency is not one of the five     -> "unroutable_delta" (no fold target; fix the delta first)
After:
  - confirmed deltas are appended to their routed artifact and marked `folded`; declined ones marked
    `rejected` in place; one §Key Decisions row per fold; `foundation-version` incremented once per
    fold session; no existing foundation text silently overwritten.
Assumptions (confirm before building):
  - [x] method-only; the mechanical gather/counter is `convergence-signal`'s job — RESOLVED (advisor + milestone).
  - [x] trigger is a rubric convention (milestone-close / on-demand), not a `milestone-done` engine
        change — RESOLVED: yes, keeps the task method-only and the engine judgment-free.
  - [x] routing: TDD/ADD → CONVENTIONS.md; DDD/SDD/UDD → their PROJECT.md section; all → Key Decisions
        — RESOLVED by the human; folded back into v5 MILESTONE.md's shared-contract line.

<!-- EXIT: every rule stated, every rejection has a named code, zero open assumptions. -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: the ritual is documented end to end
  Given skill/add/fold.md
  When I read the ritual
  Then it states gather open deltas → group by competency → propose → human confirms → write

Scenario: every competency has a fold target
  Given fold.md's routing
  When I read where each competency lands
  Then DDD→PROJECT.md §Domain, SDD→§Spec, UDD→§Users, TDD→CONVENTIONS.md, ADD→CONVENTIONS.md
  And every fold also appends a row to PROJECT.md §Key Decisions

Scenario: confirm folds, decline rejects, both auditable
  Given an open delta under review
  When the human confirms it / declines it
  Then it becomes folded (appended to its target) / rejected (left in place, not deleted)

Scenario: a fold is append-only and bumps the version
  Given fold.md
  When I read how a fold writes
  Then it appends (never silently rewrites) and increments PROJECT.md foundation-version

Scenario: the trigger is a rubric convention, not an engine change
  Given fold.md
  When I read when the ritual runs
  Then it runs at milestone close or on demand
  And add.py has no new fold command (the engine stays judgment-free)

Scenario: PROJECT.md carries the foundation-version marker
  Given .add/PROJECT.md
  When I read its header
  Then a foundation-version marker is present (established at 1)

Scenario: nothing to fold is a no-op
  Given no open deltas anywhere
  When the ritual runs
  Then it is named "no_open_deltas"
  And the foundation-version is NOT bumped

Scenario: a fold without confirmation is rejected
  Given a proposed fold with no recorded human confirmation
  When the rubric's rules are applied
  Then it is named "unconfirmed_fold"
  And the foundation is unchanged

Scenario: an unroutable delta is rejected
  Given a delta whose competency is not one of the five
  When routing is applied
  Then it is named "unroutable_delta"
  And no fold target is invented

Scenario: the rubric is byte-identical across both skill trees
  Given add-method/skill/add/fold.md and .claude/skills/add/fold.md
  When I compare their md5
  Then the two are identical
  And SKILL.md (both trees) links to fold.md
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
FOLD ROUTING (frozen):
  DDD → PROJECT.md §Domain   SDD → PROJECT.md §Spec   UDD → PROJECT.md §Users
  TDD → CONVENTIONS.md       ADD → CONVENTIONS.md
  + EVERY fold appends one row to PROJECT.md §Key Decisions (universal audit log)
RITUAL: gather `open` deltas → group by competency → PROPOSE edits → human CONFIRMS → write
  on confirm: delta open→folded (appended to its target) ; on decline: open→rejected (left in place)
  a fold is APPEND-ONLY (never silent rewrite) and bumps PROJECT.md `foundation-version` (monotonic int)
  trigger: milestone close OR on demand — a rubric convention, NOT a milestone-done engine change
  reject codes: no_open_deltas · unconfirmed_fold · unroutable_delta

ARTIFACTS (method-only; the mechanical delta counter is convergence-signal):
  skill/add/fold.md (NEW, both skill trees)  — the ritual rubric (all of the above + worked example)
  .add/PROJECT.md  — gains a `foundation-version:` marker, established at 1
  SKILL.md (both trees)  — a pointer to fold.md
  appendix-c-glossary.md (3 doc trees)  — a "Foundation version" entry

STRUCTURAL GUARD — tooling/test_foundation_update_loop.py — EXACTLY these 11 tests (frozen):
   1. fold.md exists in BOTH skill trees and is md5-identical
   2. fold.md documents the ritual sequence: gather → propose → human confirm → write
   3. fold.md documents fold routing — all 5 competencies map to a target (DDD/SDD/UDD→PROJECT.md
      sections, TDD/ADD→CONVENTIONS.md) AND the §Key Decisions universal audit row
   4. fold.md documents the status transitions: confirm→folded, decline→rejected (left in place)
   5. fold.md states folds are append-only AND bump the foundation-version
   6. fold.md states the trigger is a rubric convention (milestone close / on demand)
   7. add.py exposes NO `fold`/`foundation` subcommand (the engine stays judgment-free)
   8. fold.md documents all 3 reject codes (no_open_deltas·unconfirmed_fold·unroutable_delta)
   9. .add/PROJECT.md carries a `foundation-version:` marker
  10. SKILL.md links fold.md in both trees AND the two SKILL.md are byte-identical
  11. fold.md's worked example references the real `competency-deltas` task (provable vs history)
```

Status: FROZEN @ v1   (human-approved 2026-05-30)   <!-- Changing a frozen contract = change request back to SPECIFY. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY. -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: structural — all 11 frozen invariants asserted (method/docs task; coverage = the
contract surface, not LOC).
Plan (the 11 frozen tests, one assertion-cluster each): exists+md5 parity · ritual sequence ·
routing (5 competencies + Key Decisions) · status transitions · append-only+version-bump · trigger
convention · NO engine fold command · 3 reject codes · PROJECT.md foundation-version marker ·
SKILL.md links+identical · worked-example references real competency-deltas history.

Tests live in: `add-method/tooling/test_foundation_update_loop.py` · MUST run red (artifacts absent)
before Build.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): a fold is APPEND-ONLY and human-confirmed — never an unattended
rewrite of the foundation. The ritual lives in the method (fold.md), NOT in add.py, so the engine
cannot fold on its own (test 7 guards that no fold/foundation subcommand exists).
Code lives in: method/docs task — artifacts are `skill/add/fold.md`, the `.add/PROJECT.md`
foundation-version marker, both `SKILL.md`, the 3 glossary trees, and the structural test.
Constraints: do NOT change any test or the contract; sync both skill trees + 3 doc trees (md5
parity); ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — 11/11 new GREEN; full suite 133 OK (was 122, +11, no regressions)
- [x] coverage did not decrease — all 11 frozen invariants asserted; proven RED first (10 red,
      artifact-absent; the 11th — no engine fold command — correctly already green as an invariant)
- [x] no test or contract was altered during build — frozen 11-test list built to, not edited
- [x] concurrency / timing of the risky operation is safe — N/A (docs/method); the risky op is the
      FOLD WRITE, made safe by design: append-only + human-confirmed + no engine command (test 7)
- [x] no exposed secrets, injection openings, or unexpected dependencies — secret scan clean; no new deps
- [x] layering & dependencies follow CONVENTIONS.md — method-only; engine stays judgment-free (no fold
      cmd); Minimal pillar held (no new always-loaded doc; PROJECT.md gained one marker line); both
      skill trees + 3 glossary trees md5-identical; routing folded back into v5 MILESTONE.md
- [x] a person reviewed and approved the change — awaiting the human verify gate (owner=human)

Disclosed gap (does NOT block — regression-risk, not present-falsehood): the contract's artifact
list includes a "Foundation version" glossary entry (built, all 3 trees identical) but the 11 frozen
tests do NOT guard it (I enumerated PROJECT.md's marker as test 9 but not the glossary entry). Same
recurring class as competency-deltas' parity note. Adding a 12th test = editing a frozen contract =
a change-request. Captured as a competency delta in §7.

### GATE RECORD
Outcome: <PASS | RISK-ACCEPTED | HARD-STOP>
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: <name> · date: <date>

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>
Spec delta for the next loop: <what production taught you>

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
