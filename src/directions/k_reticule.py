"""K — Réticule. Un réticule de tir à quatre branches dont le centre est le seul point de couleur."""
import devices as dv
import geom as g
import textpath as tp
from directions.base import Direction, Font, Palette

FONT = ("Saira[wdth,wght].ttf", {"wght": 750, "wdth": 125})


def crosshair(cx, cy, arm=74, thick=30, gap=40, dot=30):
    arms = g.union(
        g.rect(cx - thick / 2, cy + gap, cx + thick / 2, cy + gap + arm),
        g.rect(cx - thick / 2, cy - gap - arm, cx + thick / 2, cy - gap),
        g.rect(cx + gap, cy - thick / 2, cx + gap + arm, cy + thick / 2),
        g.rect(cx - gap - arm, cy - thick / 2, cx - gap, cy + thick / 2),
    )
    return arms, g.rect(cx - dot / 2, cy - dot / 2, cx + dot / 2, cy + dot / 2)


class Reticule(Direction):
    code = "K"
    key = "reticule"
    name = "Réticule"
    idea = "Le réticule d'un jeu de tir, quatre branches et un centre : le seul point coloré est la cible, le produit du client."
    mark_type = "Symbole abstrait + wordmark large"
    why = [
        "Lisible en un quart de seconde par n'importe quel joueur de CS2 : c'est l'objet qu'il regarde 10 000 heures.",
        "Le centre coloré dit « on vise juste » et place le produit du client au milieu de l'image.",
        "Construction à angles droits, parfaite en pixel, indestructible en favicon.",
    ]
    risk = "Le viseur est un cliché du gaming ; ce qui le sauve est la sobriété (pas de cercle, pas de lueur)."
    palette = Palette("#0D1117", "#EEF1F5", "#19E3FF", accent2="#FF4D6D",
                      names={"ink": "Ardoise", "paper": "Brume", "accent": "Cyan viseur", "accent2": "Rouge impact"},
                      notes={"ink": "fonds, texte", "paper": "fonds clairs", "accent": "le centre", "accent2": "très rare"})
    display = Font("Saira", FONT[0], {"wght": 750, "wdth": 125})
    body = Font("Onest", "Onest[wght].ttf", {"wght": 400})
    mono = Font("Red Hat Mono", "RedHatMono[wght].ttf", {"wght": 500})
    version = "v2"

    def wordmark(self):
        t, w = tp.text("wubba", FONT[0], 200, FONT[1], tracking=0.0)
        x0, y0, x1, y1 = t.bounds
        m = tp.metrics(FONT[0], FONT[1])
        xh = m["x"] * 200 / m["upem"]
        s = xh * 1.18 / 228
        arms, dot = crosshair(0, 0, 74 * s, 30 * s, 40 * s, 34 * s)
        dx = x0 - (74 + 40) * s - xh * 0.34
        arms, dot = g.translate(arms, dx=dx, dy=xh / 2), g.translate(dot, dx=dx, dy=xh / 2)
        return [(arms, "fg"), (dot, "accent"), (t, "fg")]

    def symbol(self):
        arms, dot = crosshair(0, 0)
        return [(arms, "fg"), (dot, "accent")]

    def device(self, W, H, sch, fmt):
        from compose import mix
        line = mix(sch["bg"], sch["fg"], 0.10)
        return [(dv.hline(0, W, H / 2, 1.2), line), (dv.vline(W * 0.12, 0, H, 1.2), line),
                (dv.vline(W * 0.88, 0, H, 1.2), line)]
