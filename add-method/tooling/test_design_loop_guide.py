"""test_design_loop_guide — guards design.md, the UDD design-definition loop guide.

design.md is an on-demand guide (loaded like advisor.md / confidence.md) that takes a UI
feature from the domain to a human-confirmed captured screen BEFORE build, via FOUR ordered
beats: review-domain → research-components → wireframe → render-capture-confirm. It stays
tool-agnostic (the engine never renders; capture is a recommended recipe), reuses catalog
components before inventing, keeps design-confirm before build, binds the existing UDD
contracts read-only, and keeps identity values human-owned.

Owning task: design-loop-guide (milestone udd-design-loop). Contract §3 FROZEN @ v1.
RED until design.md exists + its seams are wired; GREEN after build.

The mirror trees (`_bundled`, dogfood `.claude/`) are enforced by test_bundle_parity; this
suite checks the CANONICAL tree (skill/add/) for content + seams, mirroring test_per_step_hooks.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_SKILL = _TOOLING.parent / "skill" / "add"
_DESIGN = _SKILL / "design.md"
_SKILL_MD = _SKILL / "SKILL.md"
_SETUP = _SKILL / "phases" / "0-setup.md"
_SPECIFY = _SKILL / "phases" / "1-specify.md"

# the four beats, in their frozen order (Reject: loop_beats_unordered)
_BEATS = ("review-domain", "research-components", "wireframe", "render-capture-confirm")

# wording_lint imports cleanly only with tooling/ on the path (same as test_per_step_hooks)
sys.path.insert(0, str(_TOOLING))
import wording_lint as _wl  # noqa: E402


def _text(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else ""


class TestDesignLoopGuide(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.guide = _text(_DESIGN)
        cls.guide_lower = cls.guide.lower()
        cls.skill = _text(_SKILL_MD)
        cls.setup = _text(_SETUP)
        cls.specify = _text(_SPECIFY)

    def test_guide_exists(self) -> None:
        self.assertTrue(_DESIGN.exists(), f"design.md missing: {_DESIGN}")

    def test_loop_four_ordered_beats(self) -> None:
        # Must 1 / Reject loop_beats_unordered — all four beats present, in the named order
        idx = []
        for beat in _BEATS:
            i = self.guide.find(beat)
            self.assertNotEqual(i, -1, f"loop_beats_unordered: beat '{beat}' absent from design.md")
            idx.append(i)
        self.assertEqual(idx, sorted(idx), f"loop_beats_unordered: beats out of order — found at {idx}")

    def test_beat1_starts_from_domain(self) -> None:
        # Must 2 — beat 1 derives screens from the domain; entities → presentational components
        for token in ("domain", "screen", "presentational"):
            self.assertIn(token, self.guide_lower, f"beat review-domain must reference '{token}'")

    def test_beat2_reuse_before_invent(self) -> None:
        # Must 3 / Reject invent_before_reuse — check the catalog first, reuse before inventing
        self.assertIn("reuse", self.guide_lower, "beat research-components must say reuse")
        self.assertIn("catalog", self.guide_lower, "beat research-components must reference the catalog")
        self.assertIn("before", self.guide_lower, "beat research-components must be reuse-BEFORE-invent")

    def test_beat3_lowfi_wireframe(self) -> None:
        # Must 4 — a low-fidelity structural layout, before styling
        self.assertIn("wireframe", self.guide_lower)
        self.assertTrue(
            any(t in self.guide_lower for t in ("low-fi", "low fidelity", "low-fidelity", "structural")),
            "beat wireframe must describe a LOW-FI / structural layout",
        )

    def test_beat4_render_capture_confirm_before_build(self) -> None:
        # Must 5 / Reject confirm_after_build — render a mock, capture a real image, confirm BEFORE build
        for token in ("html", "mock", "capture", "design-confirm", "before build"):
            self.assertIn(token, self.guide_lower, f"beat render-capture-confirm must reference '{token}'")

    def test_engine_is_tool_agnostic(self) -> None:
        # Must 6 / Reject engine_renders — the engine never renders; capture is a recommended recipe
        self.assertTrue(
            "engine never render" in self.guide_lower or "never renders" in self.guide_lower,
            "engine_renders: design.md must state the engine never renders",
        )
        self.assertTrue(
            "recommend" in self.guide_lower or "tool-agnostic" in self.guide_lower,
            "design.md must frame capture as a recommended, tool-agnostic recipe",
        )
        self.assertIn("evidence", self.guide_lower, "the captured image must be framed as design-confirm evidence")

    def test_binds_contracts_unchanged(self) -> None:
        # Must 8 / Reject data_contract_changed — binds the UDD contracts read-only
        for token in ("tokens.json", "catalog.json", "prototypes/"):
            self.assertIn(token, self.guide, f"design.md must bind '{token}'")
        self.assertTrue(
            "unchanged" in self.guide_lower or "read-only" in self.guide_lower or "never alter" in self.guide_lower,
            "data_contract_changed: design.md must bind the data contract read-only / unchanged",
        )

    def test_identity_human_owned(self) -> None:
        # Reject identity_autopicked — identity values stay human-owned
        self.assertIn("identity", self.guide_lower)
        self.assertTrue(
            "human-owned" in self.guide_lower or "never auto-pick" in self.guide_lower
            or "never invent" in self.guide_lower,
            "identity_autopicked: design.md must keep identity values human-owned",
        )

    def test_discoverable_in_skill_on_demand(self) -> None:
        # Must 7 — listed in SKILL.md's on-demand guides
        self.assertIn("design.md", self.skill, "SKILL.md must cross-ref design.md (on-demand list)")

    def test_discoverable_from_setup_and_specify(self) -> None:
        # Must 7 — a thin pointer from both phase guides
        self.assertIn("design.md", self.setup, "phases/0-setup.md must reference design.md")
        self.assertIn("design.md", self.specify, "phases/1-specify.md must reference design.md")

    def test_design_in_wording_surface(self) -> None:
        # Must 7 — the new guide joins the linted surface (presence, not a magic count)
        names = [Path(f).name for f in _wl.surface_files()]
        self.assertIn("design.md", names, "design.md must be part of the wording-lint surface")


if __name__ == "__main__":
    unittest.main()
