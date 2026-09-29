"""Variantes des meilleures directions : palettes alternatives, variantes du signe (A), mises en page de bannières.

    python3 src/variants.py palettes      # toutes les palettes alternatives + planches
    python3 src/variants.py marks         # variantes du signe de la direction A
"""
from __future__ import annotations

import copy
import sys

import compose
from directions import BY_CODE
from directions.base import Palette

P = Palette
PALETTES = {
    "A": [
        ("signal", "Signal (référence)", P("#0E0F12", "#F1F0EC", "#FF2A36", names={"ink": "Encre", "paper": "Papier", "accent": "Signal"})),
        ("magenta", "Rose direct", P("#0E0D12", "#F3F1F4", "#FF2E93", names={"ink": "Encre", "paper": "Papier", "accent": "Rose direct"})),
        ("outremer", "Outremer", P("#0B0D1A", "#F1F2F7", "#3346FF", names={"ink": "Nuit", "paper": "Givre", "accent": "Outremer"})),
        ("vert", "Vert en ligne", P("#0C120F", "#F1F4F1", "#00C45A", names={"ink": "Encre verte", "paper": "Papier", "accent": "En ligne"})),
        ("ambre", "Ambre REC", P("#12100C", "#F3EFE6", "#FF9F1C", names={"ink": "Encre chaude", "paper": "Papier", "accent": "Ambre"})),
        ("volt", "Volt", P("#0B0C0E", "#F2F3F0", "#C8F500", names={"ink": "Carbone", "paper": "Blanc", "accent": "Volt"})),
        ("mono", "Monochrome pur", P("#000000", "#FFFFFF", "#000000", names={"ink": "Noir", "paper": "Blanc", "accent": "Noir"})),
    ],
    "D": [
        ("nuit", "Nuit et ambre (référence)", P("#0B1A2B", "#EFF2EE", "#FFB23F", accent2="#FF6B5B", names={"ink": "Nuit", "paper": "Écume", "accent": "Ambre"})),
        ("polaire", "Polaire", P("#0A2233", "#EEF6F8", "#FF5A36", names={"ink": "Glace profonde", "paper": "Glace", "accent": "Fusée de détresse"})),
        ("crepuscule", "Crépuscule", P("#1B1330", "#F3EEF6", "#FF8A5B", names={"ink": "Crépuscule", "paper": "Brume", "accent": "Pêche"})),
        ("pleine-mer", "Pleine mer", P("#06283D", "#E9F1F4", "#F2C14E", names={"ink": "Abysse", "paper": "Écume", "accent": "Or"})),
    ],
    "H": [
        ("ambre", "Ambre phosphore (référence)", P("#0C0C0A", "#ECE8DC", "#FFB000", names={"ink": "Terminal", "paper": "Listing", "accent": "Ambre"})),
        ("vert", "Vert phosphore", P("#07110A", "#E6EFE4", "#33FF66", names={"ink": "Terminal", "paper": "Listing", "accent": "Phosphore"})),
        ("rapport", "Rapport (curseur rouge)", P("#111111", "#F2F2F0", "#FF3B30", names={"ink": "Noir", "paper": "Blanc", "accent": "Rouge"})),
        ("ecran-bleu", "Écran bleu", P("#1532C2", "#EEF1FF", "#FFD400", names={"ink": "Bleu écran", "paper": "Blanc", "accent": "Jaune"})),
    ],
    "E": [
        ("outremer", "Outremer (référence)", P("#0A0A0A", "#F7F6F2", "#2340FF", names={"ink": "Noir", "paper": "Blanc cassé", "accent": "Outremer"})),
        ("laque", "Laque rouge", P("#0A0A0A", "#F7F6F2", "#E3262F", names={"ink": "Noir", "paper": "Blanc cassé", "accent": "Laque"})),
        ("emeraude", "Émeraude", P("#0A0A0A", "#F5F6F2", "#0E8A5F", names={"ink": "Noir", "paper": "Blanc", "accent": "Émeraude"})),
        ("noir", "Noir seul", P("#0A0A0A", "#FFFFFF", "#0A0A0A", names={"ink": "Noir", "paper": "Blanc", "accent": "Noir"})),
    ],
    "F": [
        ("violet", "Violet et lime (référence)", P("#15122A", "#F4F1FF", "#7B5CFF", accent2="#C8FF3A",
                                                    custom={"banner": {"bg": "#7B5CFF", "fg": "#F4F1FF", "accent": "#15122A", "fg2": "#C8FF3A"}},
                                                    names={"ink": "Nuit violette", "paper": "Lilas", "accent": "Violet", "accent2": "Lime"})),
        ("bonbon", "Bonbon", P("#1E0B1A", "#FFF0F7", "#FF4FA3", accent2="#FFE14F",
                                custom={"banner": {"bg": "#FF4FA3", "fg": "#FFF0F7", "accent": "#1E0B1A", "fg2": "#FFE14F"}},
                                names={"ink": "Réglisse", "paper": "Guimauve", "accent": "Bonbon", "accent2": "Citron"})),
        ("orange", "Orange et ciel", P("#0F1B3D", "#FFF4E8", "#FF6B2C", accent2="#8FD3FF",
                                        custom={"banner": {"bg": "#FF6B2C", "fg": "#FFF4E8", "accent": "#0F1B3D", "fg2": "#0F1B3D"}},
                                        names={"ink": "Marine", "paper": "Crème", "accent": "Orange", "accent2": "Ciel"})),
    ],
    "J": [
        ("outremer", "Outremer et cyan (référence)", P("#0E1022", "#F3F4FA", "#2B3DFF", accent2="#1ED6F0",
                                                        custom={"banner": {"bg": "#2B3DFF", "fg": "#F3F4FA", "accent": "#1ED6F0", "fg2": "#1ED6F0"}},
                                                        names={"ink": "Minuit", "paper": "Givre", "accent": "Outremer", "accent2": "Cyan"})),
        ("oscillo", "Oscilloscope", P("#07120D", "#EEF5F0", "#19E68C",
                                       custom={"banner": {"bg": "#07120D", "fg": "#EEF5F0", "accent": "#19E68C", "fg2": "#19E68C"}},
                                       names={"ink": "Écran", "paper": "Papier", "accent": "Trace verte"})),
        ("corail", "Ardoise et corail", P("#111827", "#F5F5F4", "#FF5A5F",
                                           custom={"banner": {"bg": "#111827", "fg": "#F5F5F4", "accent": "#FF5A5F", "fg2": "#FF5A5F"}},
                                           names={"ink": "Ardoise", "paper": "Blanc", "accent": "Corail"})),
    ],
    # O : la couleur de la touche W est l'axe naturel de variation (comme une keycap artisan)
    "O": [
        ("lilas", "Lilas (référence)", P("#141518", "#ECEAE6", "#A98BFF", accent2="#2A2C31",
                                          names={"ink": "Châssis", "paper": "Touche claire", "accent": "Touche W", "accent2": "Touche sombre"})),
        ("echap", "Rouge Échap", P("#121214", "#EDEBE7", "#FF4D3A", accent2="#2A2B30",
                                    names={"ink": "Châssis", "paper": "Touche claire", "accent": "Rouge Échap", "accent2": "Touche sombre"})),
        ("jaune", "Jaune", P("#141414", "#EEEBE3", "#FFC933", accent2="#2B2B2E",
                              names={"ink": "Châssis", "paper": "Touche claire", "accent": "Jaune", "accent2": "Touche sombre"})),
        ("menthe", "Menthe", P("#101614", "#EAEEEB", "#4FE0A6", accent2="#26302C",
                                names={"ink": "Châssis", "paper": "Touche claire", "accent": "Menthe", "accent2": "Touche sombre"})),
        ("cyan", "Cyan", P("#0F1418", "#E8EDEF", "#34D6F5", accent2="#27303A",
                            names={"ink": "Châssis", "paper": "Touche claire", "accent": "Cyan", "accent2": "Touche sombre"})),
        ("retro", "Beige rétro", P("#221F1A", "#E9E2D0", "#E8572A", accent2="#3A3630",
                                    names={"ink": "Brun", "paper": "Beige", "accent": "Orange", "accent2": "Touche brune"})),
    ],
    # M : l'encre du tampon ; chaque encre a sa version claire pour les fonds sombres
    "M": [
        ("bleu", "Bleu tampon (référence)", P("#101014", "#EFEFEC", "#3A45D8",
                                               custom={"dark": {"bg": "#101014", "fg": "#EFEFEC", "accent": "#8E96FF", "fg2": "#8E96FF"}},
                                               names={"ink": "Encre", "paper": "Papier", "accent": "Encre à tampon"})),
        ("rouge", "Rouge « conforme »", P("#141011", "#F2EFEC", "#D7263D",
                                          custom={"dark": {"bg": "#141011", "fg": "#F2EFEC", "accent": "#FF6B7A", "fg2": "#FF6B7A"}},
                                          names={"ink": "Encre", "paper": "Papier", "accent": "Rouge tampon"})),
        ("vert", "Vert administratif", P("#0F1411", "#EEF0EC", "#1E7A4C",
                                          custom={"dark": {"bg": "#0F1411", "fg": "#EEF0EC", "accent": "#5FD39A", "fg2": "#5FD39A"}},
                                          names={"ink": "Encre", "paper": "Papier", "accent": "Vert tampon"})),
        ("violet", "Violet encre", P("#121016", "#F0EEF2", "#6B3FC4",
                                      custom={"dark": {"bg": "#121016", "fg": "#F0EEF2", "accent": "#B59BFF", "fg2": "#B59BFF"}},
                                      names={"ink": "Encre", "paper": "Papier", "accent": "Violet tampon"})),
        ("noir", "Encre noire", P("#101010", "#F2F1ED", "#101010", names={"ink": "Encre", "paper": "Papier", "accent": "Noir"})),
    ],
    # N : le carton et la couleur du trait
    "N": [
        ("kraft", "Kraft et rouge (référence)", P("#161412", "#D6B98A", "#E0442F", accent2="#F3EBDD",
                                                   names={"ink": "Marqueur", "paper": "Kraft", "accent": "Rouge", "accent2": "Étiquette"})),
        ("rose", "Kraft et rose fluo", P("#161412", "#D6B98A", "#FF3EA5", accent2="#F3EBDD",
                                          names={"ink": "Marqueur", "paper": "Kraft", "accent": "Rose fluo", "accent2": "Étiquette"})),
        ("blanc", "Carton blanc et bleu stylo", P("#141414", "#ECE9E2", "#2F5BFF", accent2="#FFFFFF",
                                                   names={"ink": "Marqueur", "paper": "Carton blanc", "accent": "Bleu stylo", "accent2": "Étiquette"})),
        ("noir", "Boîte noire, marqueur argent", P("#151515", "#D9DCE1", "#E0442F", accent2="#F3EBDD",
                                                    custom={"light": {"bg": "#151515", "fg": "#D9DCE1", "accent": "#E0442F", "fg2": "#F3EBDD"},
                                                            "dark": {"bg": "#D9DCE1", "fg": "#151515", "accent": "#E0442F", "fg2": "#F3EBDD"}},
                                                    names={"ink": "Boîte noire", "paper": "Argent", "accent": "Rouge", "accent2": "Étiquette"})),
    ],
}


