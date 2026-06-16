#!/usr/bin/env python3
"""Release-docs-accord guard (release-altitude task 4): the BOOK and the GLOSSARY
must teach the RELEASE scope level, and they must ACCORD with the shipped
`release.md` skill guide — the book reuses the guide's flow arc rather than
re-inventing it.

Scope split (deliberate, mirrors test_docs_accord):
  - cross-tree byte-identity of the book trees is owned by test_book_parity
    (canonical <-> repo-root) and test_bundle_parity (canonical <-> _bundled);
    this guard does NOT duplicate that — it asserts CONTENT on the canonical copy.
  - the operational recipe (the floor codes' internals, the CHANGELOG/RELEASES
    writers) stays in release.md / add.py; the book gets a CONCEPTUAL chapter +
    a pointer only.

Run: python3 -m unittest test_release_docs_accord -v
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_REPO_ROOT = _ADD_METHOD.parent

CANON_DOCS = _ADD_METHOD / "docs"
REPO_DOCS = _REPO_ROOT
BUNDLED_DOCS = _ADD_METHOD / "src" / "add_method" / "_bundled" / "docs"

CHAPTER_NAME = "16-releasing.md"
CHAPTER = CANON_DOCS / CHAPTER_NAME
GLOSSARY = CANON_DOCS / "appendix-c-glossary.md"
RELEASE_MD = _ADD_METHOD / "skill" / "add" / "release.md"

# The release flow arc — seven steps, in canonical order, EXACTLY as release.md
# names it (the accord anchor). A rename in either the book or the guide re-reds
# test_accord_with_release_md / test_flow_seven_steps_in_order.
FLOW_ARC = "cue → gather → draft notes → readiness floor → human confirms → cut → watch"
STEPS = ("cue", "gather", "draft notes", "readiness floor", "human confirms", "cut", "watch")

# The five net-new glossary headwords (regex: bold headword followed by an em dash).
HEADWORDS = ("Release", "Release scope level", "Readiness floor", "RELEASES.md ledger", "Hotfix release")

# Governance principles the chapter must state in its own voice (the §4/§5 anchors).
GOVERNANCE_TOKENS = (
    "release_security_open",   # the un-forceable floor code is named
    "un-forceable",            # security is the one reject --force cannot override
    "the engine records",      # engine-records-human-ships
    "never tags",              # ... it never tags / publishes / deploys
    "nested-package",          # finding #3: the root-CHANGELOG caveat
)


def _read(p: Path) -> str:
    """Read a doc; missing file -> "" so a pre-build RED is a clean assertion
    failure (chapter absent), not a FileNotFoundError."""
    try:
        return p.read_text(encoding="utf-8")
    except OSError:
        return ""


class ChapterShipsInEveryTreeTest(unittest.TestCase):
    """Must (CHAPTER) — 16-releasing.md is present in the 3 tracked trees."""

    def test_chapter_in_all_trees(self):
        for tree, where in ((CANON_DOCS, "canonical"), (REPO_DOCS, "repo-root"), (BUNDLED_DOCS, "bundled")):
            with self.subTest(tree=where):
                self.assertTrue(
                    (tree / CHAPTER_NAME).is_file(),
                    f"{CHAPTER_NAME} must exist in the {where} tree ({tree / CHAPTER_NAME})",
                )


class FlowInOrderTest(unittest.TestCase):
    """Must (FLOW IN ORDER) — the chapter names the 7-step arc in canonical order."""

    def test_flow_seven_steps_in_order(self):
        text = _read(CHAPTER)
        self.assertIn(
            FLOW_ARC, text,
            "ch.16 must name the 7-step flow arc verbatim, in order: " + FLOW_ARC,
        )
        # belt-and-suspenders: the step tokens also appear in order as prose unfolds
        ordered = re.compile(".*".join(re.escape(s) for s in STEPS), re.S)
        self.assertRegex(text, ordered, "the 7 steps must unfold in canonical order in ch.16")


class GovernancePrinciplesTest(unittest.TestCase):
    """Reject governance_omission — security-un-forceable + engine-records-human-ships + finding #3."""

    def test_governance_principles_present(self):
        text = _read(CHAPTER)
        for token in GOVERNANCE_TOKENS:
            with self.subTest(token=token):
                self.assertIn(
                    token, text,
                    f"ch.16 must state the governance principle anchored by '{token}'",
                )


class GlossaryTermsTest(unittest.TestCase):
    """Reject glossary_incomplete — the 5 terms are defined + Scope level enumerates release."""

    def test_glossary_terms_exist(self):
        text = _read(GLOSSARY)
        for head in HEADWORDS:
            with self.subTest(term=head):
                self.assertRegex(
                    text, re.compile(r"\*\*" + re.escape(head) + r"\*\*\s*—"),
                    f"glossary must define **{head}** — …",
                )

    def test_scope_level_enumerates_release(self):
        for line in _read(GLOSSARY).splitlines():
            if line.startswith("**Scope level**"):
                self.assertIn(
                    "release", line.lower(),
                    "the existing **Scope level** entry must be extended to enumerate the release level",
                )
                return
        self.fail("the **Scope level** glossary entry was not found")


class AccordWithGuideTest(unittest.TestCase):
    """Reject docs_discord — the book's flow arc matches release.md's (a rename re-reds)."""

    def test_accord_with_release_md(self):
        guide = _read(RELEASE_MD)
        book = _read(CHAPTER)
        self.assertIn(
            FLOW_ARC, guide,
            "release.md (the source of truth) must name the flow arc verbatim: " + FLOW_ARC,
        )
        self.assertIn(
            FLOW_ARC, book,
            "ch.16 must reuse release.md's flow arc verbatim, not re-invent it",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
