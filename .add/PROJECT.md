# PROJECT — survivor layer (cross-milestone context)

> The durable foundation that outlives every milestone and feeds context into each
> TDD⇄ADD loop. Read this FIRST in any session. Keep it lean — one screen, not a
> manual. Map to the AIDD diagram: Domain = DDD · Spec = SDD (living document) ·
> UI/UX = UDD. When a loop reveals a gap here, come back and update this file.

slug: AIDD-Book · stage: mvp · updated: 2026-06-02 · foundation-version: 4

---

## Domain (DDD) — the language and the boundaries
- Core concepts: **task** (one feature), **milestone** (depth-bounded group of
  tasks), **phase** (specify→…→observe→done), **gate** (PASS·RISK-ACCEPTED·HARD-STOP),
  **contract** (frozen shape), **survivor layer** (durable artifacts), **stage**
  (prototype·poc·mvp·production).
- Bounded contexts / modules: **tooling** (`add.py` + `state.json` — the state
  engine), **skill** (router `SKILL.md` + on-demand `phases/*` — what Claude loads),
  **book** (`docs/*` — the trust layer users read).
- Invariants that must always hold: the `phase:` marker in TASK.md == `state.json`;
  a FROZEN contract never changes silently (change request → back to SPECIFY);
  survivor files are never clobbered; writes are atomic; the skill stays lean
  (progressive disclosure) and all state lives on disk (anti-context-rot).
- **Residue** (what an evidence auto-gate must escalate to a human) is not limited to
  security·concurrency·architecture — **method/trust-layer edits are a residue category** (v6).

## Spec / Living Document (SDD) — what we are building, now
- Active milestone → `.add/milestones/v7/MILESTONE.md` (auto by default + one-approval
  front). See `add.py status` for live rollup. (earlier v1.1 polish tasks remain open.)
- Frozen contracts (survivor): `set-milestone`, `milestone-done`, `check` exit
  codes; the 7-phase task flow; the milestone tier (`MILESTONE.md` + `depends_on`).
- Settled vs open: SETTLED — minimal engine, one TASK.md/feature, npm `@mrq/add`,
  PROJECT.md foundation, dynamic-by-reference guideline injection. OPEN — interactive
  `add.py guide`, Vietnamese quickstart, milestone archive/rotation.
- v6 (The Self-Driving Run): DESIGNED + dogfood-tested, **NOT human-validated** — the
  dynamic run / evidence auto-gate is safe only with a human gate or a CI enforcer separate
  from the agent (a self-asserted gate is circular); the fold is the new human bottleneck.
  The principle 6/7 reframe (automated verification) needs human review before it is trusted.
