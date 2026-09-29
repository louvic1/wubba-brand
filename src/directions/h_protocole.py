"""H — Protocole. Le nom en chasse fixe, suivi d'un curseur ambre : un rapport de test qui s'écrit en direct."""
import devices as dv
import geom as g
import textpath as tp
from directions.base import Direction, Font, Palette

FONT = ("AzeretMono[wght].ttf", {"wght": 800})


class Protocole(Direction):
    code = "H"
    key = "protocole"
    name = "Protocole"
    idea = "Le nom tapé en chasse fixe, suivi d'un curseur ambre qui clignote : le ton d'un rapport de test, pince-sans-rire et exact."
    mark_type = "Wordmark mono + symbole curseur (vidéo inverse)"
    why = [
        "Le deadpan en forme pure : un protocole, des mesures, pas d'adjectifs.",
        "Le curseur est vivant par nature : il clignote en vidéo, sur le site, dans les bannières animées.",
        "L'ambre phosphore est rare dans le gaming et se lit « instrument » plutôt que « néon ».",
    ]
    risk = "L'esthétique terminal est courante chez les outils pour développeurs ; il faut l'ambre et le papier chaud pour s'en distinguer."
    palette = Palette("#0C0C0A", "#ECE8DC", "#FFB000", accent2="#7A7466",
                      names={"ink": "Terminal", "paper": "Papier listing", "accent": "Ambre phosphore",
                             "accent2": "Gris console"},
                      notes={"ink": "fond, texte", "paper": "fonds clairs", "accent": "le curseur",
                             "accent2": "texte secondaire"})
    display = Font("Azeret Mono", FONT[0], {"wght": 700})
    body = Font("IBM Plex Sans", "IBMPlexSans[wdth,wght].ttf", {"wght": 400, "wdth": 100})
    mono = Font("Azeret Mono", FONT[0], {"wght": 500})

    def wordmark(self):
        gl = tp.glyphs("wubba", FONT[0], 200, FONT[1])
        t = g.union(*[p for _, p, _, _ in gl])
        m = tp.metrics(FONT[0], FONT[1])
        xh = m["x"] * 200 / m["upem"]
        adv = gl[0][3]
        x = gl[-1][2] + adv + adv * 0.12
        cursor = g.rect(x, 0, x + adv * 0.78, xh * 1.02)
        return [(t, "fg"), (cursor, "accent")]

    def symbol(self):
        gl = tp.glyphs("w", FONT[0], 200, FONT[1])
        _, p, _, adv = gl[0]
        m = tp.metrics(FONT[0], FONT[1])
        xh = m["x"] * 200 / m["upem"]
        x0, y0, x1, y1 = p.bounds
        pad = xh * 0.28
        block = g.rect(x0 - pad, -pad, x1 + pad, xh + pad)
        return [(g.diff(block, p), "accent")]

    def device(self, W, H, sch, fmt):
        from compose import mix
        faint = mix(sch["bg"], sch["fg"], 0.05)
        lines = g.combine(*[g.rect(0, y, W, y + 1.2) for y in range(0, H, 4)])
        return [(lines, faint)]
