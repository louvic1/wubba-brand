"""M — Sceau. Un tampon d'inspection officiel qui certifie des tests absurdes : la ligne tourne autour, un w au centre."""
import math

import pathops
from fontTools.misc.transform import Transform
from fontTools.pens.transformPen import TransformPen

import devices as dv
import geom as g
import textpath as tp
from compose import TAGLINE
from directions.base import Direction, Font, Palette

RING_FONT = ("ChivoMono[wght].ttf", {"wght": 700})
CENTER_FONT = ("Chivo[wght].ttf", {"wght": 900})
R_OUT, RING, R_IN, THIN = 240, 15, 176, 6


def text_on_circle(s, file, var, size, radius, tracking=0.0):
    """Écrit s sur un cercle, dans le sens horaire, centré en haut. Le haut des lettres pointe vers l'extérieur."""
    gl = tp.glyphs(s, file, size, var, tracking)
    total = gl[-1][2] + gl[-1][3]
    out = pathops.Path()
    for ch, p, x, adv in gl:
        xc = x + adv / 2
        phi = math.pi / 2 - (xc - total / 2) / radius     # angle du glyphe sur le cercle
        t = Transform().translate(radius * math.cos(phi), radius * math.sin(phi)).rotate(phi - math.pi / 2).translate(-xc, 0)
        q = pathops.Path()
        p.draw(TransformPen(q.getPen(), t))
        out.addPath(q)
    out.simplify()
    return out, total


class Sceau(Direction):
    code = "M"
    key = "sceau"
    name = "Sceau"
    idea = "Un tampon d'inspection très officiel qui certifie des tests absurdes : la ligne tourne autour du cercle, un w au centre."
    mark_type = "Emblème (sceau) + symbole centre"
    why = [
        "Le pince-sans-rire poussé au bout : l'air d'un certificat de conformité pour du matériel testé sur un bateau.",
        "Le seul emblème du lot : il vit bien en autocollant, en sceau sur un PDF de rapport, en filigrane.",
        "Le bleu encre de tampon ne ressemble à aucune marque du matériel gaming.",
    ]
    risk = "Illisible en petit comme tous les emblèmes : sous 64 px, seul le centre (le w dans son anneau) reste."
    palette = Palette("#101014", "#EFEFEC", "#3A45D8",
                      names={"ink": "Encre", "paper": "Papier", "accent": "Encre à tampon"},
                      notes={"ink": "texte", "paper": "fonds", "accent": "le sceau"},
                      custom={"dark": {"bg": "#101014", "fg": "#EFEFEC", "accent": "#8E96FF", "fg2": "#8E96FF"}})
    display = Font("Chivo", "Chivo[wght].ttf", {"wght": 800})
    body = Font("Chivo", "Chivo[wght].ttf", {"wght": 400})
    mono = Font("Chivo Mono", "ChivoMono[wght].ttf", {"wght": 500})
    banner_scheme = "light"
    icon_scheme = "accent"
    version = "v2"

    def _center(self, size=250):
        t, _ = tp.text("w", CENTER_FONT[0], size, CENTER_FONT[1])
        x0, y0, x1, y1 = t.bounds
        return g.translate(t, dx=-(x0 + x1) / 2, dy=-(y0 + y1) / 2)

    def _rings(self):
        return g.union(dv.ring(0, 0, R_OUT, RING), dv.ring(0, 0, R_IN, THIN))

    def wordmark(self):
        phrase = " · ".join([TAGLINE.upper(), "WUBBA.STUDIO"]) + " · "
        size = 21
        radius = (R_OUT - RING + R_IN) / 2 - size * 0.36
        _, total = text_on_circle(phrase, *RING_FONT, size, radius)
        track = (2 * math.pi * radius - total) / (size * len(phrase))
        ring_text, _ = text_on_circle(phrase, *RING_FONT, size, radius, tracking=track)
        return [(self._rings(), "accent"), (ring_text, "accent"), (self._center(), "accent")]

    def symbol(self):
        return [(dv.ring(0, 0, R_OUT, RING * 1.6), "accent"), (self._center(290), "accent")]

    def icon_symbol(self, small=False):
        return [(self._center(290), "fg")]

    def device(self, W, H, sch, fmt):
        from compose import mix
        faint = mix(sch["bg"], sch["accent"], 0.10)
        if fmt == "linkedin-company":
            return []
        r = H * 0.9
        return [(dv.ring(W * 0.08, H * 0.2, r, 10), faint), (dv.ring(W * 0.08, H * 0.2, r * 0.8, 4), faint)]

    def banner_layout(self, fmt, W, H, sch, layout=None):
        """Le nom à gauche, le sceau grand et incliné à droite, comme tamponné sur la page."""
        from compose import TAGLINE, DOMAIN, mix, page, text_line
        from fontTools.misc.transform import Transform
        from fontTools.pens.transformPen import TransformPen
        muted = mix(sch["fg"], sch["bg"], 0.32)
        layers = list(self.device(W, H, sch, fmt))
        name, _ = tp.text("wubba", CENTER_FONT[0], 200, CENTER_FONT[1], tracking=-0.02)
        box = {"x-header": (90, 240, 700, 360), "og": (80, 300, 640, 420), "linkedin": (560, 190, 1040, 290),
               "linkedin-company": (380, 90, 690, 140)}[fmt]
        placed, s, _ = self.place_t([(name, "fg")], box, align="left")
        layers += self.color(placed, sch)
        nb = self.bounds(placed)
        size = {"x-header": 16, "og": 19, "linkedin": 14, "linkedin-company": 10}[fmt]
        tl, _, _ = text_line(TAGLINE, self.mono, size, box[0], nb[1] - size * 3.2, muted, "left", True, 0.05,
                             max_w={"x-header": W * 0.52, "og": 540, "linkedin": W * 0.34}.get(fmt, W * 0.34))
        layers.append(tl)
        stamp = self.wordmark()
        diam = {"x-header": H * 0.86, "og": H * 0.72, "linkedin": H * 0.9, "linkedin-company": H * 0.9}[fmt]
        cx = {"x-header": W * 0.80, "og": W * 0.76, "linkedin": W * 0.86, "linkedin-company": W * 0.88}[fmt]
        k = diam / (2 * R_OUT)
        t = Transform().translate(cx, H / 2).rotate(-0.16).scale(k)
        for p, role in stamp:
            q = pathops.Path()
            p.draw(TransformPen(q.getPen(), t))
            layers.append((q, sch.get(role, sch["fg"])))
        if fmt in ("x-header", "og"):
            # sur X, l'avatar couvre le coin bas gauche : le domaine monte en haut
            dom, _, _ = text_line(DOMAIN, self.mono, 15, box[0], 62 if fmt == "og" else H - 72, muted, "left", False, 0.03)
            layers.append(dom)
        return page(W, H, layers, bg=sch["bg"])
