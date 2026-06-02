#!/usr/bin/env python3
"""Structural proof of the v6 dynamic-run rubric (skill/add/run.md).

v6 — The Self-Driving Run — makes the build->verify half a dynamic, self-improving run once the
contract is frozen. The deliverable is a RUBRIC (skill/add/run.md), not engine logic: the engine stays
judgment-free ("engine is truth, harness is intelligence"). This guard asserts STRUCTURE only across
both skill trees (md5 parity) — it grows one section per v6 task:

  scope-lock-trigger : the trigger (frozen contract + red tests) and the touch-boundary
  dynamic-run-engine : fan-out + in-run convergence (loop-until-dry · adversarial verify · critic)
  evidence-auto-gate : what auto-PASSes verify, what always escalates (security = human, always)
  run-emits-deltas   : run findings become `open` competency deltas in OBSERVE
  autonomy-dial      : the run's autonomy is a per-scope setting (v7 flipped the default to auto)

HONEST SCOPE: these tests prove the rubric's WORDS exist as contracted — NOT that the run actually
converges or that the auto-gate is sound. Those are method/runtime properties a string check cannot
reach (see each task's OBSERVE deltas). Words-exist != method-works.

Run: python3 -m unittest test_v6_run -v
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
CANONICAL_SKILL = _ADD_METHOD / "skill" / "add" / "SKILL.md"
DOGFOOD_SKILL = _REPO / ".claude" / "skills" / "add" / "SKILL.md"


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def _run() -> str:
    return CANONICAL_RUN.read_text(encoding="utf-8")


class V6RunRubricTest(unittest.TestCase):
    # --- shared invariants -------------------------------------------------
    def test_run_md_exists_in_both_trees_with_md5_parity(self):
        self.assertTrue(CANONICAL_RUN.exists(), f"missing {CANONICAL_RUN}")
        self.assertTrue(DOGFOOD_RUN.exists(), f"missing {DOGFOOD_RUN}")
        self.assertEqual(_md5(CANONICAL_RUN), _md5(DOGFOOD_RUN),
                         "run.md differs between the canonical and dogfood skill trees")

    def test_skill_md_links_run_and_both_trees_identical(self):
        for skill in (CANONICAL_SKILL, DOGFOOD_SKILL):
            self.assertIn("run.md", skill.read_text(encoding="utf-8"),
                          f"{skill} does not point to run.md")
        self.assertEqual(_md5(CANONICAL_SKILL), _md5(DOGFOOD_SKILL),
                         "the two SKILL.md copies are not byte-identical")

    # --- scope-lock-trigger ------------------------------------------------
    def test_trigger_is_frozen_contract_plus_red_tests(self):
        low = _run().lower()
        self.assertTrue(re.search(r"frozen", low), "run.md must name the frozen contract as the trigger")
        self.assertTrue(re.search(r"red", low), "run.md must require red tests before the run starts")
        self.assertTrue(re.search(r"no frozen contract\s*->?\s*no run|no run", low),
                        "run.md must state: no frozen contract -> no run")

    def test_touch_boundary_may_and_must_not(self):
        text = _run()
        low = text.lower()
        self.assertIn("MUST NOT", text, "run.md must state a MUST NOT touch-boundary")
        # may touch disposable code; must not touch the frozen contract / locked scope
        self.assertTrue(re.search(r"code.{0,40}disposable|disposable.{0,40}code", low, re.DOTALL),
                        "run.md must say code is disposable (the run may rewrite it)")
        self.assertTrue(re.search(r"must not.{0,160}(frozen contract|locked scope)", low, re.DOTALL),
                        "run.md must forbid touching the frozen contract / locked scope")
        self.assertTrue(re.search(r"weaken.{0,40}test|test.{0,40}weaken", low, re.DOTALL),
                        "run.md must forbid weakening tests to pass the build")

    # --- dynamic-run-engine ------------------------------------------------
    def test_dynamic_run_fanout_and_convergence(self):
        low = _run().lower()
        self.assertTrue(re.search(r"fan[- ]?out", low), "run.md must describe fan-out")
        for loop in ("loop-until-dry", "adversarial verif", "completeness-critic"):
            self.assertIn(loop, low, f"run.md must document the '{loop}' convergence loop")

    # --- evidence-auto-gate ------------------------------------------------
    def test_evidence_auto_gate_pass_and_escalation(self):
        text = _run()
        low = text.lower()
        self.assertTrue(re.search(r"auto-?pass", low), "run.md must define what auto-PASSes verify")
        # security always escalates / never auto-passed
        self.assertTrue(
            re.search(r"security.{0,120}(human|hard-stop|never auto|escalat)|"
                      r"(never auto|always escalat|hard-stop).{0,120}security", low, re.DOTALL),
            "run.md must state security always escalates / never auto-passes")
        for residue in ("concurrency", "architecture"):
            self.assertIn(residue, low, f"run.md must escalate the '{residue}' residue")
        self.assertTrue(re.search(r"one outcome|exactly one|no silent", low),
                        "run.md must record exactly one outcome (no silent skip)")

    # --- run-emits-deltas --------------------------------------------------
    def test_run_emits_open_deltas(self):
        low = _run().lower()
        self.assertTrue(re.search(r"\bopen\b.{0,40}delta|delta.{0,40}\bopen\b|open competency delta", low, re.DOTALL),
                        "run.md must say findings become OPEN competency deltas")
        self.assertIn("completeness-critic", low, "run.md must source deltas from the completeness-critic")
        self.assertTrue(re.search(r"fold\.md|fold ritual|human.{0,30}fold", low),
                        "run.md must route deltas to the human-gated fold (v5)")

    # --- autonomy-dial -----------------------------------------------------
    def test_autonomy_dial_per_scope(self):
        text = _run()
        low = text.lower()
        self.assertIn("autonomy:", text, "run.md must name the `autonomy:` per-scope setting")
        self.assertIn("conservative", low, "run.md must name the conservative level")
        # v7: the default flipped conservative -> auto (a deliberate, recorded reversal).
        self.assertTrue(re.search(r"auto.{0,40}\bdefault\b|\bdefault\b.{0,40}auto", low, re.DOTALL),
                        "run.md must state auto is the default (v7 reversal)")
        self.assertTrue(re.search(r"not an? add\.py|not a.{0,20}flag|engine stays judgment", low),
                        "run.md must state the dial is a rubric convention, not an add.py flag")


if __name__ == "__main__":
    unittest.main(verbosity=2)
