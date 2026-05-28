#!/usr/bin/env python3
"""ADD — minimal scaffolder + state tracker for AI-Driven Development.

One file = one task. This tool generates the per-task TASK.md (which Claude fills
in step by step) and maintains .add/state.json so any fresh session can resume
with `add.py status` instead of re-reading the whole repo. That is the anti-
context-rot core of the ADD method.

Stdlib only. Writes are atomic (temp + os.replace) and refuse to clobber
existing artifacts unless --force is given.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path

# --- constants ---------------------------------------------------------------

ROOT_DIRNAME = ".add"
STATE_FILE = "state.json"
STAGES = ("prototype", "poc", "mvp", "production")
PHASES = ("specify", "scenarios", "contract", "tests", "build", "verify", "observe", "done")
GATES = ("none", "PASS", "RISK-ACCEPTED", "HARD-STOP")
SETUP_FILES = ("CONVENTIONS.md", "GLOSSARY.md", "MODEL_REGISTRY.md", "dependencies.allowlist")

# Minimal embedded fallback so the tool still works if templates/ is missing
# (circuit breaker: never hard-fail just because a template file was deleted).
_FALLBACK_TASK = """# TASK: {title}

slug: {slug} · created: {date} · stage: {stage}
phase: specify

## 1 · SPECIFY
Must:
Reject:
After:
Assumptions (confirm before building):

## 2 · SCENARIOS
## 3 · CONTRACT
Status: DRAFT
## 4 · TESTS
## 5 · BUILD
## 6 · VERIFY
### GATE RECORD
Outcome:
## 7 · OBSERVE
"""


# --- low-level IO (designed for failure: atomic, no silent clobber) ----------

def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _atomic_write(path: Path, text: str) -> None:
    """Write via a temp file in the same dir, then atomically replace.

    Avoids a half-written file if the process dies mid-write.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def _templates_dir() -> Path:
    return Path(__file__).resolve().parent / "templates"


def _render_template(name: str, **subs: str) -> str:
    """Load templates/<name>.tmpl and substitute {{key}} tokens.

    Falls back to a built-in minimal template only for TASK.md.
    """
    tmpl = _templates_dir() / f"{name}.tmpl"
    if tmpl.exists():
        text = tmpl.read_text(encoding="utf-8")
    elif name == "TASK.md":
        text = _FALLBACK_TASK.replace("{title}", "{{title}}").replace(
            "{slug}", "{{slug}}").replace("{date}", "{{date}}").replace("{stage}", "{{stage}}")
    else:
        text = ""
    for key, val in subs.items():
        text = text.replace("{{" + key + "}}", val)
    return text


# --- state -------------------------------------------------------------------

def find_root(start: Path | None = None) -> Path | None:
    """Walk up from cwd to find a .add/ project root."""
    cur = (start or Path.cwd()).resolve()
    for d in (cur, *cur.parents):
        if (d / ROOT_DIRNAME / STATE_FILE).exists():
            return d / ROOT_DIRNAME
    return None


def _require_root() -> Path:
    root = find_root()
    if root is None:
        _die("no .add/ project found. Run `add.py init` first.")
    return root


def load_state(root: Path) -> dict:
    return json.loads((root / STATE_FILE).read_text(encoding="utf-8"))


def save_state(root: Path, state: dict) -> None:
    state["updated"] = _now()
    _atomic_write(root / STATE_FILE, json.dumps(state, indent=2) + "\n")


def _die(msg: str, code: int = 1) -> None:
    print(f"add: error: {msg}", file=sys.stderr)
    raise SystemExit(code)


# --- commands ----------------------------------------------------------------

