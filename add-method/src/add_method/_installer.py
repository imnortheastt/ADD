"""Core installer — Python analog of bin/cli.js.

Designed for failure:
- Verifies bundled sources exist before touching target.
- Never clobbers an existing state.json (add.py init enforces this; we surface
  the warning instead of aborting).
- Uses shutil.copytree with dirs_exist_ok=True so a re-install refreshes
  tooling/docs without destroying the existing project structure.
- Loads the installed copy of add.py via importlib.util so that _templates_dir()
  resolves to the adjacent templates/ in the installed tooling, not to whatever
  add.py source might be on sys.path.
- Wraps the add.main() call in try/except SystemExit so `already initialised`
  becomes a warning, not a crash (mirrors cli.js non-zero-exit handling).
"""
from __future__ import annotations

import importlib.resources
import importlib.util
import shutil
import sys
from pathlib import Path


def _log(msg: str) -> None:
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()


def _warn(msg: str) -> None:
    sys.stderr.write("warn: " + msg + "\n")
    sys.stderr.flush()


def _fail(msg: str) -> int:
    sys.stderr.write("error: " + msg + "\n")
    sys.stderr.flush()
    return 1


def _bundled_root() -> Path:
    """Return a concrete filesystem path to src/add_method/_bundled/.

    importlib.resources.files() returns a real Path for pip-installed
    (non-zip) wheels. A zip-import scenario is flagged as unsupported.
    """
    ref = importlib.resources.files("add_method") / "_bundled"
    # Materialise to a concrete path — as_file() on a directory is unreliable
    # on Python 3.10/3.11; for non-zip installs the traversable IS a Path.
    path = Path(str(ref))
    if not path.exists():
        raise RuntimeError(
            f"Bundled data not found at {path}. "
            "This may happen if the package was installed from a zip archive "
            "(e.g. a .egg or a zipped wheel). Install from PyPI with pip into "
            "a normal site-packages directory."
        )
    return path


def install(
    target: str = ".",
    force: bool = False,
    stage: str = "prototype",
    name: str | None = None,
) -> int:
    """Install ADD into `target` directory.

    Returns 0 on success, 1 on error.
    """
    target_path = Path(target).resolve()
    if not target_path.exists():
        return _fail(f"target directory does not exist: {target_path}")

    _log(f"Installing ADD into {target_path}")

    # Locate bundled data.
    try:
        bundled = _bundled_root()
    except RuntimeError as exc:
        return _fail(str(exc))

    # Verify sources exist before touching anything (design-for-failure).
    for sub in ("skill/add", "tooling", "docs"):
        src = bundled / sub
        if not src.exists():
            return _fail(f"missing bundled source: {src}")

    # 1. skill -> <target>/.claude/skills/add/
    #    Skip-if-exists unless --force (mirrors cli.js skipIfExists logic).
    skill_dest = target_path / ".claude" / "skills" / "add"
    if skill_dest.exists() and not force:
        _warn(f"{skill_dest} exists — leaving it untouched")
    else:
        skill_dest.parent.mkdir(parents=True, exist_ok=True)
        if skill_dest.exists() and force:
            shutil.rmtree(skill_dest)
        shutil.copytree(str(bundled / "skill" / "add"), str(skill_dest))
    _log("  ✓ skill      -> .claude/skills/add/")

    # 2. tooling -> <target>/.add/tooling/
    #    Always refresh (dirs_exist_ok=True) — no test_*.py in bundle.
    tooling_dest = target_path / ".add" / "tooling"
    tooling_dest.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        str(bundled / "tooling"), str(tooling_dest), dirs_exist_ok=True
    )
    _log("  ✓ tooling    -> .add/tooling/add.py (+ templates)")

    # 3. docs -> <target>/.add/docs/
    #    Always refresh.
    docs_dest = target_path / ".add" / "docs"
    docs_dest.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        str(bundled / "docs"), str(docs_dest), dirs_exist_ok=True
    )
    _log("  ✓ trust docs -> .add/docs/ (the AIDD book)")

    # 4. run add.py init (idempotent — add.py refuses to clobber state.json).
    #    Load the INSTALLED copy so _templates_dir() resolves to the adjacent
    #    templates/ inside the installed tooling, not from this package's source.
    add_py = tooling_dest / "add.py"
    if not add_py.exists():
        _warn("`add.py` not found in installed tooling — skipping init.")
        _log("\nFinish setup manually:")
        _log(f"  python3 .add/tooling/add.py init --dir \"{target_path}\"")
        return 0

    init_argv = ["init", "--dir", str(target_path), "--stage", stage]
    if name:
        init_argv += ["--name", name]
    if force:
        init_argv.append("--force")

    try:
        spec = importlib.util.spec_from_file_location(
            "add_method._add_main",  # unique name — avoids sys.modules collision
            str(add_py),
        )
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load spec from {add_py}")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        mod.main(init_argv)  # type: ignore[attr-defined]
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else 1
        if code != 0:
            _warn(
                "`add.py init` exited non-zero (state may already exist). "
                "Run `add-method` status, or `add.py status`, to check."
            )
    except Exception as exc:  # noqa: BLE001
        _warn(f"`add.py init` raised an unexpected error: {exc}")

    _log("\nDone. In Claude Code, the `add` skill is now installed.")
    _log("Next:  open Claude Code, run `/add`, and say what you want to build —")
    _log("       the agent sizes it into a milestone and drives the build with you.")
    return 0
