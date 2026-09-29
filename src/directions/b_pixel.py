"""B — Pixel mort. Lettrage sur grille de pixels ; un seul pixel coincé, magenta, là où il ne devrait pas être."""
import devices as dv
import geom as g
from directions.base import Direction, Font, Palette

# Grille : hauteur d'x 5 pixels, ascendantes 7. Rangée 0 = ligne de base. "#" = pixel, "*" = pixel mort.
GLYPHS = {
    "w": ["#.*.#",
          "#...#",
          "#.#.#",
          "#.#.#",
          ".#.#."],
    "u": ["#..#",
          "#..#",
          "#..#",
          "#..#",
          ".###"],
    "b": ["#...",
          "#...",
          "###.",
          "#..#",
          "#..#",
          "#..#",
          "###."],
    "a": [".##.",
          "...#",
          ".###",
          "#..#",
          ".###"],
}
CELL = 40


def pixels(glyph, x0, cell=CELL, dead_role="accent"):
    rows = GLYPHS[glyph]
    solid, dead = [], []
    n = len(rows)
    for r, row in enumerate(rows):
        y = (n - 1 - r) * cell
        for c, ch in enumerate(row):
            if ch == "#":
                solid.append(g.rect(x0 + c * cell, y, x0 + (c + 1) * cell, y + cell))
            elif ch == "*":
                dead.append(g.rect(x0 + c * cell, y, x0 + (c + 1) * cell, y + cell))
    return solid, dead, len(rows[0]) * cell


class Pixel(Direction):
    icon_hfactor = 1.0
    favicon_ratio = 0.625
    code = "B"
    key = "pixel"
    name = "Pixel mort"
    idea = "Le nom écrit en pixels, avec un seul pixel coincé en magenta : l'erreur d'écran que personne ne voit, sauf toi."
    mark_type = "Lettrage pixel sur mesure + lettre-symbole"
    why = [
        "Natif du jeu vidéo et de l'écran, sans tomber dans le rétro : grille stricte, pas de dégradé.",
        "Le pixel mort dit « généré » et « détail qui cloche » : ce que le studio fabrique.",
        "Parfait au pixel près en favicon (grille alignée sur 16, 24, 32, 48 px).",
    ]
    risk = "Le pixel art peut sembler « indie game » plutôt que studio B2B ; il faut une typo de texte très sobre pour compenser."
    palette = Palette("#0B0B0C", "#F2F2EE", "#FF2BD1",
                      names={"ink": "Écran", "paper": "Blanc", "accent": "Pixel mort"},
                      notes={"ink": "fond, lettres", "paper": "fonds clairs", "accent": "un seul pixel"})
    display = Font("Schibsted Grotesk", "SchibstedGrotesk[wght].ttf", {"wght": 900})
    body = Font("Inter", "Inter[opsz,wght].ttf", {"wght": 400, "opsz": 18})
    mono = Font("Silkscreen", "Silkscreen-Regular.ttf", {})
    tagline_scale = 1.3
    version = "v2"
    icon_ratio = 0.625
    icon_lift = 0.0

    def wordmark(self):
        x = 0
        solid, dead = [], []
        for ch in "wubba":
            s, d, w = pixels(ch, x)
            solid += s
            dead += d
            x += w + CELL
        return [(g.union(*solid), "fg"), (g.union(*dead), "accent")]

    def symbol(self):
        s, d, _ = pixels("w", 0)
        return [(g.union(*s), "fg"), (g.union(*d), "accent")]

    def device(self, W, H, sch, fmt):
        from compose import mix
        faint = mix(sch["bg"], sch["fg"], 0.10)
        step = 16 if H >= 390 else 12
        cx0, cx1 = W * 0.22, W * 0.78
        grid = dv.dot_matrix(W, H, step=step, r=1.4, keep=lambda x, y: x < cx0 or x > cx1)
        return [(grid, faint)] if grid else []
