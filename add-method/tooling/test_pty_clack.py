#!/usr/bin/env python3
"""PTY-driven CI coverage for the npm clack interactive installer (installer-smarts-polish · pty-clack-harness).

The clack TUI can only be reached through a REAL pseudo-terminal: runClackPreamble short-circuits
to `cancelled` when `process.stdin.isTTY` is false (cli.js:322), so the piped force-seam used by
test_installer_prompts never reaches the prompts. These tests drive the real keystroke flow through
the shared `pty_clack` helper (stdlib pty — no new dependency), closing the gap the installer-smarts
gates disclosed as PTY-only-reachable: the agent-select step (D8) + the happy-path prompt sequence.

Contract: TASK pty-clack-harness §3 (FROZEN @ v1). Honest-skips when node or a POSIX pty is absent.

Run: python3 -m unittest test_pty_clack -v
"""
import os
import tempfile
import unittest
from pathlib import Path

# The single-source PTY helper this task builds (RED until pty_clack.py exists).
from pty_clack import drive_clack, PtyRun, PtyTimeout, ENTER, DOWN, UP, CANCEL, NODE, PTY_SUPPORTED
# Reuse the existing drop/cancel observers rather than re-implementing them (single source).
from test_installer_prompts import _brain_landed, _nothing_written

# clack prompt markers (message substrings the harness waits on before each keystroke).
M_TARGET = "which directory"      # text: "Install ADD into which directory?"
M_CONFIRM = "Write the ADD skill"  # confirm: "Write the ADD skill + tooling + book here?"
M_SCOPE = "Install scope"          # select: "Install scope?"
M_AGENT = "which agent"            # select: "Set up for which agent? (detected: …)"
M_INTENT = "build first"           # text:  "What do you want to build first?"

# accept target -> confirm write -> scope=project (DOWN off the global default) -> agent -> skip intent
_DRIVE_TO_DONE = [
    (M_TARGET, ENTER),
    (M_CONFIRM, ENTER),
    (M_SCOPE, DOWN + ENTER),   # pick "This project only" — keeps the install self-contained
    (M_AGENT, ENTER),
    (M_INTENT, ENTER),
]

_REQUIRES = unittest.skipUnless(NODE, "node not on PATH (node_unavailable — honest skip)")
_REQUIRES_PTY = unittest.skipUnless(PTY_SUPPORTED, "POSIX pty unavailable (pty_unavailable — honest skip)")


