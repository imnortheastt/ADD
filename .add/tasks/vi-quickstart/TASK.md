# TASK: Vietnamese Quickstart for MRQ

slug: vi-quickstart · created: 2026-05-28 · stage: mvp
phase: specify   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Must:
  - <required behavior>
Reject:
  - <bad input / situation> -> "<error_code>"
After:
  - <state that is true once it succeeds>
Assumptions (confirm before building):
  - [ ] <assumption — confirm or deny, never carry an open one forward>

<!-- EXIT: every rule stated, every rejection has a named code, zero open assumptions. -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: <short name>
  Given <starting situation>
  When <action>
  Then <expected result>
  And <what must remain unchanged>   # required for every rejection
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
