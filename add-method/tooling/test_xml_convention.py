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


# ─── task phase-guides-xml: the 7 remaining phase guides (0,2-7) ──────────────────────────────
# Each guide applies the SAME three tags the pilot uses — prompt · output_format · exit_gate —
# and introduces NO new vocabulary (constraints/reject_codes are reserved for the engine docs, task 3).
# The narrative list per file is ENUMERATED so the over-tagging guard is real, not hollow: a tag on any
# listed narrative section fails test_phase_narrative_untagged.
PHASE_SUBSET = {"prompt", "output_format", "exit_gate"}
PHASE_FILES = {
    "0-setup.md": {
        "prompt": False, "output_format": False,
        "narrative": (
            "## 1 · Zero-touch entry — you run init yourself",
            "## 2a · Brownfield — map it silently",
            "## 2b · Greenfield — the 4-lens interview (kept): co-specify at foundation altitude",
            "## 3 · Draft to the lock (both paths)",
            "## 4 · The one human gate — the lock-down",
            "## 5 · After the lock",
            "## Next",
        )},
    "2-scenarios.md": {
        "prompt": True, "output_format": True,
        "narrative": ("## Next",)},
    "3-contract.md": {
        "prompt": True, "output_format": True,
        "narrative": ("## The freeze review checklist", "## Next")},
    "4-tests.md": {
        "prompt": True, "output_format": True,
        "narrative": ("## The must-fail principle", "## Declaring where tests live", "## Next")},
    "5-build.md": {
        "prompt": True, "output_format": False,
        "narrative": ("## Work in small batches", "## The cardinal rule", "## Next")},
    "6-verify.md": {
        "prompt": False, "output_format": False,
        "narrative": (
            "## Part one — confirm the evidence",
            "## Part two — check what tests miss",
            "## Record exactly one outcome (no silent pass)",
        )},
    "7-observe.md": {
        "prompt": True, "output_format": False,
        "narrative": ("## Do", "## Next")},
}


def _produce_section(text: str) -> str:
    """Body of the '## Produce…' section (header varies: '## Produce', '## Produce (in TASK.md §2)')."""
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("## Produce"):
            return _section(text, s)
    return ""


class TestXmlConventionPhaseGuides(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.texts = {}
        for name in PHASE_FILES:
            p = _SKILL / "phases" / name
            assert p.exists(), f"phase guide missing: {p}"
            cls.texts[name] = p.read_text(encoding="utf-8")

    def test_phase_prompts_converted(self) -> None:
        """Must: every guide that HAS a '## AI prompt' carries a block-level <prompt> (plain-text Role:, no field tags), header preserved."""
        for name, spec in PHASE_FILES.items():
            if not spec["prompt"]:
                continue
            text = self.texts[name]
            self.assertIn("## AI prompt", text, f"{name}: '## AI prompt' header dropped")
            block = re.search(r"<prompt>(.*?)</prompt>", text, re.DOTALL)
            self.assertIsNotNone(block, f"{name}: no <prompt>…</prompt> block")
            body = block.group(1)
            self.assertIn("Role:", body, f"{name}: plain-text 'Role:' label missing inside <prompt>")
            self.assertEqual(_paired_tags(body), set(),
                             f"{name}: field-level tags inside <prompt> — use plain-text labels")

    def test_phase_output_format(self) -> None:
        """Must: every guide that HAS a '## Produce' wraps its body in <output_format>."""
        for name, spec in PHASE_FILES.items():
            if not spec["output_format"]:
                continue
            text = self.texts[name]
            self.assertIn("<output_format>", text, f"{name}: no <output_format> block")
            self.assertIn("<output_format>", _produce_section(text),
                          f"{name}: <output_format> is not inside the '## Produce' section")

    def test_phase_exit_gate(self) -> None:
        """Must: all 7 guides carry an <exit_gate> block."""
        for name in PHASE_FILES:
            self.assertIn("<exit_gate>", self.texts[name], f"{name}: no <exit_gate> block")

    def test_phase_vocab_subset(self) -> None:
        """Reject vocab_offmidiom: every paired tag in the 7 guides ∈ {prompt, output_format, exit_gate}."""
        for name in PHASE_FILES:
            tags = _paired_tags(self.texts[name])
            self.assertTrue(tags, f"{name}: no paired convention tags found (not converted)")
            offenders = tags - PHASE_SUBSET
            self.assertFalse(offenders, f"{name}: out-of-subset tags {sorted(offenders)} (constraints/reject_codes belong to task 3)")

    def test_phase_narrative_untagged(self) -> None:
        """Reject narrative_tagged: each file's enumerated narrative sections carry NO paired tags."""
        for name, spec in PHASE_FILES.items():
            text = self.texts[name]
            for header in spec["narrative"]:
                body = _section(text, header)
                self.assertEqual(_paired_tags(body), set(),
                                 f"{name}: narrative section {header!r} carries convention tags — must stay prose")


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
