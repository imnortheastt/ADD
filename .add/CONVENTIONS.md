# CONVENTIONS  (survivor layer — set once, kept for the whole project)

Language/framework:
  - Tooling: Python 3.12+ (standard library only — no third-party packages).
  - Installer: Node.js >= 16 (built-in modules only).
  - Method content: Markdown (the skill + the AIDD book).

Folders:
  - `add-method/`            the shippable npm package (`@pilotspace/add`)
    - `skill/add/`           thin router SKILL.md + `phases/*.md` (progressive disclosure)
    - `tooling/`             `add.py` (scaffolder + state tracker) + `templates/` + `test_add.py`
    - `bin/cli.js`           the `npx @pilotspace/add init` installer
    - `docs/`                the AIDD book bundled as the trust layer
  - `*.md` (repo root)       the AIDD book source chapters
  - `.add/`                  ADD runtime for THIS repo (dogfooding): state, tasks, survivor files

Naming: kebab-case files; snake_case Python; lowerCamelCase JS; task slugs alphanumeric + - _.

Lint/format: keep Python stdlib-idiomatic and type-hinted; no formatter enforced yet (add ruff in CI later).

Errors: machine-readable, never free text. The Python tool exits non-zero with `add: error: <msg>`.

Architecture:
  - The skill is thin and stateless; ALL state lives in `.add/state.json` (anti-context-rot).
  - The Python tool is the only writer of state; writes are atomic (temp + os.replace) and never clobber.
  - The method is tool-agnostic: gates are enforced by process/CI, not inside the agent.

## Method learnings (folded from OBSERVE deltas)

- (ADD) **Never self-gate a human-led gate.** The agent that built a change cannot also approve it —
  Verify has no AI role. Trust-layer/method edits especially require a separate human sign-off, and a
  run's prose guardrails (touch-boundary, autonomy dial) are not enforcement until a CI gate distinct
  from the agent exists. [v6 dogfood: 6 self-gated PASSes, none human-verified — folded foundation-version 2]
- (ADD) **Dogfood parity.** The `.add/` runtime mirror and the canonical `add-method/` tree must stay
  md5-identical for every synced artifact (SKILL.md, run.md, fold.md, …); a structural test asserts it.
  A contract's MIRRORS clause must enumerate ALL copies — the v18 clause named two trees and missed the
  `_bundled` third; the build propagated anyway, but the clause under-promised the surface.
  [xml-prompt-structure — folded foundation-version 18]
- (TDD) **Words-exist ≠ method-works.** Structural/string tests prove an artifact reads as worded, not
  that the behavior works or is enforced (recurring gap). Where behavior matters — md5 parity, an
  enforced default, real convergence — add a behavioral test, not a presence assertion.
- (ADD) **Stale-guard sweep at milestone close.** Shipping a milestone can falsify a *sibling* task's
  frozen test — a guard may encode a world-state the ship just changed. At close, run the full suite and
  re-aim or retire any guard the ship invalidated, as an explicit change-request (human-approved), never
  a silent weakening to make the suite green. [v7 ship broke test_v8_docs (it required the now-removed
  v6/v7 caveat); re-aimed → test_docs_post_ship_honesty — folded foundation-version 4]
  Reinforced v16: a milestone of several conversion tasks also wants a dedicated green-state SWEEP task that
  runs the UNION of all guards at once (full suite + both parity guards + audit + a vocab census) — per-task
  greens can each pass while a cross-file interaction is red; the sweep is the only run that proves the whole.
  [mirror-greenstate — folded foundation-version 15]
  Recurred at the first `compact` run: heavy archive disables any dogfood guard that reads a moved task
  file — a skip-guarded test goes silently dark (skip ≠ red, so the sweep must check the SKIP count too);
  re-aim such guards archive-aware (active tree, else `.add/archive/*/tasks/`), keeping the fresh-install
  skip. [v18 close — folded foundation-version 18]
- (ADD/SDD) **Docs must not outrun their gate.** A surface may not describe a flow whose verify gate is
  not yet recorded PASS. The v6/v7 onboarding drift existed precisely because three surfaces claimed v7
  before its tasks passed. Claim only what the gate has earned. [folded foundation-version 4]
- (ADD) **Co-specify at every altitude.** The brainstorm move — Diverge (framings + open questions) →
  Converge (draft the whole artifact) → Validate (show the ranked least-sure flag first) — is not
  task-only; it drives foundation (0-setup → PROJECT.md) and milestone (scope.md → MILESTONE.md)
  drafting too. One flag grammar across all three; each guide self-contained (progressive disclosure).
  Elicit before drafting; never draft from thin input. [cospecify-lift — folded foundation-version 7]
- (TDD) **Prose-guide tasks are red→green-testable.** A docs/guideline change is TDD-able by asserting
  content anchors (required section present + ordering) + cross-tree byte-identity (canonical ==
  bundled == dogfood mirror), not behavior. Write the assertion red before the edit; a parity test
  backstops drift. Validated again by verify-integrity: a prose/method change is testable by anchor-presence + a
  one-hash mirror-parity across guide ×3 / book ×4 / template ×3 / glossary, the engine held byte-identical to the pin.
  [cospecify-lift: test_cospecify_lift red→green + test_bundle_parity — folded foundation-version 7 · reinforced verify-integrity fv27]
  Held again v16 across a 7-file batch AND a fenced verbatim doc: every guard authored RED (no blocks yet) →
  green by the doc edit alone, no test weakened — RED-before-build holds even when there is no runtime to
  cover. [phase-guides-xml + xml-convention — folded foundation-version 15]
- (ADD) **Verify a gap against the shipped path.** A finding seen through the wrong entry point isn't
  real — bare `add.py init` bypasses `bin/cli.js` (which does the bundling), so "init doesn't bundle the
  skill+book" was a test artifact. Reproduce a gap on the SHIPPED path before scoping a fix.
  [install-onramp — folded foundation-version 8]
- (ADD) **A frozen guard that fails mid-build is fixed in the BUILD output, never the matcher.** Widening
  a frozen matcher inline — even to fix a real false-negative — is self-ratifying a frozen-contract change;
  route it as a human-ratified change-request at test-design time (Rule 3, phase 4), not a silent inline
  edit logged as "no test weakened". [milestone-onboarding-docs — folded foundation-version 8]
  Re-validated: a bonus `project_autonomy` key added to `status --json` tripped the frozen-surface guard
  (`json_surface_unsanctioned_key`); the BUILD was fixed (the key removed), the frozen test left intact —
  even a "harmless additive" key stays inside the frozen contract. [init-auto-default — flip-cite fv24]
- (TDD) **Assert a message-specific phrase, not an ambient token.** A substring that paths/scaffold/harness
  can also contain false-GREENs (a `/add` match off the tmpdir name); assert a phrase only the real
  behavior emits ("not attached to a milestone"). [orphan-task-guard — folded foundation-version 8]
- (TDD) **Prove a publish-time hook without publishing.** Run the hook command as a subprocess and assert
  it executed the guard and exited 0 — it reds on broken/misspelled wiring but cannot prove the registry
  (npm/PyPI) honours the hook; name that wiring-vs-live limit explicitly. [ship-clean — folded foundation-version 9]
  Validated live at v14: the hook's REAL publish-path run caught an env gap (apt setuptools below
  pyproject's declared floor) no local run could see — keep tests in the publish path even when they
  "duplicate" the guard job. [release-1-1-0 — folded foundation-version 13]
