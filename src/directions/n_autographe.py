"""N — Autographe. Le nom signé au marqueur, souligné d'un trait : l'autographe d'un streamer qui n'existe pas, sur le carton."""
import math

import pathops
from fontTools.misc.transform import Transform
from fontTools.pens.transformPen import TransformPen

import geom as g
import textpath as tp
from directions.base import Direction, Font, Palette

FONT = ("MrDafoe-Regular.ttf", {})           # v1 : SedgwickAveDisplay (du lettrage, pas une signature)
LABEL_FONT = ("CourierPrime-Bold.ttf", {})


def _bez(p0, p1, p2, p3, t):
    u = 1 - t
    return tuple(u ** 3 * a + 3 * u * u * t * b + 3 * u * t * t * c + t ** 3 * d for a, b, c, d in zip(p0, p1, p2, p3))


def _bez_d(p0, p1, p2, p3, t):
    u = 1 - t
    return tuple(3 * u * u * (b - a) + 6 * u * t * (c - b) + 3 * t * t * (d - c) for a, b, c, d in zip(p0, p1, p2, p3))


def flick(x0, x1, y, lift, w0, w1, steps=72):
    """Trait de marqueur effilé : appuyé au départ (bout rond), il s'amincit et remonte à la fin, comme un geste."""
    p0, p1, p2, p3 = (x0, y), (x0 + (x1 - x0) * 0.35, y - lift * 0.35), (x0 + (x1 - x0) * 0.7, y + lift * 0.1), (x1, y + lift)
    left, right = [], []
    for i in range(steps + 1):
        t = i / steps
        (x, yy), (dx, dy) = _bez(p0, p1, p2, p3, t), _bez_d(p0, p1, p2, p3, t)
        n = math.hypot(dx, dy) or 1
        w = (w0 + (w1 - w0) * t ** 1.6) / 2
        left.append((x - dy / n * w, yy + dx / n * w))
        right.append((x + dy / n * w, yy - dx / n * w))
    return g.union(g.poly(left + right[::-1]), g.circle(x0, y, w0 / 2), g.circle(x1, y + lift, w1 / 2))


def swoosh(x0, x1, y, lift, width):
    """Trait de soulignement à épaisseur constante (v1, gardé pour comparaison)."""
    p = pathops.Path()
    p.moveTo(x0, y)
    p.cubicTo(x0 + (x1 - x0) * 0.35, y - lift * 0.35, x0 + (x1 - x0) * 0.7, y + lift * 0.2, x1, y + lift)
    s = pathops.Path()
    p.draw(s.getPen())
    s.stroke(width, pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 4)
    s.convertConicsToQuads()
    s.simplify()
    return s


def transformed(path, t):
    q = pathops.Path()
    path.draw(TransformPen(q.getPen(), t))
    return q


