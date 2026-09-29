"""Couleurs de marque pour la direction A retenue : le même logo, douze couleurs.

Le noir et le point rouge rappelaient trop le logo Ironman ; ici, seul le point, le fond ou le mot changent de couleur.

    python3 src/colors_a.py      ->  options/A-point/couleurs/<n>-<slug>/  +  couleurs/index.html (page de choix)
"""
from __future__ import annotations

import copy
import html
from pathlib import Path

from PIL import Image

import compose
import palette as pal
import svgout
from directions import BY_CODE
from directions.base import Palette

ROOT = compose.ROOT
OUT = compose.OPT / "A-point" / "couleurs"
PAGE = ROOT / "couleurs"
IMG = PAGE / "img"
INK, PAPER = "#0E0F12", "#F1F0EC"


def P(light, dark, names, notes=None):
    """light / dark : (fond, mot, point). Le schéma sombre sert aussi à l'icône et aux bannières."""
    lb, lf, la = light
    db, df, da = dark
    return Palette(db, lb, da, names=names, notes=notes or {},
                   custom={"light": {"bg": lb, "fg": lf, "accent": la, "fg2": la},
                           "dark": {"bg": db, "fg": df, "accent": da, "fg2": da},
                           "accent": {"bg": da, "fg": db, "accent": lb, "fg2": lb}})


# (numéro, slug, nom, groupe, palette, une phrase)
OPTIONS = [
    (1, "outremer", "Outremer", "Le point change",
     P((PAPER, INK, "#2F46FF"), (INK, PAPER, "#6272FF"), {"accent": "Outremer"}),
     "Un bleu pur et froid, loin du rouge sportif ; il reste net à 16 px sur le noir comme sur le papier."),
    (2, "rose", "Rose direct", "Le point change",
     P((PAPER, INK, "#FF2E93"), (INK, PAPER, "#FF2E93"), {"accent": "Rose direct"}),
     "Presque personne ne l'utilise dans le matériel gaming ; il garde l'énergie d'un voyant sans être rouge."),
    (3, "orange", "Orange", "Le point change",
     P((PAPER, INK, "#F25A00"), (INK, PAPER, "#F25A00"), {"accent": "Orange"}),
     "Le voyant devient ambre, chaud et visible ; mais sur le noir, de loin, il tire encore vers le rouge, et SteelSeries est orange."),
    (4, "cyan", "Cyan", "Le point change",
     P((PAPER, INK, "#0091C2"), (INK, PAPER, "#00B8E6"), {"accent": "Cyan"}),
     "La couleur des écrans et des câbles lumineux ; attention, plusieurs marques de périphériques jouent déjà dans ces bleus."),
    (5, "vert", "Vert en ligne", "Le point change",
     P((PAPER, INK, "#00A35A"), (INK, PAPER, "#00C46A"), {"accent": "Vert en ligne"}),
     "Le point devient le voyant « en ligne » d'un profil ; attention, Razer, Xbox et Nvidia sont tous verts."),
    (6, "lilas", "Lilas", "Le point change",
     P((PAPER, INK, "#7C5CFF"), (INK, PAPER, "#9B7BFF"), {"accent": "Lilas"}),
     "Doux et inattendu ; sur fond sombre, il se rapproche du violet de Twitch."),
    (7, "nuit-orange", "Nuit et orange", "La couleur prend le fond",
     P((PAPER, "#111A3B", "#F25A00"), ("#111A3B", PAPER, "#FF7A1A"), {"ink": "Nuit", "accent": "Orange"}),
     "Le noir disparaît : un bleu nuit profond porte la marque, le point orange s'y détache à 6,5:1."),
    (8, "foret-lime", "Forêt et lime", "La couleur prend le fond",
     P((PAPER, "#0E2B22", "#5E9E00"), ("#0E2B22", PAPER, "#C4F03D"), {"ink": "Forêt", "accent": "Lime"}),
     "Un vert forêt presque noir et un point lime : le dehors, le terrain où le matériel n'a rien à faire."),
    (9, "bleu-jaune", "Bleu électrique et jaune", "La couleur prend le fond",
     P((PAPER, "#1D2FD6", "#E0A000"), ("#1D2FD6", PAPER, "#FFD23F"), {"ink": "Bleu électrique", "accent": "Jaune"}),
     "La plus franche : un fond bleu vif qu'on repère de loin dans un fil, le point jaune comme un soleil. Bleu et jaune ensemble rappellent un peu IKEA."),
    (10, "aubergine-rose", "Aubergine et rose", "La couleur prend le fond",
     P((PAPER, "#2A1233", "#E8337F"), ("#2A1233", PAPER, "#FF5AA5"), {"ink": "Aubergine", "accent": "Rose"}),
     "Sombre et chaude à la fois ; plus lifestyle que tech, à l'opposé des marques de matériel."),
    (11, "mot-outremer", "Mot outremer, point rose", "Le mot en couleur",
     P((PAPER, "#2F46FF", "#FF2E93"), ("#0B0E2A", PAPER, "#FF2E93"), {"ink": "Outremer", "accent": "Rose"}),
     "Deux couleurs vives au lieu d'une : le mot en bleu, le point en rose. La plus joueuse."),
    (12, "mot-foret", "Mot forêt, point orange", "Le mot en couleur",
     P(("#F2EFE6", "#0F3D2E", "#F25A00"), ("#0F3D2E", PAPER, "#FF7A1A"), {"ink": "Forêt", "accent": "Orange"}),
     "Un vert profond et un orange de balisage : l'équipement de plein air plutôt que le bureau gamer."),
]
CURRENT = P((PAPER, INK, "#FF2A36"), (INK, PAPER, "#FF2A36"), {"accent": "Signal"})
RECO = {11, 9, 2}         # mes trois préférées


