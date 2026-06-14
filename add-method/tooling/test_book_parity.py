#!/usr/bin/env python3
"""Book-parity guard: the AIDD book lives in two tracked trees that MUST stay
byte-identical — the canonical `add-method/docs/` (bundled into the package by
scripts/prepare_bundle.py) and the repo-root copy (`./NN-*.md`, the
GitHub-readable book the root README's table of contents links to).

Unlike the skill (test_tree_parity) and the engine (test_shared_engine_pin),
this pair had NO guard — which let the root copy drift silently: the root
CHANGELOG stalled at v1.1.0 and chapters 10/11 fell behind add-method/docs with
no test going red. This walks every canonical book file and asserts a
byte-identical twin at the repo root, so no chapter can drift unguarded again.

Excluded from the mirror by design:
  - README.md          — the root README is the repo/book landing page, a
                         different document from add-method/docs/README (the
                         docs index). Compared by neither direction here.
  - CHANGELOG.md, GETTING-STARTED.md at root are deliberate POINTERS to the
    package (not copies), and are not book files — so they never appear in the
    canonical docs tree this guard walks.

Run: python3 -m unittest test_book_parity -v
"""
import hashlib
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_REPO = _ADD_METHOD.parent

CANON_DOCS = _ADD_METHOD / "docs"
ROOT = _REPO

# Files in the canonical docs tree that are NOT part of the root book mirror.
EXCLUDE = {"README.md"}


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def _book_files(root: Path):
    return {
        p.relative_to(root)
        for p in root.rglob("*")
        if p.is_file() and p.name not in EXCLUDE
    }


class BookParityTest(unittest.TestCase):
    def test_book_mirrored_at_repo_root(self):
        if not CANON_DOCS.exists():
            self.skipTest("canonical docs tree absent")
        canon = _book_files(CANON_DOCS)
        self.assertTrue(canon, "no canonical book files found under add-method/docs")

        # 1. every canonical book file has a twin at the repo root
        missing = sorted(str(rel) for rel in canon if not (ROOT / rel).is_file())
        self.assertEqual(
            missing, [],
            "book file(s) missing from the repo-root mirror "
            "(propagate with `cp add-method/docs/<f> ./<f>`):\n  "
            + "\n  ".join(missing),
        )

        # 2. every twin byte-identical
        mismatched = sorted(
            str(rel) for rel in canon
            if _md5(CANON_DOCS / rel) != _md5(ROOT / rel)
        )
        self.assertEqual(
            mismatched, [],
            "book file(s) diverged between add-method/docs and the repo root "
            "(re-sync with `cp add-method/docs/<f> ./<f>`):\n  "
            + "\n  ".join(mismatched),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
