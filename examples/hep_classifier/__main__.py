"""Command-line entry point for the HEP classifier example.

Run with::

    JAX_ENABLE_X64=1 MPLBACKEND=Agg uv run python -m examples.hep_classifier
"""

from __future__ import annotations

from .experiment import main

if __name__ == "__main__":
    main()
