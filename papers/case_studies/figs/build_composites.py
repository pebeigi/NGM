"""
Organize Paper-2 figures: rename sources and build Overleaf-ready multi-panel composites.
"""
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FIGS = Path(__file__).resolve().parent
RAW = FIGS / "_raw"
RAW.mkdir(exist_ok=True)

# --- Source identity map ---
RENAME = {
    "CS1_1.png": "cs1_fd_hdv_baseline.png",
    "CS1_2.png": "cs1_fd_ideal.png",
    "CS1_3.png": "cs1_fd_high_latency.png",
    "CS1_4.png": "cs1_fd_high_loss.png",
    "CS1_5.png": "cs1_fd_high_latency_high_loss.png",
    "image773.png": "cs2_fwy_fd_100sv.png",
    "image774.png": "cs2_fwy_fd_100cav.png",
    "image775.png": "cs2_fwy_fd_90sv_10hv.png",
    "image776.png": "cs2_fwy_fd_90cav_10cahv.png",
    "image777.png": "cs2_fwy_fd_80sv_20hv.png",
    "image778.png": "cs2_fwy_fd_80cav_20cahv.png",
    "image779.png": "cs2_art_fd_90cav_10cahv.png",
    "image780.png": "cs2_art_fd_90sv_10hv.png",
    "image781.png": "cs2_art_fd_80cav_20cahv.png",
    "image782.png": "cs2_art_fd_80sv_20hv.png",
    "image784.png": "cs2_fwy_fd_90sv_10cahv.png",
    "image785.png": "cs2_fwy_fd_90cav_10hv.png",
    # Report order Figs 52–54: CAV, AV, SV
    "image786.png": "cs2_shock_cav.png",
    "image787.png": "cs2_shock_av.png",
    "image788.png": "cs2_shock_sv.png",
    "image789.png": "cs3_ttc_v2v1d.png",
    "image790.png": "cs3_ttc_v2v2d.png",
    "image791.png": "cs3_ttc_v2ped.png",
    "image792.png": "cs3_ttc_v2bike.png",
}


def _font(size: int = 28):
    for name in (
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ):
        p = Path(name)
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


def load(name: str) -> Image.Image:
    return Image.open(RAW / name).convert("RGB")


