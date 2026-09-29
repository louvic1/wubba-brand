"""Texte -> tracés vectoriels, avec HarfBuzz (mise en forme, crénage, axes variables) et pathops.

Sert aux bannières et aux wordmarks dérivés de polices : le SVG final ne dépend d'aucune police installée.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pathops
import uharfbuzz as hb

import geom as g

FONT_DIR = Path(__file__).resolve().parent.parent / ".fonts"


@lru_cache(maxsize=None)
def _face(file):
    blob = hb.Blob.from_file_path(str(FONT_DIR / file))
    return hb.Face(blob)


def _font(file, variations):
    font = hb.Font(_face(file))
    if variations:
        font.set_variations(dict(variations))
    return font


def text(s, file, size, variations=None, tracking=0.0, features=None, x=0.0, y=0.0):
    """Renvoie (tracé, largeur d'avance). y = ligne de base, coordonnées y vers le haut.

    tracking est en em (0.08 = +8 % de la taille), ajouté après chaque glyphe sauf le dernier.
    """
    variations = tuple(sorted((variations or {}).items()))
    font = _font(file, variations)
    upem = _face(file).upem
    buf = hb.Buffer()
    buf.add_str(s)
    buf.guess_segment_properties()
    hb.shape(font, buf, features or {"kern": True, "liga": True, "calt": True})
    scale = size / upem
    out = pathops.Path()
    pen_x = 0.0
    n = len(buf.glyph_infos)
    for i, (info, pos) in enumerate(zip(buf.glyph_infos, buf.glyph_positions)):
        gp = pathops.Path()
        font.draw_glyph_with_pen(info.codepoint, gp.getPen())
        gp = g.translate(gp, dx=x + pen_x + pos.x_offset * scale, dy=y + pos.y_offset * scale, sx=scale, sy=scale)
        out.addPath(gp)
        pen_x += pos.x_advance * scale
        if i < n - 1:
            pen_x += tracking * size
    out.simplify()  # retire les chevauchements des polices variables
    return out, pen_x


def glyphs(s, file, size, variations=None, tracking=0.0, features=None):
    """Comme text(), mais lettre par lettre : [(caractère, tracé, x, avance)]. Pour personnaliser un glyphe."""
    variations = tuple(sorted((variations or {}).items()))
    font = _font(file, variations)
    upem = _face(file).upem
    buf = hb.Buffer()
    buf.add_str(s)
    buf.guess_segment_properties()
    hb.shape(font, buf, features or {"kern": True, "liga": False})
    scale = size / upem
    out, pen_x = [], 0.0
    for i, (info, pos) in enumerate(zip(buf.glyph_infos, buf.glyph_positions)):
        gp = pathops.Path()
        font.draw_glyph_with_pen(info.codepoint, gp.getPen())
        gp = g.translate(gp, dx=pen_x + pos.x_offset * scale, dy=pos.y_offset * scale, sx=scale, sy=scale)
        gp.simplify()
        adv = pos.x_advance * scale
        out.append((s[info.cluster], gp, pen_x, adv))
        pen_x += adv + (tracking * size if i < len(buf.glyph_infos) - 1 else 0)
    return out


def metrics(file, variations=None):
    """Hauteur d'x, hauteur de capitale, ascendante et descendante, en unités de la police (upem)."""
    font = _font(file, tuple(sorted((variations or {}).items())))
    face = _face(file)

    def b(ch):
        gp = pathops.Path()
        font.draw_glyph_with_pen(font.get_nominal_glyph(ord(ch)), gp.getPen())
        return gp.bounds or (0, 0, 0, 0)
    return {"upem": face.upem, "x": b("x")[3], "cap": b("H")[3], "asc": b("b")[3], "desc": b("p")[1]}


def fit(s, file, width, variations=None, tracking=0.0):
    """Taille de police pour que la chaîne mesure exactement `width`."""
    _, w = text(s, file, 100, variations, tracking)
    return 100 * width / w