def cmd_init(args: argparse.Namespace) -> None:
    base = Path(args.dir).resolve()
    root = base / ROOT_DIRNAME
    state_path = root / STATE_FILE
    if state_path.exists() and not args.force:
        _die(f"already initialised at {root} (use --force to reset state)")

    (root / "tasks").mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()

    # survivor-layer files — never clobber an existing one
    for fname in SETUP_FILES:
        dest = root / fname
        if dest.exists():
            continue
        tmpl_name = fname
        _atomic_write(dest, _render_template(tmpl_name, date=today))

    state = {
        "project": args.name or base.name,
        "stage": args.stage,
        "active_task": None,
        "tasks": {},
        "created": _now(),
        "updated": _now(),
    }
    save_state(root, state)
    print(f"initialised ADD project '{state['project']}' (stage: {state['stage']}) at {root}")
    print("next: add.py new-task <slug> --title \"...\"")


def cmd_new_task(args: argparse.Namespace) -> None:
    root = _require_root()
    state = load_state(root)
    slug = args.slug
    if not slug.replace("-", "").replace("_", "").isalnum():
        _die("slug must be alphanumeric with - or _ only")
    tdir = root / "tasks" / slug
    task_md = tdir / "TASK.md"
    if task_md.exists() and not args.force:
        _die(f"task '{slug}' already exists (use --force to overwrite TASK.md)")

    (tdir / "tests").mkdir(parents=True, exist_ok=True)
    (tdir / "src").mkdir(parents=True, exist_ok=True)
    title = args.title or slug.replace("-", " ").replace("_", " ").title()
    _atomic_write(task_md, _render_template(
        "TASK.md", title=title, slug=slug, date=date.today().isoformat(), stage=state["stage"]))

    state["tasks"][slug] = {
        "title": title,
        "phase": "specify",
        "gate": "none",
        "created": _now(),
        "updated": _now(),
    }
    state["active_task"] = slug
    save_state(root, state)
    print(f"created task '{slug}' -> {task_md}")
    print("active task set. phase: specify. Fill section 1 (SPECIFY), then: add.py advance")


def _resolve_task(state: dict, slug: str | None) -> str:
    slug = slug or state.get("active_task")
    if not slug:
        _die("no task specified and no active task set")
    if slug not in state["tasks"]:
        _die(f"unknown task '{slug}'")
    return slug


def cmd_phase(args: argparse.Namespace) -> None:
    root = _require_root()
    state = load_state(root)
    slug = _resolve_task(state, args.slug)
    if args.phase not in PHASES:
        _die(f"phase must be one of: {', '.join(PHASES)}")
    state["tasks"][slug]["phase"] = args.phase
    state["tasks"][slug]["updated"] = _now()
    _sync_task_marker(root, slug, args.phase)
    save_state(root, state)
    print(f"task '{slug}' phase -> {args.phase}")


def cmd_advance(args: argparse.Namespace) -> None:
    root = _require_root()
    state = load_state(root)
    slug = _resolve_task(state, args.slug)
    cur = state["tasks"][slug]["phase"]
    idx = PHASES.index(cur)
    if idx >= len(PHASES) - 1:
        _die(f"task '{slug}' already at final phase ({cur})")
    nxt = PHASES[idx + 1]
    state["tasks"][slug]["phase"] = nxt
    state["tasks"][slug]["updated"] = _now()
    _sync_task_marker(root, slug, nxt)
    save_state(root, state)
    print(f"task '{slug}' phase {cur} -> {nxt}")


def cmd_gate(args: argparse.Namespace) -> None:
    root = _require_root()
    state = load_state(root)
    slug = _resolve_task(state, args.slug)
    if args.outcome not in GATES:
        _die(f"outcome must be one of: {', '.join(GATES)}")
    state["tasks"][slug]["gate"] = args.outcome
    if args.outcome == "PASS":
        state["tasks"][slug]["phase"] = "done"
        _sync_task_marker(root, slug, "done")
    state["tasks"][slug]["updated"] = _now()
    save_state(root, state)
    print(f"task '{slug}' gate -> {args.outcome}")
    if args.outcome == "HARD-STOP":
        print("HARD-STOP recorded: return to BUILD; nothing ships on a failing/security gate.")


