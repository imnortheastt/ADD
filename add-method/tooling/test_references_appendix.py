#!/usr/bin/env python3
"""Red→green suite for v21 references-appendix (.add/tasks/references-appendix/TASK.md §3).

Pins the FROZEN contract: appendix-g-references.md is a curated, VERIFIED references appendix —
4 themed sections, an author-year entry schema, a spec-kit↔ADD table with a divergence note, no
[UNVERIFIED] source, mirrored byte-identical across all 4 book copies. Every check PARSES the
shipped doc (asserts behaviour of the artifact, never an internal), so a build that ships a
malformed/ungrounded/unverified entry — or forgets a copy — turns one of these red.

RED until BUILD writes appendix-g-references.md: the file is missing, so the copy/parse asserts
fail for the RIGHT reason (no implementation yet), not a broken harness.

Run: python3 -m unittest test_references_appendix -v
"""
import hashlib
import re
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_REPO = _ADD_METHOD.parent

APPENDIX = "appendix-g-references.md"

# The 4 book copies (root ./ · canonical · bundle · dogfood) — all must carry the appendix byte-identical.
COPIES = {
    "root":      _REPO / APPENDIX,
    "canonical": _ADD_METHOD / "docs" / APPENDIX,
    "bundle":    _ADD_METHOD / "src" / "add_method" / "_bundled" / "docs" / APPENDIX,
    "dogfood":   _REPO / ".add" / "docs" / APPENDIX,
}
CANONICAL = COPIES["canonical"]

# The exactly-four themed section names (per §3 DOC STRUCTURE).
THEMES = (
    "Recursive self-improvement",
    "Autonomous & agentic workflows",
    "Spec-driven development & spec-kit",
    "Tests-first & verification",
)

# An entry is a bold-title bullet: "- **Title** (Author Year) — https://… — type. annotation ↔ ADD: relevance"
_ENTRY_PREFIX = "- **"
_KEY_RE = re.compile(r"\([^)]*\b(?:19|20)\d{2}[a-z]?\)")   # (Author 2003) / (Yao et al. 2023a) / (Anthropic 2026)
_URL_RE = re.compile(r"https?://\S+")
_ADD_REL = "↔ ADD:"


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def _entry_lines(text: str) -> list[str]:
    return [ln for ln in text.splitlines() if ln.startswith(_ENTRY_PREFIX)]


class ReferencesAppendixTest(unittest.TestCase):
    def _canon_text(self) -> str:
        self.assertTrue(CANONICAL.exists(),
                        f"missing {CANONICAL} — BUILD has not written the appendix yet")
        return _read(CANONICAL)

    def test_appendix_exists_in_all_four_copies_byte_identical(self):
        # The 3 tracked copies (root · canonical · bundle) are REQUIRED. The dogfood `.add/docs/`
        # copy is gitignored and absent in a packaged install / CI — included only when present
        # (mirroring test_tree_parity / test_bundle_parity's skip-guard so this never spuriously fails).
        required = {k: COPIES[k] for k in ("root", "canonical", "bundle")}
        missing = [name for name, p in required.items() if not p.exists()]
        self.assertEqual(missing, [], f"required appendix copies missing: {missing}")
        present = {name: p for name, p in COPIES.items() if p.exists()}   # dogfood included iff .add/ present
        digests = {name: _md5(p) for name, p in present.items()}
        self.assertEqual(
            len(set(digests.values())), 1,
            f"book copies not byte-identical (mirror_drift): {digests}")

    def test_four_themed_sections_present(self):
        text = self._canon_text()
        headings = [ln for ln in text.splitlines() if ln.startswith("## ")]
        for theme in THEMES:
            self.assertTrue(any(theme in h for h in headings),
                            f"themed section missing: {theme!r}")
        # every entry sits under one of the 4 theme headings (no unthemed_source)
        current = None
        for ln in text.splitlines():
            if ln.startswith("## "):
                current = ln
            elif ln.startswith(_ENTRY_PREFIX):
                self.assertIsNotNone(current, f"entry before any section: {ln[:60]}")
                self.assertTrue(any(t in current for t in THEMES),
                                f"entry under a non-theme section {current!r}: {ln[:60]}")

    def test_every_entry_is_well_formed(self):
        text = self._canon_text()
        entries = _entry_lines(text)
        self.assertGreaterEqual(len(entries), 18,
                                f"curated floor not met: {len(entries)} entries (<18)")
        for ln in entries:
            self.assertRegex(ln, r"\*\*.+?\*\*", f"entry has no bold title: {ln[:70]}")
            self.assertTrue(_KEY_RE.search(ln), f"entry has no (Author Year) cite-key: {ln[:70]}")
            self.assertTrue(_URL_RE.search(ln), f"entry has no http(s) link: {ln[:70]}")
            self.assertIn(_ADD_REL, ln, f"entry has no '↔ ADD:' relevance (ungrounded): {ln[:70]}")

    def test_no_unverified_token_and_links_present(self):
        text = self._canon_text()
        self.assertNotIn("unverified", text.lower(),
                         "an [UNVERIFIED] / 'unverified' marker shipped (unverified_source_shipped)")
        for ln in _entry_lines(text):
            self.assertTrue(_URL_RE.search(ln), f"entry missing a link: {ln[:70]}")

    def test_speckit_add_table_present_with_divergence(self):
        text = self._canon_text()
        low = text.lower()
        self.assertIn("spec-kit", low, "no spec-kit↔ADD comparison present")
        for phase in ("constitution", "specify", "plan", "tasks", "implement"):
            self.assertIn(phase, low, f"spec-kit phase not mapped in the table: {phase}")
        # the divergence note names ADD's three additions
        self.assertTrue(re.search(r"test.?first|failing.?test", low),
                        "divergence note omits the tests-first gate")
        self.assertIn("fold", low, "divergence note omits observe→fold")
        self.assertTrue(re.search(r"dynamic.{0,12}loop|goal.?loop|hold.{0,6}reopen", low),
                        "divergence note omits the dynamic goal-loop")

    def test_cite_key_scheme_documented(self):
        text = self._canon_text()
        low = text.lower()
        self.assertTrue(re.search(r"how to cite|cite-key|citation", low),
                        "no 'How to cite' / cite-key documentation present")
        self.assertIn("et al.", text, "cite-key rules omit the 3+ author 'et al.' form")

    def test_gsd_referenced(self):
        # User-requested: GSD (get-shit-done) must be present as a verified entry + a GSD↔ADD contrast.
        # This freezes the STRUCTURE (a real GSD entry + a doc-time contrast in the comparison), NOT
        # GSD's exact phase-cycle wording — that is primary-source-confirmed at BUILD and written into
        # the appendix then (the WebFetch of the GSD repo hit rendering errors, so the cycle tokens are
        # not yet primary-confirmed; freezing the literal string here would risk a frozen-test/fact clash).
        text = self._canon_text()
        low = text.lower()
        self.assertTrue("get-shit-done" in low or "gsd" in low,
                        "GSD / get-shit-done is not referenced (user-requested source missing)")
        # a real GSD entry: a bold-title bullet that names GSD/get-shit-done and carries a link
        gsd_entries = [ln for ln in _entry_lines(text)
                       if ("gsd" in ln.lower() or "get-shit-done" in ln.lower()) and _URL_RE.search(ln)]
        self.assertTrue(gsd_entries, "no verified GSD entry (bold title + link) found")
        # the project's load-bearing contrast (from PROJECT.md goal — a primary, confirmed fact)
        self.assertIn("doc-time", low, "the 'less doc-time than GSD' contrast is not stated")


if __name__ == "__main__":
    unittest.main(verbosity=2)
