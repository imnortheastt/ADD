"""Support `python -m add_method` as an alias for the `pilotspace-add` console script."""
import sys

from add_method._cli import main

if __name__ == "__main__":
    sys.exit(main())
