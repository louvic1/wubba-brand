"""J — Double-u. Le w est littéralement deux u entrelacés, comme deux maillons : la liaison, le signal qui passe."""
import math

import pathops

import devices as dv
import geom as g
from directions.base import Direction, Font, Palette

T = 36        # graisse du trait (monoline)
X = 200       # hauteur d'x (axe des traits)
R = 62        # rayon de l'arrondi du u (axe)


def stroke(path, width=T, cap=pathops.LineCap.ROUND_CAP):
    s = pathops.Path()
    path.draw(s.getPen())
    s.stroke(width, cap, pathops.LineJoin.ROUND_JOIN, 4)
    s.convertConicsToQuads()
    s.simplify()
    return s


def u_center(x0, top=X):
    """Axe d'un u : deux montants et un arc de 180° (Bézier), ouvert en haut."""
    p = pathops.Path()
    k = 0.5523 * R
    p.moveTo(x0, top)
    p.lineTo(x0, R + T / 2)
    p.cubicTo(x0, R + T / 2 - k, x0 + R - k, T / 2, x0 + R, T / 2)
    p.cubicTo(x0 + R + k, T / 2, x0 + 2 * R, R + T / 2 - k, x0 + 2 * R, R + T / 2)
    p.lineTo(x0 + 2 * R, top)
    return p


def line(x0, y0, x1, y1):
    p = pathops.Path()
    p.moveTo(x0, y0)
    p.lineTo(x1, y1)
    return p


def ring(cx, cy, r):
    p = pathops.Path()
    k = 0.5523 * r
    p.moveTo(cx, cy + r)
    p.cubicTo(cx + k, cy + r, cx + r, cy + k, cx + r, cy)
    p.cubicTo(cx + r, cy - k, cx + k, cy - r, cx, cy - r)
    p.cubicTo(cx - k, cy - r, cx - r, cy - k, cx - r, cy)
    p.cubicTo(cx - r, cy + k, cx - k, cy + r, cx, cy + r)
    p.close()
    return p


def zigzag_w(x0=0.0, a=50.0):
    """Le w en un seul trait : une trace d'oscilloscope à quatre segments, joints arrondis."""
    p = pathops.Path()
    p.moveTo(x0 + T / 2, X - T / 2)
    p.lineTo(x0 + T / 2 + a, T / 2)
    p.lineTo(x0 + T / 2 + 2 * a, X - T / 2)
    p.lineTo(x0 + T / 2 + 3 * a, T / 2)
    p.lineTo(x0 + T / 2 + 4 * a, X - T / 2)
    return stroke(p), 4 * a + T


class Signal(Direction):
    code = "J"
    key = "signal"
    name = "Signal"
    idea = "Le w est une trace d'oscilloscope, un seul trait qui monte et descend : le signal qui passe, même au milieu de l'océan."
    mark_type = "Lettrage monoline sur mesure + lettre-symbole trace"
    why = [
        "Un zigzag régulier se lit instantanément comme un w et comme un signal.",
        "Monoline rond : doux, net et parfaitement régulier à toutes les tailles.",
        "Le symbole s'anime tout seul en vidéo : la trace se dessine de gauche à droite.",
    ]
    risk = "Le zigzag est un motif courant (audio, santé connectée) ; l'outremer frôle le territoire des outils SaaS."
    version = "v2"
    palette = Palette("#0E1022", "#F3F4FA", "#2B3DFF", accent2="#1ED6F0",
                      names={"ink": "Minuit", "paper": "Givre", "accent": "Outremer", "accent2": "Cyan liaison"},
                      notes={"ink": "texte", "paper": "fonds clairs", "accent": "fonds, symbole", "accent2": "détail"},
                      custom={"banner": {"bg": "#2B3DFF", "fg": "#F3F4FA", "accent": "#1ED6F0", "fg2": "#1ED6F0"}})
    display = Font("Sora", "Sora[wght].ttf", {"wght": 700})
    body = Font("Manrope", "Manrope[wght].ttf", {"wght": 500})
    mono = Font("Geist Mono", "GeistMono[wght].ttf", {"wght": 500})
    banner_scheme = "banner"
    tagline_mono = False

    def wordmark(self):
        w, ww = zigzag_w(0)
        x = ww + 30
        u = stroke(u_center(x + T / 2))
        x += 2 * R + T + 26
        b1 = g.union(stroke(line(x + T / 2, 0 + T / 2, x + T / 2, 300)), stroke(ring(x + T / 2 + R + 6, X / 2 + 2, R + 6)))
        x += T + 2 * (R + 6) + 26
        b2 = g.translate(b1, dx=x - (ww + 30 + 2 * R + T + 26))
        x += T + 2 * (R + 6) + 26
        a = g.union(stroke(ring(x + R + 6, X / 2 + 2, R + 6)),
                    stroke(line(x + 2 * (R + 6), X - 10, x + 2 * (R + 6), T / 2)))
        return [(w, "accent"), (g.union(u, b1, b2, a), "fg")]

    def symbol(self):
        w, _ = zigzag_w(0)
        return [(w, "accent")]

    def device(self, W, H, sch, fmt):
        from compose import mix
        faint = mix(sch["bg"], sch["fg"], 0.12)
        if fmt == "linkedin-company":
            return []
        r = H * 0.62
        return [(dv.ring(W * 0.05, H * 0.1, r, 3), faint), (dv.ring(W * 0.05 + r * 0.9, H * 0.1, r, 3), faint)]
