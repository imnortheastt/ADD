# Phase 3 — Contract (freeze the shape)

Goal: fix the external shape — interfaces, data, names, error cases — and FREEZE
it. This is the seam that makes the AI-led build safe: below it code is
disposable; above it nothing breaks because the shape does not move. Fill
**§3 CONTRACT** in TASK.md.

## Produce (in TASK.md §3)

- Interfaces (endpoints/functions/messages) with inputs/outputs.
- Request/response shapes + persistent schema (note transactional needs).
- Names drawn from `GLOSSARY.md` (same concept = same name everywhere).
- A response for **every** Reject error code from §1.

Then mark `Status: FROZEN @ v1`. Generate a mock + contract tests so dependent
work can start before the real code exists.

**The freeze is the one approval.** This seam is where the single human approval lands, over the
whole bundle (§1–§4). Before asking for it, present the bundle **least-sure first**: the 1–2 points
most likely wrong (`⚠ [spec|scenario|contract|test] … — because …; if wrong: …`) — aim the human's
eye before they freeze. See `run.md`.

## AI prompt

> Role: an interface architect; frozen contracts are immutable. Read §1, §2,
> GLOSSARY. Produce §3: interfaces, shapes, schema named from the glossary; a
> response for every Reject code; a mock returning the contracted shapes and
> contract tests pinning them. Mark FROZEN. No business logic. Never change a
> frozen contract — a change reopens Specify.

## Exit gate

- [ ] Versioned and marked `FROZEN`.
- [ ] Contract tests pass against the mock.
- [ ] Every name matches the glossary.
- [ ] Every spec rejection has a contracted response.

## Next

`python3 .add/tooling/add.py advance` → read `phases/4-tests.md`.
Book: `docs/05-step-3-contract.md`.
