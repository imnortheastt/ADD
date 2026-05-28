# Phase 1 — Specify (the rules)

Goal: state what the feature MUST do and what it must REJECT, with zero ambiguity
for the AI to resolve by guessing. Fill **§1 SPECIFY** in TASK.md.

If you cannot write the spec, you do not yet understand the feature — that is
information, not an obstacle. Stop and ask the user.

## Produce (in TASK.md §1)

- **Must** — each required behavior.
- **Reject** — each refused input/situation, paired with a **named error code**
  (`amount <= 0 -> "amount_invalid"`, never "handle bad input").
- **After** — the state that is true once it succeeds.
- **Assumptions** — everything you took for granted; ask the user to confirm/deny each.

## AI prompt

> Role: a domain analyst who asks rather than assumes. Read CONVENTIONS, GLOSSARY,
> and the user's raw input. Produce §1: every Must, every Reject with a named error
> code, the After state, and EVERY assumption you had to make — then ask me to
> confirm each. Never resolve an ambiguity by guessing.

## Exit gate

- [ ] Every required behavior stated.
- [ ] Every rejection has a named error code.
- [ ] Success state-change described.
- [ ] Zero unconfirmed assumptions.

## Next

`python3 .add/tooling/add.py advance` → read `phases/2-scenarios.md`.
Book: `docs/03-step-1-specify.md`. (UI feature? also sketch flows + every screen
state: loading/empty/error/success.)
