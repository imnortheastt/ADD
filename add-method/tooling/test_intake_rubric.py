#!/usr/bin/env python3
"""Structural proof of the intake versioning rubric (task: versioning-policy, v4-1).

This task ships a JUDGMENT artifact (a rubric the AI applies at intake), not code — so the
red/green guard asserts the ARTIFACT's structure, never the AI's live classification:
intake.md exists in both synced skill trees (md5 parity), documents the 4 frozen buckets +
3 reject codes by name, states the tie-break order (frozen-scope BEFORE size), carries a
machine-parseable worked-examples table whose every bucket cell is one of the 4, and both
SKILL.md copies link to it. The human reviews the rubric's JUDGMENT at the verify gate.

Run: python3 -m unittest test_intake_rubric -v
"""
import hashlib
import re
import unittest
from pathlib import Path

# Resolve repo paths from THIS file, not cwd: tooling/ -> add-method/ -> repo root.
_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_REPO = _ADD_METHOD.parent

CANONICAL_INTAKE = _ADD_METHOD / "skill" / "add" / "intake.md"
DOGFOOD_INTAKE = _REPO / ".claude" / "skills" / "add" / "intake.md"
CANONICAL_SKILL = _ADD_METHOD / "skill" / "add" / "SKILL.md"
DOGFOOD_SKILL = _REPO / ".claude" / "skills" / "add" / "SKILL.md"

BUCKETS = {"new-major", "sub-milestone", "task", "change-request"}
REJECT_CODES = {"ask_human", "frozen_scope", "split_required"}


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def _parse_examples_table(text: str):
    """Parse the | request | bucket | rationale | markdown table; return list of bucket cells.

    Reads only the rows of the table whose header includes 'bucket'; skips the --- separator.
    """
    buckets = []
    in_table = False
    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            in_table = False
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        lowered = [c.lower() for c in cells]
        if "bucket" in lowered and "request" in lowered:
            in_table = True
            bucket_col = lowered.index("bucket")
            continue
        if not in_table:
            continue
        if set("".join(cells)) <= set("-: "):   # the |---|---| separator row
            continue
        if len(cells) > bucket_col:
            buckets.append(cells[bucket_col])
    return buckets


class IntakeRubricTest(unittest.TestCase):
    def test_intake_exists_in_both_trees_with_md5_parity(self):
        self.assertTrue(CANONICAL_INTAKE.exists(), f"missing {CANONICAL_INTAKE}")
        self.assertTrue(DOGFOOD_INTAKE.exists(), f"missing {DOGFOOD_INTAKE}")
        self.assertEqual(_md5(CANONICAL_INTAKE), _md5(DOGFOOD_INTAKE),
                         "intake.md differs between the canonical and dogfood skill trees")

    def test_documents_all_four_buckets(self):
        text = CANONICAL_INTAKE.read_text(encoding="utf-8")
        for b in BUCKETS:
            self.assertIn(b, text, f"intake.md does not document the '{b}' bucket")

    def test_documents_all_three_reject_codes(self):
        text = CANONICAL_INTAKE.read_text(encoding="utf-8")
        for code in REJECT_CODES:
            self.assertIn(code, text, f"intake.md does not document the '{code}' reject code")

    def test_states_tiebreak_order_frozen_before_size(self):
        text = CANONICAL_INTAKE.read_text(encoding="utf-8").lower()
        # a single line declaring the order: frozen-scope test, then the size test.
        m = re.search(r"tie-?break order.*frozen.*before.*size", text)
        self.assertIsNotNone(
            m, "intake.md must state the tie-break order (frozen-scope BEFORE size) on one line")

    def test_worked_examples_table_parses_and_buckets_valid(self):
        text = CANONICAL_INTAKE.read_text(encoding="utf-8")
        cells = _parse_examples_table(text)
        self.assertTrue(cells, "no worked-examples table rows found")
        for c in cells:
            self.assertIn(c, BUCKETS, f"example row has invalid bucket '{c}'")
        self.assertEqual(BUCKETS, set(cells) & BUCKETS,
                         "worked examples must cover all 4 buckets")

    def test_both_skill_md_link_intake_and_are_identical(self):
        for skill in (CANONICAL_SKILL, DOGFOOD_SKILL):
            self.assertIn("intake.md", skill.read_text(encoding="utf-8"),
                          f"{skill} does not point to intake.md")
        self.assertEqual(_md5(CANONICAL_SKILL), _md5(DOGFOOD_SKILL),
                         "the two SKILL.md copies are not byte-identical")


if __name__ == "__main__":
    unittest.main(verbosity=2)
