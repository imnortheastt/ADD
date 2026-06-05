"""Core installer — Python analog of bin/cli.js.

DROPS FILES ONLY — does NOT run `add.py init`. Initialisation is deferred to the AI
(via `/add`, which runs `init --await-lock` to arm the v12 lock-down gate) or a CLI user.
A pre-run plain init would grandfather-lock the gate before `/add` runs AND consume the
brownfield signal in the terminal, where the AI never sees it.

Designed for failure:
- Verifies bundled sources exist before touching target.
- Never clobbers an existing skill (skip-if-exists unless --force).
- Uses shutil.copytree with dirs_exist_ok=True so a re-install refreshes
  tooling/docs without destroying the existing project structure.
"""
from __future__ import annotations

import importlib.resources
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
    stage: str | None = None,
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

    # NO step 4: the installer DROPS FILES ONLY (npm ↔ pip parity with bin/cli.js).
    # Initialisation is deferred to the AI (via `/add`) or a CLI user — a pre-run plain
    # `add.py init` would grandfather-lock the v12 lock-down gate before `/add` runs (see
    # the module header). So we do NOT exec add.py here.
    _log("\nDone. The `add` skill + tooling are installed (no project state yet — that's intentional).")
    _log("Next:  open Claude Code, run `/add`, and say what you want to build — the agent")
    _log("       sets up the foundation, sizes it into a milestone, and drives the build with you;")
    _log("       you sign off once, at the lock-down.")
    _log("")
    _log("Prefer the CLI / not using Claude Code? Initialise it yourself (this arms the lock-down):")
    # Echo only flags the user actually chose — the engine's own `init`
    # defaults the stage and infers the name, so the flagless hint is the
    # shortest TRUE command (npm <-> pip parity with bin/cli.js).
    launcher = "py" if sys.platform == "win32" else "python3"  # parity with cli.js
    manual_init = f"  {launcher} .add/tooling/add.py init --await-lock"
    if stage:
        manual_init += f" --stage {stage}"
    if name:
        manual_init += f' --name "{name}"'
    _log(manual_init)
    return 0
