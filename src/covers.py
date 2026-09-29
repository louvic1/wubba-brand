"""Couvertures de chaîne : YouTube (2560 × 1440) et Twitch (1200 × 480), pour les directions finalistes.

YouTube montre tout le cadre sur une télé, une bande de 2560 × 423 sur ordinateur et seulement le centre
de 1546 × 423 sur mobile. Le nom, la ligne et les coordonnées tiennent dans ce centre ; le motif remplit le cadre.

    python3 src/covers.py            # A O D H P Q
    python3 src/covers.py A O

Sorties : options/<direction>/youtube.png (+ .svg), twitch.png (+ .svg), youtube-zones.png (zones de recadrage).
"""
from __future__ import annotations

import sys

import cairosvg

import compose
import devices as dv
import geom as g
from compose import DOMAIN, HANDLE, TAGLINE, mix, page, save, text_line
from directions import BY_CODE

YT = (2560, 1440)
YT_SAFE = (507, 509, 2053, 932)        # coordonnées y vers le haut ; la zone est symétrique
TW = (1200, 480)
TW_SAFE = (70, 56, 1130, 424)


def slot(safe, fx0, fy0, fx1, fy1):
    """Une boîte en fractions de la zone sûre."""
    x0, y0, x1, y1 = safe
    w, h = x1 - x0, y1 - y0
    return (x0 + fx0 * w, y0 + fy0 * h, x0 + fx1 * w, y0 + fy1 * h)


def tag_size(safe):
    return 28 if safe[2] - safe[0] > 1400 else 17


def texts(d, sch, safe, wb, align="center", info_align="right"):
    """La ligne sous le nom, puis domaine et identifiant au pied de la zone sûre."""
    muted = mix(sch["fg"], sch["bg"], 0.30)
    font, upper, track = (d.mono, True, 0.05) if d.tagline_mono else (d.body, False, 0.0)
    x0, y0, x1, y1 = safe
    ts = tag_size(safe) * (1.0 if upper else 1.2)
    ax = (x0 + x1) / 2 if align == "center" else wb[0]
    tl, _, _ = text_line(TAGLINE, font, ts, ax, wb[1] - ts * 2.6, muted, align, upper, track, max_w=(x1 - x0) * 0.86)
    ix = {"right": x1, "left": x0, "center": (x0 + x1) / 2}[info_align]
    info, _, _ = text_line(f"{DOMAIN}    {HANDLE}", d.mono, tag_size(safe) * 0.8, ix, y0 + tag_size(safe) * 0.4, muted,
                           info_align, False, 0.03)
    return [tl, info]


# ------------------------------------------------------------------ une composition par direction

def cover_A(d, W, H, safe, sch):
    """Le viseur encadre exactement ce que voit un téléphone ; les repères de suivi occupent le reste."""
    x0, y0, x1, y1 = safe
    faint = mix(sch["bg"], sch["fg"], 0.12)
    line = mix(sch["bg"], sch["fg"], 0.32)
    k = (y1 - y0) / 423
    pad = 26 * k
    corners = dv.hud_corners(x1 - x0 + 2 * pad, y1 - y0 + 2 * pad, 0, 56 * k, 3 * k)
    layers = [(g.translate(corners, dx=x0 - pad, dy=y0 - pad), line)]
    step = 120 * k
    grid = dv.cross_grid(W, H, step=step, size=12 * k, thick=1.8 * k,
                         keep=lambda x, y: not (x0 - 2 * pad < x < x1 + 2 * pad and y0 - 2 * pad < y < y1 + 2 * pad))
    if grid:
        layers.append((grid, faint))
    wmp, _ = d.place(d.wordmark(), slot(safe, 0.2, 0.44, 0.8, 0.8))
    layers += d.color(wmp, sch)
    layers += texts(d, sch, safe, d.bounds(wmp))
    return page(W, H, layers, bg=sch["bg"])


def cover_O(d, W, H, safe, sch):
    """Le nom en touches à gauche ; le clavier fantôme court sur tout le cadre, la grappe WASD allumée dans la zone sûre."""
    x0, y0, x1, y1 = safe
    k = (y1 - y0) / 423
    s = 118 * k
    p = s * 1.08
    q = x1 - 60 * k - 2.25 * p - s                  # bord gauche de la touche Q : D finit à 60 px du bord de la zone
    cy = (y0 + y1) / 2
    y_top = cy + 0.5 * s + 1.5 * p                   # centre la paire de rangées W / ASD sur la zone
    layers = d.keyboard(q, y_top, s, sch)
    wmp, _ = d.place(d.wordmark(), (x0 + 50 * k, cy + 10 * k, q - 1.5 * p - 60 * k, cy + 150 * k), align="left")
    layers += d.color(wmp, sch)
    wb = d.bounds(wmp)
    layers += texts(d, sch, (x0 + 50 * k, y0, q - 1.5 * p - 60 * k, y1), wb, align="left", info_align="left")
    return page(W, H, layers, bg=sch["bg"])


def cover_D(d, W, H, safe, sch):
    """L'horizon traverse tout le cadre à la hauteur de la ligne de base ; le soleil-point se couche au centre."""
    line = mix(sch["bg"], sch["fg"], 0.30)
    wmp, s, (tx, ty) = d.place_t(d.wordmark(), slot(safe, 0.22, 0.42, 0.78, 0.78))
    layers = [(dv.hline(0, W, ty - 1, 2.4), line)] + d.color(wmp, sch)
    layers += texts(d, sch, safe, d.bounds(wmp))
    return page(W, H, layers, bg=sch["bg"])


