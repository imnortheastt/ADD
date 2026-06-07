#!/usr/bin/env python3
"""Red/green tests for the 1.1.0 release readiness (task release-1-1-0, v14).

In-repo readiness only — the live-registry halves (npm/PyPI serving 1.1.0) are
verify-gate EVIDENCE gathered after the human-gated tag push, never unit tests.
Run:
    python3 -m unittest test_release_1_1_0 -v
"""
import hashlib
import json
import re
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parent                       # add-method/
REPO = PKG.parent
BUNDLE = PKG / "src" / "add_method" / "_bundled"

CHANGELOG = PKG / "CHANGELOG.md"
CI_YML = REPO / ".github" / "workflows" / "ci.yml"
PUBLISH_YML = REPO / ".github" / "workflows" / "publish.yml"

VERSION = "1.1.0"
ENGINE_MD5 = "1845b3035f371fa8d60773a3c4ce60e3"
CANONICAL_AUDIT = "run: python3 .add/tooling/add.py audit"
# the five v14 features the release notes must name
FEATURE_ANCHORS = ("add.py audit", "seam-audit", "unguarded_high_risk_auto",
                   "agent", "freeze review checklist")


class ChangelogTest(unittest.TestCase):
    def test_changelog_has_1_1_0_entry(self):
        self.assertTrue(CHANGELOG.is_file(), "CHANGELOG.md missing")
        text = CHANGELOG.read_text(encoding="utf-8")
        self.assertIn(f"## [{VERSION}]", text)
        self.assertIn("## [1.0.0]", text, "the baseline entry must exist")
        entry = text.split(f"## [{VERSION}]", 1)[1].split("## [", 1)[0]
        for anchor in FEATURE_ANCHORS:
            self.assertIn(anchor, entry, f"1.1.0 entry must name: {anchor}")

    def test_changelog_ships_in_both_channels(self):
        files = json.loads((PKG / "package.json").read_text(encoding="utf-8"))["files"]
        self.assertIn("CHANGELOG.md", files, "npm tarball must ship the changelog")
        self.assertIn("include CHANGELOG.md",
                      (PKG / "MANIFEST.in").read_text(encoding="utf-8"),
                      "sdist/wheel must ship the changelog")


class WorkflowHygieneTest(unittest.TestCase):
    def test_no_deprecated_actions(self):
        for wf in (CI_YML, PUBLISH_YML):
            text = wf.read_text(encoding="utf-8")
            self.assertNotIn("actions/checkout@v4", text, wf.name)
            self.assertNotIn("actions/setup-python@v5", text, wf.name)
            self.assertNotIn("actions/setup-node@v4", text, wf.name)

    def test_audit_line_survives_bumps(self):
        self.assertIn(CANONICAL_AUDIT, CI_YML.read_text(encoding="utf-8"),
                      "the seam-audit command must stay byte-identical")


class ReleaseShapeTest(unittest.TestCase):
    def test_versions_agree_at_1_1_0(self):
        pkg = json.loads((PKG / "package.json").read_text(encoding="utf-8"))["version"]
        py = re.search(r'(?m)^version\s*=\s*"([^"]+)"',
                       (PKG / "pyproject.toml").read_text(encoding="utf-8")).group(1)
        self.assertEqual((pkg, py), (VERSION, VERSION),
                         "publish.yml's guard would fail this release closed")

    def test_getting_started_mentions_guide_line(self):
        text = (PKG / "GETTING-STARTED.md").read_text(encoding="utf-8")
        self.assertIn("guide  :", text,
                      "orient docs must name the phase-playbook line")

    def test_engine_untouched(self):
        for p in (HERE / "add.py", REPO / ".add" / "tooling" / "add.py",
                  BUNDLE / "tooling" / "add.py"):
            self.assertEqual(hashlib.md5(p.read_bytes()).hexdigest(), ENGINE_MD5,
                             f"the release task must not touch the engine: {p}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