def with_palette(d, pal):
    v = copy.copy(d)
    v.palette = pal
    return v


def build_palettes(codes=None):
    for code, items in PALETTES.items():
        if codes and code not in codes:
            continue
        d = BY_CODE[code]
        rows = []
        for slug, label, pal in items:
            v = with_palette(d, pal)
            out = compose.OPT / f"{d.code}-{d.key}" / "palettes" / slug
            out.mkdir(parents=True, exist_ok=True)
            import svgout
            wm = v.wordmark()
            box = v.bounds(wm)
            pad = (box[3] - box[1]) * 0.35
            for kind in ("light", "dark"):
                sch = pal.scheme(kind)
                compose.save(svgout.svg_doc(v.color(wm, sch), box, "wubba", pad=pad, bg=sch["bg"]),
                             out / f"logo-{kind}", png_width=1200)
            compose.save(compose.page(256, 256, compose.tile_layers(v, pal.scheme(v.icon_scheme))), out / "icon",
                         png_width=256)
            compose.save(compose.banner(v, "x-header"), out / "x-header", png_width=1500)
            rows.append((slug, label, pal, out))
        sheet(d, rows)
        print(code, len(rows), "palettes")


def sheet(d, rows):
    """Planche des palettes d'une direction : une ligne par palette."""
    from pathlib import Path
    html_rows = []
    for slug, label, pal, out in rows:
        chips = "".join(f'<span class="chip" style="background:{c}" title="{c}"></span><code>{c}</code>'
                        for _, c, _ in pal.chips())
        html_rows.append(f"""<div class="row"><div class="lab"><b>{label}</b><div class="chips">{chips}</div></div>
<img src="file://{out / 'logo-light.png'}"><img src="file://{out / 'logo-dark.png'}">
<img class="ic" src="file://{out / 'icon.png'}"><img src="file://{out / 'x-header.png'}"></div>""")
    root = compose.ROOT
    html = f"""<!doctype html><meta charset="utf-8"><style>
@font-face{{font-family:"M";src:url("file://{root / '.fonts' / 'MartianMono[wdth,wght].ttf'}")}}
body{{margin:0;background:#EDEDEA;font:12px 'M';color:#222;width:1900px}}
h1{{font:600 26px 'M';margin:28px 24px 6px}} p{{margin:0 24px 16px;color:#666}}
.row{{display:grid;grid-template-columns:230px 330px 330px 110px 1fr;gap:14px;align-items:center;padding:12px 24px;border-top:1px solid #D2D1CC}}
.row img{{width:100%;display:block}} .row img.ic{{width:110px}}
.lab b{{display:block;font-size:13px;margin-bottom:8px}}
.chips{{display:grid;grid-template-columns:22px 1fr;gap:4px 8px;align-items:center}}
.chip{{width:22px;height:22px;display:block;border:1px solid rgba(0,0,0,.12)}} code{{font:11px 'M';color:#555}}
</style><h1>{d.code} · {d.name} — palettes</h1><p>Même dessin, couleurs différentes. La forme est choisie à part.</p>
{''.join(html_rows)}"""
    base = compose.OPT / f"{d.code}-{d.key}"
    hp = base / "_palettes.html"
    hp.write_text(html)
    compose.render_html(hp, base / "palettes.png", 1900, "auto", 1)
    hp.unlink()