def with_palette(d, palette):
    v = copy.copy(d)
    v.palette = palette
    return v


def render(v, out):
    out.mkdir(parents=True, exist_ok=True)
    wm = v.wordmark()
    box = v.bounds(wm)
    pad = (box[3] - box[1]) * 0.35
    for kind in ("light", "dark"):
        sch = v.palette.scheme(kind)
        compose.save(svgout.svg_doc(v.color(wm, sch), box, "wubba", pad=pad, bg=sch["bg"]), out / f"logo-{kind}", png_width=1200)
    compose.save(compose.page(256, 256, compose.tile_layers(v, v.palette.scheme("dark"))), out / "icon", png_width=512)
    compose.favicon_test(v, out)
    compose.save(compose.banner(v, "x-header"), out / "x-header", png_width=1500)


def webp(src, name, max_w, q=86):
    IMG.mkdir(parents=True, exist_ok=True)
    im = Image.open(src).convert("RGBA" if src.name.startswith(("favicon", "icon")) else "RGB")
    if im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    dst = IMG / f"{name}.webp"
    im.save(dst, "WEBP", quality=q, method=6)
    return f"img/{name}.webp"


def swatch(color, label):
    return f'<li><span class="sw" style="--c:{color}"></span><span><b>{html.escape(label)}</b><code>{color}</code></span></li>'


