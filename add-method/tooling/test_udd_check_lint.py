"""Red suite for udd-check-lint (udd-design-foundation 4/4).

Frozen contract §3 @ v1: wire BOTH pure validators into `add.py check` as a new
SILENT-when-absent "UDD foundation" section, plus the cross-file token resolution
tasks 1+2 deferred.

  - SECTION: cmd_check discovers the named set under `.add/design/` (Fork A) —
    `root/design/tokens.json` · `root/design/catalog.json` · `root/design/prototypes/*.json`;
    composes `_token_layer_violations` + `_catalog_tree_violations` (UNCHANGED) and the
    NEW `_prop_token_resolution_violations`; one FAIL per violation (named code), one PASS
    per clean file; SILENT (no PASS/FAIL/WARN) when no named set; FAIL-CLOSED on malformed
    JSON (named code, never a crash); read-only; the existing check format/exit preserved.
  - NEW PURE `_prop_token_resolution_violations(tokens, catalog, tree)` — resolves every
    tree token-prop alias that targets `semantic` against tokens.json (DTCG $type
    inheritance: $type sits on the GROUP): not found → unresolved_prop_token; $type ≠ the
    catalog PropSpec's token $type → prop_token_type_mismatch. PURE + TOTAL.

These run RED before build: AttributeError (_prop_token_resolution_violations missing) +
the UDD section absent (check stays silent on a design/ project, so the integration reds
see exit 0 / no code rather than the expected FAIL).
"""
import contextlib
import copy
import io
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

import add

_TOOLING = Path(__file__).resolve().parent
_SAMPLES = _TOOLING / "templates"


# ----------------------------------------------------------------------------
# fixtures for the pure cross-file resolver
# ----------------------------------------------------------------------------
def _tokens():
    """A minimal 3-layer token set; $type on the GROUP (DTCG inheritance)."""
    return {
        "primitive": {
            "color": {"$type": "color", "blue-500": {"$value": "#3B82F6"}},
            "space": {"$type": "dimension", "4": {"$value": "4px"}},
        },
        "semantic": {
            "color": {"$type": "color", "accent": {"$value": "{primitive.color.blue-500}"}},
            "space": {"$type": "dimension", "inset-md": {"$value": "{primitive.space.4}"}},
        },
    }


def _catalog():
    return {"components": {"Box": {"props": {
        "bg": {"type": "token", "token": "color"},
        "pad": {"type": "token", "token": "dimension"},
        "label": {"type": "string"},
    }}}}


def _tree(bg="{semantic.color.accent}", pad="{semantic.space.inset-md}", label="hi"):
    return {"root": "b", "elements": {"b": {"type": "Box",
            "props": {"bg": bg, "pad": pad, "label": label}}}}


def _resolve(tokens, catalog, tree):
    """Call the (not-yet-built) cross-file resolver — AttributeError until build."""
    return add._prop_token_resolution_violations(tokens, catalog, tree)


def _pairs(v):
    return [(x[0], x[1]) for x in v]


