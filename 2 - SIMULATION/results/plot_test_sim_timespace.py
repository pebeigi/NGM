"""
Publication-style time–space diagrams from test_sim.csv.

One figure per *logical* freeway lane (not each SUMO edge/lane segment).
Trajectory color encodes speed. Uses continuous corridor coordinate ``x``.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np
import pandas as pd

# Drop the first meters of corridor position (entry noise / incomplete samples).
X_MIN_CUT_M = 20.0

# on_off geometry (matches Results_Processing / freeway_sim logical lanes)
ON_OFF_LOGICAL = [
    (
        "Lane 0 — Ramp / auxiliary",
        [
            "On_Ramp_0",
            ":Weaving_Start_0_0",
            "Weaving_Area_0",
            ":Weaving_End_0_0",
            "Off_Ramp_0",
        ],
    ),
    (
        "Lane 1 — Mainline",
        [
            "Input_0",
            ":Weaving_Start_1_0",
            "Weaving_Area_1",
            ":Weaving_End_1_0",
            "Output_0",
        ],
    ),
    (
        "Lane 2 — Mainline",
        [
            "Input_1",
            ":Weaving_Start_1_1",
            "Weaving_Area_2",
            ":Weaving_End_1_1",
            "Output_1",
        ],
    ),
    (
        "Lane 3 — Mainline",
        [
            "Input_2",
            ":Weaving_Start_1_2",
            "Weaving_Area_3",
            ":Weaving_End_1_2",
            "Output_2",
        ],
    ),
]


def _lane_map(defs=ON_OFF_LOGICAL) -> dict[str, int]:
    out: dict[str, int] = {}
    for i, (_, names) in enumerate(defs):
        for n in names:
            out[n] = i
    return out


def _safe_name(title: str) -> str:
    s = re.sub(r"[^\w\-]+", "_", title.strip())
    return s.strip("_")[:80]


def _speed_line_collection(
    times: np.ndarray,
    xs: np.ndarray,
    vs: np.ndarray,
) -> LineCollection:
    """Build colored line segments between consecutive samples of one vehicle."""
    pts = np.column_stack([times, xs])
    segs = np.stack([pts[:-1], pts[1:]], axis=1)
    # color by mid-segment speed
    v_mid = 0.5 * (vs[:-1] + vs[1:])
    # drop teleport jumps (lane change / missing samples)
    dt = np.diff(times)
    dx = np.diff(xs)
    keep = (dt > 0) & (dt <= 2.0) & (np.abs(dx) < 80.0)
    segs = segs[keep]
    v_mid = v_mid[keep]
    lc = LineCollection(
        segs,
        array=v_mid,
        cmap="turbo",
        linewidths=0.55,
        alpha=0.92,
        capstyle="round",
        joinstyle="round",
    )
    return lc


def plot_logical_lane_timespace(
    df: pd.DataFrame,
    lane_idx: int,
    title: str,
    out_path: Path,
    *,
    v_clim: tuple[float, float] | None = None,
    dpi: int = 220,
) -> Path | None:
    sub = df[df["logical_lane"] == lane_idx].copy()
    if sub.empty:
        return None

    sub = sub.dropna(subset=["time", "x", "v", "id"])
    if sub.empty:
        return None

    v_min = float(sub["v"].quantile(0.02))
    v_max = float(sub["v"].quantile(0.98))
    if v_clim is not None:
        v_min, v_max = v_clim
    if v_max <= v_min:
        v_max = v_min + 1.0

    fig, ax = plt.subplots(figsize=(15, 4.5), constrained_layout=True)
    ax.set_facecolor("#f7f7f7")

    # draw denser traffic first so sparse fast vehicles stay visible
    for vid, g in sub.groupby("id", sort=False):
        g = g.sort_values("time")
        if len(g) < 2:
            continue
        lc = _speed_line_collection(
            g["time"].to_numpy(dtype=float),
            g["x"].to_numpy(dtype=float),
            g["v"].to_numpy(dtype=float),
        )
        lc.set_clim(v_min, v_max)
        ax.add_collection(lc)

    ax.set_xlim(float(sub["time"].min()), float(sub["time"].max()))
    # small pad on space axis
    x0, x1 = float(sub["x"].min()), float(sub["x"].max())
    pad = 0.02 * max(x1 - x0, 1.0)
    ax.set_ylim(x0 - pad, x1 + pad)

    # shared color scale via a proxy mappable
    sm = plt.cm.ScalarMappable(cmap="turbo", norm=plt.Normalize(vmin=v_min, vmax=v_max))
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, pad=0.015, fraction=0.035)
    cbar.set_label("Speed (m/s)", fontsize=11)
    cbar.ax.tick_params(labelsize=9)

    ax.set_xlabel("Time (s)", fontsize=12)
    ax.set_ylabel("Corridor position $x$ (m)", fontsize=12)
    ax.set_title(title, fontsize=13, pad=8)
    ax.grid(True, which="major", color="white", linewidth=1.1, alpha=1.0)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_linewidth(0.8)
        spine.set_color("#444444")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi, facecolor="white")
    plt.close(fig)
    return out_path


def main() -> None:
    here = Path(__file__).resolve().parent
    csv_path = here / "test_sim.csv"
    out_dir = here / "test_sim_timespace_logical"

    print(f"Loading {csv_path} ...")
    df = pd.read_csv(csv_path)
    need = {"time", "id", "x", "v", "lane"}
    missing = need - set(df.columns)
    if missing:
        raise SystemExit(f"CSV missing columns: {sorted(missing)}")

    lmap = _lane_map()
    df["logical_lane"] = df["lane"].map(lmap)
    n_unmapped = int(df["logical_lane"].isna().sum())
    if n_unmapped:
        print(f"Warning: {n_unmapped} rows have unmapped lane names (dropped).")
        print("  unique unmapped:", sorted(df.loc[df["logical_lane"].isna(), "lane"].astype(str).unique()))
    df = df.dropna(subset=["logical_lane"])
    df["logical_lane"] = df["logical_lane"].astype(int)

    n_before = len(df)
    df = df[df["x"] >= float(X_MIN_CUT_M)].copy()
    print(
        f"Cut first {X_MIN_CUT_M:g} m of corridor x "
        f"({n_before - len(df):,} / {n_before:,} rows removed)."
    )

    # global color scale across all plotted lanes (fair comparison)
    v_lo = float(df["v"].quantile(0.02))
    v_hi = float(df["v"].quantile(0.98))
    print(f"Speed color scale: [{v_lo:.2f}, {v_hi:.2f}] m/s")

    written: list[Path] = []
    for i, (title, names) in enumerate(ON_OFF_LOGICAL):
        present = [n for n in names if n in set(df["lane"].astype(str))]
        if not present:
            continue
        n_pts = int((df["logical_lane"] == i).sum())
        if n_pts == 0:
            continue
        fname = f"timespace_{_safe_name(title)}.png"
        path = plot_logical_lane_timespace(
            df,
            i,
            title,
            out_dir / fname,
            v_clim=(v_lo, v_hi),
        )
        if path is not None:
            print(f"Wrote {path.name}  ({n_pts} points, segments: {', '.join(present)})")
            written.append(path)

    print(f"\nDone: {len(written)} figures -> {out_dir}")


if __name__ == "__main__":
    main()
