"""D — Horizon. Le soleil se couche sur la ligne de base : le point final du mot est un demi-disque."""
import devices as dv
import geom as g
import textpath as tp
from directions.base import Direction, Font, Palette

FONT = ("Fraunces[SOFT,WONK,opsz,wght].ttf", {"wght": 700, "opsz": 144, "SOFT": 50, "WONK": 0})


def half_disc(cx, r):
    """Demi-disque posé sur y=0 (le soleil couché sur la ligne de base)."""
    return g.intersect(g.circle(cx, 0, r), g.rect(cx - r - 1, 0, cx + r + 1, r + 1))


class Horizon(Direction):
    code = "D"
    key = "horizon"
    name = "Horizon"
    idea = "Le point final du mot est un soleil couché sur la ligne de base : chaque test a lieu quelque part, au bout du monde."
    mark_type = "Wordmark serif + symbole pictogramme"
    why = [
        "Parle des lieux impossibles (mer, sommet, désert) sans dessiner un bateau.",
        "La seule direction chaleureuse et cinématographique : elle se démarque d'un secteur tout en noir néon.",
        "Le soleil-point marche comme ponctuation dans les titres, les vidéos, les signatures.",
    ]
    risk = "Peut se lire « voyage » ou « voile » plutôt que « gaming » ; il faut le gameplay dans les visuels pour ancrer."
    palette = Palette("#0B1A2B", "#EFF2EE", "#FFB23F", accent2="#FF6B5B",
                      names={"ink": "Nuit", "paper": "Écume", "accent": "Ambre", "accent2": "Corail"},
                      notes={"ink": "fonds, texte", "paper": "fonds clairs", "accent": "le soleil",
                             "accent2": "reflets, rare"})
    display = Font("Fraunces", FONT[0], {"wght": 700, "opsz": 144, "SOFT": 50, "WONK": 0})
    body = Font("Figtree", "Figtree[wght].ttf", {"wght": 400})
    mono = Font("Red Hat Mono", "RedHatMono[wght].ttf", {"wght": 500})
    tagline_mono = False

    def wordmark(self):
        t, w = tp.text("wubba", FONT[0], 200, FONT[1], tracking=-0.005)
        m = tp.metrics(FONT[0], FONT[1])
        xh = m["x"] * 200 / m["upem"]
        r = xh * 0.34
        sun = half_disc(w + r + xh * 0.1, r)
        return [(t, "fg"), (sun, "accent")]

    def symbol(self):
        r = 64
        sun = half_disc(128, r)
        bars = g.union(g.rounded_rect(128 - 60, -26, 128 + 60, -14, 6, smooth=0),
                       g.rounded_rect(128 - 40, -46, 128 + 40, -34, 6, smooth=0),
                       g.rounded_rect(128 - 20, -66, 128 + 20, -54, 6, smooth=0))
        return [(sun, "accent"), (bars, "fg2")]

    def device(self, W, H, sch, fmt):
        from compose import mix
        line = mix(sch["bg"], sch["fg"], 0.22)
        glow = mix(sch["bg"], sch["accent"], 0.14)
        y = H * 0.30
        out = [(dv.hline(0, W, y, 1.5), line)]
        if fmt != "linkedin-company":
            R = H * 0.42
            cx = W * 0.14 if fmt != "linkedin" else W * 0.5
            out.insert(0, (g.translate(half_disc(cx, R), dy=y), glow))
        return out
