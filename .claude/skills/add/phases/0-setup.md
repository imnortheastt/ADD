# Phase 0 — Setup (once per project)

Goal: make every later gate enforceable automatically. Do this once.

## Do

1. Initialise the runtime (creates `.add/` + survivor-layer files):
   ```bash
   python3 .add/tooling/add.py init --name "<project>" --stage prototype
   ```
   If the tool isn't there yet, the installer (`npx @mrq/add init`) placed it at
   `.add/tooling/add.py`.
2. Fill the survivor-layer files (they outlive all code):
   - `.add/CONVENTIONS.md` — language, folders, naming, lint, error-code style, architecture.
   - `.add/GLOSSARY.md` — one name per concept; used in specs, contracts, and code.
   - `.add/MODEL_REGISTRY.md` — which AI model/version writes this project.
   - `.add/dependencies.allowlist` — packages the AI may use; CI rejects others.
3. Confirm CI runs green on the empty skeleton before the first feature.

## Exit gate

- [ ] `.add/state.json` exists (`add.py status` works).
- [ ] CONVENTIONS, GLOSSARY, MODEL_REGISTRY, allowlist filled.
- [ ] Pipeline green on the skeleton.

## Next

```bash
python3 .add/tooling/add.py new-task <slug> --title "<feature>"
```
Then read `phases/1-specify.md`. · Book: `docs/10-setup-and-stages.md`.
