#!/usr/bin/env python3
"""Structural proof of the scope-drafting rubric (task: scope-loop, v4-1).

scope-loop ships a JUDGMENT artifact (scope.md — the facilitation method that turns a
CLASSIFIED request into a versioned MILESTONE.md), not code. So the red/green guard asserts
the ARTIFACT's structure, never the AI's live drafting: scope.md exists in both synced skill
trees (md5 parity), documents the per-outcome behavior for all 4 intake outcomes + the 3 reject
codes, states the confirm-before-create invariant and the exit-criteria->task-slug rule, carries
a worked example naming a REAL milestone slug in this repo, and both SKILL.md copies link it.
The human reviews the drafting JUDGMENT at the verify gate.

Run: python3 -m unittest test_scope_loop -v
"""
import hashlib
import re
import unittest
from pathlib import Path

# Resolve repo paths from THIS file, not cwd: tooling/ -> add-method/ -> repo root.
_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_REPO = _ADD_METHOD.parent

CANONICAL_SCOPE = _ADD_METHOD / "skill" / "add" / "scope.md"
DOGFOOD_SCOPE = _REPO / ".claude" / "skills" / "add" / "scope.md"
CANONICAL_SKILL = _ADD_METHOD / "skill" / "add" / "SKILL.md"
DOGFOOD_SKILL = _REPO / ".claude" / "skills" / "add" / "SKILL.md"
MILESTONES_DIR = _REPO / ".add" / "milestones"

# The 4 intake outcomes (the 4 buckets) plus the split path the outcomes table must cover.
OUTCOME_TOKENS = {"new-major", "sub-milestone", "task", "change-request", "split_required"}
REJECT_CODES = {"not_classified", "dangling_criterion", "no_milestone"}


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def _parse_outcomes_table(text: str):
    """Parse the | intake outcome | scope-loop action | creates | table -> outcome-column cells.

    Identified by an 'outcome' + 'action' header with no 'bucket'/'request' column.
    """
    cells_out = []
    in_table = False
    outcome_col = None
    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            in_table = False
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        lowered = [c.lower() for c in cells]
        if (any("outcome" in c for c in lowered) and any("action" in c for c in lowered)
                and not any("bucket" in c or "request" in c for c in lowered)):
            in_table = True
            outcome_col = next(i for i, c in enumerate(lowered) if "outcome" in c)
            continue
        if not in_table:
            continue
        if set("".join(cells)) <= set("-: "):   # the |---|---| separator row
            continue
        if len(cells) > outcome_col:
            cells_out.append(cells[outcome_col])
    return cells_out


def _worked_example_section(text: str) -> str:
    """Return the text from the 'worked example' heading onward (empty if absent)."""
    m = re.search(r"^#+\s*worked example.*$", text, flags=re.IGNORECASE | re.MULTILINE)
    return text[m.start():] if m else ""


def _real_milestone_slugs():
    if not MILESTONES_DIR.is_dir():
        return set()
    return {p.name for p in MILESTONES_DIR.iterdir() if p.is_dir()}


class ScopeLoopTest(unittest.TestCase):
    def test_scope_exists_in_both_trees_with_md5_parity(self):
        self.assertTrue(CANONICAL_SCOPE.exists(), f"missing {CANONICAL_SCOPE}")
        self.assertTrue(DOGFOOD_SCOPE.exists(), f"missing {DOGFOOD_SCOPE}")
        self.assertEqual(_md5(CANONICAL_SCOPE), _md5(DOGFOOD_SCOPE),
                         "scope.md differs between the canonical and dogfood skill trees")

    def test_documents_all_four_intake_outcomes(self):
        # The outcomes table must cover all 4 buckets + the split path (in its outcome column),
        # not merely mention the words in prose. Deleting the table or a row goes red.
        text = CANONICAL_SCOPE.read_text(encoding="utf-8")
        cells = _parse_outcomes_table(text)
        self.assertTrue(cells, "no outcomes table found in scope.md")
        joined = " ".join(cells).lower()
        for tok in OUTCOME_TOKENS:
            self.assertIn(tok, joined, f"outcomes table does not document the '{tok}' outcome")

    def test_documents_all_three_reject_codes(self):
        text = CANONICAL_SCOPE.read_text(encoding="utf-8")
        for code in REJECT_CODES:
            self.assertIn(code, text, f"scope.md does not document the '{code}' reject code")

    def test_states_confirm_before_create_invariant(self):
        text = CANONICAL_SCOPE.read_text(encoding="utf-8").lower()
        m = re.search(r"confirm[\s-]*before[\s-]*create", text)
        self.assertIsNotNone(
            m, "scope.md must state the confirm-before-create invariant")

    def test_states_exit_criteria_map_to_task_slug(self):
        text = CANONICAL_SCOPE.read_text(encoding="utf-8").lower()
        m = re.search(r"exit criteri.{0,60}task slug", text, flags=re.DOTALL)
        self.assertIsNotNone(
            m, "scope.md must state that every exit criterion maps to a declared task slug")

    def test_worked_example_references_real_milestone(self):
        section = _worked_example_section(CANONICAL_SCOPE.read_text(encoding="utf-8"))
        self.assertTrue(section, "scope.md has no 'worked example' section")
        real = _real_milestone_slugs()
        self.assertTrue(real, f"no milestones found under {MILESTONES_DIR}")
        hit = [s for s in real if s in section]
        self.assertTrue(
            hit, f"worked example names no real milestone slug (have {sorted(real)})")

    def test_both_skill_md_link_scope_and_are_identical(self):
        for skill in (CANONICAL_SKILL, DOGFOOD_SKILL):
            self.assertIn("scope.md", skill.read_text(encoding="utf-8"),
                          f"{skill} does not point to scope.md")
        self.assertEqual(_md5(CANONICAL_SKILL), _md5(DOGFOOD_SKILL),
                         "the two SKILL.md copies are not byte-identical")


if __name__ == "__main__":
    unittest.main(verbosity=2)
