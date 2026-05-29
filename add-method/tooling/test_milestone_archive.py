#!/usr/bin/env python3
"""Red/green tests for `add.py archive-milestone` — light, state-only collapse.

Archiving a DONE milestone removes it + its tasks from the active state.json and
appends a compact summary to state["archived"]; files on disk are untouched, and
an active/incomplete milestone is refused (no data loss). Backward-compatible via
.get defaults. Run: python3 -m unittest test_milestone_archive -v
"""
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add


class MilestoneArchiveTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-archive-")).resolve()
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])

    def tearDown(self):
        os.chdir(self._cwd)

    # --- helpers -------------------------------------------------------------

    def _state_path(self) -> Path:
        return self.tmp / ".add" / "state.json"

    def _load(self) -> dict:
        return json.loads(self._state_path().read_text(encoding="utf-8"))

    def _capture(self, *argv) -> str:
        buf = io.StringIO()
        with redirect_stdout(buf):
            add.main(list(argv))
        return buf.getvalue()

    def _make_done_milestone(self, ms="m1", n=2) -> list[str]:
        add.main(["new-milestone", ms, "--title", "Milestone One"])
        members = []
        for i in range(n):
            t = f"{ms}-t{i}"
            add.main(["new-task", t, "--milestone", ms])
            add.main(["gate", "PASS", t])           # gate PASS -> phase done -> _task_done
            members.append(t)
        add.main(["milestone-done", ms])             # status -> done
        return members

    # --- scenarios -----------------------------------------------------------

    def test_archive_collapses_state(self):
        members = self._make_done_milestone("m1", 2)
        add.main(["archive-milestone", "m1"])
        st = self._load()
        self.assertNotIn("m1", st.get("milestones", {}), "milestone must leave active state")
        for t in members:
            self.assertNotIn(t, st.get("tasks", {}), f"task {t} must leave active state")
        archived = st.get("archived", [])
        self.assertEqual(len(archived), 1)
        self.assertEqual(archived[0]["slug"], "m1")
        self.assertEqual(archived[0]["tasks"], 2)

    def test_archive_keeps_files_on_disk(self):
        members = self._make_done_milestone("m1", 1)
        add.main(["archive-milestone", "m1"])
        self.assertTrue((self.tmp / ".add" / "milestones" / "m1" / "MILESTONE.md").exists(),
                        "light archive must keep the MILESTONE.md on disk")
        for t in members:
            self.assertTrue((self.tmp / ".add" / "tasks" / t / "TASK.md").exists(),
                            f"light archive must keep {t}/TASK.md on disk")

    def test_status_shows_archived_rollup(self):
        self._make_done_milestone("m1", 2)
        add.main(["archive-milestone", "m1"])
        out = self._capture("status")
        self.assertIn("archived: 1 milestone (2 tasks)", out)

    def test_archive_clears_active_pointers(self):
        self._make_done_milestone("m1", 2)          # active_milestone=m1, active_task=member
        add.main(["archive-milestone", "m1"])
        st = self._load()
        self.assertIsNone(st.get("active_milestone"), "archived milestone can't stay active")
        self.assertIsNone(st.get("active_task"), "archived task can't stay active")

    def test_archive_rejects_unknown(self):
        before = self._state_path().read_bytes()
        err = io.StringIO()
        with self.assertRaises(SystemExit), redirect_stderr(err):
            add.main(["archive-milestone", "nope"])
        self.assertIn("unknown_milestone", err.getvalue(),
                      "must fail for the right reason, not a parse error")
        self.assertEqual(self._state_path().read_bytes(), before, "reject must not mutate state")

    def test_archive_rejects_not_done(self):
        add.main(["new-milestone", "m2", "--title", "Two"])
        add.main(["new-task", "m2-t0", "--milestone", "m2"])    # unfinished
        err = io.StringIO()
        with self.assertRaises(SystemExit), redirect_stderr(err):
            add.main(["archive-milestone", "m2"])
        self.assertIn("milestone_not_done", err.getvalue(),
                      "an active milestone must be refused (no data loss)")
        st = self._load()
        self.assertIn("m2", st.get("milestones", {}), "refused milestone must remain")
        self.assertIn("m2-t0", st.get("tasks", {}), "its task must remain")


if __name__ == "__main__":
    unittest.main(verbosity=2)
