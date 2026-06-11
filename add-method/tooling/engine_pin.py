"""engine_pin — single-source ENGINE_MD5 pin.

One constant, one home. The five prose-only suites import this value instead
of each carrying a duplicate hard-coded literal. When the engine legitimately
changes, re-aim this one line and the entire tooling suite re-anchors.

The pin is a hard-coded literal — never computed at runtime. A pin that
recomputes its own value from the file it is supposed to guard is vacuous:
it can never detect drift. The literal was recorded at the commit that first
introduced it and is updated only by a deliberate, human-approved task.
"""

ENGINE_MD5 = "a6eed5e0c374694945cf4273d1a2581d"  # re-aimed @ tamper-tripwire (verify-integrity, the method's FIRST mechanical HARD-STOP: snapshot md5(resolved red test files + frozen §3) into state[task]["tripwire"] at the tests->build advance — UNCONDITIONAL overwrite, co-witnessed by flag_verified; re-check at the verify gate inside the first `if completing:` block BEFORE the waiver write so a tamper is never RISK-ACCEPTED-launderable; tri-state (present+match -> pass · present+diverged -> HARD-STOP tamper_detected · absent+flag_verified -> HARD-STOP tripwire_missing · absent+unverified -> skip legacy); fail-closed _md5_file (unreadable -> diverged); refactor _tests_count/_declared_tests_count to expose _primary_test_files/_declared_test_files/_resolved_test_files (one resolver, paths reused never re-globbed); cmd_check gains a never-red build_tampered standing WARN. tool-agnostic — hashes bytes only, never runs tests)
