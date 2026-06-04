#!/usr/bin/env python3
"""Structural proof of the v8 install on-ramp — the installer greets AI-first, and the brain is bundled.

After `npx @pilotspace/add init`, the first thing a user reads is the installer's next-hint. v8 re-aims it
from bare `new-task` (CLI-first, skips intake) to the AI-first entry: open Claude Code, run `/add`,
describe what to build; the agent runs intake -> milestone -> one-approval.

A load-bearing invariant is GUARDED (not added — it already works): `bin/cli.js` copies the skill into
`.claude/skills/add/` and the book into `.add/docs/`, and package.json ships both. The orientation
block (agent-orientation-block) now PROMISES "the `add` skill drives the flow" — so the skill must be
present after install. This guard fails if that bundling ever regresses.

HONEST SCOPE (same caveat as v6/v7/v8-onramp): these tests prove the installer's WORDS + file ops are
as contracted -- NOT that a user actually follows the AI-first entry. Words-exist != method-works.

Run: python3 -m unittest test_v8_install -v
"""
import json
import re
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent

CLI_JS = _ADD_METHOD / "bin" / "cli.js"
PACKAGE_JSON = _ADD_METHOD / "package.json"
ADD_PY = _TOOLING / "add.py"
INSTALLER_PY = _ADD_METHOD / "src" / "add_method" / "_installer.py"


def _cli() -> str:
    return CLI_JS.read_text(encoding="utf-8")


def _installer_py() -> str:
    return INSTALLER_PY.read_text(encoding="utf-8")


def _closing_hint(text: str) -> str:
    """The tail of cmdInit — where the next-hint lives (after the 'Done.' line)."""
    idx = text.rfind("Done.")
    return text[idx:] if idx != -1 else text


class V8InstallTest(unittest.TestCase):
    # --- the cli.js next-hint is AI-first ----------------------------------
    def test_cli_next_hint_is_ai_first(self):
        hint = _closing_hint(_cli()).lower()
        self.assertIn("/add", hint, "cli.js closing hint must point at the `/add` conversational entry")
        self.assertTrue(re.search(r"intake|milestone|what.{0,20}build|describe", hint),
                        "cli.js hint must frame the AI-first flow (describe what to build -> intake/milestone)")
        # bare new-task must not be the prescribed first user step
        self.assertNotIn("new-task", hint,
                         "cli.js hint still sends the user to bare `new-task` (newtask_first_hint)")

    # --- the add.py init next-hint is AI-first ------------------------------
    def test_init_next_hint_is_ai_first(self):
        # cmd_init prints a closing 'next:' line — find it in source
        src = ADD_PY.read_text(encoding="utf-8")
        m = re.search(r'next:\s*add\.py\s+new-task', src)
        self.assertIsNone(m, "add.py cmd_init still prints `next: add.py new-task` (newtask_first_hint)")
        # and it must positively name the AI-first entry
        self.assertTrue(re.search(r'/add|ask .*claude|start the add|describe what', src, re.IGNORECASE),
                        "add.py cmd_init closing print must name the AI-first entry")

    # --- the brain is bundled (GUARD the working behavior) ------------------
    def test_cli_bundles_brain(self):
        cli = _cli()
        self.assertTrue(re.search(r'"skill",\s*"add".*?\.claude.*?skills.*?add', cli, re.DOTALL),
                        "cli.js must copy the skill into .claude/skills/add/")
        self.assertTrue(re.search(r'"docs".*?\.add.*?docs', cli, re.DOTALL),
                        "cli.js must copy the book into .add/docs/")

    def test_package_ships_brain(self):
        files = json.loads(PACKAGE_JSON.read_text(encoding="utf-8")).get("files", [])
        joined = " ".join(files)
        self.assertIn("skill/", joined, "package.json `files` must ship the skill")
        self.assertIn("docs/", joined, "package.json `files` must ship the book")
        self.assertTrue(any("add.py" in f for f in files), "package.json `files` must ship add.py")

    # --- v12 installer-arm: installer drops files only, never auto-runs init -----
    # A pre-run plain `add.py init` writes no `setup` key -> grandfathered-locked
    # (add.py:_setup_locked), so the v12 lock-down gate never arms and the `brownfield:`
    # signal is printed in the terminal before `/add` ever runs. The installer must
    # therefore DROP FILES ONLY; the AI (via /add) or a CLI user runs `init --await-lock`.
    def test_cli_does_not_autorun_init(self):
        cli = _cli()
        self.assertNotIn("spawnSync", cli,
                         "cli.js still spawns a subprocess — install must be pure file-copy (no add.py init)")
        self.assertNotIn("initArgs", cli,
                         "cli.js still builds an `init` argv — it must not run add.py init")

    def test_installer_py_does_not_autorun_init(self):
        src = _installer_py()
        self.assertNotIn("mod.main(", src,
                         "_installer.py still execs add.py main() — it must not run add.py init")
        self.assertNotIn("init_argv", src,
                         "_installer.py still builds an `init` argv — it must not run add.py init")

    def test_cli_hint_offers_manual_init(self):
        hint = _closing_hint(_cli())
        self.assertIn("--await-lock", hint,
                      "cli.js closing hint must offer the manual `add.py init --await-lock` fallback")

    def test_installer_py_hint_offers_manual_init(self):
        hint = _closing_hint(_installer_py())
        self.assertIn("--await-lock", hint,
                      "_installer.py closing hint must offer the manual `add.py init --await-lock` fallback")


if __name__ == "__main__":
    unittest.main(verbosity=2)
