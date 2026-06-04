# OsmoFlux

**A 1D axially-resolved Reverse Electrodialysis model for SWRO brine compliance and energy recovery.**

OsmoFlux evaluates cascade RED architectures against a two-outlet ambient-seawater discharge criterion — treating compliance as a hard architectural constraint, not an afterthought. The model screens thousands of configurations to identify which architectures can simultaneously satisfy both outlet constraints while maximising power density.

Built by Rohan Agarwal (Blue Leaf Labs) as an independent research project at Monta Vista High School, Cupertino, CA, through the IRPD program.  
ORCID: [0009-0005-7518-0805](https://orcid.org/0009-0005-7518-0805)

---

## Paper

> Agarwal, R. (2026). Fresh-Dilute Cascade Architecture for Compliance-Constrained Reverse Electrodialysis of SWRO Brine. *Manuscript submitted to Desalination (Elsevier).*

---

## Key results (Grand Sweep v12 — canonical run 20260531_183521)

**Three operating regimes at Carlsbad (C_H = 1.15 mol/L, β = 0):**

| Regime | Configuration | Power density | Compliance |
|--------|--------------|---------------|------------|
| 1 — Unconstrained optimum | N = 14, single-stage | 3.18 W/m² | 0% |
| 2 — Compliant single-stage | N = 154–160, single-stage | 1.04 W/m² | 100% |
| 3 — Cascade solution | N_total = 120, S = 8, 6.0 m² | **2.57 W/m²** | **100%** |

Fresh-dilute cascade occupies Regime 3 — a feasible region inaccessible to single-stage or serial architectures. At matched compliance-achieving membrane investment (15.0 m²), fresh-dilute delivers 1.589 W/m² versus serial's 0.535 W/m² — a **197% power density advantage**.

**Universal dominance:** Fresh-dilute outperformed serial cascading in all 1,728 matched cases (median advantage 86.6%, maximum 271.9%).

**Minimum compliance areas across five SWRO plant chemistries (fresh-dilute, β = 0):**

| Site | C_H (mol/L) | Min area | Power |
|------|-------------|----------|-------|
| Valley Water | 0.35 | 3.0 m² | 0.909 W/m² |
| Monterey | 0.75 | 3.0 m² | 2.023 W/m² |
| Carlsbad | 1.15 | 6.0 m² | 2.572 W/m² |
| Jebel Ali | 1.80 | 12.0 m² | 3.097 W/m² |
| Hypersaline (stress test) | 3.00 | 21.0 m² | 3.940 W/m² |

**The Fouling Paradox:** Morris screening (k = 14, r = 100) ranks FOULING_BETA **10th of 14 parameters** in scalar power sensitivity (μ* = 0.299). Yet fouling drives discrete shifts in optimal stage count and raises minimum compliance area — a structural limitation of scalar sensitivity analysis for architecture selection problems.

---

## Model architecture

```
Feed chemistry → 40-segment Nernst solver → Cascade optimizer → Morris screening
     ↑                    ↑                        ↑                    ↑
Five SWRO sites   Concentration-dependent    Fresh-dilute vs      k=14 parameters
C_H = 0.35–3.00   transport + dual-          serial vs            r=100 trajectories
                  mechanism fouling          single-stage         60,000 evaluations
```

**Physics engine:** 40-segment 1D axial model with segment-level Nernst potentials, concentration-dependent resistance, Thévenin equivalent circuit at maximum-power operation, spacer shadow factor, and combined-profile dual-mechanism fouling (biofilm exponential outlet model + divalent scaling via concentration-dependent fouling CDF).

**Compliance criterion:** HR_worst = 100% when both concentrate and physical dilute outlets ≤ ambient seawater concentration. Configurations with axial inversion (any segment where dilute exceeds concentrate) are excluded.

**Sweep scale:** 38,400 cascade configurations + 10,811 single-stage rows + 560 Morris elementary-effect rows.

---

## Repository structure

```
OsmoFlux_reproducibility.ipynb        ← Reproduction entry point (cells 1–22)
prior_notebooks/
└── OsmoFlux.ipynb                    ← Full development history
runs/
└── GRAND-SWEEP/
    └── 20260531_183521/
        ├── cascade_sweep.parquet     ← 38,400 rows
        ├── single_stage_sweep.parquet← 10,811 rows
        ├── morris_all.parquet        ← 560 rows
        ├── dashboard.json
        ├── GRAND-SWEEP-MANIFEST.json ← SHA-256 hashes
        └── figures/                  ← All submission figures
OsmoFlux_Equation_Legend.pdf
```

`prior_notebooks/OsmoFlux.ipynb` contains the full development history including intermediate experiments, bug fixes, and exploratory runs. `OsmoFlux_reproducibility.ipynb` is the clean linear path for reproducing paper results.

---

## How to reproduce

```bash
# Requirements: numpy pandas matplotlib scipy pyarrow jupyter
jupyter notebook OsmoFlux_reproducibility.ipynb
```

1. **Run cells 1–20** — model foundation (constants, physics, harness). Executes in under a second; defines all required functions.
2. **Run cell 21** — Grand Sweep v12 runner. Full compute step; expected ~30–60 min on a modern laptop using `multiprocessing.Pool`.
3. **Run cell 22** — Figure Generator v7. Reads parquets from step 2 and writes all figures to `runs/GRAND-SWEEP/<RUN_TIMESTAMP>/figures/`.

### SHA-256 verification (canonical run 20260531_183521)

```
cascade_sweep.parquet:       b041a0410cf8b840191de70a37b0667633d0592f0acfa2797ddbc1078594a641
single_stage_sweep.parquet:  15ea8ae74121d4a8b7f410f4bcae09399cf00e17c4bac35e6a5d85ed27ac1604
morris_all.parquet:          17f4a7e3af961929c6574fbb44b0b50efc11cf687ac3d36bb8b7986b06167ff7
```

macOS: `shasum -a 256 <file>` — Linux: `sha256sum <file>`

---

## Five SWRO plant chemistries

| Site | C_H (mol/L) | C_sw (mol/L) | C_H/C_sw | Notes |
|------|-------------|--------------|----------|-------|
| Valley Water | 0.35 | 0.30 | 1.17 | Brackish groundwater |
| Monterey | 0.75 | 0.60 | 1.25 | Coastal SWRO |
| Carlsbad | 1.15 | 0.60 | 1.92 | Primary case study (Poseidon/SDCWA, 54 MGD) |
| Jebel Ali | 1.80 | 0.65 | 2.77 | High-salinity gulf SWRO |
| Hypersaline | 3.00 | 0.60 | 5.00 | Stress-test boundary |

Carlsbad brine concentration derived from Petersen et al. (2019), *Water*, 11(2):208.

---

## Key references

- Petersen, K.L. et al. (2019). *Water* 11(2):208. doi:10.3390/w11020208 — Carlsbad brine plume field measurements
- Tristán, C. et al. (2024). *Desalination* — Multistage RED optimization at SWRO conditions
- Tedesco, M. et al. (2017). *Journal of Membrane Science* — RED pilot validation
- Vermaas, D.A. et al. (2013). *Environmental Science & Technology* — RED stack characterisation
- Morris, M.D. (1991). *Technometrics* 33(2):161–174 — Elementary effects screening method
- Campolongo, F. et al. (2007). *Environmental Modelling & Software* — Enhanced Morris sampling

---

## Recognition

- 2nd place nationally, Modeling the Future Challenge 2025–26 (157 teams, 25 states)
- GENIUS Olympiad 2026 finalist
- Synopsys Silicon Valley Science and Technology Championship — 2nd Award, Physical Sciences and Engineering

---

## License

MIT License. Model, code, and all outputs are free to use, modify, and build on.

---

## Contact

Rohan Agarwal — rohan.agarwal@blueleaflabs.org  
Blue Leaf Labs — [github.com/blueleaflabs](https://github.com/blueleaflabs)
