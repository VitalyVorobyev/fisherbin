# Example data

`flowcyt_fixture.npz` contains a small deterministic subset of the public
[FlowCyt benchmark](https://github.com/VIPER-GENEVA/FlowCyt-Classification-Benchmark).
It is used only by the example and tests; it is not included in the FisherBin
Python package.

The FlowCyt data, and therefore this derived fixture, are licensed separately
from FisherBin under
[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
Copyright belongs to Lorenzo Bini, Fatemeh Nassajian Mojarrad, Margarita
Liarou, Thomas Matthes, and Stéphane Marchand-Maillet. See
`flowcyt_fixture.json` for provenance and sampling details.

The complete research workflow does not commit its 600,000-cell bounded sample.
It recreates `flowcyt-results/flowcyt_sample_20000.npz` with deterministic HTTP
range reads from all 180 upstream FCS files. The complete command, sample digest,
protocol, and resulting metrics are documented in the
[FlowCyt use case](../../docs/usecases/cellpopulation.md).
