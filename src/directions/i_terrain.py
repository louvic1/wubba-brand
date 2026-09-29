"""I — Terrain. Le marquage au pochoir des caisses de matériel : ce qui part en mer, en montagne, sur une plateforme."""
import devices as dv
import geom as g
import textpath as tp
from directions.base import Direction, Font, Palette

FONT = ("BigShouldersStencilDisplay[wght].ttf", {"wght": 900})


class Terrain(Direction):
    code = "I"
    key = "terrain"
    name = "Terrain"
    idea = "Le nom au pochoir sur une plaque jaune haute visibilité, comme sur une caisse de matériel envoyée là où il n'a rien à faire."
    mark_type = "Wordmark pochoir en plaque + symbole caisse"
    why = [
        "Évoque les lieux impossibles par le matériel qu'on y envoie, pas par un paysage.",
        "Le jaune haute visibilité est la couleur des environnements extrêmes : plateformes, bateaux, stations polaires.",
        "Le pochoir est robuste, se reproduit partout (vinyle, caisse, t-shirt) et tient petit.",
    ]
    risk = "Jaune et noir rappellent Corsair et la signalétique de danger ; à tenir en aplat franc, jamais en rayures partout."
    palette = Palette("#1B1C1A", "#EFEDE6", "#FFD60A", accent2="#FF5F1F",
                      names={"ink": "Graphite", "paper": "Os", "accent": "Haute visibilité", "accent2": "Orange secours"},
                      notes={"ink": "texte, fonds", "paper": "fonds clairs", "accent": "la plaque",
                             "accent2": "alerte, très rare"})
    display = Font("Big Shoulders Display", "BigShouldersDisplay[wght].ttf", {"wght": 800})
    body = Font("Barlow", "Barlow-Regular.ttf", {})
    mono = Font("Chivo Mono", "ChivoMono[wght].ttf", {"wght": 500})
    banner_scheme = "dark"
    icon_scheme = "accent"
    version = "v2"

    def _text(self, s):
        t, w = tp.text(s, FONT[0], 200, FONT[1], tracking=0.02)
        return t

    def wordmark(self):
        t = self._text("WUBBA")
        x0, y0, x1, y1 = t.bounds
        h = y1 - y0
        plate = g.rect(x0 - h * 0.28, -h * 0.22, x1 + h * 0.28, y1 + h * 0.22)
        return [(plate, "accent"), (t, "ink-on-accent")]

    def symbol(self):
        t = self._text("W")
        x0, y0, x1, y1 = t.bounds
        h = y1 - y0
        cx = (x0 + x1) / 2
        half = h * 0.78
        plate = g.rect(cx - half, (y0 + y1) / 2 - half, cx + half, (y0 + y1) / 2 + half)
        return [(plate, "accent"), (t, "ink-on-accent")]

    def icon_symbol(self, small=False):
        return [(self._text("W"), "fg")]

    @staticmethod
    def color(layers, scheme):
        out = []
        for p, role in layers:
            if role == "ink-on-accent":
                c = scheme.get("on-accent", scheme["bg"] if scheme.get("plate-invert") else "#1B1C1A")
                if scheme["accent"] in ("#000000", "#FFFFFF"):
                    c = scheme["bg"]
                out.append((p, c))
            else:
                out.append((p, scheme.get(role, scheme["fg"])))
        return out

    def device(self, W, H, sch, fmt):
        inset = {"x-header": 40, "og": 40, "linkedin": 32, "linkedin-company": 16}[fmt]
        L = {"x-header": 64, "og": 64, "linkedin": 52, "linkedin-company": 30}[fmt]
        return [(dv.hud_corners(W, H, inset, L, 8 if H > 250 else 5), sch["accent"])]
