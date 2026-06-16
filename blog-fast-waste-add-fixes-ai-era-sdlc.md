# Fast Waste: Fixing the SDLC for the Age of Agent Coding

*AI made code cheap. That quietly broke the assumption your entire software process was built on. Here's how AI‑Driven Development (ADD) — five competencies and eight steps — puts the bottleneck back where it belongs.*

---

For the whole history of software, writing code was the slow, expensive, central act. Every methodology we have — waterfall, agile, scrum, kanban — is, at bottom, an arrangement for managing that one expensive act: how to plan it, divide it, review it, and ship it. The SDLC is a set of rituals optimized around the idea that **typing the code is the hard part.**

Then a coding agent started producing a working module in the time it takes to describe one. The marginal cost of *writing* a piece of code — and of *re‑writing* it — fell close to zero.

When the cost of one activity collapses, value moves to whatever is still scarce. And most of our SDLC ceremony is now optimizing the cheap thing. That's the problem this post is about, and ADD is one concrete answer to it.

## The new failure mode: fast waste

Here's the trap that catches every team the first week they hand real work to an agent.

> **An AI agent is fast in whatever direction it is pointed.**

If the direction is vague, the agent does not slow down and ask. It produces a confident, plausible, complete‑*looking* result built on an assumption you never made, missing an edge case you never stated. Because it looks finished, the error survives a quick read — and surfaces later, in production, when it's expensive to fix.

Speed in the wrong direction isn't progress. It's **faster waste.** And it shows up as four specific failures of the AI‑era SDLC:

1. **Fast waste** — the agent sprints confidently past an ambiguity instead of stopping at it.
2. **Context rot** — the model degrades over a long session, and every *new* session starts cold; the design lives in someone's head, so the agent re‑guesses it each time.
3. **Trust‑by‑inspection breaks down** — AI code is frequently *plausible and wrong*. You can't establish correctness by reading the diff and finding it reasonable.
4. **Verification is the real ceiling** — when an agent produces more than your team can review, the excess isn't speed. It's unreviewed risk, accumulating.

Notice that none of these is "the AI can't write code." It writes code fine. The failures are all about **direction** and **verification** — the two things AI can't reliably do alone, and exactly the two things our code‑centric process never made explicit, because when humans typed every line, direction and verification came bundled into the typing.

ADD's entire thesis is to unbundle them and protect them:

> **Build the right thing (direction), prove it's right (verification), and let the AI do the building in between.**

## Five competencies: the foundation and the engine

ADD organizes the work into five disciplines — and the order of the layers is the whole point.

