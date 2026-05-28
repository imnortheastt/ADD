# 03 · Step 1 — Specify

[← 02 The flow](./02-the-flow.md) · [Contents](./README.md) · Next: [04 Step 2 Scenarios →](./04-step-2-scenarios.md)

> **Purpose:** state, in plain language, what the feature must do and what it must reject, with no ambiguity left for the AI to resolve by guessing.
> **Produces:** `SPEC.md` for the feature.
> **Person's job:** decide and confirm the rules. **AI's job:** draft, and surface every assumption.

---

## Why this step is first

The specification is the description the AI will build from. Every other artifact descends from it. Anything vague here does not stay vague — it becomes a concrete wrong guess in the code, discovered late. The cheapest moment to remove an ambiguity is now, in a sentence, before anything depends on it.

There is also a diagnostic value: **if you cannot write the spec, you do not yet understand the feature well enough to build it.** The inability to specify is information, not an obstacle to push past.

## What a good specification contains

Four parts, kept short:

1. **Must** — the behaviors the feature is required to perform.
2. **Reject** — the inputs or situations it must refuse, each paired with a named error.
3. **After** — the state that is true once it succeeds (what changed).
4. **Assumptions** — the things you are taking for granted, listed so they can be confirmed or denied.

Naming the errors matters. "Reject bad amounts" is an instruction to guess; `amount <= 0 -> "amount_invalid"` is a rule that produces a testable scenario and a defined contract response.

## Template

```
# SPEC.md
Feature: <name>
Must:
  - <required behavior>
Reject:
  - <bad input / situation> -> "<error_code>"
After:
  - <what is true once it succeeds>
Assumptions (confirm before building):
  - <assumption>
```

## ▶ Example

```
Feature: Transfer money between my own accounts
Must:
  - move an amount from one of my accounts to another of mine
  - amount > 0
  - source and destination are different accounts
  - source has enough balance
After:
  - source balance -= amount, destination balance += amount
Reject:
  - amount <= 0           -> "amount_invalid"
  - source == destination -> "same_account"
  - balance < amount      -> "insufficient_funds"
  - account not mine      -> "forbidden"
Assumptions (confirm):
  - same currency only (no FX) in v1
  - no daily limit in v1
```

Notice what the assumptions do: they make explicit two decisions (no currency conversion, no daily limit) that a sentence-long prompt would have left to chance. A stakeholder can now confirm or correct them in seconds.

## The AI's role here

Use the AI to draft the spec from whatever raw material you have — a ticket, an interview, a contract document — and, crucially, to **list every assumption it had to make.** Its instinct is to fill gaps silently; the prompt forces those gaps into the open instead. See `playbook/1_specify.md` in [Appendix B](./appendix-b-prompts.md).

The defining instruction: *if a requirement is unclear, ask — do not resolve it by guessing.*

## Common mistakes

- **Stating only the happy path.** The "Reject" list is where most real complexity lives; an empty one usually means it has not been thought through.
- **Free-text errors.** Errors must be named codes, not sentences, so they can become scenarios and contract responses.
- **Hidden assumptions.** If an assumption is not written down, it is not confirmed — it is a future bug with a delay timer.

## Exit check

A spec is done when:

- [ ] Every required behavior is stated explicitly.
- [ ] Every rejection has a named error code.
- [ ] The success state-change is described.
- [ ] Zero unconfirmed assumptions remain.

## If the check fails

If you cannot state a rule clearly, the feature is not ready to build. Stop, take the question to whoever owns the requirement, and resolve it. Do not let the AI proceed on an unresolved point — that is the exact failure the whole method exists to prevent.

---

## When the feature has a user interface

For anything with a UI, extend this step with a quick design: the **user flows** (the happy path and the main alternatives) and **every screen state** — loading, empty, error, and success. Correct logic behind a confusing or incomplete interface is still a poor product, and undesigned states are exactly where an AI will improvise something ugly. In the early **Prototype** stage, this design work is the main event and the code is throwaway (see [10 Stages](./10-setup-and-stages.md)).
