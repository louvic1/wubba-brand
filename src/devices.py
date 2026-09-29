"""Motifs graphiques réutilisables pour les bannières (tout en tracés, coordonnées y-haut en pixels)."""
from __future__ import annotations

import math

import geom as g


def hud_corners(W, H, inset=40, length=46, thick=3):
    """Les quatre coins d'un viseur de caméra / d'un overlay de stream."""
    parts = []
    for sx, x in ((1, inset), (-1, W - inset)):
        for sy, y in ((1, inset), (-1, H - inset)):
            parts.append(g.rect(min(x, x + sx * length), min(y, y + sy * thick),
                                max(x, x + sx * length), max(y, y + sy * thick)))
            parts.append(g.rect(min(x, x + sx * thick), min(y, y + sy * length),
                                max(x, x + sx * thick), max(y, y + sy * length)))
    return g.union(*parts)


def cross_grid(W, H, step=100, size=10, thick=1.5, margin=0, keep=None):
    """Grille de repères de suivi (petites croix), comme sur un fond vert de tournage."""
    parts = []
    y = margin + step / 2
    while y < H - margin:
        x = margin + step / 2
        while x < W - margin:
            if keep is None or keep(x, y):
                parts.append(g.rect(x - size / 2, y - thick / 2, x + size / 2, y + thick / 2))
                parts.append(g.rect(x - thick / 2, y - size / 2, x + thick / 2, y + size / 2))
            x += step
        y += step
    return g.combine(*parts) if parts else None


def dot_matrix(W, H, step=14, r=1.6, keep=None):
    parts = []
    y = step / 2
    while y < H:
        x = step / 2
        while x < W:
            if keep is None or keep(x, y):
                parts.append(g.rect(x - r, y - r, x + r, y + r))
            x += step
        y += step
    return g.combine(*parts) if parts else None


def hline(x0, x1, y, thick=1.5):
    return g.rect(x0, y - thick / 2, x1, y + thick / 2)


def vline(x, y0, y1, thick=1.5):
    return g.rect(x - thick / 2, y0, x + thick / 2, y1)


def stripes(W, H, width=24, gap=24, angle=45, x0=0, x1=None):
    """Bandes obliques (danger / vitesse) limitées à [x0, x1]."""
    x1 = W if x1 is None else x1
    k = math.tan(math.radians(angle))
    parts = []
    x = x0 - H / k - width
    while x < x1 + width:
        parts.append(g.poly([(x, 0), (x + width, 0), (x + width + H / k, H), (x + H / k, H)]))
        x += width + gap
    return g.intersect(g.union(*parts), g.rect(x0, 0, x1, H))


def ring(cx, cy, r, thick):
    return g.diff(g.circle(cx, cy, r), g.circle(cx, cy, r - thick))


def wave(x0, x1, y, amp, period, thick, phase=0.0, steps=240):
    """Onde sinusoïdale épaisse, approximée par un polygone serré (utilisée comme motif, pas comme logo)."""
    top, bot = [], []
    for i in range(steps + 1):
        x = x0 + (x1 - x0) * i / steps
        yy = y + amp * math.sin(2 * math.pi * (x - x0) / period + phase)
        dydx = amp * 2 * math.pi / period * math.cos(2 * math.pi * (x - x0) / period + phase)
        n = math.hypot(1, dydx)
        ox, oy = -dydx / n * thick / 2, 1 / n * thick / 2
        top.append((x + ox, yy + oy))
        bot.append((x - ox, yy - oy))
    return g.poly(top + bot[::-1])


def checker(x0, y0, x1, y1, cell=16):
    parts = []
    j = 0
    y = y0
    while y < y1:
        i = 0
        x = x0
        while x < x1:
            if (i + j) % 2 == 0:
                parts.append(g.rect(x, y, min(x + cell, x1), min(y + cell, y1)))
            x += cell
            i += 1
        y += cell
        j += 1
    return g.combine(*parts)
