"""Information-preserving hard quantization for statistical inference."""

from .api import fit_quantizer, optimize_partition
from .components import (
    LinearComponents,
    LinearProblem,
    mixture_scores_from_posteriors,
    scores_from_components,
)
from .config import DExchangeConfig, KMeansConfig, ScalarDPConfig, SoftVoronoiConfig
from .criteria import DOptimality, NormalizedTrace, ProfiledDOptimality
from .information import (
    binned_fisher_information,
    efficient_scores,
    fisher_information,
    fractional_fisher_information,
    information_report,
    profiled_information_report,
)
from .providers import (
    CentralLogRatioTransform,
    ClassifierScore,
    LinearComponentScore,
    MixturePosteriorTransform,
    ScoreFunction,
)
from .result import (
    InformationReport,
    OptimizationTrace,
    PartitionResult,
    ProfiledGeometryReport,
    ProfiledInformationReport,
    QuantizerResult,
)
from .sources import (
    GaussLegendreConfig,
    IntegrationSource,
    ObservationSample,
    ScoreProvenance,
    ScoreSample,
)
from .transforms import FisherTransform
from .visualization import plot_information, plot_optimization, plot_partition, plot_summary

__all__ = [
    "CentralLogRatioTransform",
    "ClassifierScore",
    "DExchangeConfig",
    "DOptimality",
    "FisherTransform",
    "GaussLegendreConfig",
    "InformationReport",
    "IntegrationSource",
    "KMeansConfig",
    "LinearComponentScore",
    "LinearComponents",
    "LinearProblem",
    "MixturePosteriorTransform",
    "NormalizedTrace",
    "ObservationSample",
    "OptimizationTrace",
    "PartitionResult",
    "ProfiledDOptimality",
    "ProfiledGeometryReport",
    "ProfiledInformationReport",
    "QuantizerResult",
    "ScoreFunction",
    "ScoreProvenance",
    "ScoreSample",
    "ScalarDPConfig",
    "SoftVoronoiConfig",
    "binned_fisher_information",
    "efficient_scores",
    "fisher_information",
    "fit_quantizer",
    "fractional_fisher_information",
    "information_report",
    "mixture_scores_from_posteriors",
    "optimize_partition",
    "plot_information",
    "plot_optimization",
    "plot_partition",
    "plot_summary",
    "profiled_information_report",
    "scores_from_components",
]
