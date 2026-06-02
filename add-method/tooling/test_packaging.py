#!/usr/bin/env python3
"""Red/green guard for the published @pilotspace/add tarball — no dev junk ships.

`npm pack --dry-run --json` is the ground truth for what publish would include. We
parse files[].path and assert the runtime surface is present and that no compiled
bytecode (__pycache__/*.pyc), no .DS_Store, and no test_*.py source leaks in. The
npm-coupled checks SKIP cleanly when npm is absent (honest, never a false green);
the engines floor reads package.json directly so it always runs.

Run: python3 -m unittest test_packaging -v
"""
import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path

PKG_ROOT = Path(__file__).resolve().parent.parent      # add-method/ (holds package.json)
_PACK_TIMEOUT = 120                                    # design-for-failure: never hang the suite

_JUNK = re.compile(r"(__pycache__|\.py[co]$|(^|/)\.DS_Store$)")
_TEST_SRC = re.compile(r"(^|/)test_.*\.py$")
_RUNTIME_MUST = (
    "bin/cli.js", "tooling/add.py", "README.md", "GETTING-STARTED.md",
)


def _npm_on_path() -> bool:
    return shutil.which("npm") is not None


def _pack_paths() -> list[str]:
    """Return files[].path from `npm pack --dry-run --json`, run from the package root."""
    proc = subprocess.run(
        ["npm", "pack", "--dry-run", "--json"],
        cwd=PKG_ROOT, capture_output=True, text=True, timeout=_PACK_TIMEOUT,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"`npm pack --dry-run` failed ({proc.returncode}):\n{proc.stderr}")
    data = json.loads(proc.stdout)                     # [ { ..., "files": [ {path,size,mode} ] } ]
    return [f["path"] for f in data[0]["files"]]


@unittest.skipUnless(_npm_on_path(), "npm not on PATH — tarball checks skipped (honest skip)")
class NpmTarballTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.paths = _pack_paths()

    def test_no_bytecode_or_os_junk_ships(self):
        junk = [p for p in self.paths if _JUNK.search(p)]
        self.assertEqual(junk, [], f"compiled/OS junk must not ship: {junk}")

    def test_no_test_sources_ship(self):
        tests = [p for p in self.paths if _TEST_SRC.search(p)]
        self.assertEqual(tests, [], f"dev test sources must not ship: {tests}")

    def test_runtime_surface_ships(self):
        missing = [p for p in _RUNTIME_MUST if p not in self.paths]
        self.assertEqual(missing, [], f"runtime files must ship: {missing}")
        # the directory surfaces (templates/skill/docs) must each contribute ≥1 file
        for prefix in ("tooling/templates/", "skill/", "docs/"):
            self.assertTrue(any(p.startswith(prefix) for p in self.paths),
                            f"no file under {prefix} shipped")


class PackageConfigTest(unittest.TestCase):
    """No npm needed — reads package.json directly."""

    def test_node_floor_is_18(self):
        pkg = json.loads((PKG_ROOT / "package.json").read_text(encoding="utf-8"))
        self.assertEqual(pkg.get("engines", {}).get("node"), ">=18",
                         "cli.js uses fs.cpSync (Node 16.7+); 16 is EOL — floor must be >=18")


if __name__ == "__main__":
    unittest.main(verbosity=2)
