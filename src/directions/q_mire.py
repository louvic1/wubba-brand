"""Q — Mire. La mire de test des chaînes de télé : sept barres de couleur, un cercle, et le w au centre. Ici, c'est le matériel qui passe le test."""
import geom as g
import textpath as tp
from directions.base import Direction, Font, Palette

FONT = ("Unbounded[wght].ttf", {"wght": 700})
# les sept barres, retendues : moins criardes que la norme, mêmes teintes et même ordre
BARS = ["#D9D9D5", "#F2D22E", "#2EC4D6", "#3CC45A", "#D23CA8", "#E0362F", "#2F4FD8"]


def bar_color(i, bg, fg="#0E0E10"):
    """Une barre identique au fond (le jaune sur le jaune) passe à mi-chemin de l'encre ;
    la barre grise fonce d'un cran sur fond clair. Les autres gardent leur teinte : c'est la mire."""
    import palette as pal
    from compose import mix
    c = BARS[i]
    k = pal.contrast(c, bg)
    if k < 1.08:
        return mix(c, fg, 0.55)
    if i == 0 and k < 1.35:
        return mix(c, "#000000", 0.25)
    return c


def bars(x0, y0, x1, y1):
    w = (x1 - x0) / 7
    return [(g.rect(x0 + i * w, y0, x0 + (i + 1) * w + (0.5 if i < 6 else 0), y1), f"b{i}") for i in range(7)]


