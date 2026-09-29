"""L — Tranche. Une seule coupure horizontale dans le mot, le bas décalé et en cyan : l'image générée qui glisse d'un cran."""
import devices as dv
import geom as g
import textpath as tp
from directions.base import Direction, Font, Palette

FONT = ("InterTight[wght].ttf", {"wght": 900})


def slice_(path, y_cut, shift, gap):
    x0, y0, x1, y1 = path.bounds
    top = g.intersect(path, g.rect(x0 - 10, y_cut + gap / 2, x1 + 10, y1 + 10))
    bot = g.intersect(path, g.rect(x0 - 10, y0 - 10, x1 + 10, y_cut - gap / 2))
    return top, g.translate(bot, dx=shift)


class Tranche(Direction):
    code = "L"
    key = "tranche"
    name = "Tranche"
    idea = "Une seule coupure dans le mot, la moitié du bas glissée d'un cran et passée au cyan : l'image générée qui trahit sa fabrication."
    mark_type = "Wordmark tranché + lettre-symbole"
    why = [
        "Dit « image générée » sans les clichés du glitch (pas de bruit, pas de RVB baveux) : une seule coupe nette.",
        "Le décalage donne du mouvement au logo immobile ; en vidéo, la tranche glisse et revient.",
        "Grotesque très noir, très serré : lisible et sérieux, le détail fait le reste.",
    ]
    risk = "L'effet « tranché » est populaire depuis 2020 ; tenu à une seule coupe fine, il reste propre mais peu propriétaire."
    palette = Palette("#0F0F10", "#F4F4F2", "#00D2FF",
                      names={"ink": "Noir", "paper": "Blanc", "accent": "Cyan tranche"},
                      notes={"ink": "moitié haute, texte", "paper": "fonds", "accent": "moitié basse"})
    display = Font("Inter Tight", FONT[0], {"wght": 850})
    body = Font("Red Hat Display", "RedHatDisplay[wght].ttf", {"wght": 400})
    mono = Font("Chivo Mono", "ChivoMono[wght].ttf", {"wght": 500})
    version = "v2"

    def _cut(self, s):
        t, w = tp.text(s, FONT[0], 200, FONT[1], tracking=-0.035)
        m = tp.metrics(FONT[0], FONT[1])
        xh = m["x"] * 200 / m["upem"]
        return slice_(t, xh * 0.58, xh * 0.05, xh * 0.05)

    def wordmark(self):
        top, bot = self._cut("wubba")
        return [(top, "fg"), (bot, "accent")]

    def symbol(self):
        top, bot = self._cut("w")
        return [(top, "fg"), (bot, "accent")]

    def device(self, W, H, sch, fmt):
        from compose import mix
        faint = mix(sch["bg"], sch["accent"], 0.18)
        return [(dv.hline(0, W * 0.3, H * 0.44, 2), faint), (dv.hline(W * 0.7, W, H * 0.44, 2), faint)]
