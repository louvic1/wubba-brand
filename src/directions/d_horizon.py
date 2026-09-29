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
    version = "v2"

    def wordmark(self):
        t, w = tp.text("wubba", FONT[0], 200, FONT[1], tracking=-0.005)
        m = tp.metrics(FONT[0], FONT[1])
        xh = m["x"] * 200 / m["upem"]
        r = xh * 0.34
        sun = half_disc(w + r + xh * 0.1, r)
        return [(t, "fg"), (sun, "accent")]

    def symbol(self):
        # le soleil posé sur l'horizon : le même demi-disque que dans le mot, et sa ligne
        r = 64
        sun = half_disc(0, r)
        line = g.rect(-r * 1.55, -22, r * 1.55, -6)
        return [(sun, "accent"), (line, "fg")]

    def banner_layout(self, fmt, W, H, sch, layout=None):
        """L'horizon traverse la bannière à la hauteur exacte de la ligne de base du mot."""
        from compose import TAGLINE, DOMAIN, mix, page, text_line
        line = mix(sch["bg"], sch["fg"], 0.30)
        muted = mix(sch["fg"], sch["bg"], 0.30)
        wm = self.wordmark()
        box = {"x-header": (W / 2 - 330, 230, W / 2 + 330, 400), "og": (W / 2 - 300, 300, W / 2 + 300, 470),
               "linkedin": (W - 700, 190, W - 90, 320), "linkedin-company": (W - 430, 92, W - 64, 150)}[fmt]
        align = "right" if fmt.startswith("linkedin") else "center"
        wmp, s, (tx, ty) = self.place_t(wm, box, align=align)
        base = ty                                           # y=0 du dessin -> ligne de base à l'écran
        layers = [(dv.hline(0, W, base - 1, 2.0), line)] + self.color(wmp, sch)
        size = {"x-header": 21, "og": 25, "linkedin": 19, "linkedin-company": 13}[fmt]
        gap = {"x-header": 58, "og": 66, "linkedin": 48, "linkedin-company": 30}[fmt]
        x = W / 2 if align == "center" else box[2]
        tl, _, _ = text_line(TAGLINE, self.body, size, x, base - gap, muted, align, False, 0.0, max_w=900)
        layers.append(tl)
        if fmt in ("x-header", "og"):
            dom, _, _ = text_line(DOMAIN, self.mono, 16, W - 76 if fmt == "x-header" else 76, 62, muted,
                                  "right" if fmt == "x-header" else "left", False, 0.02)
            layers.append(dom)
        return page(W, H, layers, bg=sch["bg"])
