# Phase 0 — Setup (autonomous draft → one human lock-down)

Goal: point ADD at a repo and **you** draft the whole foundation — domain, first-milestone scope,
and the first task's contract — then hand the human exactly one decision: the **lock-down**. Brownfield
is silent (the code answers the questions); greenfield keeps a short interview. Either way, the human's
only gate is `add.py lock`. This is the setup-altitude analog of a task's one-approval contract freeze.

## 1 · Zero-touch entry — you run init yourself

When there is no `.add/state.json`, do **not** tell the human to initialise — run it yourself. Infer the
project name and stage from the repo, and **arm the lock-down gate** with `--await-lock`:

```bash
python3 .add/tooling/add.py init --name "<inferred from repo/dir>" --stage <prototype|poc|mvp|production> --await-lock
```

- `--await-lock` is **required** here: it seeds an *unlocked* setup, which arms the gate so the engine
  refuses a second task / crossing into build / a `gate` until you `lock`. A plain `init` is
  grandfathered-locked — its gate never arms, and the closing `lock` would error `already_locked`.
- name + stage are **your judgment** (read them from the dir name, README, manifests); the engine stays
  mechanical. Pick the stage from the ambition you hear: throwaway → `prototype`, one risky slice → `poc`,
  narrow-but-real → `mvp`, full rigor → `production`.

`init` prints one of two things — **that is your branch**:
- a line starting `brownfield:` → there is existing code (go to **2a**);
- the greenfield closing (no `brownfield:`) → an empty repo (go to **2b**).

## 2a · Brownfield — map it silently

The code answers the questions a greenfield interview would ask, so **read it instead of asking**. Open
`adopt.md` and follow it: fill each missing survivor file from the code, keep an existing one unchanged, and tag
every decision `evidence-grounded` (cite the file) or `guessed`. Ask the human **nothing** at this step.

## 2b · Greenfield — the 4-lens interview (kept): co-specify at foundation altitude

An empty repo has no code to read, so run the short interview. This is the **co-specify at foundation
altitude** move — the same diverge → converge → validate brainstorm a task's §1 uses (`phases/1-specify.md`),
lifted to the foundation. Ask the one load-bearing question per lens (diverge), draft the foundation
(converge), then rank what you're least sure of and show the top flag first (validate):

| Lens | The one question that unblocks the section |
|------|--------------------------------------------|
| Domain (DDD) | The 3–5 core nouns, and the one invariant that must NEVER break? |
| Spec (SDD) | The first milestone's outcome — and what's explicitly NOT in v1? |
| Users (UDD) | The primary user and the one job they hire this for? (or "no UI — surface is X") |
| Decisions | What's already decided that you'd regret re-litigating? (first Key Decision row) |

Ask only the live ones; skip what the request already answers. Rank your drafts least-sure-first using the
one notation every altitude shares — `⚠ <assumption> — least sure because <why>; if wrong: <cost>` — and
tag thin or inferred answers `guessed`.

## 3 · Draft to the lock (both paths)

1. **Fill the survivors** (they outlive all code): `.add/PROJECT.md` (the foundation — Domain · Spec/active
   milestone · UI/UX · Key Decisions, one screen), `CONVENTIONS.md`, `GLOSSARY.md`, `MODEL_REGISTRY.md`,
   `dependencies.allowlist`. Brownfield: from the code. Greenfield: from the interview, gaps flagged `guessed`.
2. **Size the first milestone** (read `scope.md`) and draft its `MILESTONE.md` — goal · scope · exit criteria
   · breadth-first tasks.
3. **Create the first task and draft its candidate front.** `new-task` is allowed pre-lock:
   ```bash
   python3 .add/tooling/add.py new-task <slug> --title "<first feature>"
   ```
   Draft §1 (specify) · §2 (scenarios) · §3 (contract). **Leave §3 `Status: DRAFT`** — the lock is its
   approval (see §5). You MAY `advance` through specify → scenarios → contract → tests pre-lock, but the
   engine **refuses crossing into build** until you `lock` (`setup_unlocked`). Sequence: front → lock → build.
4. **Write `.add/SETUP-REVIEW.md`** per `setup-review.md`: every decision you drafted (foundation, scope,
   first contract), **least-sure-first**, each tagged `guessed` | `evidence-grounded`.

## 4 · The one human gate — the lock-down

Present `SETUP-REVIEW.md` least-sure-first (the `guessed` rows are what the human must actually check). They
confirm **once** — an explicit yes to the lock-down itself, in conversation; ambient agreement mid-stream is
not a confirmation. On that recorded confirmation, you run the lock with their name:

```bash
python3 .add/tooling/add.py lock --by "<name>"
```

Typing the command themselves stays the **escape hatch** — the decision is always the human's; you just
execute it. `lock` records the lock layers (foundation · scope · contract) in one atomic write and opens the
build. It is judgment-free — it does **not** parse `SETUP-REVIEW.md`; the human *reading* it is the review.

## 5 · After the lock

- The lock **is** the first task's contract approval — the v7 one-approval-front and the lock-down collapse
  into this single signature. Do **not** ask for a separate contract-freeze sign-off (that double-gates).
- Stamp the first task's §3 `Status: FROZEN @ v1` (lock-authorized), then read `phases/5-build.md` — build is
  now open. Everything before this signature, you drafted.

## Exit gate

<exit_gate>
- [ ] `.add/state.json` exists; setup was seeded unlocked (`--await-lock`) then locked.
- [ ] Survivors filled (brownfield: from code, tagged evidence-grounded; greenfield: from the interview).
- [ ] First task created; §1–§3 drafted; `.add/SETUP-REVIEW.md` written least-sure-first.
- [ ] Human confirmed the lock-down and `add.py lock --by` ran with their name; first task §3 `FROZEN @ v1`; build open.
</exit_gate>

## Next

After the lock, read `phases/5-build.md` (build is open). · Book: `docs/10-setup-and-stages.md`
*(note: book chapters 10 / 13 / 14 still describe the older human-led setup until `book-align` lands).*
