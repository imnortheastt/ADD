# Phase 0 — Setup (once per project)

Goal: make every later gate enforceable automatically. Do this once.

## Do

1. Initialise the runtime (creates `.add/` + survivor-layer files):
   ```bash
   python3 .add/tooling/add.py init --name "<project>" --stage prototype
   ```
   If the tool isn't there yet, the installer (`npx @pilotspace/add init`) placed it at
   `.add/tooling/add.py`.
2. Fill the survivor-layer files (they outlive all code):
   - `.add/PROJECT.md` — **the foundation**: Domain (DDD) · Spec/Living-Document (SDD,
     → active milestone) · UI/UX (UDD) · Key Decisions. Cross-milestone context the
     engine reads first. Keep it to one screen. Book: `docs/14-foundation.md`.
     **Brainstorm it before you fill it — see below.**
   - `.add/CONVENTIONS.md` — language, folders, naming, lint, error-code style, architecture.
   - `.add/GLOSSARY.md` — one name per concept; used in specs, contracts, and code.
   - `.add/MODEL_REGISTRY.md` — which AI model/version writes this project.
   - `.add/dependencies.allowlist` — packages the AI may use; CI rejects others.
3. Confirm CI runs green on the empty skeleton before the first feature.

### Brainstorm the foundation before you fill it — co-specify at foundation altitude

`PROJECT.md` is read first by every later loop — a guess here propagates into every
milestone. Run the same co-specify move as a task's §1 (`phases/1-specify.md`) across
the four lenses: ask the load-bearing question per lens (diverge), draft the whole file
(converge), then show it with the least-sure flag first (validate). Keep it to one
screen — interview for the facts that bear weight, not a manual.

| Lens | The one question that unblocks the section |
|------|--------------------------------------------|
| Domain (DDD) | The 3–5 core nouns, and the one invariant that must NEVER break? |
| Spec (SDD) | The first milestone's outcome — and what's explicitly NOT in v1? |
| Users (UDD) | The primary user and the one job they hire this for? (or "no UI — surface is X") |
| Decisions | What's already decided that you'd regret re-litigating? (first Key Decision row) |

Ask only the live ones; skip what the request already answers. Rank what you're least
sure of; the top flag the human reads at confirm:
`⚠ <assumption> — least sure because <why>; if wrong: <cost>`.

## Exit gate

- [ ] `.add/state.json` exists (`add.py status` works).
- [ ] `.add/PROJECT.md` foundation filled (domain · spec · UI/UX).
- [ ] CONVENTIONS, GLOSSARY, MODEL_REGISTRY, allowlist filled.
- [ ] Pipeline green on the skeleton.

## Next

```bash
python3 .add/tooling/add.py new-task <slug> --title "<feature>"
```
Then read `phases/1-specify.md`. · Book: `docs/10-setup-and-stages.md`.
