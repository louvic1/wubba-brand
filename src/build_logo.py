"""Exporte toutes les variantes du logo Wubba : SVG maîtres, PNG, favicons, avatars, PDF, filigrane.

    python3 src/build_logo.py

Tout part de wordmark.py (géométrie) et palette.py (couleurs). Rien n'est dessiné à la main ailleurs.
"""
from __future__ import annotations

import io
import json
from pathlib import Path

import cairosvg
from PIL import Image

import geom as g
import palette as pal
import svgout
import wordmark as wm

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "logo"
INK, PAPER, SIGNAL, BLACK, WHITE = pal.INK, pal.PAPER, pal.SIGNAL, "#000000", "#FFFFFF"

# Compensation d'irradiation : en clair sur sombre, les lettres paraissent plus grasses.
# La version inversée est amincie d'une unité par côté (sur une hauteur d'x de 200, soit 4 % du fût).
THIN = -1.0

TILE = 256
TILE_R = 56            # 22 % du côté
GLYPH_IN_TILE = 0.64   # largeur du symbole dans la tuile
GLYPH_IN_TILE_SMALL = 0.74
LIFT = 0.02            # remontée optique dans la tuile


# ------------------------------------------------------------------ géométrie de base

def parts(small=False):
    p = wm.variant(**wm.SMALL) if small else wm.P
    body, dot = wm.wordmark(p)
    body_plain, _ = wm.wordmark(p, with_dot=False)
    sym, sdot = wm.symbol(p)
    return {"body": body, "dot": dot, "plain": body_plain, "sym": sym, "sdot": sdot}


def thin(path):
    return g.offset_stroke(path, THIN)


def glyph_in_square(sym, sdot, T, ratio, lift):
    """Place le symbole centré (optiquement) dans un carré de côté T. Renvoie les tracés transformés."""
    xmin, ymin, xmax, ymax = svgout.union_bounds(sym, sdot)
    s = T * ratio / (xmax - xmin)
    gw, gh = (xmax - xmin) * s, (ymax - ymin) * s
    dx = (T - gw) / 2 - xmin * s
    dy = (T - gh) / 2 - ymin * s + T * lift      # y vers le haut : on remonte en ajoutant
    return (g.translate(sym, dx=dx, dy=dy, sx=s, sy=s), g.translate(sdot, dx=dx, dy=dy, sx=s, sy=s))


def tile_layers(bg, fg, dotc, small=False, shape="tile", ratio=None, knockout=False):
    P = parts(small)
    ratio = ratio or (GLYPH_IN_TILE_SMALL if small else GLYPH_IN_TILE)
    sym, sdot = glyph_in_square(P["sym"], P["sdot"], TILE, ratio, LIFT)
    if shape == "tile":
        container = g.rounded_rect(0, 0, TILE, TILE, TILE_R, smooth=0.6)
    elif shape == "circle":
        container = g.circle(TILE / 2, TILE / 2, TILE / 2)
    else:
        container = g.rect(0, 0, TILE, TILE)
    if knockout:  # une seule couleur : symbole évidé dans la tuile
        return [(g.diff(container, g.union(sym, sdot)), bg)]
    return [(container, bg), (sym, fg), (sdot, dotc)]


# ------------------------------------------------------------------ écriture

def write_svg(name, layers, box, title, pad=0.0):
    path = OUT / "svg" / f"{name}.svg"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svgout.svg_doc(layers, box, title, pad=pad))
    return path


def write_current_color(name, layers, box, title):
    """Variante web : une seule couleur qui hérite de la couleur du texte (fill=currentColor)."""
    svg = svgout.svg_doc([(p, "currentColor") for p, _ in layers], box, title)
    path = OUT / "svg" / f"{name}.svg"
    path.write_text(svg)
    return path


def png_from_svg(svg_path, out_path, width=None, height=None):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cairosvg.svg2png(url=str(svg_path), write_to=str(out_path), output_width=width, output_height=height)
    return out_path


