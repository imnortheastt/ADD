# TASK: Machine-readable engine state (--json + owner/stop)

slug: machine-state-json · created: 2026-05-29 · stage: mvp
phase: verify   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Purpose: expose engine state as parseable JSON so ANY harness (Claude Code, Codex, CI) can
read *where the project is* and *where it must stop* — the enabling layer for autonomous ADD.

Must:
  - `--json` is a flag on FOUR existing subcommands (FORK A); each prints ONE valid JSON
    object to stdout and nothing else. Shapes:
      guide  --json -> { "task", "phase", "owner", "stop", "next_step", "chapter", "gate" }
      status --json -> { "project","stage","active_task",
                         "milestones":[{slug,status,done,total}],
                         "tasks":[{slug,phase,gate,milestone}] }
      check  --json -> { "passed":int, "failed":int,
                         "checks":[{ok:bool, name:str, reason:str}] }   (exit 0/1 as today)
      ready  --json -> { "ready":[slug], "blocked":[{slug, waiting_on:[slug]}] }
  - `owner` ∈ {"human","seam","ai"} and `stop` (bool) are derived from the phase via a
    SINGLE mapping table in add.py (the harness must NEVER hard-code it). FORK B map:
      specify→human · scenarios→human · contract→seam · tests→ai · build→ai ·
      verify→human · observe→ai · done→human ;  stop = (owner != "ai")
    Net: the harness auto-runs Tests→Build (the corridor) and may auto-draft Observe; it
    STOPS at the human intake (specify/scenarios), the Contract freeze, the Verify gate,
    and Done. (See SAFETY note in BUILD — tests=ai is only safe with v4-2's red rail.)
  - Output is machine-clean: with `--json`, stdout carries ONLY the JSON (no log lines,
    no human prose); without `--json`, the existing human text is byte-for-byte unchanged.
  - JSON is built purely from State (state.json + TASK.md marker); it reads NO docs/ chapter
    (the v2 Minimal pillar must still hold — `test_min_pillar` stays green).
Reject (named codes, fail-closed but parseable):
  - no active task on `guide --json` -> still emit valid JSON with `"task": null` and
    `"stop": true` (a harness must stop and ask, not crash) — NOT an error exit.
  - a malformed/missing state.json -> stderr `no_state` + exit 1 + EMPTY stdout
    (never a half-written JSON object a harness might parse).
  - a phase not in the owner map -> stderr `unmapped_phase` + exit 1 + empty stdout
    (fail closed; a new phase must be mapped deliberately, never defaulted).
After:
  - a harness can run: read `--json` -> if `owner=="ai"` and `stop==false` act, else
    checkpoint to the human -> `advance`/`gate`. Nothing about human-text UX changed.
Assumptions (confirm before building):
  - [x] FORK A — command coverage: `--json` on `guide` + `status` + `check` + `ready`
        (confirmed by human 2026-05-29; fuller surface up front).
  - [x] FORK B — owner map = Tests+Build autonomy (tests→ai, build→ai, observe→ai; stop at
        contract & verify). Confirmed by human 2026-05-29. CONSEQUENCE recorded: tests=ai
        means an orchestrator would write failing tests unwatched — only SAFE once v4-2
        enforces "tests red before build". This task only REPORTS the map; it runs nothing,
        so exposing tests=ai now is not itself unsafe. v4-2 owns the rail.
  - [x] JSON is single-line compact (pipe-friendly), not pretty-printed.
  - [x] `--json` is a flag on the existing subcommands, not a new `export` subcommand
        (keeps the surface minimal; reuses each command's state load).

<!-- EXIT: every rule stated, every rejection has a named code, zero open assumptions. -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: guide --json on an active task carries owner + stop
  Given an active task at phase "build"
  When I run `add.py guide --json`
  Then stdout is one JSON object with owner="ai" and stop=false
  And it includes task, phase, next_step, chapter, gate

Scenario: the owner map stops the harness at a human/seam phase
  Given an active task at phase "contract"
  When I run `add.py guide --json`
  Then owner="seam" and stop=true
  # and at "verify": owner="human", stop=true; at "tests": owner="ai", stop=false

Scenario: status --json describes the whole project
  Given a project with milestones and tasks
  When I run `add.py status --json`
  Then stdout is one JSON object with project, stage, active_task
  And milestones[] each have slug,status,done,total and tasks[] each have slug,phase,gate,milestone

Scenario: check --json reports the integrity result
  When I run `add.py check --json`
  Then stdout is one JSON object with passed, failed, and a checks[] of {ok,name,reason}
  And the exit code is 0 when failed==0, else 1

Scenario: ready --json lists unblocked and blocked tasks
  When I run `add.py ready --json`
  Then stdout is one JSON object with ready[] of slugs and blocked[] of {slug,waiting_on[]}

Scenario: --json output is machine-clean
  When I run any of the four commands with --json
  Then stdout contains exactly one JSON object and no human prose or log lines

Scenario: text mode is untouched (backward compatible)
  When I run the same command WITHOUT --json
  Then the human-readable output is byte-for-byte what it was before this task

Scenario: the Minimal pillar still holds
  When any --json command runs
  And no docs/ chapter is read (test_min_pillar stays green)

Scenario: guide --json with no active task does not crash      # Reject (parseable)
  Given a project with no active task
  When I run `add.py guide --json`
  Then stdout is valid JSON with task=null and stop=true
  And the exit code is 0 (a harness stops and asks; state is unchanged)

Scenario: missing/malformed state fails closed                 # Reject (no_state)
  Given state.json is absent or unparseable
  When I run `add.py status --json`
  Then stderr says "no_state", the exit code is 1, and stdout is EMPTY
  And no partial JSON is written

Scenario: an unmapped phase fails closed                       # Reject (unmapped_phase)
  Given an active task whose phase is not in the owner map
  When I run `add.py guide --json`
  Then stderr says "unmapped_phase", the exit code is 1, and stdout is EMPTY
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

CLI contract — a `--json` flag added to four existing subcommands. No new subcommand.

```
add.py guide --json
  exit 0 -> {"task": str|null, "phase": str, "owner": "human"|"seam"|"ai",
             "stop": bool, "next_step": str, "chapter": str, "gate": str}

add.py status --json
  exit 0 -> {"project": str, "stage": str, "active_task": str|null,
             "milestones": [{"slug": str, "status": str, "done": int, "total": int}],
             "tasks":      [{"slug": str, "phase": str, "gate": str, "milestone": str|null}]}

add.py check --json
  exit 0|1 -> {"passed": int, "failed": int,
               "checks": [{"ok": bool, "name": str, "reason": str}]}   # exit 1 iff failed>0

add.py ready --json
  exit 0 -> {"ready": [str], "blocked": [{"slug": str, "waiting_on": [str]}]}

OWNER MAP (one table; the harness reads it, never hard-codes it):
  specify, scenarios, verify, done -> "human"
  contract                         -> "seam"
  tests, build, observe            -> "ai"
  stop = (owner != "ai")

ERRORS  (stderr message + exit 1 + EMPTY stdout — never partial JSON):
  no_state        -> state.json missing or unparseable
  unmapped_phase  -> active task's phase is not in the OWNER MAP

INVARIANTS:
  - with --json: stdout = exactly one compact JSON object + trailing newline; nothing else
  - without --json: existing human text is byte-for-byte unchanged
  - JSON derived ONLY from state.json + the TASK.md phase marker; reads no docs/ chapter
```

Names match the glossary: phase ∈ {specify..done}; gate ∈ {none,PASS,RISK-ACCEPTED,HARD-STOP};
stage ∈ {prototype,poc,mvp,production}. The `owner`/`stop` vocabulary is NEW (this task
introduces it) — to be added to the glossary as part of build.

Status: FROZEN @ v1   (approved by Tin Dang via AskUserQuestion, 2026-05-29)   <!-- Changing a frozen contract = change request back to SPECIFY. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY. -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: every Must + every Reject (11 tests, one per scenario).
Plan:
  - test_guide_json_active_task_carries_owner_stop — owner/stop + keys at build
  - test_owner_map_stops_at_human_and_seam — all 8 phases map; stop == (owner != "ai")
  - test_status_json_describes_project — project/stage/active_task + milestones[]/tasks[] shapes
  - test_check_json_reports_result — passed/failed/checks[]; exit 0 iff failed==0
  - test_ready_json_lists_ready_and_blocked — ready[] + blocked[]{slug,waiting_on}
  - test_json_output_is_machine_clean — whole stdout parses as ONE json object (all 4 cmds)
  - test_text_mode_is_unchanged — no --json -> human markers present, no JSON leak
  - test_minimal_pillar_holds_for_json — read-spy over the 4 --json cmds: no docs/ read
  - test_guide_json_no_active_task_is_parseable — task=null, stop=true, exit 0
  - test_status_json_fails_closed_on_bad_state — no_state, exit 1, EMPTY stdout
  - test_guide_json_unmapped_phase_fails_closed — unmapped_phase, exit 1, EMPTY stdout

Tests live in: `add-method/tooling/test_machine_state.py` (NEW, 11 tests).
Red-first evidence: 10/11 RED before build (argparse exit 2 — `--json` unknown); the 11th
(text-mode-unchanged) was GREEN by design — it guards against the build BREAKING text mode.
A helper bug (load_state given the wrong root) was found and fixed so the red was clean —
red ONLY for the missing `--json` flag, not a buggy harness (circularity bar).

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): read-only + fail-closed. Every `--json` branch loads state via
`_load_state_for_json` (`no_state` on missing/unparseable) and builds the whole dict BEFORE any
print, so a `_die` (no_state / unmapped_phase) leaves stdout EMPTY — never partial JSON. No
command mutates state.
Code lives in: `add-method/tooling/add.py` (synced byte-identical to `.add/tooling`, md5 209182c).
Built:
  - `PHASE_OWNER` map + `_phase_owner()` (unmapped_phase) + `_load_state_for_json()` (no_state)
  - `--json` branch on cmd_guide / cmd_status / cmd_check / cmd_ready (early-return; text path untouched)
  - `--json` flag on the 4 subparsers
  - appendix-c glossary: "Owner (of a phase)" + "Stop signal" entries (3 trees, md5 80536e8)
Contract deviation (recorded, surfaced at the gate — NOT silent): the frozen contract named
one error `no_state`. The pre-existing TEXT-mode `check` keeps its finer codes
(`no_project` / `state_invalid`) for backward compatibility; only the `--json` paths emit
`no_state`. The frozen INVARIANT (empty stdout + exit 1, never partial JSON) holds in both —
strictly-better, not a shape change.
Constraints honored: no test or contract altered during build; no new dependency (stdlib `json`).

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

Evidence pre-filled by the AI; the gate signature itself is the human's (Verify owner=human).
- [x] all tests pass — full suite 100/100 (89 prior + 11 new); test_machine_state 11/11
- [x] coverage did not decrease — 11 tests added, none removed; one test per scenario
- [x] no test or contract was altered during build — only add.py + glossary changed
- [x] concurrency / timing of the risky operation is safe — all four paths are READ-ONLY (no save_state); nothing to race
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib `json` only; secret scan on the diff clean
- [x] layering & dependencies follow CONVENTIONS.md — mirrors existing cmd_* + helper structure; both add.py copies md5-identical (209182c)
- [ ] a person reviewed and approved the change   ← awaiting human gate

Blind spots surfaced for the reviewer:
  - the `no_state` contract deviation (see BUILD): --json uses `no_state`; text `check` keeps `no_project`/`state_invalid`. Invariant (empty stdout + exit 1) holds.
  - FORK B exposes `tests=ai`: this task only REPORTS the map; an orchestrator acting on it is UNSAFE until v4-2 ships "tests red before build". Recorded for v4-2.

### GATE RECORD
Outcome: <PASS | RISK-ACCEPTED | HARD-STOP>
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: <name> · date: <date>

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>
Spec delta for the next loop: <what production taught you>
