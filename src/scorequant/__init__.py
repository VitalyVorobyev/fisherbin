"""Information-preserving hard quantization for statistical inference."""

from .api import fit_quantizer, optimize_partition
from .certify import CertificationConfig, certify_partition
from .components import (
    LinearComponents,
    LinearProblem,
    mixture_scores_from_posteriors,
    scores_from_components,
)
from .config import (
    DExchangeConfig,
    KMeansConfig,
    MahalanobisLloydConfig,
    ScalarDPConfig,
    SoftVoronoiConfig,
)
from .criteria import DOptimality, NormalizedTrace, ProfiledDOptimality
from .information import (
    binned_fisher_information,
    efficient_score_bound,
    efficient_scores,
    fisher_information,
    fractional_fisher_information,
    information_report,
    profiled_information_report,
)
from .partition import exchange_stability_report
from .providers import (
    CentralLogRatioTransform,
    ClassifierScore,
    LinearComponentScore,
    MixturePosteriorTransform,
    ScoreFunction,
)
from .result import (
    EfficientScoreBound,
    GeometryReport,
    InformationReport,
    OptimizationTrace,
    PartitionCertificate,
    PartitionResult,
    ProfiledGeometryReport,
    ProfiledInformationReport,
    QuantizerResult,
    StabilityReport,
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
    "CertificationConfig",
    "ClassifierScore",
    "DExchangeConfig",
    "DOptimality",
    "EfficientScoreBound",
    "FisherTransform",
    "GaussLegendreConfig",
    "GeometryReport",
    "InformationReport",
    "IntegrationSource",
    "KMeansConfig",
    "LinearComponentScore",
    "LinearComponents",
    "LinearProblem",
    "MahalanobisLloydConfig",
    "MixturePosteriorTransform",
    "NormalizedTrace",
    "ObservationSample",
    "OptimizationTrace",
    "PartitionCertificate",
    "PartitionResult",
    "ProfiledDOptimality",
    "ProfiledGeometryReport",
    "ProfiledInformationReport",
    "QuantizerResult",
    "ScalarDPConfig",
    "ScoreFunction",
    "ScoreProvenance",
    "ScoreSample",
    "SoftVoronoiConfig",
    "StabilityReport",
    "binned_fisher_information",
    "certify_partition",
    "efficient_score_bound",
    "efficient_scores",
    "exchange_stability_report",
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
