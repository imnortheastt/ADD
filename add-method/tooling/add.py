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
MILESTONE_FILE = "MILESTONE.md"
STAGES = ("prototype", "poc", "mvp", "production")
PHASES = ("specify", "scenarios", "contract", "tests", "build", "verify", "observe", "done")
GATES = ("none", "PASS", "RISK-ACCEPTED", "HARD-STOP")


def _phase_index(name: str) -> int:
    """Ordinal of a phase in PHASES; used to enforce forward-skip rules."""
    return PHASES.index(name)

# `add.py guide` copy: per-phase (concrete next action, book chapter to read).
# Keep the action wording aligned with each phase's EXIT line in the TASK template.
PHASE_GUIDE = {
    "specify":   ("state every rule — Must / Reject (+ named code) / After; leave zero open assumptions",
                  "03-step-1-specify.md"),
    "scenarios": ("write one Given/When/Then per Must AND per Reject; every result observable",
                  "04-step-2-scenarios.md"),
    "contract":  ("freeze the shape — signature, fields, error codes; names match the glossary",
                  "05-step-3-contract.md"),
    "tests":     ("write one failing test per scenario; run them RED for the right reason",
                  "06-step-4-tests.md"),
    "build":     ("write the minimum code to pass the tests; change no test and no contract",
                  "07-step-5-build.md"),
    "verify":    ("run the suite + blind-spot checks, then record the gate",
                  "08-step-6-verify.md"),
    "observe":   ("note what to watch + the spec delta for the next loop",
                  "09-the-loop.md"),
    "done":      ("this task is done — pick the next feature",
                  "02-the-flow.md"),
}
# Phase -> who owns it, for the `--json` autonomy signal. An autonomous harness may run a
# phase only when owner=="ai" (stop is false); every other phase is a checkpoint. The map
# follows the book's who-does-what table (Verify is "human only"); `tests`/`build`/`observe`
# are AI-led. A phase missing here is `unmapped_phase` (fail closed) — never defaulted.
PHASE_OWNER = {
    "specify": "human", "scenarios": "human", "contract": "seam",
    "tests": "ai", "build": "ai", "verify": "human", "observe": "ai", "done": "human",
}
SETUP_FILES = ("PROJECT.md", "CONVENTIONS.md", "GLOSSARY.md", "MODEL_REGISTRY.md", "dependencies.allowlist")

# Guideline-injection targets + version-stable markers. NEVER change these marker
# strings: a re-run finds the old block by exact match, so changing them would
# orphan every block written by a prior version (see TASK guideline-inject).
GUIDELINE_FILES = ("AGENTS.md", "CLAUDE.md")
_GUIDE_BEGIN = "<!-- ADD:BEGIN — managed by `add.py sync-guidelines`; do not edit inside -->"
_GUIDE_END = "<!-- ADD:END -->"

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


