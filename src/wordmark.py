"""Construction du wordmark « wubba » et du symbole (le w avec son point).

Unité : hauteur d'x X = 200. Toutes les cotes du dessin sont des paramètres de P,
ce qui permet de régénérer le logo entier en changeant un chiffre.
"""
from __future__ import annotations

import math
from copy import deepcopy

import geom as g

P = {
    "X": 200,          # hauteur d'x
    "A": 272,          # hauteur des ascendantes (b)
    "S": 50,           # graisse des fûts verticaux
    "Sr": 52,          # graisse des flancs courbes (un peu plus, compensation optique)
    "H": 44,           # graisse des horizontales (plus mince, compensation optique)
    "OV": 4,           # dépassement des formes rondes
    "k_out": 0.66,     # rondeur extérieure des panses (0.5523 = cercle)
    "k_in": 0.66,      # rondeur des contreformes
    "counter": "uniform",  # contreformes en superellipse régulière (voir counter_shape)
    "dcut_extend": 0.9,
    "r_stem": 14,      # rayon des coins côté fût (drect)
    "r_free": 58,      # rayon des coins côté libre (drect)
    "Bw": 206,         # largeur des panses de b et a
    "Wu": 190,         # largeur du u
    "w_theta": 19,     # angle des diagonales du w, en degrés depuis la verticale
    "w_D": 46,         # graisse perpendiculaire des diagonales
    "w_hm": 114,       # hauteur du sommet central du w (abaissé pour loger le point)
    "dot_d": 62,       # diamètre du point
    "dot_gap": 19,     # jour entre le sommet central et le point
    "smooth": 0.6,     # lissage des coins (drect)
    "gaps": {"wu": 6, "ub": 24, "bb": 22, "ba": 18},
}


# ---------------------------------------------------------------- glyphes

def counter_shape(p, cx0, cx1, y0, y1, stem_side):
    """Contreforme d'une panse. stem_side : 'left' (b), 'right' (a, u) ou None.

    uniform : superellipse régulière (tangente au fût, jonctions plus sombres)
    dcut    : superellipse deux fois plus large, coupée net sur l'arête du fût (coin vif, jonction propre)
    drect   : rectangle en D, petits rayons côté fût, grands rayons côté libre
    """
    mode, ki = p["counter"], p["k_in"]
    if mode == "uniform" or stem_side is None:
        return g.box(cx0, y0, cx1, y1, k=ki)
    if mode == "dcut":
        w = cx1 - cx0
        if stem_side == "left":
            wide = g.box(cx0 - w * p["dcut_extend"], y0, cx1, y1, k=ki)
            return g.intersect(wide, g.rect(cx0, y0 - 5, cx1 + 5, y1 + 5))
        wide = g.box(cx0, y0, cx1 + w * p["dcut_extend"], y1, k=ki)
        return g.intersect(wide, g.rect(cx0 - 5, y0 - 5, cx1, y1 + 5))
    rs, rl = p["r_stem"], p["r_free"]
    if stem_side == "left":
        return g.rrect(cx0, y0, cx1, y1, tl=rs, tr=rl, br=rl, bl=rs, smooth=p["smooth"])
    return g.rrect(cx0, y0, cx1, y1, tl=rl, tr=rs, br=rs, bl=rl, smooth=p["smooth"])


def glyph_b(p):
    X, A, S, Sr, H, OV, Bw = p["X"], p["A"], p["S"], p["Sr"], p["H"], p["OV"], p["Bw"]
    stem = g.rect(0, 0, S, A)
    outer = g.box(0, -OV, Bw, X + OV, k=p["k_out"])
    counter = counter_shape(p, S, Bw - Sr, -OV + H, X + OV - H, "left")
    return g.diff(g.union(stem, outer), counter), Bw


def glyph_a(p):
    X, S, Sr, H, OV, Bw = p["X"], p["S"], p["Sr"], p["H"], p["OV"], p["Bw"]
    stem = g.rect(Bw - S, 0, Bw, X)
    outer = g.box(0, -OV, Bw, X + OV, k=p["k_out"])
    counter = counter_shape(p, Sr, Bw - S, -OV + H, X + OV - H, "right")
    return g.diff(g.union(stem, outer), counter), Bw


