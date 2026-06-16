"""test_wireframe_mock_recipe — guards udd-wireframe.md + its worked sample set.

udd-wireframe.md is the recommendation guide (tool-agnostic; no bundled renderer) that turns
design.md's beats 3–4 into something that renders: a Stage-A WIREFRAME (low-fi structural map)
and a Stage-B HTML MOCK (resolve tokens.json semantic -> CSS custom properties; one kit class
per catalog.json component; compose the prototype tree into HTML; mock data -> a self-contained,
no-network screen a headless tool screenshots). A worked two-screen sample (welcome + settings)
proves reuse + token-flip consistency. The recipe binds the UDD JSON contracts read-only.

Owning task: wireframe-mock-recipe (milestone udd-design-loop). Contract §3 FROZEN @ v1
(shared linked tokens.css + kit.css — one semantic-token flip re-renders BOTH screens).
RED until udd-wireframe.md + the 5 sample files exist; GREEN after build.

The mirror tree (`_bundled`) is enforced by test_bundle_parity; this suite checks the CANONICAL
templates tree (tooling/templates/) for content + reuse, mirroring test_design_loop_guide.
"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_TPL = _TOOLING / "templates"
_BUNDLED_TPL = _TOOLING.parent / "src" / "add_method" / "_bundled" / "tooling" / "templates"

_GUIDE = _TPL / "udd-wireframe.md"
_WIREFRAME = _TPL / "wireframe.sample.txt"
_TOKENS_CSS = _TPL / "tokens.sample.css"
_KIT_CSS = _TPL / "kit.sample.css"
_WELCOME = _TPL / "welcome.sample.html"
_SETTINGS = _TPL / "settings.sample.html"

# the bound, read-only UDD contracts (consumed, never reshaped)
_TOKENS_JSON = _TPL / "tokens.sample.json"
_CATALOG_JSON = _TPL / "catalog.sample.json"
_PROTOTYPE_JSON = _TPL / "prototype.sample.json"

# every new artifact must ship byte-identical in the _bundled mirror
_SHIPPED = (
    "udd-wireframe.md", "wireframe.sample.txt", "tokens.sample.css",
    "kit.sample.css", "welcome.sample.html", "settings.sample.html",
)

# the catalog components prototype.sample.json composes (Must 4)
_CATALOG_COMPONENTS = ("Screen", "Card", "Text", "Button")

_HEX = re.compile(r"#[0-9A-Fa-f]{3,8}\b")
_CSS_CLASS = re.compile(r"\.([a-zA-Z][\w-]*)\b")          # kit class definitions
_HTML_CLASS = re.compile(r'class\s*=\s*"([^"]*)"')        # class= usages in HTML


def _text(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else ""


def _html_classes(html: str) -> set[str]:
    out: set[str] = set()
    for group in _HTML_CLASS.findall(html):
        out.update(group.split())
    return out


class TestWireframeMockRecipe(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.guide = _text(_GUIDE)
        cls.guide_lower = cls.guide.lower()
        cls.wireframe = _text(_WIREFRAME)
        cls.tokens_css = _text(_TOKENS_CSS)
        cls.kit_css = _text(_KIT_CSS)
        cls.welcome = _text(_WELCOME)
        cls.settings = _text(_SETTINGS)

    # --- Musts ---

    def test_stage_a_wireframe_is_lowfi(self) -> None:
        # Must 1 — a low-fi STRUCTURAL map (regions + slots), pre-styling
        self.assertTrue(_GUIDE.exists(), f"udd-wireframe.md missing: {_GUIDE}")
        self.assertIn("stage a", self.guide_lower, "udd-wireframe.md must define a Stage-A wireframe")
        self.assertTrue(
            any(t in self.guide_lower for t in ("low-fi", "low fidelity", "low-fidelity", "structural")),
            "Stage A must describe a LOW-FI / structural map",
        )
        self.assertTrue(_WIREFRAME.exists(), f"wireframe.sample.txt missing: {_WIREFRAME}")
        # a low-fi structural map names no colors / pixel styles
        self.assertNotRegex(self.wireframe, _HEX, "wireframe.sample.txt must be pre-styling (no color literals)")
        self.assertNotIn("px", self.wireframe.lower(), "wireframe.sample.txt must be structural (no pixel styles)")

    def test_stage_b_recipe_four_moves(self) -> None:
        # Must 2 — the four moves of the HTML-mock recipe
        self.assertIn("stage b", self.guide_lower, "udd-wireframe.md must define a Stage-B HTML mock")
        for token in ("tokens.json", "css", "catalog.json", "compose", "mock data"):
            self.assertIn(token, self.guide_lower, f"Stage B must name '{token}'")
        self.assertTrue(
            "self-contained" in self.guide_lower or "no-network" in self.guide_lower,
            "Stage B must produce a self-contained / no-network screen",
        )
        self.assertTrue(
            "headless" in self.guide_lower or "screenshot" in self.guide_lower,
            "Stage B must be screenshot-able by a headless tool",
        )

    def test_screens_compose_from_shared_kit(self) -> None:
        # Must 3 — both screens link the SHARED stylesheets, neither hand-styles
        for name, html in (("welcome", self.welcome), ("settings", self.settings)):
            self.assertTrue(html, f"{name}.sample.html missing")
            self.assertIn("tokens.sample.css", html, f"{name} must link the shared tokens.sample.css")
            self.assertIn("kit.sample.css", html, f"{name} must link the shared kit.sample.css")
            self.assertNotRegex(html, re.compile(r"style\s*="), f"{name} must not hand-style (no inline style=)")

    def test_sample_set_exists_and_composes(self) -> None:
        # Must 4 — all 5 samples exist; welcome composes every catalog component as a kit class
        for p in (_WIREFRAME, _TOKENS_CSS, _KIT_CSS, _WELCOME, _SETTINGS):
            self.assertTrue(p.exists(), f"sample missing: {p.name}")
        welcome_classes = _html_classes(self.welcome)
        for comp in _CATALOG_COMPONENTS:
            self.assertIn(
                comp.lower(), welcome_classes,
                f"welcome must compose the '{comp}' catalog component via its kit class '{comp.lower()}'",
            )

    def test_binds_readonly_and_capture_is_evidence(self) -> None:
        # Must 5 — binds the UDD contracts read-only; capture = design-confirm evidence in TASK.md
        for token in ("tokens.json", "catalog.json", "prototype"):
            self.assertIn(token, self.guide_lower, f"udd-wireframe.md must bind '{token}'")
        self.assertTrue(
            "unchanged" in self.guide_lower or "read-only" in self.guide_lower,
            "udd-wireframe.md must bind the contracts read-only / unchanged",
        )
        self.assertIn("evidence", self.guide_lower, "the captured image must be framed as design-confirm evidence")
        self.assertIn("task.md", self.guide_lower, "the capture must be attached/mentioned in the feature's TASK.md")
        # unchanged-shape proxy: the bound JSONs still parse with their key shape
        self.assertIn("semantic", json.loads(_text(_TOKENS_JSON)))
        self.assertIn("Screen", json.loads(_text(_CATALOG_JSON))["components"])
        self.assertIn("root", json.loads(_text(_PROTOTYPE_JSON)))

    def test_bundled_mirror_byte_identical(self) -> None:
        # Must 6 — every new artifact ships byte-identical in the _bundled mirror
        for name in _SHIPPED:
            canon, mirror = _TPL / name, _BUNDLED_TPL / name
            self.assertTrue(canon.exists(), f"canonical missing: {name}")
            self.assertTrue(mirror.exists(), f"_bundled mirror missing: {name}")
            self.assertEqual(
                canon.read_bytes(), mirror.read_bytes(),
                f"parity_break: {name} differs canonical <-> _bundled",
            )

    # --- Rejects ---

    def test_reject_bespoke_screen(self) -> None:
        # bespoke_screen — a screen carrying inline styling instead of kit classes
        for name, p, html in (("welcome", _WELCOME, self.welcome), ("settings", _SETTINGS, self.settings)):
            self.assertTrue(p.exists(), f"{name}.sample.html missing")  # non-vacuous: must exist to be checked
            self.assertNotRegex(html, re.compile(r"style\s*="), f"bespoke_screen: {name} hand-styles inline")

    def test_reject_unbound_token(self) -> None:
        # unbound_token — a literal color in the kit instead of a var() from tokens
        self.assertIn("var(--", self.kit_css, "kit.sample.css must resolve values via var(--…)")
        self.assertNotRegex(self.kit_css, _HEX, "unbound_token: kit.sample.css must hold no hex color literal")

    def test_reject_contract_reshaped(self) -> None:
        # contract_reshaped — a bound JSON mutated rather than bound read-only
        self.assertIn("semantic", json.loads(_text(_TOKENS_JSON)), "tokens.sample.json reshaped")
        self.assertIn("Screen", json.loads(_text(_CATALOG_JSON))["components"], "catalog.sample.json reshaped")
        self.assertIn("root", json.loads(_text(_PROTOTYPE_JSON)), "prototype.sample.json reshaped")

    def test_component_reuse(self) -> None:
        # duplicate_component — the 2nd screen must REUSE a kit class, not redefine it
        kit_classes = set(_CSS_CLASS.findall(self.kit_css))
        welcome_used = _html_classes(self.welcome) & kit_classes
        settings_used = _html_classes(self.settings) & kit_classes
        shared = welcome_used & settings_used
        self.assertTrue(shared, "settings must REUSE >=1 kit class from welcome (duplicate_component)")
        self.assertNotIn("<style", self.settings.lower(), "duplicate_component: settings redefines styles in a <style> block")

    def test_parity_break_named(self) -> None:
        # parity_break — the recipe names the _bundled mirror / parity ship requirement
        self.assertTrue(
            "_bundled" in self.guide or "byte-identical" in self.guide_lower or "parity" in self.guide_lower,
            "udd-wireframe.md must name the _bundled mirror / byte-identical parity ship requirement",
        )

    # --- consistency ---

    def test_token_flip_rerenders_both(self) -> None:
        # both screens link the SAME tokens.css; the kit resolves semantic vars defined there,
        # so flipping one semantic token re-renders BOTH screens.
        self.assertIn("tokens.sample.css", self.welcome)
        self.assertIn("tokens.sample.css", self.settings)
        semantic_vars = set(re.findall(r"--(semantic-[\w-]+)\s*:", self.tokens_css))
        self.assertTrue(semantic_vars, "tokens.sample.css must define --semantic-* custom properties")
        kit_refs = set(re.findall(r"var\(--(semantic-[\w-]+)\)", self.kit_css))
        self.assertTrue(
            kit_refs & semantic_vars,
            "kit.sample.css must resolve a --semantic-* var defined in tokens.sample.css (token-flip path)",
        )


if __name__ == "__main__":
    unittest.main()
