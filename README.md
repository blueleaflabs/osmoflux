# OsmoFlux

OsmoFlux studies reverse electrodialysis (RED) as a joint brine-treatment and electricity-generation problem. The current computational study holds membrane and dilute-water resources fixed when comparing designs, then evaluates electrical control, staging, flow routing, uncertainty, and modeled cost.

## Reproduce the current study

Open [`OsmoFlux_reproducibility.ipynb`](OsmoFlux_reproducibility.ipynb) with the **blueleaflabs** Python kernel, save it, and execute the code cell marked `launcher` (`RUN FINAL SUBMISSION PACKAGE`) for a fresh main run. The later cells are separately labeled add-ons and benchmark diagnostics; the notebook’s final cell is not the main-run launcher. The run is checkpointed. Parallel phases request 12 worker processes; historical timings still make a multi-day full rerun possible. If interrupted, execute the same cell again without changing the notebook or its configuration.

The notebook embeds the source code for the experiment and its analysis. Its current main configuration writes under `runs_dev/REPRODUCIBILITY_E2E/final_submission_20261004_02/`; choose a new output parent for an independent fresh replication rather than writing into the frozen completed record. The pipeline covers the fixed-resource study, commercial-format module study, 90%-power robustness, Morris sensitivity, fouling, published-stack diagnostics, Monte Carlo techno-economic analysis with a fixed-membrane, fixed-dilute break-even frontier, matched configuration comparisons, and a fresh 31-role result index with figures. Read `PIPELINE_STATUS.json`, `master/LIVE_STATUS.json` (measured throughput and approximate ETA), and `ANALYSIS/OUTPUT_MANIFEST.json` before using results. Numerical-review flags in those files must be evaluated and disclosed alongside quantitative claims.

The notebook's source archive preserves 29 earlier notebooks for provenance. The 31-role current-paper run does not regenerate superseded E0/XP and other historical-only studies. Earlier exploratory runs are stored under `archive/` and are not counted as fresh results by the current pipeline. The final-submission computation completed in `final_submission_20261004_02`; `PIPELINE_STATUS.json` records `COMPUTATION_COMPLETE_NUMERICAL_REVIEW_REQUIRED`. Its saved results, the targeted economic add-on, and the historical 40-section screen underpin manuscript v23. Optional Hulme diagnostics were launched separately from labeled notebook cells. Read the recorded numerical-review flags and manuscript limitations before using these outputs as predictions.

## Scope

These are model predictions, not plant validation. The transport model is NaCl-equivalent and does not resolve multi-ion chemistry or site-specific fouling kinetics. Published-stack comparisons are diagnostics; they do not establish a calibrated prediction of absolute plant power. Report the assumptions and numerical-review status alongside any result.

## Repository files

- `OsmoFlux_reproducibility.ipynb`: single entry point and embedded source archive.
- `requirements.txt`: Python package requirements; the run records actual package versions in `ENVIRONMENT.json`.
- `archive/`: preserved earlier notebooks, run directories, and documents; ignored by Git.
- `runs_dev/`: created by the notebook for new outputs; ignored by Git.

The [MIT license](LICENSE) applies to the code.
