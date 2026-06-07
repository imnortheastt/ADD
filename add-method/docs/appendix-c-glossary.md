# Appendix C · Glossary

[← Appendix B Prompts](./appendix-b-prompts.md) · [Contents](./README.md) · Next: [Appendix D Worked example →](./appendix-d-worked-example.md)

---

## Terms

**AIDD (AI-Driven Development)** — a method of building software in which an AI agent writes most of the code and people direct and verify the work.

**Artifact** — a durable work product: the spec, the scenarios, the contract, the tests. The artifacts survive; the code is disposable.

**Competency delta** — a single learning a loop produces, tagged by which of the five competencies (`DDD · SDD · UDD · TDD · ADD`) it improves, written in a task's OBSERVE phase as `- [<COMPETENCY> · <status>] <learning> (evidence: …)`. Emitted `open` by the AI; the human folds it into a versioned `PROJECT.md` (`folded`) or declines it (`rejected`). The mechanism by which the foundation self-improves instead of drifting. See the `add` skill's `deltas.md`.

**Contract** — the fixed external shape of a feature: interfaces, data structures, names, and error cases. Frozen before the build, it is the surface the AI builds against.

**Co-specification** — how a spec is made in ADD: the AI and the human **brainstorm the shape together** (diverge), the AI **drafts** it, and the human **validates with the AI's advice** (validate). The AI's decisive advice is the *least-sure flag*. It replaces dictation-by-one-side — the human owns the decision, the AI owns surfacing what it does not yet know. See [03 Specify](./03-step-1-specify.md).

**Disposable code** — the view that code is one regenerable implementation of the artifacts, not a durable asset to be preserved.

**Evidence bundle** — the proof attached to a change (passing tests, clean security scan, no coverage loss) that justifies trusting it and may unlock more AI autonomy.

**Foundation version** — a monotonic integer marker in `PROJECT.md` that advances by one each time confirmed competency deltas are folded into the foundation. It makes the survivor layer's evolution auditable: a rising version with fewer new deltas per milestone is the signal that a competency is converging rather than drifting. Bumped only by the fold ritual (see the `add` skill's `fold.md`).

**Gate** — a checkpoint with an explicit pass/fail exit. Its outcome is `PASS`, `RISK-ACCEPTED`, or `HARD-STOP`.

**`HARD-STOP`** — a gate outcome meaning work cannot proceed; triggered by any failing test or security finding.

**Intake** — the step *before* a task: sizing a raw request into versioned scope by classifying it into one **request bucket**. The AI proposes `{bucket, rationale, command}`; the human confirms. Lives in the `add` skill's `intake.md` (the intake altitude, above the per-task flow).

**Least-sure flag** — the AI's ranked declaration of the **1–2 things most likely to be wrong** in what it is asking a human to approve, each carrying *why* it is uncertain and *what it costs if wrong* (`⚠ [spec|scenario|contract|test] … — because …; if wrong: …`). It reshapes the old flat assumptions list into a ranked one, so a single approval aims the reviewer's attention at the real risk instead of a wall of equal-looking ticks. Bundle-wide at the one-approval freeze seam; the §1 assumptions are its first feeder. If nothing is materially uncertain it still names the single biggest risk — never a blank "none". It makes a genuine review cheap and a lazy one visibly negligent, but cannot *force* the read. The "AI advises" half of **co-specification**.

**Living document** — an artifact expected to change as the loop learns; never frozen forever (the one exception being a versioned contract, which changes only via a change request).

**Onboarding** (formerly "on-ramp") — the path a new user walks from install to their first milestone: install → `/add` → describe the goal → the agent runs intake (sizing the request into a milestone the human confirms) → the one-approval front → the self-driving run. The AI-first entry to the method; the human talks to the agent rather than hand-typing `add.py`.

**Owner (of a phase)** — who drives a phase, exposed by `add.py … --json` as `human`, `seam`, or `ai`. It tells an autonomous harness where it may run (`ai`) and where it must checkpoint to a person (`human`/`seam`), following the who-does-what table (Verify is always `human`).

**Profile** — the intensity at which the method is run: Express, Standard, or Regulated.

**Request bucket** — one of the four intake classifications — `new-major`, `sub-milestone`, `task`, or `change-request` — chosen by the tie-break order (the frozen-scope test runs before the size test). A request too vague to size is rejected `ask_human`; one that touches frozen scope, `frozen_scope`; one spanning buckets, `split_required`.

**`RISK-ACCEPTED`** — a gate outcome meaning work proceeds with a signed waiver (owner, ticket, expiry); allowed for non-security gaps only.

**Scenario** — a single rule expressed as Given/When/Then; readable by people and checkable by machines; the bridge between spec and tests.

**Scope drafting (scope-loop)** — the second half of **intake**: once a request is classified `new-major`/`sub-milestone`, turning it into a confirmed, well-formed `MILESTONE.md` (goal · scope · exit criteria · breadth-first tasks) through discussion. Every exit criterion maps to a declared task slug; the AI proposes the draft, the human confirms before anything is created. Lives in the `add` skill's `scope.md`.

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