def panel(img: Image.Image, label: str, caption: str, target_w: int) -> Image.Image:
    """Resize to target_w, add (a)/(b) label and short caption bar."""
    w, h = img.size
    scale = target_w / w
    img = img.resize((target_w, int(h * scale)), Image.Resampling.LANCZOS)
    pad_top, pad_bot = 36, 34
    canvas = Image.new("RGB", (img.width, img.height + pad_top + pad_bot), "white")
    canvas.paste(img, (0, pad_top))
    draw = ImageDraw.Draw(canvas)
    f_lab = _font(26)
    f_cap = _font(18)
    draw.text((8, 4), f"({label})", fill="black", font=f_lab)
    # center caption under panel
    bbox = draw.textbbox((0, 0), caption, font=f_cap)
    tw = bbox[2] - bbox[0]
    draw.text(((canvas.width - tw) // 2, img.height + pad_top + 6), caption, fill="black", font=f_cap)
    return canvas


def grid(panels: list[Image.Image], ncols: int, gap: int = 12, bg="white") -> Image.Image:
    assert panels
    pw, ph = panels[0].size
    # normalize heights (same width already)
    panels = [p if p.size == (pw, ph) else p.resize((pw, ph)) for p in panels]
    nrows = (len(panels) + ncols - 1) // ncols
    W = ncols * pw + (ncols + 1) * gap
    H = nrows * ph + (nrows + 1) * gap
    out = Image.new("RGB", (W, H), bg)
    for i, p in enumerate(panels):
        r, c = divmod(i, ncols)
        x = gap + c * (pw + gap)
        y = gap + r * (ph + gap)
        out.paste(p, (x, y))
    return out


def grid_rows(row_lists: list[list[Image.Image]], gap: int = 12, bg="white") -> Image.Image:
    """Stack rows of panels, centering each row (useful for 3+2 layouts)."""
    row_imgs = []
    max_w = 0
    for panels in row_lists:
        pw, ph = panels[0].size
        w = len(panels) * pw + (len(panels) + 1) * gap
        h = ph + 2 * gap
        row = Image.new("RGB", (w, h), bg)
        for i, p in enumerate(panels):
            row.paste(p, (gap + i * (pw + gap), gap))
        row_imgs.append(row)
        max_w = max(max_w, w)
    out = Image.new("RGB", (max_w, sum(r.height for r in row_imgs)), bg)
    y = 0
    for r in row_imgs:
        out.paste(r, ((max_w - r.width) // 2, y))
        y += r.height
    return out


def main():
    # 1) Move/rename originals into _raw/
    for src, dst in RENAME.items():
        sp = FIGS / src
        if sp.exists():
            tp = RAW / dst
            if not tp.exists():
                sp.replace(tp)
            elif sp.exists() and sp.resolve() != tp.resolve():
                sp.unlink()  # duplicate leftover
            print(f"raw: {dst}")
        elif (RAW / dst).exists():
            print(f"raw exists: {dst}")
        else:
            print(f"MISSING: {src}")

    TW = 900  # panel width

    # ---- CS1 FDs: baseline pair + stress trio ----
    cs1_base = [
        ("a", "100% SV (HDV)", "cs1_fd_hdv_baseline.png"),
        ("b", "Ideal CAV (0 s, 0%)", "cs1_fd_ideal.png"),
    ]
    cs1_stress = [
        ("a", "High latency (1.0 s)", "cs1_fd_high_latency.png"),
        ("b", "High loss (50%)", "cs1_fd_high_loss.png"),
        ("c", "High latency + high loss", "cs1_fd_high_latency_high_loss.png"),
    ]
    panels = [panel(load(f), lab, cap, TW) for lab, cap, f in cs1_base]
    grid(panels, ncols=2).save(FIGS / "fig_cs1_fd_baseline.png", optimize=True)
    print("wrote fig_cs1_fd_baseline.png")
    panels = [panel(load(f), lab, cap, TW) for lab, cap, f in cs1_stress]
    grid(panels, ncols=3).save(FIGS / "fig_cs1_fd_stress.png", optimize=True)
    print("wrote fig_cs1_fd_stress.png")
    old = FIGS / "fig_cs1_fd.png"
    if old.exists():
        old.unlink()

    # ---- CS2 freeway: two figures × 3 panels (SV mixes, then CAV mixes) ----
    cs2f_sv = [
        ("a", "100% SV", "cs2_fwy_fd_100sv.png"),
        ("b", "90% SV / 10% HV", "cs2_fwy_fd_90sv_10hv.png"),
        ("c", "80% SV / 20% HV", "cs2_fwy_fd_80sv_20hv.png"),
    ]
    cs2f_cav = [
        ("a", "100% CAV", "cs2_fwy_fd_100cav.png"),
        ("b", "90% CAV / 10% CAHV", "cs2_fwy_fd_90cav_10cahv.png"),
        ("c", "80% CAV / 20% CAHV", "cs2_fwy_fd_80cav_20cahv.png"),
    ]
    panels = [panel(load(f), lab, cap, TW) for lab, cap, f in cs2f_sv]
    grid(panels, ncols=3).save(FIGS / "fig_cs2_fd_freeway_sv.png", optimize=True)
    print("wrote fig_cs2_fd_freeway_sv.png")
    panels = [panel(load(f), lab, cap, TW) for lab, cap, f in cs2f_cav]
    grid(panels, ncols=3).save(FIGS / "fig_cs2_fd_freeway_cav.png", optimize=True)
    print("wrote fig_cs2_fd_freeway_cav.png")
    old = FIGS / "fig_cs2_fd_freeway.png"
    if old.exists():
        old.unlink()

    # ---- CS2 arterial (2×2) ----
    cs2a = [
        ("a", "90% SV / 10% HV", "cs2_art_fd_90sv_10hv.png"),
        ("b", "90% CAV / 10% CAHV", "cs2_art_fd_90cav_10cahv.png"),
        ("c", "80% SV / 20% HV", "cs2_art_fd_80sv_20hv.png"),
        ("d", "80% CAV / 20% CAHV", "cs2_art_fd_80cav_20cahv.png"),
    ]
    panels = [panel(load(f), lab, cap, TW) for lab, cap, f in cs2a]
    grid(panels, ncols=2).save(FIGS / "fig_cs2_fd_arterial.png", optimize=True)
    print("wrote fig_cs2_fd_arterial.png")

    # ---- CS2 truck cross (1×2) ----
    cs2t = [
        ("a", "90% SV / 10% CAHV", "cs2_fwy_fd_90sv_10cahv.png"),
        ("b", "90% CAV / 10% HV", "cs2_fwy_fd_90cav_10hv.png"),
    ]
    panels = [panel(load(f), lab, cap, TW) for lab, cap, f in cs2t]
    grid(panels, ncols=2).save(FIGS / "fig_cs2_fd_truck.png", optimize=True)
    print("wrote fig_cs2_fd_truck.png")

    # ---- Shockwaves stacked vertically — report order CAV, AV, SV ----
    sh = [
        ("a", "CAV", "cs2_shock_cav.png"),
        ("b", "AV", "cs2_shock_av.png"),
        ("c", "SV", "cs2_shock_sv.png"),
    ]
    panels = [panel(load(f), lab, cap, 1100) for lab, cap, f in sh]
    grid(panels, ncols=1).save(FIGS / "fig_cs2_shockwave.png", optimize=True)
    print("wrote fig_cs2_shockwave.png")

    # ---- CS3 TTC CDFs (3×1; bike panel omitted) ----
    cs3 = [
        ("a", "V2V-1D (link)", "cs3_ttc_v2v1d.png"),
        ("b", "V2V-2D (intersection)", "cs3_ttc_v2v2d.png"),
        ("c", "V2Ped", "cs3_ttc_v2ped.png"),
    ]
    panels = [panel(load(f), lab, cap, TW) for lab, cap, f in cs3]
    grid(panels, ncols=1).save(FIGS / "fig_cs3_ttc_cdf.png", optimize=True)
    print("wrote fig_cs3_ttc_cdf.png")

    print("\nDone. Upload these Overleaf figs/ files:")
    for name in [
        "fig_cs1_fd_baseline.png",
        "fig_cs1_fd_stress.png",
        "fig_cs2_fd_freeway_sv.png",
        "fig_cs2_fd_freeway_cav.png",
        "fig_cs2_fd_arterial.png",
        "fig_cs2_fd_truck.png",
        "fig_cs2_shockwave.png",
        "fig_cs3_ttc_cdf.png",
    ]:
        print(" ", name, (FIGS / name).stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
