#!/usr/bin/env python3
"""Red-first tests for global-first-scope (installer-smarts task 3).

Contract FROZEN @ v1: an INTERACTIVE scope step recommends "Global home + this
project" (▶ default, with a one-line why) but requires an explicit pick. Global stays
STRICTLY ADDITIVE (the per-project drop always runs); CI / --yes / pipes never see the
prompt and stay project-only (byte-identical boundary); an already-passed --global is
honored, not re-asked; a cancel writes NOTHING (exit 130). add.py is never edited.

Hermetic: the pip interactive path is driven in-process by monkeypatching input() +
the ADD_INSTALLER_FORCE_INTERACTIVE seam, with home/HOME injected via the env hook
(reusing test_global_install's pattern). npm uses the exported pure seam (node harness)
+ a subprocess --yes run; the clack happy-path pick is PTY/manual per the established
convention.

Run: python3 -m unittest test_global_scope -v
"""
import contextlib
import io
import json
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

from test_installer_prompts import NODE, CLI_JS
from test_global_install import _make_bundled
from test_readiness_detect import _node_detect


class _Script:
    """A scripted stand-in for input(): pops responses in order, records prompts.
    A BaseException subclass in the list is raised (EOF/Ctrl-C). When EXHAUSTED it raises
    EOFError — modelling a closed stdin, so a trailing OPTIONAL prompt (e.g. the intent step)
    simply skips. To assert a prompt was SKIPPED, check it is absent from `prompts`."""

    def __init__(self, responses):
        self.responses = list(responses)
        self.prompts = []

    def __call__(self, prompt=""):
        self.prompts.append(prompt)
        if not self.responses:
            raise EOFError("scripted input exhausted (prompt=%r)" % prompt)
        r = self.responses.pop(0)
        if isinstance(r, type) and issubclass(r, BaseException):
            raise r()
        return r


class _PipScopeBase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="gscope-"))
        self.bundled = _make_bundled(self.tmp / "pkg")
        self.home = self.tmp / "home"          # ADD_HOME
        self.userhome = self.tmp / "user"      # HOME (for ~/.claude/skills/add)
        self.userhome.mkdir()
        self.proj = self.tmp / "proj"
        self.proj.mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _env(self):
        return {"ADD_HOME": str(self.home), "HOME": str(self.userhome)}

    def _interactive(self, responses, **kw):
        """Drive install() through the interactive path in-process (FORCE seam + scripted
        input + injected hermetic home). Returns (exit_code, script, stdout)."""
        script = _Script(responses)
        prev = os.environ.get("ADD_INSTALLER_FORCE_INTERACTIVE")
        os.environ["ADD_INSTALLER_FORCE_INTERACTIVE"] = "1"
        try:
            with mock.patch("builtins.input", script), \
                    contextlib.redirect_stdout(io.StringIO()) as out:
                code = _installer.install(
                    target=str(self.proj), bundled=str(self.bundled),
                    non_interactive=False, env=self._env(), **kw)
        finally:
            if prev is None:
                os.environ.pop("ADD_INSTALLER_FORCE_INTERACTIVE", None)
            else:
                os.environ["ADD_INSTALLER_FORCE_INTERACTIVE"] = prev
        return code, script, out.getvalue()

    def _home_created(self):
        return (self.home / "registry.json").exists()

    def _proj_dropped(self):
        return (self.proj / ".add" / "tooling" / "add.py").exists()


# --- the pure recommendation seam -------------------------------------------

class PipScopeOptionsTest(unittest.TestCase):
    def test_recommends_global_with_a_why(self):
        opts = _installer._scope_options()
        by_value = {o["value"]: o for o in opts}
        self.assertIn("global", by_value)
        self.assertIn("project", by_value)
        self.assertTrue(by_value["global"]["recommended"], "global must be the recommended pick")
        self.assertFalse(by_value["project"].get("recommended", False),
                         "project-only is the alternative, not the recommended default")
        self.assertTrue(by_value["global"].get("hint"), "the recommended pick must carry a one-line why")


# --- the interactive scope step (additive / project-only / cancel) ----------