def square_box(box):
    xmin, ymin, xmax, ymax = box
    side = max(xmax - xmin, ymax - ymin)
    px, py = (side - (xmax - xmin)) / 2, (side - (ymax - ymin)) / 2
    return (xmin - px, ymin - py, xmax + px, ymax + py)


def build():
    P = parts()
    body, dot, plain, sym, sdot = P["body"], P["dot"], P["plain"], P["sym"], P["sdot"]
    body_thin, sym_thin, plain_thin = thin(body), thin(sym), thin(plain)
    wbox = svgout.union_bounds(body, dot)
    sbox = square_box(svgout.union_bounds(sym, sdot))
    tbox = (0, 0, TILE, TILE)
    files = {}

    # 1. Logo principal : le wordmark signé du point
    files["logo"] = write_svg("wubba-logo", [(body, INK), (dot, SIGNAL)], wbox, "wubba")
    files["logo-reversed"] = write_svg("wubba-logo-reversed", [(body_thin, PAPER), (dot, SIGNAL)], wbox, "wubba")
    files["logo-mono-noir"] = write_svg("wubba-logo-mono-noir", [(body, BLACK), (dot, BLACK)], wbox, "wubba")
    files["logo-mono-blanc"] = write_svg("wubba-logo-mono-blanc", [(body_thin, WHITE), (dot, WHITE)], wbox, "wubba")
    files["logo-sur-signal"] = write_svg("wubba-logo-sur-signal", [(body, INK), (dot, PAPER)], wbox, "wubba")
    files["logo-currentcolor"] = write_current_color("wubba-logo-currentcolor", [(body, INK), (dot, INK)], wbox, "wubba")

    # 2. Symbole seul (le w et son point)
    files["symbole"] = write_svg("wubba-symbole", [(sym, INK), (sdot, SIGNAL)], sbox, "wubba", pad=8)
    files["symbole-reversed"] = write_svg("wubba-symbole-reversed", [(sym_thin, PAPER), (sdot, SIGNAL)], sbox, "wubba", pad=8)
    files["symbole-mono-noir"] = write_svg("wubba-symbole-mono-noir", [(sym, BLACK), (sdot, BLACK)], sbox, "wubba", pad=8)
    files["symbole-mono-blanc"] = write_svg("wubba-symbole-mono-blanc", [(sym_thin, WHITE), (sdot, WHITE)], sbox, "wubba", pad=8)
    S = parts(small=True)
    files["symbole-petit"] = write_svg("wubba-symbole-petit", [(S["sym"], INK), (S["sdot"], SIGNAL)],
                                       square_box(svgout.union_bounds(S["sym"], S["sdot"])), "wubba", pad=4)

    # 3. Icône (tuile) : app, avatar, favicon
    files["icone"] = write_svg("wubba-icone", tile_layers(INK, PAPER, SIGNAL), tbox, "wubba")
    files["icone-papier"] = write_svg("wubba-icone-papier", tile_layers(PAPER, INK, SIGNAL), tbox, "wubba")
    files["icone-signal"] = write_svg("wubba-icone-signal", tile_layers(SIGNAL, INK, PAPER), tbox, "wubba")
    files["icone-mono"] = write_svg("wubba-icone-mono", tile_layers(BLACK, None, None, knockout=True), tbox, "wubba")
    files["icone-rond"] = write_svg("wubba-icone-rond", tile_layers(INK, PAPER, SIGNAL, shape="circle", ratio=0.58), tbox, "wubba")
    files["icone-petit"] = write_svg("wubba-icone-petit", tile_layers(INK, PAPER, SIGNAL, small=True), tbox, "wubba")

    # 4. Lockups : icône + nom (le point n'apparaît qu'une fois : dans l'icône)
    X = wm.P["X"]
    icon_h = 272 + 4                                  # l'icône couvre la hauteur ascendante + dépassement
    s = icon_h / TILE
    gap = X * 0.46
    ic = [(g.translate(p, dx=0, dy=-4, sx=s, sy=s), c) for p, c in tile_layers(INK, PAPER, SIGNAL)]
    ic_rev = [(g.translate(p, dx=0, dy=-4, sx=s, sy=s), c) for p, c in tile_layers(PAPER, INK, SIGNAL)]
    word = g.translate(plain, dx=icon_h + gap)
    word_thin = g.translate(plain_thin, dx=icon_h + gap)
    hbox = svgout.union_bounds(ic[0][0], word)
    files["lockup-h"] = write_svg("wubba-lockup-horizontal", ic + [(word, INK)], hbox, "wubba")
    files["lockup-h-rev"] = write_svg("wubba-lockup-horizontal-reversed", ic_rev + [(word_thin, PAPER)], hbox, "wubba")
    # empilé : icône centrée au-dessus du mot
    wb = g.bounds(plain)
    ww = wb[2] - wb[0]
    ic_size = 420
    s2 = ic_size / TILE
    ox = (ww - ic_size) / 2
    oy = 272 + X * 0.62
    ic2 = [(g.translate(p, dx=ox, dy=oy, sx=s2, sy=s2), c) for p, c in tile_layers(INK, PAPER, SIGNAL)]
    ic2_rev = [(g.translate(p, dx=ox, dy=oy, sx=s2, sy=s2), c) for p, c in tile_layers(PAPER, INK, SIGNAL)]
    vbox = svgout.union_bounds(ic2[0][0], plain)
    files["lockup-v"] = write_svg("wubba-lockup-empile", ic2 + [(plain, INK)], vbox, "wubba")
    files["lockup-v-rev"] = write_svg("wubba-lockup-empile-reversed", ic2_rev + [(plain_thin, PAPER)], vbox, "wubba")

    # 5. Filigrane pour les previews client (blanc pur ; l'opacité se règle dans le montage)
    files["filigrane"] = write_svg("wubba-filigrane", [(body_thin, WHITE), (dot, WHITE)], wbox, "wubba")

    return files