def cmd_stage(args: argparse.Namespace) -> None:
    root = _require_root()
    state = load_state(root)
    if args.stage not in STAGES:
        _die(f"stage must be one of: {', '.join(STAGES)}")
    state["stage"] = args.stage
    save_state(root, state)
    print(f"project stage -> {args.stage}")


def cmd_status(args: argparse.Namespace) -> None:
    root = _require_root()
    state = load_state(root)
    active = state.get("active_task")
    print(f"project : {state['project']}")
    print(f"stage   : {state['stage']}")
    print(f"active  : {active or '(none)'}")
    tasks = state.get("tasks", {})
    if not tasks:
        print("tasks   : (none yet) -> add.py new-task <slug>")
        return
    print("tasks   :")
    for slug, t in tasks.items():
        mark = "*" if slug == active else " "
        print(f"  {mark} {slug:<24} phase={t['phase']:<10} gate={t['gate']}")
    if active:
        ph = tasks[active]["phase"]
        if ph == "done":
            print(f"\nresume  : task '{active}' is done ({tasks[active]['gate']}).")
            print("          start the next feature: add.py new-task <slug>")
        else:
            print(f"\nresume  : task '{active}' is at phase '{ph}'.")
            print(f"          read .add/tasks/{active}/TASK.md and continue that phase.")


def _sync_task_marker(root: Path, slug: str, phase: str) -> None:
    """Keep the `phase:` line inside TASK.md in sync with state.json."""
    task_md = root / "tasks" / slug / "TASK.md"
    if not task_md.exists():
        return
    lines = task_md.read_text(encoding="utf-8").splitlines()
    changed = False
    for i, line in enumerate(lines):
        if line.startswith("phase:"):
            comment = ""
            if "<!--" in line:
                comment = "   " + line[line.index("<!--"):]
            lines[i] = f"phase: {phase}{comment}"
            changed = True
            break
    if changed:
        _atomic_write(task_md, "\n".join(lines) + "\n")


# --- arg parsing -------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="add.py", description="ADD scaffolder + state tracker")
    sub = p.add_subparsers(dest="cmd", required=True)

    pi = sub.add_parser("init", help="create a .add/ project here")
    pi.add_argument("--dir", default=".", help="target directory (default: cwd)")
    pi.add_argument("--name", default=None, help="project name (default: dir name)")
    pi.add_argument("--stage", default="prototype", choices=STAGES)
    pi.add_argument("--force", action="store_true", help="reset state.json if present")
    pi.set_defaults(func=cmd_init)

    pn = sub.add_parser("new-task", help="scaffold a new task (TASK.md + tests/ + src/)")
    pn.add_argument("slug")
    pn.add_argument("--title", default=None)
    pn.add_argument("--force", action="store_true", help="overwrite TASK.md if present")
    pn.set_defaults(func=cmd_new_task)

    pp = sub.add_parser("phase", help="set a task's phase explicitly")
    pp.add_argument("phase", choices=PHASES)
    pp.add_argument("slug", nargs="?", default=None)
    pp.set_defaults(func=cmd_phase)

    pa = sub.add_parser("advance", help="move a task to the next phase")
    pa.add_argument("slug", nargs="?", default=None)
    pa.set_defaults(func=cmd_advance)

    pg = sub.add_parser("gate", help="record a verify gate outcome")
    pg.add_argument("outcome", choices=GATES)
    pg.add_argument("slug", nargs="?", default=None)
    pg.set_defaults(func=cmd_gate)

    ps = sub.add_parser("stage", help="set the project stage")
    ps.add_argument("stage", choices=STAGES)
    ps.set_defaults(func=cmd_stage)

    pst = sub.add_parser("status", help="print where the project is (resume point)")
    pst.set_defaults(func=cmd_status)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
