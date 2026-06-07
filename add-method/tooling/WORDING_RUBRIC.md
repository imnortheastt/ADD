# WORDING_RUBRIC — v17 prompt-clarity   (FROZEN @ v1 · 2026-06-06)

The single source for the v17 wording rewrite. `wording_lint.py` reads its lists FROM this
file (no hardcoded duplicate). The rewrite is PHRASING, never RULES — semantics are owned by
the semantic-inventory gate, not here.

The lint is a **regression FENCE, never a metric.** It may fail only on a literal regression
(a retired phrase or an emphasis shout reappears; a keep-list term vanishes) — never on a good
rewrite. A count / density / threshold check is refused by design (`metric_gate`): it would
false-positive on a good rewrite — the same failure mode that disqualified v17's behavioral
eval as a gate. Four fences, all collision-free and green at freeze:

  F1  no ENFORCED banned phrase present on the surface        (case-INSENSITIVE, word-boundary, +inflection)
  F2  no banned emphasis token present on the surface         (case-SENSITIVE — see emphasis_tokens note)
  F3  every keep-list term still present on the surface       (guards a global rename)
  F4  the rubric is self-consistent                           (freeze-time, on this doc)

Match rule: word-boundary + phrase-level + inflection-tolerant — never a single bare word,
never a substring (so 42×"fold"/48×"thin" substring hits never fire).

## idiom_map

The full retirement PLAN (the rewriters' judgment guide). `[mapped]` = planned, still on the
surface, NOT yet enforced. A rewrite task that retires an idiom flips it `[mapped]`→`[enforced]`
in the SAME commit it removes it — the lint stays green at every task close; the set only grows.

- rubber-stamp -> approve without reading [mapped]
- wall of -> flat list of [mapped]
- collapses to -> shortens to [enforced]
- first feeder -> first input [enforced]
- blast radius -> scope of impact [enforced]

## enforced_banned

Seeded EMPTY at freeze (only already-absent entries belong here), so F1 is green now. Rewrite
tasks promote idioms here as they retire them.

- (none yet)

## keep_list

Load-bearing method vocabulary — reworded AROUND, never renamed (a rename breaks GLOSSARY,
cross-refs, and tests). F3 asserts each still appears on the surface.

- one-approval front
- seam
- fold
- competency delta
- least-sure
- touch-boundary
- trust layer
- evidence auto-gate
- autonomy dial
- survivor
- dogfood
- intake altitude
- READY-QUEUE
- REVIEW-QUEUE
- change request
- HARD-STOP
- RISK-ACCEPTED
- PASS
- FROZEN
- DDD
- SDD
- UDD
- TDD
- ADD
- AIDD
- prompt
- exit_gate
- constraints
- reject_codes
- output_format
- Role:
- Read first:
- Objective:
- Steps:
- Never:

## negative_keep_list

Negatives that STAY (a hard floor/ceiling, a safety boundary, or a prohibition with no clean
positive). Each carries a `# why:` (constraint + rationale beats a bare constraint). Positivizing
one is a guardrail weakened -> `protected_negative_removed` (review-caught — NOT a lint fence).

- the `Never:` <prompt>-skeleton field # why: a designed prohibition slot AND test-enforced (test_pilot_fully_converted asserts "Never:")
- never weaken a test or edit a frozen contract # why: the method's core integrity boundary; no clean positive carries the same force
- a security finding is always HARD-STOP # why: safety boundary
- never auto-pass a security finding # why: safety boundary
- never self-fold # why: the human-confirm boundary on foundation writes

## emphasis_tokens

The banned SHOUT forms — matched CASE-SENSITIVE (exact ALL-CAPS). Case-insensitive would
false-positive on legitimate prose: the live surface has the header `## Non-negotiable rules`
(SKILL.md) and may gain ordinary "critical path" prose — neither is the banned emphasis shout.
Matching the uppercase token only keeps the fence green-now and never blocks a good rewrite.
Strong emphasis stays reserved for true hard-stops; this is a fence, NOT a CAPS-count (metric_gate).

- CRITICAL
- NON-NEGOTIABLE

## scope_qualifier_rule

JUDGMENT (non-lintable): a phase-wide rule states the scope it governs. The lint cannot enforce
this — the semantic-inventory gate + human review do. Listed here so no one expects a fence for it.
