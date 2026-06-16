# ADD in Production: What the `ai-proxy` Build Reveals

*A field study of AI-Driven Development applied to a real, non-trivial system — what it bought, and how it changed the way the agent behaved.*

---

## The subject

`ai-proxy` is a LiteLLM-class **multi-tenant, metered AI gateway**: a FastAPI data plane behind an Envoy edge, Postgres + Redis, and a Next.js/shadcn dashboard. Over its life it grew to cover six upstream providers (OpenRouter, Anthropic, Google Gemini, AWS Bedrock, Azure OpenAI, OpenAI-compatible), an OpenAI-compatible `/v1` surface (chat, streaming, tools/function-calling, JSON-mode, embeddings, images, audio), usage metering and per-tenant markup billing, budgets and spend windows, teams and governance, a load-balancing router with cooldown/circuit-breaking, response + semantic caching, SSO/OIDC, and a full enterprise dashboard.

It was built entirely through ADD:

| Dimension | Measure |
|---|---|
| Milestones | **23** (`v1` → `v24`), each a versioned foundation bump |
| Tasks | **~120** across the milestones |
| Calendar span | **6 days** (2026-06-10 → 2026-06-16) |
| Stage | graduated to **production** |
| Evidence base | **140+** append-only Key Decisions (the `fold` log), `state.json`, a 53 KB `CONVENTIONS.md`, and **262 MB / 185 session transcripts** |

**A note on evidence.** The findings below are drawn from the project's own ADD audit trail — the append-only Key Decisions log in `PROJECT.md`, which records the *outcome* of each loop (what was caught, where, and why). I verified the log is not aspirational by spot-checking one claim against the live code: the v22 "project-wide `from None` secret-chain floor" decision states `rg "from exc" infrastructure/ → zero`. The code confirms it — `from None` appears across exactly the provider adapters and the shared `upstream_retry.py` seam the decision names, and `from exc` in the infra source is zero. The audit trail tracks reality.

---

## Part A — The benefits ADD delivered

### 1. Defects caught *before any code existed* (direction)

The single most distinctive payoff. The contract-freeze ritual repeatedly caught contradictions while the cost of fixing them was one edited sentence:

- **v1** — the freeze flag's cross-artifact consistency check "caught the argon2/SHA-256 conflict before code existed."
- **v2** — the freeze review found that "`status_class` aggregate could not express the required 402 rate; caught pre-freeze" — an exit criterion that was literally unmeasurable from the contracted labels.
- **v19** — the freeze gate cross-checked "a broad §3 RANGE against §1's explicit REJECT enumeration," catching `status 400-499` contradicting `429 already retry-handled` before the classifier was written.

This is "fix the direction before turning on the speed" producing measurable saves, milestone after milestone.

### 2. Defects that **green test suites could not see** (why inspection isn't enough)

The project independently rediscovered — and then codified as a standing gate — the exact failure ADD's "trust evidence, not inspection" principle warns about: *suites assert the behavior they were written to see.*

- **v2** — "mock-shaped fixtures passed while live billing recorded **0/0 vs upstream 24/73**." Verbatim live-captured fixtures became mandatory.
- **v4** — "live v4 run found a real defect **326 green tests missed**: `pii_masked` marker never recorded on the non-blocking mask path."
- **v5** — "the v5 live pass caught **two production defects** (exchanger + resolver wiring) **invisible to 399 green tests**"; separately, "two per-tenant-OIDC paths were **production-dead while every frozen test passed**."

The lesson folded into the foundation: **milestone-close live edge verification is load-bearing and never waived**, even for an all-green milestone. Tests are necessary; they are not sufficient — proven, not asserted.

### 3. The adversarial "earned-green" refute-read caught cheats *and* misdiagnoses

Under `autonomy: auto`, the verify gate spawns an independent subagent prompted to argue the green was *not* earned. It paid for itself:

- **v14** — running `--no-coverage` "HID a real **78.14% < 80%** regression"; the refute-read returned `EARNED-WITH-GAPS` and "surfaced **3 real coverage gaps** the green hid."
- **v17** — "an adversarial refute-read catches **MIS-DIAGNOSIS**, not just cheating" — it traced two leaks dismissed as "benign" back to forgotten in-file handlers and drove them to zero.
- **v18** — it caught a fail-**open** identity bypass (a followed 3xx chaining to a trusted 200) and forced `redirect:"manual"` + a `redirect→503` test.

### 4. Security stayed a hard gate — never auto-passed

Every security finding escalated to the human as a `HARD-STOP`, exactly as the method requires, and the escalations were real:

- **v17 → v18** — the operator escalated that "`/api/auth/me` decodes the session JWT **WITHOUT signature verification**." It became its own task and was discharged as a fail-closed relay to the authoritative verifier, holding no signing secret in the dashboard.
- **v21** — "any auth/secret task's verify gate MUST run an **INDEPENDENT adversarial security subagent**" — which "caught a real **api-key / client_secret leak** (`from exc`) + weak-test gaps the self-review missed," on tasks that looked like thin passthroughs.
- **v22** — that single finding generalized into a **project-wide sweep**: all 13 secret-bearing transport-error wraps now `raise ... from None`, with a greppable invariant and a `__cause__ is None` test per site. *(This is the claim I verified against the code above.)*

Plus defense-in-depth that tests alone would never motivate: byte-identical failure responses across all authz modes (to deny timing/content-length oracles, v1), and `raise ... from None` as a *testable* security property.

### 5. The frozen contract enabled fearless, additive extension