class Autographe(Direction):
    code = "N"
    key = "autographe"
    name = "Autographe"
    idea = "Le nom signé au marqueur sur le carton du matériel : l'autographe d'un streamer qui n'existe pas. La blague est dans le geste."
    mark_type = "Signature manuscrite + lettre-symbole"
    why = [
        "Le seul logo « fait main » du lot : humain, spontané, à l'opposé du rendu IA lisse.",
        "Le carton kraft et le marqueur parlent de déballage, le rituel central du contenu matériel gaming.",
        "Le soulignement devient un geste animable : la signature se trace en 1 seconde en fin de vidéo.",
    ]
    risk = "Une signature tirée d'une police se retape facilement ; en finition, elle doit être redessinée à la main."
    palette = Palette("#161412", "#D6B98A", "#E0442F", accent2="#F3EBDD",
                      names={"ink": "Marqueur", "paper": "Kraft", "accent": "Rouge fragile", "accent2": "Étiquette"},
                      notes={"ink": "la signature", "paper": "fond carton", "accent": "le soulignement",
                             "accent2": "étiquettes, fonds clairs"})
    display = Font("Barlow Condensed", "BarlowCondensed-ExtraBold.ttf", {})
    body = Font("Barlow", "Barlow-Regular.ttf", {})
    mono = Font("Courier Prime", "CourierPrime-Bold.ttf", {})
    banner_scheme = "light"
    icon_scheme = "light"
    tagline_scale = 1.15
    icon_ratio = 0.70
    version = "v2"

    def wordmark(self):
        t, w = tp.text("wubba", FONT[0], 240, FONT[1])
        x0, y0, x1, y1 = t.bounds
        line = flick(x0 + (x1 - x0) * 0.03, x1 - (x1 - x0) * 0.02, y0 - 24, 26, 20, 5)
        return [(t, "fg"), (line, "accent")]

    def symbol(self):
        t, w = tp.text("w", FONT[0], 300, FONT[1])
        x0, y0, x1, y1 = t.bounds
        line = flick(x0 + (x1 - x0) * 0.02, x1 + 6, y0 - 22, 16, 24, 7)
        return [(t, "fg"), (line, "accent")]

    def device(self, W, H, sch, fmt):
        from compose import mix
        tape = mix(sch["bg"], "#FFFFFF", 0.35)
        if fmt == "linkedin-company":
            return []
        h = H * 0.13

        def strip(cx, cy, length, angle):
            dx, dy = math.cos(math.radians(angle)) * length / 2, math.sin(math.radians(angle)) * length / 2
            nx, ny = -math.sin(math.radians(angle)) * h / 2, math.cos(math.radians(angle)) * h / 2
            return g.poly([(cx - dx - nx, cy - dy - ny), (cx + dx - nx, cy + dy - ny),
                           (cx + dx + nx, cy + dy + ny), (cx - dx + nx, cy - dy + ny)])
        return [(strip(W * 0.06, H * 0.92, H * 0.9, -35), tape), (strip(W * 0.95, H * 0.1, H * 0.9, -35), tape)]

    def label(self, sch, width=360):
        """Étiquette d'expédition : domaine, identifiant, courriel, code-barres décoratif. Coordonnées locales, origine en bas à gauche."""
        from compose import DOMAIN, HANDLE, hex_rgb
        # l'étiquette est toujours claire : on y écrit avec la plus foncée des deux couleurs du schéma
        ink = min((sch["fg"], sch["bg"]), key=lambda c: sum(hex_rgb(c)))
        u = width
        H = u * 0.62
        left, right = u * 0.085, u * 0.915
        paper = self.palette.accent2
        layers = [(g.rect(0, 0, u, H), paper)]
        b = u * 0.035
        layers.append((g.diff(g.rect(b, b, u - b, H - b), g.rect(b + 2, b + 2, u - b - 2, H - b - 2)), ink))
        for s, k, base in ((DOMAIN, 0.092, 0.462), (HANDLE, 0.066, 0.360), ("contact@wubba.studio", 0.054, 0.278)):
            t, w = tp.text(s, LABEL_FONT[0], u * k, LABEL_FONT[1])
            if w > right - left:
                t, w = tp.text(s, LABEL_FONT[0], u * k * (right - left) / w, LABEL_FONT[1])
            layers.append((g.translate(t, dx=left, dy=u * base), ink))
        layers.append((g.rect(left, u * 0.232, right, u * 0.232 + 2), ink))
        bars, x, i = [], left, 0
        widths = [3, 1, 2, 1, 1, 3, 1, 2, 2, 1, 3, 1, 1, 2, 1, 3, 2, 1, 1, 2, 3, 1, 2, 1, 1, 3, 1, 2]
        unit = u * 0.0085
        while x < u * 0.60:
            bw = widths[i % len(widths)] * unit
            if i % 2 == 0:
                bars.append(g.rect(x, u * 0.075, x + bw, u * 0.195))
            x += bw
            i += 1
        layers.append((g.combine(*bars), ink))
        layers.append((g.rect(u * 0.68, u * 0.075, right, u * 0.195), self.palette.accent))
        return layers, (u, H)

    def banner_layout(self, fmt, W, H, sch, layout=None):
        """La signature en grand ; sur X et l'aperçu de lien, une étiquette d'expédition scotchée porte les coordonnées."""
        if layout is not None or fmt not in ("x-header", "og"):
            return None
        from compose import TAGLINE, mix, page, text_line
        muted = mix(sch["fg"], sch["bg"], 0.30)
        tape = mix(sch["bg"], "#FFFFFF", 0.35)
        layers = []
        if fmt == "x-header":
            wm_box, lab_w, lab_c, angle, tag_w = (110, 205, 860, 440), 330, (1215, 265), 4.0, 720
        else:
            wm_box, lab_w, lab_c, angle, tag_w = (90, 300, 780, 525), 300, (960, 215), -5.0, 700
        wmp, _ = self.place(self.wordmark(), wm_box, align="left")
        wb = self.bounds(wmp)
        layers += self.color(wmp, sch)
        tl, _, _ = text_line(TAGLINE, self.mono, 19, wb[0] + 6, wb[1] - 54, muted, "left", True, 0.0, max_w=tag_w)
        layers.append(tl)
        lab, (lw, lh) = self.label(sch, lab_w)
        t = Transform().translate(*lab_c).rotate(math.radians(angle)).translate(-lw / 2, -lh / 2)
        shadow = Transform().translate(lab_c[0] + 5, lab_c[1] - 7).rotate(math.radians(angle)).translate(-lw / 2, -lh / 2)
        layers.append((transformed(g.rect(0, 0, lw, lh), shadow), mix(sch["bg"], "#000000", 0.16)))
        layers += [(transformed(p, t), c) for p, c in lab]
        strip = g.rect(-lw * 0.16, -lh * 0.07, lw * 0.16, lh * 0.07)
        for cx, rot in ((0.0, -38), (lw, 38)):
            tt = t.translate(cx, lh).rotate(math.radians(rot))
            layers.append((transformed(strip, tt), tape))
        return page(W, H, layers, bg=sch["bg"])
