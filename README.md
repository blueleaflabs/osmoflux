# OsmoFlux

**A closed-form, compliance-constrained thermodynamic frontier for reverse electrodialysis (RED) on SWRO brine.**

OsmoFlux treats seawater-reverse-osmosis brine-discharge compliance as the binding constraint on RED, and asks what that constraint costs in recoverable energy. The analysis rests on three elements: a salt-balance **feasibility floor** that no stack of any architecture, area, or stage count can beat; a reversible **mixing-work ceiling** that sets the recoverable energy; and a **compliance shadow price** that prices the discharge limit in energy terms. Once flow ratio and brine drawdown are matched, the serial-versus-fresh-dilute cascade choice is a second-order effect.

Built by Rohan Agarwal (Blue Leaf Labs) as an independent research project at Monta Vista High School, Cupertino, CA, through the IRPD program.
ORCID: [0009-0005-7518-0805](https://orcid.org/0009-0005-7518-0805)

---

## Paper

> Agarwal, R. (2026). A thermodynamic frontier for compliance-constrained reverse electrodialysis in SWRO brine management. *Manuscript submitted to Desalination (Elsevier).* A preprint will be deposited following submission.

---

## What the model shows

All results below come from the canonical run **20260706_171438** (electrode-overpotential physics; 4,800 clean, β = 0 designs across five sites). They are regenerated end-to-end by `OsmoFlux_reproducibility.ipynb` with no external data dependency.

### Compliance shadow price

The energy penalty for meeting the discharge limit is zero at low-salinity sites and rises with brine salinity. `J*` is the maximum compliant power density; the penalty is the drop from the unconstrained optimum, and λ̄* is the mean shadow price over the interval where compliance binds.

| Site | C_H (mol/L) | C_SW (mol/L) | φ_min | J\* unconstrained (W/m²) | J\* compliant (W/m²) | Penalty | λ̄\* (W·m⁻² per mol·L⁻¹) |
|------|-------------|--------------|-------|--------------------------|----------------------|---------|--------------------------|
| Valley Water | 0.35 | 0.30 | 0.18 | 0.909 | 0.909 | 0% | 0 |
| Monterey | 0.75 | 0.60 | 0.26 | 2.023 | 2.023 | 0% | 0 |
| Carlsbad | 1.15 | 0.60 | 0.95 | 2.915 | 2.572 | 11.8% | 1.45 |
| Jebel Ali | 1.80 | 0.65 | 1.83 | 4.108 | 3.097 | 24.6% | 1.31 |
| Hypersaline (stress test) | 3.00 | 0.60 | 4.14 | 5.95 | 3.94 | 33.8% | 1.04 |

φ_min is the salt-balance feasibility floor `(C_H − C_SW)/(C_SW − C_L,in)` at the primary dilute feed C_L,in = 0.02 mol/L; below it, no RED stack can comply regardless of architecture, area, or stage count.

### Architecture is second-order

Once flow ratio φ and brine drawdown are matched, and with concentration polarization included, the serial and fresh-dilute cascade configurations capture within **0.003 to 0.012** of one another in exergetic efficiency. Apparent architecture advantages in uncontrolled comparisons are largely a dilute-water-budget artifact.

### Efficiency bound respected

At maximum power each stage sits at the Thévenin point (V_term / V_oc = 0.5000), so realized exergetic efficiency η_cap respects the half-power ceiling: across the 1,964 clean-compliant designs the maximum is **0.493** (median 0.37), with **no design exceeding 0.5**.

---

## Model and physics

- **Solver:** 40-segment 1-D axial model with segment-level Nernst potentials and concentration-dependent resistance; Robinson-Stokes mean ionic activities; Vermaas spacer shadow factor; permselectivity α = 0.975.
- **Operating point:** Thévenin-equivalent maximum-power operation per stage (R_load = R_int).
- **Concentration polarization:** velocity-dependent ohmic dilute-side boundary-layer resistance (a conservative lower bound; EMF/Nernstian face-potential polarization is not yet modeled).
- **Electrode overpotential:** a per-stage electrode loss (0.1 V, Veerman et al. 2010) is included in the net cascade power.
- **Fouling:** the model carries a dual-mechanism fouling term (biofilm exponential-outlet model plus a divalent-binding contribution), but it is held at β = 0 in the reported results, which are therefore clean and NaCl-equivalent throughout.

**Compliance criterion:** a design is compliant when both the concentrate outlet and the physical dilute outlet are ≤ ambient seawater concentration C_SW, and no axial segment shows inversion (dilute exceeding concentrate). Inverted designs are excluded before any result is reported.

---

## Reproduce

```bash
# Requirements: numpy pandas matplotlib scipy pyarrow jupyter
jupyter notebook OsmoFlux_reproducibility.ipynb
```

Run all cells top to bottom. The notebook is self-contained: it regenerates the β = 0 compliance grid (4,800 designs) from the embedded physics with the electrode overpotential included, then writes Figure 1, the compliance-shadow-price figure, `cascade_beta0_grid.parquet`, and `MANIFEST.json` (run identifier, package versions, SHA-256 of every output) to `runs/REPRO/<RUN_ID>/`.

The grid sweep is the long step (~1 hour, single core). It is checkpointed per (N_total, site) block to `runs/_grid_cache/`, which is stable across runs, so an interrupted run resumes rather than restarting. There is no `multiprocessing` and no external data file to supply.

### Canonical run (20260706_171438; Python 3.11.14, macOS)

```
cascade_beta0_grid.parquet:  f0edad94616571a9b1bf0d431c67251713b6672fd0b4ff19552a885f0b4e4f82
```

macOS: `shasum -a 256 <file>` — Linux: `sha256sum <file>`

---

## Repository layout

```
OsmoFlux_reproducibility.ipynb     ← self-contained reproduction entry point
runs/
├── REPRO/<RUN_ID>/                ← regenerated grid, figures, MANIFEST.json
└── _grid_cache/                   ← per-block checkpoints (resumable)
prior_notebooks/
└── OsmoFlux.ipynb                 ← full development history (superseded)
```

`prior_notebooks/OsmoFlux.ipynb` contains earlier exploratory work, including an initial architecture-advantage analysis that a later water-budget control showed to be confounded; it is retained for history and is superseded by the reproducibility notebook and the submitted paper.

---

## Five SWRO plant chemistries

| Site | C_H (mol/L) | C_SW (mol/L) | C_H/C_SW | Notes |
|------|-------------|--------------|----------|-------|
| Valley Water | 0.35 | 0.30 | 1.17 | Brackish groundwater |
| Monterey | 0.75 | 0.60 | 1.25 | Coastal SWRO |
| Carlsbad | 1.15 | 0.60 | 1.92 | Primary case study (Poseidon/SDCWA, 54 MGD) |
| Jebel Ali | 1.80 | 0.65 | 2.77 | High-salinity Gulf SWRO |
| Hypersaline | 3.00 | 0.60 | 5.00 | Stress-test boundary |

Carlsbad brine concentration derived from Petersen et al. (2019), *Water* 11(2):208.

---

## Key references

- Pattle, R.E. (1954). *Nature* 174:660. doi:10.1038/174660a0 — first demonstration of salinity-gradient power
- Veerman, J. et al. (2009). *Journal of Membrane Science*. doi:10.1016/j.memsci.2009.05.047 — multistage RED
- Vermaas, D.A. et al. (2013). *Environmental Science & Technology* — RED stack characterisation and fouling
- Ahmad, M. & Baddour, R.E. (2014). *Ocean & Coastal Management*. doi:10.1016/j.ocecoaman.2013.10.020 — brine-discharge regulation
- Rijnaarts, T. et al. (2017). *Environmental Science & Technology*. doi:10.1021/acs.est.7b03858 — divalent cations in RED
- Wang, Q. et al. (2022) — serial multistage RED as a brine-management tool
- Tristán, C. et al. (2024). *Desalination* — multistage RED optimisation at SWRO conditions
- Petersen, K.L. et al. (2019). *Water* 11(2):208. doi:10.3390/w11020208 — Carlsbad brine plume field measurements

---

## Recognition

- 2nd place nationally, Modeling the Future Challenge 2025–26
- GENIUS Olympiad 2026 finalist
- Synopsys Silicon Valley Science and Technology Championship — 2nd Award, Physical Sciences and Engineering

---

## License

MIT License. Model, code, and all outputs are free to use, modify, and build on.

---

## Contact

Rohan Agarwal — rohan.agarwal@blueleaflabs.org
Blue Leaf Labs — [github.com/blueleaflabs](https://github.com/blueleaflabs)
