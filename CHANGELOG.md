# Changelog

All notable changes to the ADD method — the book, the skill, and the published
packages — are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html). One version tag publishes
both distribution channels: `@pilotspace/add` (npm) and `pilotspace-add` (PyPI).

## [Unreleased]

_Nothing yet._

## [1.0.0] — 2026-06-02

First public release of ADD (AI-Driven Development) as an installable skill plus the
complete AIDD book as its trust layer.

### Added

- **The method, shippable.** `npx @pilotspace/add init` (npm) and `pilotspace-add init`
  (PyPI) drop the `add` skill into `.claude/skills/add/`, the state-tracked tooling
  into `.add/tooling/`, and the full book into `.add/docs/` — without ever clobbering
  existing project state.
- **Co-specification.** The Specify phase is now AI + human drafting the spec together
  and validating it by surfacing assumptions ranked **least-sure first** (⚠) — replacing
  the old flat pre-ticked assumption list. The frozen contract is the single approval gate.
- **The one-approval front.** Spec + Scenarios + Contract + Tests are drafted as one
  bundle; the human gives one approval at the frozen contract; build→verify then runs
  self-driving, with security findings always stopping back to the human.
- **State on disk, not in chat.** `add.py status` resumes any session at its exact
  phase — no context rot across sessions.
- **The AIDD book** (`docs/`): Foundations, the six steps in depth, operating it across
  a team, and copy-paste reference appendices (templates, prompts, glossary, a fully
  worked money-transfer example, checklists, and the requirements matrix).
- **Dual-ecosystem packaging.** npm package `@pilotspace/add` and PyPI package
  `pilotspace-add`, both at 1.0.0, built from one byte-identical bundled tree guarded by
  parity tests.
- **Autonomous release CI** (`.github/workflows/publish.yml`): a version tag runs the
  full test suite, asserts the tag matches both manifests, then publishes to npm
  (with provenance) and PyPI (via OIDC trusted publishing). A companion `ci.yml` runs
  the suite on every push and PR.

### Release channels

- **npm** — `@pilotspace/add@1.0.0` is published and installable.
- **PyPI** — `pilotspace-add` 1.0.0 publishes on the first version tag once the trusted
  publisher is configured (see `.github/workflows/publish.yml`).

[Unreleased]: https://github.com/pilotspace/ADD/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/pilotspace/ADD/releases/tag/v1.0.0