class Mire(Direction):
    code = "Q"
    key = "mire"
    name = "Mire"
    idea = "La mire de test des chaînes de télé : sept barres de couleur, un cercle, le w au centre. Ici, c'est le matériel qui passe le test."
    mark_type = "Wordmark + barre de mire, symbole mire ronde"
    why = [
        "« Test » dit par l'image la plus connue du monde de la diffusion : personne n'a besoin d'explication.",
        "La mire est un objet de diffusion, pas de gaming : elle place le studio du côté de l'émission, pas de la manette.",
        "Les sept barres forment un code couleur prêt à l'emploi : une barre par série de tests, par plateforme ou par format.",
    ]
    risk = "La mire parle « rétro télé » à tout le monde : c'est sa force et sa limite. Sept couleurs demandent une discipline stricte hors du logo."
    palette = Palette("#0E0E10", "#F3F2EE", "#F2D22E", accent2="#2F4FD8",
                      names={"ink": "Écran éteint", "paper": "Blanc de mire", "accent": "Jaune de barre",
                             "accent2": "Bleu de barre"},
                      notes={"ink": "fonds, texte", "paper": "fonds clairs, centre de la mire",
                             "accent": "un accent par visuel", "accent2": "liens, états"})
    display = Font("Unbounded", "Unbounded[wght].ttf", {"wght": 700})
    body = Font("Onest", "Onest[wght].ttf", {"wght": 400})
    mono = Font("Space Mono", "SpaceMono-Bold.ttf", {})
    icon_ratio = 0.80
    icon_hfactor = 1.0
    favicon_ratio = 0.86
    giant_full_color = True
    version = "v2"

    def wordmark(self):
        t, w = tp.text("wubba", FONT[0], 200, FONT[1], tracking=-0.01)
        x0, y0, x1, y1 = t.bounds
        m = tp.metrics(FONT[0], FONT[1])
        xh = m["x"] * 200 / m["upem"]
        h = xh * 0.2
        gap = xh * 0.16
        return [(t, "fg")] + bars(x0, y0 - gap - h, x1, y0 - gap)

    def _card(self, R=150, disc=0.56, wsize=None, ring=0.07):
        """La mire ronde : barres dans un cercle, un disque central, le w dedans, un filet autour."""
        outer = g.circle(0, 0, R)
        inner = g.circle(0, 0, R * (1 - ring))
        layers = [(g.diff(outer, inner), "fg")]
        layers += [(g.intersect(p, inner), role) for p, role in bars(-R, -R, R, R)]
        layers.append((g.circle(0, 0, R * disc), "disc"))
        t, _ = tp.text("w", FONT[0], wsize or R * 0.92, FONT[1])
        x0, y0, x1, y1 = t.bounds
        layers.append((g.translate(t, dx=-(x0 + x1) / 2, dy=-(y0 + y1) / 2), "wmark"))
        return layers

    def symbol(self):
        return self._card()

    def symbol_small(self):
        return self._card(disc=0.62, wsize=150 * 1.08, ring=0.09)

    @staticmethod
    def color(layers, scheme):
        fg, bg = scheme["fg"], scheme["bg"]
        mono = fg.upper() in ("#000000", "#FFFFFF") and scheme["accent"].upper() in ("#000000", "#FFFFFF")
        out = []
        for p, role in layers:
            if role.startswith("b") and role[1:].isdigit():
                i = int(role[1:])
                c = (fg if i % 2 == 0 else bg) if mono else bar_color(i, bg, fg)
            elif role == "disc":
                c = bg if mono else "#F3F2EE"
            elif role == "wmark":
                c = fg if mono else "#0E0E10"
            else:
                c = scheme.get(role, fg)
            out.append((p, c))
        return out

    def device(self, W, H, sch, fmt):
        """La grille de la mire, très discrète, sur toute la bannière."""
        from compose import mix
        if fmt == "linkedin-company":
            return []
        line = mix(sch["bg"], sch["fg"], 0.10)
        step = 50 if H >= 400 else 40
        parts = []
        x = (W % step) / 2
        while x <= W:
            parts.append(g.rect(x - 0.75, 0, x + 0.75, H))
            x += step
        y = (H % step) / 2
        while y <= H:
            parts.append(g.rect(0, y - 0.75, W, y + 0.75))
            y += step
        return [(g.combine(*parts), line)]

    def banner_layout(self, fmt, W, H, sch, layout=None):
        """Mire ronde et nom côte à côte, sur la grille ; les sept barres courent en pied de bannière."""
        if layout is not None:
            return None
        from compose import TAGLINE, DOMAIN, mix, page, text_line
        muted = mix(sch["fg"], sch["bg"], 0.30)
        layers = list(self.device(W, H, sch, fmt))
        band = {"x-header": 14, "og": 16, "linkedin": 12, "linkedin-company": 8}[fmt]
        layers += self.color(bars(0, 0, W, band), sch)
        card = self.symbol()
        wm = [(p, r) for p, r in self.wordmark()]
        if fmt == "x-header":
            cbox, wbox = (300, 170, 560, 430), (610, 250, 1210, 370)
        elif fmt == "og":
            cbox, wbox = (W / 2 - 150, 300, W / 2 + 150, 600), (W / 2 - 300, 130, W / 2 + 300, 250)
        elif fmt == "linkedin":
            cbox, wbox = (W - 820, 110, W - 600, 330), (W - 560, 175, W - 110, 265)
        else:
            cbox, wbox = (W - 520, 30, W - 390, 160), (W - 360, 70, W - 70, 124)
        cp, _ = self.place(card, cbox)
        wp, _ = self.place(wm, wbox, align="left" if fmt != "og" else "center")
        # un disque de fond derrière la mire, pour qu'elle se détache de la grille
        x0, y0, x1, y1 = self.bounds(cp)
        layers.append((g.circle((x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2 + 10), sch["bg"]))
        layers += self.color(cp, sch) + self.color(wp, sch)
        wb = self.bounds(wp)
        if fmt in ("x-header", "og"):
            size = 16 if fmt == "x-header" else 17
            ax = wb[0] if fmt == "x-header" else W / 2
            (tp_, c), _, _ = text_line(TAGLINE, self.mono, size, ax, wb[1] - 48, muted, "left" if fmt == "x-header" else "center",
                                      True, 0.02, max_w=(wb[2] - wb[0]) * (1.0 if fmt == "x-header" else 1.6))
            x0, y0, x1, y1 = tp_.bounds
            layers.append((g.rect(x0 - 8, y0 - 8, x1 + 8, y1 + 8), sch["bg"]))
            layers.append((tp_, c))
            dx, dy, al = (W - 76, H - 64, "right") if fmt == "x-header" else (76, H - 64, "left")
            (dp, c), _, _ = text_line(DOMAIN, self.mono, 15, dx, dy, sch["fg"], al, False, 0.02)
            x0, y0, x1, y1 = dp.bounds
            layers.append((g.rect(x0 - 8, y0 - 8, x1 + 8, y1 + 8), sch["bg"]))
            layers.append((dp, c))
        return page(W, H, layers, bg=sch["bg"])
