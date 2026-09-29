"""Palette Wubba : source unique des couleurs.

Trois couleurs de marque (Encre, Papier, Signal), deux échelles de neutres interpolées en OKLab
entre l'encre et le papier (le froid de l'encre glisse vers le chaud du papier), et quelques
couleurs d'état pour le site. Tous les contrastes sont calculés ici, pas estimés.
"""
from __future__ import annotations

import math

# ------------------------------------------------------------------ couleurs de marque
INK = "#0E0F12"      # Encre   : primaire
PAPER = "#F1F0EC"    # Papier  : secondaire
SIGNAL = "#FF2A36"   # Signal  : accent, le point


# ------------------------------------------------------------------ conversions

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#" + "".join(f"{max(0, min(255, round(c * 255))):02X}" for c in rgb)


def _lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _gam(c):
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def to_oklab(h):
    r, g, b = (_lin(c) for c in hex_to_rgb(h))
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = (v ** (1 / 3) for v in (l, m, s))
    return (0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
            1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
            0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_)


def from_oklab(L, a, b):
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    r = 4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    bb = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    return rgb_to_hex(tuple(_gam(max(0.0, min(1.0, c))) for c in (r, g, bb)))


def oklch(h):
    L, a, b = to_oklab(h)
    return L, math.hypot(a, b), (math.degrees(math.atan2(b, a)) + 360) % 360


def from_oklch(L, C, H):
    return from_oklab(L, C * math.cos(math.radians(H)), C * math.sin(math.radians(H)))


def luminance(h):
    r, g, b = (_lin(c) for c in hex_to_rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


# ------------------------------------------------------------------ échelle des neutres

# Clarté OKLab visée par cran. 950 = l'encre, 100 = le papier.
STEPS = {950: None, 900: 0.215, 850: 0.255, 800: 0.30, 700: 0.385, 600: 0.475,
         500: 0.575, 400: 0.68, 300: 0.80, 200: 0.885, 150: 0.925, 100: None, 50: 0.985}


def neutral_scale():
    Li, ai, bi = to_oklab(INK)
    Lp, ap, bp = to_oklab(PAPER)
    out = {}
    for step, L in STEPS.items():
        if step == 950:
            out[step] = INK
            continue
        if step == 100:
            out[step] = PAPER
            continue
        t = (L - Li) / (Lp - Li)
        out[step] = from_oklab(L, ai + (ap - ai) * t, bi + (bp - bi) * t)
    return out


NEUTRAL = neutral_scale()

# ------------------------------------------------------------------ signal et états
_Ls, _Cs, _Hs = oklch(SIGNAL)
SIGNAL_SCALE = {
    50: from_oklch(0.975, 0.018, _Hs),
    100: from_oklch(0.94, 0.045, _Hs),
    300: from_oklch(0.78, 0.14, _Hs),
    500: SIGNAL,
    600: "#D4101E",   # rouge pour du texte sur fond clair (contraste >= 4.5)
    800: from_oklch(0.38, 0.14, _Hs),
    900: from_oklch(0.25, 0.08, _Hs),
}

# États pour l'interface (site, documents). Même clarté et même chroma que le signal,
# pour qu'aucun ne crie plus fort que lui.
STATE = {
    "positive": from_oklch(0.70, 0.16, 152),
    "caution": from_oklch(0.80, 0.15, 78),
    "info": from_oklch(0.64, 0.15, 255),
}


def darken_for_text(h, bg=PAPER, target=4.6):
    """Baisse la clarté OKLCH jusqu'à atteindre le contraste voulu sur le fond donné."""
    L, C, H = oklch(h)
    while contrast(h, bg) < target and L > 0.05:
        L -= 0.01
        h = from_oklch(L, C, H)
    return h


STATE_TEXT = {k: darken_for_text(v) for k, v in STATE.items()}


def tokens():
    """Rôles sémantiques, clair et sombre. C'est ce que le site et les documents consomment."""
    n = NEUTRAL
    return {
        "light": {
            "bg": n[100], "surface": n[50], "surface-2": n[150], "line": n[200], "line-strong": n[300],
            "text": INK, "text-muted": n[600], "text-faint": n[500],
            "accent": SIGNAL, "accent-text": SIGNAL_SCALE[600], "accent-tint": SIGNAL_SCALE[50],
            "on-accent": INK,
        },
        "dark": {
            "bg": INK, "surface": n[900], "surface-2": n[850], "line": n[800], "line-strong": n[700],
            "text": PAPER, "text-muted": n[400], "text-faint": n[500],
            "accent": SIGNAL, "accent-text": SIGNAL, "accent-tint": SIGNAL_SCALE[900],
            "on-accent": INK,
        },
    }


if __name__ == "__main__":
    print("neutres")
    for k, v in NEUTRAL.items():
        print(f"  {k:>4} {v}  vs encre {contrast(v, INK):5.2f}  vs papier {contrast(v, PAPER):5.2f}")
    print("signal")
    for k, v in SIGNAL_SCALE.items():
        print(f"  {k:>4} {v}  vs encre {contrast(v, INK):5.2f}  vs papier {contrast(v, PAPER):5.2f}  vs blanc {contrast(v, '#FFFFFF'):5.2f}")
    print("états")
    for k, v in STATE.items():
        print(f"  {k:>9} {v}  vs encre {contrast(v, INK):5.2f}  vs papier {contrast(v, PAPER):5.2f}")
    for k, v in STATE_TEXT.items():
        print(f"  {k+'-text':>9} {v}  vs papier {contrast(v, PAPER):5.2f}")
    print("paires clés")
    for a, b, lab in [(PAPER, INK, "papier / encre"), (SIGNAL, INK, "signal / encre"), (SIGNAL, PAPER, "signal / papier"),
                      (INK, SIGNAL, "encre sur signal"), (NEUTRAL[600], PAPER, "texte discret clair"),
                      (NEUTRAL[400], INK, "texte discret sombre")]:
        print(f"  {lab:<22} {contrast(a, b):5.2f}")
