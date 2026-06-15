#!/usr/bin/env python3
"""Content + parity guard for setup proposing the first milestone (task
setup-suggest-milestone, v13-onboarding-polish 3/6).

phases/0-setup.md §3 "Size the first milestone" must instruct setup to PROPOSE the
first milestone as a kickoff suggestion (goal + flow + scenarios), show-before-ask
(the human reacts; setup does not auto-create), drawing on scope.md. 3 trees identical.

Assertions scope to the NEW proposal region (anchored on the unique marker "kickoff")
so the suite is genuinely red before build — pre-existing words like "flow"/"propose"
from the Run-mode section must NOT satisfy it. Run: python3 -m unittest test_setup_suggest_milestone -v
"""
from __future__ import annotations

import hashlib
import unittest
from pathlib import Path

ADD_METHOD = Path(__file__).resolve().parent.parent
REPO = ADD_METHOD.parent
CANONICAL = ADD_METHOD / "skill" / "add"
BUNDLED = ADD_METHOD / "src" / "add_method" / "_bundled" / "skill" / "add"
DOGFOOD = REPO / ".claude" / "skills" / "add"
SETUP = "phases/0-setup.md"


def _read(tree: Path, rel: str) -> str:
    return (tree / rel).read_text(encoding="utf-8")


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


class SuggestMilestone(unittest.TestCase):
    def setUp(self):
        self.setup = _read(CANONICAL, SETUP)
        # the proposal region: from the unique marker "kickoff" to the next ~900 chars
        self.assertIn("kickoff", self.setup.lower(),
                      "§3 must gain a first-milestone PROPOSAL marked as a 'kickoff' suggestion")
        i = self.setup.lower().index("kickoff")
        self.region = self.setup[i: i + 900].lower()

    def test_proposes_first_milestone_before_drafting(self):
        self.assertTrue("propose" in self.region or "suggest" in self.region)
        self.assertIn("first milestone", self.region)

    def test_proposal_has_goal_flow_scenarios(self):
        for part in ("goal", "flow", "scenario"):
            self.assertIn(part, self.region, f"the kickoff proposal must name '{part}'")

    def test_show_before_ask_human_reacts(self):
        self.assertIn("react", self.region,
                      "the human must REACT to the proposal (show-before-ask, not auto-create)")

    def test_cites_scope_md(self):
        self.assertIn("scope.md", self.region)

    def test_three_trees_byte_identical(self):
        digests = {_md5(t / SETUP) for t in (CANONICAL, BUNDLED, DOGFOOD)}
        self.assertEqual(len(digests), 1, "0-setup.md diverged across the 3 skill trees")


if __name__ == "__main__":
    unittest.main()
