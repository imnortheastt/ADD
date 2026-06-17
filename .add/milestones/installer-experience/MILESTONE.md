# MILESTONE: Installer Experience

goal: stand up or repair ADD for any coding agent through one guided installer — interactive when the terminal allows, agent-aware, self-healing on partial setups, and installable globally or per-project
rationale: new-major — a distribution/onramp theme no active milestone's goal covers (delta-resolution-polish is delta machinery); 5 deliverables too big for one task. Confirmed via intake interview 2026-06-17.
stage: mvp · status: active · created: 2026-06-17

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  · interactive npm installer via @clack/prompts + graceful plain-text fallback
       (non-TTY / CI); pip gets the matching plain-text flow — npm↔pip parity held
       for every non-clack behavior
     · agent detection (Claude Code · Claude app/cowork · Codex · OpenCode · generic
       AGENTS.md fallback) → writes the right integration file + prints THAT agent's
       exact next step
     · heal/reconcile — init AND update scan .add/ for missing/stale managed assets,
       overwrite the managed layer, ADD missing components — never wipes user data
     · global install — engine+book+skill installable to a global ADD home, updated
       once for all projects
     · per-project data — local & git-tracked by DEFAULT; --global-data opt-in
       persists a project's data under the global home keyed by project path
Out: · per-project data in the global home by default (stays opt-in; the
       self-contained / git-tracked invariant holds)
     · auto-running `add.py init` from the installer (still deferred to /add — keeps
       the v12 lock-down gate + the brownfield signal intact)
     · auto-launching / spawning the user's agent (we print/hand a next step, not spawn)
     · a hosted / web / GUI installer; install-time telemetry or network calls

## Shared decisions & glossary deltas   (living — every task must honor these)
- The managed-layer ↔ user-data boundary is sacred: heal/reconcile and global install
  NEVER clobber state.json · PROJECT.md · milestones · tasks · archive.
- Designed-for-failure on every new IO path: clack import → plain text · agent detect
  → generic AGENTS.md · global home unwritable → clear error + local fallback.
- npm↔pip parity: identical behavior except clack richness; both share the managed-layer
  list, the .add-version stamp format, and the heal logic.
- New glossary terms: **global ADD home** (shared engine+book+skill location) ·
  **global-data** (opt-in per-project data under the global home) · **agent profile**
  (detect → integration-file → next-step mapping) · **heal/reconcile** (init/update
  gap-fill that adds missing managed components without wiping user data).

## Shared / risky contracts (freeze these first)
- global-home layout + project-keying + how a local .add/tooling resolves the global
  engine (pointer vs copy)   -> owning task `global-install`   ← riskiest, freeze first
- agent-profile shape {agent_id, detect_signal, integration_files, next_step}
                                                   -> owning task `agent-detect`
- heal manifest: the canonical managed-component list + the missing/stale/present rule
                                                   -> owning task `heal-reconcile`

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] installer-prompts  depends-on: none           — @clack/prompts interactive npm flow + plain-text fallback; pip matching flow; parity preserved
- [ ] agent-detect       depends-on: none           — detect the coding agent, write its integration file (CLAUDE.md/AGENTS.md), print its exact next step
- [ ] heal-reconcile     depends-on: none           — init+update scan .add/, report missing/stale, overwrite managed + add missing, never touch user data
- [ ] global-install     depends-on: heal-reconcile — global ADD home; engine+book+skill installed once, updated for all projects
- [ ] global-data        depends-on: global-install — --global-data opt-in persists per-project data under the global home keyed by project path

## Exit criteria (observable; map each to the task that delivers it)
- [ ] `npx @pilotspace/add` in a TTY shows a guided interactive install; in CI/non-TTY it falls back to plain text with the SAME outcome   (← installer-prompts)
- [ ] the installer detects the active agent, writes its integration file, prints its exact next step; unknown agent → generic AGENTS.md   (← agent-detect)
- [ ] `init`/`update` on a partial .add/ report what's missing/stale and restore it WITHOUT touching state/PROJECT/tasks   (← heal-reconcile)
- [ ] a user installs ADD once to a global home and uses it across projects; `update` there refreshes all   (← global-install)
- [ ] `--global-data` persists a project's data under the global home keyed by path; without it, data stays local & git-tracked (default)   (← global-data)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : <add.py / state.json / templates — what shipped, or "untouched">
- skill   : <SKILL.md / phases/* / guides — what shipped, or "untouched">
- book    : <docs/* — what shipped, or "untouched">

### Cross-task evidence   (one row per task)
- <slug> : gate=<PASS|RISK-ACCEPTED> · tests=<n green> · residue=<none|note>

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [ ] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (cite which)
- goal: <restate the milestone goal — and the one evidence line that proves the ship meets it>

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] <step — e.g. open a PR from the Close ship-review above; the human reviews + merges>
- [ ] <step — e.g. export the ship-review to a hand-off doc, e.g. `pandoc CLOSE.md -o close.docx`>
- [ ] <step — e.g. tag / publish / deploy  (human-run, per release.md)>
