"""Direction A, couleur 8 (forêt et lime) sur fond blanc : 5 bannières X et 6 typographies.

Les bannières ne portent que « wubba » et « AI streamers » : pas de ligne complète, pas de coins de viseur.

    python3 src/x_blanc.py   ->  options/A-point/x-blanc/  +  x-blanc/index.html (page de choix)
"""
from __future__ import annotations

import html
import io

import cairosvg
from PIL import Image, ImageChops

import compose
import geom as g
import textpath as tp
from compose import mix, page
from directions import BY_CODE

ROOT = compose.ROOT
OUT = compose.OPT / "A-point" / "x-blanc"
PAGE = ROOT / "x-blanc"
IMG = PAGE / "img"
FONTS = ROOT / ".fonts"

WHITE, FOREST, LIME = "#FFFFFF", "#0E2B22", "#A6DB1F"
LABEL = "AI streamers"
W, H = 1500, 500
# zone de l'avatar X sur ordinateur : un disque de 334 px, à 40 px du bord gauche, à cheval sur le bas de la bannière
AVATAR = (40 + 167, 0, 167)          # centre x, centre y (y vers le haut), rayon

A = BY_CODE["A"]
MONO = ("MartianMono[wdth,wght].ttf", {"wght": 500, "wdth": 100})
SANS = ("InstrumentSans[wdth,wght].ttf", {"wght": 600, "wdth": 100})


def logo(box, align="center"):
    placed, _ = A.place(A.wordmark(), box, align=align)
    return [(p, FOREST if r == "fg" else LIME) for p, r in placed], A.bounds(placed)


def label(x, y, size, align="left", font=MONO, upper=True, tracking=0.16, color=FOREST):
    (p, c), w, _ = compose.text_line(LABEL, _font(font), size, x, y, color, align, upper, tracking)
    return (p, c), w


def _font(f):
    class F:
        file, var = f
    return F


# ------------------------------------------------------------------ les cinq bannières

def b1():
    """Centré : le logo au milieu, la mention dessous, rien d'autre."""
    layers, b = logo((W / 2 - 360, 235, W / 2 + 360, 405))
    lab, _ = label(W / 2, b[1] - 96, 44, "center")
    return layers + [lab]


def b2():
    """Géant : le logo prend presque toute la largeur libre, calé à droite de l'avatar."""
    layers, b = logo((430, 175, 1420, 425), align="right")
    lab, _ = label(b[2], b[1] - 90, 42, "right")
    return layers + [lab]


def b3():
    """Éditorial : la mention au-dessus, le logo dessous, tout aligné à droite."""
    layers, b = logo((700, 150, 1400, 330), align="right")
    lab, _ = label(b[2], b[3] + 54, 40, "right")
    return layers + [lab]


def b4():
    """Le point : un grand disque lime qui déborde à droite reprend le point du w ; le logo à gauche."""
    disc = g.intersect(g.circle(1330, 250, 300), g.rect(0, 0, W, H))
    layers, b = logo((430, 240, 1000, 390), align="left")
    lab, _ = label(b[0] + 4, b[1] - 84, 38, "left")
    return [(disc, LIME)] + layers + [lab]


def b5():
    """En ligne : le logo, un filet, puis « AI streamers » en toutes lettres, le tout centré sur une ligne."""
    layers, b = logo((0, 0, 560, 150), align="left")
    size = 66
    (p, c), w = label(0, 0, size, "left", font=SANS, upper=False, tracking=-0.005)
    gap = 56
    total = (b[2] - b[0]) + gap * 2 + 3 + w
    x0 = W / 2 - total / 2 + 60                   # un peu à droite du centre : l'avatar mange le bas gauche
    cy = 262
    dx, dy = x0 - b[0], cy - (b[1] + b[3]) / 2
    layers = [(g.translate(q, dx=dx, dy=dy), col) for q, col in layers]
    lx = x0 + (b[2] - b[0]) + gap
    rule = g.rect(lx, cy - 70, lx + 3, cy + 70)
    tb = p.bounds
    text = g.translate(p, dx=lx + 3 + gap, dy=cy - (tb[1] + tb[3]) / 2)
    return layers + [(rule, mix(FOREST, WHITE, 0.55)), (text, FOREST)]