- v7 (Auto by default — the one-approval flow): **SHIPPED 2026-06-02** — both gates PASS
  (human diff review; conservative scope), milestone done. Human-directed REVERSAL of v6's
  `conservative` default → `auto` is the default; the human-led front is ONE approval at the
  contract-freeze seam. Two safeties kept: the seam stays human (so "never self-gate a human-led
  gate" holds) and high-risk / method-defining scope is guarded (`unguarded_high_risk_auto`) —
  security is always HARD-STOP. **Onboarding aligned** (onboarding-align, PASS): the surfaces
  describe this single flow; the v6/v7 doc drift is resolved.
  Enforcement is still PROSE, not engine (DEFERRED, tracked in v7 MILESTONE: a CI enforcer + tests
  that a high-risk scope actually lowers and the one-approval seam is honored).

## Users (UDD) — UI/UX: design before code
<!-- No-UI project: ADD ships as a CLI + a Claude skill. The "interface" is the
     command surface and the text it prints — there is no screen, so this stays short. -->
- Primary users & jobs: the author (MRQ maintainer) shipping ADD as a product;
  **AI agents** that load the skill; **developers** adopting ADD who must
  read/trust/follow the method.
- The interface (no GUI): the `add.py` command surface + `npx @mrq/add`, and the text
  they print. Core flow: `init` → fill foundation → `new-task` → run the loop →
  `verify`/gate → resume any session with `status`.
- "UI states" for a CLI = output states: a clear success line, an empty/idle state
  (nothing to do), and actionable errors with named exit codes — never a bare trace.
- Design source of truth: the skill prose (`SKILL.md` + `phases/*`) and the book.
- What "good" feels like: never lose context across sessions; less doc time than GSD;
  one command to know "where am I and what's next".
- Empty-project `status` now prints a **first-run panel** (`/add` + `new-task` escape hatch) —
  the worst-lost moment (a brand-new project) is actionable, not a bare line (v7/onboarding-align).
- OPEN (UDD): the one-approval seam risks **rubber-stamping** Scenarios/Contract — wants a
  surfaced front-checklist so the single gate stays a real review, not a reflex approve.

## Key Decisions (append-only)
| date | decision | why | outcome |
|------|----------|-----|---------|
| 2026-05-28 | scope npm name `@mrq/add` | community brand | published name fixed |
| 2026-05-28 | milestone (SDD) tier = thin MILESTONE.md + deps | scale without bloat | shipped v1.0 |
| 2026-05-29 | foundation = one PROJECT.md (not 3 files) | minimal, GSD-proven | this doc |
| 2026-05-29 | guideline injection dynamic-by-reference | avoids context-rot (ETH) | v1-2 |
| 2026-05-29 | UDD = UI/UX-Driven, lives foundation-only | most tasks have no UI; no dead-weight step | this section is UDD's home |
| 2026-05-29 | docs English-only; drop the Vietnamese translation + non-English branding | single-language product surface, simpler to maintain | vi-quickstart descoped; `guide` covered in the EN Quickstart |
| 2026-06-01 | v6 "Self-Driving Run" scoped + dogfooded full-auto (AI self-gated contracts+verify) | stress-test the auto-gate by running it on the method itself | shipped; 17 open deltas; 14 folded (v2); v6 NOT human-validated |
| 2026-06-01 | fold v6 learnings → foundation-version 2: never self-gate a human-led gate · dogfood md5 parity · words-exist≠method-works · residue includes method-edits | human-gated fold of v6 dogfood evidence | CONVENTIONS.md + §Domain + §Spec updated; deltas folded |
| 2026-06-01 | v7: flip the autonomy default `conservative` → `auto` (reverses v6/foundation-v2 + retires reject code `auto_by_default`) | user-directed: low-friction default for ordinary scope; chosen with the contradiction visible | run.md dial + book principle 5 reframed; foundation-version 3 |
| 2026-06-01 | v7: compress the human-led front to ONE approval at the contract-freeze seam (AI drafts Spec+Scenarios+Contract+Tests bundle) | reduce human-led front to "approve the spec/contract once" per user | run.md "one-approval front"; seam stays human |
| 2026-06-01 | v7: keep the seam human + guard high-risk scope (`unguarded_high_risk_auto`); security stays HARD-STOP | preserve the v6 learning under an auto default — autonomy ∝ low risk (principle 5 substance) | high-risk guard in run.md; deferred: a CI enforcer (prose≠enforcement) |
| 2026-06-02 | ship v7: both gates driven to PASS (human diff review, conservative scope), milestone done; then align onboarding to the one shipped flow | earn the gate before the docs claim it — the v6/v7 doc drift existed because docs outran their verify gate | v7 SHIPPED; onboarding-align PASS; drift resolved; foundation-version 4 |
| 2026-06-02 | rule: a surface may not describe a flow whose verify gate is not yet recorded (SDD) | docs outran their gate = the original onboarding drift; honesty = claim only what passed | folded → §Spec; enforced by onboarding-align guards |
| 2026-06-02 | convention: stale-guard sweep at milestone close (ADD) | shipping a milestone can falsify a sibling task's frozen test (v7 ship broke test_v8_docs) | folded → CONVENTIONS.md |
