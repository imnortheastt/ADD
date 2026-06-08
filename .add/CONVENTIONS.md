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
  backstops drift. [cospecify-lift: test_cospecify_lift red→green + test_bundle_parity — folded foundation-version 7]
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
