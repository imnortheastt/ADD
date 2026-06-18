#!/usr/bin/env python3
"""Tests for SOUL.md seeding on install and update (installer-soul-seed).

FROZEN @ v1.8.0 contract:
  _seed_soul_md(target_path, bundled_root) seeds .add/SOUL.md from
  bundled_root/tooling/templates/SOUL.md.tmpl if the file does not exist.
  Skip-if-exists on both install() and update() — SOUL.md is user-owned.
  Fail-soft: missing template or unwritable dest logs a warning; install/update
  still return 0.

Run: python3 -m unittest test_installer_soul_seed -v
"""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_SRC = _ADD_METHOD / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from add_method import _installer  # noqa: E402

_TEMPLATE_CONTENT_MARKER = "SOUL — Trusting"


def _make_bundled(root: Path, include_soul_tmpl: bool = True) -> Path:
    """Minimal bundled root with the three MANAGED trees + SOUL.md.tmpl."""
    (root / "skill" / "add").mkdir(parents=True)
    (root / "skill" / "add" / "SKILL.md").write_text("skill\n")
    (root / "tooling").mkdir(parents=True)
    (root / "tooling" / "add.py").write_text("# add.py\n")
    templates = root / "tooling" / "templates"
    templates.mkdir(parents=True)
    if include_soul_tmpl:
        (templates / "SOUL.md.tmpl").write_text(
            f"# {_TEMPLATE_CONTENT_MARKER}\ndefault voice\n"
        )
    (root / "docs").mkdir(parents=True)
    (root / "docs" / "00-introduction.md").write_text("intro\n")
    return root


def _soul_path(target: Path) -> Path:
    return target / ".add" / "SOUL.md"


class FreshInstallSeedsSoulMd(unittest.TestCase):
    """Scenario: fresh install seeds SOUL.md (covers M1)."""

    def test_fresh_install_seeds_soul_md(self):
        with tempfile.TemporaryDirectory(prefix="ss-install-") as tmp:
            tmp_path = Path(tmp)
            bundled = _make_bundled(tmp_path / "pkg")

            proj = tmp_path / "proj"
            proj.mkdir()
            rc = _installer.install(
                target=str(proj),
                bundled=str(bundled),
                non_interactive=True,
            )
            soul = _soul_path(proj)

            self.assertEqual(rc, 0, "install must return 0")
            self.assertTrue(soul.exists(), ".add/SOUL.md must be created by install")
            self.assertIn(
                _TEMPLATE_CONTENT_MARKER,
                soul.read_text(encoding="utf-8"),
                ".add/SOUL.md must contain the template marker",
            )


class InstallSkipsExistingSoulMd(unittest.TestCase):
    """Scenario: install skips existing SOUL.md (covers M3)."""

    def test_install_skips_existing_soul_md(self):
        with tempfile.TemporaryDirectory(prefix="ss-skip-") as tmp:
            tmp_path = Path(tmp)
            proj = tmp_path / "proj"
            proj.mkdir()
            bundled = _make_bundled(tmp_path / "pkg")

            add_dir = proj / ".add"
            add_dir.mkdir()
            soul = _soul_path(proj)
            soul.write_text("my-voice\n", encoding="utf-8")

            rc = _installer.install(
                target=str(proj),
                bundled=str(bundled),
                non_interactive=True,
            )

            self.assertEqual(rc, 0)
            self.assertEqual(
                soul.read_text(encoding="utf-8"),
                "my-voice\n",
                "install must not overwrite an existing SOUL.md",
            )


class UpdateSeedsMissingSoulMd(unittest.TestCase):
    """Scenario: update seeds missing SOUL.md (covers M2)."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="ss-update-"))
        self.proj = self.tmp / "proj"
        self.proj.mkdir()
        self.bundled = _make_bundled(self.tmp / "pkg")
        # Establish a prior install (managed trees present, no stamp → update will run)
        _installer.install(
            target=str(self.proj),
            bundled=str(self.bundled),
            non_interactive=True,
        )
        # Remove SOUL.md if install seeded it (so update can re-seed it)
        soul = _soul_path(self.proj)
        if soul.exists():
            soul.unlink()

    def tearDown(self):
        shutil.rmtree(str(self.tmp), ignore_errors=True)

    def test_update_seeds_missing_soul_md(self):
        soul = _soul_path(self.proj)
        self.assertFalse(soul.exists(), "precondition: SOUL.md absent before update")

        rc = _installer.update(
            target=str(self.proj),
            bundled=str(self.bundled),
            force=True,
        )

        self.assertEqual(rc, 0, "update must return 0")
        self.assertTrue(soul.exists(), ".add/SOUL.md must be created by update")
        self.assertIn(
            _TEMPLATE_CONTENT_MARKER,
            soul.read_text(encoding="utf-8"),
            ".add/SOUL.md must contain the template marker",
        )


class UpdateSkipsExistingSoulMd(unittest.TestCase):
    """Scenario: update skips existing SOUL.md (covers M3)."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="ss-upd-skip-"))
        self.proj = self.tmp / "proj"
        self.proj.mkdir()
        self.bundled = _make_bundled(self.tmp / "pkg")
        _installer.install(
            target=str(self.proj),
            bundled=str(self.bundled),
            non_interactive=True,
        )
        # Write custom SOUL.md (overwrite whatever install may have seeded)
        _soul_path(self.proj).write_text("my-voice\n", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(str(self.tmp), ignore_errors=True)

    def test_update_skips_existing_soul_md(self):
        rc = _installer.update(
            target=str(self.proj),
            bundled=str(self.bundled),
            force=True,
        )

        self.assertEqual(rc, 0)
        self.assertEqual(
            _soul_path(self.proj).read_text(encoding="utf-8"),
            "my-voice\n",
            "update must not overwrite an existing SOUL.md",
        )


class MissingTemplateInstallStillSucceeds(unittest.TestCase):
    """Scenario: missing template — seed skipped, install succeeds (covers M4 + Reject)."""

    def test_missing_template_install_still_succeeds(self):
        with tempfile.TemporaryDirectory(prefix="ss-notmpl-") as tmp:
            tmp_path = Path(tmp)
            proj = tmp_path / "proj"
            proj.mkdir()
            # Bundled root WITHOUT SOUL.md.tmpl
            bundled = _make_bundled(tmp_path / "pkg", include_soul_tmpl=False)

            rc = _installer.install(
                target=str(proj),
                bundled=str(bundled),
                non_interactive=True,
            )

            self.assertEqual(rc, 0, "install must return 0 even when template is missing")
            self.assertFalse(
                _soul_path(proj).exists(),
                ".add/SOUL.md must be absent when template was missing",
            )
            # Managed trees must still be present (install succeeded)
            self.assertTrue((proj / ".add" / "tooling" / "add.py").exists(),
                            "tooling must be present (install succeeded)")


if __name__ == "__main__":
    unittest.main()
