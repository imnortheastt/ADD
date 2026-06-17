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
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

# The managed layer — ship-controlled trees `update` re-materializes from the package.
# (bundled subpath, dest relative to target, strip dev-only test_*.py after copy)
MANAGED = (
    ("skill/add", ".claude/skills/add", False),
    ("tooling", ".add/tooling", True),
    ("docs", ".add/docs", False),
)
STAMP_FILE = ".add-version"          # records the materialized version, under .add/
# Forward-only, idempotent state migrations keyed by the version that introduces them.
# Empty today — the framework exists so the NEXT schema change is an in-place update,
# never a re-install. Each value is callable(state: dict) -> dict.
MIGRATIONS: dict = {}


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


# --- interactive layer (stdlib input(); npm's clack twin — NO new dependency) ---
# Mirrors bin/cli.js: interactive only on a real terminal, byte-identical plain text
# everywhere else. clack is Node-only, so pip uses a single stdlib input() confirm.
CANCEL = object()  # sentinel: the user aborted before any write


def _interactive(yes: bool, non_interactive: bool) -> bool:
    if yes or non_interactive:
        return False
    seam = os.environ.get("ADD_INSTALLER_FORCE_INTERACTIVE")
    if seam in ("1", "fail"):       # documented test seam (parity with cli.js)
        return True
    return (
        sys.stdin.isatty()
        and sys.stdout.isatty()
        and not os.environ.get("CI")
    )


def _prompt_target(default_path: Path):
    """Confirm the target directory. Enter accepts the default; a typed path overrides.
    A cancel (EOF / Ctrl-C) returns CANCEL — the caller writes nothing.

    Deliberately a SINGLE confirm (npm's clack flow has a second write-confirm step):
    "parity ENOUGH" is the accepted §1 A2 assumption — a richer pip prompt is a deferred
    follow-up per the milestone Out-list, not a parity bug."""
    try:
        resp = input(
            f"Install ADD into target directory [{default_path}] "
            "(Enter to confirm, or type a path): "
        ).strip()
    except (EOFError, KeyboardInterrupt):
        return CANCEL
    if not resp:
        return default_path
    return Path(resp).expanduser().resolve()


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
    yes: bool = False,
    non_interactive: bool = False,
) -> int:
    """Install ADD into `target` directory.

    Returns 0 on success, 1 on error, 130 on a user cancel (nothing written).
    """
    target_path = Path(target).resolve()
    if not target_path.exists():
        return _fail(f"target directory does not exist: {target_path}")

    # Interactive confirm (real terminal only) — degrades to the plain path under
    # --yes/--non-interactive, CI, or a pipe. A cancel writes NOTHING (exit 130).
    if _interactive(yes, non_interactive):
        chosen = _prompt_target(target_path)
        if chosen is CANCEL:
            _log("\nInstallation cancelled — nothing was written.")
            return 130
        target_path = chosen
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
    _log("Next:  open your AI Agent CLI (like Claude Code, Codex, etc.), then run `/add`, and say what you want to build — the agent")
    _log("       sets up the foundation, sizes it into a milestone, and drives the build with you;")
    _log("       you sign off once, at the lock-down.")
    _log("")
    return 0


# --- update: re-materialize the managed layer without a re-install -----------

def _pkg_version() -> str:
    try:
        from add_method import __version__
        return __version__
    except Exception:
        return "0.0.0"


def _stamp_path(add_dir: Path) -> Path:
    return add_dir / STAMP_FILE


