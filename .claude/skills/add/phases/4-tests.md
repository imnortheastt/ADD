# Phase 4 — Tests (red safety net)

Goal: turn scenarios + contract into automated tests and confirm they FAIL before
any code exists. This operationalizes red/green TDD: red now, green only after
Build. Fill **§4 TESTS** and write the suite into `.add/tasks/<slug>/tests/`.

## The must-fail principle

Run the suite now, with no implementation — it must be **red for the right
reason** (missing implementation, not a broken harness). A test that passes
before code exists is testing nothing and will wave bad code through later.

## Produce

- One executable test per scenario (§2), asserting **behavior, not internals**.
- Contract-conformance tests (shapes + error responses from §3).
- Side-effect assertions on rejection paths (`assert balance unchanged`).
- A recorded coverage target in §4.

## AI prompt

> Role: a test author who writes tests before code. Read §2 and §3. Turn each
> scenario into an executable test; add contract-conformance and edge-case tests;
> run the suite and confirm it fails for the right reason. Record a coverage
> target. Do NOT implement the feature. Never assert on internals.

## Exit gate

- [ ] One test per scenario.
- [ ] Suite runs and is **red for the right reason**.
- [ ] Tests assert observable behavior.
- [ ] Coverage target recorded.

## Next

`python3 .add/tooling/add.py advance` → read `phases/5-build.md`.
Book: `docs/06-step-4-tests.md`.
