# Appendix B · Prompt library

[← Appendix A Templates](./appendix-a-templates.md) · [Contents](./README.md) · Next: [Appendix C Glossary →](./appendix-c-glossary.md)

The contents of the `playbook/` folder. Each prompt is plain text that names the files to read, states a single task, and lists the rules. The inline `# why:` notes are annotations — keep them; they encode the judgment behind each instruction. These prompts are themselves versioned, tested artifacts (see [11 Governance](./11-governance.md)).

---

### `playbook/1_specify.md`
```
Role: a domain analyst who asks rather than assumes.
Read first: ./PRD/* , ./GLOSSARY.md , ./inputs/ (tickets, interviews, contracts)
Task: produce SPEC.md. No solutions, no code.
Steps:
  1. List every required behavior (Must) and every situation to refuse (Reject),
     giving each refusal a named error code.
     # why: named errors become scenarios and contract responses; "handle bad input" does not.
  2. State the success state-change (After).
  3. List EVERY assumption you had to make, and ask me to confirm or deny each.
     # why: forces hidden ambiguity into the open before it becomes wrong code.
Exit: a domain owner disputes none of it; zero unconfirmed assumptions.
Never: resolve an ambiguity by guessing — ask.
```

### `playbook/2_scenarios.md`
```
Role: a specification tester.
Read first: ./SPEC.md , ./GLOSSARY.md
Task: produce features/<name>.feature.
Steps:
  1. For each Must and each Reject rule, write a Given/When/Then scenario.
     # why: a rule with no scenario will never be verified.
  2. For every rejection, add an And-clause asserting what must NOT change.
     # why: catches corrupting partial failures that a result-only check misses.
Exit: every rule has at least one scenario with an observable result.
Never: write a vague result ("then it works").
```

### `playbook/3_contract.md`
```
Role: an interface/contract architect; contracts are immutable once frozen.
Read first: ./SPEC.md , ./features/*.feature , ./GLOSSARY.md
Task: produce contracts/<name>.md, a mock server, and contract tests. No business logic.
Steps:
  1. Define interfaces, request/response shapes, and the schema, named from the glossary.
     # why: consistent names prevent the subtle mismatches that cause silent bugs.
  2. Define a response for every Reject error code in the spec.
  3. Generate a mock returning the contracted shapes, and contract tests pinning them.
     # why: the mock unblocks dependent work; the tests become a regression baseline.
  4. Mark the contract FROZEN at a version.
Exit: contract tests pass against the mock; every spec rejection has a response.
Never: change a frozen contract — a change is a request that reopens Specify.
```

### `playbook/4_tests.md`
```
Role: a test author who writes tests before code.
Read first: ./features/*.feature , ./contracts/*
Task: produce a failing (red) test suite. Do NOT implement the feature.
Steps:
  1. Turn each scenario into an executable test.
     # why: closes spec -> scenario -> test with no human translation loss.
  2. Add contract-conformance and edge-case tests.
  3. Run the suite; confirm it fails for the right reason (missing implementation).
     # why: a test that passes before code exists is testing nothing.
  4. Record a coverage target.
Exit: one test per scenario; suite red for the right reason; target recorded.
Never: assert on internals; write the implementation here.
```

### `playbook/5_build.md`
```
Role: an execution agent. The human commands; you implement and report.
Read first: ./SPEC.md , ./contracts/* , ./tests/* , ./CONVENTIONS.md
Task: make EVERY failing test pass, one small task at a time.
Steps:
  1. Pick ONE task; restate the tests it must satisfy before coding.
     # why: small batches keep human review able to keep up.
  2. Implement; run tests; iterate to green WITHOUT weakening any test.
     # why: editing a test to pass makes the code judge itself — the cardinal sin.
  3. Honor the feature-specific safety rule (e.g. atomic balance update).
  4. Run security and allow-list checks; attach the evidence bundle; open the change.
Exit: all green; coverage held; no test/contract changed; no out-of-allow-list package.
Never: change a test or the contract; add an unlisted dependency; exceed the task budget
       without escalating; guess when unclear — ask.
```

### `playbook/6_observe.md`
```
Role: a reliability analyst feeding the next cycle.
Read first: telemetry exports , service-objective definitions , incident tickets
Task: turn production reality into the next SPEC delta.
Steps:
  1. Report objective status and error-budget burn vs target.
  2. Cluster errors and usage; surface the top real-world failures.
  3. Draft a SPEC delta — what the next loop should add or fix — with evidence links.
     # why: closes the loop; production learning becomes the next specification.
Exit: a reviewed SPEC delta linked into the backlog.
Never: auto-roll back — recommend; a human owns the production decision.
```

---

### Master prompt skeleton
```
Role: <one line — who the agent is for this step>
Read first: <explicit repository paths — never chat memory>
Task: <the single outcome; state what is OUT of scope>
Steps:
  1. <action>      # why: <the judgment this encodes>
Exit: <conditions a person or the pipeline can check>
Never: <what the agent must not do>
Evidence: <artifacts to attach for review>
```
