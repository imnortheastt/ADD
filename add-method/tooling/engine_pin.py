"""engine_pin — single-source ENGINE_MD5 pin.

One constant, one home. The five prose-only suites import this value instead
of each carrying a duplicate hard-coded literal. When the engine legitimately
changes, re-aim this one line and the entire tooling suite re-anchors.

The pin is a hard-coded literal — never computed at runtime. A pin that
recomputes its own value from the file it is supposed to guard is vacuous:
it can never detect drift. The literal was recorded at the commit that first
introduced it and is updated only by a deliberate, human-approved task.
"""

ENGINE_MD5 = "45254aa9af1c0e73962aafff443be08a"  # re-aimed @ scope-violation-heal (a scope refusal now ROUTES into the bounded self-heal loop, build-scope-lock task 3/3: _scope_guard no longer dies in place on the RECOVERABLE findings — an out-of-scope touch (source 'scope') and a present-but-wrong sidecar (diverged|unparseable, source 'scope-tamper') call the SAME _heal_or_escalate the tamper tripwire uses, returning the task to BUILD for an honest redo (exit 3) and counting against the ONE shared per-task HEAL_CAP; the (CAP+1)th confirmed finding records gate=HARD-STOP and escalates heal_exhausted. The ERASED baselines stay die-in-place (exit 1, no heal): a MISSING sidecar is scope_snapshot_tampered and an erased anchor under a present sidecar is scope_anchor_missing — a redo cannot recreate erased evidence (tripwire_missing parity). Every heal reason CARRIES its named code so the refusal-token assertions still match; placement unchanged — after _tamper_guard, BEFORE the waiver write, off the HARD-STOP path; a heal never rewrites the sidecar or anchor. check stays a read-only WARN monitor — never routes to heal, never increments. Carries the prior scope-gate-enforce gate (NEW _declared_scope parses the frozen §5 grammar — backticked tokens · FIRST 'Scope (may touch):' line · ./… task dir · '/' project root · bare sibling-of-previous · outside-root dropped · directory token = WHOLE subtree · no line = UNDECLARED grandfathered · garbage = [] no cover; tests->build _scope_walk {rel: md5} pruning _SCOPE_EXCLUDE_DIRS into sidecar scope-snapshot.json anchored by sidecar-md5; v2 anchor×sidecar co-witness after the anchor-erase REFUTE; v3 UNDECLARED-crossing cleanup), the engine-merge-base-enforcement wave-ledger gate (cmd_check wave section + read-only cmd_wave_verify, v4 status-field grammar, exactly-one echo column, six drift fixtures), and the engine-argv-portability re-bind. tool-agnostic — never runs git)
