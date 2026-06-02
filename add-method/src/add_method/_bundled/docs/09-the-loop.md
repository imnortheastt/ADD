# 09 · The loop — observe and learn

[← 08 Step 6 Verify](./08-step-6-verify.md) · [Contents](./README.md) · Next: [10 Setup and stages →](./10-setup-and-stages.md)

> **Purpose:** release the verified change, watch how it behaves in reality, and turn what you learn into the next specification.
> **Produces:** a running feature, observations, and the next `SPEC.md` delta.

---

## The flow is a loop, not a line

Older mental models end at "ship." That framing is the source of a common pathology: teams treat release as a finish line, and so they hide defects to protect the line rather than manage them in the open. In AIDD, release is not the end of the flow — it is the point where the most reliable information about the feature finally becomes available: how it behaves with real users, real data, and real load.

That information is the input to the next cycle. What you learn in production becomes the next specification, and the flow returns to [Step 1](./03-step-1-specify.md). The cycle is continuous.

## Release deliberately

Release behind a mechanism that limits the blast radius of a mistake — a feature flag, a gradual rollout, or both. The verification step established that the feature is correct against everything you anticipated; a controlled release is your protection against what you did not anticipate. If something is wrong, you want to affect a few users and roll back, not affect everyone and scramble.

## Reuse the scenarios as monitors

The scenarios from [Step 2](./04-step-2-scenarios.md) have a second life here. They described the behavior you expected; in production they become the behavior you monitor. The same definition of "correct" that drove the tests now drives the alerts.

**What to watch (▶ example):**

- the overall transfer error rate;
- the rate of each individual rejection (`amount_invalid`, `same_account`, `insufficient_funds`, `forbidden`) — a sudden spike in one is a signal, not noise;
- latency, especially of the atomic balance update under load.

## Turn observation into the next spec

Every defect, surprise, or new need is written up as a change to the specification — a delta that re-enters the flow at [Step 1](./03-step-1-specify.md). An error rate that is too high, a rejection that fires more than expected, a user behavior nobody designed for: each becomes a concrete, specified next step rather than a vague intention.

This is also where the AI returns to a useful role: summarizing telemetry, clustering errors into themes, and drafting the proposed spec delta for a person to review. But the production decisions — what to roll back, what to prioritize — remain human.

## Re-entrancy: the loop is the whole point

Two principles converge here. *The flow is re-entrant* — any step can send you back to an earlier one — and *the flow is a loop* — production feeds the next specification. Together they mean the artifacts you built are never "finished"; they are living documents that the next cycle refines.

A team operating this way does not experience requirements changing as a failure of planning. It experiences it as the system working: reality is teaching the specification, and the specification is teaching the next build.

> **Do:** release small, watch the scenarios, and feed every learning back into the spec.
> **Don't:** treat shipping as the end. The most valuable information about a feature arrives *after* it ships.
