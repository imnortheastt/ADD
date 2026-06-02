#!/usr/bin/env python3
"""Structural proof of the v8 on-ramp change — the orientation block is AI-first.

The block `_guideline_block()` writes into CLAUDE.md/AGENTS.md is the agent's FIRST instruction
after install. v8 re-aims it from the manual phase-walk ("keep the `phase:` marker in sync via
`add.py phase`/`advance`, record the gate with `add.py gate`") to the AI-first flow: the `add`
skill drives intake -> milestone -> the one-approval front -> a self-driving run, and `add.py` is
the agent's hands, not the human's prescribed interface.

A load-bearing constraint is PRESERVED and asserted: the block stays a STABLE MINIMAL POINTER
(see add.py:198-201 — auto-loaded context measurably hurts). v8 re-aims the pointer; it does not
grow it into an always-loaded flow narrative.

HONEST SCOPE (same caveat as v6/v7): these tests prove the block's WORDS are AI-first as contracted
-- NOT that an agent actually runs the flow. Words-exist != method-works.

Run: python3 -m unittest test_v8_onramp -v
"""
import hashlib
import importlib.util
import re
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_REPO = _ADD_METHOD.parent

CANON_ADDPY = _TOOLING / "add.py"
DOGFOOD_ADDPY = _REPO / ".add" / "tooling" / "add.py"


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def _block() -> str:
    """Load the canonical add.py and render the orientation block it generates."""
    spec = importlib.util.spec_from_file_location("add_canon_v8", CANON_ADDPY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod._guideline_block()


class V8OnRampTest(unittest.TestCase):
    # --- parity: edits must land in both add.py trees ----------------------
    def test_addpy_parity(self):
        self.assertEqual(_md5(CANON_ADDPY), _md5(DOGFOOD_ADDPY),
                         "add.py differs between canonical and dogfood trees — v8 edit broke parity")

    # --- the block names the AI-first flow --------------------------------
    def test_block_names_ai_first_flow(self):
        low = _block().lower()
        self.assertIn("intake", low, "block must name intake (request -> milestone sizing)")
        self.assertIn("milestone", low, "block must name the milestone layer")
        self.assertTrue(re.search(r"one approval|one-approval|single approval", low),
                        "block must name the one-approval front")
        self.assertTrue(re.search(r"`?add`? skill|the add skill|skill drives", low),
                        "block must point at the `add` skill as the driver")

    # --- manual-only framing is gone --------------------------------------
    def test_block_drops_manual_only_framing(self):
        low = _block().lower()
        # the human must not be told to hand-walk phases via the add.py subcommands
        self.assertNotIn("add.py phase", low,
                         "block still prescribes `add.py phase`/`advance` to the human (manual_only_framing)")
        self.assertNotIn("add.py gate", low,
                         "block still tells the human to record the gate by hand (manual_only_framing)")
        self.assertNotIn("marker in sync", low,
                         "block still tells the human to keep the phase marker in sync (manual_only_framing)")

    # --- it stays a stable minimal pointer (not bloated) ------------------
    def test_block_stays_a_pointer(self):
        block = _block()
        self.assertIn(".add/docs/", block, "block must still point at the book (.add/docs/)")
        # honor add.py:198-201 — a pointer, not an always-loaded flow narrative
        body_lines = [ln for ln in block.splitlines() if ln.strip()]
        self.assertLessEqual(len(body_lines), 22,
                             f"block bloated to {len(body_lines)} non-blank lines — it must stay a pointer")


if __name__ == "__main__":
    unittest.main(verbosity=2)
