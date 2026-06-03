#!/usr/bin/env python3
"""Structural proof of the principles 6/7 reframe (task: principle-reframe, v6).

v6's evidence-auto-gate stands on this. As shipped, principle 6 assumes human reading is the
verification ceiling and principle 7 reads as if only a signed person can resolve a gate. This task
reframes both — ADDITIVELY — so automated verification is admitted (principle 2 at its limit) while
the residue tests cannot catch, and security ALWAYS, stay human. The red/green guard asserts STRUCTURE
across all three book trees (root · add-method/docs · .add/docs): md5 parity; P6 admits automated
verification + names the residue + keeps its "verification capacity is the real ceiling" core; P7
admits a recorded automated pass is not a skip + keeps "No silent skips" + security never auto-passes.

NOTE: these tests prove the reframe's WORDS exist as contracted — NOT that the reframe is sound.
Soundness is irreducibly human judgment (see this task's OBSERVE deltas). Exactly 6 tests — frozen @ v1.

Run: python3 -m unittest test_principle_reframe -v
"""
import hashlib
import re
import unittest
from pathlib import Path

# tooling/ -> add-method/ -> repo root
_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_REPO = _ADD_METHOD.parent

PRINCIPLES = [
    _REPO / "01-principles.md",
    _ADD_METHOD / "docs" / "01-principles.md",
    _REPO / ".add" / "docs" / "01-principles.md",
]


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def _text() -> str:
    return PRINCIPLES[0].read_text(encoding="utf-8")


def _section(text: str, heading_no: int) -> str:
    """Return the body of '## <n>. ...' up to the next '## ' or '---'."""
    m = re.search(rf"^##\s*{heading_no}\.\s.*$", text, flags=re.MULTILINE)
    if not m:
        return ""
    rest = text[m.end():]
    nxt = re.search(r"^(##\s|\-\-\-)", rest, flags=re.MULTILINE)
    return rest[: nxt.start()] if nxt else rest


class PrincipleReframeTest(unittest.TestCase):
    def test_all_three_trees_md5_identical(self):
        # `.add/docs` is the gitignored dogfood mirror — absent on a clean checkout
        # (CI). Check the trees that exist: root + shipped are committed and MUST
        # agree; the mirror joins the parity check only where a dogfood install has
        # materialised it. (Same tolerance test_flow_diagram already uses.)
        present = [p for p in PRINCIPLES if p.exists()]
        self.assertGreaterEqual(len(present), 2, "root + shipped 01-principles.md must exist")
        h = {_md5(p) for p in present}
        self.assertEqual(len(h), 1, "01-principles.md copies diverge across the doc trees")

    def test_p6_admits_automated_verification(self):
        low = _section(_text(), 6).lower()
        self.assertTrue(low, "principle 6 section not found")
        self.assertIn("automat", low, "P6 must admit AUTOMATED verification")
        self.assertTrue(
            re.search(r"test|contract check|verifier|evidence", low),
            "P6 must name automated verification (tests/checks/verifiers/evidence)")
        self.assertTrue(
            re.search(r"raise|rais\w+ the ceiling|scale", low),
            "P6 must state automated verification can raise/scale the ceiling")

    def test_p6_names_the_human_residue(self):
        low = _section(_text(), 6).lower()
        for term in ("security", "concurrency", "architecture"):
            self.assertIn(term, low, f"P6 must name '{term}' as residue that stays human")

    def test_p6_keeps_its_core_claim(self):
        low = _section(_text(), 6).lower()
        self.assertIn("verification capacity is the real ceiling", low,
                      "P6 reframe must be ADDITIVE — its core ceiling claim must survive (not gutted)")

    def test_p7_admits_recorded_automated_pass_and_keeps_heading(self):
        text = _text()
        self.assertIsNotNone(re.search(r"^##\s*7\.\s*No silent skips", text, re.MULTILINE),
                             "P7 heading 'No silent skips' must survive the reframe")
        low = _section(text, 7).lower()
        self.assertTrue(
            re.search(r"automat\w+.{0,120}(pass|gate|resolv)", low, re.DOTALL),
            "P7 must admit an automated pass/gate resolution")
        self.assertTrue(
            re.search(r"recorded|logged|recorded outcome", low),
            "P7 must require the automated pass be recorded")
        self.assertIn("accountable owner", low, "P7 must keep an accountable owner for the outcome")

    def test_p7_security_never_auto_passes(self):
        low = _section(_text(), 7).lower()
        self.assertIn("security", low, "P7 must address security under automation")
        self.assertTrue(
            re.search(r"security.{0,120}(human|hard-stop|never auto|escalat)|"
                      r"(human|hard-stop|never auto|escalat).{0,120}security", low, re.DOTALL),
            "P7 must state security always escalates to a human / never auto-passes")


if __name__ == "__main__":
    unittest.main(verbosity=2)