def _load_state_for_json() -> tuple[Path, dict]:
    """Fail-closed state load for `--json` paths: a missing project or unparseable
    state.json -> `no_state` on stderr + exit 1, with EMPTY stdout (never a partial
    JSON object a harness might parse). Built from State only — reads no docs/ chapter."""
    root = find_root()
    if root is None:
        _die("no_state")
    try:
        return root, json.loads((root / STATE_FILE).read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        _die("no_state")


def _phase_owner(phase: str) -> str:
    """Map a phase to its owner (human|seam|ai); `unmapped_phase` if absent (fail closed)."""
    owner = PHASE_OWNER.get(phase)
    if owner is None:
        _die("unmapped_phase")
    return owner


def save_state(root: Path, state: dict) -> None:
    state["updated"] = _now()
    _atomic_write(root / STATE_FILE, json.dumps(state, indent=2) + "\n")


def _die(msg: str, code: int = 1) -> None:
    print(f"add: error: {msg}", file=sys.stderr)
    raise SystemExit(code)


# --- guideline injection (dynamic-by-reference; designed for failure) --------
#
# Inject one stable, marker-delimited ADD block into the project root's AGENTS.md
# and CLAUDE.md. The block is DYNAMIC-BY-REFERENCE: it tells the agent to run
# `add.py status` and read PROJECT.md — it never embeds live state (slug, phase,
# gate). Auto-updated context files measurably hurt (ETH-Zurich: ~3% lower success,
# 20%+ more cost), so the stable pointer is the whole point.

def _guideline_block() -> str:
    """The canonical ADD block (markers + body, no trailing newline)."""
    return (
        f"{_GUIDE_BEGIN}\n"
        "## ADD — how to work in this repo\n"
        "\n"
        "This project uses **ADD (AI-Driven Development)**: you, the AI, drive the build;\n"
        "the human owns direction and verification. Before you change code:\n"
        "\n"
        "1. Run `python3 .add/tooling/add.py status` — where the project is and what's\n"
        "   next (the resume point; read it first every session).\n"
        "2. Read `.add/PROJECT.md` — the foundation (domain · spec · UI/UX) every task\n"
        "   builds on.\n"
        "3. Let the **`add` skill drive the flow**: INTAKE sizes the request into a\n"
        "   milestone, then each task runs the **one-approval front** — you draft Spec +\n"
        "   Scenarios + Contract + Tests as one bundle, the human gives ONE approval at the\n"
        "   frozen contract — followed by a self-driving build→verify run. `add.py` is your\n"
        "   hands (scaffold + track state); the human talks to you, not the CLI.\n"
        "\n"
        "The full method (the book) is in `.add/docs/`; the `add` skill loads the right\n"
        "phase guide on demand. This block is generated by `add.py sync-guidelines`; edit\n"
        "outside the markers, not inside.\n"
        f"{_GUIDE_END}"
    )


def _inject_block(path: Path) -> str:
    """Write the ADD block into `path`. Returns created|updated|unchanged.

    - unchanged: on-disk block already matches -> no write, no .bak (idempotent).
    - updated:   existing content changes -> back up the original to <path>.bak first.
    - created:   file did not exist -> write the block, no .bak.
    User content outside the markers is always preserved.
    """
    block = _guideline_block()
    if path.exists():
        current = path.read_text(encoding="utf-8")
        begin = current.find(_GUIDE_BEGIN)
        if begin != -1:
            end = current.find(_GUIDE_END, begin)
            if end != -1:                      # replace only the marked region
                end += len(_GUIDE_END)
                new = current[:begin] + block + current[end:]
            else:                              # begin without end: corrupt — append fresh
                print(f"add: warning: {path.name}: found an ADD:BEGIN with no ADD:END "
                      "— appending a fresh block; review the result", file=sys.stderr)
                new = current.rstrip("\n") + "\n\n" + block + "\n"
        else:                                  # no block yet — append, keep user content
            new = current.rstrip("\n") + "\n\n" + block + "\n"
        if new == current:
            return "unchanged"
        _atomic_write(Path(str(path) + ".bak"), current)   # rollback path before mutate
        _atomic_write(path, new)
        return "updated"
    _atomic_write(path, block + "\n")
    return "created"


def _inject_guidelines(project_root: Path) -> list[tuple[str, str]]:
    """Inject the block into each guideline file under `project_root`.

    Symlink-dedup: targets resolving (os.path.realpath) to the same inode are
    written once, against the REAL file (never replacing the symlink with a
    regular file). Per-target OSError is isolated (warn+skip) so one unwritable
    file never aborts the run or `init`.
    """
    results: list[tuple[str, str]] = []
    seen: set[str] = set()
    for name in GUIDELINE_FILES:
        target = project_root / name
        real = os.path.realpath(target)
        if real in seen:
            continue
        seen.add(real)
        write_target = Path(real) if target.is_symlink() else target
        try:
            action = _inject_block(write_target)
        except (OSError, UnicodeDecodeError) as exc:
            # design for failure: an unwritable target OR a non-UTF-8 existing file
            # (e.g. a UTF-16 CLAUDE.md from a Windows editor) must not crash init or
            # abort the other target — warn and skip this one.
            print(f"add: warning: could not sync {name} — {exc}; skipped",
                  file=sys.stderr)
            action = "skipped"
        results.append((name, action))
    return results


# --- commands ----------------------------------------------------------------

def cmd_init(args: argparse.Namespace) -> None:
    base = Path(args.dir).resolve()
    root = base / ROOT_DIRNAME
    state_path = root / STATE_FILE
    if state_path.exists() and not args.force:
        _die(f"already initialised at {root} (use --force to reset state)")

    (root / "tasks").mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    proj_name = args.name or base.name

    # survivor-layer files — never clobber an existing one, never write a blank one
    for fname in SETUP_FILES:
        dest = root / fname
        if dest.exists():
            continue
        rendered = _render_template(fname, date=today, project=proj_name, stage=args.stage)
        if not rendered.strip():
            # A missing/stale template rendered to nothing. Skip rather than create
            # a 0-content survivor file (design-for-failure; circuit breaker so an
            # upgrade with a stale templates/ dir can't silently produce empty docs).
            print(f"add: warning: template for {fname} is missing/blank — skipped",
                  file=sys.stderr)
            continue
        _atomic_write(dest, rendered)

    state = {
        "project": proj_name,
        "stage": args.stage,
        "active_task": None,
        "active_milestone": None,
        "tasks": {},
        "milestones": {},
        "created": _now(),
        "updated": _now(),
    }
    save_state(root, state)
    # zero-config: give any agent a stable pointer into the ADD runtime.
    for name, action in _inject_guidelines(base):
        if action != "unchanged":
            print(f"{action:>9}  {name}")
    print(f"initialised ADD project '{state['project']}' (stage: {state['stage']}) at {root}")
    print("next: open Claude Code, run `/add`, and say what you want to build —")
    print("      the `add` skill sizes it into a milestone and drives the build with you.")


def cmd_sync_guidelines(args: argparse.Namespace) -> None:
    project_root = _require_root().parent
    for name, action in _inject_guidelines(project_root):
        print(f"{action:>9}  {name}")


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

    # link to a milestone (explicit, or the active one) — validate before any write
    milestone = getattr(args, "milestone", None) or state.get("active_milestone")
    if milestone and milestone not in state.get("milestones", {}):
        _die("unknown_milestone")
    depends_on = _parse_deps(getattr(args, "depends_on", None))

    (tdir / "tests").mkdir(parents=True, exist_ok=True)
    (tdir / "src").mkdir(parents=True, exist_ok=True)
    title = args.title or slug.replace("-", " ").replace("_", " ").title()
    _atomic_write(task_md, _render_template(
        "TASK.md", title=title, slug=slug, date=date.today().isoformat(), stage=state["stage"]))

    state["tasks"][slug] = {
        "title": title,
        "phase": "specify",
        "gate": "none",
        "milestone": milestone,
        "depends_on": depends_on,
        "created": _now(),
        "updated": _now(),
    }
    state["active_task"] = slug
    save_state(root, state)
    print(f"created task '{slug}' -> {task_md}")
    if milestone:
        print(f"linked to milestone '{milestone}'" +
              (f", depends-on {depends_on}" if depends_on else ""))
    else:
        # warn-never-block: the task is created (escape hatch), but nudge back toward the
        # intake -> milestone flow. Speaks of STRUCTURE (not attached), never the act.
        print(f"note: '{slug}' is not attached to a milestone — size it via /add (intake), "
              "or pass --milestone <id>")
    print("active task set. phase: specify. Fill section 1 (SPECIFY), then: add.py advance")


def _parse_deps(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [d.strip() for d in raw.split(",") if d.strip()]


def _task_done(t: dict) -> bool:
    # Matrix 3: a task is done when Verify reads PASS *or a signed RISK-ACCEPTED*.
    # Both completing gates advance phase to "done" (cmd_gate), and a waiver is
    # signed at gate time — so a verdict gate is enough here; we need not re-read
    # the waiver. HARD-STOP never reaches "done". A bare `phase done` (escape
    # hatch, gate still "none") deliberately does NOT count: completion needs a
    # recorded verdict, not just a phase marker.
    return t.get("phase") == "done" and t.get("gate") in ("PASS", "RISK-ACCEPTED")


def _archived_task_slugs(state: dict) -> set[str]:
    """Slugs of tasks that left active state via archive — all were PASS-done at
    archive time, so a dep on one of them counts as satisfied (not dangling).

    INVARIANT: this is sound only because cmd_archive_milestone REFUSES to archive a
    milestone with an incomplete member. Any NEW task-removal path (un-archive/restore,
    heavy archive) MUST preserve "archived ⇒ was PASS-done" or `ready` will green-light
    a task whose dependency never completed."""
    out: set[str] = set()
    for rec in state.get("archived", []):
        out.update(rec.get("task_slugs", []))   # .get: pre-v2 records have none
    return out


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
    # Completing outcomes (PASS, RISK-ACCEPTED) are the VERIFY step's verdict, so they
    # share the verify-phase guard — no silent skips (principle 7). HARD-STOP stays
    # recordable from any phase (a security finding is always HARD-STOP). The
    # deliberate, logged override is `add.py phase verify <slug>`.
    completing = args.outcome in ("PASS", "RISK-ACCEPTED")
    if completing:
        current = state["tasks"][slug]["phase"]
        if _phase_index(current) < _phase_index("verify"):
            code = ("gate_pass_before_verify" if args.outcome == "PASS"
                    else "gate_risk_accepted_before_verify")
            _die(f"{code}: task '{slug}' is at '{current}'; reach the verify phase "
                 f"first (or `add.py phase verify {slug}` to override)")
    if args.outcome == "RISK-ACCEPTED":
        # A waiver must be SIGNED: owner, ticket, expiry (glossary). Stored in state
        # so a later `check` can read/expire it. Refuse a partial waiver outright.
        missing = [f for f in ("owner", "ticket", "expires") if not getattr(args, f)]
        if missing:
            _die("waiver_incomplete: RISK-ACCEPTED is a signed waiver; supply "
                 + ", ".join("--" + m for m in missing))
        state["tasks"][slug]["waiver"] = {
            "owner": args.owner, "ticket": args.ticket, "expires": args.expires,
        }
    if completing:
        state["tasks"][slug]["phase"] = "done"
        _sync_task_marker(root, slug, "done")
    state["tasks"][slug]["gate"] = args.outcome
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
    if getattr(args, "json", False):
        _, state = _load_state_for_json()
        tasks = state.get("tasks") or {}
        milestones = state.get("milestones") or {}
        ms_list = []
        for mslug, m in milestones.items():
            members = [t for t in tasks.values() if t.get("milestone") == mslug]
            ms_list.append({"slug": mslug, "status": m.get("status", "active"),
                            "done": sum(1 for t in members if _task_done(t)),
                            "total": len(members)})
        print(json.dumps({
            "project": state.get("project"), "stage": state.get("stage"),
            "active_task": state.get("active_task"),
            "milestones": ms_list,
            "tasks": [{"slug": s, "phase": t.get("phase"), "gate": t.get("gate"),
                       "milestone": t.get("milestone")} for s, t in tasks.items()]}))
        return
    root = _require_root()
    state = load_state(root)
    active = state.get("active_task")
    tasks = state.get("tasks", {})
    print(f"project : {state['project']}")
    print(f"stage   : {state['stage']}")
    # foundation pointer — read the cross-milestone context first (anti-rot)
    if (root / "PROJECT.md").exists():
        print("context : .add/PROJECT.md  (foundation: domain · spec · UI/UX — read first)")

    # milestone rollup (only when milestones are in use)
    milestones = state.get("milestones") or {}
    active_ms = state.get("active_milestone")
    if milestones:
        print("milestones:")
        for mslug, m in milestones.items():
            members = [t for t in tasks.values() if t.get("milestone") == mslug]
            done = sum(1 for t in members if _task_done(t))
            mark = "*" if mslug == active_ms else " "
            print(f"  {mark} {mslug:<20} {done}/{len(members)} tasks done"
                  f"   status={m.get('status', 'active')}")

    # archived rollup — one line keeps state visible without re-bloating status
    archived = state.get("archived") or []
    if archived:
        n = len(archived)
        m_tasks = sum(rec.get("tasks", 0) for rec in archived)
        print(f"archived: {n} milestone{'s' if n != 1 else ''} "
              f"({m_tasks} task{'s' if m_tasks != 1 else ''})")

    print(f"active  : {active or '(none)'}")
    if not tasks:
        print("tasks   : (none yet) -> add.py new-task <slug>")
        return
    print("tasks   :")
    for slug, t in tasks.items():
        mark = "*" if slug == active else " "
        deps = t.get("depends_on") or []
        dep_s = f"  deps={','.join(deps)}" if deps else ""
        ms_s = f"  [{t['milestone']}]" if t.get("milestone") else ""
        print(f"  {mark} {slug:<24} phase={t['phase']:<10} gate={t['gate']}{ms_s}{dep_s}")
    if active:
        ph = tasks[active]["phase"]
        if ph == "done":
            print(f"\nresume  : task '{active}' is done ({tasks[active]['gate']}).")
            print("          start the next feature: add.py new-task <slug>")
        else:
            print(f"\nresume  : task '{active}' is at phase '{ph}'.")
            print(f"          read .add/tasks/{active}/TASK.md and continue that phase.")


def cmd_guide(args: argparse.Namespace) -> None:
    """Answer "what do I do next?" for the active (or named) task.

    Strictly read-only: load_state only — never save_state, never writes a TASK.md.
    """
    if getattr(args, "json", False):
        _, state = _load_state_for_json()
        slug = args.slug or state.get("active_task")
        if not slug:
            print(json.dumps({"task": None, "phase": None, "owner": "human", "stop": True,
                              "next_step": "start your first feature -> add.py new-task <slug>",
                              "chapter": ".add/docs/02-the-flow.md", "gate": None}))
            return
        t = (state.get("tasks") or {}).get(slug)
        if t is None:
            _die(f"unknown task '{slug}'")
        phase = t.get("phase")
        owner = _phase_owner(phase)            # _die unmapped_phase before any stdout
        action, chapter = PHASE_GUIDE[phase]   # phase is mapped, so PHASE_GUIDE has it too
        print(json.dumps({"task": slug, "phase": phase, "owner": owner,
                          "stop": owner != "ai", "next_step": action,
                          "chapter": f".add/docs/{chapter}", "gate": t.get("gate")}))
        return
    root = _require_root()
    state = load_state(root)
    slug = args.slug or state.get("active_task")
    if not slug:
        print("active : (none)")
        print('next   : start your first feature -> add.py new-task <slug> --title "..."')
        print("read   : .add/docs/02-the-flow.md")
        return
    if slug not in state.get("tasks", {}):
        _die(f"unknown task '{slug}'")
    phase = state["tasks"][slug]["phase"]
    entry = PHASE_GUIDE.get(phase)
    if entry is None:           # corrupted/hand-edited state.json — fail clean, not KeyError
        _die(f"task '{slug}' has unknown phase '{phase}' (state.json corrupted?)")
    action, chapter = entry
    print(f"active : {slug}  (phase: {phase})")
    print(f"next   : {action}")
    print(f"read   : .add/docs/{chapter}")
    if phase == "verify":
        print("then   : add.py gate PASS | RISK-ACCEPTED | HARD-STOP")
    elif phase == "done":
        print("then   : start the next feature -> add.py new-task <slug>")
    else:
        print("then   : add.py advance")


def _read_task_phase(root: Path, slug: str) -> str | None:
    """Read the `phase:` marker from a task's TASK.md, or None if absent."""
    task_md = root / "tasks" / slug / "TASK.md"
    if not task_md.exists():
        return None
    for line in task_md.read_text(encoding="utf-8").splitlines():
        if line.startswith("phase:"):
            rest = line[len("phase:"):].strip()
            return rest.split()[0] if rest else None
    return None


def cmd_check(args: argparse.Namespace) -> None:
    """Read-only integrity check of the .add project. Exit 1 if anything fails."""
    as_json = getattr(args, "json", False)
    if as_json:
        root, state = _load_state_for_json()       # fail closed -> no_state + empty stdout
    else:
        root = find_root()
        if root is None:
            _die("no_project")
        try:
            state = json.loads((root / STATE_FILE).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            _die("state_invalid")

    checks: list[tuple[bool, str, str]] = []  # (ok, description, reason-if-failed)
    for key in ("project", "stage", "active_task", "tasks"):
        checks.append((key in state, f"state has key '{key}'", "missing"))

    tasks = state.get("tasks") if isinstance(state.get("tasks"), dict) else {}
    milestones = state.get("milestones") if isinstance(state.get("milestones"), dict) else {}
    archived_slugs = _archived_task_slugs(state)   # archived deps still resolve
    warnings: list[tuple[str, str]] = []  # (name, reason) — nudges that NEVER feed `failed`
    for slug, t in tasks.items():
        task_md = root / "tasks" / slug / "TASK.md"
        checks.append((task_md.exists(), f"task '{slug}' has TASK.md", "file missing"))
        marker, want = _read_task_phase(root, slug), t.get("phase")
        checks.append((marker == want, f"task '{slug}' marker matches state",
                       f"marker={marker!r} state={want!r}"))
        # drift: milestone + dependency references must resolve
        ms = t.get("milestone")
        if ms is not None:
            checks.append((ms in milestones, f"task '{slug}' milestone resolves",
                           f"unknown milestone {ms!r}"))
        else:
            # warn-never-block: a task outside a milestone is a structural nudge back toward
            # the intake flow — NOT a failure. Names structure, never the act of intake.
            warnings.append((f"task '{slug}'", "is outside a milestone — size it via the /add "
                                               "intake flow (or attach with --milestone)"))
        for dep in t.get("depends_on") or []:
            checks.append((dep in tasks or dep in archived_slugs,
                           f"task '{slug}' dep '{dep}' resolves", "unknown task"))
        # waiver expiry (Matrix 4): a RISK-ACCEPTED waiver whose `expires` has passed is
        # stale — the gate stored it; `check` is the standing monitor that catches the lapse.
        # Fail-closed: a missing/unparseable expires is a FAIL, never a silent pass.
        if t.get("gate") == "RISK-ACCEPTED":
            exp = (t.get("waiver") or {}).get("expires")
            try:
                ok = exp is not None and date.fromisoformat(exp) >= date.today()
                reason = f"waiver_expired (expires={exp})"
            except (ValueError, TypeError):
                ok, reason = False, f"waiver_expired (unparseable expires={exp!r})"
            checks.append((ok, f"task '{slug}' waiver not expired", reason))

    # drift: a done milestone must have no unfinished tasks
    for mslug, m in milestones.items():
        if m.get("status") == "done":
            unfinished = [s for s, t in tasks.items()
                          if t.get("milestone") == mslug and not _task_done(t)]
            checks.append((not unfinished, f"done milestone '{mslug}' fully complete",
                           f"unfinished: {unfinished}"))

    # dependency graph must be acyclic
    cycle = _find_cycle(tasks)
    checks.append((cycle is None, "task dependencies are acyclic",
                   f"cycle: {' -> '.join(cycle)}" if cycle else ""))

    passed = sum(1 for ok, _, _ in checks if ok)
    failed = len(checks) - passed
    if as_json:
        print(json.dumps({"passed": passed, "failed": failed,
                          "warned": len(warnings),
                          "warnings": [{"name": name, "reason": reason}
                                       for name, reason in warnings],
                          "checks": [{"ok": ok, "name": desc,
                                      "reason": reason if not ok else ""}
                                     for ok, desc, reason in checks]}))
    else:
        for ok, desc, reason in checks:
            print(f"PASS  {desc}" if ok else f"FAIL  {desc}: {reason}")
        for name, reason in warnings:
            print(f"WARN  {name} {reason}")
        summary = f"check: {passed} passed, {failed} failed"
        if warnings:
            summary += f" ({len(warnings)} warnings)"   # frozen §3: summary gains "(N warnings)"
        print(summary)
    if failed:
        raise SystemExit(1)


def cmd_new_milestone(args: argparse.Namespace) -> None:
    root = _require_root()
    state = load_state(root)
    slug = args.slug
    if not slug.replace("-", "").replace("_", "").isalnum():
        _die("bad_slug")
    state.setdefault("milestones", {})
    mdir = root / "milestones" / slug
    mfile = mdir / MILESTONE_FILE
    if mfile.exists() and not args.force:
        _die("milestone_exists")
    mdir.mkdir(parents=True, exist_ok=True)
    title = args.title or slug.replace("-", " ").replace("_", " ").title()
    _atomic_write(mfile, _render_template(
        "MILESTONE.md", title=title, goal=args.goal or "<goal>",
        stage=args.stage, date=date.today().isoformat()))
    state["milestones"][slug] = {
        "title": title, "goal": args.goal or "", "stage": args.stage,
        "status": "active", "created": _now(), "updated": _now(),
    }
    state["active_milestone"] = slug
    save_state(root, state)
    print(f"created milestone '{slug}' -> {mfile}")
    print(f"active milestone set. Decompose it into tasks: add.py new-task <slug> --depends-on ...")


def cmd_ready(args: argparse.Namespace) -> None:
    if getattr(args, "json", False):
        _, state = _load_state_for_json()
        tasks = state.get("tasks") or {}
        archived = _archived_task_slugs(state)

        def _ok(d: str) -> bool:
            return d in archived or (d in tasks and _task_done(tasks[d]))

        ready, blocked = [], []
        for slug, t in tasks.items():
            if _task_done(t):
                continue
            unmet = [d for d in (t.get("depends_on") or []) if not _ok(d)]
            (blocked.append({"slug": slug, "waiting_on": unmet})
             if unmet else ready.append(slug))
        print(json.dumps({"ready": ready, "blocked": blocked}))
        return
    root = _require_root()
    state = load_state(root)
    tasks = state.get("tasks", {})
    archived_slugs = _archived_task_slugs(state)   # an archived dep was PASS-done

    def _dep_satisfied(d: str) -> bool:
        if d in archived_slugs:
            return True                            # archived ⇒ complete when archived
        return d in tasks and _task_done(tasks[d]) # in-state dep must be done; else blocked

    ready = []
    for slug, t in tasks.items():
        if _task_done(t):
            continue
        deps = t.get("depends_on") or []
        if all(_dep_satisfied(d) for d in deps):
            ready.append(slug)
    if not ready:
        print("ready: (none — all tasks are done or blocked)")
        return
    print("ready to start (deps satisfied):")
    for slug in ready:
        deps = tasks[slug].get("depends_on") or []
        suffix = f"  (after {', '.join(deps)})" if deps else ""
        print(f"  {slug}{suffix}")


def cmd_milestone_done(args: argparse.Namespace) -> None:
    root = _require_root()
    state = load_state(root)
    slug = args.slug
    if slug not in state.get("milestones", {}):
        _die("unknown_milestone")
    members = {s: t for s, t in state.get("tasks", {}).items() if t.get("milestone") == slug}
    blockers = [s for s, t in members.items() if not _task_done(t)]
    if not members:
        _die("milestone_incomplete")  # nothing attached -> nothing proven
    if blockers:
        print(f"milestone '{slug}' has unfinished tasks:", file=sys.stderr)
        for s in blockers:
            t = members[s]
            print(f"  - {s} (phase={t.get('phase')}, gate={t.get('gate')})", file=sys.stderr)
        _die("milestone_incomplete")
    state["milestones"][slug]["status"] = "done"
    state["milestones"][slug]["updated"] = _now()
    save_state(root, state)
    waived = [s for s, t in members.items() if t.get("gate") == "RISK-ACCEPTED"]
    tail = f" ({len(waived)} via a signed RISK-ACCEPTED waiver)" if waived else ""
    print(f"milestone '{slug}' -> done ({len(members)} tasks complete{tail}).")
    print("Confirm the MILESTONE.md exit criteria are checked, then archive/start the next.")


def cmd_archive_milestone(args: argparse.Namespace) -> None:
    """Light archive: collapse a DONE milestone out of active state (files stay)."""
    root = _require_root()
    state = load_state(root)
    slug = args.slug
    # validate before any mutation — a reject must leave state.json byte-for-byte unchanged
    if slug not in state.get("milestones", {}):
        _die("unknown_milestone")
    ms = state["milestones"][slug]
    if ms.get("status") != "done":
        _die("milestone_not_done")        # run `add.py milestone-done` first; never lose live work
    tasks = state.get("tasks", {})
    members = [s for s, t in tasks.items() if t.get("milestone") == slug]
    # the status flag can go stale (a task attached AFTER milestone-done is still
    # live); re-check now so archive can never silently delete unfinished work.
    incomplete = [s for s in members if not _task_done(tasks[s])]
    if incomplete:
        print(f"milestone '{slug}' has live unfinished tasks:", file=sys.stderr)
        for s in incomplete:
            t = tasks[s]
            print(f"  - {s} (phase={t.get('phase')}, gate={t.get('gate')})", file=sys.stderr)
        _die("milestone_has_incomplete_tasks")
    # a slug-list summary (never task bodies) so the active state can't regrow,
    # yet cross-milestone deps on these tasks still resolve (see _archived_task_slugs)
    state.setdefault("archived", []).append({
        "slug": slug,
        "title": ms.get("title", slug),
        "tasks": len(members),
        "task_slugs": members,
        "archived": date.today().isoformat(),
    })
    del state["milestones"][slug]
    for s in members:
        del tasks[s]
    if state.get("active_milestone") == slug:
        state["active_milestone"] = None
    if state.get("active_task") in members:
        state["active_task"] = None
    save_state(root, state)
    print(f"archived milestone '{slug}' ({len(members)} tasks) — removed from active state.")
    print("files on disk are untouched; see `add.py status` for the archived rollup.")


def cmd_set_milestone(args: argparse.Namespace) -> None:
    root = _require_root()
    state = load_state(root)
    task = args.task
    if task not in state.get("tasks", {}):
        _die("unknown_task")
    if args.milestone == "none":
        new = None
    elif args.milestone in state.get("milestones", {}):
        new = args.milestone
    else:
        _die("unknown_milestone")
    state["tasks"][task]["milestone"] = new
    state["tasks"][task]["updated"] = _now()
    save_state(root, state)
    print(f"task '{task}' -> milestone '{new}'" if new else f"task '{task}' -> milestone (none)")


def _find_cycle(tasks: dict) -> list[str] | None:
    """Return a cycle path in the depends_on graph, or None. Ignores unknown deps."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {s: WHITE for s in tasks}
    stack: list[str] = []

    def visit(node: str) -> list[str] | None:
        color[node] = GRAY
        stack.append(node)
        for dep in tasks[node].get("depends_on") or []:
            if dep not in tasks:
                continue
            if color[dep] == GRAY:
                return stack[stack.index(dep):] + [dep]
            if color[dep] == WHITE:
                found = visit(dep)
                if found:
                    return found
        color[node] = BLACK
        stack.pop()
        return None

    for s in tasks:
        if color[s] == WHITE:
            found = visit(s)
            if found:
                return found
    return None


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
    pn.add_argument("--milestone", default=None, help="attach to a milestone (default: active)")
    pn.add_argument("--depends-on", dest="depends_on", default=None,
                    help="comma-separated task slugs this task depends on")
    pn.add_argument("--force", action="store_true", help="overwrite TASK.md if present")
    pn.set_defaults(func=cmd_new_task)

    pm = sub.add_parser("new-milestone", help="scaffold a milestone (SDD living doc)")
    pm.add_argument("slug")
    pm.add_argument("--title", default=None)
    pm.add_argument("--goal", default=None, help="one-sentence outcome")
    pm.add_argument("--stage", default="mvp", choices=STAGES)
    pm.add_argument("--force", action="store_true", help="overwrite MILESTONE.md if present")
    pm.set_defaults(func=cmd_new_milestone)

    pr = sub.add_parser("ready", help="list tasks whose dependencies are satisfied")
    pr.add_argument("--json", action="store_true", help="machine-readable JSON output")
    pr.set_defaults(func=cmd_ready)

    pmd = sub.add_parser("milestone-done", help="exit-gate a milestone (all tasks must PASS)")
    pmd.add_argument("slug")
    pmd.set_defaults(func=cmd_milestone_done)

    psm = sub.add_parser("set-milestone", help="attach/move/detach an existing task")
    psm.add_argument("task")
    psm.add_argument("milestone", help="milestone slug, or 'none' to detach")
    psm.set_defaults(func=cmd_set_milestone)

    pam = sub.add_parser("archive-milestone",
                         help="collapse a done milestone out of active state (files stay on disk)")
    pam.add_argument("slug")
    pam.set_defaults(func=cmd_archive_milestone)

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
    pg.add_argument("--owner", help="RISK-ACCEPTED waiver: accountable owner")
    pg.add_argument("--ticket", help="RISK-ACCEPTED waiver: tracking ticket/link")
    pg.add_argument("--expires", help="RISK-ACCEPTED waiver: expiry date")
    pg.set_defaults(func=cmd_gate)

    ps = sub.add_parser("stage", help="set the project stage")
    ps.add_argument("stage", choices=STAGES)
    ps.set_defaults(func=cmd_stage)

    pst = sub.add_parser("status", help="print where the project is (resume point)")
    pst.add_argument("--json", action="store_true", help="machine-readable JSON output")
    pst.set_defaults(func=cmd_status)

    pck = sub.add_parser("check", help="read-only integrity check of the .add project")
    pck.add_argument("--json", action="store_true", help="machine-readable JSON output")
    pck.set_defaults(func=cmd_check)

    psg = sub.add_parser("sync-guidelines",
                         help="(re)write the ADD guideline block into AGENTS.md + CLAUDE.md")
    psg.set_defaults(func=cmd_sync_guidelines)

    pgd = sub.add_parser("guide", help="print the one concrete next step for the active task")
    pgd.add_argument("slug", nargs="?", default=None, help="task slug (default: active task)")
    pgd.add_argument("--json", action="store_true", help="machine-readable JSON output")
    pgd.set_defaults(func=cmd_guide)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