def card(n, slug, name, group, palette, why, imgs, tag=""):
    lt, dk = palette.scheme("light"), palette.scheme("dark")
    k = pal.contrast(dk["accent"], dk["bg"])
    kl = pal.contrast(lt["accent"], lt["bg"])
    sw = "".join([swatch(dk["bg"], "Fond sombre"), swatch(dk["accent"], "Point"),
                  swatch(lt["fg"], "Mot sur clair")] + ([swatch(lt["accent"], "Point sur clair")] if lt["accent"] != dk["accent"] else []))
    return f"""
<article class="opt" id="c{n}">
  <header><span class="num">{n}</span><h2>{html.escape(name)}</h2>{tag}</header>
  <img class="banner" src="{imgs['x']}" alt="Bannière X, option {n} {html.escape(name)}" loading="lazy">
  <div class="row">
    <img src="{imgs['light']}" alt="Logo sur fond clair, option {n}" loading="lazy">
    <img src="{imgs['dark']}" alt="Logo sur fond sombre, option {n}" loading="lazy">
    <img class="ic" src="{imgs['icon']}" alt="Icône, option {n}" loading="lazy">
  </div>
  <div class="meta">
    <ul class="sws">{sw}</ul>
    <div class="side"><img class="fav" src="{imgs['fav']}" alt="Favicon à 16, 24, 32 et 48 pixels réels, option {n}" loading="lazy">
    <p class="k">Point sur fond : {k:.1f}:1 en sombre, {kl:.1f}:1 en clair</p></div>
  </div>
  <p class="why">{html.escape(why)}</p>
</article>"""


def build():
    d = BY_CODE["A"]
    for f in IMG.glob("*.webp") if IMG.exists() else []:
        f.unlink()
    cards = []
    cur = OUT / "0-actuel"
    render(with_palette(d, CURRENT), cur)
    cur_img = webp(cur / "x-header.png", "0-x", 900)
    groups = {}
    for n, slug, name, group, palette, why in OPTIONS:
        o = OUT / f"{n}-{slug}"
        render(with_palette(d, palette), o)
        imgs = {"x": webp(o / "x-header.png", f"{n}-x", 1500), "light": webp(o / "logo-light.png", f"{n}-light", 700),
                "dark": webp(o / "logo-dark.png", f"{n}-dark", 700), "icon": webp(o / "icon.png", f"{n}-icon", 256),
                "fav": webp(o / "favicon-test.png", f"{n}-fav", 520, 95)}
        tag = '<span class="reco">Mon choix</span>' if n in RECO else ""
        groups.setdefault(group, []).append(card(n, slug, name, group, palette, why, imgs, tag))
    cards = [f'<h3 class="gh">{html.escape(g)}</h3><div class="grid">{"".join(cs)}</div>' for g, cs in groups.items()]
    PAGE.mkdir(exist_ok=True)
    (PAGE / "index.html").write_text(TEMPLATE.format(current=cur_img, cards="".join(cards)))
    n = len(list(IMG.glob("*.webp")))
    print(f"couleurs : {len(OPTIONS)} options, {n} images, {sum(f.stat().st_size for f in IMG.glob('*.webp')) / 1e6:.1f} Mo")


