# Releases

Append-only release ledger (newest-first) — date · version · milestones · waivers · evidence.
A milestone is "released" iff it appears in a row here (membership is the attribution source).
The engine records a row via `add.py release <version>`; the human owns the tag/publish.

## 1.6.0 — 2026-06-16
milestones: release-altitude
waivers: none
evidence: ADD 1.6.0 — the RELEASE scope level; suite 1158 green; tag v1.6.0 triggers npm/PyPI publish

## 1.5.0 — 2026-06-16 (pre-ledger baseline)
milestones: v1-1, v1-2, v2, v3, v4-1, v5, v6, v7, v8, v8-1, v9, v9-1, v10, v12, v12-1, v13, v13-1, v14, v15, v16, v17, v18, v19, v20, v21, v22, v23, flag-first-freeze, goal-auto-ready, ground-phase, ground-context, verify-integrity, udd-design-foundation, advisor-context, build-scope-lock, next-step-seams, foundation-compaction, v13-onboarding-polish
waivers: none
evidence: pre-ledger baseline — these 38 milestones shipped via the by-hand release recipe across 1.0.0–1.5.0, before the RELEASES.md ledger existed (see add-method/CHANGELOG.md). This row seeds the ledger so the first `add.py release` cut attributes only new work.
