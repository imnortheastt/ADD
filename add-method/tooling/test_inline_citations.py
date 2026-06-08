#!/usr/bin/env python3
"""Red→green suite for v21 inline-citations (.add/tasks/inline-citations/TASK.md §3 FROZEN @ v1).

Pins the FROZEN contract (branch: ALLOW `;`-joined multi-cites): the three EXISTING book chapters
02-the-flow · 03-step-1-specify · 09-the-loop carry inline [Author Year] citations at the grounded
points, and EVERY cite RESOLVES to an appendix-g entry key (the resolution backbone, `;`-aware so a
multi-cite [A; B] resolves each key). The weave lands in every target chapter, the load-bearing
"the AI never grades its own work" point in 09 carries [Yuan et al. 2024], and ≥1 REAL `;`-joined
multi-cite appears in prose so the split branch is exercised by a genuine cite (not a synthetic
string). The 3 chapters stay ×4 byte-identical; appendix-g stays frozen at 27 keys.

Citation APTNESS — whether a source genuinely GROUNDS the claim it is attached to — is OUT OF SCOPE
here by contract: it is a human §6 SEMANTIC check (verified against the PRIMARY SOURCE for any claim
more specific than the appendix annotation). A green suite is necessary, never sufficient, for PASS.

The regexes are COPIED verbatim from test_foundations_chapter.py (the frozen task-2 test is NOT
imported, edited, or refactored — copy, don't couple). Only `extended_surface` is imported, from the
ubiquitous-language test, so the ban-surface tripwire ties to the real file set without forking a list.

RED until BUILD weaves the cites: the chapters carry no [Author Year] yet, so the deliverable asserts
(resolve / per-chapter / yuan / real-multi-cite) fail for the RIGHT reason (no cites woven), not a
broken harness. The invariant guards (appendix==27, ×4 parity, on-ban-surface) start green and protect
against regressions introduced during the weave.

Run: python3 -m unittest test_inline_citations -v
"""
import hashlib
import re
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_REPO = _ADD_METHOD.parent

WOVEN_CHAPTERS = ("02-the-flow.md", "03-step-1-specify.md", "09-the-loop.md")
APPENDIX_G = "appendix-g-references.md"
YUAN = "Yuan et al. 2024"          # the load-bearing "AI never grades its own work" anchor in 09
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

# inline citation form [Author Year] / [Org 2026a] / [Surname et al. 2023] — year-anchored so it does
# NOT match nav/markdown links like [Contents](./README.md) or [03 Step 1](...) (no year token).
# COPIED from test_foundations_chapter.py; widened with a trailing [^\[\]]* so a `;`-joined multi-cite
# body ([Schmidhuber 2003; Zelikman et al. 2023]) is captured whole, then split on "; " below.
_BRACKET_RE = re.compile(r"\[([^\[\]]*\b(?:19|20)\d{2}[a-z]?[^\[\]]*)\]")
# the entry-lead key inside appendix-g: "- **Title** (Author Year) — …" → first (… Year) parenthetical.
_ENTRY_PREFIX = "- **"
_KEY_RE = re.compile(r"\(([^)]*\b(?:19|20)\d{2}[a-z]?)\)")


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def extract_cites(text: str) -> list:
    """Every cite-key in text, `;`-aware: a bracket body carrying >=1 year, split on '; '."""
    keys = []
    for body in _BRACKET_RE.findall(text):
        for piece in body.split("; "):
            piece = piece.strip()
            if piece:
                keys.append(piece)
    return keys


def multi_cite_bodies(text: str) -> list:
    """Bracket bodies that are REAL `;`-joined multi-cites (carry a '; ')."""
    return [body for body in _BRACKET_RE.findall(text) if "; " in body]


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


class InlineCitationsTest(unittest.TestCase):

    # 1 — THE RESOLUTION BACKBONE: every inline cite in all 3 chapters resolves (dangling_citation)
    def test_every_inline_cite_resolves(self):
        keys = _appendix_g_keys()
        self.assertTrue(keys, "appendix-g produced no cite-keys — extraction or appendix is broken")
        all_cites = []
        for chap in WOVEN_CHAPTERS:
            p = _canon(chap)
            self.assertTrue(p.exists(), f"missing chapter {p}")
            all_cites.extend(extract_cites(_read(p)))
        self.assertTrue(all_cites, "no inline [Author Year] citation woven into any of the 3 chapters yet")
        dangling = sorted({c for c in all_cites} - keys)
        self.assertEqual(dangling, [],
                         f"inline cites resolve to no appendix-g entry (dangling_citation): {dangling}")

    # 2 — the weave lands in EVERY target chapter (chapter_ungrounded)
    def test_weave_lands_in_every_chapter(self):
        keys = _appendix_g_keys()
        for chap in WOVEN_CHAPTERS:
            cites = [c for c in extract_cites(_read(_canon(chap))) if c in keys]
            self.assertGreaterEqual(len(cites), 1,
                                    f"{chap} carries no resolving cite (chapter_ungrounded)")

    # 3 — the load-bearing anchor: [Yuan et al. 2024] in 09 ("the AI never grades its own work")
    def test_yuan_anchor_in_loop(self):
        cites = extract_cites(_read(_canon("09-the-loop.md")))
        self.assertIn(YUAN, cites,
                      f"09-the-loop is missing the load-bearing anchor [{YUAN}]")

    # 4 — a REAL `;`-joined multi-cite appears in prose AND resolves (exercises the split branch)
    def test_real_multi_cite_present_and_resolves(self):
        keys = _appendix_g_keys()
        bodies = []
        for chap in WOVEN_CHAPTERS:
            bodies.extend(multi_cite_bodies(_read(_canon(chap))))
        self.assertTrue(bodies,
                        "no REAL `;`-joined multi-cite in prose — the ALLOW-branch `;`-split is dead code")
        for body in bodies:
            pieces = [p.strip() for p in body.split("; ") if p.strip()]
            self.assertGreaterEqual(len(pieces), 2, f"multi-cite did not split into ≥2 keys: [{body}]")
            unresolved = sorted(set(pieces) - keys)
            self.assertEqual(unresolved, [],
                             f"a half of multi-cite [{body}] resolves to nothing: {unresolved}")

    # 5 — appendix-g stays frozen at 27 keys (appendix_reopened)
    def test_appendix_g_frozen(self):
        n = len(_appendix_g_keys())
        self.assertEqual(n, APPENDIX_G_KEY_COUNT,
                         f"appendix-g key count changed to {n} (appendix_reopened — the 27 are frozen)")

    # 6 — the 3 chapters stay mirrored ×4 byte-identical (mirror_drift)
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

    # 7 — tripwire: the 3 chapters stay on the ubiquitous-language ban surface (no forked ban list here)
    def test_woven_chapters_on_ban_surface(self):
        from test_ubiquitous_language import extended_surface
        surface = {p.resolve() for p in extended_surface()}
        for chap in WOVEN_CHAPTERS:
            self.assertIn(_canon(chap).resolve(), surface,
                          f"{chap} dropped off extended_surface() — ban lint no longer covers it")


if __name__ == "__main__":
    unittest.main(verbosity=2)
