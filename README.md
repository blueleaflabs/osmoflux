# OsmoFlux

OsmoFlux studies reverse electrodialysis (RED) as a joint brine-treatment and electricity-generation problem. The current computational study holds membrane and dilute-water resources fixed when comparing designs, then evaluates electrical control, staging, flow routing, uncertainty, and modeled cost.

## Reproduce manuscript v26 figures and tables

Open `OsmoFlux_analysis.ipynb`, select **Python (blueleaflabs)**, then **Restart Kernel and Run All Cells**. This is the current paper-analysis entry point. It regenerates all ten main figures, both supplementary figures, numerical evidence tables, and an analysis-integrity report from saved data; it does not rerun the simulations. Earlier analysis is retained under the local `archive/notebook_backups/` directory.

Run from the project folder or a subfolder. All paths are relative to the discovered project root; `OSMOFLUX_ROOT` can specify a different checkout. The configuration cell selects `final_submission_20261004_02` under `runs/REPRO/` and its companion `benchmark_observations/` subfolder. Both directories are local data, excluded from Git. The analysis requires the recorded input files; a Git clone alone does not include them. No pre-existing figures, `archive/analysis/` exports, temporary scripts, or original Hulme workbook are required.

Outputs go to `runs/REPRO/<RUN_ID>/derived_analysis/`, derived from the same `RUN_ID` that selects the source data. Missing output folders are created by the notebook. The existing uppercase `ANALYSIS/` contains original run results and must be retained. Only `derived_analysis/` is writable; it is excluded from source-input hashing. Original simulation files remain read-only. After updating the notebook, restart the kernel before running all cells. `COVERAGE.json` maps the manuscript figures and tables to outputs. `VERIFICATION.json` records analysis completion and whether the optional v26 regression test was run; `INPUT_MANIFEST.json` records relative input paths and SHA-256 hashes; `OUTPUT_MANIFEST.json` records output hashes. Run data supplies all plotted values and result annotations. Historical authored paper tables and manuscript-value comparisons are optional regression-test material, disabled by default. Enable `RUN_V26_REGRESSION` in the configuration cell (or `OSMOFLUX_V26_REGRESSION=1`) to compare against v26. Test expectations never supply plotted values. The gallery displays the regenerated figures in manuscript order. The former project-level `analysis/v26/` output folder is no longer used; it can be deleted independently of the saved run data.

`requirements-analysis.lock.txt` records the tested Python 3.11 analysis/kernel dependencies. To recreate the environment, install those requirements and register its Jupyter kernel as `blueleaflabs`. The notebook's original source run is read-only. `analysis/`, backup files under `archive/`, and the planned local `zenodo/` upload folder are ignored by Git. These analysis manifests are not a selected Zenodo release: the release identity and full-run package will be agreed separately before publication.

## Rerun the simulations


Open [`OsmoFlux_reproducibility.ipynb`](OsmoFlux_reproducibility.ipynb) with the **blueleaflabs** Python kernel, save it, and execute the code cell marked `launcher` (`RUN FINAL SUBMISSION PACKAGE`) for a fresh main run. The later cells are separately labeled add-ons and benchmark diagnostics; the notebook’s final cell is not the main-run launcher. The run is checkpointed. Parallel phases request 12 worker processes; historical timings still make a multi-day full rerun possible. If interrupted, execute the same cell again without changing the notebook or its configuration.

The notebook embeds the source code for the experiment and its analysis. The completed record now resides at `runs/REPRO/final_submission_20261004_02/`. The simulation notebook retains its historical development output configuration; select a new run ID/output parent under `runs_dev/` before launching an independent fresh replication. Historical paths inside saved receipts are provenance and remain unchanged. The pipeline covers the fixed-resource study, commercial-format module study, 90%-power robustness, Morris sensitivity, fouling, published-stack diagnostics, Monte Carlo techno-economic analysis with a fixed-membrane, fixed-dilute break-even frontier, matched configuration comparisons, and a fresh 31-role result index with figures. Read `PIPELINE_STATUS.json`, `master/LIVE_STATUS.json` (measured throughput and approximate ETA), and `ANALYSIS/OUTPUT_MANIFEST.json` before using results. Numerical-review flags in those files must be evaluated and disclosed alongside quantitative claims.

The notebook's source archive preserves 29 earlier notebooks for provenance. The 31-role current-paper run does not regenerate superseded E0/XP and other historical-only studies. Earlier exploratory runs are stored under `archive/` and are not counted as fresh results by the current pipeline. The final-submission computation completed in `final_submission_20261004_02`; `PIPELINE_STATUS.json` records `COMPUTATION_COMPLETE_NUMERICAL_REVIEW_REQUIRED`. Its saved results, the targeted economic add-on, and the historical 40-section screen underpin the current manuscript; the v26 analysis notebook rebuilds its reporting from the saved outputs. Optional Hulme diagnostics were launched separately from labeled notebook cells. Read the recorded numerical-review flags and manuscript limitations before using these outputs as predictions.

