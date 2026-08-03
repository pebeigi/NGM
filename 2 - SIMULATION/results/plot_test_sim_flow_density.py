"""
Edie flow–density diagrams from test_sim.csv.

Produces:
  - one whole-highway (mainline total) FD
  - one FD per logical lane (ramp + each mainline lane)

Matches Results_Processing.ipynb Edie settings: dx=200 m, dt=10 s, s in [100, 1500] m.
"""
from __future__ import annotations

import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Reuse the same logical-lane stitching as the time–space plots
from plot_test_sim_timespace import ON_OFF_LOGICAL, _lane_map, _safe_name

DX = 200.0
DT = 10.0
S_MIN = 100.0
S_MAX = 1500.0
MAINLINE_START = 1  # on_off: 0 = ramp, 1+ = mainline


def _style_fd_ax(ax, title: str, *, density_lim: float, flow_lim: float) -> None:
    ax.set_facecolor("#f7f7f7")
    ax.set_title(title, fontsize=12, pad=8)
    ax.set_xlabel("Density (veh/km)", fontsize=11)
    ax.set_ylabel("Flow (veh/h)", fontsize=11)
    ax.set_xlim(0, density_lim)
    ax.set_ylim(0, flow_lim)
    ax.grid(True, which="major", color="white", linewidth=1.1)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_linewidth(0.8)
        spine.set_color("#444444")


def edie_bins(df: pd.DataFrame, dx: float = DX, dt: float = DT) -> pd.DataFrame:
    """Edie space–time bins for one trajectory table (needs s, time, id, v, logical_lane)."""
    run = df[(df["s"] >= S_MIN) & (df["s"] <= S_MAX)].copy()
    if run.empty:
        return pd.DataFrame()

    t0 = float(run["time"].min())
    run["t_rel"] = run["time"] - t0
    run = run.sort_values(["id", "t_rel"])

    run["dt_raw"] = run.groupby("id")["t_rel"].shift(-1) - run["t_rel"]
    run["dt_raw"] = run["dt_raw"].clip(lower=0.0, upper=dt)

    run["tbin"] = np.floor(run["t_rel"] / dt).astype(int)
    run["sbin"] = np.floor((run["s"] - S_MIN) / dx).astype(int)

    t_bin_end = (run["tbin"] + 1) * dt
    run["dt"] = np.minimum(run["dt_raw"], t_bin_end - run["t_rel"]).clip(lower=0.0)
    run["ds"] = run["v"] * run["dt"]

    agg = (
        run.groupby(["logical_lane", "tbin", "sbin"], as_index=False)
        .agg(time_spent=("dt", "sum"), dist_traveled=("ds", "sum"))
    )
    cell_area = dx * dt
    agg["density_veh_km"] = agg["time_spent"] / cell_area * 1000.0
    agg["flow_veh_h"] = agg["dist_traveled"] / cell_area * 3600.0
    return agg


def _auto_lims(dens: np.ndarray, flow: np.ndarray, *, d_cap: float, f_cap: float) -> tuple[float, float]:
    d_lim = min(d_cap, max(40.0, float(np.nanpercentile(dens, 99.5)) * 1.12))
    f_lim = min(f_cap, max(500.0, float(np.nanpercentile(flow, 99.5)) * 1.15))
    return d_lim, f_lim


def _scatter_fd(
    dens: np.ndarray,
    flow: np.ndarray,
    out_path: Path,
    title: str,
    *,
    color: str,
    density_lim: float,
    flow_lim: float,
    dpi: int = 220,
) -> Path:
    dens = np.asarray(dens, dtype=float)
    flow = np.asarray(flow, dtype=float)
    ok = np.isfinite(dens) & np.isfinite(flow)
    dens, flow = dens[ok], flow[ok]
    d_lim, f_lim = _auto_lims(dens, flow, d_cap=density_lim, f_cap=flow_lim)

    fig, ax = plt.subplots(figsize=(7.2, 5.4), constrained_layout=True)
    ax.scatter(
        dens,
        flow,
        s=18,
        alpha=0.42,
        c=color,
        edgecolors="none",
        rasterized=True,
    )
    _style_fd_ax(ax, title, density_lim=d_lim, flow_lim=f_lim)
    subtitle = f"Edie · Δx = {DX:g} m · Δt = {DT:g} s · $s\\in[{S_MIN:g},{S_MAX:g}]$ m"
    ax.text(
        0.98,
        0.02,
        subtitle,
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=8,
        color="#555555",
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi, facecolor="white")
    plt.close(fig)
    return out_path