# ------------------------------------------------------------------ rasters

def rasters(files):
    png = OUT / "png"
    for key in ("logo", "logo-reversed", "logo-mono-noir", "logo-mono-blanc", "logo-sur-signal"):
        for w in (400, 800, 1600, 3200):
            png_from_svg(files[key], png / f"{files[key].stem}-{w}w.png", width=w)
    for key in ("symbole", "symbole-reversed", "symbole-mono-noir", "symbole-mono-blanc"):
        for w in (256, 512, 1024):
            png_from_svg(files[key], png / f"{files[key].stem}-{w}.png", width=w)
    for key in ("icone", "icone-papier", "icone-signal", "icone-mono", "icone-rond"):
        for w in (256, 512, 1024):
            png_from_svg(files[key], png / f"{files[key].stem}-{w}.png", width=w)
    for key in ("lockup-h", "lockup-h-rev", "lockup-v", "lockup-v-rev"):
        for w in (800, 1600):
            png_from_svg(files[key], png / f"{files[key].stem}-{w}w.png", width=w)
    for w in (1200, 2400):
        png_from_svg(files["filigrane"], OUT / "filigrane" / f"wubba-filigrane-{w}w.png", width=w)


def webp():
    """Versions WebP des PNG les plus utilisés sur le web (plus légères, même rendu)."""
    png, out = OUT / "png", OUT / "webp"
    out.mkdir(exist_ok=True)
    for name in ("wubba-logo-800w", "wubba-logo-1600w", "wubba-logo-reversed-800w", "wubba-logo-reversed-1600w",
                 "wubba-icone-512", "wubba-lockup-horizontal-800w"):
        Image.open(png / f"{name}.png").save(out / f"{name}.webp", lossless=True)