BANNERS = [
    (1, "centre", "Centré", b1, "Le logo au milieu, la mention dessous. La plus sûre : elle tient sur tous les écrans, l'avatar ne touche rien."),
    (2, "geant", "Géant", b2, "Le logo aussi grand que possible, calé à droite pour laisser la place à l'avatar. La plus forte dans un fil."),
    (3, "editorial", "Éditorial à droite", b3, "La mention en petit au-dessus, le logo dessous, tout aligné à droite. Calme, très « studio »."),
    (4, "point", "Le point", b4, "Un grand disque lime reprend le point du w et déborde du cadre. La seule avec un vrai aplat de couleur."),
    (5, "ligne", "En ligne", b5, "Le logo et « AI streamers » sur une seule ligne, séparés par un filet. Se lit d'un coup, comme une signature."),
]


def preview(svg_text):
    """La bannière telle qu'on la voit sur un profil X : l'avatar posé à cheval sur le bas gauche."""
    Hp = H + 190
    ring = 8
    cx, r = AVATAR[0], AVATAR[2]
    cy_top = H                      # centre de l'avatar sur le bord bas de la bannière (coordonnées écran)
    sym, _ = A.place(A.symbol(), (cx - r * 0.55, Hp - cy_top - r * 0.55, cx + r * 0.55, Hp - cy_top + r * 0.55))
    body = svg_text.split(">", 1)[1].rsplit("</svg>", 1)[0]
    parts = [f'<rect width="{W}" height="{Hp}" fill="#F4F4F2"/>', f'<svg x="0" y="0" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{body}</svg>',
             f'<rect x="0" y="{H}" width="{W}" height="1" fill="#DADAD6"/>',
             f'<circle cx="{cx}" cy="{cy_top}" r="{r + ring}" fill="#F4F4F2"/>',
             f'<circle cx="{cx}" cy="{cy_top}" r="{r}" fill="{WHITE}" stroke="#E2E2DE" stroke-width="2"/>']
    for p, role in sym:
        parts.append(f'<path fill="{FOREST if role == "fg" else LIME}" d="{g.to_d(p, Hp)}"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{Hp}" viewBox="0 0 {W} {Hp}">' + "".join(parts) + "</svg>")


# ------------------------------------------------------------------ les six typographies

