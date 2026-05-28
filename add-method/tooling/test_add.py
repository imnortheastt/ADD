#!/usr/bin/env python3
"""Red/green tests for add.py. Run: python3 -m unittest test_add -v"""
import json
import os
import tempfile
import unittest
from pathlib import Path

import add


class AddToolTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-test-")
        os.chdir(self.tmp)

    def tearDown(self):
        os.chdir(self._cwd)

    def _run(self, *argv):
        return add.main(list(argv))

    def _state(self):
        return json.loads((Path(self.tmp) / ".add" / "state.json").read_text())

    # --- init ---
    def test_init_creates_state_and_setup_files(self):
        self._run("init", "--name", "demo", "--stage", "mvp")
        root = Path(self.tmp) / ".add"
        self.assertTrue((root / "state.json").exists())
        for f in add.SETUP_FILES:
            self.assertTrue((root / f).exists(), f"missing {f}")
        st = self._state()
        self.assertEqual(st["project"], "demo")
        self.assertEqual(st["stage"], "mvp")
        self.assertIsNone(st["active_task"])

    def test_init_refuses_clobber_without_force(self):
        self._run("init")
        with self.assertRaises(SystemExit):
            self._run("init")

    # --- new-task ---
    def test_new_task_scaffolds_and_activates(self):
        self._run("init")
        self._run("new-task", "transfer", "--title", "Transfer money")
        tdir = Path(self.tmp) / ".add" / "tasks" / "transfer"
        self.assertTrue((tdir / "TASK.md").exists())
        self.assertTrue((tdir / "tests").is_dir())
        self.assertTrue((tdir / "src").is_dir())
        st = self._state()
        self.assertEqual(st["active_task"], "transfer")
        self.assertEqual(st["tasks"]["transfer"]["phase"], "specify")
        self.assertIn("Transfer money", (tdir / "TASK.md").read_text())

    def test_new_task_rejects_bad_slug(self):
        self._run("init")
        with self.assertRaises(SystemExit):
            self._run("new-task", "bad slug!")

    def test_new_task_requires_init(self):
        with self.assertRaises(SystemExit):
            self._run("new-task", "x")

    # --- advance / phase / marker sync ---
    def test_advance_moves_phase_and_syncs_marker(self):
        self._run("init")
        self._run("new-task", "t")
        self._run("advance")  # specify -> scenarios
        st = self._state()
        self.assertEqual(st["tasks"]["t"]["phase"], "scenarios")
        marker = [l for l in (Path(self.tmp) / ".add" / "tasks" / "t" / "TASK.md"
                              ).read_text().splitlines() if l.startswith("phase:")][0]
        self.assertIn("scenarios", marker)

    def test_phase_explicit_set(self):
        self._run("init")
        self._run("new-task", "t")
        self._run("phase", "build", "t")
        self.assertEqual(self._state()["tasks"]["t"]["phase"], "build")

    # --- gate ---
    def test_gate_pass_marks_done(self):
        self._run("init")
        self._run("new-task", "t")
        self._run("gate", "PASS")
        st = self._state()
        self.assertEqual(st["tasks"]["t"]["gate"], "PASS")
        self.assertEqual(st["tasks"]["t"]["phase"], "done")

    def test_gate_hardstop_keeps_phase(self):
        self._run("init")
        self._run("new-task", "t")
        self._run("phase", "verify", "t")
        self._run("gate", "HARD-STOP")
        st = self._state()
        self.assertEqual(st["tasks"]["t"]["gate"], "HARD-STOP")
        self.assertEqual(st["tasks"]["t"]["phase"], "verify")

    # --- stage ---
    def test_stage_change(self):
        self._run("init")
        self._run("stage", "production")
        self.assertEqual(self._state()["stage"], "production")

    # --- find_root walks up ---
    def test_find_root_from_subdir(self):
        self._run("init")
        sub = Path(self.tmp) / "a" / "b"
        sub.mkdir(parents=True)
        os.chdir(sub)
        self.assertIsNotNone(add.find_root())

    # --- check (project integrity validator) ---
    def test_check_passes_on_clean_project(self):
        self._run("init")
        self._run("new-task", "t")
        self.assertEqual(self._run("check"), 0)

    def test_check_detects_missing_task_md(self):
        self._run("init")
        self._run("new-task", "t")
        task_md = Path(self.tmp) / ".add" / "tasks" / "t" / "TASK.md"
        task_md.unlink()
        with self.assertRaises(SystemExit) as cm:
            self._run("check")
        self.assertEqual(cm.exception.code, 1)  # contract: failure -> exit 1
        self.assertFalse(task_md.exists())       # read-only: not recreated

    def test_check_detects_phase_mismatch(self):
        self._run("init")
        self._run("new-task", "t")
        st = self._state()
        st["tasks"]["t"]["phase"] = "build"  # diverge from TASK.md marker (specify)
        (Path(self.tmp) / ".add" / "state.json").write_text(json.dumps(st))
        with self.assertRaises(SystemExit) as cm:
            self._run("check")
        self.assertEqual(cm.exception.code, 1)

    def test_check_no_project(self):
        with self.assertRaises(SystemExit) as cm:
            self._run("check")
        self.assertEqual(cm.exception.code, 1)  # "no_project"

    def test_check_state_invalid(self):
        self._run("init")
        (Path(self.tmp) / ".add" / "state.json").write_text("{ not json")
        with self.assertRaises(SystemExit) as cm:
            self._run("check")
        self.assertEqual(cm.exception.code, 1)  # "state_invalid"


if __name__ == "__main__":
    unittest.main(verbosity=2)
