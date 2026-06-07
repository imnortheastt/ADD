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

- **No `.add/state.json` yet** (a fresh install drops tooling + docs but does *not* init — so `status` says
  `no .add/ project found`) → enter **autonomous setup**: YOU run init yourself —
  `add.py init --name "<inferred>" --stage <picked> --await-lock` (don't tell the human to) — then read
  `phases/0-setup.md` and draft the foundation + first scope + first contract through to the human lock-down.
- **A task is active** → open `.add/tasks/<active>/TASK.md`, look at its `phase:`
  marker, and read the matching `phases/<n>-<phase>.md`. Work *only* that phase.
- **No active task** → first SIZE the request (see Intake below), then create the
  right scope: `python3 .add/tooling/add.py new-task <slug> --title "..."`.

## Intake — size a request before creating scope

When the user brings a raw request, classify it BEFORE making a milestone or task:
read `intake.md` and place it in exactly one bucket — `new-major` · `sub-milestone`
· `task` · `change-request` — then propose `{ bucket, rationale, command }` and let
the human confirm. This is the intake altitude (request → versioned scope); see
`intake.md` for the rubric, the tie-break order, and worked examples. A question or
unsharp intent? **Interview before you size** — explore and suggest first (`intake.md`).

Once a request is classified `new-major`/`sub-milestone`, drafting the actual
`MILESTONE.md` (goal · scope · exit criteria · breadth-first tasks) is the second
half of intake: read `scope.md` for how to fill it well, the per-outcome behavior,
and the confirm-before-create rule. You propose the draft; the human confirms.

## The flow and which file to load

Load the phase guide **only for the phase you are in** (progressive disclosure):

| Phase | Guide | Produces (TASK.md section) | Who leads |
|-------|-------|----------------------------|-----------|
| setup | `phases/0-setup.md` | `.add/` + survivors + first §1–§3 + `SETUP-REVIEW.md` | AI drafts → **human locks** (the lock-down) |
| specify | `phases/1-specify.md` | §1 rules + ranked least-sure flag | AI drafts (co-specify)† |
| scenarios | `phases/2-scenarios.md` | §2 Given/When/Then | AI drafts† |
| contract | `phases/3-contract.md` | §3 frozen shape | AI drafts → **human approves once** (the seam)† |
| tests | `phases/4-tests.md` | §4 + red suite in `tests/` | AI drafts† |
| build | `phases/5-build.md` | code in `src/`, tests green | **AI** |
| verify | `phases/6-verify.md` | §6 checks + gate record | **AI auto-gates on evidence**; human on residue/security‡ |
| observe | `phases/7-observe.md` | §7 spec delta | human + AI |

† **One-approval front (v7).** §1–§4 are one bundle; the human gives **one approval at the
contract freeze** (the seam), presented least-sure-first. See `run.md`.
‡ **Verify auto-gate (v6–v7).** Under `autonomy: auto` (the default) a run may auto-PASS on
complete evidence — recorded as *auto-resolved*, an explicit PASS, not a skip. **Security always
escalates** (HARD-STOP); so do concurrency / architecture residue and `conservative` autonomy.
See `run.md`.

Whenever you present a seam to the human in chat (intake · front approval · gate ·
milestone close), follow `report-template.md` — SUMMARY → DECISION → ⚠ FLAGS →
EVIDENCE → NEXT, engine-sourced facts, show-before-ask, never pre-stamp a seam —
and the question is a summary, never the artifact.

In **observe**, also emit **competency deltas** — learnings tagged by which of the five
(`DDD · SDD · UDD · TDD · ADD`) they improve — so the foundation self-improves across loops.
You write them as `open`; the human folds them into `PROJECT.md`. Read `deltas.md` for the
grammar and the status lifecycle. At milestone close (or on demand), run the fold ritual that
gathers confirmed deltas into a versioned foundation — read `fold.md`.

## Beyond the front — load on demand

Once **§3 CONTRACT is FROZEN**, the build→verify half is a dynamic, auto-gated run
(`autonomy: auto` default, lowered to `conservative` for a human gate) — read `run.md`. To
pipeline several ready tasks behind their own frozen contracts, read `streams.md`.

## Non-negotiable rules (from the method)

<constraints>
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
</constraints>

## Advancing

After a phase's exit gate is met, advance the state (this also syncs the marker
inside TASK.md):

```bash
python3 .add/tooling/add.py advance            # next phase of the active task
python3 .add/tooling/add.py gate PASS          # at verify: records PASS, marks done
python3 .add/tooling/add.py use <slug>         # switch the active task (e.g. across parallel streams)
```

## Depth by stage

The steps never change; their depth does. Read the stage from `add.py status`:

- **prototype** — run light; code is throwaway; design/experience is the point.
- **poc** — run contract/tests/build deeply on the single riskiest slice only.
- **mvp** — full flow, narrow scope, light observation.
- **production** — every step at full rigor + the observe loop.

## The method rationale

The full method (the *why* behind every rule) is the AIDD book in `.add/docs/`.
When a phase decision is genuinely unclear, read the linked chapter — each phase
guide points to its chapter. Do not duplicate the book here; load it on demand.
