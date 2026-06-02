#!/usr/bin/env python3
"""Structural proof of the v7 rubric change — auto by default + the one-approval front.

v7 deliberately REVERSES the v6/foundation-version-2 default: `auto` becomes the dial default
(retiring reject code `auto_by_default`), and the human-led front compresses to a SINGLE approval
at the contract-freeze seam. Two v6 safeties are preserved and asserted here:

  - the contract freeze stays HUMAN (the AI drafts the bundle, a human approves the seam) — so
    "never self-gate a human-led gate" still holds under an auto default;
  - high-risk / method-defining scope is GUARDED — `auto` is refused and must lower to conservative
    (reject code `unguarded_high_risk_auto`), closing the v6 dogfood blind-spot;
  - security stays a HARD-STOP, always.

HONEST SCOPE (same caveat as v6): these tests prove the rubric's WORDS exist as contracted — NOT
that a run actually honors the one-approval seam or that the high-risk guard is enforced (those are
runtime properties a string check cannot reach; see the v7 OBSERVE deltas + the deferred CI enforcer).
Words-exist != method-works.

Run: python3 -m unittest test_v7_auto_default -v
"""
import hashlib
import re
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_REPO = _ADD_METHOD.parent

CANONICAL_RUN = _ADD_METHOD / "skill" / "add" / "run.md"
DOGFOOD_RUN = _REPO / ".claude" / "skills" / "add" / "run.md"
PRINCIPLES = _ADD_METHOD / "docs" / "01-principles.md"
PRINCIPLES_DOGFOOD = _REPO / ".add" / "docs" / "01-principles.md"


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def _run() -> str:
    return CANONICAL_RUN.read_text(encoding="utf-8")


class V7AutoDefaultTest(unittest.TestCase):
    # --- parity: edits must land in both skill trees -----------------------
    def test_run_md_parity_preserved(self):
        self.assertEqual(_md5(CANONICAL_RUN), _md5(DOGFOOD_RUN),
                         "run.md differs between canonical and dogfood trees — v7 edit broke parity")

    # --- auto is the default ----------------------------------------------
    def test_auto_is_the_default(self):
        low = _run().lower()
        self.assertTrue(re.search(r"auto.{0,12}\(the default\)|auto is the default|default.{0,12}auto", low),
                        "run.md must state auto is the default")
        # the old default must be gone — guards against a half-flip
        self.assertNotIn("conservative (the default)", low,
                         "run.md still calls conservative the default — the v7 flip is incomplete")
        self.assertNotIn("default is conservative", low,
                         "run.md still says the default is conservative — the v7 flip is incomplete")

    # --- principle 5 is preserved (per-scope), only the starting point moved
    def test_dial_stays_per_scope_and_rubric(self):
        low = _run().lower()
        self.assertIn("conservative", low, "conservative must remain available as the lowering")
        self.assertTrue(re.search(r"per-scope|per scope", low),
                        "run.md must keep the dial a per-scope setting (principle 5 intact)")
        self.assertTrue(re.search(r"not an? add\.py|not a.{0,20}flag|engine stays judgment", low),
                        "run.md must keep the dial a rubric, not an add.py flag")

    # --- high-risk scope is guarded (the v6 blind-spot) --------------------
    def test_high_risk_scope_must_lower(self):
        low = _run().lower()
        self.assertTrue(re.search(r"high-risk|method-defining", low),
                        "run.md must name the high-risk / method-defining scope guard")
        self.assertIn("unguarded_high_risk_auto", low,
                      "run.md must name the unguarded_high_risk_auto reject code")

    # --- the one-approval front (the seam stays human) ---------------------
    def test_one_approval_front_at_the_seam(self):
        low = _run().lower()
        self.assertTrue(re.search(r"one approval|single approval|one human approval", low),
                        "run.md must document the single human approval at the seam")
        self.assertTrue(re.search(r"freez.{0,40}contract|contract.{0,40}freez|frozen contract", low),
                        "the one approval must be AT the contract-freeze seam")
        self.assertTrue(re.search(r"draft.{0,80}(scenario|contract)|bundle", low, re.DOTALL),
                        "run.md must say the AI drafts the front bundle for one approval")

    # --- security stays a HARD-STOP ---------------------------------------
    def test_security_hard_stop_unchanged(self):
        low = _run().lower()
        self.assertTrue(re.search(r"security.{0,40}(hard-stop|escalat|human)", low, re.DOTALL),
                        "security must still always escalate / HARD-STOP under the auto default")

    # --- the book principle reframe ---------------------------------------
    def test_principle_five_reframed_to_start_auto(self):
        for p in (PRINCIPLES, PRINCIPLES_DOGFOOD):
            self.assertTrue(p.exists(), f"missing {p}")
        self.assertEqual(_md5(PRINCIPLES), _md5(PRINCIPLES_DOGFOOD),
                         "01-principles.md differs between canonical and dogfood trees")
        low = PRINCIPLES.read_text(encoding="utf-8").lower()
        self.assertTrue(re.search(r"start.{0,20}auto|auto.{0,30}default|default.{0,30}auto", low, re.DOTALL),
                        "principle 5 must reframe to start-auto-lower-on-risk")
        self.assertIn("per scope", low.replace("per-scope", "per scope"),
                      "principle 5 must keep trust earned per scope")


if __name__ == "__main__":
    unittest.main(verbosity=2)
