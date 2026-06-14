# Contributing — repo layout & the edit-then-sync model

This repo is three things at once: the **AIDD book**, the **`add` skill + engine**,
and the **shippable package** (`@pilotspace/add` on npm, `pilotspace-add` on PyPI).
To serve all three, a few artifacts are mirrored across trees — but **every mirror is
either *generated* or *guarded by a parity test***, so none can silently drift. Read
this before editing, so you change the canonical copy and let the rest follow.

## The trees

| Tree | Role | Canonical? | Kept honest by |
|---|---|---|---|
| `add-method/` — `skill/add/`, `tooling/add.py` (+ `templates/`), `docs/` | **The package source** | ✅ **edit here** | — |
| `add-method/src/add_method/_bundled/` | What ships inside the Python wheel | ❌ generated | `scripts/prepare_bundle.py` → `test_bundle_parity` |
| `.claude/skills/add/` | Dogfood skill (this repo runs `/add` on itself) | ❌ mirror of `add-method/skill/add/` | `test_tree_parity` (byte) |
| `.add/tooling/add.py` | Dogfood engine | ❌ mirror of `add-method/tooling/add.py` | `test_shared_engine_pin` (md5) |
| `.add/state.json`, `PROJECT.md`, `CONVENTIONS.md`, `tasks/`, `milestones/`, `archive/` | The **live dogfood project** — real ADD data, not a copy | ✅ its own data | `add.py check` · `add.py audit` |
| `.add/docs/` | Local book materialization | n/a — **gitignored** | re-created by install / `add.py update` |
| root `./NN-*.md`, `appendix-*.md`, `*.png` | The GitHub-readable book (the README's table of contents links here) | ❌ mirror of `add-method/docs/` | `test_book_parity` (byte) |
| root `CHANGELOG.md`, `GETTING-STARTED.md` | **Pointers** to the package — deliberately *not* copies | ❌ pointer | — |

## The one rule

**Edit the canonical tree (`add-method/`), then propagate.** Never hand-edit a
generated tree (`_bundled/`) or one side of a mirror in isolation — a parity test will
fail in CI.

After changing anything under `add-method/skill/`, `add-method/tooling/add.py`, or
`add-method/docs/`:

```bash
# 1. regenerate the wheel bundle
python3 add-method/scripts/prepare_bundle.py

# 2. propagate to the dogfood + book mirrors (hand-copy; there is no sync script yet)
rm -rf .claude/skills/add && cp -R add-method/skill/add .claude/skills/add
cp add-method/tooling/add.py .add/tooling/add.py
# the book — every docs file EXCEPT README.md (the root README is its own document)
for f in add-method/docs/*; do [ "$(basename "$f")" = README.md ] || cp "$f" ./; done

# 3. verify nothing drifted
cd add-method && python3 -m unittest discover -s tooling -p 'test_*.py'
```

> The book parity guard (`test_book_parity`) excludes `README.md` on purpose: the root
> README is the repo/book landing page — a different document from
> `add-method/docs/README.md` (the docs index). The loop above honors that exclusion.

## Running the suite

CI (`.github/workflows/ci.yml`) runs the tooling tests, then audits the dogfood board:

```bash
cd add-method && python3 -m unittest discover -s tooling -p 'test_*.py'   # tooling tests
python3 .add/tooling/add.py audit                                          # recorded human gates
```

Most parity tests are byte/md5 comparisons that finish in milliseconds. A few tests —
`test_installer_handoff`, `test_v8_install`, and `test_shared_engine_pin`'s guard
runner — shell out to `node` / `npx` / `pip`, so they need those tools (and network)
installed and will fail in a bare sandbox without them.

## Releasing

One version tag publishes both registries; the full recipe is in
[`RELEASING.md`](./RELEASING.md). Because the root `CHANGELOG.md` and
`GETTING-STARTED.md` are pointers, a release edits only `add-method/CHANGELOG.md`.