class PropTokenResolutionTest(unittest.TestCase):
    def test_clean_triple_resolves(self):
        """Every token-prop alias resolves to an existing semantic token of the right $type."""
        self.assertEqual(_resolve(_tokens(), _catalog(), _tree()), [])

    def test_shipped_samples_resolve_clean(self):
        """The shipped sample triple cross-resolves clean (the exit-criterion path)."""
        tok = json.loads((_SAMPLES / "tokens.sample.json").read_text(encoding="utf-8"))
        cat = json.loads((_SAMPLES / "catalog.sample.json").read_text(encoding="utf-8"))
        tree = json.loads((_SAMPLES / "prototype.sample.json").read_text(encoding="utf-8"))
        self.assertEqual(_resolve(tok, cat, tree), [])

    def test_unresolved_prop_token(self):
        """An alias with no match in tokens.json → unresolved_prop_token."""
        v = _resolve(_tokens(), _catalog(), _tree(bg="{semantic.color.ghost}"))
        self.assertIn(("unresolved_prop_token", "elements.b.props.bg"), _pairs(v))
        self.assertNotIn(("unresolved_prop_token", "elements.b.props.pad"), _pairs(v))

    def test_prop_token_type_mismatch(self):
        """A token:color prop bound to a dimension token → prop_token_type_mismatch."""
        v = _resolve(_tokens(), _catalog(), _tree(bg="{semantic.space.inset-md}"))
        self.assertIn(("prop_token_type_mismatch", "elements.b.props.bg"), _pairs(v))
        self.assertNotIn(("prop_token_type_mismatch", "elements.b.props.pad"), _pairs(v))

    def test_group_alias_is_unresolved(self):
        """An alias terminating at a GROUP (no $value), not a token, → unresolved_prop_token."""
        v = _resolve(_tokens(), _catalog(), _tree(bg="{semantic.color}"))
        self.assertIn(("unresolved_prop_token", "elements.b.props.bg"), _pairs(v))

    def test_skips_non_token_and_non_semantic_props(self):
        """The resolver acts ONLY on token-PropSpec × semantic-alias; everything else is task 1/2's."""
        # a string prop (label="hi"), a non-alias literal, and a primitive alias → no cross-file code
        self.assertEqual(_resolve(_tokens(), _catalog(), _tree(bg="#3B82F6")), [],
                         "a non-alias literal is task-2's prop_type_mismatch, not ours")
        self.assertEqual(_resolve(_tokens(), _catalog(), _tree(bg="{primitive.color.blue-500}")), [],
                         "a primitive alias is task-2's non_semantic_prop_token, not ours")

    def test_pure_and_deterministic(self):
        tok, cat = _tokens(), _catalog()
        tree = _tree(bg="{semantic.color.ghost}", pad="{semantic.color.accent}")  # 2 faults: unresolved + type
        snap_tok, snap_cat, snap_tree = copy.deepcopy(tok), copy.deepcopy(cat), copy.deepcopy(tree)
        r1 = _resolve(tok, cat, tree)
        r2 = _resolve(tok, cat, tree)
        self.assertEqual(r1, r2, "deterministic order")
        self.assertIn(("unresolved_prop_token", "elements.b.props.bg"), _pairs(r1))
        self.assertIn(("prop_token_type_mismatch", "elements.b.props.pad"), _pairs(r1))  # pad token:dimension ← color token
        self.assertEqual(tok, snap_tok, "pure — tokens not mutated")
        self.assertEqual(cat, snap_cat, "pure — catalog not mutated")
        self.assertEqual(tree, snap_tree, "pure — tree not mutated")

    def test_skips_malformed_token_propspec(self):
        """A malformed token PropSpec (bad / absent $type) is task-2's malformed_catalog —
        the resolver SKIPS it, never re-flagging (the §3 'no double-flag' clause)."""
        bad_type = {"components": {"Box": {"props": {"bg": {"type": "token", "token": "bogus"}}}}}
        self.assertEqual(_resolve(_tokens(), bad_type, _tree(bg="{semantic.color.accent}")), [],
                         "a token PropSpec naming an unknown $type is malformed_catalog (task 2), not ours")
        no_key = {"components": {"Box": {"props": {"bg": {"type": "token"}}}}}
        self.assertEqual(_resolve(_tokens(), no_key, _tree(bg="{semantic.color.accent}")), [],
                         "a token PropSpec with no 'token' key is malformed_catalog (task 2), not ours")

    def test_skips_token_with_malformed_type(self):
        """If the RESOLVED semantic token's $type is malformed (None / non-string), task-1 owns
        unknown_type — the resolver SKIPS the comparison (the §3 'no double-flag' clause)."""
        # bg + pad both bound to accent, whose token carries a malformed (or absent) $type
        both = _tree(bg="{semantic.color.accent}", pad="{semantic.color.accent}")
        no_dollar = {"semantic": {"color": {"accent": {"$value": "#aaa"}}}}          # no $type anywhere
        self.assertEqual(_resolve(no_dollar, _catalog(), both), [],
                         "a resolved token with no $type is task-1's unknown_type, not our mismatch")
        nonstr_dollar = {"semantic": {"color": {"$type": 42, "accent": {"$value": "#aaa"}}}}  # non-string $type
        self.assertEqual(_resolve(nonstr_dollar, _catalog(), both), [],
                         "a resolved token with a non-string $type is task-1's unknown_type, not our mismatch")


