# Model reasoning and local compute

## Measure the stage that actually dominates

Separate wall time into reasoning/tool-wait, source preparation, engine startup/transpilation, simulation, and result parsing. Record a small representative sample, not just the fastest match. Initialization can dominate short runs; long or stuck games can dominate tail latency.

- Hosted model inference is remote. Local CPU load from Node/Python does not measure the model's reasoning quality.
- Local simulation usually benefits from CPU throughput and enough RAM for independent processes. Logical CPU count is a ceiling hint, not a benchmark; hyperthreads, thermal throttling, competing processes, and engine behavior matter.
- GPU matters only if the actual simulation or locally hosted model uses it. Do not prescribe a GPU upgrade for a CPU-only JavaScript interpreter.
- If the engine is inaccurate or the result parser is wrong, fix that before increasing workers.

## Calibrate without launching a full league

1. Run a representative match using the real engine and full-length termination. Record runtime, observed peak memory and exit/result status. Include a difficult long game if the workload has one.
2. Start with a small worker count that leaves interactive headroom. Verify that parallel results match serial results for the same inputs and that processes do not share mutable output/state.
3. Increase only when the measured wall time improves without paging, result changes or resource exhaustion. Report measured speedup, not an assumed linear ratio.

Use the engine's isolation requirements. In the historical CodeCombat Node harness, repeated matches in one process contaminated interpreter state, so a fresh process per match was required. This is a fact about that harness, not a universal rule for every simulator.

For memory budgeting, reserve RAM for the OS and foreground work. Sum all process-tree memory when each worker launches children. A missing memory measurement is not zero and does not support a confident parallelism recommendation.

The bundled probe reports hardware inventory and, when supplied measured per-match time/memory, a conservative suggestion. Run `resource_probe.py --help` for its options. Output distinguishes an estimate from observation. A known memory shortfall means reduce the workload or free resources, not force one worker anyway.

Approximate scheduling only after calibration:

`ideal batch time ≈ ceil(matches / workers) × representative match time`

This is a planning estimate. Startup overhead, variability, parsing, contention and retries can make actual time longer. Avoid expanding workers simply because there are many independent matches.

## Parallel reasoning is a different budget

Assign agents independent work: inspect rules, investigate a specific loss, or review a candidate's invariants. More agents are not automatically more useful, and agent count is not the simulation worker count. Preserve the user's chosen model unless they request a change.

Model output must state an actionable hypothesis and what would refute it. A variant that only improves a hand-picked training opponent is not a validated improvement. Keep a small holdout set and account for repeated tuning.

## Reduce work before buying throughput

- Cache still-valid baseline results keyed by actual input/runtime identity.
- Reject a candidate at the first required gate failure; record other cases as `NOT_RUN`, not failures or wins.
- Run full acceptance only for viable candidates.
- Use approximate simulators for screening, never for silently replacing the final oracle.
- Preserve completed results when interrupted, and resume only missing work after checking input identity.
- Cap retries, candidate count, total matches, per-match timeout and output size. Stop new scheduling on cancellation; terminate only the child processes belonging to this run.
