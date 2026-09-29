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
    idea = "Le langage de l'esport, dit sans détour : capitales larges penchées à 12°, et un accent volt qui ne sert qu'à dire « ça bouge »."
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

    def wordmark(self):
        t, w = tp.text("WUBBA", FONT[0], 200, FONT[1], tracking=0.01)
        t = skew(t)
        x0, y0, x1, y1 = t.bounds
        h = y1 - y0
        bar = skew(g.rect(x1 + h * 0.16, 0, x1 + h * 0.16 + h * 0.20, h))
        return [(t, "fg"), (bar, "accent")]

    def symbol(self):
        # W en deux chevrons : quatre barres obliques, la seconde paire en accent
        u, h, t = 60, 220, 52
        k = math.tan(math.radians(20))
        def bar(x_top, dirn):
            # barre oblique de largeur t, du haut (x_top) vers le bas
            dx = h * k * dirn
            return g.poly([(x_top, h), (x_top + t, h), (x_top + t + dx, 0), (x_top + dx, 0)])
        left = g.union(bar(0, 1), bar(2 * h * k + t * 0.0 - t * 0.0, -1))
        right = g.translate(left, dx=2 * h * k + t * 0.35)
        return [(skew(left, 0.0), "fg"), (skew(right, 0.0), "accent")]

    def device(self, W, H, sch, fmt):
        from compose import mix
        faint = mix(sch["bg"], sch["fg"], 0.07)
        if fmt == "linkedin-company":
            return [(dv.stripes(W, H, 10, 26, 78, x0=0, x1=W * 0.3), faint)]
        return [(dv.stripes(W, H, 18, 40, 78, x0=0, x1=W * 0.28), faint),
                (dv.stripes(W, H, 18, 40, 78, x0=W * 0.72, x1=W), faint)]
