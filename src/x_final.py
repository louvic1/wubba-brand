"""Bannière X retenue : la B2 (logo géant calé à droite) avec le point vert à gauche, derrière la photo de profil.

Fond noir, mot blanc, vert #72AC0E. Typo T2 (Sora, Figtree, JetBrains Mono).
Pour comparer : la même sur vert forêt, et l'ancienne sur blanc (archive).

    python3 src/x_final.py   ->  options/A-point/x-final/  +  section « Retenue » en tête de x-blanc/index.html
"""
from __future__ import annotations

import re

import cairosvg

import compose
import geom as g
import x_blanc as xb
from compose import page

BLACK, WHITE, FOREST, GREEN = "#000000", "#FFFFFF", "#0E2B22", "#72AC0E"
THEMES = {"noir": (BLACK, WHITE, GREEN), "foret": (FOREST, WHITE, GREEN), "blanc": (WHITE, FOREST, GREEN)}   # fond, mot, vert
KEEP = "noir"                                                    # la retenue va à la racine de x-final/, les autres en sous-dossier
OUT = compose.OPT / "A-point" / "x-final"
LABEL_FONT = ("JetBrainsMono[wght].ttf", {"wght": 500})          # l'utilitaire de la paire T2
DISC = (110, 160, 270)                                           # centre x, centre y (vers le haut), rayon


def use(theme):
    """x_blanc lit ses couleurs dans ses globales (fond, mot, point) : on les règle avant chaque rendu."""
    xb.WHITE, xb.FOREST, xb.LIME = THEMES[theme]
    return THEMES[theme]


def banner(theme):
    bg, word, green = use(theme)
    x, y, r = DISC
    disc = g.intersect(g.circle(x, y, r), g.rect(0, 0, xb.W, xb.H))
    layers, b = xb.logo((430, 175, 1420, 425), align="right")
    lab, _ = xb.label(b[2], b[1] - 90, 42, "right", font=LABEL_FONT, color=word)
    return page(xb.W, xb.H, [(disc, green)] + layers + [lab], bg=bg)


def avatar(theme, size=400):
    """La photo de profil assortie : le w et son point sur le fond de la bannière (X la recadre en cercle)."""
    bg, word, green = use(theme)
    m = size * 0.2
    placed, _ = xb.A.place(xb.A.symbol(), (m, m, size - m, size - m))
    return page(size, size, [(p, word if role == "fg" else green) for p, role in placed], bg=bg)


def export(theme):
    d = OUT if theme == KEEP else OUT / theme
    d.mkdir(parents=True, exist_ok=True)
    svg = banner(theme)
    base = d / "wubba-x-banniere"
    compose.save(svg, base, png_width=xb.W)
    cairosvg.svg2png(bytestring=svg.encode(), write_to=str(base) + "@2x.png", output_width=xb.W * 2)
    cairosvg.svg2png(bytestring=xb.preview(svg).encode(), write_to=str(base) + "-profil.png", output_width=xb.W)
    av = d / "wubba-photo-profil"
    compose.save(avatar(theme), av, png_width=400)
    cairosvg.svg2png(bytestring=avatar(theme).encode(), write_to=str(av) + "@2x.png", output_width=800)
    return base, av