![ADD's five competencies — DDD · SDD · UDD are human‑led and feed context to TDD ⇄ ADD, where the AI executes under your direction](./add-competencies.png)

**The foundation (context the agent stands on):**

- **DDD — Domain.** The shared, precise language and the boundaries it lives in: the core concepts, the contexts they belong to, and the invariants that must always hold. *One name per concept* — the same names the spec, the contract, the tests, and the code all use.
- **SDD — Spec.** The *living document* of what's being built right now, and what's settled versus still open. Not a frozen plan signed once — a layer that changes as the loop learns.
- **UDD — UI/UX.** Users use the *interface*, not the spec. The user flows, the states every screen must handle (loading · empty · error · success), and a design source of truth. The AI can generate a prototype; a person owns the empathy.

**The engine (where the work happens):**

- **TDD ⇄ ADD.** The tight red/green loop: write the failing test, let the AI generate code until it's green, repeat.

![The engine needs ground — the TDD ⇄ ADD engine runs on a DDD · SDD · UDD foundation; context feeds up, corrections feed back down](./add-foundation.png)

The crucial relationship: **the first four feed context to the fifth, where the AI executes.** An engine needs something to stand on. Every loop quietly assumes context that no single task owns — *what the words mean, what we're building, how users experience it.* When that context lives only in a person's head, the agent fills the gap with plausible guesses. The foundation is what kills context rot: ADD writes all three concerns into **one living `PROJECT.md`**, kept to a single screen, that the engine reads first every session. State lives on disk, not in the chat — so you close your laptop, come back tomorrow, and the agent re‑orients instantly instead of re‑guessing.

## Eight steps: direction before speed, evidence before trust

The engine itself is one repeatable flow. Six steps build a feature, a seventh feeds production reality back in, and a step‑0 preamble grounds the whole thing in the code as it actually is.

![The ADD flow — Ground → Specify → Scenarios → Contract → Tests → Build → Verify → Observe, with backward‑correction arrows and a Tests ⇄ Build red/green engine](./add-flow.png)

| # | Step | Produces | Resolves which AI‑era failure |
|---|------|----------|-------------------------------|
| 0 | **Ground** | a map of the real files, symbols, and conventions the task touches | aims the spec at reality, not assumption |
| 1 | **Specify** | the rules the feature must obey, lowest‑confidence assumption flagged first | kills *fast waste* — the ambiguity is surfaced, not sprinted past |
| 2 | **Scenarios** | the rules as pass/fail cases (Given/When/Then) | makes "correct" concrete before any code |
| 3 | **Contract** | the frozen data + interface shape | the one human decision point — the agent never freezes the interface it then builds against |
| 4 | **Tests** | a failing‑first (red) suite | proves the contract is executable *before* a line of code exists |
| 5 | **Build** | the code, until every test is green | the AI runs fast and safe because everything it needs is already fixed |
| 6 | **Verify** | a recorded outcome (`PASS` / `RISK‑ACCEPTED` / `HARD‑STOP`) | replaces trust‑by‑inspection with trust‑by‑evidence |
| 7 | **Observe** | a spec delta + lessons learned | turns production signal into the next Specify |

Two rules govern movement through the flow, and they never conflict. **Forward‑skipping is forbidden:** you never start a step before its input artifact exists — skip forward and the AI builds against a guess. **Backward correction is always allowed:** any step may send you back to repair an earlier artifact. A Build that exposes a missing rule sends you back to Specify — and *that's the method working,* not failing. The specification is a living document, not a contract signed once.

The shape is deliberate. The human‑led steps (1–2) establish direction. A **frozen contract** forms a decision point in the middle. The AI‑led build (5) runs fast on the far side *because everything it needs is already fixed.* This is "direction before speed" rendered as a pipeline: you set the wheel before you start the engine.

## A concrete pass: transferring money between accounts

Abstractions are easy to nod along to, so here's one feature all the way through — *transfer money between a user's own accounts.*

**Specify** writes the rules, and it ranks the assumptions by confidence, lowest first:

```
⚠ same currency only (no FX) in v1 — lowest confidence: the ticket never said.
  If wrong: the amount/rounding model changes and this contract is wrong.
```

The product owner reads *that* line first — the one most likely to be wrong and most expensive if it is — and confirms it. The single riskiest guess is killed in one sentence, before any code exists.

**Contract** freezes the shape the build and the tests both depend on:

```
POST /transfers   body: { fromAccountId, toAccountId, amount }
  200 -> { transferId, fromBalance, toBalance }
  400 -> { error: "amount_invalid" | "same_account" | "insufficient_funds" }
  403 -> { error: "forbidden" }
Schema: accounts.balance (read + write, must be transactional)
Status: FROZEN @ v1
```

**Tests** are written next and run *first, with no implementation* — all five fail. That's the honest baseline. Then the **Build** prompt hands the AI the spec, the contract, and the tests with one non‑negotiable constraint:

```
Implement POST /transfers so EVERY test passes.
  - Do NOT change any test.
  - Do NOT change the contract.
  - Make the balance update atomic; re-check the balance inside the transaction.
  - Stop and ask if any requirement is unclear — do not guess.
```

This is the rule that inverts the usual agent failure mode: **never weaken a test or edit a frozen contract to make the build pass.** If the agent thinks the spec is wrong, that's a change request back to Specify — not a quiet edit to the goalposts.

And then **Verify**, where trust is actually established — not by reading the diff and finding it plausible (that's the exact trap), but by evidence plus a check of the things tests *can't* catch:

> **Concurrency (the check that matters here):** two simultaneous transfers from account A must not both pass the balance check and overdraw it. The reviewer confirms the balance re‑check happens *inside* the transaction and the row is locked — so a race can't double‑spend. ✓

A green test suite would never have caught that; tests run serially and miss races. This is why ADD treats verification as two parts — *confirm the evidence, then check the residue:* concurrency, security, architecture. Every verify ends in exactly one recorded outcome, owned by a person or a named run. There are no silent skips.

A week later, telemetry shows an unexpectedly high `forbidden` rate. The signal clusters: users are trying to transfer *into* a shared account they can see but don't own. That observation becomes a spec delta — "support transfers into accounts I'm authorized on" — and the flow returns to Step 1. **Observe** closed the loop, and production reality became the next specification.

## From the field: 23 milestones in six days

The money‑transfer feature is a teaching example. Here's the same method on a real production system.

`ai-proxy` is a LiteLLM‑class multi‑tenant AI gateway — six upstream providers, an OpenAI‑compatible `/v1` surface, metering and billing, budgets, governance, a load‑balancing router, caching, SSO, and an enterprise dashboard. It was built end to end through ADD: **23 versioned milestones, ~120 tasks, six days, graduated to production.** Its foundation carries an append‑only log of 140+ decisions — the method's own audit trail of what each loop caught and why. Three findings stand out, because each is the thesis above turning into evidence.

**Green test suites shipped clean while hiding real defects.** A live end‑to‑end run caught a defect that *326 passing tests* missed — a PII marker silently never recorded. A later milestone's live pass caught two production‑*dead* code paths that *399 passing tests* waved through. That's "trust‑by‑inspection breaks down" measured, not asserted — and it's exactly why ADD makes live verification and an adversarial **earned‑green refute‑read** load‑bearing *on top of* the suite. The refute‑read alone caught a coverage regression a `--no-coverage` run had hidden, and a fail‑open identity bypass where a followed redirect could chain to a trusted response.

**Security stopped hard, every time.** An unverified session‑JWT decode in the dashboard escalated to a human as a `HARD-STOP`, became its own remediation task, then generalized into a project‑wide sweep — 13 secret‑bearing error paths hardened so a crash reporter couldn't walk the exception chain back to an API key. No security finding was ever auto‑passed. *(I spot‑checked that sweep against the live code; the audit trail matched.)*

**The foundation compounded.** Every loop folded its lessons — tagged by discipline — back into the foundation, so later milestones reused proven patterns by name instead of re‑deriving them, and follow‑up debt was tracked as `OPEN` and closed on the record (two whole milestones existed to pay it down). The method improved itself across loops.

And the agent's *behavior* changed with it: it surfaced its least‑confident assumption and asked before building, froze the contract and then refused to touch it, **attacked its own green** with a refute‑read and an independent security subagent, and treated a passing suite as necessary but never sufficient.

*(The full field study, with every claim traced to its milestone, lives alongside this post: [`case-study-ai-proxy-add-in-production.md`](./case-study-ai-proxy-add-in-production.md).)*

## Why this actually fixes the AI‑era SDLC

Walk the four failures back through the method:

- **Fast waste** dies at Specify and the frozen Contract. The agent's ambiguity is surfaced and confirmed *before* the speed turns on — direction before acceleration, every time.
- **Context rot** dies at the foundation. The durable context lives in `PROJECT.md` and on disk, not in a chat window that decays. A new session re‑orients instead of re‑guessing.
- **Trust‑by‑inspection** dies at the red‑tests gate and Verify. A feature is trusted because its tests pass and its non‑functional risks were checked — not because the code reads plausibly. The artifacts (spec, scenarios, contract, tests) are the durable asset; the code is one disposable implementation that satisfies them.
- **The verification ceiling** is respected *and raised.* You can't move faster than you can verify — but a passing suite, a contract check, and an adversarial verifier are all verification, and they scale in a way human reading never will. So Verify can **auto‑gate on complete evidence**, recording an explicit pass owned by a named run — while **security always stops for a human.** Autonomy is earned by more verification, not by a lower bar.

There's a useful way to test whether a team has actually internalized this: ask what they'd be upset to lose. If the answer is "the code," they're still working the old way. If the answer is "the contracts and the tests," they're working in ADD.

## Where it sits

ADD didn't appear from nowhere — it's spec‑driven development and tests‑first discipline pointed at agent coding. But it deliberately closes the loop past its siblings: spec‑kit stops at `implement`; GSD ends at verify. ADD adds three things neither carries as a first‑class gate — a **failing‑tests‑first gate** (no build until the tests are red for the right reason), an **observe → consolidate** step (confirmed lessons fold back into a versioned foundation, so the method improves itself across loops), and a **dynamic goal‑loop** (the engine holds a milestone open until its exit criteria are met, instead of declaring done when a checklist empties).

The agentic loop already runs — by 2026, more than 80% of the code merged at Anthropic was Claude‑authored. What that loop doesn't supply on its own is the discipline to *trust* the output. That's the whole job now, and it's a harder job than typing ever was: turning a fuzzy need into a buildable definition, and proving the result correct through evidence.

The code got cheap. Direction and verification didn't. Build the right thing, prove it's right, and let the AI do the building in between.

---

*ADD ships as an AI‑agent skill: `npx @pilotspace/add init` (Node) or `pip install pilotspace-add` (Python), then talk to the agent and it drives the method. The full book — principles, every step, governance, and the worked example above — lives alongside this post in the AIDD‑Book.*