TYPES = [
    ("T1", "Archivo Expanded, Instrument Sans, Martian Mono", "Actuelle : large et solide comme le logo.",
     ("Archivo", "Archivo[wdth,wght].ttf", "font-stretch:125%;font-weight:800", "Archivo:wdth,wght@125,800"),
     ("Instrument Sans", "InstrumentSans[wdth,wght].ttf", "font-weight:400", "Instrument+Sans:wght@400;600"),
     ("Martian Mono", "MartianMono[wdth,wght].ttf", "font-weight:500", "Martian+Mono:wght@500")),
    ("T2", "Sora, Figtree, JetBrains Mono", "Géométrique et technique ; la plus proche du dessin rond du logo.",
     ("Sora", "Sora[wght].ttf", "font-weight:700", "Sora:wght@700"),
     ("Figtree", "Figtree[wght].ttf", "font-weight:400", "Figtree:wght@400;600"),
     ("JetBrains Mono", "JetBrainsMono[wght].ttf", "font-weight:500", "JetBrains+Mono:wght@500")),
    ("T3", "Outfit, IBM Plex Sans, IBM Plex Mono", "Ronde et amicale en titre, rigoureuse en texte : le labo de test.",
     ("Outfit", "Outfit[wght].ttf", "font-weight:700", "Outfit:wght@700"),
     ("IBM Plex Sans", "IBMPlexSans[wdth,wght].ttf", "font-weight:400", "IBM+Plex+Sans:wght@400;600"),
     ("IBM Plex Mono", "IBMPlexMono-Medium.ttf", "font-weight:500", "IBM+Plex+Mono:wght@500")),
    ("T4", "Bricolage Grotesque, Bricolage Grotesque, Azeret Mono", "Une seule famille pleine de caractère : plus créateur, moins corporate.",
     ("Bricolage Grotesque", "BricolageGrotesque[opsz,wdth,wght].ttf", "font-weight:800;font-variation-settings:'opsz' 96", "Bricolage+Grotesque:opsz,wght@12..96,400;12..96,800"),
     ("Bricolage Grotesque", "BricolageGrotesque[opsz,wdth,wght].ttf", "font-weight:400;font-variation-settings:'opsz' 14", ""),
     ("Azeret Mono", "AzeretMono[wght].ttf", "font-weight:500", "Azeret+Mono:wght@500")),
    ("T5", "Epilogue, Epilogue, Red Hat Mono", "Un grotesque éditorial, net et dense : le ton d'un rapport de test.",
     ("Epilogue", "Epilogue[wght].ttf", "font-weight:800", "Epilogue:wght@400;800"),
     ("Epilogue", "Epilogue[wght].ttf", "font-weight:400", ""),
     ("Red Hat Mono", "RedHatMono[wght].ttf", "font-weight:500", "Red+Hat+Mono:wght@500")),
    ("T6", "Unbounded, Onest, Space Mono", "Large et arrondie, la plus joueuse ; forte en titre, à doser.",
     ("Unbounded", "Unbounded[wght].ttf", "font-weight:700", "Unbounded:wght@700"),
     ("Onest", "Onest[wght].ttf", "font-weight:400", "Onest:wght@400;600"),
     ("Space Mono", "SpaceMono-Bold.ttf", "font-weight:700", "Space+Mono:wght@700")),
]


def logo_svg(height=64):
    placed, _ = A.place(A.wordmark(), (0, 0, 1000, height))
    b = A.bounds(placed)
    w = b[2] - b[0]
    paths = "".join(f'<path fill="{FOREST if r == "fg" else LIME}" d="{g.to_d(g.translate(p, dx=-b[0], dy=-b[1]), b[3] - b[1])}"/>'
                    for p, r in placed)
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{b[3] - b[1]:.0f}" viewBox="0 0 {w:.1f} {b[3] - b[1]:.1f}">{paths}</svg>'


def type_banner(mono_file, mono_css):
    """La bannière 1 (centrée) avec la mention dans l'utilitaire de la paire."""
    layers, b = logo((W / 2 - 360, 235, W / 2 + 360, 405))
    weight = 700 if "700" in mono_css else 500
    var = {"wght": weight} if "[" in mono_file else {}
    (p, c), _ = label(W / 2, b[1] - 96, 44, "center", font=(mono_file, var))
    return page(W, H, layers + [(p, c)], bg=WHITE)


def type_specimen(code, names, note, disp, body, mono, banner_png):
    faces = {(f[0], f[1]) for f in (disp, body, mono)}
    ff = "\n".join(f'@font-face{{font-family:"{fam}";src:url("file://{FONTS / file}");font-weight:100 900;font-stretch:50% 200%}}'
                   for fam, file in faces)
    return f"""<!doctype html><meta charset="utf-8"><style>{ff}
@font-face{{font-family:"M";src:url("file://{FONTS / 'MartianMono[wdth,wght].ttf'}")}}
body{{margin:0;background:{WHITE};width:1600px;color:{FOREST}}}
.s{{display:grid;grid-template-columns:1fr 1fr;gap:48px;padding:44px 52px;align-items:center}}
.logo svg{{height:58px;width:auto;display:block}}
h1{{font-family:'{disp[0]}';{disp[2]};font-size:84px;line-height:1;margin:34px 0 22px;letter-spacing:-.01em}}
p{{font-family:'{body[0]}';{body[2]};font-size:21px;line-height:1.45;margin:0 0 12px;max-width:34em}}
.abc{{font-size:17px;color:{mix(FOREST, WHITE, 0.25)}}}
.lab{{font-family:'{mono[0]}';{mono[2]};font-size:15px;letter-spacing:.14em;text-transform:uppercase;margin-top:22px}}
.lab b{{color:{mix(LIME, FOREST, 0.35)}}}
.ban img{{width:100%;display:block;border:1px solid #E4E6E2}}
</style><div class="s"><div><div class="logo">{logo_svg()}</div>
<h1>AI streamers</h1>
<p>AI streamers who test gaming gear where it has no business working</p>
<p class="abc">ABCDEFGHIJKLMNOPQRSTUVWXYZ<br>abcdefghijklmnopqrstuvwxyz 0123456789 ? ! @ &amp;</p>
<div class="lab">wubba.studio <b>·</b> @wubbastudio</div></div>
<div class="ban"><img src="file://{banner_png}"></div></div>"""