## Scope

These are model predictions, not plant validation. The transport model is NaCl-equivalent and does not resolve multi-ion chemistry or site-specific fouling kinetics. Published-stack comparisons are diagnostics; they do not establish a calibrated prediction of absolute plant power. Report the assumptions and numerical-review status alongside any result.

## Repository files

- `OsmoFlux_analysis.ipynb`: current v26 figures, tables, checks, and input/output provenance.
- `requirements-analysis.lock.txt`: exact tested analysis and notebook-kernel dependencies.
- `OsmoFlux_reproducibility.ipynb`: simulation launcher and embedded source archive.
- `requirements.txt`: Python package requirements; the run records actual package versions in `ENVIRONMENT.json`.
- `archive/`: preserved earlier notebooks, run directories, and documents; ignored by Git.
- `runs/REPRO/`: completed July 6 and current submission records; ignored by Git.
- `runs_dev/`: development and exploratory outputs; ignored by Git.

The [MIT license](LICENSE) applies to the code.

## Prepare a manual Zenodo release

`build_zenodo.py` is a standalone Python 3.11 script using only the standard library.
It never uploads, commits, pushes, freezes a manifest, or modifies source data. The
analysis notebook remains the analysis entry point; packaging is an explicit step.
The script, `test_build_zenodo.py`, and `zenodo-release-v26.json` are intended for Git. Proposals stay under the
ignored `archive/zenodo_review/`; final upload files go under ignored `zenodo/`.

### 1. Propose an inventory

From the project folder, after completing the analysis:

```sh
python build_zenodo.py propose \
  --run-id final_submission_20261004_02 \
  --config zenodo-release-v26.json \
  --out archive/zenodo_review/proposal-02
```

Use a new proposal directory each time. Read `REVIEW.md`. `proposal-01` was an
initial schema-1 draft and is superseded by this configuration-driven workflow;
do not approve or build it.

`zenodo-release-v26.json` declares the code files, document paths, ordered figure
filenames for each document, notebook names, requirements file and Python version.
Figure counts come from those lists; document roles are not guessed from filenames.
The configuration itself is automatically included in the code archive and its
content and hash are recorded in the manifest. Changing it after approval blocks
the build. A future paper version gets its own configuration; no packaging-code
change is needed. The run ID remains an explicit argument, and the Git commit and
file hashes are discovered rather than written into the configuration.
 The manifest includes
all files in this selected run, including original uppercase `ANALYSIS/`, frozen
launcher source, and `benchmark_observations/`. Generated `derived_analysis/`
files form a separate archive group. Other runs, `_grid_cache`, OS/cache files,
and the reserved `runs/REPRO/<RUN_ID>/release/` approval directory are excluded.
The inventory checks the analysis input/output hashes and executed notebook code.
It also checks that the manuscript and supplement embed the exact generated PNGs.

### 2. Agree on and save the release identity

Before approving a manifest, synchronize the paper images, finalize and commit the
intended code changes, then generate a fresh proposal from a clean checkout. The
script records the local Git commit and origin; confirming that commit is pushed
to GitHub remains a separate release step. A dirty-checkout proposal is useful for
review but is deliberately blocked from building a final package.

After review, explicitly copy the approved proposed manifest into
`runs/REPRO/<RUN_ID>/release/release-manifest.json` and save its SHA-256 alongside
it. Copy it unchanged: editing any byte changes its fingerprint. The script has
no implicit "latest run" selection and no automatic approval step.

### 3. Verify and build from the approved manifest

Use the saved manifest path and its exact SHA-256 with these commands (replace
`APPROVED_SHA256` with the agreed fingerprint):

```sh
python build_zenodo.py verify \
  --manifest runs/REPRO/final_submission_20261004_02/release/release-manifest.json \
  --manifest-sha256 APPROVED_SHA256
python build_zenodo.py build \
  --manifest runs/REPRO/final_submission_20261004_02/release/release-manifest.json \
  --manifest-sha256 APPROVED_SHA256
```

A build rejects changed, missing, or newly added source files, a changed Git
checkout, and an existing nonempty upload directory. It rechecks each file while
archiving. `zenodo/` receives only seven upload files: `code.zip`, `run-data.zip`,
`analysis.zip`, `paper.zip`, `README.md`, `release-manifest.json`, and
`SHA256SUMS.txt`. All archives share the same `osmoflux/` extraction root.
Archives use sorted entries, fixed metadata, and no compression so identical
inputs produce identical bytes without depending on compression-library versions.
Allow at least the total source size again as free disk space when building.

Upload those seven files manually to Zenodo. The DOI is handled separately after
reservation/publication. Changing the paper later requires a new proposed release
manifest and package; never edit files inside an already approved package.

Run the packaging checks with `python -m unittest test_build_zenodo.py`.
These tests use small temporary fixtures, not the real run.
