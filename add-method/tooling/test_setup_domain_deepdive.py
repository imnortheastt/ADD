#!/usr/bin/env python3
"""Content + parity guard for the setup domain deep-dive step (task
setup-domain-deepdive, v13-onboarding-polish 4/6).

phases/0-setup.md must gain a "## 2c · Domain deep-dive" step that deepens domain
knowledge across MULTIPLE TURNS, one deep-dive per drive — DDD, SDD, UDD, TDD —
captures the user's ADRs into PROJECT.md Key Decisions, and under autonomy=auto
auto-completes all four drives in one pass (still flag-first) WITHOUT skipping the
human baseline approval (the lock).

Assertions scope to the NEW deep-dive region (anchored on the unique marker
"## 2c") so the suite is genuinely red before build — pre-existing §2b lens
vocabulary must NOT satisfy it. Run: python3 -m unittest test_setup_domain_deepdive -v
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


class DomainDeepDive(unittest.TestCase):
    def setUp(self):
        self.setup = _read(CANONICAL, SETUP)
        # the deep-dive region: from the unique marker "## 2c" to the next ~1400 chars
        self.assertIn("## 2c", self.setup,
                      "0-setup.md must gain a '## 2c · Domain deep-dive' step")
        i = self.setup.index("## 2c")
        self.region = self.setup[i: i + 1400]
        self.region_l = self.region.lower()

    def test_names_all_four_drives(self):
        for drive in ("DDD", "SDD", "UDD", "TDD"):
            self.assertIn(drive, self.region,
                          f"the deep-dive must name the {drive} drive")

    def test_is_multi_turn(self):
        self.assertIn("multiple turns", self.region_l,
                      "the deep-dive must deepen across MULTIPLE TURNS")

    def test_captures_adrs_into_project_key_decisions(self):
        self.assertIn("adr", self.region_l, "the deep-dive must capture ADRs")
        self.assertIn("project.md", self.region_l)
        self.assertIn("key decisions", self.region_l,
                      "ADRs land in PROJECT.md Key Decisions")

    def test_auto_completes_all_four_flag_first(self):
        self.assertIn("auto", self.region_l)
        self.assertTrue(
            "auto-complete" in self.region_l or "auto-completes" in self.region_l,
            "under autonomy=auto the step auto-completes the four drives in one pass")
        self.assertTrue(
            "flag" in self.region_l or "lowest-confidence" in self.region_l,
            "auto-complete still surfaces the lowest-confidence flag")

    def test_preserves_the_baseline_approval_gate(self):
        self.assertTrue(
            "lock" in self.region_l or "baseline approval" in self.region_l,
            "the step must say auto deepens drafting, not the lock/baseline-approval gate")
        self.assertIn("drafting", self.region_l,
                      "auto deepens DRAFTING, never the gate")

    def test_2b_interview_retained(self):
        # the deep-dive deepens §2b, it does not replace it
        self.assertIn("## 2b", self.setup,
                      "the §2b 4-lens interview section must be retained")

    def test_no_existing_section_dropped(self):
        for anchor in ("## 2a", "## 2b", "## 3 · Draft to the lock",
                       "## Run mode", "## 4 · The one human gate", "## Exit gate"):
            self.assertIn(anchor, self.setup,
                          f"the edit must not drop the existing '{anchor}' section")

    def test_three_trees_byte_identical(self):
        digests = {_md5(t / SETUP) for t in (CANONICAL, BUNDLED, DOGFOOD)}
        self.assertEqual(len(digests), 1, "0-setup.md diverged across the 3 skill trees")


if __name__ == "__main__":
    unittest.main()
