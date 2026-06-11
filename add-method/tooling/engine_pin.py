"""engine_pin — single-source ENGINE_MD5 pin.

One constant, one home. The five prose-only suites import this value instead
of each carrying a duplicate hard-coded literal. When the engine legitimately
changes, re-aim this one line and the entire tooling suite re-anchors.

The pin is a hard-coded literal — never computed at runtime. A pin that
recomputes its own value from the file it is supposed to guard is vacuous:
it can never detect drift. The literal was recorded at the commit that first
introduced it and is updated only by a deliberate, human-approved task.
"""

ENGINE_MD5 = "7b05eaf9ba63d6455d3c92d9cec40f17"  # re-aimed @ heal-then-escalate (verify-integrity, the bounded self-heal loop: a CONFIRMED cheat no longer dies on sight — _tamper_guard's divergence branch routes to the new _heal_or_escalate router; under HEAL_CAP=3 it records state[task]["heal"]={attempts,history}, sets phase=build DIRECTLY (no mid-loop re-snapshot), saves BEFORE exit (atomic — no free attempt on re-run), and exits 3 (redo signal, distinct from _die's 1 / argparse's 2); the 4th confirmed cheat records gate=HARD-STOP and _die's heal_exhausted (escalation). MONOTONIC — attempts never auto-resets (cmd_phase is unguarded, so a reset would be a zero-human cap bypass). New `heal` subcommand (cmd_heal) is the SEMANTIC honor-system entry — the agent reports an overfit/vacuous/stub refute-read finding via --reason at the verify phase (heal_reason_required / heal_not_at_verify); the engine never spawns the refute-read. GATES vocabulary unchanged. tool-agnostic — never runs tests)
