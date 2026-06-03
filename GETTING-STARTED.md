# Getting started with ADD

ADD is **AI-first**: you install it once, then talk to the agent and it drives the
method. This is the 2-minute on-ramp. For the full hands-on walkthrough that takes one
real feature from nothing to a verified pass, follow
[`add-method/GETTING-STARTED.md`](./add-method/GETTING-STARTED.md).

## 1 · Install

From your project root, pick either ecosystem — both install the same skill, tooling,
and book:

```bash
# Node / npm
npx @pilotspace/add init --name "My App" --stage prototype
```

```bash
# Python / pip
pip install add-method
add-method init --name "My App" --stage prototype
```

> **Prerequisites:** Node ≥ 18 (npm path) or Python ≥ 3.10 (pip path). The tool itself
> is Python stdlib-only. Pick the `--stage` that matches your intent —
> `prototype` · `poc` · `mvp` · `production`; you can change it later.

This creates:

| Path | What |
|------|------|
| `.claude/skills/add/` | the `add` skill Claude Code loads |
| `.add/tooling/add.py` | scaffolder + state tracker (stdlib-only) |
| `.add/docs/` | the AIDD book — the trust layer |
| `.add/state.json` | where the project is (the resume point) |

It never overwrites existing state.

## 2 · Build your first feature

In Claude Code, run `/add` and say what you want:

> `/add` — *"I want to let users transfer money between their own accounts."*

The agent then:

1. **Orients** from `add.py status` (never re-reading your repo).
2. **Sizes** your request into a milestone — *you confirm the shape*.
3. Drafts the **one-approval front** — Spec + Scenarios + Contract + Tests as one
   bundle — *you give one approval at the frozen contract*.
4. Runs **build → verify** to green; a security finding always stops back to you.

So: **describe it → confirm the milestone → approve each contract → review the
result.** Everything in between is the agent.

## 3 · Resume anytime

```bash
python3 .add/tooling/add.py status
```

State lives on disk, not in a chat window — close your laptop, come back tomorrow, and
this tells you exactly where you left off.

## The non-negotiables

1. **Direction before speed** — no Build until spec, scenarios, contract, and *red*
   tests exist.
2. **Trust evidence, not inspection** — a feature is trusted because its tests pass and
   the blind spots (concurrency, security, architecture) were checked.
3. **Never weaken a test or edit a frozen contract** to make the build pass.
4. **No silent skips** — every Verify records `PASS`, `RISK-ACCEPTED`, or `HARD-STOP`.
5. **Ask, don't guess.**

## Next

- **The full walkthrough** — [`add-method/GETTING-STARTED.md`](./add-method/GETTING-STARTED.md)
- **The method, end to end** — [the book](./README.md#table-of-contents) (start at
  [`00-introduction.md`](./00-introduction.md))
- **What changed** — [`CHANGELOG.md`](./CHANGELOG.md)