MARKS = [
    ("rond", "Point rond (référence)", {}),
    ("carre", "Point carré : le pixel", {"dot_shape": "square"}),
    ("anneau", "Anneau : le voyant REC éteint", {"dot_shape": "ring", "dot_d": 66}),
    ("reticule", "Réticule à la place du point", {"dot_shape": "cross", "dot_d": 60}),
    ("leger", "Graisse légère", {"S": 40, "Sr": 42, "H": 35, "w_D": 37, "dot_d": 54}),
    ("noir", "Graisse noire", {"S": 60, "Sr": 62, "H": 53, "w_D": 55, "dot_d": 68, "dot_gap": 17}),
    ("rondes", "Panses rondes (géométrique classique)", {"k_out": 0.5523, "k_in": 0.5523}),
    ("carrees", "Panses carrées (plus « matériel »)", {"k_out": 0.76, "k_in": 0.74}),
    ("tiret", "Sommet plein, point au-dessus", {"w_hm": 200, "dot_gap": 26, "dot_d": 56}),
]


def build_marks():
    """Variantes du signe de la direction A : même idée, dessins différents."""
    import svgout
    import wordmark as wm
    from directions.a_point import Point
    base = BY_CODE["A"]
    rows = []
    for slug, label, params in MARKS:
        p = wm.variant(**params)

        class V(Point):
            def wordmark(self, _p=p):
                body, dot = wm.wordmark(_p)
                return [(body, "fg"), (dot, "accent")]

            def symbol(self, _p=p):
                w, d = wm.symbol(_p)
                return [(w, "fg"), (d, "accent")]

            def symbol_small(self, _p=p):
                return self.symbol(_p)
        v = V()
        out = compose.OPT / "A-point" / "signes" / slug
        out.mkdir(parents=True, exist_ok=True)
        wmk = v.wordmark()
        box = v.bounds(wmk)
        pad = (box[3] - box[1]) * 0.35
        for kind in ("light", "dark"):
            sch = base.palette.scheme(kind)
            compose.save(svgout.svg_doc(v.color(wmk, sch), box, "wubba", pad=pad, bg=sch["bg"]),
                         out / f"logo-{kind}", png_width=1200)
        compose.save(compose.page(256, 256, compose.tile_layers(v, base.palette.scheme("dark"))), out / "icon",
                     png_width=256)
        compose.favicon_test(v, out)
        rows.append((slug, label, out))
    root = compose.ROOT
    html_rows = "".join(f"""<div class="row"><div class="lab"><b>A{i + 1}</b>{label}</div>
<img src="file://{o / 'logo-light.png'}"><img src="file://{o / 'logo-dark.png'}">
<img class="ic" src="file://{o / 'icon.png'}"><img class="fv" src="file://{o / 'favicon-test.png'}"></div>"""
                        for i, (slug, label, o) in enumerate(rows))
    html = f"""<!doctype html><meta charset="utf-8"><style>
@font-face{{font-family:"M";src:url("file://{root / '.fonts' / 'MartianMono[wdth,wght].ttf'}")}}
body{{margin:0;background:#EDEDEA;font:12px 'M';color:#222;width:1900px}}
h1{{font:600 26px 'M';margin:28px 24px 6px}} p{{margin:0 24px 16px;color:#666}}
.row{{display:grid;grid-template-columns:230px 420px 420px 120px 1fr;gap:16px;align-items:center;padding:12px 24px;border-top:1px solid #D2D1CC}}
.row img{{width:100%;display:block}} .row img.ic{{width:120px}} .row img.fv{{width:auto;max-width:100%;image-rendering:pixelated}}
.lab b{{display:block;font-size:22px;margin-bottom:6px}}
</style><h1>A · Le point de trop — variantes du signe</h1><p>Même idée, dessins différents. Favicon rendu à 16, 24, 32 et 48 px réels.</p>{html_rows}"""
    hp = compose.OPT / "A-point" / "_signes.html"
    hp.write_text(html)
    compose.render_html(hp, compose.OPT / "A-point" / "signes.png", 1900, "auto", 1)
    hp.unlink()
    print("A", len(rows), "signes")


