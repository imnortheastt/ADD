#!/usr/bin/env python3
"""Behavioral proof of the SPEC-delta GUARDS (task: spec-delta-guards, delta-resolution).

CONTRACT (frozen @ v1): an open SPEC delta can never be lost silently — PROJECT-WIDE.
  - `compact <ms>` REFUSES "open_spec_deltas_unresolved" while ANY task in the project
    holds an open SPEC delta (after open_deltas_unfolded, BEFORE the move; tree+state
    byte-unchanged on reject). Deliberately broader than the member-scoped competency guard.
  - `status` prints a read-only "spec : N open SPEC delta(s) …" line (project-wide; silent at 0).
  - `milestone-done` prints a "note: N open SPEC delta(s) to resolve …" (project-wide; never blocks).
  - `report <ms> --json` carries summary["open_spec"] = project-wide count.
  All four surfaces read ONE source: len(_collect_open_spec_deltas(root)). One test per SCENARIO.
Run: python3 -m unittest test_spec_delta_guards -v
"""
from __future__ import annotations

import io
import os
import re
import json
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add


def _run(argv):
    out, err = io.StringIO(), io.StringIO()
    code = None
    with redirect_stdout(out), redirect_stderr(err):
        try:
            add.main(argv)
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
    return out.getvalue(), err.getvalue(), code


def _meet_exit_criteria(ms):
    root = add.find_root()
    p = root / "milestones" / ms / add.MILESTONE_FILE
    text = p.read_text(encoding="utf-8")
    text = re.sub(r"## Exit criteria.*?(?=\n## |\Z)",
                  lambda m: m.group(0).replace("- [ ]", "- [x]"), text, flags=re.S)
    p.write_text(text, encoding="utf-8")


def _snapshot(base):
    return {str(p.relative_to(base)): p.read_bytes()
            for p in sorted(base.rglob("*")) if p.is_file()}


class SpecDeltaGuardsTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-spec-guards-")
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])
        self.root = Path(self.tmp) / ".add"

    def tearDown(self):
        os.chdir(self._cwd)
        shutil.rmtree(self.tmp, ignore_errors=True)

    # --- helpers -------------------------------------------------------------
    def _plant_spec(self, slug, text="x"):
        """Inject one grammar-valid OPEN SPEC delta into slug's §7 block."""
        p = self.root / "tasks" / slug / "TASK.md"
        s = p.read_text(encoding="utf-8")
        i = s.index("### Spec delta") + len("### Spec delta")
        p.write_text(s[:i] + f"\n- [SPEC · open] {text} (evidence: e)\n" + s[i:],
                     encoding="utf-8")

    def _light_archive(self, ms, *slugs):
        """Drive a milestone to light-archived (the precondition compact operates on)."""
        add.main(["new-milestone", ms, "--goal", "g"])
        for s in slugs:
            add.main(["new-task", s, "--milestone", ms])
            add.main(["phase", "verify", s])
            add.main(["gate", "PASS", s])
        _meet_exit_criteria(ms)
        _run(["milestone-done", ms])
        _run(["archive-milestone", ms])

    def _state_bytes(self):
        return (self.root / "state.json").read_bytes()

    # --- scenarios -----------------------------------------------------------
    def test_compact_blocks_open_spec_delta_projectwide(self):  # Must 1 (project-wide)
        self._light_archive("v1", "t1")          # v1 ready to compact (member: t1)
        add.main(["new-task", "outsider"])        # a NON-member task elsewhere
        self._plant_spec("outsider", "stray idea")
        before_tree, before_state = _snapshot(self.root), self._state_bytes()
        out, err, code = _run(["compact", "v1"])
        self.assertIsNotNone(code)
        self.assertIn("open_spec_deltas_unresolved", out + err)
        self.assertIn("outsider", out + err)      # names the offending NON-member -> project-wide
        self.assertFalse((self.root / "archive" / "v1").exists())
        self.assertEqual(_snapshot(self.root), before_tree)   # byte-unchanged
        self.assertEqual(self._state_bytes(), before_state)

    def test_compact_proceeds_when_spec_resolved(self):  # Must 1 (unblock)
        self._light_archive("v1", "t1")
        add.main(["new-task", "outsider"])
        self._plant_spec("outsider", "stray idea")
        _run(["drop-delta", "outsider"])          # resolve the only open SPEC delta
        out, err, code = _run(["compact", "v1"])
        self.assertIsNone(code, f"compact should succeed once resolved: {err}")
        self.assertTrue((self.root / "archive" / "v1").exists())

    def test_status_nudges_open_spec_silent_when_none(self):  # Must 2
        add.main(["new-task", "a"])
        self._plant_spec("a", "rate limit")
        out, _, _ = _run(["status"])
        self.assertRegex(out, r"spec\s*:\s*1\b", "status must surface the open SPEC count")
        before = self._state_bytes()
        _run(["drop-delta", "a"])                 # now zero open
        out2, _, _ = _run(["status"])
        self.assertNotRegex(out2, r"spec\s*:\s*\d+ open",
                            "status must be silent when no open SPEC delta")
        # status itself never wrote (compare a status run against its own pre-bytes)
        pre = self._state_bytes()
        _run(["status"])
        self.assertEqual(self._state_bytes(), pre, "status must be read-only")

    def test_milestone_done_nudges_open_spec(self):  # Must 3
        add.main(["new-milestone", "mvp", "--goal", "g"])
        add.main(["new-task", "t", "--milestone", "mvp"])
        add.main(["phase", "verify", "t"])
        add.main(["gate", "PASS", "t"])
        self._plant_spec("t", "watch the retry path")
        _meet_exit_criteria("mvp")
        out, err, code = _run(["milestone-done", "mvp"])
        self.assertIsNone(code, f"milestone-done must still succeed: {err}")
        self.assertRegex(out, r"note:.*open SPEC delta", "must nudge open SPEC deltas")

    def test_report_counts_open_spec_projectwide(self):  # Must 4
        add.main(["new-milestone", "v1", "--goal", "g"])
        add.main(["new-task", "t", "--milestone", "v1"])
        add.main(["new-task", "elsewhere"])       # the open delta lives OFF the reported milestone
        self._plant_spec("elsewhere", "stray")
        before = self._state_bytes()
        out, err, code = _run(["report", "v1", "--json"])
        self.assertIsNone(code, f"report failed: {err}")
        data = json.loads(out)
        self.assertEqual(data["summary"]["open_spec"], 1,
                         "report open_spec is the PROJECT-WIDE count")
        self.assertEqual(self._state_bytes(), before, "report must be read-only")


if __name__ == "__main__":
    unittest.main()
