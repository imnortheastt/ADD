#!/usr/bin/env python3
"""Structural proof of the competency-delta shape (task: competency-deltas, v5).

competency-deltas freezes the SHAPE of a self-improvement signal, not a reader. A delta is one
tagged line written in a task's OBSERVE phase:

    - [<COMPETENCY> · <status>] <learning> (evidence: <pointer>)
        COMPETENCY ∈ {DDD, SDD, UDD, TDD, ADD}   status ∈ {open, folded, rejected}   evidence required

The deliverable is a JUDGMENT rubric (skill/add/deltas.md) plus a mechanical scaffold slot, so the
red/green guard asserts STRUCTURE, never the AI's live tagging: the rubric exists in both synced
skill trees (md5 parity), documents all five competencies + all three statuses (new=open) + all
three reject codes + the grammar + a worked example; SKILL.md links it; the new-task scaffold ships
a commented `### Competency deltas` block; and the glossary defines the term. The parser that READS
deltas is out of scope here (deferred to convergence-signal). Exactly 8 tests — frozen @ v1.

Run: python3 -m unittest test_competency_deltas -v
"""
import hashlib
import re
import unittest
from pathlib import Path

# Resolve repo paths from THIS file, not cwd: tooling/ -> add-method/ -> repo root.
_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_REPO = _ADD_METHOD.parent

CANONICAL_DELTAS = _ADD_METHOD / "skill" / "add" / "deltas.md"
DOGFOOD_DELTAS = _REPO / ".claude" / "skills" / "add" / "deltas.md"
CANONICAL_SKILL = _ADD_METHOD / "skill" / "add" / "SKILL.md"
DOGFOOD_SKILL = _REPO / ".claude" / "skills" / "add" / "SKILL.md"
TASK_TMPL = _ADD_METHOD / "tooling" / "templates" / "TASK.md.tmpl"
GLOSSARY = _ADD_METHOD / "docs" / "appendix-c-glossary.md"

COMPETENCIES = {"DDD", "SDD", "UDD", "TDD", "ADD"}
STATUSES = {"open", "folded", "rejected"}
REJECT_CODES = {"unknown_competency", "no_evidence", "unknown_status"}
DELTAS_HEADING = "### Competency deltas"


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def _deltas_block(text: str) -> str:
    """Return the '### Competency deltas' block (up to the next heading), '' if absent."""
    m = re.search(r"^### +Competency deltas.*?$", text, flags=re.IGNORECASE | re.MULTILINE)
    if not m:
        return ""
    rest = text[m.end():]
    nxt = re.search(r"^#{1,3} ", rest, flags=re.MULTILINE)
    return rest[: nxt.start()] if nxt else rest


class CompetencyDeltasTest(unittest.TestCase):
    def test_deltas_md_exists_in_both_trees_with_md5_parity(self):
        self.assertTrue(CANONICAL_DELTAS.exists(), f"missing {CANONICAL_DELTAS}")
        self.assertTrue(DOGFOOD_DELTAS.exists(), f"missing {DOGFOOD_DELTAS}")
        self.assertEqual(_md5(CANONICAL_DELTAS), _md5(DOGFOOD_DELTAS),
                         "deltas.md differs between the canonical and dogfood skill trees")

    def test_documents_all_five_competencies(self):
        text = CANONICAL_DELTAS.read_text(encoding="utf-8")
        for c in COMPETENCIES:
            self.assertIn(c, text, f"deltas.md does not document the '{c}' competency")
        # No sixth competency tag: every bracketed 3-upper tag used must be one of the five.
        tags = set(re.findall(r"\[([A-Z]{3}) ·", text))
        self.assertTrue(tags, "deltas.md shows no bracketed competency tag at all")
        self.assertTrue(tags <= COMPETENCIES,
                        f"deltas.md introduces a non-canonical competency tag: {tags - COMPETENCIES}")

    def test_documents_all_three_statuses_and_new_is_open(self):
        text = CANONICAL_DELTAS.read_text(encoding="utf-8")
        for s in STATUSES:
            self.assertIn(s, text, f"deltas.md does not document the '{s}' status")
        low = text.lower()
        self.assertIsNotNone(
            re.search(r"(new|fresh|emit\w*).{0,60}open|open.{0,40}(new|fresh|emit)", low, re.DOTALL),
            "deltas.md must state that a newly emitted delta is `open`")

    def test_documents_all_three_reject_codes(self):
        text = CANONICAL_DELTAS.read_text(encoding="utf-8")
        for code in REJECT_CODES:
            self.assertIn(code, text, f"deltas.md does not document the '{code}' reject code")

    def test_states_the_delta_grammar(self):
        text = CANONICAL_DELTAS.read_text(encoding="utf-8")
        self.assertIn("<COMPETENCY> · <status>", text,
                      "deltas.md must state the bracketed-tag grammar")
        self.assertIn("(evidence:", text,
                      "deltas.md must state the required (evidence: …) pointer")

    def test_skill_md_links_deltas_and_both_trees_identical(self):
        for skill in (CANONICAL_SKILL, DOGFOOD_SKILL):
            self.assertIn("deltas.md", skill.read_text(encoding="utf-8"),
                          f"{skill} does not point to deltas.md")
        self.assertEqual(_md5(CANONICAL_SKILL), _md5(DOGFOOD_SKILL),
                         "the two SKILL.md copies are not byte-identical")

    def test_scaffold_emits_competency_deltas_block_commented_example(self):
        text = TASK_TMPL.read_text(encoding="utf-8")
        self.assertIn(DELTAS_HEADING, text,
                      f"{TASK_TMPL} does not scaffold a '{DELTAS_HEADING}' block")
        block = _deltas_block(text)
        self.assertTrue(block, "could not isolate the Competency deltas block in the template")
        # The example must be a COMMENT — no LIVE delta line a future parser would count.
        for ln in block.splitlines():
            self.assertFalse(
                re.match(r"\s*- \[(DDD|SDD|UDD|TDD|ADD) ·", ln),
                f"scaffold has a LIVE delta line (must be an HTML comment): {ln!r}")

    def test_glossary_has_competency_delta_entry(self):
        text = GLOSSARY.read_text(encoding="utf-8")
        self.assertIsNotNone(
            re.search(r"\*\*Lesson learned\*\*", text, re.IGNORECASE),
            "appendix-c-glossary.md has no 'Competency delta' entry")


if __name__ == "__main__":
    unittest.main(verbosity=2)
