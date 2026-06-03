#!/usr/bin/env python3
"""Behavioral proof of `add.py deltas` (task: deltas-report, v10).

CONTRACT (frozen @ v1): a READ-ONLY report. `add.py deltas` scans every
.add/tasks/*/TASK.md "### Competency deltas" block, shows only `open` deltas
grouped by competency in canonical order with per-group counts + a grand total;
`--json` prints ONE object {total, by_competency}; exit 0 ALWAYS; writes
nothing; folded/rejected excluded; malformed/comment lines skipped (not fatal).
One test per SCENARIO. Run: python3 -m unittest test_deltas_report -v
"""
import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

import add


def _run(argv):
    """Run add.main(argv), capturing (exit_code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    code = 0
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            add.main(argv)
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    return code, out.getvalue(), err.getvalue()


class DeltasReportTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-deltas-report-")
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])

    def tearDown(self):
        os.chdir(self._cwd)

    # --- helpers -------------------------------------------------------------
    def _add_deltas(self, slug, *lines):
        """Create task `slug` (if new) and inject live delta lines into its block."""
        root = add.find_root()
        if slug not in (add.load_state(root).get("tasks") or {}):
            add.main(["new-task", slug, "--title", "Feature"])
        p = Path(self.tmp) / ".add" / "tasks" / slug / "TASK.md"
        text = p.read_text(encoding="utf-8")
        marker = "### Competency deltas"
        idx = text.index(marker) + len(marker)
        p.write_text(text[:idx] + "\n" + "\n".join(lines) + "\n" + text[idx:],
                     encoding="utf-8")

    def _state_bytes(self):
        return (Path(self.tmp) / ".add" / "state.json").read_bytes()

    # --- scenarios -----------------------------------------------------------
    def test_groups_open_by_competency(self):
        self._add_deltas("a",
                         "- [TDD · open] guards prove words not behavior (evidence: build1)",
                         "- [TDD · open] dogfood twin can drift (evidence: build2)")
        self._add_deltas("b",
                         "- [ADD · open] bundle must be regenerated (evidence: parity)")
        before = self._state_bytes()
        code, out, _ = _run(["deltas"])
        self.assertEqual(code, 0, "deltas must exit 0")
        self.assertIn("TDD (2)", out)
        self.assertIn("ADD (1)", out)
        self.assertIn("3 total", out)
        self.assertEqual(self._state_bytes(), before, "deltas must be read-only")

    def test_excludes_folded_and_rejected(self):
        self._add_deltas("a",
                         "- [DDD · open] shown-open-one (evidence: e)",
                         "- [DDD · folded] hidden-folded-one (evidence: e)",
                         "- [DDD · rejected] hidden-rejected-one (evidence: e)")
        code, out, _ = _run(["deltas"])
        self.assertEqual(code, 0)
        self.assertIn("shown-open-one", out)
        self.assertNotIn("hidden-folded-one", out)
        self.assertNotIn("hidden-rejected-one", out)

    def test_no_open_deltas_message(self):
        code, out, _ = _run(["deltas"])
        self.assertEqual(code, 0)
        self.assertIn("no open deltas", out.lower())

    def test_json_shape(self):
        self._add_deltas("a", "- [SDD · open] spec-line (evidence: s)")
        self._add_deltas("b", "- [UDD · open] ux-line (evidence: u)")
        code, out, _ = _run(["deltas", "--json"])
        self.assertEqual(code, 0)
        obj = json.loads(out)  # raises if not exactly one JSON object
        self.assertIsInstance(obj, dict)
        self.assertEqual(obj["total"], 2)
        self.assertIn("SDD", obj["by_competency"])
        entry = obj["by_competency"]["SDD"][0]
        for k in ("task", "text", "evidence"):
            self.assertIn(k, entry)

    def test_malformed_line_skipped(self):
        self._add_deltas("a",
                         "- [TDD · open] valid-open-one (evidence: e)",
                         "- [BOGUS] not a delta at all",
                         "- just a dash line, no tag")
        code, out, _ = _run(["deltas"])
        self.assertEqual(code, 0, "a malformed line must not crash the report")
        self.assertIn("valid-open-one", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
