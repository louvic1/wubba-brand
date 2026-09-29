"""F — Bulle. Lettres rondes et pleines ; les deux b deviennent des yeux qui regardent de côté, impassibles."""
import devices as dv
import geom as g
import textpath as tp
from directions.base import Direction, Font, Palette

FONT = ("Fredoka[wdth,wght].ttf", {"wght": 700, "wdth": 112})


class Bulle(Direction):
    code = "F"
    key = "bulle"
    name = "Bulle"
    idea = "Un mot rond comme son nom ; les deux b ont des pupilles et regardent de côté, l'air de rien. Le deadpan a un visage."
    mark_type = "Wordmark-personnage + symbole (les yeux)"
    why = [
        "« wubba » sonne rond et drôle : cette direction l'assume au lieu de le cacher.",
        "Les yeux de côté font un personnage sans dessiner de mascotte ; il peut s'animer en vidéo.",
        "Violet et lime sortent complètement du noir-rouge-vert du matériel gaming.",
    ]
    risk = "Le plus joueur de tous : il peut faire « app pour ados » face à un directeur marketing."
    palette = Palette("#15122A", "#F4F1FF", "#7B5CFF", accent2="#C8FF3A",
                      names={"ink": "Nuit violette", "paper": "Lilas", "accent": "Violet", "accent2": "Lime"},
                      notes={"ink": "texte", "paper": "fonds clairs", "accent": "fonds, pupilles", "accent2": "détails"},
                      custom={"banner": {"bg": "#7B5CFF", "fg": "#F4F1FF", "accent": "#15122A", "fg2": "#C8FF3A"}})
    display = Font("Fredoka", FONT[0], {"wght": 600, "wdth": 110})
    body = Font("Nunito", "Nunito[wght].ttf", {"wght": 500})
    mono = Font("Space Mono", "SpaceMono-Regular.ttf", {})
    banner_scheme = "banner"
    tagline_mono = False
    tagline_role = "fg2"
    tagline_scale = 1.1
    version = "v2"

    def _word(self, word):
        gl = tp.glyphs(word, FONT[0], 200, FONT[1], tracking=-0.01)
        m = tp.metrics(FONT[0], FONT[1])
        xh = m["x"] * 200 / m["upem"]
        letters, pupils = [], []
        for ch, p, x, adv in gl:
            letters.append(p)
            if ch == "b":
                pupils.append(self._pupil(p))
        return g.union(*letters), g.union(*pupils) if pupils else None

    @staticmethod
    def _pupil(glyph):
        """Pupille inscrite dans la contreforme du b, collée côté droit : le regard de côté."""
        contours = list(glyph.contours)
        counter = min(contours, key=lambda c: (c.bounds[2] - c.bounds[0]) * (c.bounds[3] - c.bounds[1]))
        cx0, cy0, cx1, cy1 = counter.bounds
        ch, cw = cy1 - cy0, cx1 - cx0
        r = min(ch, cw) * 0.30
        y = (cy0 + cy1) / 2
        x = cx1 - r - min(ch, cw) * 0.12
        pupil = g.circle(x, y, r)
        while abs(g.intersect(pupil, glyph).area) > 0.5 and r > 2:   # jamais au contact de la lettre
            r *= 0.95
            x = cx1 - r - min(ch, cw) * 0.12
            pupil = g.circle(x, y, r)
        return pupil

    def wordmark(self):
        w, eyes = self._word("wubba")
        return [(w, "fg"), (eyes, "accent")]

    def symbol(self):
        w, eyes = self._word("bb")
        return [(w, "fg"), (eyes, "accent")]

    def device(self, W, H, sch, fmt):
        from compose import mix
        blob = mix(sch["bg"], sch["fg"], 0.10)
        if fmt == "linkedin-company":
            return []
        R = H * 0.9
        return [(g.circle(W * 0.06, -R * 0.35, R), blob), (g.circle(W * 0.98, H * 1.05, R * 0.7), blob)]
