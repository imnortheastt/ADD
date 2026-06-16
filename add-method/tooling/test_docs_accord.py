#!/usr/bin/env python3
"""Docs-accord guard (udd-design-loop task 4): the BOOK and the GLOSSARY must
describe the UDD design-definition loop, and they must ACCORD with the shipped
`design.md` skill guide — the book/glossary reuse the guide's beat names rather
than re-inventing them.

Scope split (deliberate):
  - cross-tree byte-identity of the 4 book trees is owned by test_book_parity
    (canonical <-> repo-root) and test_bundle_parity (canonical <-> _bundled);
    this guard does NOT duplicate that — it asserts CONTENT on the canonical copy.
  - the operational recipe (kit classes, CSS vars, json-render API) stays in
    udd-wireframe.md; the book gets a CONCEPTUAL description + a pointer only.

Run: python3 -m unittest test_docs_accord -v
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent

CANON_DOCS = _ADD_METHOD / "docs"
CHAPTER_14 = CANON_DOCS / "14-foundation.md"
GLOSSARY = CANON_DOCS / "appendix-c-glossary.md"
DESIGN_MD = _ADD_METHOD / "skill" / "add" / "design.md"

# The loop's four beats, in canonical order, as design.md names them.
BEATS = ("review-domain", "research-components", "wireframe", "render-capture-confirm")

# The four net-new glossary headwords (regex: bold headword followed by an em dash).
HEADWORDS = ("Wireframe", "Design mock", "Capture", "Design-confirm")

# Recipe-only tokens that must NOT leak into the conceptual book chapter.
RECIPE_ONLY = (":root", "var(--", "defineCatalog")


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


class BookDescribesLoopTest(unittest.TestCase):
    """Must 1 — chapter 14 names the loop's 4 ordered beats + design-confirm + pointer."""

    def test_book_names_loop_beats_in_order(self):
        text = _read(CHAPTER_14)
        ordered = re.compile(".*".join(re.escape(b) for b in BEATS), re.S)
        self.assertRegex(
            text, ordered,
            "chapter 14 must name the 4 beats in order: " + " → ".join(BEATS),
        )
        self.assertIn("design-confirm", text,
                      "chapter 14 must frame the capture as the human design-confirm")

    def test_book_points_to_the_guide(self):
        self.assertIn("design.md", _read(CHAPTER_14),
                      "chapter 14 must POINT to the design.md skill guide for the recipe")


class GlossaryDefinesTermsTest(unittest.TestCase):
    """Must 2 + Must 3 — the four entries exist and carry the capture extras."""

    def test_glossary_defines_four_terms(self):
        text = _read(GLOSSARY)
        for head in HEADWORDS:
            with self.subTest(term=head):
                self.assertRegex(
                    text, re.compile(r"\*\*" + re.escape(head) + r"\*\*\s*—"),
                    f"glossary must define **{head}** — …",
                )

    def test_capture_entries_carry_location_default_warn(self):
        text = _read(GLOSSARY)
        for token in (".add/design/captures/", "@json-render/image", "missing_capture"):
            with self.subTest(token=token):
                self.assertIn(
                    token, text,
                    f"the capture/design-confirm entries must surface '{token}'",
                )


class AccordWithGuideTest(unittest.TestCase):
    """Must 5 + Reject term_mismatch — the book reuses design.md's beat names."""

    def test_beats_are_sourced_from_the_guide(self):
        guide = _read(DESIGN_MD)
        book = _read(CHAPTER_14)
        for beat in BEATS:
            with self.subTest(beat=beat):
                self.assertIn(beat, guide,
                              f"design.md (the source of truth) must name the beat '{beat}'")
                self.assertIn(beat, book,
                              f"chapter 14 must reuse design.md's beat name '{beat}', not re-invent it")


class RecipeStaysInGuideTest(unittest.TestCase):
    """Reject recipe_in_book — the book stays conceptual, not a copy of the recipe."""

    def test_recipe_not_copied_into_book(self):
        text = _read(CHAPTER_14)
        leaked = [t for t in RECIPE_ONLY if t in text]
        self.assertEqual(
            leaked, [],
            "chapter 14 must point to the guide, not inline the recipe; "
            f"recipe-only tokens leaked into the book: {leaked}",
        )


class NetNewNotBridgedTest(unittest.TestCase):
    """Reject false_bridge — the 4 net-new terms are NOT rename-bridge entries."""

    def test_terms_not_in_rename_bridge(self):
        import test_ubiquitous_language as ul
        rename_slugs = {t["slug"] for t in ul.TERMS}
        new_slugs = {"wireframe", "design-mock", "capture", "design-confirm"}
        clash = new_slugs & rename_slugs
        self.assertEqual(
            clash, set(),
            "net-new UDD terms must not be added to the rename-bridge TERMS list: " + str(clash),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
