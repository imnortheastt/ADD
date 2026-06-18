#!/usr/bin/env python3
"""Red-first tests for readiness-and-detect (installer-smarts task 2).

Contract FROZEN @ v1: an ADDITIVE enriched detector (env > CLAUDE.md-in-target >
installed-CLI > generic) seeds the INTERACTIVE agent default only; the env-only
detector AND the non-interactive write are unchanged (byte-identical boundary,
test_agent_detect pin). A fail-soft readiness line (git · python3 · agent) renders
on the interactive path only. Every probe is a PATH/file lookup (no spawn) and is
INJECTABLE (a `which` seam) so the dev machine's installed agents don't pollute tests.

Run: python3 -m unittest test_readiness_detect -v
"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_SRC = _TOOLING.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
from add_method import _installer            # noqa: E402

from test_installer_prompts import _run_pip, _brain_landed, NODE, CLI_JS


def _node_detect(expr):
    """Read a JSON value from a cli.js export by running it through node's script flag.
    The script string is fully test-controlled (no external input) — a hermetic harness
    for the npm twin, the JS analog of importing _installer for the pip twin."""
    script = "const m=require(%s); process.stdout.write(JSON.stringify(%s));" % (
        json.dumps(str(CLI_JS)), expr)
    r = subprocess.run([NODE, "-e", script], capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        raise AssertionError("node harness failed: " + r.stderr)
    return json.loads(r.stdout)


# --- pip enriched detector (hermetic; which is injected) -------------------------

class PipEnrichedDetectTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="rd-pip-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_env_signal_wins(self):
        (self.tmp / "AGENTS.md").write_text("x")            # file + cli would say otherwise
        p = _installer._detect_agent_enriched(
            {"CLAUDECODE": "1"}, self.tmp, which=lambda c: "/b/" + c)
        self.assertEqual(p["id"], "claude", "env signal must win over file + CLI")

    def test_file_signal_with_no_env(self):
        (self.tmp / "CLAUDE.md").write_text("x")
        p = _installer._detect_agent_enriched({}, self.tmp, which=lambda c: None)
        self.assertEqual(p["id"], "claude", "CLAUDE.md in target is the claude signal")
        self.assertEqual(_installer._detect_agent({})["id"], "generic",
                         "the env-only detector must stay generic (the pin)")

    def test_cli_signal_with_no_env_no_file(self):
        p = _installer._detect_agent_enriched(
            {}, self.tmp, which=lambda c: "/b/codex" if c == "codex" else None)
        self.assertEqual(p["id"], "codex", "an installed agent CLI is the machine signal")

    def test_generic_fallback_never_raises(self):
        p = _installer._detect_agent_enriched({}, self.tmp, which=lambda c: None)
        self.assertEqual(p["id"], "generic")

    def test_ambiguous_agents_md_does_not_pick(self):
        (self.tmp / "AGENTS.md").write_text("x")            # shared by codex/opencode/generic
        p = _installer._detect_agent_enriched({}, self.tmp, which=lambda c: None)
        self.assertEqual(p["id"], "generic", "AGENTS.md alone must not pick a specific agent")

    def test_probe_failure_reads_as_absent(self):
        def boom(_c):
            raise OSError("which exploded")
        p = _installer._detect_agent_enriched({}, self.tmp, which=boom)
        self.assertEqual(p["id"], "generic", "a throwing probe must read as absent, never crash")


# --- pip readiness line (hermetic) ----------------------------------------------

class PipReadinessLineTest(unittest.TestCase):
    def test_line_names_git_python3_and_agent(self):
        tmp = Path(tempfile.mkdtemp(prefix="rd-pip-"))
        try:
            line = _installer._readiness_line(
                {}, tmp, which=lambda c: "/b/" + c if c in ("git", "python3") else None)
            self.assertIn("git", line)
            self.assertIn("python3", line)
            self.assertIn("agent", line.lower())
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_line_is_fail_soft_on_a_throwing_probe(self):
        tmp = Path(tempfile.mkdtemp(prefix="rd-pip-"))
        try:
            def boom(_c):
                raise OSError("nope")
            line = _installer._readiness_line({}, tmp, which=boom)   # must not raise
            self.assertIn("git", line)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


# --- npm enriched detector (hermetic, via cli.js exports) ------------------------

@unittest.skipUnless(NODE, "node not on PATH — honest skip")
class NpmEnrichedDetectTest(unittest.TestCase):
    def test_env_signal_wins(self):
        tmp = tempfile.mkdtemp(prefix="rd-npm-")
        out = _node_detect("m.detectAgentEnriched({CLAUDECODE:'1'}, %s, ()=>null).id" % json.dumps(tmp))
        self.assertEqual(out, "claude")

    def test_cli_signal(self):
        tmp = tempfile.mkdtemp(prefix="rd-npm-")
        out = _node_detect(
            "m.detectAgentEnriched({}, %s, (c)=>c==='codex'?'/b/codex':null).id" % json.dumps(tmp))
        self.assertEqual(out, "codex")

    def test_generic_and_env_only_detector_unchanged(self):
        tmp = tempfile.mkdtemp(prefix="rd-npm-")
        self.assertEqual(
            _node_detect("m.detectAgentEnriched({}, %s, ()=>null).id" % json.dumps(tmp)), "generic")
        self.assertEqual(_node_detect("m.detectAgent({}).id"), "generic",
                         "the env-only detectAgent must stay generic on empty env (the pin)")


# --- interactive-only behavior (subprocess) -------------------------------------

class ReadinessLineInteractiveOnlyTest(unittest.TestCase):
    def test_pip_interactive_shows_readiness(self):
        with tempfile.TemporaryDirectory(prefix="rd-pip-") as tmp:
            res = _run_pip(["init"], cwd=tmp, stdin="\nn\n",   # target Enter, then project-only scope
                           env_extra={"ADD_INSTALLER_FORCE_INTERACTIVE": "1"})
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertIn("Pre-flight", res.stdout + res.stderr,
                          "the interactive path must show the readiness pre-flight line")

    def test_pip_noninteractive_hides_readiness(self):
        with tempfile.TemporaryDirectory(prefix="rd-pip-") as tmp:
            res = _run_pip(["init"], cwd=tmp)
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertNotIn("Pre-flight", res.stdout + res.stderr,
                             "the non-interactive path must NOT show the readiness line")
            self.assertTrue(_brain_landed(Path(tmp)))


# --- non-interactive write stays env-only (the boundary) ------------------------

class NonInteractiveEnvOnlyWriteTest(unittest.TestCase):
    def test_claude_md_does_not_flip_the_noninteractive_write(self):
        with tempfile.TemporaryDirectory(prefix="rd-pip-") as tmp:
            # CLAUDE.md present but NO agent env + --yes: env-only detection => generic =>
            # writes AGENTS.md. If enriched detection wrongly ran here it would pick claude
            # (from CLAUDE.md) and write NO AGENTS.md.
            (Path(tmp) / "CLAUDE.md").write_text("# pre-existing user file\n")
            # strip any agent env the host shell leaks (this very session sets CLAUDECODE),
            # so env-only detection genuinely resolves to generic here.
            clear_env = {k: "" for k in ("CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT",
                                         "CODEX_HOME", "OPENCODE")}
            res = _run_pip(["init", "--yes"], cwd=tmp, env_extra=clear_env)
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertTrue(
                (Path(tmp) / "AGENTS.md").exists(),
                "non-interactive write must use env-only detection (generic -> AGENTS.md)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
