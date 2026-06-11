"""engine_pin — single-source ENGINE_MD5 pin.

One constant, one home. The five prose-only suites import this value instead
of each carrying a duplicate hard-coded literal. When the engine legitimately
changes, re-aim this one line and the entire tooling suite re-anchors.

The pin is a hard-coded literal — never computed at runtime. A pin that
recomputes its own value from the file it is supposed to guard is vacuous:
it can never detect drift. The literal was recorded at the commit that first
introduced it and is updated only by a deliberate, human-approved task.
"""

ENGINE_MD5 = "a20734dfb197f27c6cba724f07fd81d8"  # re-aimed @ engine-argv-portability (flags-before-slug on py<=3.12: main() now parse_known_args + _rebind_optional_positionals — non-flag extras fill UNFILLED optional positionals in the order each subparser declares via set_defaults(_opt_positionals=...); markers on phase/advance/gate/reopen/heal/guide ("slug",) and report ("milestone","task"). Safety rule frozen in §3: ANY flag-like extra refuses the WHOLE re-bind and leftovers re-raise the stock exit-2 "unrecognized arguments" — a typo'd flag's value is never mis-bound as a slug (wrong-task hazard). Behavior identical on 3.13+ where argparse binds natively (extras empty -> re-bind is a no-op). No state.json change; parse seam only)
