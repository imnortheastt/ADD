"""engine_pin — single-source ENGINE_MD5 pin.

One constant, one home. The five prose-only suites import this value instead
of each carrying a duplicate hard-coded literal. When the engine legitimately
changes, re-aim this one line and the entire tooling suite re-anchors.

The pin is a hard-coded literal — never computed at runtime. A pin that
recomputes its own value from the file it is supposed to guard is vacuous:
it can never detect drift. The literal was recorded at the commit that first
introduced it and is updated only by a deliberate, human-approved task.
"""

ENGINE_MD5 = "70d779c4e441e0419851be0941d7fdf2"  # re-aimed @ goal-auto-ready-gate (auto-ready goal: _exit_criteria_cited/_goal_auto_ready classify the active milestone, check WARNs goal_not_auto_ready, status surfaces goal-ready — all additive, freeze gate/autonomy/milestone_goal_unmet unchanged; verify-stage gap-close: the WARN excludes a done-but-not-yet-archived active milestone, Must #4 live-only)
