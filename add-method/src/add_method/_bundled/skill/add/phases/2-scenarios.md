# Phase 2 — Scenarios (pass/fail cases)

Goal: rewrite each rule as a concrete Given/When/Then that is readable by people
and checkable by machines. This is the highest-leverage artifact — the tests are
generated from it. Fill **§2 SCENARIOS** in TASK.md.

## Produce (in TASK.md §2)

```gherkin
Scenario: <short name>
  Given <starting situation>
  When <action>
  Then <observable result>
  And <what must remain unchanged>   # REQUIRED for every rejection
```

The `And ... unchanged` clause catches corrupting partial failures (e.g. a balance
deducted before a check fails). Never omit it on a rejection.

## AI prompt

> Role: a specification tester. Read §1 and GLOSSARY. Write one scenario per Must
> and per Reject rule. For every rejection add an And-clause asserting what must NOT
> change. Results must be specific and observable — never "then it works".

## Exit gate

- [ ] One scenario per Must rule.
- [ ] One scenario per Reject rule.
- [ ] Each result is a specific, observable fact.
- [ ] Every rejection asserts what stays unchanged.

## Next

`python3 .add/tooling/add.py advance` → read `phases/3-contract.md`.
Book: `docs/04-step-2-scenarios.md`.
