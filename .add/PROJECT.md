# PROJECT — survivor layer (cross-milestone context)

> The durable foundation that outlives every milestone and feeds context into each
> TDD⇄ADD loop. Read this FIRST in any session. Keep it lean — one screen, not a
> manual. Map to the AIDD diagram: Domain = DDD · Spec = SDD (living document) ·
> UI/UX = UDD. When a loop reveals a gap here, come back and update this file.

slug: AIDD-Book · stage: mvp · updated: 2026-06-06 · foundation-version: 14

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
  a FROZEN contract never changes silently (change request → back to SPECIFY) — the freeze
  binds the **data/interface seam** (fields · reject codes · behavior); a **presentation/layout**
  layer iterates freely WITHOUT a re-freeze (v9: the report render re-skinned v2→v3→v4 with zero
  data-seam change); survivor files are never clobbered; writes are atomic; the skill stays lean
  (progressive disclosure) and all state lives on disk (anti-context-rot).
- **Verify re-checks the milestone's frozen exit criteria** after a task changes shape — a
  shared-contract drift turns a gate red, not slips silently to milestone close (v9 · SDD).
- **Residue** (what an evidence auto-gate must escalate to a human) is not limited to
  security·concurrency·architecture — **method/trust-layer edits are a residue category** (v6).

## Spec / Living Document (SDD) — what we are building, now
- Latest shipped → `.add/milestones/v9-1/MILESTONE.md` (phase-detail drill-down). See
  `add.py status` for live rollup. (earlier v1.1 polish tasks remain open.)
- SDD is elicitation-driven, not template-driven: co-specify (Diverge→Converge→Validate
  + ranked least-sure flag) drives drafting at EVERY altitude — foundation (0-setup),
  milestone (scope.md), task (§1); named diverge seeds + foundation lenses make
  "ask before draft" checkable (cospecify-lift v5).
- Frozen contracts (survivor): `set-milestone`, `milestone-done`, `check` exit
  codes; the 7-phase task flow; the milestone tier (`MILESTONE.md` + `depends_on`);
  `report` / `report --json` (read-only awareness) + `report_data` facts seam;
  `report <task>` / `report <m> <task>` (read-only phase drill-down) + `task_phases` extraction
  seam (per-phase fields + `(empty)` fail-closed; smart milestone-first-else-task resolution).
- Surfaces evolve **additively**: a new output tier or field (a WARN level; `warnings`/`warned` in
  `--json`) leaves existing semantics + exit codes unchanged, so no existing consumer breaks — additive
  is the backward-safe way to extend a frozen seam (orphan-task-guard v8-1).
- Settled vs open: SETTLED — minimal engine, one TASK.md/feature, npm `@pilotspace/add`,
  PROJECT.md foundation, dynamic-by-reference guideline injection; **per-phase report
  drill-down** (SHIPPED v9-1: `report <task>` renders each phase's RESULT). OPEN — interactive
  `add.py guide`, Vietnamese quickstart, milestone archive/rotation; cross-task / cross-milestone
  phase DIFF (explicitly out of v9-1 — the next awareness slice if wanted); **deferred enforcement/UX
  from the v6–v8 fold** — `add.py activate <slug>` (re-point the active task among siblings), a
  high-risk-auto friction signal at the dial, a surfaced one-approval review checklist, an automated
  fold-nudge (emission outpaces human fold capacity).
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
- v9 (Awareness surface): **SHIPPED 2026-06-02** — `add.py report [milestone]` rolls per-task
  phase results up under a milestone retrospective (verdict-first label grid · phase track ·
  exit-criteria · waivers · carried learnings); `--json` is the stable facts seam (tool captures
  data, agent formats); `milestone-done` persists the canonical render to `RETRO.md` fail-closed
  (doc written BEFORE the status commit). 208 tests, dual-tree byte-identical, stdlib-only. Proved
  by dogfood: v9's own close generated its RETRO.md byte-identical to the canonical render.
- v9-1 (Phase-detail drill-down): **SHIPPED 2026-06-02** — `add.py report <task>` (and explicit
  `report <m> <task>`) renders a single task's SEVEN phase blocks (specify→observe): each phase's
  captured §N body + reached/current marker, the verify block's GATE sourced from state.json (never
  prose), missing/placeholder → `(empty)`. Two pure seams (`task_phases` + `render_task_detail`),
  smart single-arg CLI (milestone-first-else-task), read-only + fail-closed (utf-8 + OSError guard
  on the read). Purely additive — the v9 rollup is byte-for-byte unchanged. 219 tests, dual-tree
  byte-identical. Dogfood-proved: v9-1's own close reported on itself via the v9 surface.
