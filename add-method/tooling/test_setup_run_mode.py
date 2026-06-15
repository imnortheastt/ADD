#!/usr/bin/env python3
"""Content + parity guard for the setup "Run mode" step (task setup-run-mode,
v13-onboarding-polish 2/6).

phases/0-setup.md must gain a "## Run mode" step that (a) shows an autonomy×streams
comparison table, (b) proposes parallel+auto as the DEFAULT confirm-to-keep, (c) cites
`add.py waves` + the autonomy dial and preserves the one-approval-per-contract floor,
(d) records the choice in PROJECT.md Key Decisions; and streams.md must name parallel+auto
as the project default (opt-out). All three skill trees stay byte-identical.

Content-test pattern per test_cospecify_lift. Run: python3 -m unittest test_setup_run_mode -v
"""
from __future__ import annotations

import hashlib
import unittest
from pathlib import Path

ADD_METHOD = Path(__file__).resolve().parent.parent
REPO = ADD_METHOD.parent

CANONICAL = ADD_METHOD / "skill" / "add"
BUNDLED = ADD_METHOD / "src" / "add_method" / "_bundled" / "skill" / "add"
DOGFOOD = REPO / ".claude" / "skills" / "add"

SETUP = "phases/0-setup.md"
STREAMS = "streams.md"


def _read(tree: Path, rel: str) -> str:
    return (tree / rel).read_text(encoding="utf-8")


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


class RunModeStep(unittest.TestCase):
    def setUp(self):
        self.setup = _read(CANONICAL, SETUP)
        # the "## Run mode" section text (heading -> next "## " or EOF)
        self.assertIn("## Run mode", self.setup, "setup guide must gain a '## Run mode' step")
        start = self.setup.index("## Run mode")
        nxt = self.setup.find("\n## ", start + 1)
        self.section = self.setup[start: nxt if nxt != -1 else len(self.setup)]

    def test_run_mode_table_present(self):
        # a markdown table (pipe rows) naming both modes + gate/concurrency columns
        self.assertIn("|", self.section, "the run-mode step must include a comparison table")
        low = self.section.lower()
        self.assertIn("sequential", low)
        self.assertIn("parallel", low)
        self.assertTrue("gate" in low, "table must name the human gates")
        self.assertTrue("concurren" in low or "flow" in low, "table must name concurrency/flow")

    def test_proposes_parallel_auto_default(self):
        low = self.section.lower()
        self.assertIn("default", low, "the step must name a default")
        self.assertIn("parallel", low)
        self.assertIn("auto", low)
        self.assertIn("confirm", low, "the default must be confirm-to-keep, not a silent flip")

    def test_cites_waves_and_autonomy(self):
        self.assertIn("add.py waves", self.section, "must cite the scheduler")
        self.assertIn("autonomy", self.section.lower(), "must cite the autonomy dial")
        # the one-approval floor must be explicit so 'auto' is not read as 'no gate'
        self.assertIn("contract", self.section.lower())

    def test_records_in_project_key_decisions(self):
        self.assertIn("Key Decisions", self.section, "the choice must be recorded in PROJECT.md Key Decisions")

    def test_streams_names_new_default(self):
        streams = _read(CANONICAL, STREAMS).lower()
        self.assertIn("default", streams)
        self.assertTrue("parallel" in streams and "auto" in streams)
        self.assertIn("opt-out", streams, "streams.md must name parallel+auto as the project default (opt-out)")

    def test_three_trees_byte_identical(self):
        for rel in (SETUP, STREAMS):
            digests = {_md5(t / rel) for t in (CANONICAL, BUNDLED, DOGFOOD)}
            self.assertEqual(len(digests), 1, f"{rel} diverged across the 3 skill trees")


if __name__ == "__main__":
    unittest.main()