Because the contract was the one-way door, every new capability landed *additively* against a byte-identical regression net — and the same seam pattern compounded:

- The "freeze-first **SHARED-SEAM** pattern" is recorded as proven for a new provider (v9), then "repeats a THIRD time and this time **COMPOSES**" (v11, response-format composing with v10 tools).
- Frozen behavioral pins evolved by **supersession** (record at the new freeze, leave the frozen file untouched, keep the default behavior-preserving) — so "NEVER retry → a precise retryable set" shipped with "default `retries=0` keeps v5 byte-identical" (v6).

Six providers and dozens of endpoints were added without a single "rewrite the core" milestone.

### 6. The foundation compounded — the method improved itself

This is the part older SDLCs have no analogue for. Every loop emitted lessons tagged `DDD · SDD · UDD · TDD · ADD`, and `fold` consolidated them into a versioned foundation. Later milestones then *reused* them by name instead of re-deriving. And debt was never silently dropped — it was tracked as `OPEN` and closed on the record:

- `v7 OPEN: empty-key boot guard` → **resolved v12** (`empty-key-boot-guard`).
- `v21 OPEN: secret-chain sweep` and `OPEN: Azure AD authority not configurable` → **both resolved v22**.
- Whole milestones existed to *pay down* carried debt: **v12** ("pay down v7/v9/v11 follow-up debt"), **v17** ("clear carried debt v13/v14/v15").

The foundation got richer every loop; a new session re-oriented on it instead of re-guessing.

### 7. Production velocity *with* a safety floor

23 production-stage milestones in six days — while the never-weaken-a-test contract held the whole way. Lint conflicts with frozen tests were resolved with `per-file-ignores`, "**never test edits**" (v1); post-freeze refinements went into §6/§7, "**NEVER §3**," because the tamper tripwire md5s the whole frozen body — "even editing a §3 pseudocode COMMENT after the snapshot trips the tripwire" (v19). Speed did not come from lowering the bar.

---

## Part B — How the agent *behaved* under ADD

The method didn't just produce artifacts; it reshaped the LLM's operating behavior. Across the run, the agent reliably:

1. **Surfaced its least-confident assumption first and asked, instead of guessing.** The `⚠` lowest-confidence flag at spec time is what turned silent guesses into one-line human confirmations (e.g., single-currency, seed-then-restart resolver refresh) before any build.
2. **Froze the contract and then refused to touch it.** Post-freeze, the agent routed every refinement into §6/§7 rather than editing §3 — the tamper tripwire made "just tweak the contract to pass" structurally impossible.
3. **Wrote tests red-first and checked red was for the *right* reason.** "Red confirmed for the RIGHT reason before any build line" (v1); absence-of-behavior tests were explicitly marked `GREEN-BY-DESIGN` (v6) so a green-before-build didn't get misread.
4. **Attacked its own green.** It spawned an adversarial refute-read on verify, and an *independent* security subagent for any auth/secret task — actively trying to disprove its own success.
5. **Escalated security to the human every time.** No security finding was auto-passed; each became a `HARD-STOP` and often a dedicated remediation task.
6. **Recorded explicit outcomes and converted residue into future tasks.** Nothing was silently skipped; `OPEN` follow-ups were carried in the foundation and reopened as tasks (the goal-loop), not forgotten.
7. **Reused folded patterns instead of re-deriving them.** "The reusable recipe for evolving any frozen Protocol," "a repeatable 4-step template for the next provider" — the agent built on prior decisions by name.
8. **Refused to trust a green suite alone.** It treated live/edge verification as load-bearing and ran it at every milestone close, because it had folded the lesson that suites only see what they were written to see.

---

## What this says about the AI-era SDLC claims

The build is a working confirmation of the blog's thesis, not a restatement of it:

- **"Fast waste" is preventable.** Direction (spec + frozen contract) caught real contradictions *before code* — repeatedly, cheaply.
- **"Trust-by-inspection breaks down" — empirically.** Green suites of 326 and 399 tests hid real production defects; only evidence-plus-residue checks (live verify, refute-read, security subagent) caught them.
- **"Verification is the ceiling, and automation raises it."** The auto refute-read and the load-bearing live-verify *scaled* verification past what human reading of a 120k-line diff could ever cover — while security stayed at human speed, by design.
- **"Keep the artifacts, throw the code."** 140+ durable decisions and a versioned foundation were the asset; the code was extended and superseded additively without a rewrite.
- **The loop improves itself.** `OPEN → RESOLVED` chains and named pattern reuse are the `fold` current turned inward — the distinguishing step spec-kit and GSD don't carry.

---

## Honest caveats

- **One project, one team, one operator + agent.** This is a rich field study, not a controlled trial; there is no A/B against the same system built without ADD.
- **The evidence is the project's own audit trail.** I validated one claim against the code directly; the rest rests on the fold log's recorded outcomes. The log's specificity (named defects, test counts, file paths) is what makes it credible — and it matched the code where I checked.
- **"Six days" is calendar span.** Hours of effort and operator intensity aren't measured here.
- **Some wins are discipline a strong human team could also reach.** ADD's claim isn't that the discipline is unique — it's that the method makes that discipline the *default path* for a fast, eager agent, and records the evidence that it held.

> **The one-line finding.** Pointed at a real production system for six days, ADD turned a fast, plausible-but-fallible agent into one that surfaced its doubts before building, froze and respected its contracts, attacked its own green, stopped hard on security, and compounded every lesson into the next milestone — and the defects it caught were the ones a green test suite, read and found plausible, would have shipped.
