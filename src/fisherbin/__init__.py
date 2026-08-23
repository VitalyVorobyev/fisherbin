"""Information-preserving binning for statistical inference."""

from .api import fit
from .components import scores_from_components
from .config import KMeansConfig, SoftVoronoiConfig
from .information import (
    binned_fisher_information,
    fisher_information,
    fractional_fisher_information,
    information_report,
)
from .result import FitResult, InformationReport, OptimizationTrace
from .transforms import FisherTransform
from .visualization import plot_information, plot_optimization, plot_partition, plot_summary

__all__ = [
    "FisherTransform",
    "FitResult",
    "InformationReport",
    "KMeansConfig",
    "OptimizationTrace",
    "SoftVoronoiConfig",
    "binned_fisher_information",
    "fisher_information",
    "fit",
    "fractional_fisher_information",
    "information_report",
    "plot_information",
    "plot_optimization",
    "plot_partition",
    "plot_summary",
    "scores_from_components",
]
