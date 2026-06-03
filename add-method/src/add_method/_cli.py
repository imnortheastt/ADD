"""Console-script entry point: pilotspace-add.

Mirrors bin/cli.js command structure:
    pilotspace-add init [targetDir] [--force] [--stage STAGE] [--name NAME]
    pilotspace-add help
"""
from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    """Entry point registered as the `pilotspace-add` console script."""
    raw = argv if argv is not None else sys.argv[1:]

    # Pull off the subcommand (default: init), matching cli.js behaviour.
    if raw and not raw[0].startswith("-"):
        cmd, rest = raw[0], raw[1:]
    else:
        cmd, rest = "init", raw

    if cmd in ("help", "--help", "-h"):
        print("usage: pilotspace-add init [targetDir] [--force] [--stage STAGE] [--name NAME]")
        return 0

    if cmd != "init":
        print(f"pilotspace-add: error: unknown command '{cmd}'. Try: pilotspace-add init",
              file=sys.stderr)
        return 1

    parser = argparse.ArgumentParser(
        prog="pilotspace-add",
        description="Install the ADD method into a target project.",
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="Target project directory (default: cwd)",
    )
    parser.add_argument("--force", action="store_true",
                        help="Overwrite existing skill tree and reset state.json")
    parser.add_argument("--stage", default="prototype",
                        choices=("prototype", "poc", "mvp", "production"),
                        help="Initial project stage (default: prototype)")
    parser.add_argument("--name", default=None,
                        help="Project name (default: target directory name)")

    args = parser.parse_args(rest)

    from add_method._installer import install
    return install(
        target=args.target,
        force=args.force,
        stage=args.stage,
        name=args.name,
    )


if __name__ == "__main__":
    sys.exit(main())