def build():
    out = {t: export(t) for t in THEMES}
    base, av = out[KEEP]
    fbase, _ = out["foret"]

    # planche T2 sur le fond retenu, avec la bannière retenue
    bg, word, green = use(KEEP)
    code, names, note, disp, body, mono = [t for t in xb.TYPES if t[0] == "T2"][0]
    hp = OUT / "_T2.html"
    hp.write_text(xb.type_specimen(code, names, note, disp, body, mono, base.with_suffix(".png")))
    spec = OUT / "T2-retenue.png"
    compose.render_html(hp, spec, 1600, "auto", 1)
    hp.unlink()
    xb.trim(spec, bg=tuple(int(bg[i:i + 2], 16) for i in (1, 3, 5)))

    imgs = {"b": xb.webp(base.with_suffix(".png"), "final", 1500), "pv": xb.webp(str(base) + "-profil.png", "final-profil", 1000),
            "av": xb.webp(av.with_suffix(".png"), "final-avatar", 400), "t2": xb.webp(spec, "final-t2", 1600),
            "fb": xb.webp(fbase.with_suffix(".png"), "final-foret", 1500),
            "fpv": xb.webp(str(fbase) + "-profil.png", "final-foret-profil", 1000)}
    swatches = "".join(f'<span><i style="background:{c}"></i><code>{c}</code> {n}</span>\n      '
                       for c, n in ((bg, "fond"), (word, "mot"), (green, "vert")))
    section = f"""
  <h2>Retenue</h2>
  <article class="opt final">
    <header><span class="num">B2</span><h3>Fond noir, point vert à gauche</h3></header>
    <img src="{imgs['b']}" alt="Bannière X retenue sur fond noir : logo blanc géant à droite, disque vert à gauche">
    <figure class="pv"><img src="{imgs['pv']}" alt="La bannière sur un profil X, la photo de profil noire posée sur le disque vert"><figcaption>Sur un profil X : la photo de profil noire se pose sur le disque vert</figcaption></figure>
    <div class="swap">
      {swatches}<img class="av" src="{imgs['av']}" alt="Photo de profil assortie">
    </div>
    <p>Typo T2 : Sora pour les titres, Figtree pour le texte, JetBrains Mono pour les petites mentions comme « AI STREAMERS ».</p>
    <img src="{imgs['t2']}" alt="Planche T2 sur fond noir">
  </article>
  <article class="opt">
    <header><span class="num">B2</span><h3>À comparer : fond vert forêt</h3></header>
    <img src="{imgs['fb']}" alt="La même bannière sur fond vert forêt">
    <figure class="pv"><img src="{imgs['fpv']}" alt="La version vert forêt sur un profil X"><figcaption>Sur un profil X</figcaption></figure>
    <p>La même bannière sur vert forêt {FOREST}. Le noir avec ce vert rappelle Nvidia, dont le vert est #76B900.</p>
  </article>
"""
    page_path = xb.PAGE / "index.html"
    doc = page_path.read_text()
    if "<h2>Retenue</h2>" in doc:
        start = doc.index("  <h2>Retenue</h2>")
        doc = doc[:start] + doc[doc.index("  <h2>Bannières X</h2>"):]
    style = """.final { border-color:var(--fg) }
.swap { display:flex; flex-wrap:wrap; align-items:center; gap:14px 22px }
.swap span { display:flex; align-items:center; gap:8px; font-size:14px }
.swap i { width:26px; height:26px; display:inline-block; border:1px solid var(--line) }
.swap .av { width:96px; height:96px; border-radius:50%; border:1px solid var(--line); margin-left:auto }
"""
    if ".swap {" not in doc:
        doc = doc.replace("</style>", style + "</style>", 1)
    doc = doc.replace("  <h2>Bannières X</h2>", section + "\n  <h2>Bannières X</h2>", 1)
    doc = re.sub(r'<p class="eyebrow">.*?</p>', '<p class="eyebrow">wubba · direction A · bannière X retenue</p>', doc, count=1)
    lede = ('<p class="lede">Retenu : la bannière B2 sur fond noir, avec le point vert à gauche, et la typo T2. '
            "Juste dessous, la même sur vert forêt pour comparer. Les cinq bannières et les six typographies d'origine suivent.</p>")
    doc = re.sub(r'<p class="lede">.*?</p>', lede, doc, count=1, flags=re.S)
    page_path.write_text(doc)
    print("finale :", ", ".join(sorted(str(p.relative_to(OUT)) for p in OUT.rglob("*.png"))))


if __name__ == "__main__":
    build()
