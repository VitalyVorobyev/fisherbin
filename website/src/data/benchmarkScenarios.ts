/**
 * Hand-maintained prose for each `benchmarks/bench.py` scenario and quality label.
 *
 * Every `task`/`stop` pair here is verified against the corresponding `_bench_*`
 * function in `benchmarks/bench.py`: the config it constructs, the criterion it
 * passes, and the stopping rule that config's own docstring records. A scenario
 * or label absent from `benchmarks/baselines.json` has no entry here.
 */
export const benchmarkScenarios: Record<string, {task: string; stop: string}> = {
  certify: {task: "Branch-and-bound global D certificate", stop: "optimal or node budget"},
  compile: {task: "Compile a stable D partition into a rule", stop: "n/a"},
  d_exchange: {task: "Fixed-sample D partition, exact exchange", stop: "exchange-stable or max_scans"},
  d_exchange_nobatch: {task: "Same, one relocation per scan", stop: "exchange-stable or max_scans"},
  kmeans: {task: "Weighted k-means in whitened score space (trace)", stop: "relative objective-change tolerance"},
  lloyd: {task: "Mahalanobis-Lloyd D partition with exact guard", stop: "no improving batch, then exchange-stable"},
  predict: {task: "Label held-out scores with a fitted k-means quantizer", stop: "n/a"},
  profiled_exchange: {task: "Profiled D_s partition, exact exchange", stop: "exchange-stable or max_scans"},
  scalar_dp: {task: "Exact interval solution, rank-one score", stop: "exact"},
  soft: {task: "Soft Voronoi D rule, hardened", stop: "annealing schedule end"},
};

export const qualityLabels: Record<string, string> = {
  certified_logdet_objective: "certified log det I_q",
  geometric_mean_retention: "D-efficiency (train)",
  held_out_geometric_mean_retention: "D-efficiency (held out)",
  logdet_objective: "log det I_q",
  profiled_logdet_objective: "profiled log det",
};
