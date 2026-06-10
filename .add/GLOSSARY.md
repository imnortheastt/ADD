# GLOSSARY  (one name per concept — used everywhere: specs, contracts, code)

ADD: AI-Driven Development — the orchestration engine (the build/verify discipline) and this skill.
AIDD: the umbrella method and the book that explains the why (the trust layer).
Task: one feature taken through the flow; lives in `.add/tasks/<slug>/TASK.md`.
Phase: a step of the flow — specify, scenarios, contract, tests, build, verify, observe, done.
Stage: project depth — prototype, poc, mvp, production (controls how deeply each phase is run).
Gate: a checkpoint with an explicit outcome: PASS, RISK-ACCEPTED, or HARD-STOP. No silent skips.
GOAL: the one durable outcome a project (and each milestone) runs toward — the loop's orientation anchor, declared as the lowercase `goal:` line in PROJECT.md / MILESTONE.md and surfaced by status/guide every session; distinct from a task's §1 Must (a single required behavior, not the whole-project outcome).
deep verify: the deepened Verify evidence (v20) required beyond passing tests — for a task that produced code, that every new symbol is referenced (wiring) and no new dead/unused code exists; for prose/non-code, a recorded no-skim semantic read; which path applies is resolver-judged and the engine never classifies (a rubric, not add.py).
Contract: the frozen external shape (interfaces, data, names, errors); changing it is a change request.
Survivor layer: documents kept for the whole project (CONVENTIONS, GLOSSARY, MODEL_REGISTRY, allowlist).
State: `.add/state.json` — the single source of truth for where the project is (the resume point).
Heavy archive / compact: step two of the archive lifecycle — `add.py compact <slug>` moves a light-archived milestone's files into the recovery bundle (step one, `archive-milestone`, only removes it from state).
Recovery bundle: `.add/archive/<slug>/` — the moved MILESTONE.md + siblings + task dirs; recovery = reverse the move, state needs no edit.
Instruction tags: the frozen v16 5-tag XML vocabulary (`<prompt>` · `<exit_gate>` · `<output_format>` · `<constraints>` · `<reject_codes>`) marking executable blocks in guides — guides-only.
Form tags: the v18 closed fill-region tag class (`<must>` · `<reject>` · `<after>` · `<assumptions>` · `<scenarios>` · `<test_plan>`) in templates/artifacts — template-only; neither tag class borrows from the other.
lowest-confidence flag: the bundle's least-sure point, surfaced at the contract freeze so the human's eye lands where it matters; the §3 artifact label reads `Least-sure flag surfaced at freeze:` (same concept, lived label). The engine refuses a frozen §3 that crosses into build without a well-formed one (`unflagged_freeze`); `audit` re-checks it on every record that crossed.