# ----------------------------------------------------------------------------
# integration: the cmd_check "UDD foundation" section over .add/design/
# ----------------------------------------------------------------------------
class CheckUddSectionTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-check-lint-")
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo", "--stage", "mvp"])
        self.design = Path(self.tmp) / ".add" / "design"

    def tearDown(self):
        os.chdir(self._cwd)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write(self, *, tokens=None, catalog=None, trees=None, raw=None):
        self.design.mkdir(parents=True, exist_ok=True)
        if tokens is not None:
            (self.design / "tokens.json").write_text(json.dumps(tokens), encoding="utf-8")
        if catalog is not None:
            (self.design / "catalog.json").write_text(json.dumps(catalog), encoding="utf-8")
        if trees:
            (self.design / "prototypes").mkdir(exist_ok=True)
            for name, t in trees.items():
                (self.design / "prototypes" / f"{name}.json").write_text(json.dumps(t), encoding="utf-8")
        if raw:
            for rel, content in raw.items():
                p = self.design / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(content, encoding="utf-8")

    def _check(self):
        buf = io.StringIO()
        code = 0
        try:
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                add.main(["check"])
        except SystemExit as e:
            code = e.code or 0
        return code, buf.getvalue()

    def test_clean_named_set_passes(self):
        """A clean tokens+catalog+prototype under .add/design/ → check stays green, UDD PASS lines, no writes."""
        self._write(tokens=_tokens(), catalog=_catalog(), trees={"main": _tree()})
        before = {p: p.read_bytes() for p in self.design.rglob("*.json")}
        code, out = self._check()
        self.assertEqual(code, 0, out)
        self.assertIn("layer-valid", out)
        self.assertIn("prototype 'main' valid", out)   # the prototype PASS line, not only the tokens PASS
        after = {p: p.read_bytes() for p in self.design.rglob("*.json")}
        self.assertEqual(before, after, "cmd_check must be read-only")

    def test_token_layer_violation_red(self):
        """A tokens.json cross_layer_citation surfaces as a named FAIL; check exits 1."""
        bad = {
            "primitive": {"color": {"$type": "color", "blue": {"$value": "#3B82F6"}}},
            "component": {"button": {"$type": "color", "bg": {"$value": "{primitive.color.blue}"}}},  # component→primitive
        }
        self._write(tokens=bad)
        code, out = self._check()
        self.assertEqual(code, 1)
        self.assertIn("cross_layer_citation", out)

    def test_catalog_tree_violation_red(self):
        """A prototype citing an uncataloged component surfaces its named code; check exits 1."""
        self._write(catalog={"components": {"Box": {"props": {}}}},
                    trees={"main": {"root": "x", "elements": {"x": {"type": "Ghost", "props": {}}}}})
        code, out = self._check()
        self.assertEqual(code, 1)
        self.assertIn("tree_cites_uncataloged_component", out)

    def test_unresolved_prop_token_red(self):
        """The deferral, half 1: an unresolved token-prop alias goes red."""
        self._write(tokens=_tokens(), catalog=_catalog(),
                    trees={"main": _tree(bg="{semantic.color.ghost}")})
        code, out = self._check()
        self.assertEqual(code, 1)
        self.assertIn("unresolved_prop_token", out)

    def test_prop_token_type_mismatch_red(self):
        """The deferral, half 2: a token-prop $type mismatch goes red."""
        self._write(tokens=_tokens(), catalog=_catalog(),
                    trees={"main": _tree(bg="{semantic.space.inset-md}")})
        code, out = self._check()
        self.assertEqual(code, 1)
        self.assertIn("prop_token_type_mismatch", out)

    def test_malformed_tokens_failclosed(self):
        """A malformed tokens.json → a named FAIL, no traceback; cmd_check still finishes."""
        self._write(raw={"tokens.json": "{ not valid json"})
        code, out = self._check()
        self.assertEqual(code, 1)
        self.assertIn("malformed_tokens_json", out)
        self.assertIn("check:", out)  # the tally still printed — cmd_check did not crash

    def test_malformed_catalog_failclosed(self):
        """A malformed catalog.json → malformed_catalog_json named FAIL, no traceback; cmd_check finishes."""
        self._write(tokens=_tokens(), trees={"main": _tree()},
                    raw={"catalog.json": "{ not valid json"})
        code, out = self._check()
        self.assertEqual(code, 1)
        self.assertIn("malformed_catalog_json", out)
        self.assertIn("check:", out)

    def test_malformed_prototype_failclosed(self):
        """A malformed prototype json → malformed_prototype_json named FAIL, no traceback; cmd_check finishes."""
        self._write(tokens=_tokens(), catalog=_catalog(),
                    raw={"prototypes/main.json": "{ not valid json"})
        code, out = self._check()
        self.assertEqual(code, 1)
        self.assertIn("malformed_prototype_json", out)
        self.assertIn("check:", out)

    def test_no_named_set_is_silent(self):
        """A project with no .add/design/ named set emits NO UDD line and stays green (the dogfood case)."""
        # no self._write — .add/design/ does not exist
        code, out = self._check()
        self.assertEqual(code, 0, out)
        self.assertNotIn("layer-valid", out)
        self.assertNotIn("prototype '", out)


if __name__ == "__main__":
    unittest.main()