def favicons(files):
    fav = OUT / "favicon"
    fav.mkdir(parents=True, exist_ok=True)
    small, big = files["icone-petit"], files["icone"]
    ims = {}
    for sz in (16, 32, 48):
        data = cairosvg.svg2png(url=str(small), output_width=sz, output_height=sz)
        ims[sz] = Image.open(io.BytesIO(data)).convert("RGBA")
        ims[sz].save(fav / f"favicon-{sz}.png")
    ims[48].save(fav / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)], append_images=[ims[16], ims[32]])
    # apple-touch : pas de transparence, iOS arrondit lui-même -> carré plein
    sq = svgout.svg_doc(tile_layers(INK, PAPER, SIGNAL, shape="square"), (0, 0, TILE, TILE), "wubba")
    (fav / "_square.svg").write_text(sq)
    png_from_svg(fav / "_square.svg", fav / "apple-touch-icon.png", 180, 180)
    png_from_svg(big, fav / "icon-192.png", 192, 192)
    png_from_svg(big, fav / "icon-512.png", 512, 512)
    # maskable : zone sûre = cercle de 80 % -> symbole plus petit sur fond plein
    mk = svgout.svg_doc(tile_layers(INK, PAPER, SIGNAL, shape="square", ratio=0.5), (0, 0, TILE, TILE), "wubba")
    (fav / "_maskable.svg").write_text(mk)
    png_from_svg(fav / "_maskable.svg", fav / "icon-maskable-512.png", 512, 512)
    (fav / "_square.svg").unlink()
    (fav / "_maskable.svg").unlink()
    # favicon.svg : la tuile, lisible sur onglet clair comme sombre
    (fav / "favicon.svg").write_text(small.read_text())
    (fav / "site.webmanifest").write_text(json.dumps({
        "name": "wubba", "short_name": "wubba",
        "icons": [{"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"},
                  {"src": "/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}],
        "theme_color": INK, "background_color": INK, "display": "standalone"}, indent=2) + "\n")
    (fav / "head-snippet.html").write_text(
        '<link rel="icon" href="/favicon.ico" sizes="48x48">\n'
        '<link rel="icon" href="/favicon.svg" type="image/svg+xml">\n'
        '<link rel="apple-touch-icon" href="/apple-touch-icon.png">\n'
        '<link rel="manifest" href="/site.webmanifest">\n'
        f'<meta name="theme-color" content="{INK}">\n')


def social(files):
    soc = OUT / "social"
    soc.mkdir(parents=True, exist_ok=True)
    # Avatars : carré plein bord à bord (X, LinkedIn, Instagram et TikTok recadrent en cercle)
    sq = svgout.svg_doc(tile_layers(INK, PAPER, SIGNAL, shape="square", ratio=0.56), (0, 0, TILE, TILE), "wubba")
    tmp = soc / "_avatar.svg"
    tmp.write_text(sq)
    for name, sz in (("avatar-x-400", 400), ("avatar-linkedin-400", 400), ("avatar-1080", 1080)):
        png_from_svg(tmp, soc / f"{name}.png", sz, sz)
    (soc / "avatar.svg").write_text(sq)
    tmp.unlink()


def pdfs(files):
    pdf = OUT / "pdf"
    pdf.mkdir(parents=True, exist_ok=True)
    for key in ("logo", "logo-reversed", "logo-mono-noir", "symbole", "icone", "lockup-h"):
        src = files[key]
        svg = src.read_text()
        if key == "logo-reversed":  # un PDF blanc sur transparent est invisible : on pose le fond encre
            box = svg.split('viewBox="')[1].split('"')[0].split()
            svg = svg.replace("</title>", f'</title><rect width="{box[2]}" height="{box[3]}" fill="{INK}"/>', 1)
        cairosvg.svg2pdf(bytestring=svg.encode(), write_to=str(pdf / f"{src.stem}.pdf"))


if __name__ == "__main__":
    f = build()
    rasters(f)
    webp()
    favicons(f)
    social(f)
    pdfs(f)
    n = sum(1 for _ in OUT.rglob("*") if _.is_file())
    print(f"{n} fichiers dans {OUT}")
