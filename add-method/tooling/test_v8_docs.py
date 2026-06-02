#!/usr/bin/env python3
"""Structural proof of the v8 onboarding docs — the user's first-contact docs are AI-first.

The onboarding docs (GETTING-STARTED.md, README.md) are where a new user meets ADD. v8 re-leads them
with the conversational entry (`/add`) and the milestone on-ramp (request -> intake -> milestone ->
one-approval -> self-driving run), demoting the raw `add.py` walk to the agent's hands / escape hatch.
The seven-phase walkthrough STAYS — it is the loop the agent drives — but it is no longer the first
thing the user is told to hand-type.

Two invariants are enforced:
  - the HONESTY RULE on prose artifacts: v7-designed one-approval/auto behavior is labelled
    "as designed in v7" vs shipped v6 (the terse orientation block is exempt; these docs are NOT);
  - the glossary defines "On-ramp" and stays byte-identical across both trees.

HONEST SCOPE (same caveat as the other v8 guards): these tests prove the docs' WORDS lead AI-first --
NOT that a reader follows them. Words-exist != method-works.

Run: python3 -m unittest test_v8_docs -v
"""
import hashlib
import re
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_REPO = _ADD_METHOD.parent

GETTING_STARTED = _ADD_METHOD / "GETTING-STARTED.md"
README = _ADD_METHOD / "README.md"
GLOSSARY = _ADD_METHOD / "docs" / "appendix-c-glossary.md"
GLOSSARY_DOGFOOD = _REPO / ".add" / "docs" / "appendix-c-glossary.md"


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def _before_phase_walk(text: str) -> str:
    """The lead-in of GETTING-STARTED, before the seven-phase walkthrough begins."""
    low = text.lower()
    for marker in ("walk the seven phases", "phase 1 — specify", "## 4 ", "seven phases"):
        i = low.find(marker)
        if i != -1:
            return text[:i]
    return text


class V8DocsTest(unittest.TestCase):
    # match the slash-COMMAND /add only — not the path .../add.py nor the package @mrq/add
    SLASH_ADD = re.compile(r"(?<![\w@/])/add(?![\w.])")

    # --- GETTING-STARTED leads AI-first ------------------------------------
    def test_getting_started_leads_ai_first(self):
        lead = _before_phase_walk(GETTING_STARTED.read_text(encoding="utf-8")).lower()
        self.assertTrue(self.SLASH_ADD.search(lead),
                        "GETTING-STARTED must introduce the `/add` command before the manual phase-walk")
        self.assertIn("intake", lead, "GETTING-STARTED must name intake in the lead-in")
        self.assertIn("milestone", lead, "GETTING-STARTED must name the milestone on-ramp in the lead-in")

    # --- README Use-it is agent-first --------------------------------------
    def test_readme_use_it_is_agent_first(self):
        low = README.read_text(encoding="utf-8").lower()
        i = low.find("## use it")
        self.assertNotEqual(i, -1, "README must have a 'Use it' section")
        section = low[i:i + 600]
        self.assertTrue(self.SLASH_ADD.search(section),
                        "README 'Use it' must lead with the `/add` command (talk to the agent)")

    # --- prose artifacts label designed-vs-shipped -------------------------
    def test_docs_label_designed_vs_shipped(self):
        blob = (GETTING_STARTED.read_text(encoding="utf-8") + README.read_text(encoding="utf-8")).lower()
        self.assertTrue(re.search(r"as designed in v7|designed in v7|v7.{0,30}not.{0,10}ship|shipped.{0,10}v6", blob),
                        "onboarding prose must label v7-designed-vs-shipped (honesty rule on prose artifacts)")

    # --- glossary defines On-ramp, both trees identical --------------------
    def test_glossary_defines_onramp(self):
        for p in (GLOSSARY, GLOSSARY_DOGFOOD):
            self.assertTrue(p.exists(), f"missing {p}")
        self.assertEqual(_md5(GLOSSARY), _md5(GLOSSARY_DOGFOOD),
                         "appendix-c-glossary.md differs between canonical and dogfood trees")
        low = GLOSSARY.read_text(encoding="utf-8").lower()
        self.assertTrue(re.search(r"\*\*on-ramp\*\*", low),
                        "glossary must define the term **On-ramp**")


if __name__ == "__main__":
    unittest.main(verbosity=2)
