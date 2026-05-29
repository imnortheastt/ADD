# TASK: Classify a request: new-major | sub-milestone | task (AI proposes, human confirms)

slug: versioning-policy · created: 2026-05-29 · stage: mvp
phase: scenarios   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Purpose: give the AI a deterministic-enough RUBRIC to classify any incoming request into
exactly ONE of four buckets — and to record WHY — so intake (scope-loop, the next task) sizes
and versions scope correctly. The AI proposes; the human confirms. This is judgment guidance
(method-side), NOT engine logic — by the v4-1 rule "the engine is truth; the harness is the
intelligence", classification cannot live in `add.py` as a decision procedure.

Must:
  - A FOUR-bucket rubric, each with a crisp decision test and the `add.py` command it implies:
      • new-major  (vN)    — a new product theme/pillar not covered by any active milestone's
                             goal  -> `add.py new-milestone vN`
      • sub-milestone(vN-M)— a slice of an EXISTING major theme, too big for one task
                             -> `add.py new-milestone vN-M`
      • task               — fits within the ACTIVE milestone's stated scope
                             -> `add.py new-task <slug>`
      • change-request     — modifies ALREADY-FROZEN scope (a frozen contract or a shipped
                             milestone's promise) -> route back to SPECIFY/CONTRACT of the
                             affected task; do NOT size it as new scope.
  - Buckets are mutually exclusive; the rubric states the tie-break ORDER: (1) does it touch
    frozen scope? -> change-request. else (2) size test: new theme -> major · slice -> sub ·
    fits -> task. Exactly one bucket per request.
  - The AI emits a PROPOSAL = { bucket, rationale, the exact `add.py` command implied }; the
    human confirms or overrides BEFORE anything is created.
  - The rationale is RECORDED in the artifact created/affected (the new MILESTONE.md goal/body,
    the new TASK.md, or — for change-request — a note in the affected TASK.md). State surface,
    not a machine field (form decision: method-only, human-confirmed).
  - The rubric lives in `add-method/skill/add/intake.md` (NEW; a new INTAKE altitude — phases
    0–7 are per-task, intake is request->milestone), loaded only at intake (progressive
    disclosure), with a pointer from `SKILL.md`. No `add.py` change; reads no docs/ chapter to
    decide (the v2 Minimal pillar holds). Synced to the 3 doc/skill trees like every artifact.
Reject (named situations the rubric must NOT mishandle):
  - an ambiguous / underspecified request -> the AI STOPS and asks, never guesses a bucket
    -> "ask_human"  (the skill's "ask, don't guess" rule, at milestone altitude).
  - a request that changes frozen scope -> MUST be classified change-request and routed to
    SPECIFY/CONTRACT; never spawn a parallel milestone that forks the truth -> "frozen_scope".
  - a request spanning multiple buckets -> split it; propose the SMALLEST set of correctly-sized
    items, each with its own rationale; never force a multi-theme request into one milestone
    -> "split_required".
After:
  - given any request, the AI can produce a confirmed { bucket + rationale + implied command };
    scope-loop (next task) consumes THIS rubric to draft the actual versioned MILESTONE.md.
    Nothing in the engine changed; the human made every sizing decision.
Assumptions (confirm before building):
  - [x] Form = method-only rubric (no engine change; rationale recorded in the created/affected
        doc, not state.json). Confirmed by human 2026-05-29 (AskUserQuestion).
  - [x] Taxonomy = 4 buckets incl. change-request (-> back to SPECIFY/CONTRACT). Confirmed by
        human 2026-05-29 (AskUserQuestion).
  - [x] Home = `skill/add/intake.md` (loaded at intake) + pointer from SKILL.md. Confirmed by
        human 2026-05-30 — forced by the Minimal pillar (a runtime rubric must be on the loaded
        State surface, not in docs/); a NEW intake altitude that scope-loop will extend.
  - [x] Verification of a JUDGMENT artifact (the honest tension — ADD's red/green is code-centric;
        this deliverable is a rubric). Confirmed red/green surface (human 2026-05-30): a table of
        WORKED EXAMPLES (request -> expected bucket + rationale shape); a thin machine test guards
        STRUCTURE (intake.md exists, documents all 4 buckets + the tie-break order, every example
        maps to a valid bucket and is well-formed) and goes RED before the rubric exists; the human
        reviews the JUDGMENT (do the example classifications hold up) at verify.

<!-- EXIT: every rule stated, every rejection has a named code, zero open assumptions. -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

Worked examples use THIS project's real history (dogfood: the cases are checkable against
what actually happened) — they double as the red/green example table the structural test reads.

```gherkin
Scenario: a brand-new theme -> new-major
  Given a request "give ADD a hosted web dashboard" not covered by any active milestone's goal
  When the AI applies the rubric
  Then the proposed bucket is "new-major" with the implied command `add.py new-milestone v5`
  And the rationale names WHY it is a new theme (not a slice of an existing one)

Scenario: a slice of an existing theme -> sub-milestone
  Given a request "add the build corridor + tests-red-before-build" under the live v4 theme
  When the AI applies the rubric
  Then the proposed bucket is "sub-milestone" with the implied command `add.py new-milestone v4-2`
  And the rationale names the parent theme it slices

Scenario: work that fits the active milestone -> task
  Given a request "expose owner/stop as --json" while v4-1 (the intake interface) is active
  When the AI applies the rubric
  Then the proposed bucket is "task" with the implied command `add.py new-task <slug>`
  And the rationale shows it fits the active milestone's stated scope

Scenario: a change to already-frozen scope -> change-request
  Given a request "guide --json phase/gate should be str|null" against the FROZEN
        machine-state-json contract
  When the AI applies the rubric
  Then the proposed bucket is "change-request" routed to SPECIFY/CONTRACT of that task
  And no new milestone or task is created to fork the truth

Scenario: the tie-break order puts frozen-scope first
  Given a request that both looks like new work AND touches frozen scope
  When the AI applies the rubric
  Then it is classified "change-request" (the frozen-scope test runs before the size test)

Scenario: every classification emits the full proposal shape
  When the AI classifies any request
  Then it emits { bucket, rationale, the exact implied `add.py` command }
  And the human confirms or overrides before anything is created

Scenario: the rationale is recorded in the artifact
  Given a confirmed classification
  When the milestone/task is created (or a change-request note is added)
  Then the rationale is written into that MILESTONE.md / TASK.md (State surface, not state.json)

Scenario: an ambiguous request stops and asks            # Reject (ask_human)
  Given a request too underspecified to size
  When the AI applies the rubric
  Then it returns "ask_human" and asks the human instead of guessing a bucket
  And no milestone, task, or file is created

Scenario: a multi-theme request must be split            # Reject (split_required)
  Given a request that spans more than one bucket
  When the AI applies the rubric
  Then it returns "split_required" and proposes the SMALLEST set of correctly-sized items
  And nothing is forced into a single milestone

Scenario: applying the rubric stays minimal             # Minimal pillar + no engine change
  When the rubric is applied
  Then it reads no docs/ chapter and requires no change to add.py
  And the rubric lives in skill/add/intake.md, identical across the shipped + dogfood trees

Scenario: the structural test is red before the rubric exists   # red-first
  Given skill/add/intake.md does not yet document the 4 buckets + tie-break + examples
  When the structural test runs
  Then it FAILS — proving the test guards the artifact, not a tautology
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
<METHOD> <path>   body: { <fields> }
  200 -> { <success fields> }
  4xx -> { error: "<code>" | "<code>" }
Schema: <tables/fields touched, and access pattern>
```

Status: DRAFT   <!-- becomes: FROZEN @ v1 once approved. Changing a frozen contract = change request back to SPECIFY. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY. -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: <e.g. 90%>
Plan (one test per scenario, asserting behavior not internals):
  - test_<scenario>: arrange <Given> / act <When> / assert <Then> + assert <unchanged>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [ ] all tests pass
- [ ] coverage did not decrease
- [ ] no test or contract was altered during build
- [ ] concurrency / timing of the risky operation is safe
- [ ] no exposed secrets, injection openings, or unexpected dependencies
- [ ] layering & dependencies follow CONVENTIONS.md
- [ ] a person reviewed and approved the change

### GATE RECORD
Outcome: <PASS | RISK-ACCEPTED | HARD-STOP>
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: <name> · date: <date>

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>
Spec delta for the next loop: <what production taught you>
