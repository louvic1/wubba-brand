"""C — Incrustation. Une plaque de fond vert dont le nom est découpé : derrière les lettres, n'importe quel décor."""
import devices as dv
import geom as g
import textpath as tp
from directions.base import Direction, Font, Palette

FONT = ("Anybody[wdth,wght].ttf", {"wght": 850, "wdth": 118})


class Incrust(Direction):
    code = "C"
    key = "incrust"
    name = "Incrustation"
    idea = "Le nom découpé dans une plaque de fond vert : ce qui apparaît dans les lettres dépend de l'endroit où on la pose."
    mark_type = "Wordmark en réserve dans une plaque + symbole plaque"
    why = [
        "C'est le métier en une image : incruster quelqu'un là où il n'est pas.",
        "Le vert d'incrustation est une norme de tournage (#00B140), pas une couleur de mode.",
        "La réserve fait que le logo prend la couleur du support : photo, vidéo, fond de marque.",
    ]
    risk = "Vert + noir évoque Razer ou Spotify au premier coup d'œil ; le vert d'incrustation est plus bleuté, mais il faut le tenir exactement."
    palette = Palette("#0C120F", "#F2F4F1", "#00B140", accent2="#0047BB",
                      names={"ink": "Studio", "paper": "Blanc", "accent": "Fond vert", "accent2": "Fond bleu"},
                      notes={"ink": "texte, fonds", "paper": "fonds clairs", "accent": "la plaque",
                             "accent2": "rare : second plan"})
    display = Font("Anybody", "Anybody[wdth,wght].ttf", {"wght": 800, "wdth": 118})
    body = Font("Hanken Grotesk", "HankenGrotesk[wght].ttf", {"wght": 400})
    mono = Font("DM Mono", "DMMono-Medium.ttf", {})
    banner_scheme = "accent"
    icon_scheme = "accent"
    version = "v2"

    def _plate(self, word, pad_x=0.26, pad_y=0.34, radius=0.06):
        t, w = tp.text(word, FONT[0], 200, FONT[1], tracking=-0.01)
        x0, y0, x1, y1 = t.bounds
        m = tp.metrics(FONT[0], FONT[1])
        xh = m["x"] * 200 / m["upem"]
        asc = m["asc"] * 200 / m["upem"]
        h = asc + 2 * pad_y * xh
        plate = g.rounded_rect(x0 - pad_x * xh, -pad_y * xh, x1 + pad_x * xh, asc + pad_y * xh, h * radius, smooth=0.3)
        return g.diff(plate, t)

    def wordmark(self):
        return [(self._plate("wubba"), "accent")]

    def symbol(self):
        t, w = tp.text("w", FONT[0], 200, FONT[1])
        x0, y0, x1, y1 = t.bounds
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        half = max(x1 - x0, y1 - y0) / 2 + 42
        plate = g.rounded_rect(cx - half, cy - half, cx + half, cy + half, half * 0.18, smooth=0.3)
        return [(g.diff(plate, t), "accent")]

    def icon_symbol(self, small=False):
        t, _ = tp.text("w", FONT[0], 200, FONT[1])
        return [(t, "fg")]

    def device(self, W, H, sch, fmt):
        from compose import mix
        marks = mix(sch["bg"], "#000000", 0.28)
        step = 110 if H >= 390 else 70
        cx0, cx1 = W * 0.2, W * 0.8
        grid = dv.cross_grid(W, H, step=step, size=16 if H >= 390 else 11, thick=3 if H >= 390 else 2,
                             keep=lambda x, y: (x < cx0 or x > cx1) and y > (100 if H >= 390 else 0))
        return [(grid, marks)] if grid else []
