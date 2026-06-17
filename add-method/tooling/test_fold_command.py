#!/usr/bin/env python3
"""Behavioral proof of `add.py fold` — mechanized competency-delta consolidation
(task: fold-command, delta-resolution). CONTRACT frozen @ v1.

ONE atomic session: flip every open competency delta -> folded + stamp
`[folded foundation-version N]`, transcribe it VERBATIM into its routed foundation
section (DDD/SDD/UDD -> PROJECT.md §Domain/§Spec/§Users, TDD/ADD -> CONVENTIONS.md
§Method learnings), prepend ONE §Key Decisions row, bump foundation-version ONCE.
Batch = one call, one bump, one stamp value. Validate-all-then-write: any reject
leaves the whole tree byte-identical. One test per §2 scenario + 2 unit proofs.

This command is the HUMAN-AUTHORIZED reversal of the prior "engine stays
judgment-free; there is no add.py fold" principle (test_foundation_update_loop
re-frozen @ v3) — the engine TRANSCRIBES, it never composes/merges prose.

Run: python3 -m unittest test_fold_command -v
"""
from __future__ import annotations

import io
import os
import re
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add


def _run(argv):
    out, err = io.StringIO(), io.StringIO()
    code = None
    with redirect_stdout(out), redirect_stderr(err):
        try:
            add.main(argv)
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
    return out.getvalue(), err.getvalue(), code


def _snapshot(base):
    return {str(p.relative_to(base)): p.read_bytes()
            for p in sorted(base.rglob("*")) if p.is_file()}


class FoldCommandTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-fold-")
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])
        self.root = Path(self.tmp) / ".add"
        self.project = self.root / "PROJECT.md"
        self.conventions = self.root / "CONVENTIONS.md"

    def tearDown(self):
        os.chdir(self._cwd)
        shutil.rmtree(self.tmp, ignore_errors=True)

    # --- helpers -------------------------------------------------------------
    def _new_task(self, slug):
        add.main(["new-task", slug])

    def _plant_comp(self, slug, tag, text, ev="e"):
        """Inject one grammar-valid OPEN competency delta into slug's §7 block.

        Insert right after the heading; the heading's own trailing newline isolates
        the entry with a blank line so _collect_open_deltas reads it un-polluted."""
        p = self.root / "tasks" / slug / "TASK.md"
        s = p.read_text(encoding="utf-8")
        i = s.index("### Competency deltas") + len("### Competency deltas")
        p.write_text(s[:i] + f"\n- [{tag} · open] {text} (evidence: {ev})\n" + s[i:],
                     encoding="utf-8")

    def _set_fv(self, n):
        """Give PROJECT.md a parseable `foundation-version:` header (templates omit it)."""
        s = self.project.read_text(encoding="utf-8")
        if re.search(r"foundation-version:\s*\d+", s):
            s = re.sub(r"foundation-version:\s*\d+", f"foundation-version: {n}", s)
        else:
            s = re.sub(r"(?m)^(slug:.*)$", rf"\1 · foundation-version: {n}", s, count=1)
        self.project.write_text(s, encoding="utf-8")

    def _add_method_learnings(self):
        """CONVENTIONS.md gains the TDD/ADD route target (the template omits it)."""
        s = self.conventions.read_text(encoding="utf-8")
        if "## Method learnings" not in s:
            self.conventions.write_text(
                s.rstrip() + "\n\n## Method learnings (folded from OBSERVE deltas)\n",
                encoding="utf-8")

    def _fv(self):
        m = re.search(r"foundation-version:\s*(\d+)", self.project.read_text(encoding="utf-8"))
        return int(m.group(1)) if m else None

    def _task_md(self, slug):
        return (self.root / "tasks" / slug / "TASK.md").read_text(encoding="utf-8")

    # --- scenarios -----------------------------------------------------------
    def test_fold_all_in_one_session(self):  # the happy path (Musts 1-6, 8)
        self._new_task("alpha"); self._plant_comp("alpha", "SDD", "wording-lint rejects slang")
        self._new_task("beta"); self._plant_comp("beta", "ADD", "pre-freeze downstream scan")
        self._set_fv(35)
        self._add_method_learnings()
        out, err, code = _run(["fold"])
        self.assertIsNone(code, f"fold should succeed: {err}")
        # flip + stamp, every delta carrying the SAME N=36
        self.assertIn("[SDD · folded]", self._task_md("alpha"))
        self.assertIn("[folded foundation-version 36]", self._task_md("alpha"))
        self.assertIn("[ADD · folded]", self._task_md("beta"))
        self.assertIn("[folded foundation-version 36]", self._task_md("beta"))
        # transcribe VERBATIM into the routed sections
        proj = self.project.read_text(encoding="utf-8")
        conv = self.conventions.read_text(encoding="utf-8")
        self.assertIn("wording-lint rejects slang", proj)   # SDD -> ## Spec
        self.assertIn("pre-freeze downstream scan", conv)    # ADD -> ## Method learnings
        # one §Key Decisions row naming the new version
        self.assertIn("foundation-version 36", proj)
        # bumped exactly once + summary
        self.assertEqual(self._fv(), 36)
        self.assertIn("35 -> 36", out)

    def test_filter_narrows_scope(self):  # Must: --task narrows; still one bump
        self._new_task("a"); self._plant_comp("a", "SDD", "alpha lesson")
        self._new_task("b"); self._plant_comp("b", "SDD", "beta lesson")
        self._set_fv(10)
        out, err, code = _run(["fold", "--task", "a"])
        self.assertIsNone(code, f"fold --task a should succeed: {err}")
        self.assertIn("[SDD · folded]", self._task_md("a"))
        self.assertIn("[SDD · open]", self._task_md("b"))   # untouched
        self.assertEqual(self._fv(), 11)                    # exactly one bump

    def test_no_open_deltas_refuses(self):  # Reject
        self._set_fv(5)
        before = _snapshot(self.root)
        out, err, code = _run(["fold"])
        self.assertIsNotNone(code)
        self.assertIn("no_open_deltas", out + err)
        self.assertEqual(_snapshot(self.root), before)      # byte-unchanged

    def test_missing_route_section_refuses_atomically(self):  # Reject + atomicity
        # An ADD lesson routes to CONVENTIONS.md "## Method learnings" — ABSENT in a fresh
        # project (the template omits it); the co-occurring SDD lesson routes cleanly to ## Spec.
        self._new_task("m"); self._plant_comp("m", "ADD", "an ADD lesson")  # -> ## Method learnings (missing)
        self._new_task("s"); self._plant_comp("s", "SDD", "an SDD lesson")  # -> ## Spec (present)
        self._set_fv(7)
        # deliberately do NOT call _add_method_learnings() -> the route section stays absent
        before = _snapshot(self.root)
        out, err, code = _run(["fold"])
        self.assertIsNotNone(code)
        self.assertIn("missing_route_section", out + err)
        self.assertIn("[SDD · open]", self._task_md("s"))   # co-occurring delta UNTOUCHED
        self.assertEqual(self._fv(), 7)                     # no bump
        self.assertEqual(_snapshot(self.root), before)      # nothing written at all

    def test_no_foundation_version_refuses(self):  # Reject
        self._new_task("x"); self._plant_comp("x", "SDD", "a lesson")
        # deliberately do NOT _set_fv -> the template carries no foundation-version header
        before = _snapshot(self.root)
        out, err, code = _run(["fold"])
        self.assertIsNotNone(code)
        self.assertIn("no_foundation_version", out + err)
        self.assertEqual(_snapshot(self.root), before)

    def test_one_bump_for_many_deltas(self):  # invariant: one session, one bump, one stamp value
        self._new_task("p"); self._plant_comp("p", "SDD", "l1"); self._plant_comp("p", "SDD", "l2")
        self._new_task("q"); self._plant_comp("q", "DDD", "l3")
        self._set_fv(20)
        out, err, code = _run(["fold"])
        self.assertIsNone(code, f"fold should succeed: {err}")
        self.assertEqual(self._fv(), 21)                    # exactly one bump
        self.assertEqual(self._task_md("p").count("[folded foundation-version 21]"), 2)
        self.assertEqual(self._task_md("q").count("[folded foundation-version 21]"), 1)

    def test_fold_competency_delta_pure(self):  # earned-green unit proof of the pure core
        line = "- [ADD · open] keep this exact text (evidence: proof)\n"
        out = add._fold_competency_delta(line, 42)
        self.assertIsNotNone(out)
        self.assertIn("[ADD · folded]", out)
        self.assertIn("[folded foundation-version 42]", out)
        self.assertIn("keep this exact text (evidence: proof)", out)   # byte-preserved
        # no open delta -> None (the validate-all-then-write contract for the caller)
        self.assertIsNone(
            add._fold_competency_delta("- [ADD · folded] already (evidence: e)\n", 42))


if __name__ == "__main__":
    unittest.main()