- v13 (Decision-seam reports): **SHIPPED 2026-06-05** — decide digest (DECIDE NEXT + frozen
  facts seam) · §4-declared tests fallback (`†` footnote) · fence-safe drill-down (fenced
  blocks render byte-verbatim). Two SDD residues OPEN: (a) the `Tests live in:` declaration
  grammar (backticked tokens · `./` task-relative · root-relative with `/` · bare sibling
  shorthand · directory → non-recursive `*.py`) is engine-parsed but stated nowhere — write
  it into the §4 template/guide; (b) declared tokens may name paths outside the project root
  (read-only; leaks only an integer def-count — reviewed at §6, human-confirmed) — a
  confinement Reject rule is a candidate for a future contract version.
- v13-1 (Report hardening): **SHIPPED 2026-06-05** — all three v13 residues closed: the
  `Tests live in:` grammar STATED (template comment + guide section, prose ≡ engine) ·
  declared paths CONFINED to the project root (contract v2: resolve-then-check per file
  read; `..`/absolute/symlink escapes count 0 — the pathlib absolute-join hole
  `root / "/abs"` IS `/abs` was live in v1; future path-resolving contracts must name
  absolute tokens explicitly) · DECIDE NEXT plan-aware (`planned_unscaffolded` additive
  key + footer hint; the foundation-v11 manual cross-check retired by its own sunset).
- v14 (Production-ready ADD): **SHIPPED 2026-06-05** — `add.py audit` (judgment-free seam
  re-verification) · blocking seam-audit CI job + consumer workflow · `risk: high` grammar +
  `unguarded_high_risk_auto` engine guard · `guide  :` phase-playbook line + agent-agnostic
  AGENTS.md block (any agent, CLI alone) · the freeze review checklist · **1.1.0 live on npm
  + PyPI** (tag-driven, guard-gated; npm auth = granular 2FA-bypass token after OIDC would
  not engage — rotation ~90d watched). SDD learnings carried: (a) prose artifacts accrete
  PROPERTY guards across milestones — grep the guards and design to the UNION before any
  rewrite (VALIDATED v15: the union rule's first PREMEDITATED application — a 16-guard
  GETTING-STARTED rewrite landed green first pass); (b) strip comments before machine-token
  matching, or every documentation form of the token self-triggers; (c) a CI job that runs
  another ecosystem's tests must provision THAT ecosystem's declared floor itself (build
  isolation honors it everywhere else).
- v15 (Zero-command on-ramp): **SHIPPED 2026-06-06** — after one install command a newcomer
  reaches their first verified feature purely by talking to the AI: GETTING-STARTED restructured
  around the conversational spine (the 7-phases-by-hand became an escape-hatch appendix), both
  installers end with an AI handoff + inferred `--name/--stage`, and a protocol-walk test drives a
  fresh install → init → lock → first gated task issuing every `add.py` call ITSELF against the
  INSTALLED tree (criterion 3). SDD learning carried: a behavioral JOURNEY test (the protocol walk)
  and a PROSE-coherence test are different guarantees — the walk proved the machinery works at v1
  while the guide still told the human to TYPE the lock; words-exist≠method-works cuts both ways, so
  a green journey is not evidence the guide is coherent. Engine feature-frozen all milestone
  (add.py md5 pinned ×3); the lock moved from human-typed to AGENT-run on the human's explicit
  confirmation, consent prose-guarded — the machine-readable confirm protocol (gap 5) stays OPEN.

## Users (UDD) — UI/UX: design before code
<!-- No-UI project: ADD ships as a CLI + a Claude skill. The "interface" is the
     command surface and the text it prints — there is no screen, so this stays short. -->
- Primary users & jobs: the author (MRQ maintainer) shipping ADD as a product;
  **AI agents** that load the skill; **developers** adopting ADD who must
  read/trust/follow the method.
