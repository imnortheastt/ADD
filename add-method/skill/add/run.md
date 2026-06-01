# The dynamic run — executing a locked scope

Once a task's CONTRACT is frozen (phase 3), the scope is *locked*: the external shape will not move.
That lock is ADD's autonomy seam — below it code is disposable; above it nothing breaks. This rubric
covers what runs on the far side of the seam: the **build->verify half, executed as a dynamic,
self-improving run** instead of a manual, sequential build. The human-led FRONT (Specify · Scenarios
· Contract) does not change — the run is what v6 adds.

> **Self-improving = within-run convergence + emit v5 deltas** — same definition as v5: tracked,
> evidence-backed, never autonomous training. The run converges in-turn AND feeds the human-gated
> fold loop (`deltas.md` · `fold.md`). The engine stays judgment-free: this is a rubric, not `add.py`.

## When the run begins — the scope-lock trigger

The trigger is the **frozen contract**, nothing else. A run may start only when:

- §3 CONTRACT is marked `FROZEN @ vN` (the shape is fixed), AND
- §4 TESTS exist and are RED for the right reason (the target the run drives to green).

No frozen contract -> no run: you are still on the human-led front, and starting early is the
forward-skip the flow forbids. The lock is what makes autonomous execution *safe* — the AI cannot
drift the interface, because the interface is frozen above it.

## The touch-boundary — what the run may and may not touch

A locked run has a hard boundary. It MAY:

- write and rewrite **code** (`src/`) — code is disposable below the seam;
- drive the **tests** to green WITHOUT weakening them (a weakened test is a method violation);
- gather **evidence** for the verify gate (test output, blind-spot checks).

It MUST NOT:

- change the **frozen contract** or the **locked scope** — a discovered gap is backward-correction:
  the run STOPS and hands back to a human to reopen Specify (principle 4). The run never re-locks
  scope on its own.
- weaken, delete, or skip a **test** to make the build pass (that inverts the method).
- touch the **human-led front artifacts** (§1–§3) except to halt and escalate.

Crossing the boundary is not a fast run; it is an unverified one. When the run hits something only the
front can resolve, it stops — and that stop is the loop working, not failing.

## The dynamic run — fan-out and in-run convergence

Once it starts, the run does not crawl the build in one linear pass. It **fans out** the independent
work — several build attempts, several test-fix loops, several checks at once — and then **converges**
on a trustworthy result with three loops:

- **loop-until-dry** — keep hunting failures and gaps until N consecutive passes find nothing new.
  Stopping at the first green is how defects survive; the run stops only when the well runs dry.
- **adversarial verify** — for every "done" claim, an independent skeptic tries to REFUTE it. The
  claim survives only if it withstands refutation, not because one pass looked plausible.
- **completeness-critic** — a final pass that asks "what did we NOT cover — a scenario, a blind-spot,
  an unstated assumption?" Whatever it finds re-enters the run.

The run ends only when the loops go dry AND the auto-gate's evidence is satisfied. This is the run
**self-improving within the turn** — the same convergence the foundation loop runs across milestones,
compressed into one task.

## The evidence auto-gate

The verify gate may be resolved by **evidence** rather than by a person — when the evidence is
sufficient and the result is recorded (principle 7, reframed: an automated, recorded pass is an
explicit pass, not a skip).

- **Auto-PASS requires ALL of:** every test green; coverage not decreased; no test weakened and no
  contract edited; the convergence loops dry; the completeness-critic found nothing open.
- **Always escalates to a human (never auto-passed):** any **security** finding (HARD-STOP, always);
  a **concurrency**/timing risk the tests cannot exercise; an **architecture**/layering violation; and
  any failing test. These are the residue principle 2 names — automation cannot judge them.
- **Records exactly one outcome** (no silent skip): `PASS` (evidence + the named run as accountable
  owner) · `RISK-ACCEPTED` (non-security, signed) · `HARD-STOP`. The record states it was
  auto-resolved, names the run, and lists the residue checks performed.

The auto-gate NEVER writes a human signature it did not get. An auto-PASS is logged as *auto-resolved*,
honestly — the line between a pass and a skip is the recorded outcome, not a forged name.

## Emitting deltas — feeding the foundation back

The completeness-critic does not discard what it finds. Every gap, surprise, or convention that helped
or hurt becomes an **`open` competency delta** in the task's OBSERVE block, in the `deltas.md` grammar,
tagged by competency:

- a finding the run FIXED but that taught the foundation something (a missing scenario -> `TDD`);
- a finding the run could NOT fix — a residue escalation -> a delta AND the escalation to a human.

These `open` deltas feed v5's human-gated fold (`fold.md`) at milestone close: the run emits `open`;
the human folds. That is the loop closing — **v6 run -> v5 foundation** — so a dynamic run sharpens the
five competencies instead of letting its findings evaporate at end-of-run.

## The autonomy dial

How much a run may auto-gate is a **per-scope setting**, not a global switch (principle 5: trust is
earned per scope). A task declares its level in its `TASK.md` header:

```
autonomy: conservative | auto
```

- **conservative (the default)** — the run does all the work and converges, but STOPS at the verify
  gate for a human. Auto-PASS is disabled.
- **auto** — the run may auto-PASS when the evidence + residue checks above are satisfied. Security
  still always escalates.

The default is conservative; raising to `auto` is a deliberate, recorded choice for a low-risk,
well-tested scope, and can be lowered at any time. The dial is a **rubric convention** read by the
human and the run — it is **not an `add.py` flag** (the engine stays judgment-free); the level lives in
the `TASK.md` header where the run already reads.
