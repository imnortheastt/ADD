"""intake-interview §4 suite — interview before you size.

Four RED targets (the build drives these green):
  - test_interview_section_present : intake.md carries the frozen section — header +
    the three moves' needles ("explore it WITH the user", "2–3 sized options",
    "Only then emit") and the floor's "never guess a bucket".
  - test_section_before_buckets    : the section sits BEFORE "## The four buckets"
    (pins the chronological placement: interview, then classify).
  - test_skill_anchor_names_rule   : SKILL.md's intake paragraph names the rule.
  - test_one_home_only             : the rule's needle phrase lives in EXACTLY
    {intake.md, SKILL.md} across skill/add/**/*.md — red now (0 homes), green only
    at exactly 2. Guards the contract's `rule_sprinkled` rejection permanently.

One GREEN guard (green at write-time, disclosed in §4 — guards `guard_weakened`):
  - test_ask_human_floor_verbatim : the pre-existing ask_human reject line stays
    byte-present; the new section is ADDITIVE, never a rewording.

Lint / inventory / mirror parity are owned by the STANDING fences (wording_lint,
semantic-inventory, the skill/add tree-parity + md5 guards) — declared in §4, not
duplicated.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
sys.path.insert(0, str(_TOOLING))

_SKILL = _TOOLING.parent / "skill" / "add"
_INTAKE = _SKILL / "intake.md"
_SKILL_MD = _SKILL / "SKILL.md"

# The frozen hunk-A needles (contract §3, verbatim fragments — guard-dense: one per claim).
_SECTION_HEADER = "## Interview before you size"
_NEEDLE_EXPLORE = "explore it WITH the user"
_NEEDLE_OPTIONS = "2–3 sized options"
_NEEDLE_EMIT = "Only then emit"
_NEEDLE_FLOOR = "never guess a bucket"
# The home-identity needle (shared by the section header and the SKILL.md anchor).
_HOME_NEEDLE = "Interview before you size"

# The pre-existing ask_human reject line — byte-exact (the additive guard).
_ASK_HUMAN_LINE = "Ask the human; never guess a bucket."


class IntakeInterview(unittest.TestCase):
    def test_interview_section_present(self) -> None:
        text = _INTAKE.read_text(encoding="utf-8")
        for needle in (_SECTION_HEADER, _NEEDLE_EXPLORE,
                       _NEEDLE_OPTIONS, _NEEDLE_EMIT):
            self.assertIn(needle, text,
                          f"intake.md is missing the frozen needle: {needle!r}")
        section = text.split(_SECTION_HEADER, 1)[-1].split("\n## ", 1)[0]
        self.assertIn(_NEEDLE_FLOOR, section,
                      "the section's floor line must keep 'never guess a bucket'")

    def test_section_before_buckets(self) -> None:
        text = _INTAKE.read_text(encoding="utf-8")
        self.assertIn(_SECTION_HEADER, text, "the interview section is missing")
        self.assertLess(text.index(_SECTION_HEADER), text.index("## The four buckets"),
                        "the interview section must sit before '## The four buckets'")

    def test_skill_anchor_names_rule(self) -> None:
        text = _SKILL_MD.read_text(encoding="utf-8")
        self.assertIn(_HOME_NEEDLE, text,
                      "SKILL.md's intake paragraph must name the rule")

    def test_one_home_only(self) -> None:
        homes = sorted(
            p.relative_to(_SKILL).as_posix()
            for p in _SKILL.rglob("*.md")
            if _HOME_NEEDLE in p.read_text(encoding="utf-8")
        )
        self.assertEqual(homes, ["SKILL.md", "intake.md"],
                         f"the rule must live in exactly two homes, found: {homes}")

    def test_ask_human_floor_verbatim(self) -> None:
        text = _INTAKE.read_text(encoding="utf-8")
        self.assertIn(_ASK_HUMAN_LINE, text,
                      "the pre-existing ask_human reject line changed or vanished")


if __name__ == "__main__":
    unittest.main()