def trim(path, bg=(255, 255, 255)):
    im = Image.open(path).convert("RGB")
    box = ImageChops.difference(im, Image.new("RGB", im.size, bg)).getbbox()
    if box:
        im.crop((0, max(0, box[1] - 30), im.width, min(im.height, box[3] + 30))).save(path)


def webp(src, name, max_w, q=88):
    IMG.mkdir(parents=True, exist_ok=True)
    im = Image.open(src).convert("RGB")
    if im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    im.save(IMG / f"{name}.webp", "WEBP", quality=q, method=6)
    return f"img/{name}.webp"


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    for f in IMG.glob("*.webp") if IMG.exists() else []:
        f.unlink()
    bcards = []
    for n, slug, name, fn, why in BANNERS:
        svg = page(W, H, fn(), bg=WHITE)
        base = OUT / f"b{n}-{slug}"
        compose.save(svg, base, png_width=W)
        cairosvg.svg2png(bytestring=svg.encode(), write_to=str(base) + "@2x.png", output_width=W * 2)
        pv = preview(svg)
        cairosvg.svg2png(bytestring=pv.encode(), write_to=str(base) + "-profil.png", output_width=W)
        bcards.append((n, name, why, webp(base.with_suffix(".png"), f"b{n}", 1500), webp(str(base) + "-profil.png", f"b{n}-profil", 1000)))
    tcards = []
    for code, names, note, disp, body, mono in TYPES:
        bp = OUT / f"{code}-banniere.png"
        cairosvg.svg2png(bytestring=type_banner(mono[1], mono[2]).encode(), write_to=str(bp), output_width=W)
        hp = OUT / f"_{code}.html"
        hp.write_text(type_specimen(code, names, note, disp, body, mono, bp))
        png = OUT / f"{code}.png"
        compose.render_html(hp, png, 1600, "auto", 1)
        hp.unlink()
        trim(png)
        link = "https://fonts.googleapis.com/css2?" + "&".join("family=" + f[3] for f in (disp, body, mono) if f[3]) + "&display=swap"
        tcards.append((code, names, note, webp(png, code, 1600), link))
    PAGE.mkdir(exist_ok=True)
    (PAGE / "index.html").write_text(render(bcards, tcards))
    files = list(IMG.glob("*.webp"))
    print(f"x-blanc : {len(bcards)} bannières, {len(tcards)} typos, {len(files)} images, {sum(f.stat().st_size for f in files) / 1e6:.1f} Mo")


def render(bcards, tcards):
    b = "".join(f"""
<article class="opt" id="b{n}">
  <header><span class="num">B{n}</span><h3>{html.escape(name)}</h3></header>
  <img src="{src}" alt="Bannière X {n}, {html.escape(name)}" loading="lazy">
  <figure class="pv"><img src="{pv}" alt="Bannière {n} sur un profil X, avec l'avatar" loading="lazy"><figcaption>Sur un profil X, avec l'avatar</figcaption></figure>
  <p>{html.escape(why)}</p>
</article>""" for n, name, why, src, pv in bcards)
    t = "".join(f"""
<article class="opt" id="{code.lower()}">
  <header><span class="num">{code}</span><h3>{html.escape(names)}</h3></header>
  <img src="{src}" alt="Planche typographique {code} : {html.escape(names)}" loading="lazy">
  <p>{html.escape(note)}</p>
  <p class="link"><code>{html.escape(link)}</code></p>
</article>""" for code, names, note, src, link in tcards)
    return TEMPLATE.format(banners=b, types=t)


