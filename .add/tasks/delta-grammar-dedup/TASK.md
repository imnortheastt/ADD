# TASK: collapse duplicated _DELTA_RE to one canonical regex

slug: delta-grammar-dedup · created: 2026-06-04 · stage: mvp
phase: tests   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
autonomy: auto

> Behavior-preserving refactor. The delta grammar is compiled TWICE in add.py:
> `_delta_start` (local, in `_task_prose`) and the module-level `_DELTA_RE`. The
> module comment at the canonical one literally says "Reuse the same grammar as
> `_task_prose`'s `_delta_start`" — i.e. an acknowledged copy. Collapse to ONE source.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: ONE canonical compiled delta-grammar regex in add.py — the
`(DDD|SDD|UDD|TDD|ADD) · (open|folded|rejected)` shape — reused by every consumer
(`_task_prose`, `_collect_open_deltas`, `_lint_task_deltas`). The behavior of all
three delta surfaces (report, `deltas`, `check` lint) is unchanged.
Framings weighed: keep `_DELTA_RE` as the single source + delete `_delta_start` (chosen) ·
  factor a shared `_match_delta()` helper · leave the duplication (rejected — the milestone's debt)
Must:
  - Exactly ONE compiled regex literal in add.py encodes the enumerated delta grammar.
  - `_task_prose` reuses that canonical regex (the local `_delta_start` is gone).
  - The canonical regex still matches an INDENTED tag line (un-stripped), because
    `_task_prose` matches against un-stripped `lines[i]` — i.e. stays PERMISSIVE.
  - `deltas`, the report, and the lint produce byte-identical output to pre-refactor.
Reject:
  - n/a — internal refactor; no new external input. (The lint's existing rejects —
    `unknown_competency`, `unknown_status`, `no_evidence`, `malformed_delta` — are unchanged.)
After:
  - `grep -cE "\(DDD\|SDD\|UDD\|TDD\|ADD\)" add.py` == 1; all existing delta/lint/report tests green.
Assumptions — least-sure first:
  ⚠ The canonical regex MUST be the PERMISSIVE form (leading `\s*` before `-`), because
    `_task_prose` feeds it un-stripped lines (line 1227/1234) — least sure that every caller
    is fine with the permissive form; if wrong: an indented non-delta line could be mis-read.
    Mitigation: `_collect_open_deltas` + lint feed it ALREADY-stripped lines, so `\s*` matches
    zero there — verified by reading (add.py:1598-1599, 1670-1675); the parity test pins it.
  - [x] `_TAG_BROAD_RE` is a DIFFERENT abstraction (no enumeration) and is NOT part of this dedup
        — confirmed by reading the comment at add.py:1542-1544.
  - [x] exactly 2 copies exist today (`_delta_start` @1205, `_DELTA_RE` @1536) — confirmed by grep.

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: one canonical source after the collapse
  Given add.py
  When I count compiled regexes whose pattern enumerates (DDD|SDD|UDD|TDD|ADD)
  Then exactly one such regex literal exists
  And _task_prose references the module-level canonical (no local _delta_start)

Scenario: indented tag line still recognized by the report path (behavior preserved)
  Given a TASK.md whose §7 delta tag line is INDENTED ("    - [DDD · open] x (evidence: e)")
  When I call _task_prose on it
  Then the delta is extracted with competency DDD and status open
  And the text "x" is preserved (the permissive match still fires)

Scenario: both delta paths agree on the same grammar
  Given a set of lines: a valid stripped tag, a valid indented tag, a malformed "- [BOGUS]" line
  When the _task_prose path and the _collect_open_deltas path each parse them
  Then both recognize exactly the same valid deltas
  And neither accepts the malformed line as a delta
```

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
Module-level canonical (the ONLY enumerated delta regex):
  _DELTA_RE = re.compile(r"\s*-\s*\[\s*(DDD|SDD|UDD|TDD|ADD)\s*·\s*(open|folded|rejected)\s*\]\s*(.+)$")
    group(1)=competency  group(2)=status  group(3)=tail   (matches stripped AND indented via .match)
Consumers (all reuse _DELTA_RE; no second compiled copy):
  _task_prose            : was `_delta_start`; now _DELTA_RE        (un-stripped lines → needs permissive)
  _collect_open_deltas   : _DELTA_RE.match(stripped)                (unchanged)
  _lint_task_deltas      : _DELTA_RE.match(tag_line)                (unchanged; tag_line is stripped)
Out of scope: _TAG_BROAD_RE (broad detector, no enumeration) — untouched.
```

Status: FROZEN @ v1   <!-- approved at the one-approval front (contract seam) -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: the dedup is structurally guarded + behavior pinned (3 tests).
Tests live in: `add-method/tooling/test_delta_grammar_dedup.py` · run from `add-method/tooling/`.
Plan (one test per scenario, asserting behavior not internals where possible):
  - test_one_canonical_delta_grammar_source: count compiled regexes enumerating
    (DDD|SDD|UDD|TDD|ADD) in add.py source → assert == 1. RED now (2), green after collapse.
  - test_task_prose_recognizes_indented_tag_line: feed an INDENTED tag line through
    `_task_prose`; assert the delta is extracted in full. Green now (permissive `_delta_start`),
    MUST stay green after (forces the canonical to remain permissive — the regression guard).
  - test_both_delta_paths_agree: parity — `_task_prose` vs `_collect_open_deltas` recognize the
    same valid deltas and both reject a malformed line. Green now, green after.

<!-- RED driver: test_one_canonical_delta_grammar_source (2 sources today). The other two are
     the behavior-preserving safety net — they pass now and must keep passing. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule: PRESERVE behavior — delete the local `_delta_start`, point `_task_prose` at the
module-level `_DELTA_RE`, and make `_DELTA_RE` the permissive form (leading `\s*`). Move the
`_DELTA_RE` definition above `_task_prose` if that reads cleaner; do NOT change the grammar tokens.
Code lives in: `add-method/tooling/add.py` (canonical only — orchestrator syncs bundle + dogfood).
Constraints: do NOT change any test or the contract; touch only the delta-parse sites; ask if unclear.

<!-- EXIT: own test file green; no test/contract touched; the enumerated grammar compiled once. -->

### Build notes (2026-06-04)

Three edits to `add-method/tooling/add.py` only:

1. Deleted `_delta_start = re.compile(...)` local variable (was line 1205 in `_task_prose`).
2. Replaced both `_delta_start.match(...)` usages (lines 1227, 1234) with `_DELTA_RE.match(...)`.
3. Made `_DELTA_RE` PERMISSIVE: added leading `\s*` to the pattern string and rewrote
   its module-level comment (a) removing the reference to the deleted `_delta_start`,
   (b) explaining the permissive/stripped-caller split, and (c) avoiding the literal
   enumeration token in comment text (the test counts lines containing that token across
   the full source file — a comment hit would register as a second copy).

`_DELTA_RE` was NOT moved; it remains at its original position below the `_COMPETENCY_ORDER`
constants — no forward-reference issue (Python resolves globals at call time, not definition time).

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [ ] all tests pass (own file + full suite at integration)
- [ ] coverage did not decrease
- [ ] no test or contract was altered during build
- [ ] concurrency / timing — n/a (module-load-time regex compile; pure parse)
- [ ] no exposed secrets, injection openings, or unexpected dependencies
- [ ] layering & dependencies follow CONVENTIONS.md (one source, reused by all consumers)
- [ ] a person reviewed and approved the change

### GATE RECORD
Outcome: <PASS | RISK-ACCEPTED | HARD-STOP>
Reviewed by: <name> · date: <date>

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch: any future re-introduction of a parallel delta grammar (the one-source guard catches it).
Spec delta for the next loop: add a lint rule that rejects a second compiled enumerated-grammar
regex at the module level (currently only a structural test guards it).

### Competency deltas
- [ADD · open] comment text must not repeat regex enumeration literals — a source-scan test counts
  all matching lines including comments, so a comment containing the pattern registers as a phantom
  duplicate; strip the literal from comment prose (evidence: delta-grammar-dedup build, comment
  line required rewrite to keep grep count at 1)
- [ADD · open] when deduplicating a regex, the canonical must absorb the deleted copy's form
  (strict vs permissive) — the old _DELTA_RE was strict while _delta_start was permissive;
  the contract required the permissive form because _task_prose feeds un-stripped lines
  (evidence: delta-grammar-dedup §3 CONTRACT v1; test_task_prose_recognizes_indented_tag_line)
