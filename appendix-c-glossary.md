# Appendix C · Glossary

[← Appendix B Prompts](./appendix-b-prompts.md) · [Contents](./README.md) · Next: [Appendix D Worked example →](./appendix-d-worked-example.md)

---

## Terms

**AIDD (AI-Driven Development)** — a method of building software in which an AI agent writes most of the code and people direct and verify the work.

**Artifact** — a durable work product: the spec, the scenarios, the contract, the tests. The artifacts survive; the code is disposable.

**Contract** — the fixed external shape of a feature: interfaces, data structures, names, and error cases. Frozen before the build, it is the surface the AI builds against.

**Disposable code** — the view that code is one regenerable implementation of the artifacts, not a durable asset to be preserved.

**Evidence bundle** — the proof attached to a change (passing tests, clean security scan, no coverage loss) that justifies trusting it and may unlock more AI autonomy.

**Gate** — a checkpoint with an explicit pass/fail exit. Its outcome is `PASS`, `RISK-ACCEPTED`, or `HARD-STOP`.

**`HARD-STOP`** — a gate outcome meaning work cannot proceed; triggered by any failing test or security finding.

**Intake** — the step *before* a task: sizing a raw request into versioned scope by classifying it into one **request bucket**. The AI proposes `{bucket, rationale, command}`; the human confirms. Lives in the `add` skill's `intake.md` (the intake altitude, above the per-task flow).

**Living document** — an artifact expected to change as the loop learns; never frozen forever (the one exception being a versioned contract, which changes only via a change request).

**Owner (of a phase)** — who drives a phase, exposed by `add.py … --json` as `human`, `seam`, or `ai`. It tells an autonomous harness where it may run (`ai`) and where it must checkpoint to a person (`human`/`seam`), following the who-does-what table (Verify is always `human`).

**Profile** — the intensity at which the method is run: Express, Standard, or Regulated.

**Request bucket** — one of the four intake classifications — `new-major`, `sub-milestone`, `task`, or `change-request` — chosen by the tie-break order (the frozen-scope test runs before the size test). A request too vague to size is rejected `ask_human`; one that touches frozen scope, `frozen_scope`; one spanning buckets, `split_required`.

**`RISK-ACCEPTED`** — a gate outcome meaning work proceeds with a signed waiver (owner, ticket, expiry); allowed for non-security gaps only.

**Scenario** — a single rule expressed as Given/When/Then; readable by people and checkable by machines; the bridge between spec and tests.

**Spec (`SPEC.md`)** — the plain-language statement of what a feature must do, must reject, and assumes.

**Spine / continuous concern** — a concern that runs through every step rather than being one step: security, testing, observability, cost.

**Stage** — one pass through the flow at a chosen depth: Prototype, Proof of Concept, MVP, or Production-Ready.

**State surface** — everything an agent loads every session: the `add` skill (router `SKILL.md` + the active phase) and the lean operational docs — `PROJECT.md`, the active `MILESTONE.md` and `TASK.md`, and `state.json`. Kept small to avoid context rot. Contrast **Story surface**.

**Stop signal** — the boolean an autonomous harness reads from `add.py … --json` (`stop = owner != "ai"`): true means pause for a person before proceeding. The irreducible stops are the contract freeze and the Verify gate. See **Owner (of a phase)**.

**Story surface** — the book (`docs/*`): the whole method, read once by a person to trust ADD, then referenced by a pointer and **never auto-loaded** into agent context. Contrast **State surface**.

**Survivor layer** — the set of durable artifacts (conventions, glossary, frozen contracts) that outlive any particular code.

**Trust ladder / autonomy ladder** — the graduated levels of AI autonomy, earned with evidence and verification capacity.

**Verification capacity / review throughput** — the rate at which a team can confirm AI output is correct; the real ceiling on safe speed.

---

## Optional mapping to formal phase names

This book uses plain step names. Teams connecting it to a larger formal standard may use these equivalents. The mapping is optional; the plain flow is complete on its own.

| Plain step (this book) | Formal phase name |
|------------------------|-------------------|
| Project setup | Foundation |
| Specify | Domain Discovery + Spec Definition |
| (design portion) | UX-Driven Design |
| Scenarios | Behavior specification (Given/When/Then) |
| Contract | Contract Freeze |
| Tests | Test-Driven Verification |
| Build | AI-Driven Development (the engine) |
| Verify | the review gate within the build |
| Observe (loop) | Operate and Learn |

The formal standard also names the *foundation* and *design* work as full phases in their own right; this book folds them into project setup and the Specify step (and the Prototype stage) to keep the flow to six memorable steps.
