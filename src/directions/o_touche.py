"""O — Touche W. Le nom tapé sur cinq touches de clavier ; la touche W, celle qui fait avancer dans tous les FPS, est en couleur."""
import devices as dv
import geom as g
import textpath as tp
from directions.base import Direction, Font, Palette

LEGEND = ("Rubik[wght].ttf", {"wght": 600})
JB_MONO = "JetBrainsMono[wght].ttf"
U = 200          # une touche


def keycap(x, letter, legend_size=0.40, y=0.0):
    """Une touche vue de face, un peu d'en haut : jupe, dessus décalé vers le haut, légende centrée."""
    skirt = g.rounded_rect(x, y, x + U, y + U, U * 0.16, smooth=0.5)
    top = g.rounded_rect(x + U * 0.13, y + U * 0.21, x + U * 0.87, y + U * 0.92, U * 0.11, smooth=0.5)
    t, w = tp.text(letter, LEGEND[0], U * legend_size, {"wght": 700} if legend_size > 0.45 else LEGEND[1])
    x0, y0, x1, y1 = t.bounds
    cx, cy = x + U / 2, y + U * 0.565
    legend = g.translate(t, dx=cx - (x0 + x1) / 2, dy=cy - (y0 + y1) / 2)
    return skirt, g.diff(top, legend), legend