TEMPLATE = """<title>Bannière et typo wubba</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@125,800&family=Instrument+Sans:wght@400;600&family=Martian+Mono:wdth,wght@87.5,500&display=swap">
<style>
/* Deux listes numérotées à parcourir au téléphone : les bannières (B1 à B5), puis les typographies (T1 à T6). */
:root {{
  --bg:#F3F4F1; --panel:#FFFFFF; --fg:#0E2B22; --muted:#56655F; --line:#DCE0DA; --lime:#A6DB1F;
  --display:"Archivo","Arial Black",system-ui,sans-serif; --sans:"Instrument Sans",system-ui,-apple-system,"Segoe UI",sans-serif;
  --mono:"Martian Mono",ui-monospace,Menlo,monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg:#0B1A15; --panel:#12241D; --fg:#EEF2EC; --muted:#A5B3AB; --line:#24382F; color-scheme:dark }} }}
:root[data-theme="dark"] {{ --bg:#0B1A15; --panel:#12241D; --fg:#EEF2EC; --muted:#A5B3AB; --line:#24382F; color-scheme:dark }}
body {{ background:var(--bg); color:var(--fg); font:16px/1.5 var(--sans); }}
.wrap {{ max-width:1080px; margin:0 auto; padding-inline:16px; padding-block:28px 64px; }}
h1 {{ font-family:var(--display); font-stretch:125%; font-weight:800; font-size:clamp(28px,5.6vw,48px); line-height:1.04; margin:0 0 12px; letter-spacing:-.015em; text-wrap:balance }}
h2 {{ font-family:var(--display); font-stretch:125%; font-weight:800; font-size:24px; margin:40px 0 6px }}
.lede, .intro {{ max-width:62ch; color:var(--muted); margin:0 0 18px }}
.eyebrow, .num, code, figcaption {{ font-family:var(--mono); letter-spacing:.02em }}
.eyebrow {{ font-size:12px; text-transform:uppercase; color:var(--muted); margin:0 0 10px }}
.opt {{ background:var(--panel); border:1px solid var(--line); padding:14px; margin:0 0 16px; display:grid; gap:12px }}
.opt header {{ display:flex; align-items:baseline; gap:12px }}
.num {{ font-size:22px; font-weight:500; min-width:2.2em }}
.opt h3 {{ font-size:18px; margin:0; line-height:1.25 }}
.opt img {{ display:block; width:100%; height:auto; border:1px solid var(--line) }}
.opt p {{ margin:0; max-width:70ch }}
.pv {{ margin:0; max-width:560px }}
figcaption {{ font-size:11px; color:var(--muted); margin-top:6px }}
.link code {{ font-size:11px; color:var(--muted); word-break:break-all }}
.dot {{ display:inline-block; width:.6em; height:.6em; border-radius:50%; background:var(--lime); vertical-align:.05em; margin-right:.35em }}
</style>

<div class="wrap">
  <p class="eyebrow">wubba · direction A · forêt et lime sur blanc</p>
  <h1>Bannière et typo wubba</h1>
  <p class="lede">Cinq bannières X sur fond blanc, avec seulement « wubba » et « AI streamers », puis six typographies. Réponds avec un numéro de chaque liste, par exemple B2 et T3.</p>

  <h2>Bannières X</h2>
  <p class="intro">1500 × 500, sans coins ni slogan. Sous chaque bannière, la même vue sur un profil X, pour vérifier que l'avatar ne cache rien. La mention prendra la typo que tu choisiras plus bas.</p>
  {banners}

  <h2>Typographies</h2>
  <p class="intro">Chaque planche montre le titre, le texte et les petites étiquettes, avec le logo et la bannière centrée dans cette typo. Le logo, lui, ne change pas : il est dessiné. Les trois familles de chaque paire sont gratuites sur Google Fonts.</p>
  {types}
</div>
"""


if __name__ == "__main__":
    build()
