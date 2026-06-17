#!/usr/bin/env python3
"""Tests for opt-in per-project data persistence (installer-experience · global-data).

FROZEN @ v1: an OPT-IN `--global-data` (which implies `--global`) snapshots a project's
USER-DATA (state.json · PROJECT.md · milestones · tasks … — NOT the managed trees) under
<home>/data/<key>, keyed by absolute project path. `update --global` re-persists every
opted-in (already-snapshotted) + existing project; a vanished project is pruned from the
registry but its snapshot is KEPT. The per-project local + git-tracked DEFAULT is untouched.

Fully hermetic: home + skill base resolve from the injected `env` (reusing global-install's
hook), so tests touch a tmp home/HOME — never the real ~/.add or ~/.claude. To put user-data
into a project, tests PRE-SEED <proj>/.add/state.json etc. (the installer drops files only —
it never inits). npm uses subprocess with the same env (skips honestly without node).

Run: python3 -m unittest test_global_data -v
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_SRC = _ADD_METHOD / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from add_method import _installer            # noqa: E402

CLI_JS = _ADD_METHOD / "bin" / "cli.js"
NODE = shutil.which("node")


def _make_bundled(root: Path) -> Path:
    (root / "skill" / "add").mkdir(parents=True)
    (root / "skill" / "add" / "SKILL.md").write_text("skill\n")
    (root / "tooling").mkdir(parents=True)
    (root / "tooling" / "add.py").write_text("# add.py\n")
    (root / "docs").mkdir(parents=True)
    (root / "docs" / "00-introduction.md").write_text("intro\n")
    return root


def _seed_project_data(proj: Path) -> None:
    """Give a project the USER-DATA an initialised .add/ would have (without running init)."""
    add = proj / ".add"
    add.mkdir(parents=True, exist_ok=True)
    (add / "state.json").write_text(json.dumps({"stage": "mvp", "v": 1}) + "\n")
    (add / "PROJECT.md").write_text("# project\n")
    (add / "tasks").mkdir(exist_ok=True)
    (add / "tasks" / "demo.md").write_text("# a task\n")


# --- data_key (pure) --------------------------------------------------------

class DataKeyTest(unittest.TestCase):
    def test_data_key_pure_distinct_safe(self):                   # D1
        k1 = _installer.data_key("/home/a/projone")
        self.assertEqual(k1, _installer.data_key("/home/a/projone"), "deterministic")
        self.assertNotEqual(k1, _installer.data_key("/home/a/projtwo"), "distinct paths distinct keys")
        self.assertNotIn(os.sep, k1, "key must be filesystem-safe (no separator)")
        self.assertNotIn("/", k1)
        self.assertTrue(k1, "non-empty")


# --- global data persist (hermetic via injected env) ------------------------

class GlobalDataTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="gdata-"))
        self.bundled = _make_bundled(self.tmp / "pkg")
        self.home = self.tmp / "home"
        self.userhome = self.tmp / "user"; self.userhome.mkdir()
        self.proj = self.tmp / "proj"; self.proj.mkdir()

    def _env(self):
        return {"ADD_HOME": str(self.home), "HOME": str(self.userhome)}

    def _install(self, target, **kw):
        return _installer.install(target=str(target), bundled=str(self.bundled),
                                  non_interactive=True, env=self._env(), **kw)

    def _snap(self) -> Path:
        """The single project's snapshot dir under <home>/data/."""
        return self.home / "data" / _installer.data_key(str(self.proj.resolve()))

    def test_global_data_persists_user_data(self):                # D2, D3
        _seed_project_data(self.proj)
        self.assertEqual(self._install(self.proj, as_global_data=True), 0)
        snap = self._snap()
        self.assertTrue((snap / "state.json").exists(), "state.json must be persisted")
        self.assertTrue((snap / "PROJECT.md").exists())
        self.assertTrue((snap / "tasks" / "demo.md").exists(), "tasks/ must be persisted")
        self.assertFalse((snap / "tooling").exists(), "managed tooling must NOT be persisted")
        self.assertFalse((snap / "docs").exists(), "managed docs must NOT be persisted")
        # it implied --global: the home + registry are populated
        self.assertTrue((self.home / "tooling" / "add.py").exists())
        self.assertEqual(json.loads((self.home / "registry.json").read_text()),
                         [str(self.proj.resolve())])

    def test_global_data_clean_replaces_snapshot(self):           # D3
        _seed_project_data(self.proj)
        self._install(self.proj, as_global_data=True)
        self.assertTrue((self._snap() / "PROJECT.md").exists())
        (self.proj / ".add" / "PROJECT.md").unlink()              # delete locally
        self._install(self.proj, as_global_data=True)             # re-persist
        self.assertFalse((self._snap() / "PROJECT.md").exists(),
                         "a locally-deleted file must leave no orphan in the snapshot")

    def test_update_global_repersists_optedin(self):              # D4
        _seed_project_data(self.proj)
        self._install(self.proj, as_global_data=True)
        (self.proj / ".add" / "state.json").write_text(json.dumps({"stage": "production"}) + "\n")
        code = _installer.update(target=str(self.proj), bundled=str(self.bundled),
                                 version="9.9.9", env=self._env(), as_global=True)
        self.assertEqual(code, 0)
        self.assertEqual(json.loads((self._snap() / "state.json").read_text()).get("stage"),
                         "production", "update --global must re-persist the opted-in project")

    def test_update_global_keeps_vanished_snapshot(self):         # D4
        _seed_project_data(self.proj)
        self._install(self.proj, as_global_data=True)
        snap = self._snap()
        shutil.rmtree(self.proj)                                  # vanish the project dir
        code = _installer.update(target=str(self.tmp), bundled=str(self.bundled),
                                 version="9.9.9", env=self._env(), as_global=True)
        self.assertEqual(code, 0)
        reg = json.loads((self.home / "registry.json").read_text())
        self.assertNotIn(str(self.proj.resolve()), reg, "vanished project pruned from registry")
        self.assertTrue((snap / "state.json").exists(),
                        "a vanished project's snapshot is KEPT (persist outlives the dir)")

    def test_default_persists_nothing(self):                      # D5
        _seed_project_data(self.proj)
        self._install(self.proj, as_global=True)                  # --global, NOT --global-data
        self.assertFalse((self.home / "data").exists(),
                         "a plain global install must persist no data")

    def test_persist_nothing_to_persist_skips(self):              # D8
        # fresh drop: NO pre-seeded user-data — only the managed trees the drop creates.
        self.assertEqual(self._install(self.proj, as_global_data=True), 0,
                         "nothing to persist is a skip (exit 0), not an error")
        self.assertFalse(self._snap().exists(), "no snapshot dir when there is no user-data")

    def test_global_data_no_python_spawn(self):                   # D7
        _seed_project_data(self.proj)
        self._install(self.proj, as_global_data=True)
        # the snapshot is a COPY of existing data — no NEW state.json authored anywhere new
        self.assertFalse((self.home / "state.json").exists())
        self.assertNotIn("spawnSync", CLI_JS.read_text(encoding="utf-8"))

    def test_data_unwritable_fails(self):                         # Reject data_unwritable
        _seed_project_data(self.proj)
        self.home.mkdir(parents=True)
        (self.home / "data").write_text("i am a file, not a dir")  # mkdir(<home>/data/<key>) impossible
        code = self._install(self.proj, as_global_data=True)
        self.assertNotEqual(code, 0, "an unwritable data dir must fail closed")


