from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
PACKAGE = ROOT / "src" / "scorequant"

# Installed as `sitecustomize` so it runs before the interpreter imports anything
# the package pulls in. A meta-path finder that raises is the only reliable way to
# simulate a runtime where JAX and Optax are genuinely absent.
_BLOCKER_SOURCE = """\
import importlib.abc
import sys


class BlockExecutionLibraries(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split(".", 1)[0] in {"jax", "optax"}:
            raise ModuleNotFoundError(fullname)
        return None


sys.meta_path.insert(0, BlockExecutionLibraries())
"""


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text())
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            modules.add(node.module)
    return modules


def _package_sources() -> list[Path]:
    # rglob, not glob: the shared numerical kernels live in the `solvers/` package,
    # which is exactly where a backend import would be most tempting to add.
    return sorted(path for path in PACKAGE.rglob("*.py") if "__pycache__" not in path.parts)


def _run_without_execution_libraries(tmp_path: Path, code: str) -> subprocess.CompletedProcess[str]:
    (tmp_path / "sitecustomize.py").write_text(_BLOCKER_SOURCE)
    environment = os.environ.copy()
    environment["PYTHONPATH"] = os.pathsep.join((str(tmp_path), str(ROOT / "src")))
    return subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )


def test_execution_libraries_stay_behind_adapter() -> None:
    offenders: list[str] = []
    for path in _package_sources():
        if path.name == "_execution.py":
            continue
        imports = _imports(path)
        if any(name == "jax" or name.startswith("jax.") or name == "optax" for name in imports):
            offenders.append(str(path.relative_to(PACKAGE)))
    assert offenders == []


def test_domain_contracts_do_not_import_solver_or_api_layers() -> None:
    domain_modules = ("config.py", "criteria.py", "reports.py", "sources.py")
    forbidden = {"api", "partition", "quantizers", "certify", "visualization"}
    offenders: dict[str, list[str]] = {}
    for name in domain_modules:
        reverse = sorted(_imports(PACKAGE / name) & forbidden)
        if reverse:
            offenders[name] = reverse
    assert offenders == {}


def test_frontend_concerns_never_enter_python_core() -> None:
    forbidden = {"pyodide", "marimo", "react", "docusaurus"}
    offenders: dict[str, list[str]] = {}
    for path in _package_sources():
        matched = sorted(_imports(path) & forbidden)
        if matched:
            offenders[str(path.relative_to(PACKAGE))] = matched
    assert offenders == {}


def test_execution_library_blocker_actually_blocks(tmp_path: Path) -> None:
    # Guards the test below. A blocker that silently fails to install would make
    # the JAX-free import claim pass vacuously on a machine that has JAX.
    completed = _run_without_execution_libraries(tmp_path, "import jax")
    assert completed.returncode != 0, "the blocker did not prevent `import jax`"
    assert "ModuleNotFoundError" in completed.stderr


def test_package_import_does_not_require_jax_or_optax(tmp_path: Path) -> None:
    completed = _run_without_execution_libraries(
        tmp_path,
        "import scorequant; print(scorequant.ExecutionConfig(backend='numpy'))",
    )
    assert completed.returncode == 0, completed.stderr
    assert "backend='numpy'" in completed.stdout
