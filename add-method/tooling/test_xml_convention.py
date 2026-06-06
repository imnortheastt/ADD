"""test_xml_convention.py — enforce the v16 XML prompt convention on the pilot.

The convention is frozen in .add/tasks/xml-convention/TASK.md §3. This guard asserts it on
the worked-reference pilot (phases/1-specify.md, FULLY converted) and grows file-by-file as
later v16 tasks land.

Scope (task xml-convention): the pilot only. The 3-mirror parity is enforced by
test_bundle_parity + test_tree_parity (not re-authored here — checking the canonical tree suffices,
since parity guarantees _bundled/ and .claude/skills/add/ match it byte-for-byte).

Run: python3 -m unittest test_xml_convention -v
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_SKILL = _TOOLING.parent / "skill" / "add"
PILOT = _SKILL / "phases" / "1-specify.md"

# The frozen CLOSED vocabulary (TASK.md §3 CONTRACT). A tag outside this set = reject `vocab_offmidiom`.
# Lean BLOCK-LEVEL core: 5 tags, all-underscore. Tags mark block BOUNDARIES only — NO field children,
# NO nesting. Inside <prompt> the appendix-b skeleton labels (Role:/Read first:/Steps:/Never:) stay
# plain text. A stray field tag like <role> is auto-rejected here (it's not in the 5-tag set).
VOCAB = {
    "prompt", "exit_gate", "constraints", "reject_codes", "output_format",
}

# Sections of the pilot that are genuine narrative — they MUST stay prose (reject `narrative_tagged`).
NARRATIVE_HEADERS = ("## Co-specify in three moves", "## The least-sure flag is bundle-wide")

_OPEN = re.compile(r"<([a-z][a-z0-9_-]*)>")
_CLOSE = re.compile(r"</([a-z][a-z0-9_-]*)>")


def _paired_tags(text: str) -> set[str]:
    """Convention tags are PAIRED. A name with both <x> and </x> is a convention tag;
    a single unpaired <x> is a prose placeholder (<name>, <why>, <cost>) and is ignored."""
    return set(_OPEN.findall(text)) & set(_CLOSE.findall(text))


def _section(text: str, header: str) -> str:
    """Return the body of a '## <header>' section, up to the next '## ' or EOF."""
    out: list[str] = []
    grabbing = False
    for line in text.splitlines():
        if line.strip() == header:
            grabbing = True
            continue
        if grabbing and line.startswith("## "):
            break
        if grabbing:
            out.append(line)
    return "\n".join(out)


class TestXmlConventionPilot(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        assert PILOT.exists(), f"pilot missing: {PILOT}"
        cls.text = PILOT.read_text(encoding="utf-8")

    def test_pilot_fully_converted(self) -> None:
        """Must: 1-specify.md is the COMPLETE worked reference — block-level <prompt>, <output_format>, <exit_gate>."""
        block = re.search(r"<prompt>(.*?)</prompt>", self.text, re.DOTALL)
        self.assertIsNotNone(block, "no <prompt>…</prompt> block (## AI prompt not converted)")
        body = block.group(1)
        # block-level: skeleton labels are PLAIN TEXT inside <prompt> (not tagged)
        for label in ("Role:", "Never:"):
            self.assertIn(label, body, f"plain-text skeleton label '{label}' missing inside <prompt>")
        self.assertEqual(_paired_tags(body), set(),
                         "field-level tags found inside <prompt> — block-level uses plain-text labels")
        for tag in ("output_format", "exit_gate"):
            self.assertIn(f"<{tag}>", self.text, f"<{tag}> missing — pilot is not a full reference")

    def test_ai_prompt_header_preserved(self) -> None:
        """Reject header_dropped: the '## AI prompt' header survives (test_declare_grammar_doc relies on it)."""
        self.assertIn("## AI prompt", self.text, "the '## AI prompt' header was dropped")

    def test_vocab_in_set(self) -> None:
        """Reject vocab_offmidiom: every PAIRED convention tag is in the frozen vocabulary."""
        tags = _paired_tags(self.text)
        self.assertTrue(tags, "no paired convention tags found (pilot not yet converted)")
        offenders = tags - VOCAB
        self.assertFalse(offenders, f"out-of-vocabulary tags: {sorted(offenders)}")

    def test_narrative_untagged(self) -> None:
        """Reject narrative_tagged: genuine narrative sections carry NO paired convention tags."""
        for header in NARRATIVE_HEADERS:
            body = _section(self.text, header)
            self.assertEqual(_paired_tags(body), set(),
                             f"{header} carries convention tags — narrative must stay prose")


if __name__ == "__main__":
    unittest.main()
