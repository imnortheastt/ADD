"""engine_pin — single-source ENGINE_MD5 pin.

One constant, one home. The five prose-only suites import this value instead
of each carrying a duplicate hard-coded literal. When the engine legitimately
changes, re-aim this one line and the entire tooling suite re-anchors.

The pin is a hard-coded literal — never computed at runtime. A pin that
recomputes its own value from the file it is supposed to guard is vacuous:
it can never detect drift. The literal was recorded at the commit that first
introduced it and is updated only by a deliberate, human-approved task.
"""

ENGINE_MD5 = "6009233ac98e4aa2743ecd891a80ec0d"  # re-aimed @ reader-anchor defect fix (declaration-token readers anchor to line-start or `·`-separator — a title/prose substring no longer fools the autonomy/risk guards)
