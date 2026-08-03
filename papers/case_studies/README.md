# NGM Case Studies Paper (Paper 2) — Overleaf project

Upload this folder to Overleaf as a new project.

## Required files
| File | Role |
|------|------|
| `main.tex` | Full TRB manuscript |
| `references.bib` | Bibliography |
| `trbunofficial.cls` | **Copy from your Paper 1 Overleaf project** (not stored here) |
| `trb.bst` | TRB BibTeX style (if not bundled in the class) |

## Figures to add under `figs/`
Uncomment the figure blocks in `main.tex` once files exist:

- `cs1_fd_compare.pdf` — CS1 flow–density (ideal vs latency/loss)
- `cs2_fd_freeway.pdf` — CS2 freeway FD pairs (optional; captions already described)
- `cs2_fd_arterial.pdf` — CS2 arterial FD pairs
- `cs2_shockwave_sv_av_cav.pdf` — space–time diagrams
- `cs3_ttc_cdf.pdf` — TTC CDFs by interaction type

Export from `2 - SIMULATION/results/Results_Processing.ipynb` / report figures 38–54.

## Compiler
pdfLaTeX → BibTeX → pdfLaTeX × 2

## Split from Paper 1
- **Paper 1:** NGM tool / architecture / extension surface / calibration modules
- **Paper 2 (this):** CS1–CS3 operational & safety results only; cite Paper 1 as `BeigiNGMTool2026`
