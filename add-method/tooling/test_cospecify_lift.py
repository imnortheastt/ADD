"""Guard the co-specify brainstorm rubric lifted to milestone + foundation altitudes.

Task: cospecify-lift (v5). The brainstorm move (Diverge -> Converge -> Validate)
defined at task §1 (skill/add/phases/1-specify.md) must also be taught at the
milestone altitude (scope.md) and the foundation altitude (phases/0-setup.md),
using the SAME lowest-confidence flag grammar, and all three shipped trees must stay
byte-identical.
"""
from __future__ import annotations

import unittest
from pathlib import Path

ADD_METHOD = Path(__file__).resolve().parent.parent          # .../add-method
REPO = ADD_METHOD.parent                                     # repo root

CANONICAL = ADD_METHOD / "skill" / "add"
BUNDLED = ADD_METHOD / "src" / "add_method" / "_bundled" / "skill" / "add"
LOCAL = REPO / ".claude" / "skills" / "add"

# The one notation, owned by phases/1-specify.md — every altitude reuses it verbatim.
FLAG_GRAMMAR = "⚠ <assumption> — lowest confidence because <why>; if wrong: <cost>"

SCOPE = "scope.md"
SETUP = "phases/0-setup.md"

MILESTONE_ANCHOR = "co-specify at milestone level"
DRAFTING_HEADING = "## Drafting a good MILESTONE.md"
SEED_LABELS = ["Outcome", "Edge of scope", "Riskiest seam", "Done-looks-like", "First slice"]

FOUNDATION_ANCHOR = "co-specify at foundation level"
LENS_LABELS = ["Domain (DDD)", "Spec (SDD)", "Users (UDD)", "Decisions"]


def _read(tree: Path, rel: str) -> str:
    return (tree / rel).read_text(encoding="utf-8")


class ScopeMilestoneBrainstorm(unittest.TestCase):
    """Scenario 1: scope.md teaches diverge-before-draft."""

    def test_anchor_present_and_before_drafting_section(self) -> None:
        text = _read(CANONICAL, SCOPE)
        self.assertIn(MILESTONE_ANCHOR, text)
        self.assertIn(DRAFTING_HEADING, text)
        self.assertLess(
            text.index(MILESTONE_ANCHOR),
            text.index(DRAFTING_HEADING),
            "brainstorm section must precede '## Drafting a good MILESTONE.md'",
        )

    def test_five_diverge_seeds_present(self) -> None:
        text = _read(CANONICAL, SCOPE)
        for label in SEED_LABELS:
            self.assertIn(label, text, f"missing diverge seed: {label}")

    def test_references_specify_guide(self) -> None:
        self.assertIn("phases/1-specify.md", _read(CANONICAL, SCOPE))


class SetupFoundationInterview(unittest.TestCase):
    """Scenario 2: 0-setup.md teaches the four-lens foundation interview."""

    def test_anchor_present(self) -> None:
        self.assertIn(FOUNDATION_ANCHOR, _read(CANONICAL, SETUP))

    def test_four_lenses_present(self) -> None:
        text = _read(CANONICAL, SETUP)
        for label in LENS_LABELS:
            self.assertIn(label, text, f"missing foundation lens: {label}")

    def test_references_specify_guide(self) -> None:
        self.assertIn("phases/1-specify.md", _read(CANONICAL, SETUP))


class FlagGrammarConsistent(unittest.TestCase):
    """Scenario 3: reject flag_grammar_drift — one notation across altitudes."""

    def test_both_guides_use_verbatim_flag(self) -> None:
        for rel in (SCOPE, SETUP):
            self.assertIn(
                FLAG_GRAMMAR,
                _read(CANONICAL, rel),
                f"{rel} must use the verbatim lowest-confidence flag grammar",
            )


class TreesIdentical(unittest.TestCase):
    """Scenario 4: reject tree_drift — canonical == bundled == local."""

    def test_bundled_matches_canonical(self) -> None:
        for rel in (SCOPE, SETUP):
            self.assertEqual(
                _read(BUNDLED, rel), _read(CANONICAL, rel), f"_bundled/{rel} drifted"
            )

    def test_local_mirror_matches_canonical(self) -> None:
        for rel in (SCOPE, SETUP):
            self.assertEqual(
                _read(LOCAL, rel), _read(CANONICAL, rel), f".claude/{rel} drifted"
            )


if __name__ == "__main__":
    unittest.main()