TYPE_PAIRS = [
    ("T1", "Archivo Expanded · Instrument Sans · Martian Mono (référence)",
     ("Archivo", "Archivo[wdth,wght].ttf", "font-stretch:125%;font-weight:800"),
     ("Instrument Sans", "InstrumentSans[wdth,wght].ttf", "font-weight:400"),
     ("Martian Mono", "MartianMono[wdth,wght].ttf", "font-weight:500")),
    ("T2", "Bricolage Grotesque condensée · Inter · JetBrains Mono",
     ("Bricolage Grotesque", "BricolageGrotesque[opsz,wdth,wght].ttf", "font-stretch:75%;font-weight:800;font-variation-settings:'opsz' 96"),
     ("Inter", "Inter[opsz,wght].ttf", "font-weight:400"),
     ("JetBrains Mono", "JetBrainsMono[wght].ttf", "font-weight:500")),
    ("T3", "Familjen Grotesk · IBM Plex Sans · IBM Plex Mono",
     ("Familjen Grotesk", "FamiljenGrotesk[wght].ttf", "font-weight:700"),
     ("IBM Plex Sans", "IBMPlexSans[wdth,wght].ttf", "font-weight:400"),
     ("IBM Plex Mono", "IBMPlexMono-Medium.ttf", "font-weight:500")),
    ("T4", "Syne · Hanken Grotesk · DM Mono",
     ("Syne", "Syne[wght].ttf", "font-weight:800"),
     ("Hanken Grotesk", "HankenGrotesk[wght].ttf", "font-weight:400"),
     ("DM Mono", "DMMono-Medium.ttf", "font-weight:500")),
    ("T5", "Anybody étendue · Onest · Geist Mono",
     ("Anybody", "Anybody[wdth,wght].ttf", "font-stretch:140%;font-weight:850"),
     ("Onest", "Onest[wght].ttf", "font-weight:400"),
     ("Geist Mono", "GeistMono[wght].ttf", "font-weight:500")),
]