def main() -> None:
    here = Path(__file__).resolve().parent
    csv_path = here / "test_sim.csv"
    out_dir = here / "test_sim_flow_density"

    print(f"Loading {csv_path} ...")
    df = pd.read_csv(csv_path)
    need = {"time", "id", "v", "lane"}
    missing = need - set(df.columns)
    if missing:
        raise SystemExit(f"CSV missing columns: {sorted(missing)}")
    pos_col = "x" if "x" in df.columns else "lane_pos"
    if pos_col not in df.columns:
        raise SystemExit("Need corridor position column 'x' or 'lane_pos'")

    df = df.dropna(subset=["time", "id", "v", "lane", pos_col]).copy()
    df["time"] = pd.to_numeric(df["time"], errors="coerce")
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df["v"] = pd.to_numeric(df["v"], errors="coerce")
    df["s"] = pd.to_numeric(df[pos_col], errors="coerce")
    df = df.dropna(subset=["time", "id", "v", "s"])

    lmap = _lane_map()
    df["logical_lane"] = df["lane"].map(lmap)
    n_drop = int(df["logical_lane"].isna().sum())
    if n_drop:
        print(f"Dropped {n_drop} rows with unmapped lane names.")
    df = df.dropna(subset=["logical_lane"])
    df["logical_lane"] = df["logical_lane"].astype(int)

    print("Computing Edie bins ...")
    agg = edie_bins(df)
    if agg.empty:
        raise SystemExit("No Edie bins (check S_MIN/S_MAX coverage).")

    # ---- Per logical lane ----
    lane_titles = {i: title for i, (title, _) in enumerate(ON_OFF_LOGICAL)}
    colors = {
        0: "#2a9d8f",
        1: "#264653",
        2: "#e76f51",
        3: "#457b9d",
    }
    written: list[Path] = []
    for lane in sorted(agg["logical_lane"].unique()):
        d = agg[agg["logical_lane"] == lane]
        title = lane_titles.get(int(lane), f"Logical lane {int(lane)}")
        path = _scatter_fd(
            d["density_veh_km"].to_numpy(),
            d["flow_veh_h"].to_numpy(),
            out_dir / f"fd_{_safe_name(title)}.png",
            f"Flow–density — {title}",
            color=colors.get(int(lane), "#264653"),
            density_lim=150.0,
            flow_lim=2500.0,
        )
        print(f"Wrote {path.name}  ({len(d)} cells)")
        written.append(path)

    # ---- Whole highway: mainline total (sum lanes per space–time cell) ----
    main = agg[agg["logical_lane"] >= MAINLINE_START]
    if main.empty:
        print("No mainline cells for whole-highway FD.")
    else:
        n_ml = int(main["logical_lane"].nunique())
        hw = (
            main.groupby(["tbin", "sbin"], as_index=False)
            .agg(time_spent=("time_spent", "sum"), dist_traveled=("dist_traveled", "sum"))
        )
        cell_area = DX * DT
        hw["density_veh_km"] = hw["time_spent"] / cell_area * 1000.0
        hw["flow_veh_h"] = hw["dist_traveled"] / cell_area * 3600.0
        path = _scatter_fd(
            hw["density_veh_km"].to_numpy(),
            hw["flow_veh_h"].to_numpy(),
            out_dir / "fd_Whole_Highway_Mainline_Total.png",
            f"Flow–density — Whole highway (mainline total, {n_ml} lanes)",
            color="#6a4c93",
            density_lim=250.0,
            flow_lim=6000.0,
        )
        print(f"Wrote {path.name}  ({len(hw)} cells)")
        written.append(path)

    print(f"\nDone: {len(written)} figures -> {out_dir}")


if __name__ == "__main__":
    main()
