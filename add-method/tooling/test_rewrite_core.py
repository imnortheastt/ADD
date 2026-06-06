"""Red safety net for v17 task `rewrite-core`.

A pure reword keeps the existing fences (wording_lint, semantic_inventory, test_xml_convention,
parity) GREEN by design — so the genuine RED for this task lives only in the 2 structural wins +
the blast-radius promotion. These four assertions encode "the rewrite happened" and run RED until
the build lands; they remain as permanent regression guards afterwards.

Run: python3 test_rewrite_core.py   (beside wording_lint.py / semantic_inventory.py — not mirrored).
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

import wording_lint as wl


def _surface_by_name() -> dict[str, Path]:
    """Map bare filename -> path over the canonical 19-file surface (SKILL.md, run.md, …)."""
    return {p.name: p for p in wl.surface_files()}


def _constraints_blocks(text: str) -> list[str]:
    """Every <constraints>…</constraints> block body in `text` (DOTALL)."""
    return re.findall(r"<constraints>(.*?)</constraints>", text, re.DOTALL)


class TestRunmdStructuralWin(unittest.TestCase):
    """Structural Win 2 — run.md's auto-gate + autonomy-dial prose moves INTO <constraints>."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.run_md = _surface_by_name()["run.md"].read_text(encoding="utf-8")
        cls.blocks = _constraints_blocks(cls.run_md)

    def test_runmd_autogate_in_constraints(self) -> None:
        # Key on `auto-resolved` — an S1-protected token UNIQUE to `## The evidence auto-gate`
        # within run.md (L108/L110). Gate-stable: the wording pass cannot mutate it (semantic-
        # inventory S1 would fire), so a CORRECT Win 2 can never leave this test red. (A prose
        # needle like "Auto-PASS requires ALL of" would break on a legitimate reword.)
        needle = "auto-resolved"
        self.assertIn(needle, self.run_md, "fixture drift: `auto-resolved` missing from run.md")
        self.assertTrue(any(needle in b for b in self.blocks),
                        "`## The evidence auto-gate` body is not inside a <constraints> block (Win 2 not done)")

    def test_runmd_autonomy_dial_in_constraints(self) -> None:
        needle = "unguarded_high_risk_auto"
        self.assertIn(needle, self.run_md, "fixture drift: autonomy-dial token missing from run.md")
        self.assertTrue(any(needle in b for b in self.blocks),
                        "`## The autonomy dial` body is not inside a <constraints> block (Win 2 not done)")


class TestBlastRadiusPromotion(unittest.TestCase):
    """Promotion — `blast radius` is core-only (streams.md); rewrite-core flips it surface-wide."""

    def test_blast_radius_enforced_and_absent(self) -> None:
        rubric = wl.load_rubric()
        self.assertIn("blast radius", rubric.enforced_banned,
                      "`blast radius` not promoted to enforced_banned (idiom_unretired)")
        hits = [p.name for p in wl.surface_files()
                if re.search(r"blast radius", p.read_text(encoding="utf-8"), re.IGNORECASE)]
        self.assertEqual(hits, [], f"`blast radius` still present on the surface in {hits} (not retired)")


class TestSkillTrim(unittest.TestCase):
    """Structural Win 1 — the duplicative always-loaded summary is trimmed; frozen token preserved."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = _surface_by_name()["SKILL.md"].read_text(encoding="utf-8")

    def test_skill_summary_trimmed(self) -> None:
        for header in ("## The dynamic run (v6–v7)", "## Parallel streams"):
            self.assertNotIn(header, self.skill,
                             f"duplicative section {header!r} still in SKILL.md (trim not done)")
        # the trim must PRESERVE the only frozen gate-outcome token unique to the trimmed region
        self.assertIn("auto-resolved", self.skill,
                      "the trim dropped `auto-resolved` from SKILL.md (semantic-inventory S1 would fire)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
