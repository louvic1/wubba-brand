"""Écriture des fichiers SVG maîtres (tracés seulement, aucune police, aucun filtre)."""
from __future__ import annotations

import geom as g


def svg_doc(layers, box, title, pad=0.0, bg=None, width=None, height=None, rx=None):
    """layers : liste de (tracé, couleur). box : (xmin, ymin, xmax, ymax) en coordonnées y-haut.

    Le viewBox est calé sur la boîte + marge. Les coordonnées sont retournées (SVG y-bas).
    """
    xmin, ymin, xmax, ymax = box
    w = xmax - xmin + 2 * pad
    h = ymax - ymin + 2 * pad
    dx = -xmin + pad
    parts = []
    if bg:
        r = f' rx="{rx}"' if rx else ""
        parts.append(f'<rect width="{_n(w)}" height="{_n(h)}"{r} fill="{bg}"/>')
    for path, fill in layers:
        if path is None:
            continue
        d = g.to_d(path, ymax + pad, dx=dx)
        parts.append(f'<path fill="{fill}" d="{d}"/>')
    size = ""
    if width:
        size += f' width="{_n(width)}"'
    if height:
        size += f' height="{_n(height)}"'
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {_n(w)} {_n(h)}"{size} role="img" '
        f'aria-labelledby="t"><title id="t">{title}</title>' + "".join(parts) + "</svg>\n"
    )


def union_bounds(*paths):
    ps = [p for p in paths if p is not None]
    return g.bounds(g.union(*ps))


def _n(v):
    s = f"{round(v, 2):.2f}".rstrip("0").rstrip(".")
    return s or "0"
