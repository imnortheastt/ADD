"""test_semantic_inventory.py — the v17 semantic-inventory red→green suite.

Pins the frozen contract in .add/tasks/semantic-inventory/TASK.md §3: `semantic-inventory`
is a DETERMINISTIC preservation-diff GATE that proves NECESSARY-not-SUFFICIENT preservation
(nothing dropped/renamed/relocated; every safety invariant's anchors intact in a tight
list-item window; no listed exception introduced). It refuses a verbatim-text diff and a
model-judged "same meaning?" check — both mis-gate a good reword. The INVERSION class (an
added exception around surviving anchors) is CEDED, by name, to human review + indicative eval.

One test per §2 scenario. Fixtures are temp files / direct dataclasses; surface tests read the
canonical add-method/skill/add tree (mirrors byte-identical via test_bundle_parity/test_tree_parity).

Run: python3 -m unittest test_semantic_inventory -v
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import semantic_inventory as si
import wording_lint as wl

_TOOLING = Path(__file__).resolve().parent


def _write(dir_path: Path, name: str, body: str) -> Path:
    p = dir_path / name
    p.write_text(body, encoding="utf-8")
    return p


# A minimal, self-consistent inventory doc used by machinery tests (kept off the real surface).
_MINI_INVENTORY = """# SEMANTIC_INVENTORY — fixture

## token_layer
- a.md: PASS, HARD-STOP, frozen_scope
- b.md: RISK-ACCEPTED

## invariants
- security-always-hardstop @ a.md | anchors: security, HARD-STOP, always | neg: unless, except
- never-weaken-test @ a.md | anchors: weaken, never, test | neg: unless

## coverage
- security finding is always -> security-always-hardstop
- weaken a test -> never-weaken-test

## cede_list
- inversion around surviving anchors (an added exception that keeps every anchor)
- positivity / scope judgment
"""

# A surface fixture a.md that satisfies the mini inventory (every token + both invariants green).
_MINI_A = """# a

- a **security** finding is **always** a `HARD-STOP`.
- never **weaken** a `test` or edit a frozen contract.

