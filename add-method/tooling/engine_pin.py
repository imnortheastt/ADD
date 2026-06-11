"""engine_pin — single-source ENGINE_MD5 pin.

One constant, one home. The five prose-only suites import this value instead
of each carrying a duplicate hard-coded literal. When the engine legitimately
changes, re-aim this one line and the entire tooling suite re-anchors.

The pin is a hard-coded literal — never computed at runtime. A pin that
recomputes its own value from the file it is supposed to guard is vacuous:
it can never detect drift. The literal was recorded at the commit that first
introduced it and is updated only by a deliberate, human-approved task.
"""

ENGINE_MD5 = "e6b8c3da98ef092c38f5d1c78760c4ad"  # re-aimed @ ground-bundle-wiring (grounding wiring, measure-not-block: add _section0_anchors + _grounded_state (tri-state True/False/None) + _task_grounded; cmd_status prints a `grounded:` line for the active task ONLY when §0 exists (None/legacy -> no line, so existing output is byte-unchanged), after the --json early-return; cmd_check appends a `task_not_grounded` WARN — never red — IFF the active task's §3 is FROZEN and _grounded_state is False, riding the existing warnings array (no new --json key). additive; the ground phase, spec-bundle freeze + autonomy ladder unchanged)
