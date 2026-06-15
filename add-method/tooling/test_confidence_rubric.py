"""test_confidence_rubric — guards skill/add/confidence.md, the confidence self-score rubric.

The rubric is ADVISORY (it sharpens a draft and aims the lowest-confidence flag); it is
NEVER a gate. This suite asserts the doc states exactly that and carries the six-dimension
0-1 rubric, the refine threshold, the feeds-flag link, the may-recommend-autonomy line, and
the advisory-only <constraints> block — and that the frozen-vocab guard (test_xml_convention)
actually COVERS the new doc (confidence.md ∈ ENGINE_FILES, tags={constraints}).

Owning task: confidence-rubric (milestone advisor-context). RED until confidence.md exists
and is registered; GREEN after.
"""
from __future__ import annotations

import importlib.util
import re
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_DOC = _TOOLING.parent / "skill" / "add" / "confidence.md"

# Reuse the XML-convention guard's own helpers + registry so this test stays consistent with it.
_spec = importlib.util.spec_from_file_location(
    "xmlconv_for_confidence", _TOOLING / "test_xml_convention.py")
_xmlconv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_xmlconv)  # type: ignore[union-attr]


class TestConfidenceRubric(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        assert _DOC.exists(), f"confidence.md missing: {_DOC}"
        cls.text = _DOC.read_text(encoding="utf-8")
        cls.lower = cls.text.lower()

    def test_intro_names_self_score_and_advisory(self) -> None:
        self.assertIn("confidence self-score", self.lower,
                      "intro must name it the 'confidence self-score'")
        self.assertIn("advisory", self.lower, "intro must call the rubric 'advisory'")

    def test_six_dimensions(self) -> None:
        for dim in ("Completeness", "Clarity", "Practicality",
                    "Optimization", "Edge cases", "Self-evaluation"):
            self.assertIn(dim.lower(), self.lower, f"missing rubric dimension: {dim}")

    def test_scale_and_refine_threshold(self) -> None:
        self.assertRegex(self.text, r"0\s*[–-]\s*1", "missing the 0-1 scale")
        self.assertRegex(self.lower, r"<\s*0\.9", "missing the '< 0.9' refine threshold")
        self.assertIn("refine", self.lower, "missing the refine rule")

    def test_feeds_lowest_confidence_flag(self) -> None:
        self.assertIn("lowest-confidence flag", self.lower,
                      "must cite the lowest-confidence flag it feeds")
        self.assertTrue(("run.md" in self.lower) or ("1-specify.md" in self.lower),
                        "must point at run.md or 1-specify.md where the flag lives")

    def test_may_recommend_autonomy_not_force(self) -> None:
        self.assertIn("autonomy", self.lower, "must relate the score to autonomy")
        self.assertIn("recommend", self.lower, "lowering autonomy must be RECOMMEND-only")
        for forcing in ("must lower", "forces", "force lowering", "automatically lower"):
            self.assertNotIn(forcing, self.lower,
                             f"autonomy lowering must not be mandatory ('{forcing}')")

    def test_advisory_only_constraints_block(self) -> None:
        block = re.search(r"<constraints>(.*?)</constraints>", self.text, re.DOTALL)
        self.assertIsNotNone(block, "missing the advisory-only <constraints> block")
        body = block.group(1).lower()
        self.assertIn("never a gate", body,
                      "the <constraints> block must state the score is never a gate")
        self.assertTrue(("auto-pass" in body) or ("evidence" in body),
                        "the <constraints> block must rule out auto-PASS / substituting for evidence")

    def test_vocab_subset(self) -> None:
        tags = _xmlconv._paired_tags(_xmlconv._strip_code_fences(self.text))
        self.assertTrue(tags, "confidence.md carries no paired convention tag (not converted)")
        offenders = tags - {"constraints"}
        self.assertFalse(offenders, f"out-of-subset tags {sorted(offenders)} (engine doc: only constraints)")

    def test_registered_in_engine_files(self) -> None:
        self.assertIn("confidence.md", _xmlconv.ENGINE_FILES,
                      "confidence.md not registered in test_xml_convention.ENGINE_FILES")
        self.assertEqual(_xmlconv.ENGINE_FILES["confidence.md"]["tags"], {"constraints"},
                         "confidence.md must register tags={'constraints'}")


if __name__ == "__main__":
    unittest.main()