class PipInteractiveScopeTest(_PipScopeBase):
    def test_pick_global_is_additive(self):                       # global creates home AND drops
        code, script, _out = self._interactive(["", ""])          # target Enter, scope Enter = global
        self.assertEqual(code, 0)
        self.assertTrue(self._home_created(), "picking global must create the shared home + registry")
        self.assertTrue((self.userhome / ".claude" / "skills" / "add" / "SKILL.md").exists(),
                        "global must also install the skill to ~/.claude/skills/add")
        self.assertTrue(self._proj_dropped(), "global is ADDITIVE — the per-project drop still runs")
        self.assertTrue(any("global" in p.lower() or "home" in p.lower() for p in script.prompts),
                        "the scope step must actually prompt about the global home")

    def test_pick_project_only_leaves_home_untouched(self):
        code, _script, _out = self._interactive(["", "n"])        # target Enter, scope 'n' = project only
        self.assertEqual(code, 0)
        self.assertFalse(self._home_created(), "project-only must NOT create the global home")
        self.assertFalse(self.home.exists(), "no global home dir at all on project-only")
        self.assertTrue(self._proj_dropped(), "the per-project drop still runs")

    def test_cancel_at_scope_writes_nothing(self):                # Reject: scope_cancel_writes_nothing
        code, _script, _out = self._interactive(["", EOFError])   # target Enter, then cancel at scope
        self.assertEqual(code, 130, "a scope cancel must exit 130")
        self.assertFalse(self._home_created(), "a cancel must not create the global home")
        self.assertFalse((self.proj / ".add").exists(), "a cancel must write nothing to the project")


# --- the invariants: non-interactive never global, explicit flag not re-asked ---

class PipScopeInvariantsTest(_PipScopeBase):
    def test_noninteractive_never_global(self):                   # Reject: noninteractive_never_global
        code = _installer.install(target=str(self.proj), bundled=str(self.bundled),
                                  non_interactive=True, env=self._env())   # no FORCE, no flag
        self.assertEqual(code, 0)
        self.assertFalse(self.home.exists(), "a non-interactive run must never auto-create the home")
        self.assertTrue(self._proj_dropped(), "non-interactive still drops the per-project files")

    def test_explicit_global_flag_skips_scope_prompt(self):       # Reject: explicit_flag_not_reasked
        # as_global already True -> the scope prompt must be SKIPPED. Only the target prompt may
        # read input(); if _prompt_scope is wrongly called the _Script raises on the empty list.
        code, script, _out = self._interactive([""], as_global=True)   # ONLY the target response
        self.assertEqual(code, 0)
        self.assertTrue(self._home_created(), "an explicit --global must still create the home")
        # with --global already set the SCOPE prompt must be skipped (only target + the optional
        # intent step run) — assert the scope question (its distinctive "global ADD home" text)
        # is absent, not a raw call count.
        self.assertFalse(any("global ADD home" in p for p in script.prompts),
                         "with --global already set, the scope prompt must be skipped")


# --- npm twin: the pure seam (node harness) + the non-interactive invariant --

@unittest.skipUnless(NODE, "node not on PATH — honest skip")
class NpmScopeOptionsTest(unittest.TestCase):
    def test_recommends_global(self):
        opts = _node_detect("m.scopeOptions()")
        by_value = {o["value"]: o for o in opts}
        self.assertIn("global", by_value)
        self.assertIn("project", by_value)
        self.assertTrue(by_value["global"]["recommended"], "global must be the recommended pick")
        self.assertTrue(by_value["global"].get("hint"), "the recommended pick must carry a one-line why")


@unittest.skipUnless(NODE, "node not on PATH — honest skip")
class NpmNonInteractiveNeverGlobalTest(unittest.TestCase):
    def test_yes_run_never_creates_home(self):
        tmp = Path(tempfile.mkdtemp(prefix="gscope-npm-"))
        try:
            home = tmp / "home"
            userhome = tmp / "user"; userhome.mkdir()
            proj = tmp / "proj"; proj.mkdir()
            env = {**os.environ, "ADD_HOME": str(home), "HOME": str(userhome)}
            res = subprocess.run([NODE, str(CLI_JS), "init", "--yes", str(proj)],
                                 capture_output=True, text=True, env=env, timeout=60)
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertFalse(home.exists(), "a --yes run must never auto-create the global home")
            self.assertNotIn("Global home", res.stdout, "no scope line on the non-interactive path")
            self.assertTrue((proj / ".add" / "tooling" / "add.py").exists(),
                            "the per-project drop still runs")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