TEMPLATE = """<title>Couleurs wubba</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@125,800&family=Instrument+Sans:wght@400;600&family=Martian+Mono:wdth,wght@87.5,400;87.5,500&display=swap">
<style>
/* Une colonne d'options numérotées, pensée pour le téléphone : on compare en faisant défiler, on répond avec un numéro. */
:root {{
  --bg:#EDEDEA; --panel:#F8F8F6; --fg:#141416; --muted:#5D5D5A; --line:#D7D6D1; --tag:#141416; --tag-fg:#F8F8F6;
  --display:"Archivo","Arial Black",system-ui,sans-serif; --sans:"Instrument Sans",system-ui,-apple-system,"Segoe UI",sans-serif;
  --mono:"Martian Mono",ui-monospace,Menlo,monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg:#121214; --panel:#1B1B1E; --fg:#EDEDEA; --muted:#A2A29D; --line:#2E2E32; --tag:#EDEDEA; --tag-fg:#121214; color-scheme:dark }} }}
:root[data-theme="dark"] {{ --bg:#121214; --panel:#1B1B1E; --fg:#EDEDEA; --muted:#A2A29D; --line:#2E2E32; --tag:#EDEDEA; --tag-fg:#121214; color-scheme:dark }}
body {{ background:var(--bg); color:var(--fg); font:16px/1.5 var(--sans); }}
.wrap {{ max-width:1080px; margin:0 auto; padding-inline:16px; padding-block:28px 64px; }}
h1 {{ font-family:var(--display); font-stretch:125%; font-weight:800; font-size:clamp(30px,6vw,52px); line-height:1.02; margin:0 0 12px; letter-spacing:-.015em; text-wrap:balance }}
.lede {{ max-width:62ch; margin:0 0 20px; color:var(--muted) }}
.eyebrow,.k,code,.num,.reco,.gh,.cur figcaption {{ font-family:var(--mono); letter-spacing:.02em }}
.eyebrow {{ font-size:12px; text-transform:uppercase; color:var(--muted); margin:0 0 10px }}
.cur {{ margin:0 0 28px; display:grid; grid-template-columns:minmax(0,260px) minmax(0,1fr); gap:14px; align-items:center }}
.cur img {{ display:block; width:100%; opacity:.9 }}
.cur figcaption {{ font-size:12px; color:var(--muted) }}
.gh {{ font-size:12px; font-weight:500; text-transform:uppercase; color:var(--muted); margin:36px 0 12px; padding-top:14px; border-top:1px solid var(--line) }}
.grid {{ display:grid; grid-template-columns:minmax(0,1fr); gap:16px }}
@media (min-width:900px) {{ .grid {{ grid-template-columns:repeat(2,minmax(0,1fr)); }} }}
.opt {{ background:var(--panel); border:1px solid var(--line); padding:14px; display:grid; gap:12px; align-content:start }}
.opt header {{ display:flex; align-items:center; gap:12px }}
.num {{ font-size:28px; font-weight:500; min-width:1.6em }}
.opt h2 {{ font-size:19px; margin:0; line-height:1.2 }}
.reco {{ margin-left:auto; font-size:11px; text-transform:uppercase; background:var(--tag); color:var(--tag-fg); padding:4px 8px }}
.opt img {{ display:block; width:100%; height:auto }}
.row {{ display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr) minmax(0,.42fr); gap:10px; align-items:center }}
.meta {{ display:grid; grid-template-columns:minmax(0,1fr); gap:12px; align-items:center }}
.sws {{ list-style:none; margin:0; padding:0; display:grid; gap:6px }}
.sws li {{ display:flex; align-items:center; gap:10px; font-size:13px }}
.sws b {{ font-weight:600; margin-right:8px }}
.sw {{ width:22px; height:22px; flex:none; background:var(--c); border:1px solid var(--line) }}
code {{ font-size:12px; color:var(--muted) }}
.fav {{ image-rendering:pixelated; max-width:260px }}
.k {{ font-size:11px; color:var(--muted); margin:6px 0 0 }}
.why {{ margin:0; max-width:70ch }}
.end {{ margin-top:36px; color:var(--muted); max-width:62ch }}
@media (max-width:640px) {{
  .row {{ grid-template-columns:minmax(0,1fr) minmax(0,1fr); }}
  .row .ic {{ grid-column:1 / -1; max-width:120px }}
  .cur {{ grid-template-columns:minmax(0,1fr) }}
}}
</style>

<div class="wrap">
  <p class="eyebrow">wubba · direction A · couleur de marque</p>
  <h1>Couleurs wubba</h1>
  <p class="lede">Le même logo, douze couleurs. Pour chaque option : la bannière X, le logo sur fond clair et sombre, l'icône, et le favicon rendu à 16, 24, 32 et 48 pixels réels. Réponds-moi simplement avec le numéro.</p>
  <figure class="cur"><img src="{current}" alt="Version actuelle : encre et point rouge"><figcaption>Point de départ écarté : encre et point rouge, trop proches du logo Ironman.</figcaption></figure>
  {cards}
  <p class="end">Les couleurs viennent seules : le dessin du logo ne bouge pas. Une fois la couleur choisie, on passe à la typographie.</p>
</div>
"""


if __name__ == "__main__":
    build()
