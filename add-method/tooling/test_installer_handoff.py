#!/usr/bin/env python3
"""Tests for the flagless installer handoff (v15 installer-handoff).

Behavioral pins for what v12 shipped as words (a flagless install that lands
the brain and hands off to /add) plus the v15 delta: the manual-init escape
hint drops the flags the user never typed — the engine already infers the
name and defaults the stage, so the hint shows the shortest TRUE command.
The npx-side tests skip honestly when `node` is absent (the npm-gated
precedent in test_packaging).
Run: python3 -m unittest test_installer_handoff -v
"""
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PKG_ROOT = Path(__file__).resolve().parent.parent          # add-method/
REPO_ROOT = PKG_ROOT.parent
CLI_JS = PKG_ROOT / "bin" / "cli.js"
README = PKG_ROOT / "README.md"
SRC_DIR = PKG_ROOT / "src"

NODE = shutil.which("node")

ENGINE_MD5 = "1f838fad76393aaad5a5779f5d1dd788"
ENGINE_PATHS = (
    PKG_ROOT / "tooling" / "add.py",
    REPO_ROOT / ".add" / "tooling" / "add.py",
    PKG_ROOT / "src" / "add_method" / "_bundled" / "tooling" / "add.py",
)


def _run_node_init(extra=(), cwd=None):
    return subprocess.run(
        [NODE, str(CLI_JS), "init", *extra],
        cwd=cwd, capture_output=True, text=True, timeout=120)


def _run_pip_init(extra=(), cwd=None):
    env = dict(os.environ)
    env["PYTHONPATH"] = str(SRC_DIR) + os.pathsep + env.get("PYTHONPATH", "")
    code = ("import sys; from add_method._cli import main; "
            "sys.exit(main(sys.argv[1:]))")
    return subprocess.run(
        [sys.executable, "-c", code, "init", *extra],
        cwd=cwd, capture_output=True, text=True, timeout=120, env=env)


def _assert_brain_landed(tc, root: Path, out: str):
    tc.assertTrue((root / ".claude" / "skills" / "add" / "SKILL.md").exists(),
                  "skill tree missing after flagless install")
    tc.assertTrue((root / ".add" / "tooling" / "add.py").exists(),
                  "tooling missing after flagless install")
    tc.assertTrue(any((root / ".add" / "docs").glob("*.md")),
                  "book missing after flagless install")
    tc.assertFalse((root / ".add" / "state.json").exists(),
                   "installer must NEVER run init — no state.json")
    low = out.lower()
    tc.assertIn("open claude code", low,
                "the final output must hand off to the conversation")
    tc.assertIn("/add", out, "the handoff names /add")


def _hint_line(out: str) -> str:
    """The manual-init escape-hint line (must exist — a shipped guard pins
    --await-lock in the closing hint)."""
    for ln in out.splitlines():
        if "init --await-lock" in ln:
            return ln
    raise AssertionError("no manual-init hint line containing 'init --await-lock'")


@unittest.skipUnless(NODE, "node not on PATH — npx-side install check skipped (honest skip)")
class NpxFlaglessTest(unittest.TestCase):
    def test_npx_flagless_install_behavioral(self):
        with tempfile.TemporaryDirectory(prefix="add-npx-") as tmp:
            res = _run_node_init(cwd=tmp)
            self.assertEqual(res.returncode, 0,
                             f"flagless npx init failed:\n{res.stderr}")
            _assert_brain_landed(self, Path(tmp), res.stdout)

    def test_npx_flagless_hint_drops_flags(self):
        with tempfile.TemporaryDirectory(prefix="add-npx-") as tmp:
            res = _run_node_init(cwd=tmp)
            self.assertEqual(res.returncode, 0, res.stderr)
            hint = _hint_line(res.stdout)
            self.assertNotIn("--stage", hint,
                             "flagless install must not echo a --stage the "
                             "user never typed (the engine defaults it)")
            self.assertNotIn("--name", hint,
                             "flagless install must not echo a --name the "
                             "user never typed (the engine infers it)")

    def test_explicit_flags_echo_into_hint(self):
        with tempfile.TemporaryDirectory(prefix="add-npx-") as tmp:
            res = _run_node_init(("--name", "Acme", "--stage", "mvp"), cwd=tmp)
            self.assertEqual(res.returncode, 0, res.stderr)
            hint = _hint_line(res.stdout)
            self.assertIn("--stage mvp", hint,
                          "an explicitly chosen stage still echoes into the hint")
            self.assertIn('--name "Acme"', hint,
                          "an explicitly chosen name still echoes into the hint")

    def test_missing_flag_value_fails(self):
        # in-build STRENGTHENING amendment (disclosed at the gate): a trailing
        # `--stage` with no value must fail loudly, matching the pip twin's
        # argparse error — never silently drop the flag the user tried to pass
        with tempfile.TemporaryDirectory(prefix="add-npx-") as tmp:
            res = _run_node_init(("--stage",), cwd=tmp)
            self.assertNotEqual(res.returncode, 0,
                                "npx init --stage (no value) must fail, not "
                                "silently ignore the flag")


class PipFlaglessTest(unittest.TestCase):
    def test_pip_flagless_install_behavioral(self):
        with tempfile.TemporaryDirectory(prefix="add-pip-") as tmp:
            res = _run_pip_init(cwd=tmp)
            self.assertEqual(res.returncode, 0,
                             f"flagless pip init failed:\n{res.stderr}")
            _assert_brain_landed(self, Path(tmp), res.stdout)

    def test_pip_flagless_hint_drops_flags(self):
        with tempfile.TemporaryDirectory(prefix="add-pip-") as tmp:
            res = _run_pip_init(cwd=tmp)
            self.assertEqual(res.returncode, 0, res.stderr)
            hint = _hint_line(res.stdout)
            self.assertNotIn("--stage", hint,
                             "flagless pip install must not echo --stage")
            self.assertNotIn("--name", hint,
                             "flagless pip install must not echo --name")

    def test_missing_flag_value_fails(self):
        # twin of the npx-side strengthening amendment: argparse already
        # enforces this — the test pins the parity so neither side regresses
        with tempfile.TemporaryDirectory(prefix="add-pip-") as tmp:
            res = _run_pip_init(("--stage",), cwd=tmp)
            self.assertNotEqual(res.returncode, 0,
                                "pip init --stage (no value) must fail")


class ReadmeFlaglessTest(unittest.TestCase):
    def test_readme_install_examples_flagless_first(self):
        text = README.read_text(encoding="utf-8")
        self.assertRegex(
            text, re.compile(r"^npx @pilotspace/add init\s*$", re.M),
            "README's npx install example must lead with the flagless form")
        self.assertRegex(
            text, re.compile(r"^pilotspace-add init\s*$", re.M),
            "README's pip install example must lead with the flagless form")


class EnginePinTest(unittest.TestCase):
    def test_engine_untouched(self):
        for p in ENGINE_PATHS:
            self.assertTrue(p.exists(), f"missing engine copy: {p}")
            digest = hashlib.md5(p.read_bytes()).hexdigest()
            self.assertEqual(
                digest, ENGINE_MD5,
                f"{p} changed — the installer handoff never edits the engine")


if __name__ == "__main__":
    unittest.main(verbosity=2)