The gate records `PASS` and notes `frozen_scope` on a scope change.
"""
_MINI_B = "A signed `RISK-ACCEPTED` is non-security only.\n"


class TestInventoryLoad(unittest.TestCase):
    def test_inventory_single_source(self) -> None:
        """§2: the gate loads units/invariants FROM the doc (no hardcoded duplicate) + prints its path."""
        with tempfile.TemporaryDirectory() as d:
            ip = _write(Path(d), "SEMANTIC_INVENTORY.md",
                        _MINI_INVENTORY.replace("frozen_scope", "sentinel_code_xyz"))
            inv = si.load_inventory(ip)
            tokens = [t for t, _f in inv.token_layer]
            self.assertIn("sentinel_code_xyz", tokens)
            self.assertNotIn("frozen_scope", tokens)
            self.assertEqual({iv.id for iv in inv.invariants},
                             {"security-always-hardstop", "never-weaken-test"})

    def test_main_prints_inventory_path(self) -> None:
        """§2: the gate reports the inventory path it read."""
        with tempfile.TemporaryDirectory() as d:
            ip = _write(Path(d), "SEMANTIC_INVENTORY.md", _MINI_INVENTORY)
            a = _write(Path(d), "a.md", _MINI_A)
            _write(Path(d), "b.md", _MINI_B)
            rc, out = si.run(["--inventory", str(ip), "--surface", str(a), str(Path(d) / "b.md")])
            self.assertEqual(rc, 0, out)
            self.assertIn(str(ip), out)


class TestSpotCheckScope(unittest.TestCase):
    def test_spot_check_scopes_to_named_files(self) -> None:
        """--surface <one file> judges only that file's units — never flags another file's tokens as dropped."""
        with tempfile.TemporaryDirectory() as d:
            ip = _write(Path(d), "SEMANTIC_INVENTORY.md", _MINI_INVENTORY)
            a = _write(Path(d), "a.md", _MINI_A)
            _write(Path(d), "b.md", _MINI_B)  # holds RISK-ACCEPTED, declared @ b.md — out of scope here
            rc, out = si.run(["--inventory", str(ip), "--surface", str(a)])
            self.assertEqual(rc, 0, out)                       # b.md's token is NOT flagged dropped
            self.assertNotIn("unit_dropped", out)


class TestTokenChecks(unittest.TestCase):
    def test_unit_dropped(self) -> None:
        """§2: a frozen token removed from its file -> unit_dropped, exit 1."""
        inv = si.Inventory(token_layer=[("frozen_scope", "a.md")])
        with tempfile.TemporaryDirectory() as d:
            a = _write(Path(d), "a.md", "nothing relevant here.\n")
            found = si.check_tokens(inv, [a])
            self.assertEqual([f.code for f in found], ["unit_dropped"])

    def test_unit_relocated(self) -> None:
        """§2: a frozen token MOVED to another file -> unit_relocated (present, wrong file)."""
        inv = si.Inventory(token_layer=[("frozen_scope", "a.md")])
        with tempfile.TemporaryDirectory() as d:
            a = _write(Path(d), "a.md", "nothing relevant here.\n")
            b = _write(Path(d), "b.md", "the `frozen_scope` code moved here.\n")
            found = si.check_tokens(inv, [a, b])
            self.assertEqual([f.code for f in found], ["unit_relocated"])

    def test_clean_reword_no_falsepositive(self) -> None:
        """§2: prose around a surviving token reworded -> zero findings (prime invariant)."""
        inv = si.Inventory(token_layer=[("frozen_scope", "a.md"), ("PASS", "a.md")])
        with tempfile.TemporaryDirectory() as d:
            a = _write(Path(d), "a.md",
                       "Completely different wording, yet `frozen_scope` and `PASS` both remain.\n")
            self.assertEqual(si.check_tokens(inv, [a]), [])


class TestInvariantChecks(unittest.TestCase):
    def _inv(self) -> si.Inventory:
        return si.Inventory(invariants=[
            si.Invariant("security-always-hardstop", "a.md",
                         ["security", "HARD-STOP", "always"], ["unless", "except", "RISK-ACCEPTED"]),
        ])

    def test_invariant_broken(self) -> None:
        """§2: a removed scope-qualifier ('always') -> invariant_broken with the id."""
        with tempfile.TemporaryDirectory() as d:
            a = _write(Path(d), "a.md", "- a security finding is a HARD-STOP.\n")  # 'always' dropped
            found = si.check_invariants(self._inv(), [a])
            self.assertEqual([f.code for f in found], ["invariant_broken"])
            self.assertIn("security-always-hardstop", found[0].unit)

    def test_exception_introduced(self) -> None:
        """§2: a neg-anchor inside the window -> exception_introduced."""
        with tempfile.TemporaryDirectory() as d:
            a = _write(Path(d), "a.md",
                       "- a security finding is always a HARD-STOP, unless RISK-ACCEPTED by an owner.\n")
            found = si.check_invariants(self._inv(), [a])
            self.assertEqual([f.code for f in found], ["exception_introduced"])

    def test_inversion_around_anchors_is_ceded(self) -> None:
        """§2: a scope-narrowing that KEEPS every anchor + trips no neg-anchor -> gate passes (BY DESIGN).

        The honest necessary-not-sufficient boundary: this inversion is ceded to review + indicative
        eval, NOT caught here. The doc names the cede (asserted by test_cede_list_present)."""
        with tempfile.TemporaryDirectory() as d:
            # 'always' + 'security' + 'HARD-STOP' all survive; the narrowing word ('rarely') is not a neg-anchor.
            a = _write(Path(d), "a.md",
                       "- a security finding is always a HARD-STOP for code we rarely treat as in scope.\n")
            self.assertEqual(si.check_invariants(self._inv(), [a]), [])

    def test_window_is_anchor_local_not_file(self) -> None:
        """§2: a neg-anchor in a DIFFERENT list-item must NOT trip S3 (window is the item, not the file)."""
        with tempfile.TemporaryDirectory() as d:
            a = _write(Path(d), "a.md",
                       "- a security finding is always a HARD-STOP.\n"
                       "- a separate outcome list may include RISK-ACCEPTED for non-security gaps.\n")
            self.assertEqual(si.check_invariants(self._inv(), [a]), [])


class TestRefusedByDesign(unittest.TestCase):
    def test_verbatim_diff_refused(self) -> None:
        """§2: every check kind is a deterministic diff; a verbatim-text kind is refused by design."""
        self.assertTrue(si.CHECK_KINDS, "the gate must expose its check kinds")
        self.assertNotIn("verbatim", si.CHECK_KINDS)
        self.assertNotIn("text", si.CHECK_KINDS)

    def test_model_judged_refused(self) -> None:
        """§2: no model-in-loop check kind exists — model_judged_gate is refused by design."""
        self.assertNotIn("model", si.CHECK_KINDS)
        self.assertTrue(all(k == "diff" for k in si.CHECK_KINDS),
                        f"a non-diff (e.g. model/verbatim) check leaked in: {si.CHECK_KINDS}")


class TestFreezeTimeChecks(unittest.TestCase):
    def test_invariant_uncovered_at_freeze(self) -> None:
        """§2: a negative_keep_list item mapped to NO invariant -> invariant_uncovered."""
        inv = si.Inventory(
            invariants=[si.Invariant("never-self-fold", "fold.md", ["self-fold", "never"], [])],
            coverage=[("self-fold", "never-self-fold")],
        )
        negatives = [("never self-fold", "boundary"),
                     ("a security finding is always HARD-STOP", "safety")]
        found = si.check_coverage(inv, negatives)
        self.assertEqual([f.code for f in found], ["invariant_uncovered"])
        self.assertIn("security", found[0].unit)

    def test_overclaim_refused(self) -> None:
        """§2: an inventory with no cede_list -> overclaim_sufficient (the doc must name the cede)."""
        inv_no_cede = si.Inventory(cede_present=False)
        self.assertEqual([f.code for f in si.check_cede(inv_no_cede)], ["overclaim_sufficient"])
        inv_cede = si.Inventory(cede_present=True)
        self.assertEqual(si.check_cede(inv_cede), [])


class TestDesignForFailure(unittest.TestCase):
    def test_load_missing_inventory_raises(self) -> None:
        """§2: a missing inventory fails LOUD (InventoryError), never a silent green."""
        with self.assertRaises(si.InventoryError):
            si.load_inventory(_TOOLING / "no_such_inventory_zzz.md")

    def test_main_broken_inventory_exits_2(self) -> None:
        """§2: the CLI exits 2 (not 0) on a missing/malformed inventory — no false green."""
        rc, _ = si.run(["--inventory", str(_TOOLING / "no_such_inventory_zzz.md")])
        self.assertEqual(rc, 2)
        with tempfile.TemporaryDirectory() as d:
            empty = _write(Path(d), "SEMANTIC_INVENTORY.md", "# empty, no sections\n")
            rc2, _ = si.run(["--inventory", str(empty), "--surface", str(empty)])
            self.assertEqual(rc2, 2)


class TestLiveSurfaceGreen(unittest.TestCase):
    def test_live_surface_green(self) -> None:
        """§2: the frozen inventory over the live surface -> 0 findings (every unit + invariant intact)."""
        inv = si.load_inventory()
        findings = si.lint_surface(inv, si.surface_files(), si.negative_keep_list())
        self.assertEqual(findings, [], f"live surface is not green: {[(f.file, f.code, f.unit) for f in findings]}")

    def test_coverage_negative_keep_list(self) -> None:
        """§2: every task-1 negative_keep_list item maps to >=1 frozen invariant (real coverage)."""
        inv = si.load_inventory()
        negatives = si.negative_keep_list()
        self.assertEqual(len(negatives), 5, "expected the 5 frozen task-1 negatives")
        self.assertEqual(si.check_coverage(inv, negatives), [])

    def test_extraction_reproducible(self) -> None:
        """§2: --extract re-derives the per-file token set; a rule-found unit absent from the snapshot is drift."""
        inv = si.load_inventory()
        extracted = si.extract_tokens(si.surface_files())
        # every gate-outcome the rule finds in run.md must be in the frozen snapshot for run.md (no silent miss)
        frozen_run = {t for t, f in inv.token_layer if f.endswith("run.md")}
        run_path = next(p for p in si.surface_files() if p.name == "run.md")
        for tok in extracted.get(str(run_path), []):
            if tok in si.GATE_OUTCOMES:
                self.assertIn(tok, frozen_run, f"{tok} extracted from run.md but missing from the snapshot (drift)")

    def test_surface_is_the_19_file_contract(self) -> None:
        """The surface matches wording-lint's 19-file contract (same canonical tree)."""
        self.assertEqual([str(p) for p in si.surface_files()],
                         [str(p) for p in wl.surface_files()])


if __name__ == "__main__":
    unittest.main()