def glyph_u(p):
    X, S, Sr, H, OV, Wu = p["X"], p["S"], p["Sr"], p["H"], p["OV"], p["Wu"]
    stem = g.rect(Wu - S, 0, Wu, X)
    ym = (X - OV) / 2                                   # mi-hauteur de la courbe extérieure
    outer = g.box(0, -OV, Wu, X, k=p["k_out"], tl="sharp", tr="sharp")
    y0 = -OV + H
    y1 = 2 * ym - y0 + (X - 2 * ym)                     # la courbe intérieure finit à la même hauteur
    cbox = counter_shape(p, Sr, Wu - S, y0, y1, "right")
    counter = g.union(cbox, g.rect(Sr, (y0 + y1) / 2, Wu - S, X + 60))
    return g.diff(g.union(outer, stem), counter), Wu


def w_metrics(p):
    X, th, D, hm = p["X"], math.radians(p["w_theta"]), p["w_D"], p["w_hm"]
    k = 1 / math.tan(th)              # pente dy/dx
    hw = D / (2 * math.cos(th))       # demi-graisse horizontale
    c1 = hw + X / k                   # axe du creux gauche, à la ligne de base
    M = c1 + hm / k                   # axe du sommet central
    Ww = 2 * M                        # largeur totale
    return {"k": k, "hw": hw, "c1": c1, "M": M, "Ww": Ww}


def glyph_w(p):
    X, hm = p["X"], p["w_hm"]
    m = w_metrics(p)
    k, hw, c1, M, Ww = m["k"], m["hw"], m["c1"], m["M"], m["Ww"]
    e = 80  # prolongement des traits avant découpe

    def stroke(xa, ya, xb, yb):
        return g.poly([(xa - hw, ya), (xa + hw, ya), (xb + hw, yb), (xb - hw, yb)])

    outer_l = stroke(hw, X, c1 + e / k, -e)
    outer_r = stroke(Ww - hw, X, Ww - c1 - e / k, -e)
    inner_l = stroke(c1 - e / k, -e, M + e / k, hm + e)
    inner_r = stroke(Ww - c1 + e / k, -e, M - e / k, hm + e)
    inner = g.intersect(g.union(inner_l, inner_r), g.rect(-500, -500, Ww + 500, hm))
    w = g.intersect(g.union(outer_l, outer_r, inner), g.rect(-10, 0, Ww + 10, X))
    return w, Ww


def dot(p, cx):
    """Le point. Forme au choix : rond (référence), carré (pixel), anneau (REC), réticule."""
    r = p["dot_d"] / 2
    base = p["w_hm"] if p["w_hm"] < p["X"] else p["X"]
    cy = base + p["dot_gap"] + r
    shape = p.get("dot_shape", "circle")
    if shape == "square":
        a = r * 0.9
        return g.rect(cx - a, cy - a, cx + a, cy + a)
    if shape == "ring":
        return g.diff(g.circle(cx, cy, r * 1.06), g.circle(cx, cy, r * 1.06 - p["S"] * 0.42))
    if shape == "cross":
        t, L = p["S"] * 0.40, r * 1.25
        return g.union(g.rect(cx - t / 2, cy - L, cx + t / 2, cy + L), g.rect(cx - L, cy - t / 2, cx + L, cy + t / 2))
    return g.circle(cx, cy, r)


# ---------------------------------------------------------------- assemblages

def wordmark(p=None, with_dot=True):
    """Retourne (tracé des lettres, tracé du point ou None, largeur, xmin, ymin, ymax)."""
    p = p or P
    order = [("w", glyph_w), ("u", glyph_u), ("b", glyph_b), ("b", glyph_b), ("a", glyph_a)]
    gaps = [p["gaps"]["wu"], p["gaps"]["ub"], p["gaps"]["bb"], p["gaps"]["ba"]]
    x = 0.0
    letters = []
    the_dot = None
    for i, (name, fn) in enumerate(order):
        path, adv = fn(p)
        letters.append(g.translate(path, dx=x))
        if name == "w" and with_dot:
            the_dot = dot(p, x + w_metrics(p)["M"])
        x += adv + (gaps[i] if i < len(gaps) else 0)
    body = g.union(*letters)
    return body, the_dot


def symbol(p=None):
    """Le w seul et son point : c'est l'icône."""
    p = p or P
    w, Ww = glyph_w(p)
    return w, dot(p, w_metrics(p)["M"])


# Coupe « petite taille » : traits plus gras, point plus gros, jour plus serré. Pour 32 px et moins.
SMALL = {"w_D": 56, "w_hm": 110, "dot_d": 72, "dot_gap": 14}


def variant(**changes):
    q = deepcopy(P)
    for key, val in changes.items():
        if key == "gaps":
            q["gaps"].update(val)
        else:
            q[key] = val
    return q