# --- npm: real packaged sources via subprocess ------------------------------

@unittest.skipUnless(NODE, "node not on PATH — npx-side global-data checks skipped (honest skip)")
class NpmGlobalDataTest(unittest.TestCase):
    def _env(self, home, userhome):
        env = dict(os.environ)
        env.pop("CI", None)
        env["ADD_HOME"] = str(home)
        env["HOME"] = str(userhome)
        return env

    def test_global_data_npm(self):                               # D2, D3, D6
        with tempfile.TemporaryDirectory(prefix="gdata-npm-") as tmp:
            tmp = Path(tmp)
            home, userhome, proj = tmp / "home", tmp / "user", tmp / "proj"
            userhome.mkdir(); proj.mkdir()
            _seed_project_data(proj)
            res = subprocess.run([NODE, str(CLI_JS), "init", "--global-data", "--yes"], cwd=proj,
                                 capture_output=True, text=True, timeout=120,
                                 env=self._env(home, userhome))
            self.assertEqual(res.returncode, 0, res.stderr)
            data = home / "data"
            self.assertTrue(data.exists(), "global data dir created")
            snaps = list(data.iterdir())
            self.assertEqual(len(snaps), 1, "one project snapshot")
            self.assertTrue((snaps[0] / "state.json").exists(), "user-data persisted")
            self.assertFalse((snaps[0] / "tooling").exists(), "managed tooling excluded")


class ParityDataTest(unittest.TestCase):
    def test_parity_data(self):                                   # D6 structural
        js = CLI_JS.read_text(encoding="utf-8")
        py = (_SRC / "add_method" / "_installer.py").read_text(encoding="utf-8")
        self.assertIn("dataKey", js, "cli.js must define the dataKey twin")
        self.assertIn("data_key", py, "_installer.py must define data_key")
        self.assertIn("global-data", js, "cli.js must accept the --global-data flag")
        self.assertIn("as_global_data", py, "_installer.py must thread as_global_data")
        # both must name the <home>/data/<key> dir explicitly (the quoted "data" path segment)
        self.assertIn('"data"', js, "cli.js must write under the data/ dir")
        self.assertIn('"data"', py, "_installer.py must write under the data/ dir")


if __name__ == "__main__":
    unittest.main(verbosity=2)