- (TDD) **Lint a grammar with two regexes, not one.** A broad attempt-detector ("does this line *try* to be
  a tag/delta?") and a strict valid-shape matcher are distinct abstractions; conflating them either misses
  malformed attempts or false-skips them. [deltas-lint — folded foundation-version 9]
- (ADD) **Spawn a worker's worktree from current HEAD, never a stale base.** A worktree forked off an old
  commit forces the worker to recreate the frozen front byte-identically; after committing the front, verify
  `worktree base == HEAD` before spawning. [deltas-report — folded foundation-version 9] Recurred
  v12-1: stream B forked one commit behind the front (7f7ee54 vs c896698) because the orchestrator never
  ran the check — it must EXECUTE pre-spawn, not merely exist in streams.md (words-exist ≠ method-works).
  [status-lock-hint — folded foundation-version 10]
  Runtime reality v19: on a runner that creates the worktree AT spawn from a pool (Claude Code), that pool
  can hand out a STALE base, so the pre-spawn evidence cell is UNSATISFIABLE — verified 2/2 workers forked a
  v17-era base. The `unverified_fork_base` check then SHIFTS to worker step-0 (sync-to-base + re-echo)
  verified by the orchestrator at MERGE-time before merge-back — the check shifts, it never skips (the
  founding lesson: a check that lives only in prose never runs, recursing onto the wave ledger itself).
  [shared-engine-pin + fence-aware-section — folded foundation-version 19; streams.md text amended by the
  wave-protocol-runtime task]
- (ADD) **Close an unscaffolded milestone by a scope audit, not by building its task list.** A planned-but-
  never-scaffolded milestone (0 TASK.md) may have tasks already superseded/delivered/obsolete by later work;
  audit each against shipped code and keep only the real residue. [ship-clean — folded foundation-version 9]
- (TDD/ADD) **A source-scan guard counts comments too.** A test that greps source lines for a literal
  (e.g. a regex enumeration) registers comment/docstring hits as phantom duplicates; keep the literal out
  of prose — or better, scope the scan to compiled-regex literals (known debt: the v12-1 one-source guard
  is the line-scan form, so any legitimate future use of the literal in add.py prose trips it).
  [delta-grammar-dedup — folded foundation-version 10]
- (ADD) **A dedup's canonical must absorb the deleted copy's form.** When collapsing duplicate
  regexes/validators, diff their shapes first (strict vs permissive) and freeze the form every call site
  needs — `_task_prose` feeds un-stripped lines, so the canonical `_DELTA_RE` had to adopt the permissive
  leading `\s*`. [delta-grammar-dedup — folded foundation-version 10]
- (ADD) **Re-verify a routed delta's gap before scoping it.** A fold can route an already-closed delta as
  a follow-up task — v12-1's multiline-render gap had been fixed by v11 `1b817c0` BEFORE the fold scoped
  it. At fold time, empirically check the gap still exists against current code.
  [deltas-multiline-render — folded foundation-version 10]
  Validated v15: re-verifying the routed gap shrank installer-handoff from "implement the handoff"
  to "pin it + fix the hint" — half the scoped work was already shipped (v12). [installer-handoff —
  folded foundation-version 14]
- (TDD) **Diff §4's coverage-target nouns against the test list before declaring red-complete.**
  A red suite can under-cover its own stated target — two §4-mandated branches (3rd marker
  prefix, milestone --json key-set) were only caught at verify. At the tests phase, walk the
  §4 target noun-by-noun against the actual test names. [decide-digest — folded foundation-version 11]
- (TDD) **A right-reason red may need the fixture to exceed a hidden threshold — name it in the
  test constants.** Fenced lines under the render width were already verbatim; only over-width
  fixtures exposed the wrap/collapse, so the red condition lived above width 72. Name the
  threshold beside the constant ("deliberately > width 72") so the red reason is auditable.
  [fence-safe-wrap — folded foundation-version 11]
- (ADD) **DECIDE NEXT is state-only — cross-check it against MILESTONE.md's planned task list
  before acting.** The digest cannot see planned-but-unscaffolded tasks (it said "fold + archive"
  with 2 of 3 planned tasks not yet created); until the engine grows a "n planned, not yet
  scaffolded" hint, the orchestrator does that diff at every decision seam.
  [decide-digest — folded foundation-version 11] **RETIRED by its own sunset clause** (2026-06-05):
  the engine grew the hint (`_planned_unscaffolded`, v13-1 decide-planned-hint) — the manual diff
  is no longer required. Kept as precedent: write conventions WITH a sunset condition so the
  fold-out decision is mechanical. [decide-planned-hint — folded foundation-version 12]
- (ADD) **Anything written on a §6 security line escalates to the human gate — whatever the
  apparent severity.** Under `autonomy: auto` the agent may not reclassify its own security-line
  note as "no finding" and auto-PASS; writing it on that line IS the escalation trigger
  (security judgment belongs to the human — rule 4). [tests-declared-fallback — folded foundation-version 11]
  Validated in practice v13-1: the resolve()-metadata note took ONE question to adjudicate —
  escalation is cheap, self-clearing is the only expensive path.
  [declared-path-confinement — folded foundation-version 12]
- (TDD) **Test a scaffold-template change behaviorally, not only by file anchors.** Run the
  scaffolder in a tmp project and assert the GENERATED artifact carries the change — that pins the
  template→scaffold copy path a pure file-anchor test misses.
  [declare-grammar-doc — folded foundation-version 12]
- (TDD) **A fixture that reuses the scaffolded template inherits its example rows.** A prose parser
  tested against a real scaffold can match template placeholders/examples (the "User can…" exit
  criterion read as a task slug); scope parsers to their section and treat the template's own
  placeholder rows as a guard case. [decide-planned-hint — folded foundation-version 12]
- (TDD) **Protocol-walk a user-journey exit criterion.** When the criterion IS a journey ("an agent
  starting from AGENTS.md alone can…"), write the test that executes it literally: parse the entry
  artifact for its instructions, run them, assert the destination — it pins the criterion itself,
  not a proxy. [agent-portability — folded foundation-version 13]
- (TDD) **Refuse-on-drift before executing a repo-extracted string.** A test that runs a command
  extracted from a repo artifact (a ci.yml run line) must assert the extracted value equals the
  pinned constant BEFORE executing, so drift turns the suite red without ever running unpinned
  input. [audit-ci — folded foundation-version 13]
- (TDD) **Arrange-through-CLI inherits the engine's input contracts.** A fixture arranging through
  the real engine crashes on the engine's own validation (the RISK-ACCEPTED arrange step needed the
  waiver flags) — stronger than file-writing, but budget for fidelity to its argument grammar.
  [gate-audit — folded foundation-version 13]
- (ADD) **A strictly-strengthening in-build test amendment is legal but never silent.** Disclose it
  at the gate beside the security note that motivated it, and let the human adjudicate both in one
  escalation. [audit-ci — folded foundation-version 13]
- (ADD) **New enforcement over a legacy board: adjudicate epoch debt at the human gate.** A new
  audit applied to old records surfaces convention-epoch debt as TRUE positives — retro-ratify as
  an honest present-day act if the human so decides; never auto-grandfather, never fabricate past
  records. [gate-audit — folded foundation-version 13]
- (ADD) **Bulk adjudication surfaces the CONTRADICTING SUBSET, never just the count.** Before
  stamping N records, grep the target set for text that negates the act being stamped and show that
  subset — a blanket stamp wrote "approved" onto 6 records whose own text said the opposite, and the
  shape-only audit reported clean over it. [gate-audit — folded foundation-version 13]
- (ADD) **A method-defining task dogfoods its own rule in its header.** The task that ships a guard
  declares the tokens the guard reads; the gate that records it becomes the rule's first live proof.
  [high-risk-signal — folded foundation-version 13] Same for a seam-discipline rule at its own
  approval seams: the freeze and gate asks already run in the rule's shape before it lands — cheap
  live validation. [question-summary-layer — folded foundation-version 17]
- (ADD) **A hard-to-reverse act under the conservative dial absorbs repeated change requests
  cleanly.** Five contract versions in one release act, each human-worded, no test weakened, zero
  partial state — the dial's cost is questions, never corruption. [release-1-1-0 — folded foundation-version 13]
- (ADD) **When a service's silent auth fallback hides the broken layer, pivot the mechanism on the
  human's word.** Two OIDC-shaped failures (404, ENEEDAUTH) named no cause; the token pivot went
  green first try — against an opaque external seam, switching mechanisms beats deeper debugging.
  [release-1-1-0 — folded foundation-version 13]
- (TDD) **Pin behavior at the edges first.** Happy-path behavioral pins found nothing new; the
  missing-VALUE edge found the real bug — cli.js silently dropped a valueless `--stage`/`--name`
  while the pip twin errored. Spend the first behavioral assertions on the boundary inputs, not the
  golden path. [installer-handoff — folded foundation-version 14]
- (ADD) **Pair every multi-surface build with an adversarial parity hunter.** The suite checks each
  surface in isolation, so a divergence between twins (cli.js vs argparse) passes green; only a
  cross-surface lens that diffs the surfaces against each other catches it. [installer-handoff —
  folded foundation-version 14]
- (ADD) **A cross-cutting reword enumerates EVERY surface carrying the pattern before freezing** —
  companion guides AND the book, swept in the same grep as the gap-named file. Scope only the one
  file the gap named and a green structural suite (even a passing protocol walk) will sit atop the
  SAME defect in unswept twins; here the human-types-the-lock instruction survived in two unswept
  guides past a green v1 — the cross-surface lens, not the suite, caught it → CR v2. [skill-onramp —
  folded foundation-version 14]
- (ADD) **Moving WHO-EXECUTES a gated action (human→agent) keeps the DECISION human only if the
  trigger is defined tightly.** "Recorded confirmation" needed "an explicit yes to the gate itself"
  so an eager agent can't read ambient mid-stream agreement as consent; prose-guard the consent and
  name the machine-readable enforcement as a deferral, never silent. [skill-onramp — folded
  foundation-version 14]
- (ADD) **Tag by AUDIENCE — a rendered doc wraps the intact fence; a consumed one tags bare.** A published
  page (appendix-b) must keep each code fence INTACT and wrap it (`<prompt>` + a blank line each side,
  load-bearing so CommonMark still parses the fence) — REMOVING the fence renders the body as live markdown
  and silently swallows `<…>` placeholders + mangles indented lines; a skill file the agent reads as TEXT can
  tag bare. The fence-exemption clause is load-bearing, not decorative: a fence is self-marking, so never wrap
  one — which is exactly why the engine docs stayed at the two tags the first-use map reserved.
  [appendix-templates-xml + engine-docs-xml — folded foundation-version 15]
- (TDD) **A vocab/structure test is BLIND to rendering — guard the render structurally.** "Tags are valid" ≠
  "the page renders". After stripping fences, assert no `<lowercase>` placeholder and no ≥4-space-indent prose
  line survives OUTSIDE a fence — the structural proxy for "fences were wrapped, not removed" that a vocab
  check cannot make. A green vocab suite over a broken page is the trap. [appendix-templates-xml — folded foundation-version 15]
- (TDD) **Author a content guard with BOTH halves, then triage its RED.** A content guard needs its positive
  AND negative half (a tag PRESENT in raw text AND ABSENT after the transform) — present-only misses a
  deletion, absent-only misses a leak. And a freshly-authored assertion can fail for the WRONG reason (an
  `assertRegex`/`re.search` with no DOTALL cannot match a multi-line block); triage RED as "not converted" vs
  "the assertion can't express its intent" before trusting it. [engine-docs-xml — folded foundation-version 15]
- (TDD) **A multi-file convention needs a CENSUS guard, not only per-file subset checks.** Count that all N
  expected tags appear (WHOLE) AND no unexpected tag appears (CLOSED) across the entire surface — it catches a
  tag that drifted off-vocabulary in a file the per-file table forgot to enumerate. The per-file
  narrative-enumeration list is what makes each over-tag guard real in the first place, and it must GROW with
  every task or the guard goes hollow. [mirror-greenstate + phase-guides-xml + xml-convention — folded foundation-version 15]
  A NEW prose section is unguarded until enumerated — add it to the per-file table the moment it lands,
  in the same task that creates the section. [intake-interview — folded foundation-version 18]
- (ADD) **A verbatim-reproduction transform is a verifying SCRIPT, not a hand-edit.** When a transform must
  preserve bytes (a "verbatim reproduction" doc), do it with a script that asserts the invariant — bodies
  byte-identical · tag/fence counts equal · no placeholder leak — BEFORE it writes, so "verbatim" is provable,
  not trusted. [appendix-templates-xml — folded foundation-version 15]
- (TDD) **A deterministic preservation gate is NECESSARY-not-SUFFICIENT — pair it with a human-led
  conservative verify.** The gate proves anchors/tokens survived, but it is blind to an inversion AROUND
  surviving anchors (an added "unless"/negation/scope-narrowing that keeps every anchor word) and
  near-SILENT on files carrying no frozen unit — a GREEN there means "nothing was checked", not "meaning
  preserved". The human diff-read at the conservative gate owns that ceded class, and it works: of 4
  positivizations all-gates-green, the human reverted exactly the one whose obligation moved (CR-3).
  [rewrite-core + semantic-inventory + rewrite-guides — folded foundation-version 16]
- (ADD) **Empty-diff-as-evidence: a gate-blind protected class is verified by byte-identity, never by
  gates.** Ship protected safety lines byte-unchanged and SHOW the empty diff at the gate as the proof
  (`git diff <freeze>..HEAD` over the protected files); pin the exact strings with green-guards so the
  byte-identity survives future tasks. [rewrite-guides — folded foundation-version 16]
- (TDD) **On a guard-dense surface the per-commit battery must cover every edited line's pinned
  needles.** Boundary-scoped guard lists miss out-of-boundary pins — grep the tooling tests for the
  literal phrases of EVERY line you edit, or run the whole suite per commit (test_no_ceremony pinned a
  phrase a positivize pass moved; caught only at task-close → CR-2). [rewrite-guides — folded foundation-version 16]
- (TDD) **F3 keep-term presence guards a TOTAL loss, never a PARTIAL rename.** Short substring-prone
  keep terms (`ADD` · `PASS` · `Role:`) appear so widely a real global rename could leave the substring
  present and F3 green — don't oversell it; rename-safety for those terms belongs to semantic-inventory's
  per-file unit diff + human review. [wording-rubric — folded foundation-version 16]
- (SDD) **A numeric figure in a contract ("trim ~290 words") is an ESTIMATE, not an obligation.**
  Express the target as the behavior ("remove duplicative content"), not a hard count — the safe trim
  was 180 W; stopping short to keep load-bearing prose was correct, and the close records the criterion
  met-WITH-deviation rather than silently satisfied. [rewrite-core + clarity-greenstate — folded foundation-version 16]
  On a contract SHAPE line the figure reads as a BOUND even when the verbatim-quoted text is the
  authority — mark shape-line figures ≈ or omit them where the quote governs (the 4-vs-3 wrap was
  the gate's only deviation). [question-summary-layer — folded foundation-version 17]
  Test-side twin: never PIN a speculative number before counting the baseline — pin the contracted
  semantics ("shrank") or count first. [xml-prompt-structure — folded foundation-version 18]
- (SDD) **Positivization has a boundary: when the negative IS the obligation, keep it.** "Never clobber"
  prohibits destruction; "keep unchanged" prohibits modification — the reword moved the rule, not the
  framing. Guide prose should mirror engine semantics verbatim (add.py's own comment carried the
  original wording). [rewrite-guides — folded foundation-version 16]
- (ADD) **Build ORDER derives from a frozen contract's BINDING PROPERTIES, not its prose staging
  order.** §3's narrative listed restructure→CR-1, but the binding invariants (CR isolated AND gates
  green per commit) uniquely forced CR-1 first — derive the order from the invariants before the first
  commit. [rewrite-core — folded foundation-version 16]
- (ADD) **A staged-by-risk plan can have a LEGITIMATE no-op stage — record it as a finding, never skip
  silently.** 7 of 10 files were already rubric-clean, so a planned commit was a true no-op; the record
  is what distinguishes "verified nothing to do" from "forgot". [rewrite-core — folded foundation-version 16]
- (ADD) **A contract carrying a code table needs a freeze-time self-consistency lint over ITS OWN
  table.** §3 mapped one condition to TWO reject codes and the collision survived the one-approval
  freeze, caught only at build — cheap to check whenever a contract carries a code table.
  [wording-rubric — folded foundation-version 16]
- (ADD) **A milestone close needs an exit-criteria ROLL-UP with deviations surfaced.** Roll each
  criterion up to the task that delivered it and rule on every met-WITH-deviation at the close seam —
  a deviation that lives only in a delta gets folded, not ruled on (the ~290→180 trim).
  [clarity-greenstate — folded foundation-version 16]
- (ADD) **A behavioral spot-check is steering-evidence, never preservation-proof.** Blind cold agents
  meeting the hard-stops proves the CURRENT prose steers; preservation vs the OLD prose needs a
  baseline — that proof lives in the review leg (the human diff-reads). Keep the labels straight at the
  close. [clarity-greenstate — folded foundation-version 16]
- (SDD) **A contract adding a CLI verb must pre-declare the INSTRUMENT-REACTION class.** Self-maintaining
  instruments (the min-pillar LIFECYCLE census, the ubiquitous-language prose ban) react to ANY new
  subcommand — a "sole sanctioned test edit" clause under-enumerates exactly the way mirror clauses once
  did; name the class ("plus the self-maintaining instruments' own protocol edits"), not a closed file
  list. [archive-compaction — folded foundation-version 18]
- (SDD) **A both-forms term ban must name the FULLY-HYPHENATED compound too.** `one[- ]approval front`
  is blind to "one-approval-front" — a fence clause banning hyphen+space forms misses the all-hyphen
  form; the raw-grep recipe (substring, no boundaries) is the closing sweep.
  [ubiquitous-language — folded foundation-version 18]
  Discipline reaches prose VERBS, not only nouns: "fold" used as a PROMPT instruction verb collided with the
  method's own fold ritual — same-concept-same-name applies to actions too, so a worker PROMPT must avoid a
  reserved method verb for an unrelated step. [wave-ledger — folded foundation-version 19]
- (TDD) **Run the FULL suite once during the TESTS phase, not only the new file.** Instrument reactions
  (census, prose bans) are discoverable pre-freeze — found there they enter the contract; found
  post-build they become gate residue. [archive-compaction — folded foundation-version 18]
- (TDD) **Pin §4 needles as single-line fragments of the frozen text (or whitespace-normalize the
  assert) at WRITE time.** A needle frozen from a wrapped §3 blockquote collides with the landed
  re-flow. [intake-interview — folded foundation-version 18]
- (TDD) **Duplicate tripwire pins consolidate to ONE shared constant.** Five ENGINE_MD5 copies make
  every intentional engine edit a 5-file re-stamp; a single shared pin keeps the tripwire at 1/5 the
  ceded surface (the actual test refactor is its own future task, not part of the fold).
  [ubiquitous-language — folded foundation-version 18]
  SHIPPED v19: engine_pin.py holds the one literal, five suites import it (`from engine_pin import
  ENGINE_MD5`) — the "future task" named at v18 is done; a legitimate engine change now re-aims ONE line, and
  a sweep over EVERY tooling *.py (not just test files) keeps a second pin from hiding in a helper.
  [shared-engine-pin — folded foundation-version 19]
- (ADD) **Archive is a TWO-STEP lifecycle: `archive-milestone` (state) → `compact` (files).** Close a
  milestone consolidation-first, then light-archive, then compact; recovery is a reverse move, state
  needs no edit. Naming compact in the close nudge / fold.md is deferred — a method-surface edit is its
  own task. [archive-compaction — folded foundation-version 18]
- (ADD) **Fold routing splits SDD by content: "what we build" → §Spec · "how we author contracts" →
  CONVENTIONS (beside TDD/ADD).** Real-but-unwritten since foundation-v17 — applied again this fold;
  naming the split in fold.md is deferred (method-surface edit).
  [intake-interview — folded foundation-version 18]
- (ADD) **A prose-rewrite contract enumerates the MACHINE-TOKEN REGISTRY up front.** The machine/prose
  boundary was discovered five separate times mid-build (### heading · ⚠ glyph · seam-audit job ·
  folded status · owner enum), each costing an execution call — pre-draw the line once (or have add.py
  emit the registry). [ubiquitous-language — folded foundation-version 18]
- (TDD) **A prose-slicing guard must be fence-aware.** A words-exist guard that slices a section at `\n## `
  truncates at a `## ` line inside a fenced example — silently scanning a prefix while claiming the whole;
  route slicing through ONE fence-aware slicer (`md_section.section`, whose terminator scan skips ``` fences)
  so an embedded template may use real `##` headings. This RETIRES the prior workaround (### headings forced
  into the WAVE.md template). [fence-aware-section — folded foundation-version 19]
- (TDD) **Contract the expected-harmless and let the suite arbitrate — don't pre-shim.** A ⚠ "probably
  harmless" assumption (heading-inclusion across four importers) was resolved GREEN with zero compensating
  strips; a pre-emptive compatibility shim would have shipped untested code for a non-problem. Flag the
  assumption, contract the simple shape, and let the red→green suite confirm or refute it.
  [fence-aware-section — folded foundation-version 19]
- (ADD) **Offer "fix a flag first" at the bundle freeze.** The contract-freeze presentation includes a
  pre-freeze change-request path; a human hardening BEFORE the freeze is strictly-strengthening at near-zero
  cost (the sweep widened to every tooling *.py + cwd-independence subprocess-proven, both landed before the
  freeze). Distinct from the in-build strengthening amendment (disclosed at the gate, :audit-ci) — this one
  reshapes the contract while it is still open. [shared-engine-pin — folded foundation-version 19]
- (ADD) **A wave worker commits its own SUMMARY.md/deltas.md with its code.** Uncommitted worktree files
  survive only by harness courtesy (they had to be hand-copied before `git worktree remove`); the worker
  `<return>` contract must say "commit SUMMARY.md + deltas.md in the worktree, not just write them."
  [shared-engine-pin — folded foundation-version 19; enacted by the wave-protocol-runtime task]
- (SDD) **Import a sibling test module by reference, not by name, when the bare name would shadow a local.**
  `import md_section` over `from md_section import section` — name-collision awareness extends to import style
  (test_audit_ci / test_intake_interview carry a local `section`). [fence-aware-section — folded foundation-version 19]
- (ADD) **The instrument-reaction guard-class set depends on the ARTIFACT you ship.** A CLI verb trips three —
  the subcommand census (`test_min_pillar` LIFECYCLE), the `engine_pin` re-aim + 3-copy mirror, and the
  ubiquitous-language prose-ban on add.py literals. A NEW skill/doc FILE additionally trips two more — bundle/tree
  parity (the file-SET + byte-identity across the 3 skill trees) and the wording-lint surface-COUNT contract
  (shipping `loop.md` turned test_bundle_parity / test_tree_parity / test_wording_lint::surface red until each was
  updated). Pre-declare BY type: CLI verb → census + engine_pin + prose-ban; new skill/doc file → + bundle/tree
  parity + surface-count. Supersedes the "all three guard classes" note as artifact-keyed. [dynamic-task-loop — folded foundation-version 20] **v21 refinement:** a new `add-method/docs/*.md` ALSO trips the EXTENDED
  ubiquitous-language surface — `extended_surface()` globs every docs file + skill + templates + diagrams +
  README + GETTING-STARTED, not only the wording-lint surface-count; predict the EXTENDED surface for a new
  doc, not just the lint count. [references-appendix — folded foundation-version 21]
- (ADD) **A precondition on a lifecycle-CLOSING verb ripples to EVERY test that drives that lifecycle to close.**
  v20's goal-gate on `milestone-done` broke ~12 closer/decide-next tests at once — the new-milestone template ships
  an unchecked exit-criteria box, so total>0 by default; the same default that makes the gate real makes the
  reaction universal. Cost is one ADDITIVE fixture file-write per reactor (git numstat: 0 deletions across the 9
  fixtures, 0 assertions weakened) — budget a file-write each, not an argv append. [dynamic-task-loop — folded foundation-version 20]
- (TDD) **A cross-surface "stated identically" drift sentinel normalizes whitespace, not bytes.** "Stated
  identically" means same WORDING; each surface (guide · book · run.md) wraps at its own column, so a byte-equality
  sentinel false-fails on a line-wrap while a `_norm`'d one still fails on genuinely different words. [verify-deepen — folded foundation-version 20]
- (ADD) **The §6 Deep-checks block (WIRING · DEAD-CODE · SEMANTIC · SECURITY) is standard AND has teeth.** It now
  travels onto every verify (the template carries it); on verify-deepen's OWN task its WIRING path caught a real
  defect — §4 declared an empty `./tests/` so the test-count reported 0 while the real 10-test suite lived in
  `tooling/` (count 0→10, fixed pre-gate). A plausible-looking §4 can silently count zero tests. [reopen-transition+verify-deepen — folded foundation-version 20]
- (TDD) **A passing structural/resolution test over a grounding or prose deliverable is necessary, never
  sufficient — the human SEMANTIC check must carry what the resolver is blind to.** A resolver proves cites
  RESOLVE / sections EXIST / tokens are banned; it cannot see (a) **APTNESS** — whether the source grounds the
  claim: for any claim MORE specific than the appendix annotation, verify against the PRIMARY SOURCE, because
  the annotation fixed existence+title+author, not characterization depth; (b) internal **CONSISTENCY** — a
  counting pass ("three currents" over a four-currents heading slipped 642-green); (c) load-bearing **FIGURES**
  — spot-check each citable number against its source. Declare the §6 SEMANTIC blind-spots explicitly so green
  never reads as done. v21 hit this THREE times (form-test missed link-existence · resolution-test missed
  consistency · resolution-test missed aptness: [Yuan et al. 2024]'s "drifts" overstatement passed 649-green,
  caught only by WebFetch of arxiv 2401.10020 showing self-rewarding *improves*).
  [references-appendix + foundations-chapter + inline-citations — folded foundation-version 21]
- (TDD) **A cite-resolver that matches one [Author Year] per bracket reads the appendix's own `;`-joined form
  `[A; B]` as a single dangling key.** Split the bracket body on `; ` and resolve each key. A FROZEN test that
  predates the multi-cite form keeps the single-key limitation — copy its regexes into a NEW `;`-aware test,
  never refactor the frozen one (copy, don't couple). v21: 2 red→green fixes forced single-key brackets in
  foundations; inline-citations shipped the `;`-aware resolver + a real `[Schmidhuber 2003; Zelikman et al. 2023]`
  exercising the split. [foundations-chapter + inline-citations — folded foundation-version 21]
- (TDD) **A count-vs-set assertion guards an invariant only against the mutation it can see — name the blind
  spot, or a "latent guard" reads as a false all-clear.** "Exactly one entry per cite-key" has no dedicated
  uniqueness test; `test_appendix_g_frozen` asserts `len(set(keys)) == 27`, so an entry EDITED to collide
  collapses the set to 26 → red. But a 28th entry ADDED with a colliding key gives 28 lines / 27 unique → green:
  the entry count is only floored (`assertGreaterEqual(len(entries), 18)`), never pinned at 27. A dedicated
  uniqueness (or exact-count) assert therefore closes a REAL gap for the add-case — not optional hardening.
  The headline lesson a 4th time: `len(set)==27` is necessary, never sufficient, blind to the mutation no test
  names. [references-appendix — folded foundation-version 21; sharpened by advisor re-check]
- (ADD) **The book has FOUR mirror trees — root · canonical · bundle · dogfood — and an APPENDIX's root copy is
  guarded by NO test.** Only CHAPTERS are cross-tree guarded (test_inline_citations + test_flow_diagram span all
  four incl. the repo-root published copy); an appendix's root copy drifts silently. A docs task syncs all four
  by hand and md5-confirms the appendix root leg — bundle-green is false comfort. Extends "Dogfood parity" /
  the mirror-clause-enumerates-ALL-copies family. [arc-book-align — folded foundation-version 22] **VALIDATED at
  the ground fold:** a byte-sync test added for a NEW term (`test_book_glossary_synced_x4`) caught the
  PRE-EXISTING repo-root appendix-c drift this bullet predicted — the root mirror had silently fallen a whole term
  behind canonical; a "synced ×N" guard pays for itself beyond the change that adds it, and the appendix-root leg
  is now guarded. [ground-prose-align — folded foundation-version 25]
- (ADD) **Dogfooding a rule at its own gate is its first live proof — and catches what no test asserts.** Rendering
  the decision arc · running the reconcile rule · presenting a presentation-contract AT the very gate that ships
  it surfaced gaps every green suite missed: the 5-of-7 gate-coverage gap, the verbatim reconcile-rule
  duplication, the digest-vs-prose mismatch. Practice the rule on its own gate the session it lands — reinforces
  "a method-defining task dogfoods its own rule". Reinforced by verify-integrity: the first NORMAL task through a
  freshly-shipped guard is its cheapest end-to-end test (task 2 crossed tests→build under task 1's live tripwire,
  re-checked clean at the gate), and the method audits its OWN builds — dogfooding the earned-green rubric on task 3
  caught a real nit (a trivially-true assert) before the gate. [report-arc + arc-gate-wiring + arc-book-align — folded foundation-version 22 · reinforced verify-integrity fv27]
- (ADD) **The change-request is the method working, not a failure.** A frozen-contract gap caught at verify is
  fixed via reopen→contract→re-freeze (the live-run form is `add.py phase contract`; `reopen` is for DONE tasks),
  never a silent build edit; the §3 carries both freeze stamps. Reinforces "a frozen guard is fixed in the BUILD
  output / route it as a human-ratified change-request". [arc-book-align v1→v2 — folded foundation-version 22]
- (ADD) **A single-source rule is POINTED-to, never restated — and no presence test catches a verbatim restatement.**
  The reconcile rule folded into report-template.md was duplicated verbatim into 6-verify.md; only review caught it.
  A "traceable everywhere, defined once" design needs a no-restate lint or parity check, not a presence assertion
  (words-exist≠method-works, applied to single-sourcing). [arc-gate-wiring — folded foundation-version 22]
- (ADD) **To prove "X can NEVER reach state S", enumerate every WRITER of S — not the string-callers of the obvious
  command.** Grep every assignment to the guarded state field; a transition guard's completeness IS the full set of
  mutators (here: exactly two writers — `cmd_init` declared-at-init boundary + `cmd_stage` guard). [graduate-guide — folded foundation-version 22]
- (ADD) **A multi-source report declares ONE traversal basis per tier (filesystem OR state), or the sets silently
  diverge under archival.** `open_deltas` globs `tasks/*` while residue/coverage iterate `state["tasks"]`; they agree
  only while every archived milestone is compacted out of `tasks/`. Same archive seam as the done-tally blind spot
  (§Domain). Pin each tier's source-of-truth in the contract or document the divergence. [graduation-analytics — folded foundation-version 22]
- (ADD) **A gate report's ⚠ FLAGS must reconcile with `add.py report --decide`'s open-item count before stamping —
  fix the data (the TASK.md markers), never the sentence.** Prose calling an item "resolved" while the digest still
  counts it open is the un-transparent gate the decision arc exists to kill. Now SHIPPED as report-template.md's
  reconcile rule. [report-arc — folded foundation-version 22]
- (ADD) **A cross-surface term can carry two axes — disambiguate before unifying, keep both senses + one bridging
  clause.** "scope level" (decision-granularity vs orchestration-loop) and "report" (the chat report at a decision
  point vs the verify gate's three Test/Quality/Risk reports) each carry two senses; never merge the lists.
  [stage-book-align + arc-book-align "report" polysemy — folded foundation-version 22] A lived working LABEL
  drifts from its canonical glossary TERM the same way — §3's "Least-sure flag surfaced at freeze" vs the
  glossary's "lowest-confidence flag" shipped bridged-not-migrated; introduce a working label only with a
  bridge ("formerly …") or migrate it in the same breath, never a silent rename. [unflagged-freeze — folded foundation-version 23]
- (ADD) **Reinterpreting or closing a contract sweeps the LOADED foundation prose for the stale shape, not just the
  test guard.** A green suite cannot catch prose drift (tests don't exercise docs); add "sweep loaded-layer prose
  for the old shape" to the change-request checklist (close-gap-before-gate). Reinforces stale-guard-sweep. [stage-goal-criteria — folded foundation-version 22]
- (TDD) **A presence / marker / structural test is necessary-not-sufficient — it pins vocabulary or existence, never
  that the CLAIM holds or the behavior works.** A presence fence ("the term exists") is not a coverage fence ("the
  claim 'every X' is true" — the chapter named 5 of 7 wired gates, 690-green); a prose-marker test pins steps NAMED,
  not orchestration DRIVEN; a gather-not-judge invariant is asserted STRUCTURALLY (no verdict field in the schema),
  never via a word denylist that lags the contract. The human SEMANTIC read + the engine seam carry what the test is
  blind to — recurring face of "words-exist≠method-works". A presence test also proves a phrase EXISTS on ONE surface,
  never that two surfaces AGREE on its qualifier (a template read "for high-risk" while the guide read "recommended
  under auto"; every anchor test passed) — cross-surface qualifier agreement needs a shared render or an
  adversarial/human read. [arc-book-align + graduate-guide + graduation-analytics — folded foundation-version 22 · reinforced verify-integrity fv27]
- (TDD) **A new guard that invalidates an existing test's PREMISE is adapted by SPLITTING, never loosening — and
  disclosed at the gate.** Move the old guarantee to where it still holds (the bare flip → a non-guarded stage), add
  the new guarantee (refuse@0 / succeed@≥1 / --force), surface the touched files as a strictly-strengthening
  amendment for the human to judge. Reinforces "a strictly-strengthening in-build amendment is legal but never silent". [graduate-guide — folded foundation-version 22]
- (SDD) **How-we-author contracts — five v22 sharpenings.** (1) A guarded transition must NAME its at-creation door
  (`init --stage`) as a `declared_at_init` boundary, or the "NEVER reaches S" silently leaks through a second door.
  (2) A data-shape-bounded reject clause NAMES its trigger (the first archived RISK-ACCEPTED/HARD-STOP) so it
  re-opens as a change-request the day the shape stops being empty, instead of under-reporting. (3) An assumption
  resolved-by-DESIGN yet milestone-spanning gets a *resolved-with-forward-watch* state (a §7 monitor), not a bare
  `[x]`/`[ ]`/⚠. (4) A MILESTONE-declared task slug is checked against existing `tasks/` (and archived) dirs before
  create — a collision would overwrite a done task. (5) Contract-freeze greps for the PRIOR contract that froze an
  extended `--json`/state seam and states additive-vs-closed explicitly. [graduate-guide + graduation-analytics + report-arc + stage-book-align + stage-goal-criteria — folded foundation-version 22]
- (ADD) **A new guard gains teeth without retro-redding its predecessors via a VERIFIED-MARKER.** Stamp the
  marker on the guarded crossing (the freeze/gate the guard newly governs) and enforce only on MARKED records;
  pre-marker records pre-date the rule and stay green — no fabricated retro-pass, no silent grandfather.
  Distinct from "adjudicate epoch debt at the human gate" (which retro-ratifies old records *by choice*; this
  scopes enforcement forward *by construction*). [unflagged-freeze — folded foundation-version 23]
- (TDD/ADD) **A prose-accord guard pins EVERY surface the contract names, and a word-ban is blind to a stale
  multi-VALUED enumeration** — two faces of necessary-not-sufficient on a "prose ≡ enforcement" deliverable.
  (a) DocsAccordTest pinned 1 of the 4 surfaces frozen §4 named ("GLOSSARY + the autonomy docs ×3"), so 2
  shipped stale-green — caught by human review at the gate, not CI; enumerate every named surface or the accord
  is only as wide as the pin (same shape as the census whole-and-closed rule). (b) A word-ban catches a banned
  WORD, never a stale ENUMERATION — once a 3rd rung landed, "auto | conservative" descriptions read green to the
  slang fence; widen level-set prose by a structural/test pin or a manual sweep, never the vocab ban.
  [explicit-autonomy-dial — folded foundation-version 23]
- (ADD) **Anchor a declaration-token reader to a declaration POSITION — line-start or a `·`-separator,
  never a bare substring.** A freeform H1 title or quoted prose containing `token: value` must never be
  read as a declaration; the symmetric hazard is worse — a title faking a *lowered* rung can DEFEAT a
  guard that trusts the first match. Anchor every header-token reader (autonomy AND risk) to its
  declaration column. [init-auto-default — fixed @ 55d64d9 — folded foundation-version 24]
- (TDD/ADD) **A live-only / never-retro guard must key on the milestone's terminal STATUS, not just the
  active-pointer + dict-membership.** A done-but-not-yet-archived milestone stays the `active_milestone`
  pointer (and in the dict) until `archive` clears it, so pointer-membership alone briefly flags a CLOSED
  milestone — the build keyed the `goal_not_auto_ready` WARN on the pointer and fired on a `status=done`
  milestone; the verify adversarial pass caught the Must #4 violation and closed it test-first
  (`status != "done"` guard + `test_done_active_milestone_not_flagged`, red→green). Reinforces
  verified-marker-scopes-forward (enforce live, never retro-red). [goal-auto-ready-gate — folded foundation-version 24]
- (ADD) **A lint forces a SLOT, never honesty — the irreducible floor.** `(verify: <citation>)` on every
  exit criterion raises the goal-clarity floor (a citation MUST exist, an empty `(verify:)` does not count)
  but cannot prove the citation is real — `(verify: it works)` passes the lint (citation-theater). The
  engine raises the floor; the human still owns whether the citation is honest (autonomy is EARNED, not
  mechanically proven). Recurring face of necessary-not-sufficient; RESOLVING/running the cited verifier
  (a test that exists, a command that passes) is the recorded forward upgrade. [goal-auto-ready-gate — folded foundation-version 24]
- (ADD) **Ground the contract in the real code before §3 — the ground phase's founding proof.** Reading the
  actual symbols a task touches (`PHASES` + every keyed function) BEFORE drafting the frozen contract pre-caught
  four shipping defects the spec alone would have missed — a `decide_data` else→`gate` seam mislabel, a
  `render_decide` seam_label `KeyError`, the `PHASES[:7]` structural-slice shifts (the index-hazard bullet), and
  header-parsed-vs-positional numbering — each surfaced during §0 grounding / the advisor pass, before build.
  Grounding INFORMS a human-approved contract, it never authors it; the `## 0 · GROUND` map records the anchors
  §3 cites. A phase-0 PREAMBLE earns prose in the FLOW chapter, not a dedicated step-chapter — preserving the
  "seven steps" brand and the lean-over-GSD rule (the engine pointer was already correct).
  [ground-phase-engine + ground-prose-align — folded foundation-version 25]
- (TDD/ADD) **Mutating an ordered constant is an absolute-index hazard — grep the absolute forms first.**
  Inserting at index 0 of an ordered tuple (`PHASES`) silently shifts every ABSOLUTE index/slice (`PHASES[:7]`,
  `names[n-1]`, `i = p["n"]-1`) while RELATIVE logic (`PHASES.index(...)`) stays correct. Before mutating an
  ordered constant, grep the absolute forms and prefer relative derivations. [ground-phase-engine — folded foundation-version 25]
- (ADD) **An additive measure-not-block surface stays byte-invisible to existing tests and copies the proven
  shape.** Two moves land a new engine surface for free: (a) SUPPRESS the no-op/legacy case so CURRENT output is
  byte-unchanged — every existing task's status is identical, zero existing output-tests need conforming, the
  dogfood `check` count is unmoved; (b) MIRROR the established measure-not-block shape verbatim — a human-readable
  `status` line + a never-red WARN riding the existing `warnings` array, never a new `--json` key (sidesteps the
  `json_surface_unsanctioned_key` landmine and the design churn). Reinforces "a harmless additive `--json` key
  still stays inside the frozen contract." [ground-bundle-wiring — folded foundation-version 25] **VALIDATED at the
  ground-context fold:** the TEMPLATE twin held — an additive `## 0 · GROUND` template LINE inserted BETWEEN existing
  fields was byte-invisible to the structure/token-pinning template guards (the suite grew with zero scaffold/render
  test broken), because template tests pin tokens + structure, not exact line-sets. [ground-context-sources — folded foundation-version 26]
- (TDD) **A prose guard derived from the engine constant self-maintains — a ladder change then satisfies it
  minimally.** Derive the test's expected set from the engine constant (`FLOW_PHASES = [p for p in add.PHASES if
  p != "done"]`) so a ladder change AUTO-propagates the prose requirement — adding `ground` to `PHASES` made
  `test_flow_diagram` REQUIRE ground in the mermaid + CHECKLIST with no test edit. The ladder change must then
  make the MINIMAL diagram/CHECKLIST edit to keep the suite green, deferring the narrative to the prose task; and
  guarding a checklist by an exact item-COUNT + a line BUDGET (`==6→7` items, `≤16` lines) makes "gains one line"
  a precise, self-checking change. The book diagram + CHECKLIST are a ladder-shape reaction class — extends the
  instrument-reaction guard family. [ground-phase-engine + ground-bundle-wiring + ground-prose-align — folded foundation-version 25]
- (ADD) **A ladder change grandfathers pre-existing tasks — retrofit to dogfood, never claim the lived run.** A
  phase inserted into the ladder grandfathers every existing task at its current phase (all three ground-phase
  tasks were created at `specify`, before `ground` existed). Retrofit the new §0 section onto each so the surface
  is dogfooded HONESTLY (it records the grounding that informed §3) WITHOUT claiming the task flowed THROUGH the
  new phase — which narrows the residual from "zero lived dogfood" to "zero lived runs STARTING at ground," the
  accepted ceiling recorded for the next milestone, never papered over. Reinforces "a method-defining task
  dogfoods its own rule." [ground-phase-engine + ground-bundle-wiring + ground-prose-align — folded foundation-version 25]
  **CEILING CLOSED at ground-context:** the FIRST lived ground run (a task created AT `ground`, not retrofitted)
  reached `grounded ✓` live, closing the "zero lived runs STARTING at ground" residual recorded here as the accepted
  next-milestone ceiling. [ground-context-sources — folded foundation-version 26]
- (ADD) **Ground has two axes — completeness (WHAT) and economics (HOW).** The §0 gather names not only WHAT to
  gather (the working-folder categories: docs/textbase · TODOs · config/manifests · data/fixtures, beyond code) but
  HOW to gather it — sweep the BROAD pass cheaply (a small-model subagent / fast index / skim, returning a compact
  map), then DEEPEN task-specifically on what THIS task needs. Naming the economics closes both failure modes at
  once: skipping context, and indexing the whole repo. A complete §0 is the task-relevant delta gathered
  cheaply-then-deeply, never a repo-wide scan. [ground-context-sources + ground-gather-hint — folded foundation-version 26]
- (ADD) **A capability can be ADDED as guide-prose recommendation while the engine stays tool-agnostic — the pin
  holds across the addition.** The gather-method hint RECOMMENDS a subagent; `add.py` spawns nothing (the
  orchestrating agent chooses the tool), so the engine stayed byte-identical to `engine_pin` through BOTH
  ground-context tasks. When a new method capability is advice, not mechanism, it lands entirely in the ×3 guide
  prose — no engine action, no new measure, no new gate — and the unchanged engine pin is the proof the line was not
  crossed. [ground-gather-hint — folded foundation-version 26]
- (ADD) **Dogfooding the shipped technique in-flight validates it.** The build of the sweep-cheap-then-deepen hint
  USED that very split — a haiku subagent ran the broad working-folder sweep (returning the ×3/×3 sync md5s + the
  guard list) while the main context deepened on the precise guard assertions, pre-mapping the `Anchors the contract
  cites:` measure line before the broaden touched it. The method proved itself by being the method that built it;
  reinforces "a method-defining task dogfoods its own rule." [ground-context-sources + ground-gather-hint — folded foundation-version 26]
- (TDD) **A prose feature is RED-greenable by token-presence guards; triage the RED split.** A prose/template task's
  red suite splits into two halves: "the feature is missing" (the NEW behavior — must be red before build) and "the
  invariants still hold" (must stay green throughout); triaging the split confirms the red is the new behavior, not
  a broken invariant. Pin the behavior by token presence — assert `"subagent"`+(`"index"`|`"skim"`), `"deepen"`,
  `"working folder"` — so the phrasing stays free and only the behavior is locked. A prose-economics hint is as
  pinnable as a structural one. [ground-context-sources + ground-gather-hint — folded foundation-version 26]
- (ADD) **Build-integrity needs a mechanical floor AND a judgment ceiling — and a confirmed cheat is HARD-STOP-class.**
  The tamper-tripwire catches the cheats it can SEE (a test or the frozen §3 edited after the red run, by md5); the
  earned-green refute-read the ones it cannot (src overfit to fixtures · vacuous asserts · stubbed-away logic) — neither
  layer alone closes the gamed-green gap. The mechanical floor lives in agent-writable state.json, so it is
  necessary-not-sufficient: a co-witness flag raises the forgery cost (forge two, not one) but a determined agent
  patching both still slips — the adversarial read + the human gate stay the real backstop. A confirmed cheat is never
  auto-passed nor RISK-ACCEPTED-waived, exactly like security. [verify-integrity: earned-green-rubric + tamper-tripwire + heal-then-escalate — folded foundation-version 27]
- (ADD) **A mechanical-HARD-STOP guard = snapshot at a phase seam → re-check at the gate before any completing outcome
  → fail-closed; and a self-heal cap is real only if it cannot be cleared without a recorded human action.**
  Generalizable to any "freeze X at phase A, enforce at phase B" (the tamper-tripwire snapshots md5(test paths + §3) at
  tests→build, re-checks at verify). The bounded loop returns a confirmed cheat to BUILD for an honest redo and counts
  attempts MONOTONICALLY — never auto-resetting, because the phase verb is unguarded (a tests→build re-cross would
  otherwise zero the counter with zero human action); after the cap it forces the HARD-STOP. [verify-integrity: tamper-tripwire + heal-then-escalate — folded foundation-version 27] Validated under real fire: engine-merge-base-enforcement ran the loop to its cap TWICE — 3 honest src-only redos, then heal_exhausted HARD-STOP escalations the human routed as change-requests; refute→heal→re-refute converged to two consecutive EARNED passes. [flip-cite — folded foundation-version 28]
- (TDD) **An engine change that legitimately invalidates an EXISTING assertion makes the test edit an EVOLUTION, not a
  weakening — iff three hold: the real invariant stays guarded, coverage holds-or-rises, and the reason is documented.**
  The reusable discriminator behind "split, never loosen": when the landed behavior makes an old assertion false (a
  first tamper now returns-to-build, not dies), move the assertion to the new truth while keeping the real invariant
  strict (`gate=="none"`) and letting coverage rise (1→3 cheat tokens), then disclose every touched file at the gate.
  The independent refute-read is the backstop that judges evolution-vs-weakening when no test can. [verify-integrity: heal-then-escalate — folded foundation-version 27]
- (ADD) **A security-line classification can EMERGE during build, not only at the §3 freeze — surface it for human
  ratification AT the verify gate, never self-grant.** When a build discovers a property that deserves HARD-STOP weight
  (md5-as-tamper-evidence), the reasoning holding is not licence to self-check the box: present it as an explicit ask.
  [verify-integrity: tamper-tripwire — folded foundation-version 27]
- (SDD) **Two how-we-author sharpenings.** (1) A staged method needs a scope guard that fails if a LATER stage's
  machinery leaks BACKWARD into an earlier stage's prose — assert the later tokens ABSENT from the earlier guide so each
  stage describes without pre-empting the next's enforcement. (2) When a new feature needs the exact file set an existing
  counter resolves, extract a path-returning helper and delegate the counter to it (one resolution source), never
  re-glob — the snapshot and the engine then agree by construction. [verify-integrity: earned-green-rubric + tamper-tripwire — folded foundation-version 27]
- (SDD) **Parsing a hand-written artifact: exactly-one-match + terminator-explicit — never substring-first-wins, never
  regex-`\b`.** Two clauses, one discipline. A label lookup must match EXACTLY ONE candidate (>1 → refuse as malformed,
  naming the collision) — first-wins on hand-written input is fail-open by construction: a decoy `fork-base-prev` label
  stole the echo column. And a keyword token must name its terminators (whitespace/separator/end-of-line) or use exact
  token equality — `\b` fires at `|` and `-`, so the unfilled template placeholder `live|merging` parsed as its valid
  prefix and greened an unfilled ledger on both surfaces. [engine-merge-base-enforcement: refute passes 4–5 — folded foundation-version 28]
- (SDD) **When a spec's enforcement crosses a seam the engine cannot observe, NAME the enforcement-deferral explicitly
  at the freeze.** Prose must never masquerade as enforcement: the frozen flag that declared the spawn-time fork-base
  check DEFERRED to a future engine task is what made the gap honest — and what engine-merge-base-enforcement closed.
  [wave-protocol-runtime — folded foundation-version 28]
- (TDD) **A refute-read's coverage gaps route as NEXT-LOOP deltas, never post-hoc test edits.** After the tests→build
  snapshot the suite is tamper-guarded; hardening it in place reads as tamper. The honest absorb-point is the next
  freeze (a change-request re-snapshot) — exactly how the 11 refute-discovered wave vectors became pinned fixtures.
  [engine-argv-portability — folded foundation-version 28]
- (TDD) **A red suite for a PARSER of hand-written artifacts must include grammar-DRIFT fixtures, not only
  template-conformant ones.** Ten conformant tests stayed green across six contract-violating false-greens that only
  adversarial probing surfaced — conformant fixtures test the happy grammar, not the fail-closed promise.
  [engine-merge-base-enforcement: refute passes 1–4 — folded foundation-version 28]
- (TDD) **Token-presence + ×N-mirror-parity is the honest test shape for a prose-discipline change with no executable
  engine hook.** Lock the WORDS and the MIRROR; let the adversarial refute-read confirm the words carry mechanism —
  red→green works on prose exactly like code when the assert is a vocabulary token. [wave-protocol-runtime — folded foundation-version 28]
- (ADD) **Grounding probes against MUTATING engine verbs run in a sandbox, never the live project.** A §0 `new-task`/
  `use` probe polluted live state.json and needed a git restore; read-only verbs may probe live, mutating verbs never.
  [engine-argv-portability — folded foundation-version 28]
- (ADD) **Close-gap-before-gate converges.** A disclosed non-finding observation routed as a MICRO change-request (one
  contract sentence · one red fixture · one-line fix · targeted re-refute) closes in a single short cycle and lets the
  gate record a clean PASS instead of a PASS-with-asterisk — disclosure plus a small honest loop beats waving residue
  through. [engine-merge-base-enforcement: pass-6 N12 → v4 — folded foundation-version 28]
- (ADD) **A folded runtime-exception must be MIRRORED onto every protocol surface it governs.** One surface carrying
  the rule while a sibling protocol file contradicts it re-opens the prose-only gap the fold closed (the cross-surface
  recursion v19 delta #7 named). [wave-protocol-runtime — folded foundation-version 28]
- (ADD) **Design-for-failure on a concurrency invariant: the check SHIFTS, never SKIPS, when its evidence cell is
  unsatisfiable.** Relocate the guarantee (pre-spawn rev-parse → worker step-0 echo + merge-time verify), never drop
  it — an unsatisfiable check that silently lifts un-guards the invariant it existed for. [wave-protocol-runtime — folded foundation-version 28]
- (SDD) **Contract completeness has three mechanical checks at freeze: (1) every Reject code is SATISFIABLE by the
  frozen signature — a reject needing a parameter the signature never receives ships dead; (2) every Reject code has
  a matching §4 test line — an asymmetry here shipped 2 untested codes past a green build; (3) structural/containment
  rules must be STATED, not implied — "a token is a leaf (no child tokens)" and "props is an object, children is an
  array" each existed only in the validator, never in the frozen §1, so a verify refute found both gaps after green.**
  Apply all three as a freeze-time self-lint over the Reject table before the human approves.
  [udd-catalog-content-schema + udd-check-lint + udd-token-schema — folded foundation-version 29]
- (SDD) **A contract that broadens an engine verb-set must (a) NAME the verb CLASS, not "every verb", and (b) map
  which frozen tests lock the old shape before freezing.** "Every mutating verb" swept setup/lifecycle verbs whose
  bespoke output must NOT converge; the collision with test_brownfield_scan surfaced only at a 909-test full-suite
  run, forcing a post-build change-request. Naming the class (workflow vs setup vs control) at the freeze makes the
  scope precise; mapping the frozen test surface makes the collision a freeze-blocker, not a build surprise.
  [next-footer-engine + gate-owner-marker — folded foundation-version 29]
- (TDD) **The verify-gate adversarial refute earns its keep even on an honest, green build: conformant fixtures test
  the happy grammar, not the fail-closed promise.** Three traversal/validator tasks confirmed this in one milestone:
  (a) a total-function (never-raises) probe + a wrong-JSON-type input must be in the red suite FROM GROUND — 13
  conformant scenarios all passed yet missed an AttributeError on non-object input; (b) a COMPOSING validator needs
  first-class "no-double-flag" boundary tests — the build green missed 3 double-flag shapes; (c) a recursive
  validator needs a "never-skip-a-subtree / no phantom children" probe — 10 behavior scenarios passed while a
  `$value` node with non-`$` children skipped its whole subtree. In each case the verify refute, not the build,
  found the gap. Author these adversarial fixtures at red-suite time, not as verify residue.
  [udd-catalog-content-schema + udd-check-lint + udd-token-schema — folded foundation-version 29]
- (TDD) **String-PRESENCE asserts under-enforce a structured-prose contract — add STRUCTURE asserts.**
  `assertIn(anchor)` misses ordering, table form, and OR-halves (a non-hex literal passed presence); a prose
  contract with layout/order obligations needs asserts that enforce those dimensions. Reinforces
  words-exist≠method-works applied to prose tests specifically. [udd-design-template — folded foundation-version 29]
- (ADD) **The engine-pin idiom has three mandatory parts: re-aim the slug annotation AND bump the md5 AND carry the
  PRIOR task's "re-aimed @ <slug>" marker.** (1) The self-test (`test_pin_annotation_names_this_task`) is part of
  the idiom, not optional — omitting it from the red suite means a stale annotation only surfaces at verify. (2) A
  same-task verify re-cross updates ENGINE_MD5 WITHOUT changing the `re-aimed @` slug — the slug names the TASK,
  the md5 names the build. (3) The prior task's annotation test asserts its marker survives; if the re-aim
  overwrites it, that sibling test goes red.
  [gate-owner-marker + udd-catalog-content-schema + next-footer-engine — folded foundation-version 29]
- (ADD) **A human-approved mid-build change-request trips the tamper tripwire — the honest re-arm is
  `phase tests → advance`, never a gate override.** The tripwire snapshots the red test paths + §3 at tests→build;
  any edit (even a legitimate, human-approved bundle change) re-fires it. The path: reopen → contract → tests →
  build → re-advance (re-snapshot). Worth one line in run.md so agents do not read `build_tampered` as a cheat
  signal. Distinct from strengthening a test at VERIFY (close-gap-before-gate), which ALSO trips build_tampered
  and follows the same honest path. [scope-decl-template + udd-design-template — folded foundation-version 29]
- (ADD) **The §5 scope declaration is FROZEN into `state.json`'s anchor at tests→build — editing §5 prose alone
  cannot clear a scope violation.** Only a full tests→build re-cross (reopen → contract → tests → advance)
  re-baselines the anchor. Sibling caveat: sibling-session commits landing on the shared branch mid-task can redden
  unrelated guards; the full-suite-before-gate rule catches and routes them rather than letting the gate record
  over them. [next-footer-engine + scope-decl-template — folded foundation-version 29]
- (ADD) **Every state-CREATING seam needs its state-REMOVING transition specified in the SAME contract — and a
  shared-cap cross-source escalation test, not a same-source one.** Declared→undeclared had no cleanup path
  until a verify refute disclosed it (v3 change-request). Proving a SHARED violation cap is distinct: seeding the
  counter from one source (tamper) then triggering a different source (scope) is the only assertion that
  distinguishes a shared cap from parallel independent caps.
  [scope-gate-enforce + scope-violation-heal — folded foundation-version 29]
- (SDD) **A new skill-engine doc silently trips two surface-inventory guards — register AND declare it
  before tests→build.** Adding `confidence.md` / `advisor.md` reddened `test_xml_convention.ENGINE_FILES`
  (registration) and the `test_wording_lint` surface COUNT at the same time; both must be named in §5 Scope
  before the tests→build cross, or the frozen anchor records an undeclared touch. Sharpens
  §5-scope-frozen-at-tests-build for the new-engine-doc case: the inventory guards, not just the prose,
  define the scope a method-surface task must declare. [advisor-strategy — folded foundation-version 30]
- (TDD) **A content guard that enumerates the FULL set it covers + asserts mutual distinctness defeats both
  the missing-item cheat and the boilerplate cheat.** `test_per_step_hooks` lists all 8 phase guides and
  asserts each Advisor·Confidence hook is present AND distinct from its siblings — a count/membership pair
  plus distinctness is the test-pattern for any "every X carries a non-boilerplate Y" doc requirement.
  [per-step-hooks — folded foundation-version 30]
- (ADD) **Two authoring rules for method-surface milestones: build in the build phase, and deliver per-step
  context as thin pointers.** (a) Authoring the implementation during SPECIFY makes the tests→build snapshot
  capture an already-built tree, so the scope-gate becomes a no-op — write code IN build so the gate
  meaningfully checks touched ⊆ declared. (b) Richer per-step AI context belongs in ONE shared doc
  (`advisor.md` / `confidence.md`) reached by a thin per-guide pointer, never inline prose — progressive
  disclosure kept the 8 guides minimal (applies single-source-point-not-restate to per-step hooks).
  [advisor-strategy + per-step-hooks — folded foundation-version 30]
