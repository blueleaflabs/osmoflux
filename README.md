# OsmoFlux

**The first 1D axially-resolved Reverse Electrodialysis model built for
brine compliance risk — not just energy recovery.**

Desalination plants discharge approximately 142 million cubic metres of
hypersaline brine per day globally. At California's largest plant
(Carlsbad, 54 MGD), peer-reviewed field measurements confirm the discharge
plume exceeds permitted salinity limits. OsmoFlux asks: can Reverse
Electrodialysis reduce brine salinity enough to meet coastal discharge
thresholds while recovering energy to offset costs?

Built by Rohan Agarwal (Blue Leaf Labs) over seven months as a high school
sophomore. Placed 2nd nationally in the 2025-26 Modeling the Future
Challenge (157 teams, 25 states). Full report:
https://www.mtfchallenge.org/awards/

---

## What OsmoFlux does

OsmoFlux translates brine chemistry at a real desalination plant into a
quantitative environmental-and-financial outcome through four sequential
stages:

```
Feed Inputs → 40-Segment Nernst Solver → Cascade Optimizer → Monte Carlo TEA
```

**1. Physics Engine**
- 40-segment 1D Nernst-Planck solver with iterative convergence
- Dual-mechanism fouling: biofilm (exponential outlet model) +
  divalent scaling
- Thévenin equivalent circuit per segment
- Spacer shadow factor for realistic ionic transport

**2. Architecture Optimizer**
- Fresh-dilute vs serial vs reverse cascade configurations
- Staging sweep across 240 geometry combinations
- Environmental compliance constraint: discharge salinity < 2.0 ppt
  above ambient
- Harm reduction calculation per configuration

**3. Morris Sensitivity Screening**
- 12 parameters, 130 model calls (r=10 trajectories, p=4 levels)
- Identifies which parameters actually drive risk vs power output

**4. Monte Carlo Technoeconomic Analysis**
- 5,000-sample joint simulation
- 5 uncertain axes: membrane capex, fouling severity, electricity
  price, brine disposal cost, discount rate
- Full NPV probability distribution, P(NPV>0), break-even surface

**Total: 6,300+ converged simulations**

---

## The Fouling Paradox

The most surprising result from the Morris screening:

> Fouling severity ranks **9th of 12 parameters** in absolute power
> sensitivity (μ\* = 0.135) — yet it is the **#1 driver of cascade
> architecture selection**.

The variable that matters least for power matters most for design.

Under high fouling, serial cascading accumulates salt in the dilute
stream across stages. Downstream stages operate on a less favourable
gradient and can push the dilute outlet **above ambient seawater
salinity** — turning the compliance system into a second non-compliant
discharge. Fresh-dilute cascading breaks this by giving each stage an
independent low-salinity feed.

**Fresh-dilute cascade achieves 96–100% discharge salinity reduction
under realistic fouling. Serial cascade achieves 66–100%.**

---

## Case Study: Carlsbad SWRO Plant

- Brine concentration: C_H = 1.15 mol/L NaCl (derived from published
  site data at 50% recovery)
- Discharge volume: 190,000 m³/day
- Low-salinity feed: treated effluent from the co-located Encina Water
  Pollution Control Facility (EWPCF)
- Primary deployment geometry: N=80 cell pairs, A=0.05 m²/pair
- At clean-membrane conditions: 99.1% harm reduction, reducing excess
  salt discharge from ~6,100 tons/day to ~55 tons/day

Monte Carlo TEA results (Carlsbad, single-stack):
- P(NPV > 0): 37% under moderate fouling / 12% under severe fouling
- P50 NPV: −$26M moderate / −$86M severe
- Cascade break-even membrane cost: ~$40/m²

---

## Repository structure

```
OsmoFlux.ipynb          # Main notebook — all experiments run from here
runs/                   # Experiment outputs (parquet + PNG figures)
outputs/                # Variable reference and freeze manifest
```

All canonical results are SHA-256 hashed in the Freeze Manifest
(`outputs/OsmoFlux_Freeze_Manifest.docx`). Every number in the full
report traces to a timestamped, verified run.

---

## How to run

```python
# Requires: numpy, pandas, matplotlib, scipy, jupyter
jupyter notebook OsmoFlux.ipynb
```

Set `ACTIVE_EXPERIMENT_IDS` in Cell 21 to select which experiments to
run. Key experiment IDs:

| ID | Description |
|----|-------------|
| `CASCADE-CL-SWEEP` | Cascade architecture sweep (240 configurations) |
| `MORRIS-SCREENING` | 12-parameter sensitivity analysis |
| `BRINE-CARLSBAD-MC` | Monte Carlo TEA, moderate fouling |
| `BRINE-CARLSBAD-MC-SEVERE` | Monte Carlo TEA, severe fouling |

---

## Key references

- Petersen et al. (2019). *Water* 11(2):208.
  doi:10.3390/w11020208 — Carlsbad brine plume field measurements
- Vermaas et al. (2014). *J. Membrane Science* — RED stack design
- Długołęcki et al. (2010). *J. Membrane Science* — ion exchange
  membrane resistance

---

## Citation

```
Agarwal, R. (2026). OsmoFlux: A 1D axially-resolved Reverse
Electrodialysis model for desalination brine compliance risk.
Blue Leaf Labs. https://github.com/blueleaflabs/osmoflux
```

Full report and competition results:
https://www.mtfchallenge.org/awards/

---

## License

MIT License. Model, code, and all outputs are free to use, modify,
and build on.
```
