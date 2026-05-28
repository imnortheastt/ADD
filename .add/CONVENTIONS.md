# CONVENTIONS  (survivor layer — set once, kept for the whole project)

Language/framework:
  - Tooling: Python 3.12+ (standard library only — no third-party packages).
  - Installer: Node.js >= 16 (built-in modules only).
  - Method content: Markdown (the skill + the AIDD book).

Folders:
  - `add-method/`            the shippable npm package (`@mrq/add`)
    - `skill/add/`           thin router SKILL.md + `phases/*.md` (progressive disclosure)
    - `tooling/`             `add.py` (scaffolder + state tracker) + `templates/` + `test_add.py`
    - `bin/cli.js`           the `npx @mrq/add init` installer
    - `docs/`                the AIDD book bundled as the trust layer
  - `*.md` (repo root)       the AIDD book source chapters
  - `.add/`                  ADD runtime for THIS repo (dogfooding): state, tasks, survivor files

Naming: kebab-case files; snake_case Python; lowerCamelCase JS; task slugs alphanumeric + - _.

Lint/format: keep Python stdlib-idiomatic and type-hinted; no formatter enforced yet (add ruff in CI later).

Errors: machine-readable, never free text. The Python tool exits non-zero with `add: error: <msg>`.

Architecture:
  - The skill is thin and stateless; ALL state lives in `.add/state.json` (anti-context-rot).
  - The Python tool is the only writer of state; writes are atomic (temp + os.replace) and never clobber.
  - The method is tool-agnostic: gates are enforced by process/CI, not inside the agent.