def _read_stamp(add_dir: Path) -> dict | None:
    p = _stamp_path(add_dir)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _write_stamp(add_dir: Path, version: str, channel: str = "pip") -> None:
    add_dir.mkdir(parents=True, exist_ok=True)
    _stamp_path(add_dir).write_text(
        json.dumps(
            {
                "version": version,
                "channel": channel,
                "installed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def _clean_replace(src: Path, dest: Path, *, strip_tests: bool = False) -> None:
    """Wipe dest, then copy src -> dest — so a file REMOVED upstream leaves no orphan
    behind (the bug a merge-copy `init --force` had). The managed trees hold no user
    data, so wipe-and-copy is safe."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(str(src), str(dest))
    if strip_tests:
        pyc = dest / "__pycache__"
        if pyc.exists():
            shutil.rmtree(pyc)
        for child in dest.iterdir():
            if child.name.startswith("test_") and child.name.endswith(".py"):
                child.unlink()


def _run_migrations(state_file: Path, from_version: str | None, to_version: str) -> None:
    """Apply forward-only, idempotent state migrations. No-op while MIGRATIONS is empty."""
    if not MIGRATIONS or not state_file.exists():
        return
    try:
        state = json.loads(state_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    changed = False
    for ver, migrate in sorted(MIGRATIONS.items(), key=lambda kv: _vkey(kv[0])):
        if from_version is None or _vkey(from_version) < _vkey(ver) <= _vkey(to_version):
            state = migrate(state)
            changed = True
    if changed:
        state_file.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def _vkey(v: str) -> list:
    """A sortable key for dotted versions (numeric parts compared as ints)."""
    return [(0, int(p)) if p.isdigit() else (1, p) for p in (v or "0").split(".")]


def _add_dir(target_path: Path) -> Path:
    return target_path / ".add"


def update(
    target: str = ".",
    force: bool = False,
    bundled: str | None = None,
    version: str | None = None,
    channel: str = "pip",
) -> int:
    """Re-materialize the managed layer (skill · tooling · docs) from the installed
    package into an EXISTING .add/ project, preserving ALL user data. Idempotent;
    clean-replaces so no orphan files survive a version bump. 0 on success/no-op, 1 on error."""
    target_path = Path(target).resolve()
    add_dir = _add_dir(target_path)
    if not (add_dir / "tooling").exists() and not (add_dir / "state.json").exists():
        return _fail(f"no ADD project at {target_path} (.add/ not found) — run `init` first")

    try:
        bundled_root = Path(bundled) if bundled else _bundled_root()
    except RuntimeError as exc:
        return _fail(str(exc))
    for sub, _dest, _strip in MANAGED:
        if not (bundled_root / sub).exists():
            return _fail(f"missing bundled source: {bundled_root / sub}")

    new_version = version or _pkg_version()
    stamp = _read_stamp(add_dir)
    cur_version = stamp.get("version") if stamp else None
    if cur_version == new_version and not force:
        _log(f"ADD already at {new_version} — nothing to update (use --force to re-materialize).")
        return 0

    # design-for-failure: back up state BEFORE touching anything.
    state_file = add_dir / "state.json"
    if state_file.exists():
        shutil.copyfile(str(state_file), str(add_dir / "pre-update-state.bak.json"))

    for sub, dest_rel, strip in MANAGED:
        _clean_replace(bundled_root / sub, target_path / dest_rel, strip_tests=strip)
    _run_migrations(state_file, cur_version, new_version)
    _write_stamp(add_dir, new_version, channel=channel)

    _log(
        f"ADD updated {cur_version or '(unstamped)'} -> {new_version} · "
        "skill · tooling · docs refreshed · your project state untouched."
    )
    return 0


def update_check(target: str = ".", version: str | None = None) -> int:
    """Read-only: compare the project's stamp to the installed package version. No writes."""
    add_dir = _add_dir(Path(target).resolve())
    if not add_dir.exists():
        return _fail("no ADD project here (.add/ not found) — run `init` first")
    new_version = version or _pkg_version()
    stamp = _read_stamp(add_dir)
    cur = stamp.get("version") if stamp else None
    if cur == new_version:
        _log(f"ADD is current: project and package both at {new_version}.")
    elif cur is None:
        _log(f"ADD project is unstamped; installed package is {new_version}. Run `update`.")
    else:
        _log(f"ADD update available: project on {cur}, package is {new_version}. Run `update`.")
    return 0
