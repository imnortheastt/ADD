---
name: add
description: >-
  ADD (AI-Driven Development) — a minimal, state-tracked workflow for building
  software where the AI writes the code and the human owns direction and
  verification. Drives every feature through one lean TASK.md: Specify →
  Scenarios → Contract → Tests → Build → Verify → Observe, with red/green TDD
  built in. Use this skill whenever working in a repo that has a `.add/`
  directory, when the user says "add", "start a task", "next phase", "specify
  this feature", "ADD method", or "AI-driven development", or when scaffolding a
  new feature and you want spec/tests-first discipline instead of vague-prompt
  coding. Also use it to resume work across sessions (it reads `.add/state.json`
  so you never re-read the whole repo).
---

# ADD — the orchestration engine

You are the orchestrator. ADD keeps the AI fast *and* safe by fixing direction
(spec, scenarios, contract, failing tests) **before** the build, and trusting
the result through passing evidence rather than a plausible-looking diff.

**One file = one task.** Each feature lives in a single `.add/tasks/<slug>/TASK.md`
with seven sections. You fill them top to bottom; the Python tool tracks where
you are so context never rots across sessions.

## Always start here (orient — do not skip)

Run the tool to find the resume point instead of re-reading the repo:

```bash
python3 .add/tooling/add.py status
```

- **No `.add/` yet** → go to **phase 0 (setup)**: read `phases/0-setup.md`.
- **A task is active** → open `.add/tasks/<active>/TASK.md`, look at its `phase:`
  marker, and read the matching `phases/<n>-<phase>.md`. Work *only* that phase.
- **No active task** → ask the user which feature to build, then
  `python3 .add/tooling/add.py new-task <slug> --title "..."`.

## The flow and which file to load

Load the phase guide **only for the phase you are in** (progressive disclosure):

| Phase | Guide | Produces (TASK.md section) | Who leads |
|-------|-------|----------------------------|-----------|
| setup | `phases/0-setup.md` | `.add/` + survivor files | human |
| specify | `phases/1-specify.md` | §1 rules + named rejections | human |
| scenarios | `phases/2-scenarios.md` | §2 Given/When/Then | human |
| contract | `phases/3-contract.md` | §3 frozen shape | human + AI |
| tests | `phases/4-tests.md` | §4 + red suite in `tests/` | human sets, AI writes |
| build | `phases/5-build.md` | code in `src/`, tests green | **AI** |
| verify | `phases/6-verify.md` | §6 checks + gate record | **human** |
| observe | `phases/7-observe.md` | §7 spec delta | human + AI |

## Non-negotiable rules (from the method)

1. **Direction before speed.** Never start Build until §1–§4 exist and tests are red.
2. **Trust evidence, not inspection.** A feature is trusted because its tests pass
   and the blind-spots (concurrency, security, architecture) were checked — not
   because the code reads plausibly.
3. **Never weaken a test or edit a frozen contract to make the build pass.** That
   inverts the method. A real change is a *change request* back to Specify.
4. **No silent skips.** Every Verify ends in exactly one recorded outcome:
   `PASS`, `RISK-ACCEPTED` (signed, non-security only), or `HARD-STOP`. A security
   finding is always `HARD-STOP`.
5. **Ask, don't guess.** If a requirement is unclear, stop and ask the user.

## Advancing

After a phase's exit gate is met, advance the state (this also syncs the marker
inside TASK.md):

```bash
python3 .add/tooling/add.py advance            # next phase of the active task
python3 .add/tooling/add.py gate PASS          # at verify: records PASS, marks done
```

## Depth by stage

The steps never change; their depth does. Read the stage from `add.py status`:

- **prototype** — run light; code is throwaway; design/experience is the point.
- **poc** — run contract/tests/build deeply on the single riskiest slice only.
- **mvp** — full flow, narrow scope, light observation.
- **production** — every step at full rigor + the observe loop.

## The trust layer

The full method (the *why* behind every rule) is the AIDD book in `.add/docs/`.
When a phase decision is genuinely unclear, read the linked chapter — each phase
guide points to its chapter. Do not duplicate the book here; load it on demand.
