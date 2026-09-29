"""Assets du site wubba.studio, tirés du même dessin que le logo (direction A, fond noir).

    python3 src/site_assets.py   ->  site/src/partials/logo-*.svg, site/src/assets/img/*, site/src/assets/fonts/*.woff2

Le mot est en currentColor et le point en var(--dot) : le CSS du site décide des couleurs.
"""
from __future__ import annotations

import io
from pathlib import Path

import cairosvg
from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from PIL import Image

import geom as g
import wordmark as wm

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site" / "src"
PARTIALS = SITE / "partials"
IMG = SITE / "assets" / "img"
FONTS_OUT = SITE / "assets" / "fonts"
FONTS_IN = ROOT / ".fonts"

BLACK, WHITE, GREEN = "#000000", "#FFFFFF", "#72AC0E"

# Latin de base + Latin-1 + ponctuation typographique (apostrophe courbe, guillemets, tirets, puces, ×).
UNICODES = "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+2000-206F,U+20AC,U+2122,U+2190-2193,U+2197,U+2212,U+00D7"


def _bounds(paths):
    xs = [b for p in paths for b in (p.bounds[0], p.bounds[2])]
    ys = [b for p in paths for b in (p.bounds[1], p.bounds[3])]
    return min(xs), min(ys), max(xs), max(ys)


def inline_svg(letters, dot, cls, label, pad=0.0):
    """Un SVG en ligne : lettres en currentColor, point en var(--dot)."""
    x0, y0, x1, y1 = _bounds([letters, dot])
    x0, y0, x1, y1 = x0 - pad, y0 - pad, x1 + pad, y1 + pad
    w, h = x1 - x0, y1 - y0
    d_letters = g.to_d(g.translate(letters, dx=-x0, dy=-y0), h, precision=2)
    d_dot = g.to_d(g.translate(dot, dx=-x0, dy=-y0), h, precision=2)
    return (f'<svg class="{cls}" viewBox="0 0 {w:.2f} {h:.2f}" role="img" aria-label="{label}" focusable="false">'
            f'<path class="{cls}__letters" fill="currentColor" d="{d_letters}"/>'
            f'<path class="{cls}__dot" fill="var(--dot, {GREEN})" d="{d_dot}"/></svg>')


def tile_svg(size, ratio=0.64, small=False, bg=BLACK, lift=0.02):
    """Le symbole (w + point) centré sur une tuile carrée, comme l'icône de marque."""
    w, d = wm.symbol(wm.variant(**wm.SMALL)) if small else wm.symbol()
    x0, y0, x1, y1 = _bounds([w, d])
    s = size * ratio / max(x1 - x0, (y1 - y0) / 0.9)
    tx = (size - (x1 - x0) * s) / 2 - x0 * s
    ty = (size - (y1 - y0) * s) / 2 - y0 * s + size * lift
    place = lambda p: g.translate(g.translate(p, sx=s, sy=s), dx=tx, dy=ty)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
            f'<rect width="{size}" height="{size}" fill="{bg}"/>'
            f'<path fill="{WHITE}" d="{g.to_d(place(w), size)}"/>'
            f'<path fill="{GREEN}" d="{g.to_d(place(d), size)}"/></svg>')


def png(svg, out, size):
    cairosvg.svg2png(bytestring=svg.encode(), write_to=str(out), output_width=size, output_height=size)


def logos():
    PARTIALS.mkdir(parents=True, exist_ok=True)
    body, dot = wm.wordmark()
    (PARTIALS / "logo-wordmark.svg").write_text(inline_svg(body, dot, "wordmark", "wubba"))
    w, d = wm.symbol()
    (PARTIALS / "logo-symbol.svg").write_text(inline_svg(w, d, "symbol", "wubba"))


def icons():
    IMG.mkdir(parents=True, exist_ok=True)
    (IMG / "favicon.svg").write_text(tile_svg(64, ratio=0.74, small=True))
    png(tile_svg(64, ratio=0.74, small=True), IMG / "favicon-32.png", 32)
    png(tile_svg(180), IMG / "apple-touch-icon.png", 180)
    png(tile_svg(512), IMG / "icon-512.png", 512)
    png(tile_svg(192), IMG / "icon-192.png", 192)
    png(tile_svg(512, ratio=0.5), IMG / "icon-maskable-512.png", 512)
    # favicon.ico (16, 32, 48) pour les vieux navigateurs et les onglets de courriel
    ims = []
    for s in (16, 32, 48):
        buf = io.BytesIO()
        cairosvg.svg2png(bytestring=tile_svg(64, ratio=0.74, small=True).encode(), write_to=buf, output_width=s, output_height=s)
        ims.append(Image.open(io.BytesIO(buf.getvalue())).convert("RGBA"))
    ims[-1].save(IMG / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)], append_images=ims[:-1])


def font(src, out, axes=None, pin=None):
    f = TTFont(FONTS_IN / src)
    # sous-ensemble d'abord : l'instanciation avant le sous-ensemble laisse un glyphe « NULL » orphelin
    opts = subset.Options()
    opts.layout_features = ["*"]
    opts.name_IDs = ["*"]
    opts.notdef_outline = True
    sub = subset.Subsetter(options=opts)
    sub.populate(unicodes=subset.parse_unicodes(UNICODES))
    sub.subset(f)
    if pin or axes:
        f = instancer.instantiateVariableFont(f, pin or axes)
    FONTS_OUT.mkdir(parents=True, exist_ok=True)
    f.flavor = "woff2"
    f.save(FONTS_OUT / out)
    return (FONTS_OUT / out).stat().st_size


def fonts():
    sizes = {
        "sora.woff2": font("Sora[wght].ttf", "sora.woff2", axes={"wght": (600, 800)}),
        "figtree.woff2": font("Figtree[wght].ttf", "figtree.woff2", axes={"wght": (400, 600)}),
        "jetbrains-mono.woff2": font("JetBrainsMono[wght].ttf", "jetbrains-mono.woff2", pin={"wght": 500}),
    }
    for k, v in sizes.items():
        print(f"  {k}: {v / 1024:.1f} Ko")


if __name__ == "__main__":
    logos()
    icons()
    fonts()
    print("assets du site écrits dans", SITE)