- The interface (no GUI): the `add.py` command surface + `npx @pilotspace/add`, and the text
  they print. Core flow: `init` → fill foundation → `new-task` → run the loop →
  `verify`/gate → resume any session with `status`.
- "UI states" for a CLI = output states: a clear success line, an empty/idle state
  (nothing to do), and actionable errors with named exit codes — never a bare trace.
- **TUI rendering house rule (no `wcwidth`/`rich`, stdlib-only)**: carry richness on
  width-neutral channels (color on a tty only, honoring `NO_COLOR`/`TERM`); put only ASCII-safe
  text in `len()`-aligned columns; confine Unicode glyphs to line-END or non-aligned row STARTs
  (bullets). Two glyph tiers (Unicode/ASCII) chosen by stdout encoding/`--plain`. The persisted
  render is PLAIN + fixed-width (canonical); color/adaptive-width are a tty-only skin (v9 · UDD).
- **Two render idioms, chosen by PURPOSE (v9-1 · UDD)**: a ROLLUP (`report <m>`) is a scannable
  digest — collapse prose, fit `len()`-aligned columns. A DRILL (`report <task>`) is a READ surface
  where line-structure (scenarios, contract code) carries meaning — preserve physical lines + each
  line's indent, soft-wrap only over-long lines, never clip. Don't force one renderer's rules on
  the other; the shared frozen thing is the DATA seam, not the layout.
- Design source of truth: the skill prose (`SKILL.md` + `phases/*`) and the book.
- What "good" feels like: never lose context across sessions; less doc time than GSD;
  one command to know "where am I and what's next".
- Empty-project `status` now prints a **first-run panel** (`/add` + `new-task` escape hatch) —
  the worst-lost moment (a brand-new project) is actionable, not a bare line (v7/onboarding-align).
- ADDRESSED (UDD, 2026-06-02): the one-approval rubber-stamp risk is met by **co-specification's
  least-sure flag** — the AI ranks the 1–2 most-likely-wrong points bundle-wide and leads the
  single approval with them, instead of a flat all-`[x]` assumptions wall. Deliberately NOT a
  front-checklist (that would re-add the ceremony ADD avoids). Honest residual: the flag aims the
  review but cannot *force* engagement; true enforcement waits on a CI checker (prose ≠ enforcement).
  The reform reaches the **operational artifact**, not only the book: `new-task` now scaffolds the
  ranked least-sure §1 (`templates/TASK.md.tmpl` + the `_FALLBACK_TASK` circuit breaker), pinned by
  `test_cospecify_scaffold.py` so it cannot regress to the flat confirm-list that originally exposed it.
- **One next step at the most-lost moment (v12-1 · UDD):** when the user is most lost (unlocked setup,
  empty project), status must show exactly ONE next move — competing hints dilute the only correct
  action. The unlocked window now replaces the generic resume//add hint with the single review→lock step.
- **A review prompt lives AT the seam (v14 · UDD):** put the checklist where the decision already
  happens, sized to the reviewer's real attention (one minute · six lines · ⚠-first) — a separate
  review artifact is ceremony that competes with the decision instead of aiming it.
