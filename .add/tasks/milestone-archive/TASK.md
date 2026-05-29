# TASK: collapse done milestones

slug: milestone-archive · created: 2026-05-28 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

`add.py archive-milestone <slug>` collapses a FINISHED milestone so state.json and
`status` stay small as the project grows. Decision (user-picked): LIGHT archive —
shrink the active state only; files on disk are untouched (history preserved).

Must:
  - Require the milestone be done (`status == "done"`, set by `milestone-done`).
  - Remove the milestone from `state["milestones"]` AND remove its member tasks from
    `state["tasks"]` (this is the actual state shrink).
  - Append ONE compact record to `state["archived"]` (a list): `{slug, title, tasks:
    <count>, archived: <date>}` — a summary only, never the task bodies.
  - If `active_milestone` was this slug -> set it None; if `active_task` was one of the
    archived tasks -> set it None.
  - Files on disk (MILESTONE.md, each TASK.md) are NOT moved or deleted.
  - `status` prints a one-line "archived: N milestone(s) (M tasks)" rollup when any exist.
  - Backward-compatible: read archived via `.get("archived", [])`; an old state.json
    with no `archived` key keeps working.
Reject:
  - Unknown milestone slug -> `_die("unknown_milestone")`.
  - Milestone not done -> `_die("milestone_not_done")` (run `milestone-done` first;
    NEVER collapse an active/incomplete milestone — that would lose live work).
After:
  - `state["milestones"]`/`state["tasks"]` no longer contain the milestone or its tasks;
    `state["archived"]` has the summary; `status` stays small; the files still exist.
Assumptions (confirm before building):
  - [x] LIGHT archive — shrink state, keep files (user-picked)
  - [x] gate on `status == "done"` (compose with milestone-done) — not a re-check of tasks
  - [x] compact record carries a COUNT, not the task list, to keep state small

<!-- EXIT: every rule stated, every rejection has a named code, zero open assumptions. -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: archive a done milestone collapses it out of active state
  Given a done milestone "m1" with 2 PASS tasks
  When I run `add.py archive-milestone m1`
  Then state.milestones has no "m1" and state.tasks has neither member task
  And state.archived has one record {slug: m1, tasks: 2}

Scenario: the milestone + task files stay on disk
  Given the same archived milestone
  When I inspect the filesystem
  Then .add/milestones/m1/MILESTONE.md and each task's TASK.md still exist

Scenario: status shows the archived rollup
  Given one archived milestone with 2 tasks
  When I run `add.py status`
  Then output contains "archived: 1 milestone (2 tasks)"

Scenario: archiving clears active pointers that referenced it
  Given m1 is the active milestone and a member task is the active task
  When I archive m1
  Then active_milestone is null and active_task is null

Scenario: an unknown milestone is rejected
  Given any project
  When I run `add.py archive-milestone nope`
  Then it exits non-zero with "unknown_milestone"
  And state.json is unchanged

Scenario: a not-done milestone is refused (no data loss)
  Given an active milestone "m2" with an unfinished task
  When I run `add.py archive-milestone m2`
  Then it exits non-zero with "milestone_not_done"
  And m2 and its task are still in active state
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
cli:  add.py archive-milestone <slug>      (new subcommand; requires a .add/ root)

cmd_archive_milestone(args):
  - slug not in state["milestones"]            -> _die("unknown_milestone")
  - state["milestones"][slug]["status"] != done -> _die("milestone_not_done")
  - members = [s for s,t in tasks if t.milestone == slug]
  - state.setdefault("archived", []).append(
        { "slug": slug, "title": <title>, "tasks": len(members),
          "archived": date.today().isoformat() })
  - del state["milestones"][slug]; for s in members: del state["tasks"][s]
  - active_milestone == slug   -> None
  - active_task in members      -> None
  - save_state

cmd_status: after the milestone rollup, if state.get("archived"):
  print "archived: <N> milestone(s) (<M> tasks)"   where M = sum(rec["tasks"])

Schema delta (backward-compatible): state["archived"]: list[{slug,title,tasks,archived}]
  read everywhere via state.get("archived", []).
```

Status: FROZEN @ v1   <!-- Changing a frozen contract = change request back to SPECIFY. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY. -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: all 6 scenarios (new file add-method/tooling/test_milestone_archive.py).
Plan (one test per scenario; assert state shape + filesystem + output + immutability-on-reject):
  - test_archive_collapses_state:      done m1(2 tasks) / archive / milestones&tasks gone, record present
  - test_archive_keeps_files_on_disk:  archive / MILESTONE.md + TASK.md still exist
  - test_status_shows_archived_rollup: archive / status / "archived: 1 milestone (2 tasks)"
  - test_archive_clears_active_pointers: archive active m1 / active_milestone & active_task -> null
  - test_archive_rejects_unknown:      archive nope / SystemExit + "unknown_milestone" + state unchanged
  - test_archive_rejects_not_done:     active m2 w/ unfinished task / archive / "milestone_not_done" + m2 intact

Tests live in: `add-method/tooling/test_milestone_archive.py` · MUST run red before Build.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): NEVER collapse a not-done milestone (reject first, before
any mutation); the archived record is a COUNT-only summary so state can't regrow; the
write is atomic via save_state; on any reject, state.json is left byte-for-byte unchanged
(validate-before-mutate). stdlib only.
Code lives in: `add-method/tooling/add.py` (cmd_archive_milestone + status rollup + subparser).
Keep `.add/tooling/add.py` byte-identical to source.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — 59/59 green; 6 new in test_milestone_archive.py
- [x] coverage did not decrease — tests only added; red-first confirmed (4 errors + 2 non-vacuous FAIL)
- [x] no test or contract was altered during build — contract FROZEN @ v1
- [x] concurrency / timing safe — validate-before-mutate; single atomic save_state; no shared state
- [x] no exposed secrets / injection / unexpected deps — stdlib only; record is a count summary
- [x] layering & deps follow CONVENTIONS.md — flat stdlib add.py; backward-compat via .get("archived", [])
- [x] a person reviewed — author self-review + live smoke (collapse, status rollup, not-done reject);
      combined v1-1 adversarial review runs before the push. Human author sign-off: pending.

### GATE RECORD
Outcome: PASS
Reviewed by: author (self) · date: 2026-05-29 · combined v1-1 adversarial review pending pre-push
Evidence: 59/59 green · reject-leaves-state-unchanged covered by test_archive_rejects_unknown ·
no-data-loss on not-done by test_archive_rejects_not_done · live smoke matched the approved preview.

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): does state.json actually stay small across many
milestones? do users want to LIST or RESTORE an archived milestone? Spec delta for the
next loop: `add.py archived` (list records), an `un-archive`/restore path, and optional
heavy archive (move files to `.add/milestones/_archive/<slug>/`) if the tree gets noisy.
