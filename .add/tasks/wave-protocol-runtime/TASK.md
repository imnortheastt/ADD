# TASK: streams.md: merge-time fork-base check + worker commits SUMMARY.md

slug: wave-protocol-runtime · created: 2026-06-08 · stage: mvp · risk: high · autonomy: conservative
phase: specify   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- risk: high — amends the method's own orchestration rubric (streams.md), same surface as wave-ledger;
     autonomy lowered to conservative: the verify gate stops for the human. Source: v19 wave deltas #7 + #8. -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower
     the autonomy level with `autonomy: conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: amend streams.md "Wave ledger" so its fork-base discipline is SATISFIABLE on a runner that creates the worktree AT spawn, and so a worker durably persists its own report — closing v19 wave deltas #7 (merge-time fork-base) + #8 (worker commits SUMMARY.md). This is a method-surface (prose) change-request, not engine code.
Framings weighed: amend the existing ledger protocol in place — add a merge-time alternative to the pre-spawn `unverified_fork_base` cell + a "worker commits SUMMARY.md/deltas.md" line to the worker `<return>` (chosen: the CONVENTIONS:90 amendment already states the rule; streams.md must mirror it or the check stays prose-only — the exact lesson #7 teaches) · invent a new add.py refusal that runs the check (rejected: the check is orchestrator-discipline across an opaque harness seam, not engine state — words-exist≠method-works cuts both ways, but engine enforcement of a worktree-pool fact the engine can't observe is vacuous) · leave it CONVENTIONS-only (rejected: the human already declined this — a shipped protocol doc that contradicts its own folded convention is the recursion)
Must:
<must>
  - streams.md states that on a spawn-time-worktree runner the pre-spawn fork-base evidence cell is impossible, and the `unverified_fork_base` refusal SHIFTS to: worker step-0 sync-to-base + re-echo, verified by the orchestrator at MERGE-time before merge-back — the check shifts, it never skips
  - streams.md worker `<return>` contract requires the worker to COMMIT its SUMMARY.md + deltas.md in the worktree (not merely write them) — uncommitted worktree files survive only by harness courtesy
  - both add.py copies of streams.md (canonical add-method + dogfood .add, + bundle if present) stay md5-identical after the edit (dogfood-parity convention)
  - the existing pre-spawn rule is PRESERVED as the default for fresh-HEAD-worktree runners — the merge-time path is an additive alternative, not a replacement (positivization-boundary: don't delete the working rule)
</must>
Reject:
<reject>
  - the edit removes/weakens the fresh-base pre-spawn rule rather than adding the merge-time alternative -> "fork_base_rule_weakened"
  - streams.md mirror copies diverge in md5 after the edit -> "mirror_drift"
</reject>
After:
<after>
  - a future wave on a spawn-time-worktree runner has a contracted, in-protocol path for the fork-base check — the CONVENTIONS:90 runtime-exception and the shipped streams.md text agree, and the worker contract names the SUMMARY.md commit
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ a prose amendment is enough — the check is orchestrator-discipline and cannot be engine-enforced (the harness creates the worktree, the engine never sees the pool) — lowest confidence because "words-exist≠method-works" warns that prose checks don't run; mitigation/cost: the merge-time leg IS engine-adjacent (the orchestrator verifies the echo before a cherry-pick the engine could guard later) — name the enforcement-deferral explicitly rather than claim prose = enforcement; if wrong: a follow-up add.py guard on merge-back
  - [ ] streams.md is the only surface carrying the pre-spawn rule (vs. the book docs/ chapter on streams) — confirm by grep before freeze; if a book chapter also states it, the cross-cutting-reword rule applies (enumerate every surface)
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: <short name>
  Given <starting situation>
  When <action>
  Then <expected result>
  And <what must remain unchanged>   # required for every rejection
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
<METHOD> <path>   body: { <fields> }
  200 -> { <success fields> }
  4xx -> { error: "<code>" | "<code>" }
Schema: <tables/fields touched, and access pattern>
```

Status: DRAFT
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: <e.g. 90%>
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_<scenario>: arrange <Given> / act <When> / assert <Then> + assert <unchanged>
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

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

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
