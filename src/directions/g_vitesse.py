"""G — Vitesse. Capitales très larges, penchées comme une plaque de course ; un W taillé en deux chevrons."""
import math

import devices as dv
import geom as g
import textpath as tp
from directions.base import Direction, Font, Palette

FONT = ("Unbounded[wght].ttf", {"wght": 900})
SKEW = math.tan(math.radians(12))


def skew(path, k=SKEW):
    from fontTools.pens.transformPen import TransformPen
    import pathops
    out = pathops.Path()
    path.draw(TransformPen(out.getPen(), (1, 0, k, 1, 0, 0)))
    return out


class Vitesse(Direction):
    code = "G"
    key = "vitesse"
    name = "Vitesse"
    idea = "Le langage de l'esport, dit sans détour : capitales larges penchées à 12°, et un W en deux chevrons dont le second est volt."
    mark_type = "Wordmark capitales + symbole W chevrons"
    why = [
        "Parle la langue visuelle des équipes et des tournois : zéro traduction pour un public CS2.",
        "Le volt tranche sur le noir et ne ressemble à aucune marque de périphérique majeure.",
        "Le symbole en chevrons tient à 16 px et se lit comme un W et comme une flèche.",
    ]
    risk = "Le plus codé « esport » : il peut sembler générique face aux orgs, et moins « agence » face aux marques."
    palette = Palette("#0A0B0D", "#F2F3F5", "#D4FF00", accent2="#8A93A6",
                      names={"ink": "Carbone", "paper": "Blanc", "accent": "Volt", "accent2": "Acier"},
                      notes={"ink": "fonds, lettres", "paper": "fonds clairs", "accent": "un trait, un chevron",
                             "accent2": "texte secondaire"})
    display = Font("Unbounded", FONT[0], {"wght": 800})
    body = Font("Barlow", "Barlow-Medium.ttf", {})
    mono = Font("JetBrains Mono", "JetBrainsMono[wght].ttf", {"wght": 600})
    version = "v2"

    def _chevron_w(self, x0, width, height, bar):
        """W en deux chevrons (V + V) qui partagent le sommet central. Renvoie (V gauche, V droit)."""
        run = (width - bar) / 4

        def slab(xt, dirn):
            return g.poly([(xt, height), (xt + bar, height), (xt + bar + dirn * run, 0), (xt + dirn * run, 0)])
        v1 = g.union(slab(x0, 1), slab(x0 + 2 * run, -1))
        v2 = g.union(slab(x0 + 2 * run, 1), slab(x0 + 4 * run, -1))
        return v1, v2

    def _word(self):
        gl = tp.glyphs("WUBBA", FONT[0], 200, FONT[1], tracking=0.01)
        m = tp.metrics(FONT[0], FONT[1])
        cap = m["cap"] * 200 / m["upem"]
        stem = tp.text("I", FONT[0], 200, FONT[1])[0].bounds
        bar = (stem[2] - stem[0]) * 1.12
        _, wpath, _, _ = gl[0]
        x0, y0, x1, y1 = wpath.bounds
        v1, v2 = self._chevron_w(x0, x1 - x0, cap, bar)
        rest = g.union(*[p for _, p, _, _ in gl[1:]])
        return skew(v1), skew(v2), skew(rest)

    def wordmark(self):
        v1, v2, rest = self._word()
        return [(v1, "fg"), (v2, "accent"), (rest, "fg")]

    def symbol(self):
        v1, v2, _ = self._word()
        return [(v1, "fg"), (v2, "accent")]

    def device(self, W, H, sch, fmt):
        from compose import mix
        faint = mix(sch["bg"], sch["fg"], 0.07)
        if fmt == "linkedin-company":
            return [(dv.stripes(W, H, 10, 26, 78, x0=0, x1=W * 0.3), faint)]
        return [(dv.stripes(W, H, 18, 40, 78, x0=0, x1=W * 0.28), faint),
                (dv.stripes(W, H, 18, 40, 78, x0=W * 0.72, x1=W), faint)]
