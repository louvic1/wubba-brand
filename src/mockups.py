"""Mises en situation génériques, pour toutes les directions : planche d'autocollants et signature courriel.

    python3 src/mockups.py            # toutes les directions
    python3 src/mockups.py A O D H    # quelques-unes

Sorties dans options/<code>-<key>/mockups/ : stickers.png (1600 × 1000), signature.png (1200 × 360).
Seuls les textes publics validés apparaissent (nom, domaine, identifiant, courriel).
"""
from __future__ import annotations

import math
import sys

import cairosvg
import pathops
from fontTools.misc.transform import Transform

import compose
import geom as g
from compose import DOMAIN, HANDLE, mix
from directions import ALL, BY_CODE
from motion import svg, xform

EMAIL = "contact@wubba.studio"


def outer(path):
    """Garde les contours extérieurs d'une forme (un autocollant découpé n'a pas de trous)."""
    path = pathops.Path(path)
    path.simplify()
    contours = list(path.contours)
    if not contours:
        return path
    sign = 1 if max(contours, key=lambda c: abs(c.area)).area > 0 else -1
    out = pathops.Path()
    for c in contours:
        if c.area * sign > 0:
            out.addPath(c)
    out.simplify()
    return out


def grow(path, amount):
    s = pathops.Path()
    path.draw(s.getPen())
    s.stroke(amount * 2, pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 4)
    s.convertConicsToQuads()
    s.simplify()
    return g.union(path, s)


def sticker(colored, cx, cy, angle, border, shadow=True, base_color="#FFFFFF"):
    """colored = [(tracé, couleur)] déjà placés autour de (cx, cy). Renvoie des calques (tracé, couleur, alpha)."""
    try:
        base = outer(grow(g.union(*[p for p, _ in colored]), border))
    except pathops.PathOpsError:
        # formes trop fines pour l'opération (texte circulaire du sceau) : découpe simple, cercle ou plaque
        x0, y0, x1, y1 = g.union(*[p for p, _ in colored]).bounds
        w, h = x1 - x0, y1 - y0
        if abs(w - h) < 0.08 * max(w, h):
            base = g.circle((x0 + x1) / 2, (y0 + y1) / 2, max(w, h) / 2 + border)
        else:
            base = g.rounded_rect(x0 - border, y0 - border, x1 + border, y1 + border, border * 2, smooth=0.6)
    T = Transform().translate(cx, cy).rotate(math.radians(angle)).translate(-cx, -cy)
    out = []
    if shadow:
        out.append((g.translate(xform(base, T), dx=5, dy=-9), "#000000", 0.20))
    out.append((xform(base, T), base_color, 1.0))
    out += [(xform(p, T), c, 1.0) for p, c in colored]
    return out


def fit(d, layers, box, sch, align="center"):
    placed, _ = d.place(layers, box, align=align)
    return d.color(placed, sch)


def plate(d, layers, box, sch, pad_k=0.34, radius_k=0.22):
    """Logo posé sur une plaque de couleur (autocollant rectangulaire)."""
    colored = fit(d, layers, box, sch)
    x0, y0, x1, y1 = g.union(*[p for p, _ in colored]).bounds
    pad = (y1 - y0) * pad_k
    r = g.rounded_rect(x0 - pad, y0 - pad, x1 + pad, y1 + pad, min(x1 - x0, y1 - y0) * radius_k, smooth=0.6)
    return [(r, sch["bg"])] + colored


def stickers(d, out):
    W, H = 1600, 1000
    layers = [(g.rect(0, 0, W, H), "#DCD9D2", 1.0)]
    lid = g.rounded_rect(110, 70, W - 110, H - 70, 44, smooth=0.6)
    layers.append((lid, "#2B2C30", 1.0))
    dark, light = d.palette.scheme("dark"), d.palette.scheme("light")
    # 1. plaque sombre avec le logo
    layers += sticker(plate(d, d.wordmark(), (230, 560, 830, 740), dark), 530, 650, -6, 16)
    # 2. tuile d'icône
    ic = compose.tile_layers(d, d.palette.scheme(d.icon_scheme), T=256)
    ic = [(g.translate(p, dx=980, dy=560, sx=0.94, sy=0.94), c) for p, c in ic]
    layers += sticker(ic, 980 + 120, 560 + 120, 8, 14)
    # 3. logo découpé, couleurs claires, sur fond blanc
    layers += sticker(fit(d, d.wordmark(), (760, 240, 1360, 400), light), 1060, 320, 4, 22)
    # 4. symbole découpé
    layers += sticker(fit(d, d.symbol(), (300, 180, 560, 440), light), 430, 310, -10, 20)
    # 5. avatar rond
    ic = compose.tile_layers(d, d.palette.scheme(d.icon_scheme), T=256, shape="circle")
    ic = [(g.translate(p, dx=1250, dy=640, sx=0.7, sy=0.7), c) for p, c in ic]
    layers += sticker(ic, 1250 + 90, 640 + 90, 0, 12)
    path = out / "stickers.png"
    cairosvg.svg2png(bytestring=svg(W, H, layers).encode(), write_to=str(path))
    return path


def signature(d, out):
    W, H = 1200, 360
    white = "#FFFFFF"
    ink = "#1B1C1F"
    muted = "#5C5D61"
    layers = [(g.rect(0, 0, W, H), white, 1.0)]
    ic = compose.tile_layers(d, d.palette.scheme(d.icon_scheme), T=256)
    layers += [(g.translate(p, dx=70, dy=(H - 176) / 2, sx=176 / 256, sy=176 / 256), c, 1.0) for p, c in ic]
    layers.append((g.rect(300, 70, 302, H - 70), "#DDDDDA", 1.0))
    sch = d.palette.scheme("light")
    x0, y0, x1, y1 = g.union(*[p for p, _ in d.wordmark()]).bounds
    if (x1 - x0) / (y1 - y0) < 1.6:
        # un emblème (le sceau) est illisible à cette hauteur : le nom passe dans la typo de titre
        (p, c), _, _ = compose.text_line("wubba", d.display, 64, 352, 200, ink, "left")
        layers.append((p, c, 1.0))
    else:
        # sur fond blanc, un fond de schéma coloré n'existe pas : on garde les couleurs du logo telles quelles
        layers += [(p, c, 1.0) for p, c in fit(d, d.wordmark(), (352, 196, 820, 262), sch, align="left")]
    y = 140
    for s, col, size in ((EMAIL, ink, 30), (f"{DOMAIN}  ·  {HANDLE}", muted, 26)):
        (p, c), _, _ = compose.text_line(s, d.body, size, 352, y, col, "left")
        layers.append((p, c, 1.0))
        y -= 48
    path = out / "signature.png"
    cairosvg.svg2png(bytestring=svg(W, H, layers).encode(), write_to=str(path))
    return path


def build(code):
    d = BY_CODE[code]
    out = compose.OPT / f"{d.code}-{d.key}" / "mockups"
    out.mkdir(parents=True, exist_ok=True)
    stickers(d, out)
    signature(d, out)
    print(code, d.name)


if __name__ == "__main__":
    for c in (sys.argv[1:] or [d.code for d in ALL]):
        build(c)
