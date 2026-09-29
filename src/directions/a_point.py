"""A — Le point de trop. Wordmark géométrique sur mesure ; un point sur un w qui n'en prend jamais."""
import devices as dv
import geom as g
import palette as pal
import wordmark as wm
from directions.base import Direction, Font, Palette


class Point(Direction):
    code = "A"
    key = "point"
    name = "Le point de trop"
    idea = "Un point posé là où aucun w n'en porte : le voyant REC d'un live, et la tête d'un joueur qui lève les bras."
    mark_type = "Wordmark sur mesure + lettre-symbole"
    why = [
        "L'idée du studio, dite par la typo : un élément placé là où il n'a pas d'affaire à être.",
        "Le point rouge se lit « en direct » sans un mot, dans toutes les langues.",
        "Lettres dessinées à la main en superellipses : impossibles à retaper avec une police.",
    ]
    risk = "Le rouge sur noir est partagé par plusieurs marques gaming (HyperX, ROG). La forme porte la distinction, pas la couleur."
    palette = Palette(pal.INK, pal.PAPER, pal.SIGNAL,
                      names={"ink": "Encre", "paper": "Papier", "accent": "Signal"},
                      notes={"ink": "texte, fonds sombres", "paper": "fonds clairs", "accent": "le point, rien d'autre"})
    display = Font("Archivo", "Archivo[wdth,wght].ttf", {"wght": 800, "wdth": 125})
    body = Font("Instrument Sans", "InstrumentSans[wdth,wght].ttf", {"wght": 400, "wdth": 100})
    mono = Font("Martian Mono", "MartianMono[wdth,wght].ttf", {"wght": 500, "wdth": 100})
    tagline_mono = True

    def wordmark(self):
        body, dot = wm.wordmark()
        return [(body, "fg"), (dot, "accent")]

    def symbol(self):
        w, d = wm.symbol()
        return [(w, "fg"), (d, "accent")]

    def symbol_small(self):
        w, d = wm.symbol(wm.variant(**wm.SMALL))
        return [(w, "fg"), (d, "accent")]

    def device(self, W, H, sch, fmt):
        from compose import mix
        faint = mix(sch["bg"], sch["fg"], 0.12)
        line = mix(sch["bg"], sch["fg"], 0.32)
        inset = {"x-header": 40, "og": 40, "linkedin": 32, "linkedin-company": 18}[fmt]
        L = {"x-header": 46, "og": 46, "linkedin": 38, "linkedin-company": 22}[fmt]
        out = [(dv.hud_corners(W, H, inset, L, 2.5 if H > 250 else 2), line)]
        if fmt != "linkedin-company":
            cx0, cx1 = W * 0.13, W * 0.87
            grid = dv.cross_grid(W, H, step=100 if H >= 400 else 80, size=9, thick=1.4,
                                 keep=lambda x, y: (x < cx0 or x > cx1) and inset + 30 < y < H - inset - 30)
            if grid:
                out.append((grid, faint))
        return out
