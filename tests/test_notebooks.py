from __future__ import annotations

from pathlib import Path

import nbformat
import pytest
from nbclient import NotebookClient

NOTEBOOKS = sorted((Path(__file__).parents[1] / "examples" / "notebooks").glob("*.ipynb"))


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
def test_notebook_executes(path: Path) -> None:
    notebook = nbformat.read(path, as_version=4)
    client = NotebookClient(
        notebook,
        timeout=180,
        kernel_name="python3",
        resources={"metadata": {"path": str(Path(__file__).parents[1])}},
    )
    client.execute()
