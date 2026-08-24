"""FlowCyt population-quantification example.

This package demonstrates how an application can estimate scores, learn a hard
partition, and consume the frozen labels in a downstream likelihood.  Its
FlowCyt-specific data loading, classifier calibration, likelihood, and reporting
stay outside :mod:`fisherbin`; reusable domain-independent abstractions may be
promoted to the library as they become clear.
"""

from .data import (
    CLASS_NAMES,
    FEATURE_NAMES,
    REFERENCE_PATIENTS,
    TEST_PATIENTS,
    FlowCytData,
    RobustArcsinhTransform,
    load_csv_directory,
    load_fixture,
)
from .likelihood import MixtureEstimate, fit_binned_mixture, fit_unbinned_mixture
from .scores import ScoreModel, fit_score_model, mixture_scores, reference_composition

__all__ = [
    "CLASS_NAMES",
    "FEATURE_NAMES",
    "REFERENCE_PATIENTS",
    "TEST_PATIENTS",
    "FlowCytData",
    "MixtureEstimate",
    "RobustArcsinhTransform",
    "ScoreModel",
    "fit_binned_mixture",
    "fit_score_model",
    "fit_unbinned_mixture",
    "load_csv_directory",
    "load_fixture",
    "mixture_scores",
    "reference_composition",
]
