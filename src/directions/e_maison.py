"""E — Maison. Un logotype de maison de couture pour un studio de gamers IA : le déplacement appliqué à la marque elle-même."""
import devices as dv
import geom as g
import textpath as tp
from directions.base import Direction, Font, Palette

FONT = ("BodoniModa[opsz,wght].ttf", {"wght": 900, "opsz": 96})


class Maison(Direction):
    code = "E"
    key = "maison"
    name = "Maison"
    idea = "Un logotype de maison de couture pour un studio qui fait tester du matériel gaming : la marque est elle-même hors de son contexte."
    mark_type = "Logotype serif Didone + monogramme"
    why = [
        "Dans un secteur où tout le monde est noir néon et sans-serif, un Didone se remarque à 3 mètres.",
        "Signale « agence premium » à un directeur marketing avant la première ligne.",
        "L'outremer électrique empêche le cliché crème et terracotta des marques de luxe génériques.",
    ]
    risk = "Les déliés du Didone disparaissent sous 24 px : l'icône et le favicon utilisent une coupe plus grasse."
    palette = Palette("#0A0A0A", "#F7F6F2", "#2340FF",
                      names={"ink": "Noir", "paper": "Blanc cassé", "accent": "Outremer"},
                      notes={"ink": "logotype, texte", "paper": "fonds", "accent": "filets, liens, un détail"})
    display = Font("Bodoni Moda", FONT[0], {"wght": 800, "opsz": 96})
    body = Font("Epilogue", "Epilogue[wght].ttf", {"wght": 400})
    mono = Font("IBM Plex Mono", "IBMPlexMono-Medium.ttf", {})
    banner_scheme = "light"
    icon_scheme = "dark"
    tagline_mono = True
    version = "v2"

    def wordmark(self):
        t, _ = tp.text("wubba", FONT[0], 200, FONT[1], tracking=-0.025)
        return [(t, "fg")]

    def symbol(self, opsz=96):
        t, _ = tp.text("w", FONT[0], 200, {"wght": 900, "opsz": opsz})
        x0, y0, x1, y1 = t.bounds
        dot = g.rect(x1 + 10, 0, x1 + 34, 24)
        return [(t, "fg"), (dot, "accent")]

    def icon_symbol(self, small=False):
        # coupe optique « petit corps » : déliés plus épais, lisibles à 16 px
        return self.symbol(opsz=6 if small else 11)

    def device(self, W, H, sch, fmt):
        from compose import mix
        rule = mix(sch["bg"], sch["fg"], 0.85)
        inset = {"x-header": 40, "og": 40, "linkedin": 36, "linkedin-company": 20}[fmt]
        return [(dv.hline(inset, W - inset, H - inset, 2.0), sch["accent"]),
                (dv.hline(inset, W - inset, inset, 1.2), rule)]