- **Precise promises beat catchy absolutes (v15 · UDD):** "zero-command" survived contact with the
  rewrite only as "one **shell** command" — `/add` is still typed. A headline that the product can't
  literally keep erodes trust; name the exact, honest boundary (the install is the one command; the
  loop after it is conversational) rather than the slogan.

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
| 2026-06-02 | ship v9: `report` + `RETRO.md` awareness surface (per-task phase rollup under a milestone retro; `--json` facts seam; close writes the retro fail-closed) | a human should see "what happened / what it cost / what we learned" without reading four files by hand | v9 SHIPPED 2/2, 4/4 criteria; 208 tests; dogfood-proved (own RETRO.md == canonical) |
| 2026-06-02 | freeze the DATA seam, not the presentation | the report layout re-skinned v2→v3→v4 (visual → terminal-correct → human-review) with ZERO data-seam change — pixels iterate, facts are the contract | foundation invariant updated; report-render status = "data seam frozen @ v1 · presentation iterate-freely" |
| 2026-06-02 | verify must re-check the milestone's frozen exit criteria after a task changes shape | a task-contract drift (v3 made `report` stdout multi-valued) silently falsified a v9 exit criterion — caught by the advisor, not a gate | new SDD invariant in §Domain; the criterion was re-pinned to the canonical render |
| 2026-06-02 | TDD house patterns: test pure renderers at canonical args (not via tier-sensitive CLI capture); prove "abort-before-mutate" by monkeypatch-raise + assert-no-commit | StringIO capture auto-selected the ASCII tier; the fail-closed retro write needed its rollback proven, not just read | folded from v9 `[TDD]` deltas; applied in test_report.py + test_retro.py |
| 2026-06-02 | fold v9 learnings → foundation-version 5 (freeze-data-not-presentation · verify-rechecks-criteria · no-wcwidth TUI rule · per-phase drill-down OPEN) | human-gated fold of v9 dogfood evidence | §Domain + §Spec + §UDD updated; 7 deltas folded |
| 2026-06-02 | rule: a surface may not describe a flow whose verify gate is not yet recorded (SDD) | docs outran their gate = the original onboarding drift; honesty = claim only what passed | folded → §Spec; enforced by onboarding-align guards |
| 2026-06-02 | convention: stale-guard sweep at milestone close (ADD) | shipping a milestone can falsify a sibling task's frozen test (v7 ship broke test_v8_docs) | folded → CONVENTIONS.md |
| 2026-06-02 | ship v9-1: `report <task>` phase-detail drill-down (7 phase blocks · gate-from-state · `(empty)` fail-closed · smart milestone-first-else-task CLI) | the v9 rollup shows WHICH phase, not WHAT each phase decided — drill answers the other half, read-only + additive | v9-1 SHIPPED 1/1, 2/2 criteria; 219 tests; dogfood-proved (own RETRO via the v9 surface) |
| 2026-06-02 | trace argparse positional BINDING when a contract adds an optional positional (SDD) | the drafted two-arg `report [m] [task]` made drill-down UNREACHABLE (a lone arg always binds to the 1st positional) — advisor caught it before freeze; chose smart single-arg instead | folded → §Spec CLI seam; the obvious contract shape can silently strand a code path |
| 2026-06-02 | two render idioms by purpose: rollup collapses prose+columns, drill preserves line-structure (UDD) | a drill-down is a READ surface (scenarios/code shape matters), not a scannable digest — `_detail_body` vs `_wrap` diverge deliberately | folded → §UDD; shared frozen thing is the DATA seam, not the layout |
| 2026-06-02 | fold v9-1 learnings → foundation-version 6 (argparse-binding-trace · freeze-data-paid-off · utf-8+OSError-on-read · two-render-idioms) | human-gated fold of v9-1 dogfood evidence | §Spec + §UDD updated; 4 deltas folded; `[ADD] freeze-data-not-presentation` proven (ragged wrap shipped as disclosed debt, no re-freeze) |
| 2026-06-02 | reframe Specify as **co-specification** (brainstorm by both → AI drafts → human validates with AI advice); the advice is a ranked **least-sure flag**, bundle-wide at the freeze seam | the one-approval front risked rubber-stamping a flat all-`[x]` assumptions wall (the open §UDD risk); rank the uncertainty + name the 1–2 most-likely-wrong so the single approval is *aimed*, without adding GSD-style ceremony — it reshapes the assumptions list ADD already had | book 03 + appendices A/B/C/D + skill `phases/1-specify` · `run.md` · `phases/3-contract` · `SKILL.md`, all trees byte-identical; 219 tests green; `Framings weighed:` persists the brainstorm; "none material" must still name the biggest risk; **honest limit:** the flag aims the review but cannot *force* engagement (a self-asserted "human engaged" is barred; true enforcement deferred to a CI checker) |
| 2026-06-02 | publish npm under `@pilotspace/add` (was `@mrq/add`); PyPI ships as `add-method` | the only npm credential is the `pilotspace` account, which has no access to the `@mrq` scope (npm 404'd the publish — `@mrq` was aspirational brand, never registered); `add-method` is taken on npm, `@pilotspace/add` is free and matches the `pilotspace` GitHub org | renamed across package.json · README · GETTING-STARTED · cli.js · skill `phases/0-setup` (+ both mirrors) · 4 tests; 231 tests green; npm = @pilotspace/add@1.0.0, PyPI = add-method 1.0.0 |
| 2026-06-03 | sync names: rename PyPI dist + console script `add-method` → `pilotspace-add` (npm `@pilotspace/add` unchanged); publish jobs made idempotent, version held at 1.0.0 | user asked to align the two install names; PyPI has no scopes so exact parity is impossible — `pilotspace-add` mirrors the npm scope and (unlike npm `@pilotspace/add@1.0.0`, already live) PyPI was unpublished so the rename costs nothing; idempotent npm/pypi publish lets a single `v1.0.0` tag debut PyPI at 1.0.0 while npm safely skips, keeping both registries at 1.0.0 | import pkg `add_method` kept (src/installer/_bundled untouched); renamed pyproject name+script · `_cli`/`__init__`/`__main__`/`_installer` · root+pkg README · root GETTING-STARTED · CHANGELOG · publish.yml; 234 tests green; `npx @pilotspace/add` + `pip install pilotspace-add` |
| 2026-06-03 | fold v5 learnings → foundation-version 7 (co-specify-at-every-altitude · prose-guides-are-TDD-able · elicitation-driven-SDD) | human-gated fold of cospecify-lift dogfood evidence | §Spec + CONVENTIONS updated; 3 deltas folded (ADD/TDD → CONVENTIONS, SDD → §Spec) |
| 2026-06-03 | fold v6–v8 learnings → foundation-version 8 (18 open deltas: 4 new conventions · 9 reinforce existing via flip-cite · 4 deferred to §Spec OPEN) | human-gated bulk fold of the v6/v7/v8/v8-1 open-delta backlog; consolidate not append-18-bullets (lean foundation, one screen) | +3 CONVENTIONS bullets (verify-shipped-path · frozen-guard→fix-build-not-matcher · message-specific-assert) + 1 §Spec bullet (additive-evolution); reinforcements flip-cited append-only (no dup text); backlog → §Spec OPEN; onboarding-align [TDD] left open (human-deferred 2026-06-02) |
| 2026-06-04 | ship v12 Autonomous Onboarding: installer drops files only → `/add` finds an un-inited repo → AI runs `init --await-lock`, drafts the foundation (brownfield silent / greenfield 4-lens) + SETUP-REVIEW.md, build-boundary gate holds pre-lock; one human lock-down freezes foundation+first-scope+first-contract | the human's only setup act becomes one signature; the AI owns init+drafting end-to-end | v12 SHIPPED 6/6, 8/8 criteria; 322 tests; add.py engine unchanged this session (book/installer tail); RETRO.md written |
| 2026-06-04 | validated: the conservative autonomy dial's escalation path works under real concurrency — worker B returned ESCALATE (not auto-PASS) and a human recorded the verify gate | the dial's "stop for the human" row had never been exercised in a real parallel run until v10's deltas-lint/deltas-report | confirms run.md's conservative row; no code change — folded foundation-version 9 |
| 2026-06-04 | fold v10+v12 learnings → foundation-version 9 (9 open deltas: 4 new conventions · 1 dial-validated note · 3 → v12-1 follow-up tasks · 1 onboarding-words closed via flip-cite) | human-gated fold clearing the v10/v12 open-delta backlog at v12 close; consolidate not append-9-bullets (lean foundation) | +4 CONVENTIONS bullets (publish-hook-subprocess · two-regex-grammar-lint · worktree-from-HEAD · scope-audit-unscaffolded-close); cmd_status-hint + multiline-delta-render + _DELTA_RE-dedup → v12-1 tasks; onboarding-align [TDD] folded (reinforces existing Words-exist≠method-works); deltas flipped open→folded |
| 2026-06-04 | fold v12-1 learnings → foundation-version 10 (5 open deltas: 3 new conventions · 1 worktree-from-HEAD reinforcement flip-cite · 1 UDD one-next-step bullet) | human-gated fold at v12-1 close; all 5 confirmed (none rejected) | +3 CONVENTIONS bullets (comment-literal-phantom-dup · dedup-absorbs-deleted-form · reverify-routed-delta-gap); worktree-from-HEAD flip-cited (the check must EXECUTE pre-spawn); §UDD one-next-step; deltas flipped open→folded |
| 2026-06-05 | fold v13 learnings → foundation-version 11 (6 open deltas: 4 new conventions · 1 §Spec v13-shipped bullet carrying 2 SDD residues) | human-gated fold at v13 close; all 6 confirmed (none rejected); the 3 actionable residues (Tests-live-in grammar doc · confinement Reject rule · DECIDE-NEXT planned-task hint) stay visible as §Spec OPEN pending a next-milestone intake | +4 CONVENTIONS bullets (diff-§4-target-nouns · red-fixture-exceeds-hidden-threshold · decide-next-is-state-only · security-line-always-escalates); §Spec v13 bullet; deltas flipped open→folded |
| 2026-06-05 | fold v13-1 learnings → foundation-version 12 (5 open deltas: 2 new TDD conventions · 1 security-line flip-cite validation · 1 convention RETIRED by its own sunset clause — a first · 1 SDD absolute-join rule into §Spec) | human-gated fold at v13-1 close; all 5 confirmed (none rejected) | +2 CONVENTIONS bullets (behavioral-scaffold-test · template-fixture-inherits-examples); decide-next cross-check retired (engine hint shipped); security-line rule validated cheap in practice; §Spec v13-1 bullet; deltas flipped open→folded |
| 2026-06-05 | npm publish auth = granular 2FA-bypass token (NPM_TOKEN secret); PyPI stays OIDC; OIDC trusted publishing for npm ATTEMPTED and parked (mint never engaged from the workflow: 404 then ENEEDAUTH with form byte-exact, npm ≥11.5, id-token: write, no token config) | the 1.1.0 release act hit four auth-layer failures, each failing closed; Tin pivoted the mechanism after OIDC proved opaque — a working release now beats a perfect auth story | v1.1.0 live on BOTH registries (run 27009563639); rotation ~90d watched in §7 + publish.yml header; OIDC revisit-later note kept in the workflow header |
| 2026-06-05 | fold v14 learnings → foundation-version 13 (14 open deltas: 9 new conventions · 1 publish-hook flip-cite validation · 1 §Spec v14 bullet carrying 3 SDD learnings · 1 §UDD seam-sized-review bullet) | human-gated fold at v14 close; all 14 confirmed (none rejected) | +9 CONVENTIONS bullets (protocol-walk · refuse-on-drift · arrange-through-CLI-contracts · strengthen-never-silent · epoch-debt-at-the-gate · contradicting-subset · dogfood-own-rule · dial-absorbs-change-requests · pivot-mechanism-on-human-word); §Spec v14 bullet; §UDD seam bullet; deltas flipped open→folded |
| 2026-06-06 | ship v15 Zero-command on-ramp: after one install command a newcomer reaches their first verified feature by talking to the AI — GETTING-STARTED conversational spine (7-phases-by-hand → escape-hatch appendix); both installers print an AI handoff + infer `--name/--stage`; protocol-walk test drives fresh-install→gated-task issuing every add.py call itself; the lock moves human-typed → AGENT-run on the human's explicit confirmation (consent prose-guarded) | the human's only post-install act is conversation; the CLI becomes the agent's hands + the human's override, never a required keystroke | v15 SHIPPED 3/3, 3/3 criteria; 457 tests; engine feature-frozen (md5 pinned ×3); a CR v2 closed a cross-surface gap (same human-types instruction in 2 unswept guides) found by the adversarial lens, not the suite |
| 2026-06-06 | fold v15 learnings → foundation-version 14 (9 open deltas: 4 new conventions · 1 §Spec v15 bullet · 1 §UDD precise-promises bullet · 2 flip-cite reinforcements) | human-gated fold at v15 close; all 9 confirmed (none rejected) | +4 CONVENTIONS bullets (pin-behavior-at-edges · multi-surface-parity-hunter · cross-cutting-reword-enumerates-every-surface · move-who-executes-needs-tight-trigger); §Spec v15 bullet (behavioral-journey≠prose-coherence); §UDD precise-promises bullet; UNION-rule + reverify-routed-gap flip-cited as validated; deltas flipped open→folded |
