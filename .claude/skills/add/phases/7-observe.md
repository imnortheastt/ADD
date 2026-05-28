# Phase 7 — Observe (feed the next loop)

Goal: release deliberately, watch reality, and turn what you learn into the next
spec. Release is not the finish line — it is where the most reliable information
about the feature finally appears. Fill **§7** in TASK.md.

## Do

1. **Release behind a blast-radius limit** — feature flag and/or gradual rollout.
2. **Reuse scenarios as monitors** — the §2 scenarios that defined "correct" now
   define what you alert on: overall error rate, each rejection's rate (a spike in
   one is a signal), latency of the risky operation under load.
3. **Draft the next spec delta** — every defect, surprise, or new need becomes a
   concrete change that re-enters the flow at Specify (a new task).

## AI prompt

> Role: a reliability analyst feeding the next cycle. Read telemetry, objectives,
> incidents. Report error-budget burn; cluster errors and surface the top
> real-world failures; draft a SPEC delta with evidence links. Never auto-roll-back
> — recommend; a human owns the production decision.

## Exit gate

- [ ] Released behind a flag/rollout.
- [ ] Scenario-based monitors live.
- [ ] A reviewed spec delta captured (becomes the next `new-task`).

## Next

Loop. The artifacts you built are living documents the next cycle refines.
Book: `docs/09-the-loop.md`.
