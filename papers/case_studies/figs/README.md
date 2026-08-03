# Paper 2 figures (Overleaf)

Upload the composite PNGs in this folder to Overleaf under `figs/`.

| File | Contents |
|------|----------|
| `fig_cs1_fd_baseline.png` | CS1 FDs (a–b): HDV baseline, Ideal CAV |
| `fig_cs1_fd_stress.png` | CS1 FDs (a–c): HighLatency, HighLoss, Combined |
| `fig_cs2_fd_freeway_sv.png` | CS2 freeway human mixes (a–c) |
| `fig_cs2_fd_freeway_cav.png` | CS2 freeway connected mixes (a–c) |
| `fig_cs2_fd_arterial.png` | CS2 arterial pairs (a–d) |
| `fig_cs2_fd_truck.png` | CS2 HV/CAHV cross-mixes (a–b) |
| `fig_cs2_shockwave.png` | Shockwave space–time stacked: CAV / AV / SV |
| `fig_cs3_ttc_cdf.png` | CS3 TTC CDFs (1×3): V2V-1D / V2V-2D / V2Ped |

Renamed single-panel sources live in `_raw/`. Rebuild composites with:

```bash
python build_composites.py
```

Network layout images (report Figs 38, 44, 45) were not included and are omitted from `main.tex`.
