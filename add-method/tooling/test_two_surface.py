#!/usr/bin/env python3
"""Doc-gate for the State/Story two-surface architecture (task: state-story-architecture).

The shipped book is the artifact under test. We assert it names the two doc
surfaces and reconciles the loop-back rule with the strict-order rule — the
frozen vocabulary from the task CONTRACT. Run: python3 -m unittest test_two_surface -v
"""
import unittest
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / "docs"
PRINCIPLES = DOCS / "01-principles.md"
FLOW = DOCS / "02-the-flow.md"


class TwoSurfaceDocGateTest(unittest.TestCase):
    def test_principles_names_two_surfaces(self):
        # case-insensitive: the CONTRACT freezes that the *term* appears, not its
        # casing in prose (a term at a sentence start is capitalised).
        text = PRINCIPLES.read_text(encoding="utf-8").lower()
        for term in ("state surface", "story surface", "never auto-loaded"):
            self.assertIn(term, text, f"01-principles.md must name: {term!r}")

    def test_flow_reconciles_loopback_and_order(self):
        text = FLOW.read_text(encoding="utf-8").lower()
        for term in ("backward correction", "forward-skipping"):
            self.assertIn(term, text, f"02-the-flow.md must state: {term!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
