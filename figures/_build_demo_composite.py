"""Build Paper-1 demo composites: time-space (2 lanes) and flow-density (2 lanes)."""
from pathlib import Path
import shutil
from PIL import Image, ImageDraw, ImageFont

res = Path(r"c:\Users\Pedram\NGM_Test_v1\2 - SIMULATION\results")
ts_dir = res / "test_sim_timespace_logical"
fd_dir = res / "test_sim_flow_density"
out_dir = Path(r"c:\Users\Pedram\NGM_Test_v1\figures")
out_dir.mkdir(exist_ok=True)

raw = out_dir / "demo_raw"
raw.mkdir(exist_ok=True)


def font(sz=28):
    for p in [r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\arial.ttf"]:
        if Path(p).exists():
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


def prep(path, label, caption, tw):
    img = Image.open(path).convert("RGB")
    w, h = img.size
    scale = tw / w
    img = img.resize((tw, int(h * scale)), Image.Resampling.LANCZOS)
    pad_t, pad_b = 42, 34
    canvas = Image.new("RGB", (img.width, img.height + pad_t + pad_b), "white")
    canvas.paste(img, (0, pad_t))
    d = ImageDraw.Draw(canvas)
    d.text((10, 6), f"({label})", fill="black", font=font(30))
    bb = d.textbbox((0, 0), caption, font=font(20))
    twc = bb[2] - bb[0]
    d.text(
        ((canvas.width - twc) // 2, img.height + pad_t + 6),
        caption,
        fill="black",
        font=font(20),
    )
    return canvas


def stack_vertical(panels, out_name, panel_width):
    imgs = [prep(p, lab, cap, panel_width) for lab, cap, p in panels]
    pw = max(im.width for im in imgs)
    # pad widths to match
    aligned = []
    for im in imgs:
        if im.width == pw:
            aligned.append(im)
        else:
            c = Image.new("RGB", (pw, im.height), "white")
            c.paste(im, ((pw - im.width) // 2, 0))
            aligned.append(c)
    gap = 12
    H = sum(im.height for im in aligned) + gap * (len(aligned) + 1)
    W = pw + 2 * gap
    out = Image.new("RGB", (W, H), "white")
    y = gap
    for im in aligned:
        out.paste(im, (gap, y))
        y += im.height + gap
    out_path = out_dir / out_name
    out.save(out_path, optimize=True)
    print("wrote", out_path, out.size, f"{out_path.stat().st_size // 1024} KB")
    return out_path


def stack_horizontal(panels, out_name, panel_width):
    imgs = [prep(p, lab, cap, panel_width) for lab, cap, p in panels]
    ph = max(im.height for im in imgs)
    aligned = []
    for im in imgs:
        if im.height == ph:
            aligned.append(im)
        else:
            c = Image.new("RGB", (im.width, ph), "white")
            c.paste(im, (0, (ph - im.height) // 2))
            aligned.append(c)
    gap = 12
    W = sum(im.width for im in aligned) + gap * (len(aligned) + 1)
    H = ph + 2 * gap
    out = Image.new("RGB", (W, H), "white")
    x = gap
    for im in aligned:
        out.paste(im, (x, gap))
        x += im.width + gap
    out_path = out_dir / out_name
    out.save(out_path, optimize=True)
    print("wrote", out_path, out.size, f"{out_path.stat().st_size // 1024} KB")
    return out_path


ts_panels = [
    ("a", "Lane 1 (mainline)", ts_dir / "timespace_Lane_1_Mainline.png"),
    ("b", "Lane 2 (mainline)", ts_dir / "timespace_Lane_2_Mainline.png"),
]
fd_panels = [
    ("a", "Lane 1 (mainline)", fd_dir / "fd_Lane_1_Mainline.png"),
    ("b", "Lane 2 (mainline)", fd_dir / "fd_Lane_2_Mainline.png"),
]

for _lab, _cap, p in ts_panels + fd_panels:
    shutil.copy2(p, raw / p.name)

# Time–space: stacked (wide plots read better vertically)
stack_vertical(ts_panels, "fig_demo_timespace.png", panel_width=1400)
# Flow–density: side-by-side
stack_horizontal(fd_panels, "fig_demo_flow_density.png", panel_width=900)

# Remove obsolete 2x2 if present
old = out_dir / "fig_demo_mixedfleet.png"
if old.exists():
    old.unlink()
    print("removed", old)
