"""
Generate NGM repository overview figure (ICML / NeurIPS style).
Outputs: figures/ngm_overview.pdf and figures/ngm_overview.png
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.lines as mlines

# ---------------------------------------------------------------------------
# Style (clean conference-paper aesthetic)
# ---------------------------------------------------------------------------
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
    "font.size": 9,
    "axes.linewidth": 0,
})

# Muted palette
C_BG_STAGE = "#F7F8FA"
C_BORDER = "#2C3E50"
C_ACCENT1 = "#3B6EA8"   # stage 1 blue
C_ACCENT2 = "#2E8B6E"   # stage 2 green
C_ACCENT3 = "#7B5EA7"   # datasets purple
C_ARROW = "#5A6A7A"
C_TEXT = "#1A1A1A"
C_MUTED = "#5C6670"

BOX_KW = dict(boxstyle="round,pad=0.35,rounding_size=0.08", linewidth=1.2)


def rounded_box(ax, xy, w, h, facecolor, edgecolor=C_BORDER, alpha=1.0, zorder=2):
    x, y = xy
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.15",
        facecolor=facecolor, edgecolor=edgecolor,
        linewidth=1.0, alpha=alpha, zorder=zorder,
    )
    ax.add_patch(patch)
    return patch


def label_box(ax, xy, w, h, title, lines, title_color=C_TEXT, fs_title=9.5, fs_body=7.8):
    x, y = xy
    ax.text(x + w / 2, y + h - 0.22, title, ha="center", va="top",
            fontsize=fs_title, fontweight="bold", color=title_color, zorder=5)
    body = "\n".join(lines)
    ax.text(x + w / 2, y + h - 0.55, body, ha="center", va="top",
            fontsize=fs_body, color=C_MUTED, linespacing=1.35, zorder=5)


def arrow(ax, start, end, style="-|>", mutation=12):
    arr = FancyArrowPatch(
        start, end, arrowstyle=style, mutation_scale=mutation,
        linewidth=1.4, color=C_ARROW, zorder=3,
        connectionstyle="arc3,rad=0.0",
    )
    ax.add_patch(arr)


def main():
    fig_w, fig_h = 15.5, 5.4
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.set_xlim(0, fig_w)
    ax.set_ylim(0, fig_h)
    ax.axis("off")

    # ---- Title strip ----
    ax.text(fig_w / 2, fig_h - 0.2,
            "NGM: Next Generation Modeling — End-to-End Calibration-to-Simulation Framework",
            ha="center", va="top", fontsize=11.5, fontweight="bold", color=C_TEXT)

    # ===================================================================
    # STAGE 0 — Datasets (left)
    # ===================================================================
    sx, sy, sw, sh = 0.35, 0.55, 2.15, 4.35
    rounded_box(ax, (sx, sy), sw, sh, C_BG_STAGE, edgecolor=C_ACCENT3, alpha=0.55)
    ax.text(sx + sw / 2, sy + sh - 0.15, "0 — Datasets",
            ha="center", va="top", fontsize=10, fontweight="bold", color=C_ACCENT3)

    ds_boxes = [
        ("Waymo Open\nMotion", "AV / CF pairs"),
        ("TGSIM Freeways", "I-395, I-90/94,\nI-294"),
        ("TGSIM VRU", "Foggy Bottom\nped / bike"),
    ]
    for i, (t, sub) in enumerate(ds_boxes):
        by = sy + sh - 1.0 - i * 1.15
        rounded_box(ax, (sx + 0.18, by), sw - 0.36, 0.95, "white", edgecolor="#C8CDD3")
        ax.text(sx + sw / 2, by + 0.62, t, ha="center", va="center",
                fontsize=8.5, fontweight="bold", color=C_TEXT)
        ax.text(sx + sw / 2, by + 0.28, sub, ha="center", va="center",
                fontsize=7.2, color=C_MUTED)

    ax.text(sx + sw / 2, sy + 0.22, "ngm_paths.py",
            ha="center", va="bottom", fontsize=7.5, style="italic", color=C_MUTED)

    # ===================================================================
    # STAGE 1 — Parametric Input (center-left)
    # ===================================================================
    s1x, s1y, s1w, s1h = 2.85, 0.55, 4.55, 4.35
    rounded_box(ax, (s1x, s1y), s1w, s1h, C_BG_STAGE, edgecolor=C_ACCENT1, alpha=0.55)
    ax.text(s1x + s1w / 2, s1y + s1h - 0.15, "1 — Parametric Input (Calibration)",
            ha="center", va="top", fontsize=10, fontweight="bold", color=C_ACCENT1)

    modules = [
        ("Car-Following", ["IDM", "Prospect Theory (PT)"], 3.35),
        ("Lane Changing", ["MOBIL", "Drift Diffusion (DDM)"], 2.15),
        ("Lateral Motion", ["Curvilinear transform", "Polynomial shape"], 0.95),
        ("VRU (Ped / Bike)", ["Social Force (SF)", "Prospect Theory (PT)"], -0.25),
    ]
    for title, models, by in modules:
        rounded_box(ax, (s1x + 0.2, s1y + by), s1w - 0.4, 0.88, "white", edgecolor="#C8CDD3")
        ax.text(s1x + 0.55, s1y + by + 0.62, title, ha="left", va="center",
                fontsize=8.3, fontweight="bold", color=C_TEXT)
        ax.text(s1x + 0.55, s1y + by + 0.28, "  ·  ".join(models), ha="left", va="center",
                fontsize=7.2, color=C_MUTED)

    # GA box
    rounded_box(ax, (s1x + 0.2, s1y + 0.55), s1w - 0.4, 0.55, "#E8F0FA", edgecolor=C_ACCENT1)
    ax.text(s1x + s1w / 2, s1y + 0.82, "Genetic Algorithm (GA)  →  per-class parameter CSVs",
            ha="center", va="center", fontsize=7.8, fontweight="bold", color=C_ACCENT1)

    # ===================================================================
    # BRIDGE — Parameter pools
    # ===================================================================
    bx, by, bw, bh = 7.65, 2.05, 1.35, 1.25
    rounded_box(ax, (bx, by), bw, bh, "#FFF8E7", edgecolor="#C9A227")
    ax.text(bx + bw / 2, by + bh - 0.12, "Parameter\nPools", ha="center", va="top",
            fontsize=8.5, fontweight="bold", color="#8A6D1B")
    ax.text(bx + bw / 2, by + 0.38,
            "merged_IDM_*.csv\nmerged_PT_*.csv\nMOBIL_results.csv\nSF / PT ATM",
            ha="center", va="center", fontsize=6.8, color=C_MUTED, linespacing=1.3)

    # ===================================================================
    # STAGE 2 — Simulation (right)
    # ===================================================================
    s2x, s2y, s2w, s2h = 9.25, 0.55, 3.9, 4.35
    rounded_box(ax, (s2x, s2y), s2w, s2h, C_BG_STAGE, edgecolor=C_ACCENT2, alpha=0.55)
    ax.text(s2x + s2w / 2, s2y + s2h - 0.15, "2 — Simulation",
            ha="center", va="top", fontsize=10, fontweight="bold", color=C_ACCENT2)

    # GUI + SUMO stack
    rounded_box(ax, (s2x + 0.2, s2y + 3.0), s2w - 0.4, 0.85, "white", edgecolor="#C8CDD3")
    label_box(ax, (s2x + 0.2, s2y + 3.0), s2w - 0.4, 0.85,
              "PyQt5 Wizard (GUI.py)", ["Network · Demand · Signals · Models"])

    rounded_box(ax, (s2x + 0.2, s2y + 1.95), s2w - 0.4, 0.9, "white", edgecolor="#C8CDD3")
    label_box(ax, (s2x + 0.2, s2y + 1.95), s2w - 0.4, 0.9,
              "SUMO + TraCI Runtime", ["Freeway · Arterial · Intersection · TGSIM"])

    # Vehicle classes
    rounded_box(ax, (s2x + 0.2, s2y + 1.05), s2w - 0.4, 0.75, "white", edgecolor="#C8CDD3")
    ax.text(s2x + s2w / 2, s2y + 1.55, "Vehicle Mix", ha="center", va="center",
            fontsize=8.3, fontweight="bold", color=C_TEXT)
    ax.text(s2x + s2w / 2, s2y + 1.22,
            "SV · AV · HV · CAV · CAHV  |  Ped · Bike",
            ha="center", va="center", fontsize=7.0, color=C_MUTED)

    # Cooperative layer
    rounded_box(ax, (s2x + 0.2, s2y + 0.55), s2w - 0.4, 0.4, "#E8F5F0", edgecolor=C_ACCENT2)
    ax.text(s2x + s2w / 2, s2y + 0.75,
            "C-IDM · C-MOBIL · V2X Bus (range, latency, loss)",
            ha="center", va="center", fontsize=7.2, fontweight="bold", color=C_ACCENT2)

      # ===================================================================
    # OUTPUTS (far right)
    # ===================================================================
    ox, oy, ow, oh = 13.55, 0.55, 1.75, 4.35
    rounded_box(ax, (ox, oy), ow, oh, C_BG_STAGE, edgecolor="#C0392B", alpha=0.45)
    ax.text(ox + ow / 2, oy + oh - 0.15, "Outputs & Analysis",
            ha="center", va="top", fontsize=10, fontweight="bold", color="#C0392B")

    outputs = [
        ("Trajectories", "per-vehicle CSV"),
        ("Flow–Density", "EDIE-style FD"),
        ("Safety", "TTC · PET"),
        ("Case Studies", "CS1–CS4 batch runs"),
    ]
    for i, (t, sub) in enumerate(outputs):
        oby = oy + oh - 1.05 - i * 0.95
        rounded_box(ax, (ox + 0.15, oby), ow - 0.3, 0.78, "white", edgecolor="#C8CDD3")
        ax.text(ox + ow / 2, oby + 0.5, t, ha="center", va="center",
                fontsize=8.2, fontweight="bold", color=C_TEXT)
        ax.text(ox + ow / 2, oby + 0.2, sub, ha="center", va="center",
                fontsize=7.0, color=C_MUTED)

    # ===================================================================
    # Arrows
    # ===================================================================
    arrow(ax, (sx + sw, sy + sh / 2), (s1x, s1y + s1h / 2))
    arrow(ax, (s1x + s1w, s1y + s1h / 2 - 0.3), (bx, by + bh / 2))
    arrow(ax, (bx + bw, by + bh / 2), (s2x, s2y + s1h / 2))
    arrow(ax, (s2x + s2w, s2y + s1h / 2), (ox, oy + oh / 2))

    # Extension surface callout (bottom)
    rounded_box(ax, (2.85, 0.08), 11.2, 0.38, "#EEF2FF", edgecolor="#4A5FC1", alpha=0.9)
    ax.text(8.45, 0.27,
            "Extension surface: swap models · networks · demand · metrics via documented modules (no core rewrite)",
            ha="center", va="center", fontsize=7.8, fontstyle="italic", color="#3D4EA3")

    # Legend for human vs connected models
    leg_y = 0.02
    human = mlines.Line2D([], [], color=C_MUTED, marker="s", linestyle="None",
                          markersize=7, markerfacecolor="white", markeredgecolor="#C8CDD3")
    conn = mlines.Line2D([], [], color=C_ACCENT2, marker="s", linestyle="None",
                         markersize=7, markerfacecolor="#E8F5F0", markeredgecolor=C_ACCENT2)
    ax.legend(handles=[human, conn],
              labels=["Human-driven models (PT / DDM / SF)", "Connected models (C-IDM / C-MOBIL / V2X)"],
              loc="lower left", bbox_to_anchor=(0.01, -0.02), frameon=False,
              fontsize=7.2, ncol=2, handlelength=1.2)

    out_dir = __file__.replace("ngm_overview_figure.py", "")
    import os
    os.makedirs(out_dir, exist_ok=True)
    pdf_path = os.path.join(out_dir, "ngm_overview.pdf")
    png_path = os.path.join(out_dir, "ngm_overview.png")
    fig.savefig(pdf_path, bbox_inches="tight", dpi=300, facecolor="white")
    fig.savefig(png_path, bbox_inches="tight", dpi=300, facecolor="white")
    plt.close(fig)
    print(f"Saved: {pdf_path}")
    print(f"Saved: {png_path}")


if __name__ == "__main__":
    main()
