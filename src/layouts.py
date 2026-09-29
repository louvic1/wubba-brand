"""Mises en page alternatives des bannières, génériques pour toutes les directions.

X (1500 x 500) : carton, géant, clair, manchette.
Aperçu de lien (1200 x 630) : centre, gauche, accent, symbole.

    python3 src/layouts.py A D H E F J
"""
from __future__ import annotations

import sys

import compose
import geom as g
from compose import DOMAIN, TAGLINE, mix, page, text_line
from directions import BY_CODE


def _tag(d):
    return (d.mono, True, 0.06) if d.tagline_mono else (d.body, False, 0.0)


def x_layout(d, name):
    W, H = 1500, 500
    if name == "carton":
        return compose.banner(d, "x-header")
    if name == "clair":
        return compose.banner(d, "x-header", "light")
    sch = d.palette.scheme(d.banner_scheme)
    muted = sch[d.tagline_role] if d.tagline_role else mix(sch["fg"], sch["bg"], 0.32)
    font, upper, track = _tag(d)
    layers = []
    if name == "geant":
        faint = mix(sch["bg"], sch["fg"], 0.09)
        sym = d.symbol()
        sp, s, _ = d.place_t(sym, (W * 0.60, -H * 0.18, W * 1.12, H * 1.18))
        if getattr(d, "giant_full_color", False):
            # un symbole fait de plusieurs tons (la touche de O) ne survit pas au fantôme : on le garde en couleurs
            layers += d.color(sp, sch)
        else:
            layers += [(p, sch["accent"] if role == "accent" else faint) for p, role in sp]
        wmp, _, _ = d.place_t(d.wordmark(), (80, 250, 600, 350), align="left")
        layers += d.color(wmp, sch)
        wb = d.bounds(wmp)
        tl, _, _ = text_line(TAGLINE, font, 15 if upper else 18, 80, wb[1] - 48, muted, "left", upper, track,
                             max_w=760)
        layers.append(tl)
    elif name == "manchette":
        wmp, _, _ = d.place_t(d.wordmark(), (72, 150, W - 72, 440), align="left")
        layers += d.color(wmp, sch)
        tl, _, _ = text_line(TAGLINE, font, 15 if upper else 19, W - 72, 58, muted, "right", upper, track,
                             max_w=900)
        layers.append(tl)
    return page(W, H, layers, bg=sch["bg"])


def og_layout(d, name):
    W, H = 1200, 630
    if name == "centre":
        return compose.banner(d, "og")
    kind = "accent" if name == "accent" else d.banner_scheme
    sch = d.palette.scheme(kind)
    muted = sch[d.tagline_role] if (d.tagline_role and kind != "accent") else mix(sch["fg"], sch["bg"], 0.28)
    font, upper, track = _tag(d)
    layers = []
    if name == "gauche":
        wmp, _, _ = d.place_t(d.wordmark(), (80, 300, 860, 460), align="left")
        layers += d.color(wmp, sch)
        wb = d.bounds(wmp)
        tl, _, _ = text_line(TAGLINE, d.body, 30, 80, wb[1] - 78, muted, "left", False, 0.0, max_w=900)
        dom, _, _ = text_line(DOMAIN, d.mono, 20, 80, 70, sch["fg"], "left", False, 0.03)
        ic = compose.tile_layers(d, d.palette.scheme(d.icon_scheme if kind != "light" else "dark"))
        icon = [(g.translate(p, dx=W - 80 - 104, dy=H - 80 - 104, sx=104 / 256, sy=104 / 256), c) for p, c in ic]
        layers += [tl, dom] + icon
    elif name == "accent":
        wmp, _, _ = d.place_t(d.wordmark(), (W / 2 - 330, 290, W / 2 + 330, 470))
        layers += d.color(wmp, sch)
        wb = d.bounds(wmp)
        tl, _, _ = text_line(TAGLINE, font, 18 if upper else 24, W / 2, wb[1] - 72, muted, "center", upper, track,
                             max_w=1000)
        dom, _, _ = text_line(DOMAIN, d.mono, 18, W / 2, 64, sch["fg"], "center", False, 0.03)
        layers += [tl, dom]
    elif name == "symbole":
        ic = compose.tile_layers(d, d.palette.scheme(d.icon_scheme))
        size = 330
        layers += [(g.translate(p, dx=90, dy=(H - size) / 2, sx=size / 256, sy=size / 256), c) for p, c in ic]
        wmp, _, _ = d.place_t(d.wordmark(), (500, 330, W - 90, 430), align="left")
        layers += d.color(wmp, sch)
        wb = d.bounds(wmp)
        tl, _, _ = text_line(TAGLINE, d.body, 22, 500, wb[1] - 56, muted, "left", False, 0.0, max_w=W - 590)
        dom, _, _ = text_line(DOMAIN, d.mono, 17, 500, (H - size) / 2 + 6, muted, "left", False, 0.03)
        layers += [tl, dom]
    return page(W, H, layers, bg=sch["bg"])


X_NAMES = [("carton", "Carton-titre"), ("geant", "Symbole géant"), ("clair", "Version claire"),
           ("manchette", "Manchette")]
OG_NAMES = [("centre", "Centré"), ("gauche", "Éditorial à gauche"), ("accent", "Fond d'accent"),
            ("symbole", "Icône + nom")]


def build(code):
    d = BY_CODE[code]
    out = compose.OPT / f"{d.code}-{d.key}" / "layouts"
    out.mkdir(parents=True, exist_ok=True)
    for slug, _ in X_NAMES:
        compose.save(x_layout(d, slug), out / f"x-{slug}", png_width=1500)
    for slug, _ in OG_NAMES:
        compose.save(og_layout(d, slug), out / f"og-{slug}", png_width=1200)
    root = compose.ROOT
    xs = "".join(f'<figure><img src="file://{out / f"x-{s}.png"}"><figcaption>X · {n}</figcaption></figure>'
                 for s, n in X_NAMES)
    ogs = "".join(f'<figure><img src="file://{out / f"og-{s}.png"}"><figcaption>Aperçu de lien · {n}</figcaption></figure>'
                  for s, n in OG_NAMES)
    html = f"""<!doctype html><meta charset="utf-8"><style>
@font-face{{font-family:"M";src:url("file://{root / '.fonts' / 'MartianMono[wdth,wght].ttf'}")}}
body{{margin:0;background:#EDEDEA;font:12px 'M';color:#222;width:1900px}}
h1{{font:600 26px 'M';margin:28px 24px 16px}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:18px;padding:0 24px 24px}}
figure{{margin:0}} img{{width:100%;display:block}} figcaption{{margin-top:6px;color:#666}}
</style><h1>{d.code} · {d.name} — mises en page</h1><div class="grid">{xs}</div><div class="grid">{ogs}</div>"""
    hp = compose.OPT / f"{d.code}-{d.key}" / "_layouts.html"
    hp.write_text(html)
    compose.render_html(hp, compose.OPT / f"{d.code}-{d.key}" / "layouts.png", 1900, "auto", 1)
    hp.unlink()
    print(code, "mises en page")


if __name__ == "__main__":
    for c in sys.argv[1:] or ["A", "O", "D", "H", "E", "F", "J"]:
        build(c)
