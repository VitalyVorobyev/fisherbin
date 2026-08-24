"""Information-preserving binning for statistical inference."""

from .api import fit, fit_components, fit_scores
from .components import LinearComponents, LinearProblem, scores_from_components
from .config import KMeansConfig, SoftVoronoiConfig
from .information import (
    binned_fisher_information,
    fisher_information,
    fractional_fisher_information,
    information_report,
)
from .result import (
    ComponentFitResult,
    FitResult,
    InformationReport,
    ModelFitResult,
    OptimizationTrace,
)
from .transforms import FisherTransform
from .visualization import plot_information, plot_optimization, plot_partition, plot_summary

__all__ = [
    "FisherTransform",
    "ComponentFitResult",
    "FitResult",
    "InformationReport",
    "KMeansConfig",
    "LinearComponents",
    "LinearProblem",
    "ModelFitResult",
    "OptimizationTrace",
    "SoftVoronoiConfig",
    "binned_fisher_information",
    "fisher_information",
    "fit",
    "fit_components",
    "fit_scores",
    "fractional_fisher_information",
    "information_report",
    "plot_information",
    "plot_optimization",
    "plot_partition",
    "plot_summary",
    "scores_from_components",
]