class Touche(Direction):
    code = "O"
    key = "touche"
    name = "Touche W"
    idea = "Le nom tapé sur cinq touches de clavier. La touche W est en couleur : dans tous les jeux de tir, W, c'est avancer."
    mark_type = "Logotype en touches + symbole touche"
    why = [
        "Natif du jeu sans le moindre cliché visuel : pas de néon, pas de flamme, juste la touche la plus usée du clavier.",
        "Le W coloré est à la fois l'initiale et la commande « avancer » : une idée, deux lectures.",
        "L'icône est un objet réel que chaque joueur a sous les doigts ; elle se décline en goodies (keycap artisan).",
    ]
    risk = "Le relief de touche demande trois tons ; en une couleur il faut la version au trait (livrée)."
    palette = Palette("#141518", "#ECEAE6", "#A98BFF", accent2="#2A2C31",
                      names={"ink": "Châssis", "paper": "Touche claire", "accent": "Touche W", "accent2": "Touche sombre"},
                      notes={"ink": "fonds, légendes", "paper": "touches, fonds clairs", "accent": "la touche W",
                             "accent2": "touches sur fond sombre"})
    display = Font("Rubik", "Rubik[wght].ttf", {"wght": 700})
    body = Font("Lexend", "Lexend[wght].ttf", {"wght": 400})
    mono = Font("JetBrains Mono", "JetBrainsMono[wght].ttf", {"wght": 500})

    def _keys(self, letters):
        layers = []
        for i, ch in enumerate(letters):
            skirt, top, legend = keycap(i * U * 1.08, ch)
            k = "a" if ch == "W" else "k"
            layers += [(skirt, k + "skirt"), (top, k + "top"), (legend, k + "legend")]
        return layers

    def wordmark(self):
        return self._keys("WUBBA")

    def symbol(self):
        return self._keys("W")

    def symbol_small(self):
        skirt, top, legend = keycap(0, "W", legend_size=0.56)
        return [(skirt, "askirt"), (top, "atop"), (legend, "alegend")]

    @staticmethod
    def color(layers, scheme):
        from compose import mix
        bg, fg, acc = scheme["bg"], scheme["fg"], scheme["accent"]
        mono = acc.upper() in ("#000000", "#FFFFFF") and fg.upper() in ("#000000", "#FFFFFF")
        lum = lambda c: sum(int(c.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))  # noqa: E731
        dark_bg = lum(bg) < 3 * 110
        if mono:
            m = {"kskirt": fg, "ktop": bg, "klegend": fg, "askirt": fg, "atop": fg, "alegend": bg}
        elif not dark_bg and lum(acc) > lum(bg):
            # sur le fond d'accent, l'accent devient le papier : la touche W passe en encre pour rester celle qu'on voit
            m = {"kskirt": mix(bg, fg, 0.22), "ktop": mix(bg, "#FFFFFF", 0.55), "klegend": fg,
                 "askirt": mix(fg, "#000000", 0.3), "atop": fg, "alegend": bg}
        elif dark_bg:
            key = scheme.get("fg2") if scheme.get("fg2") not in (None, acc) else mix(bg, fg, 0.14)
            m = {"kskirt": mix(key, "#000000", 0.35), "ktop": key, "klegend": fg,
                 "askirt": mix(acc, "#000000", 0.30), "atop": acc, "alegend": bg}
        else:
            m = {"kskirt": mix(bg, fg, 0.22), "ktop": mix(bg, "#FFFFFF", 0.55), "klegend": fg,
                 "askirt": mix(acc, "#000000", 0.25), "atop": acc, "alegend": fg}
        return [(p, m.get(role, scheme.get(role, fg))) for p, role in layers]

    version = "v2"
    giant_full_color = True

    def wasd(self, cx, cy, size):
        """La grappe WASD centrée sur (cx, cy) : W en couleur, A S D en touches normales. size = largeur d'une touche."""
        k = size / U
        layers = []
        for letter, col, row in (("W", 1.08, 1.08), ("A", 0, 0), ("S", 1.08, 0), ("D", 2.16, 0)):
            role = "a" if letter == "W" else "k"
            for p, part in zip(keycap(col * U, letter, y=row * U), ("skirt", "top", "legend")):
                layers.append((g.translate(p, dx=cx - 1.58 * U * k, dy=cy - 1.04 * U * k, sx=k, sy=k), role + part))
        return layers

    def keyboard(self, x0, y_top, s, sch, lit="WASD", max_x=None):
        """Un clavier fantôme au trait (rangées chiffres à Z, décalages réels) ; les touches de `lit` sont pleines.
        x0 = bord gauche de la touche Q, y_top = haut de la rangée des chiffres, s = taille d'une touche.
        max_x coupe le clavier à la dernière touche entière avant cette abscisse."""
        from compose import mix
        line = mix(sch["bg"], sch["fg"], 0.16)
        ink = mix(sch["bg"], sch["fg"], 0.26)
        pitch = s * 1.08
        rows = (("`1234567890-=", -1.5, [], [("delete", 2.0)]),
                ("QWERTYUIOP[]", 0.0, [("tab", 1.5)], [("\\", 1.5)]),
                ("ASDFGHJKL;'", 0.25, [("caps", 1.75)], [("return", 2.25)]),
                ("ZXCVBNM,./", 0.75, [("shift", 2.25)], [("shift", 2.75)]))
        k = s / U
        ghosts, legends, solid = [], [], []
        for r, (keys, off, left, right) in enumerate(rows):
            y = y_top - s - r * pitch
            cells = []
            x = x0 + off * pitch
            for lab, w in reversed(left):
                x -= w * pitch
                cells.append((x, lab, w))
            x = x0 + off * pitch
            for ch in keys:
                cells.append((x, ch, 1.0))
                x += pitch
            for lab, w in right:
                cells.append((x, lab, w))
                x += w * pitch
            for cx, lab, w in cells:
                if max_x is not None and cx + s + (w - 1) * pitch > max_x:
                    continue
                if lab in lit:
                    role = "a" if lab == "W" else "k"
                    for p, part in zip(keycap(0, lab, legend_size=0.46), ("skirt", "top", "legend")):
                        solid.append((g.translate(p, dx=cx, dy=y, sx=k, sy=k), role + part))
                    continue
                kw = s + (w - 1) * pitch
                rr = g.rounded_rect(cx, y, cx + kw, y + s, s * 0.16, smooth=0.5)
                ghosts.append(g.diff(rr, g.offset_stroke(rr, -max(1.6, s * 0.022))))
                small = len(lab) > 1
                t, _ = tp.text(lab, JB_MONO if small else LEGEND[0], s * (0.17 if small else 0.30),
                               {"wght": 500} if small else LEGEND[1])
                bx0, by0, bx1, by1 = t.bounds
                legends.append(g.translate(t, dx=cx + s * 0.16 - bx0 if small else cx + kw / 2 - (bx0 + bx1) / 2,
                                           dy=y + s * 0.5 - (by0 + by1) / 2))
        return [(g.combine(*ghosts), line), (g.combine(*legends), ink)] + self.color(solid, sch)

    def banner_layout(self, fmt, W, H, sch, layout=None):
        """Le nom en touches, et le clavier fantôme où seule la grappe WASD est allumée."""
        if layout is not None or fmt == "linkedin-company":
            return None
        from compose import TAGLINE, DOMAIN, mix, page, text_line
        muted = mix(sch["fg"], sch["bg"], 0.32)
        layers = []
        wm = self.wordmark()
        if fmt == "x-header":
            layers += self.keyboard(W * 0.60, H * 0.78, 90, sch)
            wmp, _ = self.place(wm, (100, 270, 700, 380), align="left")
            wb = self.bounds(wmp)
            layers += self.color(wmp, sch)
            tl, _, _ = text_line(TAGLINE, self.mono, 16, wb[0], wb[1] - 52, muted, "left", True, 0.05, max_w=600)
            dom, _, _ = text_line(DOMAIN, self.mono, 15, W - 76, H - 70, muted, "right", False, 0.04)
            layers += [tl, dom]
        elif fmt == "og":
            layers += self.keyboard(W / 2 - 1.25 * 92 * 1.08 - 92 / 2, 350, 92, sch)
            wmp, _ = self.place(wm, (W / 2 - 280, 440, W / 2 + 280, 545))
            wb = self.bounds(wmp)
            layers += self.color(wmp, sch)
            tl, _, _ = text_line(TAGLINE, self.mono, 16, W / 2, wb[1] - 46, muted, "center", True, 0.05, max_w=1000)
            dom, _, _ = text_line(DOMAIN, self.mono, 17, 76, H - 64, sch["fg"], "left", False, 0.04)
            layers += [tl, dom]
        else:  # linkedin
            layers += self.keyboard(470, H * 0.86, 80, sch, max_x=860)
            wmp, _ = self.place(wm, (W - 640, 200, W - 90, 300), align="right")
            wb = self.bounds(wmp)
            layers += self.color(wmp, sch)
            tl, _, _ = text_line(TAGLINE, self.mono, 14, W - 90, wb[1] - 44, muted, "right", True, 0.05, max_w=620)
            layers += [tl]
        return page(W, H, layers, bg=sch["bg"])

    def device(self, W, H, sch, fmt):
        from compose import mix
        faint = mix(sch["bg"], sch["fg"], 0.06)
        if fmt == "linkedin-company":
            return []
        s = H * 0.16
        parts = []
        for row in range(4):
            for col in range(6):
                x = W * 0.03 + col * s * 1.1 + (row % 2) * s * 0.3
                y = H * 0.12 + row * s * 1.1
                parts.append(g.diff(g.rounded_rect(x, y, x + s, y + s, s * 0.18, smooth=0.4),
                                    g.rounded_rect(x + 3, y + 3, x + s - 3, y + s - 3, s * 0.15, smooth=0.4)))
        return [(g.combine(*parts), faint)]