def cover_H(d, W, H, safe, sch):
    """Les lignes de balayage couvrent le cadre ; le nom et son curseur au centre."""
    layers = list(d.device(W, H, sch, "x-header"))
    wmp, _ = d.place(d.wordmark(), slot(safe, 0.2, 0.44, 0.8, 0.8))
    layers += d.color(wmp, sch)
    layers += texts(d, sch, safe, d.bounds(wmp))
    return page(W, H, layers, bg=sch["bg"])


def cover_P(d, W, H, safe, sch):
    """Le mot en île au centre, ses courbes de niveau jusqu'aux bords du cadre."""
    from directions.p_topo import contours, island, stroke_lines, terrain
    x0, y0, x1, y1 = safe
    k = (y1 - y0) / 423
    far = mix(sch["bg"], sch.get("fg2") or sch["accent"], 0.55)
    word, s, _ = d.place_t(d.wordmark_plain(), slot(safe, 0.24, 0.42, 0.76, 0.8))
    t = word[0][0]
    base = island(t, 34 * s)
    step = 30 * k
    peaks = [(W * 0.08, H * 0.2, 80 * k), (W * 0.9, H * 0.82, 120 * k), (W * 0.62, H * 0.08, 60 * k)]
    lines = terrain(W, H, base, step, seed=23, noise=46 * k, peaks=peaks, res=4 if W > 2000 else 3)
    frame = g.rect(0, 0, W, H)
    layers = []
    far_p = [q for i, q in lines if i >= 2]
    if far_p:
        layers.append((g.intersect(stroke_lines(far_p, 2.4 * k), frame), far))
    layers.append((contours(base, step, step, 2, 2.9 * k), sch["accent"]))
    layers.append((t, sch["fg"]))
    tb = t.bounds
    muted = mix(sch["fg"], sch["bg"], 0.30)
    for text, font, size, y in ((TAGLINE, d.mono, tag_size(safe), tb[1] - step * 2.6 - tag_size(safe)),
                                (f"{DOMAIN}    {HANDLE}", d.mono, tag_size(safe) * 0.8, y0 + tag_size(safe) * 0.4)):
        (tp_, c), _, _ = text_line(text, font, size, (x0 + x1) / 2, y, muted, "center", text == TAGLINE, 0.04,
                                  max_w=(x1 - x0) * 0.86)
        bx0, by0, bx1, by1 = tp_.bounds
        layers.append((g.rounded_rect(bx0 - 14 * k, by0 - 12 * k, bx1 + 14 * k, by1 + 12 * k, 5 * k, smooth=0.5), sch["bg"]))
        layers.append((tp_, c))
    return page(W, H, layers, bg=sch["bg"])


def cover_Q(d, W, H, safe, sch):
    """La grille de mire sur tout le cadre, les sept barres en pied de zone sûre, mire ronde et nom au centre."""
    x0, y0, x1, y1 = safe
    k = (y1 - y0) / 423
    layers = list(d.device(W, H, sch, "x-header"))
    from directions.q_mire import bars
    layers += d.color(bars(0, y0 + 4 * k, W, y0 + 20 * k), sch)   # dans la bande visible sur ordinateur
    cp, _ = d.place(d.symbol(), slot(safe, 0.14, 0.2, 0.34, 0.92))
    wp, _ = d.place(d.wordmark(), slot(safe, 0.38, 0.46, 0.86, 0.76), align="left")
    cx0, cy0, cx1, cy1 = d.bounds(cp)
    layers.append((g.circle((cx0 + cx1) / 2, (cy0 + cy1) / 2, (cx1 - cx0) / 2 + 12 * k), sch["bg"]))
    layers += d.color(cp, sch) + d.color(wp, sch)
    wb = d.bounds(wp)
    muted = mix(sch["fg"], sch["bg"], 0.30)
    for text, size, y in ((TAGLINE, tag_size(safe) * 0.9, wb[1] - tag_size(safe) * 2.4),
                          (f"{DOMAIN}    {HANDLE}", tag_size(safe) * 0.8, y0 + 44 * k)):
        (tp_, c), _, _ = text_line(text, d.mono, size, wb[0], y, muted, "left", text == TAGLINE, 0.02,
                                  max_w=(x1 - wb[0]) * 0.94)
        bx0, by0, bx1, by1 = tp_.bounds
        layers.append((g.rect(bx0 - 10 * k, by0 - 10 * k, bx1 + 10 * k, by1 + 10 * k), sch["bg"]))
        layers.append((tp_, c))
    return page(W, H, layers, bg=sch["bg"])


COVERS = {"A": cover_A, "O": cover_O, "D": cover_D, "H": cover_H, "P": cover_P, "Q": cover_Q}


def zones(svg_text, out):
    """Aperçu des recadrages YouTube : cadre télé, bande ordinateur, centre mobile."""
    W, H = YT
    overlay = (f'<rect x="0" y="{H - 932}" width="{W}" height="423" fill="none" stroke="#FF2BD1" stroke-width="6" stroke-dasharray="24 14"/>'
               f'<rect x="507" y="{H - 932}" width="1546" height="423" fill="none" stroke="#2EE6D6" stroke-width="6"/>')
    svg2 = svg_text.replace("</svg>", overlay + "</svg>")
    cairosvg.svg2png(bytestring=svg2.encode(), write_to=str(out), output_width=1280)


def build(code):
    d = BY_CODE[code]
    out = compose.OPT / f"{d.code}-{d.key}"
    sch = d.palette.scheme(d.banner_scheme)
    yt = COVERS[code](d, *YT, YT_SAFE, sch)
    save(yt, out / "youtube", png_width=YT[0])
    zones(yt, out / "youtube-zones.png")
    tw = COVERS[code](d, *TW, TW_SAFE, sch)
    save(tw, out / "twitch", png_width=TW[0])
    print(code, d.name)


if __name__ == "__main__":
    for c in (sys.argv[1:] or list(COVERS)):
        build(c)
