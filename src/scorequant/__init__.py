"""Information-preserving hard quantization for statistical inference."""

from .api import fit_quantizer, optimize_partition
from .artifact import Quantizer
from .certify import CertificationConfig, certify_partition
from .components import (
    LinearComponents,
    LinearProblem,
    scores_from_components,
)
from .config import (
    DExchangeConfig,
    ExecutionConfig,
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
    CentralLogRatioScore,
    DensityRatioScore,
    LinearComponentScore,
    ScoreFunction,
    ScoreProvider,
)
from .ratios import (
    IntensityParameterization,
    MixtureParameterization,
    mixture_scores_from_ratios,
    ratio_closure_report,
    ratios_from_posteriors,
)
from .reports import RatioClosureReport
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
    RatioProvenance,
    ScoreProvenance,
    ScoreSample,
    ScoreSchema,
)
from .transforms import FisherTransform
from .visualization import plot_information, plot_optimization, plot_partition, plot_summary

__all__ = [
    "CentralLogRatioScore",
    "CertificationConfig",
    "DExchangeConfig",
    "ExecutionConfig",
    "DOptimality",
    "DensityRatioScore",
    "EfficientScoreBound",
    "FisherTransform",
    "GaussLegendreConfig",
    "GeometryReport",
    "InformationReport",
    "IntegrationSource",
    "IntensityParameterization",
    "KMeansConfig",
    "LinearComponentScore",
    "LinearComponents",
    "LinearProblem",
    "MahalanobisLloydConfig",
    "MixtureParameterization",
    "NormalizedTrace",
    "ObservationSample",
    "OptimizationTrace",
    "PartitionCertificate",
    "PartitionResult",
    "ProfiledDOptimality",
    "ProfiledGeometryReport",
    "ProfiledInformationReport",
    "Quantizer",
    "QuantizerResult",
    "RatioClosureReport",
    "RatioProvenance",
    "ScalarDPConfig",
    "ScoreFunction",
    "ScoreProvenance",
    "ScoreProvider",
    "ScoreSample",
    "ScoreSchema",
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
    "mixture_scores_from_ratios",
    "optimize_partition",
    "plot_information",
    "plot_optimization",
    "plot_partition",
    "plot_summary",
    "profiled_information_report",
    "ratio_closure_report",
    "ratios_from_posteriors",
    "scores_from_components",
]
