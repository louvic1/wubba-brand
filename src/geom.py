"""Primitives géométriques pour le logo Wubba.

Tout est construit en coordonnées « y vers le haut » (ligne de base à y=0, hauteur d'x à y=X),
puis retourné en SVG au moment de l'écriture. Les unions et différences passent par skia-pathops,
pour que chaque lettre sorte en un seul tracé propre, sans chevauchement ni trait.
"""
from __future__ import annotations

import math

import pathops
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

KAPPA = 0.5522847498  # quart de cercle en Bézier cubique


def rect(x0, y0, x1, y1):
    p = pathops.Path()
    p.moveTo(x0, y0)
    p.lineTo(x1, y0)
    p.lineTo(x1, y1)
    p.lineTo(x0, y1)
    p.close()
    return p


def poly(points):
    p = pathops.Path()
    p.moveTo(*points[0])
    for pt in points[1:]:
        p.lineTo(*pt)
    p.close()
    return p


def circle(cx, cy, r):
    return box(cx - r, cy - r, cx + r, cy + r, k=KAPPA)


def box(x0, y0, x1, y1, k=KAPPA, tl=None, tr=None, br=None, bl=None):
    """Forme fermée qui passe par le milieu des quatre côtés.

    Chaque coin vaut soit un facteur k (0.5523 = ellipse, ~0.7 = superellipse, ~0.9 = presque carré),
    soit la chaîne "sharp" pour un vrai coin droit. Quatre ancres par forme, jamais plus.
    """
    xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
    c = {"tl": tl if tl is not None else k, "tr": tr if tr is not None else k,
         "br": br if br is not None else k, "bl": bl if bl is not None else k}
    p = pathops.Path()
    p.moveTo(xm, y1)  # milieu du haut, sens horaire (y vers le haut)

    def corner(kind, corner_pt, start, end):
        if kind == "sharp":
            p.lineTo(*corner_pt)
            p.lineTo(*end)
        else:
            kk = kind
            c1 = (start[0] + kk * (corner_pt[0] - start[0]), start[1] + kk * (corner_pt[1] - start[1]))
            c2 = (end[0] + kk * (corner_pt[0] - end[0]), end[1] + kk * (corner_pt[1] - end[1]))
            p.cubicTo(*c1, *c2, *end)

    corner(c["tr"], (x1, y1), (xm, y1), (x1, ym))
    corner(c["br"], (x1, y0), (x1, ym), (xm, y0))
    corner(c["bl"], (x0, y0), (xm, y0), (x0, ym))
    corner(c["tl"], (x0, y1), (x0, ym), (xm, y1))
    p.close()
    return p


def rounded_rect(x0, y0, x1, y1, r, smooth=0.6):
    """Rectangle aux côtés droits et aux coins lissés (courbure continue, façon icône d'app).

    smooth=0 donne un arc de cercle classique ; 0.6 étire la courbe sur 1.6 r pour éviter
    l'effet « os » (le côté droit qui semble pincé à la jonction).
    """
    e = r * (1 + smooth)                 # longueur sur laquelle la courbe s'étend depuis le coin
    h = e * (KAPPA + 0.2 * smooth)       # poignée : plus longue qu'un arc, donc transition plus douce
    p = pathops.Path()
    p.moveTo(x0 + e, y1)
    p.lineTo(x1 - e, y1)
    p.cubicTo(x1 - e + h, y1, x1, y1 - e + h, x1, y1 - e)
    p.lineTo(x1, y0 + e)
    p.cubicTo(x1, y0 + e - h, x1 - e + h, y0, x1 - e, y0)
    p.lineTo(x0 + e, y0)
    p.cubicTo(x0 + e - h, y0, x0, y0 + e - h, x0, y0 + e)
    p.lineTo(x0, y1 - e)
    p.cubicTo(x0, y1 - e + h, x0 + e - h, y1, x0 + e, y1)
    p.close()
    return p


def rrect(x0, y0, x1, y1, tl, tr, br, bl, smooth=0.6):
    """Rectangle à côtés droits, un rayon par coin, coins lissés comme rounded_rect."""
    def ext(r):
        e = r * (1 + smooth)
        return e, e * (KAPPA + 0.2 * smooth)
    etl, htl = ext(tl); etr, htr = ext(tr); ebr, hbr = ext(br); ebl, hbl = ext(bl)
    p = pathops.Path()
    p.moveTo(x0 + etl, y1)
    p.lineTo(x1 - etr, y1)
    p.cubicTo(x1 - etr + htr, y1, x1, y1 - etr + htr, x1, y1 - etr)
    p.lineTo(x1, y0 + ebr)
    p.cubicTo(x1, y0 + ebr - hbr, x1 - ebr + hbr, y0, x1 - ebr, y0)
    p.lineTo(x0 + ebl, y0)
    p.cubicTo(x0 + ebl - hbl, y0, x0, y0 + ebl - hbl, x0, y0 + ebl)
    p.lineTo(x0, y1 - etl)
    p.cubicTo(x0, y1 - etl + htl, x0 + etl - htl, y1, x0 + etl, y1)
    p.close()
    return p


def combine(*paths):
    """Regroupe des contours dans un seul tracé, sans opération booléenne (pour des motifs sans chevauchement)."""
    out = pathops.Path()
    for p in paths:
        if p is not None:
            out.addPath(p)
    return out


def union(*paths):
    out = pathops.Path()
    for p in paths:
        out = pathops.op(out, p, pathops.PathOp.UNION)
    return out


def diff(a, *bs):
    out = a
    for b in bs:
        out = pathops.op(out, b, pathops.PathOp.DIFFERENCE)
    return out


def intersect(a, b):
    return pathops.op(a, b, pathops.PathOp.INTERSECTION)


def translate(path, dx=0.0, dy=0.0, sx=1.0, sy=1.0):
    out = pathops.Path()
    pen = TransformPen(out.getPen(), (sx, 0, 0, sy, dx, dy))
    path.draw(pen)
    return out


def offset_stroke(path, amount):
    """Épaissit (amount>0) ou amincit (amount<0) une forme pleine d'une valeur absolue, via un contour."""
    s = pathops.Path()
    path.draw(s.getPen())
    s.stroke(abs(amount) * 2, pathops.LineCap.BUTT_CAP, pathops.LineJoin.MITER_JOIN, 4)
    return union(path, s) if amount > 0 else diff(path, s)


def bounds(path):
    return path.bounds  # (xmin, ymin, xmax, ymax)


def to_d(path, height, dx=0.0, dy=0.0, scale=1.0, precision=2):
    """Chemin SVG : retourne l'axe y (SVG a y vers le bas) et arrondit les coordonnées."""
    pen = SVGPathPen(None, ntos=lambda v: _fmt(v, precision))
    tp = TransformPen(pen, (scale, 0, 0, -scale, dx, height * scale + dy))
    path.draw(tp)
    return pen.getCommands()


def _fmt(v, precision):
    s = f"{round(v, precision):.{precision}f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def deg(a):
    return math.radians(a)
