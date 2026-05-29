# TASK: Machine-readable engine state (--json + owner/stop)

slug: machine-state-json · created: 2026-05-29 · stage: mvp
phase: specify   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Purpose: expose engine state as parseable JSON so ANY harness (Claude Code, Codex, CI) can
read *where the project is* and *where it must stop* — the enabling layer for autonomous ADD.

Must:
  - `add.py guide --json` prints ONE valid JSON object to stdout and exits 0:
    `{ "task", "phase", "owner", "stop", "next_step", "chapter", "gate" }`
    where `owner` ∈ {"human","seam","ai"} and `stop` is a bool (true = the harness must
    checkpoint to the human before proceeding).
  - `add.py status --json` prints ONE valid JSON object: project, stage, active_task, and
    arrays of milestones `{slug,status,done,total}` and tasks `{slug,phase,gate,milestone}`.
  - The `owner`/`stop` of a phase is derived from the phase name via a SINGLE mapping table
    in add.py (the harness must never hard-code it) — see the assumption below for the map.
  - Output is machine-clean: with `--json`, stdout carries ONLY the JSON (no log lines,
    no human prose); without `--json`, the existing human text is byte-for-byte unchanged.
  - JSON is built purely from State (state.json + TASK.md marker); it reads NO docs/ chapter
    (the v2 Minimal pillar must still hold — `test_min_pillar` stays green).
Reject (named codes, fail-closed but parseable):
  - no active task on `guide --json` -> still emit valid JSON with `"task": null` and
    `"stop": true` (a harness must stop and ask, not crash) — NOT an error exit.
  - a malformed/missing state.json -> stderr `no_state` + exit 1 + EMPTY stdout
    (never a half-written JSON object a harness might parse).
  - an unknown `owner` would-be value (phase not in the map) -> stderr `unmapped_phase`
    + exit 1 + empty stdout (fail closed; a new phase must be mapped deliberately).
After:
  - a harness can run: read `--json` -> if `owner=="ai"` and `stop==false` act, else
    checkpoint to the human -> `advance`/`gate`. Nothing about human-text UX changed.
Assumptions (confirm before building):
  - [ ] FORK A — command coverage: ship `--json` on `guide` + `status` ONLY this task;
        defer `check`/`ready` to when a harness actually needs them. (Recommended: yes.)
  - [ ] FORK B — the `owner` map, esp. **Verify**: the book conflicts — the mermaid colors
        Build+Verify as "machine", but the who-does-what table says Verify is "human only".
        For the STOP signal that governs autonomy, the prose must win:
          specify→human · scenarios→human · contract→seam · tests→seam ·
          build→ai · verify→human · observe→human · done→human
        `stop = (owner != "ai")`. (Recommended: adopt this map; it stops the harness at
        every human/seam phase and only auto-runs Build.) Confirm or correct the mapping.
  - [x] JSON is single-line compact (pipe-friendly), not pretty-printed.
  - [x] `--json` is a flag on the existing subcommands, not a new `export` subcommand
        (keeps the surface minimal; reuses each command's state load).

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
