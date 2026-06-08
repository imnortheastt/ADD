#!/usr/bin/env python3
"""Book-copy invariants retained after the v21 inline-citation weave was REVERTED.

History: v21 task 3 wove inline [Author Year] citations into three existing book chapters
(02-the-flow · 03-step-1-specify · 09-the-loop) and shipped this file to guard them. The weave
was later removed (PROJECT.md §Key Decisions — "v21 inline-citation weave reverted"); the four
weave-resolution tests went with it. What remains are the three invariants the weave introduced
that are STILL load-bearing for the book and are covered NOWHERE else:

  - appendix-g stays frozen at 27 cite-keys — the ONLY exact-27 guard (test_bundle_parity checks
    canonical↔bundle file-sets, test_references_appendix only floors entries at >=18).
  - the three (formerly-woven) chapters stay ×4 byte-identical — the ONLY guard of the root ./
    copy against canonical for these chapters (test_bundle_parity covers canonical↔bundle only).
  - those chapters stay on the ubiquitous-language ban surface — a tripwire against the lint
    surface being narrowed out from under them.

The regexes were COPIED verbatim from test_foundations_chapter.py (copy, don't couple). Only
`extended_surface` is imported, from the ubiquitous-language test, so the ban-surface tripwire ties
to the real file set without forking a list.

Run: python3 -m unittest test_inline_citations -v
"""
import hashlib
import re
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_REPO = _ADD_METHOD.parent

# the three chapters that hosted the (reverted) v21 weave; still guarded for parity + ban-surface
WOVEN_CHAPTERS = ("02-the-flow.md", "03-step-1-specify.md", "09-the-loop.md")
APPENDIX_G = "appendix-g-references.md"
APPENDIX_G_KEY_COUNT = 27          # frozen in references-appendix (v21 task 1)


def _copies_of(filename: str) -> dict:
    """The 4 book copies of a doc: root ./ · canonical · bundle · dogfood (.add/docs, gitignored)."""
    return {
        "root":      _REPO / filename,
        "canonical": _ADD_METHOD / "docs" / filename,
        "bundle":    _ADD_METHOD / "src" / "add_method" / "_bundled" / "docs" / filename,
        "dogfood":   _REPO / ".add" / "docs" / filename,
    }


CANON_APPENDIX_G = _copies_of(APPENDIX_G)["canonical"]

# the entry-lead key inside appendix-g: "- **Title** (Author Year) — …" → first (… Year) parenthetical.
_ENTRY_PREFIX = "- **"
_KEY_RE = re.compile(r"\(([^)]*\b(?:19|20)\d{2}[a-z]?)\)")


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def _appendix_g_keys() -> set:
    """The valid cite-key set = the lead (Author Year) of every appendix-g entry line."""
    assert CANON_APPENDIX_G.exists(), f"appendix-g missing at {CANON_APPENDIX_G} (references-appendix not built?)"
    keys = set()
    for ln in _read(CANON_APPENDIX_G).splitlines():
        if ln.startswith(_ENTRY_PREFIX):
            m = _KEY_RE.search(ln)          # FIRST year-parenthetical = the entry's cite-key
            if m:
                keys.add(m.group(1).strip())
    return keys


def _canon(chapter: str) -> Path:
    return _copies_of(chapter)["canonical"]


class BookCopyInvariantsTest(unittest.TestCase):

    # appendix-g stays frozen at 27 keys (appendix_reopened)
    def test_appendix_g_frozen(self):
        n = len(_appendix_g_keys())
        self.assertEqual(n, APPENDIX_G_KEY_COUNT,
                         f"appendix-g key count changed to {n} (appendix_reopened — the 27 are frozen)")

    # the 3 chapters stay mirrored ×4 byte-identical (mirror_drift) — only guard of root ./ vs canonical here
    def test_chapters_mirrored_byte_identical(self):
        for chap in WOVEN_CHAPTERS:
            copies = _copies_of(chap)
            required = {k: copies[k] for k in ("root", "canonical", "bundle")}
            missing = [name for name, p in required.items() if not p.exists()]
            self.assertEqual(missing, [], f"{chap}: required copies missing: {missing}")
            present = {name: p for name, p in copies.items() if p.exists()}  # dogfood iff present
            digests = {name: _md5(p) for name, p in present.items()}
            self.assertEqual(len(set(digests.values())), 1,
                             f"{chap} copies not byte-identical (mirror_drift): {digests}")

    # tripwire: the 3 chapters stay on the ubiquitous-language ban surface (no forked ban list here)
    def test_woven_chapters_on_ban_surface(self):
        from test_ubiquitous_language import extended_surface
        surface = {p.resolve() for p in extended_surface()}
        for chap in WOVEN_CHAPTERS:
            self.assertIn(_canon(chap).resolve(), surface,
                          f"{chap} dropped off extended_surface() — ban lint no longer covers it")


if __name__ == "__main__":
    unittest.main(verbosity=2)
