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

## Declaring where tests live

§4's `Tests live in:` line is machine-read: when a task has no local `tests/`,
`add.py report` counts test functions at the declared path(s) instead. The FIRST
line matching `Tests live in:` is read; paths are its backticked tokens.
Resolution: `./…` → this task's dir · a token containing `/` → the project root
(the parent of `.add/`) · a bare name → a sibling of the previous token's
directory (else the task dir). A directory token counts the `*.py` files directly
inside it (non-recursive); a `.py` file token counts itself; anything else is
ignored. Resolved files are deduped, and reports mark declared counts with `†`.
Paths are confined: anything resolving (symlinks followed)
outside the project root counts 0 — `..` traversal, absolute paths, and
symlink escapes are never read.

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
