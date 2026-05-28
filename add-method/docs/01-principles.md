# 01 · Core principles

[← 00 The shift](./00-introduction.md) · [Contents](./README.md) · Next: [02 The flow →](./02-the-flow.md)

Everything in this book follows from a small set of principles. If a practice ever seems arbitrary, trace it back to one of these.

---

## 1. Direction before speed

An AI agent accelerates in whatever direction it is given. Therefore the direction must be fixed before the acceleration begins. In practice this means the early, human-led steps of the flow are not optional preamble — they are the steering, and the build step is the engine. You do not start the engine until the wheel is set.

**Consequence:** the specification, scenarios, and contract come *before* any code, every time.

## 2. Trust through evidence, not inspection

AI output is often wrong in ways that read as correct. You cannot establish correctness by reading the code and judging it plausible. You establish it by defining, in advance, what "correct" means — as automated tests — and confirming the code satisfies them, then checking by hand only the narrow set of things tests cannot catch.

**Consequence:** tests are written *before* the implementation, and a feature is trusted because its tests pass, not because someone reviewed it and liked it.

## 3. The artifacts survive; the code is disposable

The durable assets of a project are the decisions and agreements: the specification, the scenarios, the contract, the tests. The code is merely one implementation that satisfies them and can be regenerated at will. Protect the artifacts; treat the code as replaceable.

**Consequence:** effort goes into keeping contracts and specs stable and clear, not into preserving particular code. Metrics that count code volume or reuse measure the wrong thing.

## 4. The loop is re-entrant, not a waterfall

The flow has an order, but it is not a one-way march. Any step may reveal a gap in an earlier one — and when it does, you return to that earlier step, fix the artifact, and come forward again. The specification is a living document, not a frozen contract signed once.

**Consequence:** discovering a missing rule during the build is the method working, not failing. The only true one-way door is the frozen interface contract, and even that reopens through a deliberate change request.

## 5. Trust is earned per scope, not granted globally

How much you let the AI do is not a single switch. It rises with the evidence available and with your capacity to verify, and it can differ from one part of the system to another. A well-tested, low-risk area may allow more autonomy than a new, high-risk one.

**Consequence:** autonomy is a setting you choose deliberately and can lower at any time (see [11 Governance](./11-governance.md)).

## 6. You cannot move faster than you can verify

When an agent produces more than the team can review, the excess is not speed — it is unreviewed risk accumulating. Verification capacity is the real ceiling on throughput.

**Consequence:** if AI output outpaces review, the correct response is to reduce the AI's autonomy or batch size, never to rush or skip the review.

## 7. No silent skips

Every checkpoint resolves explicitly. A step is either passed, or passed with a recorded and signed acceptance of a known risk, or stopped. Nothing is quietly waved through.

**Consequence:** every gate produces a recorded outcome with an accountable owner (see [11 Governance](./11-governance.md)).

## 8. Tool-agnostic by construction

The instructions you give the AI are plain text that reference files in the repository, not commands tied to one product. Enforcement of the gates lives in your build pipeline, not in the agent. This keeps the method portable: the agent is replaceable; the method is not.

**Consequence:** the same project works whether the team uses one AI coding tool or another, and switching tools changes nothing structural.

---

> **The principles, compressed.** Steer before you accelerate. Trust evidence, not impressions. Keep the decisions, throw away the code. Loop freely, but never skip silently. Grant the AI only as much autonomy as you can verify.
