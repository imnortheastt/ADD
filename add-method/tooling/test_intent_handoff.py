#!/usr/bin/env python3
"""Red-first tests for intent-handoff (installer-smarts task 4).

Contract FROZEN @ v1: an optional, LAST interactive prompt captures a one-line build
intent and persists it as a NOTE (`<target>/.add/.intent`) for `/add` to read — WITHOUT
running init. Deferred-init is sacred: the installer writes inert text, never execs add.py,
never creates state.json. The prompt is interactive-only + fully optional (EOF/empty/Ctrl-C
-> skip, exit 0, never cancel). Both twins decision-equivalent; the 3 SKILL.md trees stay
md5-equal and instruct `/add` to read the note.

Run: python3 -m unittest test_intent_handoff -v
"""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

_TOOLING = Path(__file__).resolve().parent
_SRC = _TOOLING.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
from add_method import _installer            # noqa: E402

from test_installer_prompts import NODE, CLI_JS, PKG_ROOT, REPO_ROOT
from test_global_install import _make_bundled
from test_readiness_detect import _node_detect


# --- the pure write helper (no init, ever) ----------------------------------

class PipWriteIntentNoteTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="intent-"))
        (self.tmp / ".add").mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_writes_when_nonempty(self):
        wrote = _installer._write_intent_note(self.tmp, "a todo app")
        self.assertTrue(wrote)
        self.assertEqual((self.tmp / ".add" / ".intent").read_text().strip(), "a todo app")
        self.assertFalse((self.tmp / ".add" / "state.json").exists(),
                         "the note must NEVER create state.json (deferred-init)")

    def test_skips_when_empty_or_whitespace(self):
        self.assertFalse(_installer._write_intent_note(self.tmp, "   "))
        self.assertFalse(_installer._write_intent_note(self.tmp, ""))
        self.assertFalse((self.tmp / ".add" / ".intent").exists(),
                         "empty/whitespace intent must write nothing")


class PipPromptIntentTest(unittest.TestCase):
    def test_eof_returns_empty_string(self):
        with mock.patch("builtins.input", side_effect=EOFError):
            self.assertEqual(_installer._prompt_intent(), "",
                             "EOF at the optional intent prompt must skip (return ''), not raise")

    def test_keyboard_interrupt_returns_empty_string(self):
        with mock.patch("builtins.input", side_effect=KeyboardInterrupt):
            self.assertEqual(_installer._prompt_intent(), "")


# --- interactive install: typed intent writes the note (no init) -------------

class PipInteractiveIntentTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="intent-"))
        self.bundled = _make_bundled(self.tmp / "pkg")
        self.proj = self.tmp / "proj"; self.proj.mkdir()
        self.userhome = self.tmp / "user"; self.userhome.mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _env(self):
        return {"ADD_HOME": str(self.tmp / "home"), "HOME": str(self.userhome)}

    def _interactive(self, responses):
        prev = os.environ.get("ADD_INSTALLER_FORCE_INTERACTIVE")
        os.environ["ADD_INSTALLER_FORCE_INTERACTIVE"] = "1"
        try:
            with mock.patch("builtins.input", side_effect=responses), \
                    mock.patch("sys.stdout"):           # swallow the banner/readiness noise
                return _installer.install(target=str(self.proj), bundled=str(self.bundled),
                                          non_interactive=False, env=self._env())
        finally:
            if prev is None:
                os.environ.pop("ADD_INSTALLER_FORCE_INTERACTIVE", None)
            else:
                os.environ["ADD_INSTALLER_FORCE_INTERACTIVE"] = prev

    def test_typed_intent_writes_note_and_never_inits(self):     # target, scope=project, intent
        code = self._interactive(["", "n", "a todo app"])
        self.assertEqual(code, 0)
        self.assertEqual((self.proj / ".add" / ".intent").read_text().strip(), "a todo app")
        self.assertFalse((self.proj / ".add" / "state.json").exists(),
                         "the installer must NEVER init from the intent")

    def test_skipped_intent_writes_nothing(self):               # Reject: intent_skipped_no_note
        code = self._interactive(["", "n", ""])
        self.assertEqual(code, 0, "a skipped intent must still succeed")
        self.assertFalse((self.proj / ".add" / ".intent").exists())
        self.assertTrue((self.proj / ".add" / "tooling" / "add.py").exists(),
                        "the per-project drop still happened")


# --- non-interactive never prompts/writes; never inits ----------------------

class IntentInvariantsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="intent-"))
        self.bundled = _make_bundled(self.tmp / "pkg")
        self.proj = self.tmp / "proj"; self.proj.mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_noninteractive_no_intent_no_state(self):           # Reject: noninteractive_no_intent + intent_never_inits
        code = _installer.install(target=str(self.proj), bundled=str(self.bundled),
                                  non_interactive=True)
        self.assertEqual(code, 0)
        self.assertFalse((self.proj / ".add" / ".intent").exists(),
                         "a non-interactive run writes no .intent")
        self.assertFalse((self.proj / ".add" / "state.json").exists(),
                         "the installer never creates state.json (deferred-init)")
        self.assertTrue((self.proj / ".add" / "tooling" / "add.py").exists())


# --- npm twin: the write helper (node harness) + the --yes invariant --------

@unittest.skipUnless(NODE, "node not on PATH — honest skip")
class NpmIntentTest(unittest.TestCase):
    def test_writeIntentNote_writes_when_nonempty(self):
        tmp = Path(tempfile.mkdtemp(prefix="intent-npm-"))
        try:
            (tmp / ".add").mkdir()
            import json
            wrote = _node_detect('m.writeIntentNote(%s, "build a thing")' % json.dumps(str(tmp)))
            self.assertTrue(wrote)
            self.assertEqual((tmp / ".add" / ".intent").read_text().strip(), "build a thing")
            self.assertFalse((tmp / ".add" / "state.json").exists())
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_yes_run_writes_no_intent(self):
        tmp = Path(tempfile.mkdtemp(prefix="intent-npm-"))
        try:
            proj = tmp / "proj"; proj.mkdir()
            res = subprocess.run([NODE, str(CLI_JS), "init", "--yes", str(proj)],
                                 capture_output=True, text=True, timeout=60)
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertFalse((proj / ".add" / ".intent").exists(),
                             "a --yes run must write no .intent")
            self.assertFalse((proj / ".add" / "state.json").exists(),
                             "the installer never inits")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


# --- skill wiring: /add reads the note; 3 trees md5-equal --------------------

class SkillReadsIntentTest(unittest.TestCase):
    def _trees(self):
        return [
            REPO_ROOT / ".claude" / "skills" / "add" / "SKILL.md",
            PKG_ROOT / "skill" / "add" / "SKILL.md",
            PKG_ROOT / "src" / "add_method" / "_bundled" / "skill" / "add" / "SKILL.md",
        ]

    def test_skill_instructs_add_to_read_intent(self):
        for p in self._trees():
            self.assertTrue(p.exists(), f"missing skill tree: {p}")
            self.assertIn(".add/.intent", p.read_text(encoding="utf-8"),
                          f"{p} must tell /add to read .add/.intent")

    def test_three_skill_trees_md5_equal(self):
        digests = {hashlib.md5(p.read_bytes()).hexdigest() for p in self._trees()}
        self.assertEqual(len(digests), 1, "the 3 SKILL.md trees must stay byte-identical (parity)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
