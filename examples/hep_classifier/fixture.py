"""Build the committed FAIR Universe HiggsML fixture.

This script is **not** run by the example, the tests, or CI. It is the recorded
procedure that produced ``examples/data/hep_higgsml_fixture.npz``, kept in the
repository so the fixture can be rebuilt and audited rather than taken on trust.

It needs the network and two packages the project does not depend on, so run it
in a throwaway environment::

    uv run --with pandas --with pyarrow --with numpy \
        python -m examples.hep_classifier.fixture

Why the tau-energy-scale variants are precomputed here instead of at run time
-----------------------------------------------------------------------------
``tes`` is not a factor on one column. Upstream ``mom4_manipulate`` scales
``PRI_had_pt``, recoils the missing transverse momentum against the rescaled tau
four-vector, and then ``DER_data`` recomputes every derived quantity from the
shifted primaries -- ten of the twenty-eight feature columns move. Reproducing
that here would mean copying the four-vector algebra out of a repository that
carries no licence file, and its correctness could only be checked against the
upstream output this script can simply use. So the transformation is applied
*by upstream's own code*, fetched at a pinned commit and never vendored, and
what the repository commits is the resulting arrays.

``dopostprocess=False`` is deliberate. Upstream re-applies the ``PRI_had_pt > 26``
selection after the shift, which drops 169 of 1,000 rows at ``tes = 0.90``. That
is an acceptance change, and it would leave the variants unaligned and the
density ratio singular at the threshold. Holding the selection fixed makes the
example a measurement of the *shape* sensitivity to the tau energy scale, which
is what it claims to be.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import types
import urllib.request
from pathlib import Path

import numpy as np

#: Upstream commit the fixture was built from. Pinned so a rebuild is comparable.
UPSTREAM_COMMIT = "31816a0d8c8dda03d4b28d9e824674821756962b"
UPSTREAM_REPO = "https://github.com/FAIR-Universe/HEP-Challenge"
RAW_BASE = f"https://raw.githubusercontent.com/FAIR-Universe/HEP-Challenge/{UPSTREAM_COMMIT}"
SAMPLE_PATH = "input_data/FAIR_Universe_HiggsML_data.parquet"

#: The dataset's archival record. The code repository above ships the sample but
#: carries no licence file of its own, so the licence claim rests on this record.
ZENODO_DOI = "10.5281/zenodo.15131565"
ZENODO_URL = "https://doi.org/10.5281/zenodo.15131565"
SOURCE_LICENSE = "CC-BY-4.0"
LICENSE_URL = "https://creativecommons.org/licenses/by/4.0/"

#: Tau-energy-scale points. The headline score uses delta = 0.05; 0.025 and 0.10
#: give the convergence study that keeps a single finite-difference number honest.
TES_POINTS = (0.90, 0.95, 0.975, 1.00, 1.025, 1.05, 1.10)

OUTPUT = Path("examples/data/hep_higgsml_fixture.npz")
PROVENANCE = Path("examples/data/hep_higgsml_fixture.json")


def _fetch(path: str) -> bytes:
    with urllib.request.urlopen(f"{RAW_BASE}/{path}", timeout=120) as response:
        return bytes(response.read())


def _load_upstream_module(name: str, sources: dict[str, bytes]) -> types.ModuleType:
    """Execute an upstream module from memory without writing it into the tree."""
    module = types.ModuleType(name)
    module.__file__ = f"<upstream {name}.py @ {UPSTREAM_COMMIT[:12]}>"
    sys.modules[name] = module
    exec(compile(sources[name], module.__file__, "exec"), module.__dict__)
    return module


def build() -> None:
    """Fetch the upstream sample, apply every tes variant, and write the fixture."""
    import pandas as pd

    sources = {
        "derived_quantities": _fetch("ingestion_program/derived_quantities.py"),
        "systematics": _fetch("ingestion_program/systematics.py"),
    }
    _load_upstream_module("derived_quantities", sources)
    systematics = _load_upstream_module("systematics", sources)

    raw = _fetch(SAMPLE_PATH)
    sample_sha256 = hashlib.sha256(raw).hexdigest()
    frame = pd.read_parquet(__import__("io").BytesIO(raw))

    features = [name for name in frame.columns if name.startswith(("PRI_", "DER_"))]
    weights = frame["weights"].to_numpy(dtype=np.float64)
    if not np.all(np.isfinite(weights)) or not np.any(weights > 0) or np.any(weights < 0):
        raise ValueError("weights must be finite and nonnegative with at least one positive")

    variants: dict[str, np.ndarray] = {}
    for tes in TES_POINTS:
        result = systematics.systematics(data_set=frame.copy(), tes=tes, dopostprocess=False)
        shifted = result["data"] if isinstance(result, dict) else result
        shifted = shifted.reset_index(drop=True)
        if len(shifted) != len(frame):
            raise ValueError(f"tes={tes} changed the row count; the variants must stay aligned")
        variants[f"features_tes_{tes:.4f}"] = shifted[features].to_numpy(dtype=np.float64)

    detailed = frame["detailed_labels"].to_numpy(dtype=str)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        OUTPUT,
        weights=weights,
        labels=frame["labels"].to_numpy(dtype=np.int64),
        detailed_labels=detailed,
        feature_names=np.array(features, dtype=object),
        tes_points=np.array(TES_POINTS, dtype=np.float64),
        **variants,
    )

    responsive = [
        name
        for index, name in enumerate(features)
        if not np.allclose(
            variants[f"features_tes_{TES_POINTS[0]:.4f}"][:, index],
            variants[f"features_tes_{TES_POINTS[-1]:.4f}"][:, index],
            rtol=1e-9,
            atol=1e-9,
        )
    ]
    PROVENANCE.write_text(
        json.dumps(
            {
                "title": "FAIR Universe HiggsML deterministic ScoreQuant fixture",
                "dataset": "FAIR Universe - HiggsML Uncertainty Challenge Public Dataset",
                "source_license": SOURCE_LICENSE,
                "license_url": LICENSE_URL,
                "license_record_doi": ZENODO_DOI,
                "license_record_url": ZENODO_URL,
                "bytes_fetched_from": f"{UPSTREAM_REPO}/blob/{UPSTREAM_COMMIT}/{SAMPLE_PATH}",
                "provenance_caveat": (
                    "The bytes were fetched from the challenge's code repository, which carries "
                    "no licence file. The sample is a subset of the public dataset archived at "
                    f"DOI {ZENODO_DOI}, and the {SOURCE_LICENSE} claim is made under that record, "
                    "not under the code repository."
                ),
                "upstream_commit": UPSTREAM_COMMIT,
                "upstream_sample_sha256": sample_sha256,
                "systematics_applied_by": (
                    "upstream ingestion_program/systematics.py and derived_quantities.py at the "
                    "pinned commit, executed from memory; neither file is vendored"
                ),
                "dopostprocess": False,
                "dopostprocess_note": (
                    "Upstream re-applies PRI_had_pt > 26 after the shift, which drops 169 of "
                    "1000 rows at tes=0.90. Holding the selection fixed keeps the variants "
                    "row-aligned and makes this a shape measurement, not an acceptance one."
                ),
                "tes_points": list(TES_POINTS),
                "n_events": int(len(frame)),
                "feature_names": features,
                "tes_responsive_features": responsive,
                "weight_sum": float(weights.sum()),
                "composition": {
                    str(name): int(count)
                    for name, count in zip(*np.unique(detailed, return_counts=True), strict=True)
                },
            },
            indent=2,
        )
        + "\n"
    )
    print(f"wrote {OUTPUT} ({OUTPUT.stat().st_size / 1e6:.2f} MB)")
    print(f"wrote {PROVENANCE}")
    print(f"{len(responsive)} of {len(features)} features respond to tes: {responsive}")


if __name__ == "__main__":
    if importlib.util.find_spec("pandas") is None:
        raise SystemExit("run under: uv run --with pandas --with pyarrow --with numpy")
    build()