@_REQUIRES
@_REQUIRES_PTY
class ClackHappyPathTest(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory(prefix="pty-happy-")
        self.target = Path(self._td.name)
        self._home = tempfile.TemporaryDirectory(prefix="pty-home-")  # sandbox any global write

    def tearDown(self):
        self._td.cleanup()
        self._home.cleanup()

    def test_happy_path_drops_brain(self):
        run = drive_clack(["init"], _DRIVE_TO_DONE, cwd=self.target,
                          env_extra={"HOME": self._home.name})
        self.assertIsInstance(run, PtyRun)
        self.assertEqual(run.exit_code, 0, run.output)
        self.assertTrue(_brain_landed(self.target),
                        "accepting the clack prompts must drop the brain into the target")
        # every prompt in the sequence must have RENDERED — proves all five keystrokes drove a
        # real prompt, not that the flow short-circuited after the confirm.
        for marker in (M_TARGET, M_CONFIRM, M_SCOPE, M_AGENT, M_INTENT):
            self.assertIn(marker, run.output, f"the {marker!r} prompt must have rendered")
        # the DOWN at the scope select must have actually picked project-only: a global pick would
        # write .add into HOME. Its absence proves the keystroke landed (not silently absorbed).
        self.assertFalse((Path(self._home.name) / ".add").exists(),
                         "project-only scope must write nothing under HOME (the global home)")


@_REQUIRES
@_REQUIRES_PTY
class ClackAgentOverrideTest(unittest.TestCase):
    """D8: the agent SELECT is keystroke-navigable — override the detected default."""

    def setUp(self):
        self._td = tempfile.TemporaryDirectory(prefix="pty-override-")
        self.target = Path(self._td.name)
        self._home = tempfile.TemporaryDirectory(prefix="pty-home-")

    def tearDown(self):
        self._td.cleanup()
        self._home.cleanup()

    def test_agent_override_writes_codex(self):
        # CLAUDECODE=1 is the AUTHORITATIVE env signal -> detected default = claude (index 0),
        # deterministic regardless of which agent CLIs sit on the machine's PATH.
        steps = [
            (M_TARGET, ENTER),
            (M_CONFIRM, ENTER),
            (M_SCOPE, DOWN + ENTER),     # project-only
            (M_AGENT, DOWN + ENTER),     # claude -> codex (the override keystroke)
            (M_INTENT, ENTER),
        ]
        run = drive_clack(["init"], steps, cwd=self.target,
                          env_extra={"HOME": self._home.name, "CLAUDECODE": "1"})
        self.assertEqual(run.exit_code, 0, run.output)
        agents_md = self.target / "AGENTS.md"
        self.assertTrue(agents_md.exists(), "the overridden codex agent must write AGENTS.md")
        # codex's agent-specific next_step text pins the pick (vs generic / opencode, which also use AGENTS.md)
        self.assertIn("Codex", agents_md.read_text(encoding="utf-8"))
        self.assertFalse((self.target / "CLAUDE.md").exists(),
                         "the detected claude pointer must NOT be written once overridden")
        self.assertTrue(_brain_landed(self.target),
                        "an override changes which agent profile, not whether the brain drops")


@_REQUIRES
@_REQUIRES_PTY
class ClackCancelTest(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory(prefix="pty-cancel-")
        self.target = Path(self._td.name)

    def tearDown(self):
        self._td.cleanup()

    def test_cancel_writes_nothing(self):
        # Ctrl-C at the confirm prompt -> clack.isCancel -> runClackPreamble returns cancelled
        # -> cmdInit exits 130 BEFORE any write.
        run = drive_clack(["init"], [(M_TARGET, ENTER), (M_CONFIRM, CANCEL)], cwd=self.target)
        self.assertEqual(run.exit_code, 130, "user_cancelled is the 130 exit contract (cli.js:435)")
        self.assertTrue(_nothing_written(self.target),
                        "a cancel before the write must leave the target untouched")


@_REQUIRES
@_REQUIRES_PTY
class ClackTimeoutTest(unittest.TestCase):
    """The harness must FAIL fast, never hang the suite, and never orphan the child."""

    def setUp(self):
        self._td = tempfile.TemporaryDirectory(prefix="pty-timeout-")
        self.target = Path(self._td.name)

    def tearDown(self):
        self._td.cleanup()

    def test_prompt_timeout_raises(self):
        with self.assertRaises(PtyTimeout) as ctx:
            drive_clack(["init"], [("THIS_MARKER_NEVER_RENDERS", ENTER)],
                        cwd=self.target, read_timeout=2.0, exit_timeout=5.0)
        self.assertEqual(ctx.exception.code, "prompt_timeout")

    def test_child_timeout_raises(self):
        # stop after the first prompt -> child waits forever at the confirm -> child never exits
        with self.assertRaises(PtyTimeout) as ctx:
            drive_clack(["init"], [(M_TARGET, ENTER)],
                        cwd=self.target, read_timeout=5.0, exit_timeout=2.0)
        self.assertEqual(ctx.exception.code, "child_timeout")


class HelperReuseTest(unittest.TestCase):
    """`reusable` Must: ONE importable helper, the PTY allocation lives only there (no copy-paste)."""

    def test_single_source_helper(self):
        import pty_clack
        for name in ("drive_clack", "PtyRun", "PtyTimeout", "ENTER", "DOWN", "UP",
                     "CANCEL", "NODE", "PTY_SUPPORTED"):
            self.assertTrue(hasattr(pty_clack, name), f"pty_clack must export {name}")
        # single source: the drive_clack the tests call IS the one defined in the helper module
        # (no per-test re-implementation), and the PTY allocation lives there, not in a test.
        self.assertIs(drive_clack, pty_clack.drive_clack)
        self.assertEqual(drive_clack.__module__, "pty_clack")
        # the allocation primitive (assembled so this literal never appears verbatim here) lives
        # only in the helper — proving the tests drive THROUGH it, not around it.
        needle = "os." + "openpty("
        self.assertIn(needle, Path(pty_clack.__file__).read_text(encoding="utf-8"))
        self.assertNotIn(needle, Path(__file__).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
