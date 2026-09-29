"""Interface commune à toutes les directions d'identité.

Chaque direction fournit des calques (tracé, rôle). Les rôles sont traduits en couleurs par un schéma,
ce qui donne gratuitement les versions claire, sombre, monochromes et sur couleur d'accent.
Rôles : "fg" (lettres), "accent" (le détail signature), "fg2" (élément secondaire).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import geom as g
import svgout


@dataclass
class Font:
    family: str
    file: str
    var: dict = field(default_factory=dict)
    stack: str = "sans-serif"
    css_axes: str = ""          # fragment d'URL Google Fonts, ex. "wdth,wght@62..125,100..900"

    @property
    def gf_url(self):
        return "https://fonts.google.com/specimen/" + self.family.replace(" ", "+")


@dataclass
class Palette:
    ink: str
    paper: str
    accent: str
    accent2: str | None = None
    names: dict = field(default_factory=dict)   # noms français des couleurs
    notes: dict = field(default_factory=dict)   # rôle de chaque couleur
    custom: dict = field(default_factory=dict)  # schémas propres à la direction

    def scheme(self, kind):
        """Schémas nommés : light, dark, accent (fond d'accent), mono-black, mono-white, ou un schéma propre."""
        if kind in self.custom:
            return dict(self.custom[kind])
        a2 = self.accent2 or self.accent
        if kind == "light":
            return {"bg": self.paper, "fg": self.ink, "accent": self.accent, "fg2": a2}
        if kind == "dark":
            return {"bg": self.ink, "fg": self.paper, "accent": self.accent, "fg2": a2}
        if kind == "accent":
            return {"bg": self.accent, "fg": self.ink, "accent": self.paper, "fg2": self.paper}
        if kind == "mono-black":
            return {"bg": "#FFFFFF", "fg": "#000000", "accent": "#000000", "fg2": "#000000"}
        if kind == "mono-white":
            return {"bg": "#000000", "fg": "#FFFFFF", "accent": "#FFFFFF", "fg2": "#FFFFFF"}
        raise ValueError(kind)

    def chips(self):
        rows = [("ink", self.ink), ("paper", self.paper), ("accent", self.accent)]
        if self.accent2:
            rows.append(("accent2", self.accent2))
        return [(self.names.get(k, k), v, self.notes.get(k, "")) for k, v in rows]


class Direction:
    code = "?"
    key = "?"
    name = "?"
    idea = ""                  # une phrase
    mark_type = ""
    why = []                   # 2-3 raisons
    risk = ""                  # le risque honnête
    palette: Palette = None
    display: Font = None
    body: Font = None
    mono: Font = None
    banner_scheme = "dark"     # schéma par défaut des bannières
    tagline_mono = True        # la ligne en mono capitales (sinon : police de texte, casse normale)
    icon_scheme = "dark"       # tuile : fond encre par défaut
    icon_ratio = 0.64          # largeur du symbole dans la tuile
    icon_lift = 0.02           # remontée optique
    icon_hfactor = 0.9         # limite de hauteur relative (1.0 pour les symboles carrés)
    favicon_ratio = 0.74       # symbole plus grand aux tailles minuscules

    # -- à fournir par chaque direction
    def wordmark(self):
        raise NotImplementedError

    def symbol(self):
        raise NotImplementedError

    def symbol_small(self):
        return self.symbol()

    def icon_symbol(self, small=False):
        """Ce qui va dans la tuile d'icône (par défaut : le symbole)."""
        return self.symbol_small() if small else self.symbol()

    def device(self, W, H, scheme, fmt):
        """Motif graphique propre à la direction pour les bannières. Renvoie [(tracé, couleur)]."""
        return []

    # -- outils communs
    @staticmethod
    def color(layers, scheme):
        return [(p, scheme.get(role, scheme["fg"])) for p, role in layers]

    @staticmethod
    def bounds(layers):
        return svgout.union_bounds(*[p for p, _ in layers])

    @staticmethod
    def place(layers, box_target, align="center", valign="center"):
        """Met à l'échelle et place des calques dans une boîte (x0, y0, x1, y1), en coordonnées y-haut."""
        xmin, ymin, xmax, ymax = svgout.union_bounds(*[p for p, _ in layers])
        x0, y0, x1, y1 = box_target
        s = min((x1 - x0) / (xmax - xmin), (y1 - y0) / (ymax - ymin))
        w, h = (xmax - xmin) * s, (ymax - ymin) * s
        if align == "center":
            dx = x0 + (x1 - x0 - w) / 2
        elif align == "left":
            dx = x0
        else:
            dx = x1 - w
        if valign == "center":
            dy = y0 + (y1 - y0 - h) / 2
        elif valign == "bottom":
            dy = y0
        else:
            dy = y1 - h
        return [(g.translate(p, dx=dx - xmin * s, dy=dy - ymin * s, sx=s, sy=s), r) for p, r in layers], s