def build_type():
    """Paires typographiques candidates pour A, posées à côté du logo pour juger l'accord."""
    root = compose.ROOT
    fonts = root / ".fonts"
    faces, rows = set(), []
    for code, label, disp, body, mono in TYPE_PAIRS:
        for fam, file, _ in (disp, body, mono):
            faces.add((fam, file))
        rows.append(f"""<section><div class="light"><div class="top"><span class="code">{code}</span><span class="lab">{label}</span>
<img src="file://{compose.OPT / 'A-point' / 'logo-light-transparent.svg'}"></div>
<h2 style="font-family:'{disp[0]}';{disp[2]}">We build AI streamers who test gaming gear where it has no business working.</h2>
<p style="font-family:'{body[0]}';{body[2]}">The price is the license and the library, not the render. It covers a concept written for one product, eight to twelve assets cut from a single shoot, six months of paid usage on every channel, and category exclusivity for the term.</p>
<div class="data" style="font-family:'{mono[0]}';{mono[2]}"><span>ASSETS <b>8–12</b></span><span>RIGHTS <b>6 MO</b></span><span>DELIVERY <b>10–15 D</b></span><span>WUBBA.STUDIO</span></div></div>
<div class="dark"><h3 style="font-family:'{disp[0]}';{disp[2]}">wubba studio</h3>
<div class="data" style="font-family:'{mono[0]}';{mono[2]}"><span>● 9:16 · 1:1 · 16:9</span></div></div></section>""")
    ff = "\n".join(f'@font-face{{font-family:"{fam}";src:url("file://{fonts / file}");font-weight:100 900;font-stretch:50% 200%}}'
                   for fam, file in faces)
    html = f"""<!doctype html><meta charset="utf-8"><style>{ff}
@font-face{{font-family:"M";src:url("file://{fonts / 'MartianMono[wdth,wght].ttf'}")}}
body{{margin:0;background:#EDEDEA;width:1900px}}
h1{{font:600 26px 'M';margin:28px 24px 16px}}
section{{display:grid;grid-template-columns:1.6fr 1fr;margin:0 24px 18px}}
.light{{background:#F1F0EC;color:#0E0F12;padding:26px 34px}} .dark{{background:#0E0F12;color:#F1F0EC;padding:26px 34px;display:flex;flex-direction:column;justify-content:space-between}}
.top{{display:flex;align-items:center;gap:18px}} .top img{{height:44px;margin-left:auto}}
.code{{font:600 22px 'M'}} .lab{{font:12px 'M';color:#666}}
h2{{font-size:40px;line-height:1.04;margin:18px 0 14px;letter-spacing:-.01em;text-wrap:balance}}
h3{{font-size:64px;line-height:1;margin:0;letter-spacing:-.01em}}
p{{font-size:17px;line-height:1.5;margin:0 0 16px;max-width:70ch}}
.data{{display:flex;gap:26px;font-size:13px;letter-spacing:.06em;color:#5C5C5D}} .dark .data{{color:#FF2A36}}
.data b{{color:#0E0F12}}
</style><h1>A · Le point de trop — paires typographiques</h1>{''.join(rows)}"""
    hp = compose.OPT / "A-point" / "_type.html"
    hp.write_text(html)
    compose.render_html(hp, compose.OPT / "A-point" / "typo.png", 1900, "auto", 1)
    # une image par paire, pour le catalogue
    tdir = compose.OPT / "A-point" / "typo"
    tdir.mkdir(exist_ok=True)
    head = html.split("<h1>")[0]
    for (code, *_), row in zip(TYPE_PAIRS, rows):
        one = head + row.replace("margin:0 24px 18px", "margin:0")
        hp.write_text(one.replace("body{margin:0;background:#EDEDEA;width:1900px}",
                                  "body{margin:0;background:#EDEDEA;width:1852px}"))
        compose.render_html(hp, tdir / f"{code}.png", 1852, "auto", 1)
    hp.unlink()
    print("A", len(TYPE_PAIRS), "paires typo")


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "palettes"
    if what == "palettes":
        build_palettes(set(sys.argv[2:]) or None)
    elif what == "marks":
        build_marks()
    elif what == "type":
        build_type()
