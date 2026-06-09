#!/usr/bin/env python3
"""Marker guard for the decision arc (task: report-arc, milestone v23).

report-template.md gains an ARC block — three labelled lines goal:/done:/plan:
rendered ABOVE the five existing blocks — that every human gate carries, so the
human confirms with full sight of the work's arc (the goal it serves, what's
proven, the plan ahead) rather than a local snapshot.

The shipped skill doc is the artifact under test. We assert the frozen §3 ARC
contract: the three labels in order above SUMMARY, the seven-gate rule, the
engine-source mapping, and SKILL.md's pointer naming the ARC. Parity across the
three skill trees is guarded by test_tree_parity + test_bundle_parity; banned
wording by test_wording_lint + test_ubiquitous_language. The arc's per-gate
quality is a human read at the gate — this file guards only the mechanical shape.

Red before the build edit, green after. Run: python3 -m unittest test_report_arc -v
"""
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
CANON_SKILL = _TOOLING.parent / "skill" / "add"
TEMPLATE = CANON_SKILL / "report-template.md"
SKILL = CANON_SKILL / "SKILL.md"

# the seven human gates the arc is required at (frozen §3)
GATES = (
    "baseline-lock",
    "contract-freeze",
    "verify",
    "intake",
    "scope",
    "milestone-close",
    "graduation",
)


class ReportArcMarkerTest(unittest.TestCase):
    def setUp(self):
        self.text = TEMPLATE.read_text(encoding="utf-8")

    def test_arc_block_has_three_labels_in_order(self):
        self.assertIn("ARC", self.text, "report-template.md must define an ARC block")
        for label in ("goal:", "done:", "plan:"):
            self.assertIn(
                label, self.text, f"the ARC block must carry the label {label!r}"
            )
        g = self.text.index("goal:")
        d = self.text.index("done:")
        p = self.text.index("plan:")
        self.assertTrue(
            g < d < p, "ARC labels must appear in order: goal: · done: · plan:"
        )

    def test_arc_renders_above_the_five_blocks(self):
        # ARC first, above SUMMARY; the unchanged five blocks all remain present.
        self.assertIn("ARC", self.text, "report-template.md must define an ARC block")
        self.assertIn("SUMMARY", self.text, "the SUMMARY block must remain present")
        self.assertLess(
            self.text.index("ARC"),
            self.text.index("SUMMARY"),
            "the ARC block must render ABOVE SUMMARY",
        )
        for block in ("SUMMARY", "DECISION", "FLAGS", "EVIDENCE", "NEXT"):
            self.assertIn(block, self.text, f"the {block} block must remain present")

    def test_arc_required_at_all_seven_gates(self):
        for gate in GATES:
            self.assertIn(
                gate,
                self.text,
                f"the ARC must be named as required at the {gate!r} gate",
            )

    def test_arc_facts_are_engine_sourced(self):
        for src in ("m-goal", "DECIDE NEXT"):
            self.assertIn(
                src, self.text, f"the ARC source mapping must name {src!r}"
            )
        # the 'done' line maps to exit-criteria met/total + tasks done
        self.assertTrue(
            "exit-criteria" in self.text or "exit criteria" in self.text,
            "the ARC 'done' line must map to exit-criteria met/total",
        )

    def test_at_least_one_per_gate_example(self):
        # one shared shape, per-gate content: >=1 worked example beyond the spec line.
        self.assertIn(
            "example",
            self.text.lower(),
            "the template must carry >=1 worked per-gate example",
        )
        self.assertGreaterEqual(
            self.text.count("goal:"),
            2,
            "expected the arc spec plus >=1 worked example (>=2 'goal:' lines)",
        )

    def test_skill_pointer_names_the_arc(self):
        skill = SKILL.read_text(encoding="utf-8")
        i = skill.find("report-template")
        self.assertNotEqual(i, -1, "SKILL.md must point at report-template.md")
        window = skill[max(0, i - 200) : i + 400]
        self.assertIn(
            "ARC",
            window,
            "SKILL.md's report-template pointer must name the ARC block",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
