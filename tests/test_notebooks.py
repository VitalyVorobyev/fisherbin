from __future__ import annotations

import os
from pathlib import Path

import nbformat
import pytest
from nbclient import NotebookClient

# The kernel subprocess inherits a copy of this process's environment at
# launch time (jupyter_client's provisioner does `os.environ.copy()`), so
# setting these here -- rather than relying on the ambient shell -- makes
# every notebook run deterministically small and headless regardless of how
# pytest itself was invoked.
os.environ.setdefault("MPLBACKEND", "Agg")

REPO_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = sorted((REPO_ROOT / "examples" / "notebooks").glob("*.ipynb"))
NOTEBOOK_TIMEOUT_SECONDS = 180

if not NOTEBOOKS:
    raise RuntimeError(f"no notebooks discovered under {REPO_ROOT / 'examples' / 'notebooks'}")


@pytest.mark.parametrize("path", NOTEBOOKS, ids=lambda path: path.stem)
def test_notebook_is_an_instructive_workflow(path: Path) -> None:
    notebook = nbformat.read(path, as_version=4)
    markdown = [cell for cell in notebook.cells if cell.cell_type == "markdown"]
    code = [cell for cell in notebook.cells if cell.cell_type == "code"]
    source = "\n".join(cell.source for cell in notebook.cells)

    assert len(markdown) >= 4
    assert len(code) >= 4
    assert "run_experiment" not in source
    assert "##" in source


@pytest.mark.parametrize("path", NOTEBOOKS, ids=lambda path: path.stem)
def test_notebook_executes(path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Execute every notebook end to end in fast mode, headless, with a timeout.

    `NotebookClient.execute` raises `CellExecutionError` (a subclass of
    `Exception`) on the first cell that errors, which fails this test.
    """
    monkeypatch.setenv("SCOREQUANT_EXAMPLE_FAST", "1")
    monkeypatch.setenv("MPLBACKEND", "Agg")
    notebook = nbformat.read(path, as_version=4)
    client = NotebookClient(
        notebook,
        timeout=NOTEBOOK_TIMEOUT_SECONDS,
        kernel_name="python3",
        resources={"metadata": {"path": str(REPO_ROOT)}},
    )
    client.execute()
