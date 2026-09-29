"""Catalogue de toutes les options, en une page HTML publiable (Artifact) avec ses images en WebP.

    python3 src/catalogue.py      ->  catalogue/index.html + catalogue/img/*.webp

Chaque option a un bouton « Je garde ». Les choix vont dans la base de la page (capability db,
collection "picks") pour que Claude puisse les relire ; sans base, ils restent dans le navigateur.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

from PIL import Image

import compose
import critique
import layouts
import variants
from directions import ALL, BY_CODE

ROOT = compose.ROOT
OUT = ROOT / "catalogue"
IMG = OUT / "img"
DATE = "29 septembre 2026"
SHORTLIST = ["A", "O", "D", "H"]
# directions gardées pour mémoire mais déconseillées : la faille qui les disqualifie
WEAK = {
    "K": "Le réticule est le symbole le plus courant du jeu de tir : rien ici n'appartient à Wubba, et un « + » dans une tuile se lit bouton « ajouter ».",
    "L": "L'effet tranché est partout depuis 2020 ; même tenu à une seule coupe propre, il ne devient jamais propriétaire.",
}


# ------------------------------------------------------------------ images

def webp(src, name, max_w=1600, q=84):
    IMG.mkdir(parents=True, exist_ok=True)
    im = Image.open(src).convert("RGB")
    if im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    dst = IMG / f"{name}.webp"
    im.save(dst, "WEBP", quality=q, method=6)
    return f"img/{name}.webp", im.size


def strip(paths, name, height=220, gap=16, bg=(237, 237, 234), max_w=1800):
    """Assemble plusieurs images sur une ligne, à hauteur égale."""
    ims = [Image.open(p).convert("RGB") for p in paths]
    ims = [im.resize((round(im.width * height / im.height), height), Image.LANCZOS) for im in ims]
    W = sum(im.width for im in ims) + gap * (len(ims) - 1)
    out = Image.new("RGB", (W, height), bg)
    x = 0
    for im in ims:
        out.paste(im, (x, 0))
        x += im.width + gap
    tmp = IMG / f"_{name}.png"
    IMG.mkdir(parents=True, exist_ok=True)
    out.save(tmp)
    res = webp(tmp, name, max_w=max_w)
    tmp.unlink()
    return res


def esc(s):
    return html.escape(s, quote=True)


# ------------------------------------------------------------------ fragments

def pick_btn(pid, label="Je garde"):
    return f'<button class="pick" type="button" data-pick="{pid}" aria-pressed="false"><span class="box"></span>{label}</button>'


def score_bars(code):
    v1 = critique.V1[code][0]
    v2 = critique.V2.get(code, v1)
    rows = []
    for dim, a, b in zip(critique.DIMS, v1, v2):
        delta = f'<em>+{b - a}</em>' if b > a else ""
        rows.append(f'<li><span>{dim}</span><i class="bar"><b style="width:{b * 20}%"></b><s style="width:{a * 20}%"></s></i>'
                    f'<strong>{b}</strong>{delta}</li>')
    return f'<ul class="score">{"".join(rows)}</ul>'


def chips(pal):
    return "".join(f'<span class="chip" style="--c:{c}" title="{esc(n)} {c}"></span>' for n, c, _ in pal.chips())


def direction_block(d, imgs):
    code = d.code
    v1, notes = critique.V1[code]
    v2 = critique.V2.get(code, v1)
    changes = "".join(f"<li>{esc(c)}</li>" for c in critique.CHANGES.get(code, []))
    issues = "".join(f"<li>{esc(c)}</li>" for c in notes)
    why = "".join(f"<li>{esc(w)}</li>" for w in d.why)
    fonts = f"{esc(d.display.family)} · {esc(d.body.family)} · {esc(d.mono.family)}"
    i = imgs[code]
    return f"""
<article class="dir" id="dir-{code}">
  <header class="dir-head">
    <div class="dir-id"><span class="code">{code}</span><div><h3>{esc(d.name)}</h3><p class="kind">{esc(d.mark_type)}</p></div></div>
    <div class="dir-score"><span class="big">{sum(v2)}</span><span class="of">/50</span><span class="was">v1 : {sum(v1)}</span></div>
    {'<span class="weak-badge">Écartée</span>' if code in WEAK else ''}
    {pick_btn(f"dir-{code}", "Je garde cette direction")}
  </header>
  <p class="idea">{esc(d.idea)}</p>
  {f'<p class="weak-note"><b>Je ne la recommande pas.</b> {esc(WEAK[code])}</p>' if code in WEAK else ''}
  <div class="dir-logos">
    <figure><img src="{i['light']}" alt="Logo {esc(d.name)} sur fond clair" loading="lazy"></figure>
    <figure><img src="{i['dark']}" alt="Logo {esc(d.name)} sur fond sombre" loading="lazy"></figure>
    <figure class="sq"><img src="{i['icon']}" alt="Icône {esc(d.name)}" loading="lazy"></figure>
  </div>
  <div class="dir-banners">
    <figure><img src="{i['x']}" alt="Bannière X {esc(d.name)}" loading="lazy"><figcaption>X · 1500 × 500</figcaption></figure>
    <figure><img src="{i['og']}" alt="Aperçu de lien {esc(d.name)}" loading="lazy"><figcaption>Aperçu de lien · 1200 × 630</figcaption></figure>
  </div>
  <div class="dir-facts">
    <div><h4>Pourquoi</h4><ul>{why}</ul><p class="risk"><b>Risque</b> {esc(d.risk)}</p></div>
    <div><h4>Critique v1 → v2</h4>{score_bars(code)}</div>
    <div><h4>Ce qui clochait en v1</h4><ul>{issues}</ul><h4>Ce que la v2 a changé</h4><ul>{changes or '<li>Rien : la v1 tenait.</li>'}</ul>
      <h4>Palette</h4><p class="chips">{chips(d.palette)}</p><h4>Typo</h4><p class="small">{fonts}</p>
      <h4>Favicon réel</h4><img class="fav" src="{i['fav']}" alt="Favicon à 16, 24, 32 et 48 px" loading="lazy">
      <p><a class="board-link" href="{i['board']}">Ouvrir la planche complète</a></p></div>
  </div>
</article>"""


def build():
    OUT.mkdir(exist_ok=True)
    for f in list(IMG.glob("*.webp")) + list(IMG.glob("*.mp4")) if IMG.exists() else []:
        f.unlink()
    imgs = {}
    for d in ALL:
        o = compose.OPT / f"{d.code}-{d.key}"
        imgs[d.code] = {
            "light": webp(o / "logo-light.png", f"{d.code}-logo-light", 900)[0],
            "dark": webp(o / "logo-dark.png", f"{d.code}-logo-dark", 900)[0],
            "icon": webp(o / "icon.png", f"{d.code}-icon", 256)[0],
            "fav": webp(o / "favicon-test.png", f"{d.code}-favicon", 700, 92)[0],
            "x": webp(o / "x-header.png", f"{d.code}-x", 1500)[0],
            "og": webp(o / "og.png", f"{d.code}-og", 1200)[0],
            "board": webp(o / "board.png", f"{d.code}-board", 1600, 80)[0],
        }
    overview = webp(compose.OPT / "overview.png", "overview", 1900, 82)[0]

    # -------- variantes : signes A
    signs = []
    for n, (slug, label, _) in enumerate(variants.MARKS, 1):
        o = compose.OPT / "A-point" / "signes" / slug
        src, _ = strip([o / "logo-light.png", o / "logo-dark.png", o / "icon.png"], f"A-signe-{slug}", 200)
        signs.append((f"sign-A{n}", f"A{n}", label, src))
    # -------- variantes : palettes
    palettes = {}
    by_score = lambda c: -sum(critique.V2.get(c, critique.V1[c][0]))  # noqa: E731
    for code, items in sorted(variants.PALETTES.items(), key=lambda kv: by_score(kv[0])):
        d = BY_CODE[code]
        rows = []
        for slug, label, pal in items:
            o = compose.OPT / f"{d.code}-{d.key}" / "palettes" / slug
            src, _ = strip([o / "logo-light.png", o / "logo-dark.png", o / "icon.png", o / "x-header.png"],
                           f"{code}-pal-{slug}", 180)
            rows.append((f"pal-{code}-{slug}", label, pal, src))
        palettes[code] = rows
    # -------- variantes : mises en page
    lays = {}
    for code in ["A", "O", "D", "H", "E", "F", "J", "P", "Q"]:
        d = BY_CODE[code]
        o = compose.OPT / f"{d.code}-{d.key}" / "layouts"
        items = []
        for slug, label in layouts.X_NAMES:
            items.append((f"lay-{code}-x-{slug}", f"X · {label}", webp(o / f"x-{slug}.png", f"{code}-lay-x-{slug}", 1200)[0]))
        for slug, label in layouts.OG_NAMES:
            items.append((f"lay-{code}-og-{slug}", f"Lien · {label}", webp(o / f"og-{slug}.png", f"{code}-lay-og-{slug}", 1000)[0]))
        lays[code] = items
    # -------- variantes : typo
    types = []
    for code, label, *_ in variants.TYPE_PAIRS:
        types.append((f"type-A-{code}", code, label,
                      webp(compose.OPT / "A-point" / "typo" / f"{code}.png", f"A-type-{code}", 1500)[0]))

    # -------- animations (WebP animé copié tel quel, carton 9:16 en MP4)
    import shutil
    motions = []
    for d in sorted(ALL, key=lambda d: -sum(critique.V2.get(d.code, critique.V1[d.code][0]))):
        m = compose.OPT / f"{d.code}-{d.key}" / "motion"
        if (m / "sting.webp").exists():
            shutil.copyfile(m / "sting.webp", IMG / f"{d.code}-sting.webp")
            shutil.copyfile(m / "endcard-9x16.mp4", IMG / f"{d.code}-endcard.mp4")
            # affiche du carton vertical : sa dernière image, pour que la vidéo ne soit jamais un rectangle noir
            import subprocess
            import imageio_ffmpeg
            tmp = IMG / f"_{d.code}-poster.png"
            subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-hide_banner", "-loglevel", "error", "-y", "-sseof", "-0.2",
                            "-i", str(m / "endcard-9x16.mp4"), "-frames:v", "1", str(tmp)], check=True)
            poster = webp(tmp, f"{d.code}-endcard-poster", 540)[0]
            tmp.unlink()
            motions.append((d, f"img/{d.code}-sting.webp", f"img/{d.code}-endcard.mp4", poster))
    # -------- mises en situation
    mocks = []
    for d in sorted(ALL, key=lambda d: -sum(critique.V2.get(d.code, critique.V1[d.code][0]))):
        m = compose.OPT / f"{d.code}-{d.key}" / "mockups"
        if (m / "stickers.png").exists():
            mocks.append((d, webp(m / "stickers.png", f"{d.code}-stickers", 1200)[0],
                          webp(m / "signature.png", f"{d.code}-signature", 900, 90)[0]))

    # -------- couvertures de chaîne
    import covers as cv
    chans = []
    for d in sorted(ALL, key=lambda d: -sum(critique.V2.get(d.code, critique.V1[d.code][0]))):
        o = compose.OPT / f"{d.code}-{d.key}"
        if d.code in cv.COVERS and (o / "youtube.png").exists():
            chans.append((d, webp(o / "youtube.png", f"{d.code}-youtube", 1600)[0],
                          webp(o / "youtube-zones.png", f"{d.code}-youtube-zones", 900)[0],
                          webp(o / "twitch.png", f"{d.code}-twitch", 1200)[0]))

    page = render(imgs, overview, signs, palettes, lays, types, motions, mocks, chans)
    (OUT / "index.html").write_text(page)
    files = list(IMG.glob("*.webp")) + list(IMG.glob("*.mp4"))
    n = len(files)
    size = sum(f.stat().st_size for f in files) / 1e6
    print(f"catalogue : {n} images, {size:.1f} Mo, page {len(page) / 1e3:.0f} ko")


# ------------------------------------------------------------------ page

def render(imgs, overview, signs, palettes, lays, types, motions, mocks, chans):
    ranked = sorted(ALL, key=lambda d: -sum(critique.V2.get(d.code, critique.V1[d.code][0])))
    short = []
    reasons = {
        "A": "La plus forte et la plus propre. L'idée du studio dite par la typo, lisible à 16 px, sérieuse devant un directeur marketing.",
        "D": "La plus chaleureuse. Elle sort du noir néon du secteur et raconte les lieux impossibles sans dessiner de bateau.",
        "H": "La plus pince-sans-rire. Un rapport de test qui s'écrit en direct ; le curseur clignote tout seul en vidéo.",
        "O": "La plus gaming sans cliché. Le nom tapé sur des touches, le W allumé : dans tous les jeux de tir, W veut dire avancer.",
    }
    for code in SHORTLIST:
        d = BY_CODE[code]
        s = sum(critique.V2[code])
        short.append(f"""<a class="short" href="#dir-{code}"><img src="{imgs[code]['dark']}" alt="Logo {esc(d.name)}">
<div class="short-meta"><span class="code">{code}</span><b>{esc(d.name)}</b><span class="s">{s}/50</span></div>
<p>{esc(reasons[code])}</p></a>""")

    table_rows = []
    for d in ranked:
        v1 = sum(critique.V1[d.code][0])
        v2 = sum(critique.V2.get(d.code, critique.V1[d.code][0]))
        table_rows.append(f"""<tr><td><a href="#dir-{d.code}">{d.code}</a></td><td>{esc(d.name)}{' <span class="weak-badge">écartée</span>' if d.code in WEAK else ''}</td><td class="hide-s">{esc(d.mark_type)}</td>
<td class="num">{v1}</td><td class="num"><b>{v2}</b></td><td class="chips">{chips(d.palette)}</td><td>{pick_btn(f"dir-{d.code}", "")}</td></tr>""")

    dirs = "".join(direction_block(d, imgs) for d in ALL)

    sign_cards = "".join(f"""<figure class="opt"><img src="{src}" alt="{esc(label)}" loading="lazy">
<figcaption><b>{code}</b> {esc(label)}{pick_btn(pid, "")}</figcaption></figure>""" for pid, code, label, src in signs)

    pal_blocks = []
    for code, rows in palettes.items():
        d = BY_CODE[code]
        cards = "".join(f"""<figure class="opt wide"><img src="{src}" alt="{esc(d.name)} en palette {esc(label)}" loading="lazy">
<figcaption><span class="chips">{chips(pal)}</span><b>{esc(label)}</b>{pick_btn(pid, "")}</figcaption></figure>""" for pid, label, pal, src in rows)
        pal_blocks.append(f'<h3 class="vh"><a href="#dir-{code}">{code}</a> · {esc(d.name)}</h3><div class="opts one">{cards}</div>')

    lay_blocks = []
    for code, items in lays.items():
        d = BY_CODE[code]
        cards = "".join(f"""<figure class="opt"><img src="{src}" alt="{esc(d.name)} : {esc(label)}" loading="lazy">
<figcaption><b>{esc(label)}</b>{pick_btn(pid, "")}</figcaption></figure>""" for pid, label, src in items)
        lay_blocks.append(f'<h3 class="vh"><a href="#dir-{code}">{code}</a> · {esc(d.name)}</h3><div class="opts two">{cards}</div>')

    type_cards = "".join(f"""<figure class="opt wide"><img src="{src}" alt="{esc(label)}" loading="lazy">
<figcaption><b>{code}</b> {esc(label)}{pick_btn(pid, "")}</figcaption></figure>""" for pid, code, label, src in types)

    motion_cards = "".join(f"""<figure class="opt motion"><div class="mv"><img src="{webp_src}" alt="Animation du logo {esc(d.name)}" loading="lazy">
<video src="{mp4}" poster="{poster}" autoplay muted loop playsinline preload="metadata" aria-label="Carton de fin vertical {esc(d.name)}"></video></div>
<figcaption><b>{d.code}</b> {esc(d.name)}{pick_btn(f"anim-{d.code}", "")}</figcaption></figure>""" for d, webp_src, mp4, poster in motions)
    mock_cards = "".join(f"""<figure class="opt"><img src="{st}" alt="Autocollants {esc(d.name)}" loading="lazy">
<img class="sig" src="{sg}" alt="Signature courriel {esc(d.name)}" loading="lazy">
<figcaption><b>{d.code}</b> {esc(d.name)}{pick_btn(f"mock-{d.code}", "")}</figcaption></figure>""" for d, st, sg in mocks)

    chan_cards = "".join(f"""<figure class="opt"><img src="{yt}" alt="Couverture YouTube {esc(d.name)}" loading="lazy">
<div class="chan"><img src="{tw}" alt="Bannière Twitch {esc(d.name)}" loading="lazy"><img src="{zn}" alt="Zones de recadrage YouTube {esc(d.name)}" loading="lazy"></div>
<figcaption><b>{d.code}</b> {esc(d.name)} · YouTube 2560 × 1440, Twitch 1200 × 480, zones de recadrage{pick_btn(f"chan-{d.code}", "")}</figcaption></figure>""" for d, yt, zn, tw in chans)

    labels = {f"dir-{d.code}": f"Direction {d.code} · {d.name}" for d in ALL}
    labels.update({f"chan-{d.code}": f"Chaînes {d.code} · {d.name}" for d, *_ in chans})
    labels.update({f"anim-{d.code}": f"Animation {d.code} · {d.name}" for d, *_ in motions})
    labels.update({f"mock-{d.code}": f"En situation {d.code} · {d.name}" for d, _, _ in mocks})
    labels.update({pid: f"Signe {code} · {label}" for pid, code, label, _ in signs})
    for code, rows in palettes.items():
        labels.update({pid: f"{code} · palette {label}" for pid, label, _, _ in rows})
    for code, items in lays.items():
        labels.update({pid: f"{code} · {label}" for pid, label, _ in items})
    labels.update({pid: f"Typo {code} · {label}" for pid, code, label, _ in types})

    counts = {"n_dir": len(ALL), "n_pal": sum(len(r) for r in palettes.values()), "n_sign": len(signs),
              "n_lay": sum(len(i) for i in lays.values()), "n_type": len(types), "n_anim": len(motions),
              "n_mock": 2 * len(mocks), "n_pal_dirs": len(palettes)}

    return TEMPLATE.format(
        date=DATE, overview=overview, shortlist="".join(short), table="".join(table_rows), dirs=dirs,
        signs=sign_cards, palettes="".join(pal_blocks), layouts="".join(lay_blocks), types=type_cards,
        motions=motion_cards, mocks=mock_cards, chans=chan_cards,
        labels=json.dumps(labels, ensure_ascii=False), **counts)


TEMPLATE = """<title>Options d'identité Wubba</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&family=Martian+Mono:wdth,wght@87.5,400;87.5,500&display=swap">
<style>
/* Catalogue d'options : une galerie de travail neutre, pour que la couleur vienne des propositions et pas de la page. */
:root {{
  --bg:#EEEEEB; --panel:#F8F8F6; --fg:#141416; --muted:#5E5E5C; --faint:#8C8C88; --line:#D6D5D0;
  --pick:#141416; --pick-fg:#F8F8F6; --ghost:rgba(20,20,22,.14);
  --sans:"Geist",ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;
  --mono:"Martian Mono",ui-monospace,"SFMono-Regular",Menlo,monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg:#121214; --panel:#1B1B1E; --fg:#EDEDEA; --muted:#A3A39E; --faint:#77776F; --line:#2E2E32;
  --pick:#EDEDEA; --pick-fg:#121214; --ghost:rgba(237,237,234,.16); color-scheme:dark }} }}
:root[data-theme="dark"] {{ --bg:#121214; --panel:#1B1B1E; --fg:#EDEDEA; --muted:#A3A39E; --faint:#77776F; --line:#2E2E32;
  --pick:#EDEDEA; --pick-fg:#121214; --ghost:rgba(237,237,234,.16); color-scheme:dark }}
*{{box-sizing:border-box}}
body{{background:var(--bg);color:var(--fg);font:16px/1.55 var(--sans);margin:0;padding-inline:max(16px,3vw);padding-block:0 64px}}
img{{max-width:100%;height:auto;display:block}}
a{{color:inherit}}
.wrap{{max-width:1320px;margin:0 auto}}
.top{{padding-block:40px 20px;border-bottom:1px solid var(--line)}}
.eyebrow,.kind,figcaption,.small,.code,th,.was,.of{{font-family:var(--mono);letter-spacing:.02em}}
.eyebrow{{font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin:0 0 10px}}
h1{{font-size:clamp(34px,6vw,64px);line-height:1;margin:0 0 16px;letter-spacing:-.02em;font-weight:700;text-wrap:balance}}
h2{{font-size:clamp(24px,3.4vw,34px);line-height:1.1;margin:0 0 8px;letter-spacing:-.01em;font-weight:700;text-wrap:balance}}
h3{{font-size:20px;line-height:1.2;margin:0;font-weight:600}}
h4{{font-family:var(--mono);font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin:18px 0 8px;font-weight:500}}
.lede{{max-width:68ch;color:var(--muted);margin:0 0 16px}}
.counts{{display:flex;flex-wrap:wrap;gap:8px 22px;font-family:var(--mono);font-size:12px;color:var(--muted)}}
.counts b{{color:var(--fg);font-size:15px}}
nav.toc{{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:var(--bg);border-bottom:1px solid var(--line);
  display:flex;gap:18px;overflow-x:auto;padding-block:12px;font-family:var(--mono);font-size:12px;white-space:nowrap}}
nav.toc a{{text-decoration:none;color:var(--muted)}} nav.toc a:hover,nav.toc a:focus-visible{{color:var(--fg)}}
nav.toc .sel{{margin-left:auto;color:var(--fg)}}
section{{padding-block:44px 8px;border-bottom:1px solid var(--line)}}
.intro{{max-width:72ch;color:var(--muted);margin:0 0 22px}}
.shortlist{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}}
.short{{display:block;text-decoration:none;background:var(--panel);border:1px solid var(--line);padding:14px}}
.short img{{width:100%}}
.short-meta{{display:flex;align-items:baseline;gap:10px;margin:12px 0 6px}}
.short-meta .s{{margin-left:auto;font-family:var(--mono);font-size:13px}}
.short p{{margin:0;color:var(--muted);font-size:15px}}
.reco{{margin-top:22px;max-width:76ch}}
.reco p{{margin:0 0 10px}}
.tablewrap{{overflow-x:auto;margin-top:22px}}
table{{border-collapse:collapse;width:100%;min-width:640px;font-size:14px}}
th{{text-align:left;font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);font-weight:500;padding:8px 10px;border-bottom:1px solid var(--line)}}
td{{padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:middle}}
td.num{{font-variant-numeric:tabular-nums;text-align:right;font-family:var(--mono);font-size:13px}}
.chip{{display:inline-block;width:16px;height:16px;background:var(--c);border:1px solid var(--ghost);margin-right:3px;vertical-align:middle}}
.overview{{margin-top:22px;border:1px solid var(--line)}}
.dir{{padding-block:34px;border-top:1px solid var(--line)}}
.dir:first-of-type{{border-top:0}}
.dir-head{{display:flex;flex-wrap:wrap;align-items:center;gap:14px 24px}}
.dir-id{{display:flex;align-items:center;gap:14px;min-width:0}}
.dir-id .code{{font-size:40px;line-height:1;font-weight:500}}
.kind{{font-size:11px;color:var(--muted);margin:4px 0 0;text-transform:uppercase;letter-spacing:.06em}}
.dir-score{{display:flex;align-items:baseline;gap:6px;margin-left:auto}}
.dir-score .big{{font-size:34px;font-weight:700;font-variant-numeric:tabular-nums}}
.dir-score .of{{font-size:13px;color:var(--muted)}} .dir-score .was{{font-size:11px;color:var(--faint);margin-left:8px}}
.idea{{font-size:19px;line-height:1.45;max-width:66ch;margin:14px 0 18px}}
.dir-logos{{display:grid;grid-template-columns:1fr 1fr 150px;gap:12px}}
.dir-logos figure,.dir-banners figure,.opt{{margin:0}}
.dir-logos .sq img{{width:150px}}
.dir-banners{{display:grid;grid-template-columns:1.25fr 1fr;gap:12px;margin-top:12px}}
figcaption{{font-size:11px;color:var(--muted);margin-top:6px}}
.dir-facts{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:28px;margin-top:8px}}
.dir-facts ul{{margin:0;padding-left:18px}} .dir-facts li{{margin-bottom:4px}}
.dir-facts>div{{min-width:0}}
.risk{{margin:12px 0 0;color:var(--muted)}} .risk b{{color:var(--fg);margin-right:6px}}
.small{{font-size:12px;color:var(--muted)}}
.fav{{max-width:280px;image-rendering:pixelated}}
.board-link{{font-family:var(--mono);font-size:12px}}
ul.score{{list-style:none;padding:0;margin:0;display:grid;gap:5px}}
ul.score li{{display:grid;grid-template-columns:96px 1fr 18px 22px;align-items:center;gap:8px;font-size:13px}}
ul.score strong{{font-family:var(--mono);font-size:12px;text-align:right}}
ul.score em{{font-style:normal;font-family:var(--mono);font-size:11px;color:var(--muted)}}
.bar{{position:relative;height:8px;background:var(--ghost)}}
.bar b{{position:absolute;inset:0 auto 0 0;background:var(--fg)}}
.bar s{{position:absolute;inset:0 auto 0 0;border-right:2px solid var(--bg);text-decoration:none}}
.vh{{margin:28px 0 12px;font-size:17px}} .vh a{{text-decoration:none}}
.opts{{display:grid;gap:14px}}
.opts.two{{grid-template-columns:repeat(2,minmax(0,1fr))}}
.opts.three{{grid-template-columns:repeat(3,minmax(0,1fr))}}
.opts.one{{grid-template-columns:minmax(0,1fr)}}
.opt{{background:var(--panel);border:1px solid var(--line);padding:10px}}
.opt figcaption{{display:flex;align-items:center;gap:10px;flex-wrap:wrap;font-size:12px;color:var(--fg)}}
.opt figcaption .pick{{margin-left:auto}}
.mv{{display:grid;grid-template-columns:minmax(0,3fr) minmax(0,1fr);gap:10px;align-items:center}}
.mv video{{width:100%;aspect-ratio:9/16;display:block;background:#000}}
.opt img.sig{{margin-top:10px}}
.chan{{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:10px;margin-top:10px;align-items:start}}
.weak-badge{{font-family:var(--mono);font-size:11px;letter-spacing:.06em;text-transform:uppercase;border:1px solid var(--line);padding:3px 8px;color:var(--muted)}}
.weak-note{{max-width:72ch;color:var(--muted);border-top:1px solid var(--line);padding-top:10px;margin:0 0 14px}}
.pick{{font:500 12px var(--mono);display:inline-flex;align-items:center;gap:8px;cursor:pointer;background:transparent;color:var(--fg);
  border:1px solid var(--line);padding:6px 10px;border-radius:999px;white-space:nowrap}}
.pick .box{{width:12px;height:12px;border:1.5px solid currentColor;border-radius:3px;display:inline-block}}
.pick[aria-pressed="true"]{{background:var(--pick);color:var(--pick-fg);border-color:var(--pick)}}
.pick[aria-pressed="true"] .box{{background:currentColor}}
.pick:focus-visible{{outline:2px solid var(--fg);outline-offset:2px}}
.dir-head .pick{{margin-left:0}}
#ma-selection ul{{padding-left:18px;margin:8px 0 0}}
#picked-empty{{color:var(--muted)}}
textarea{{width:100%;min-height:140px;font:15px/1.5 var(--sans);padding:12px;background:var(--panel);color:var(--fg);border:1px solid var(--line)}}
.status{{font-family:var(--mono);font-size:12px;color:var(--muted);margin-top:8px}}
.method{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:24px}}
.method ul{{margin:0;padding-left:18px}} .method li{{margin-bottom:6px}}
code{{font-family:var(--mono);font-size:.86em}}
footer{{padding-block:28px;color:var(--faint);font-family:var(--mono);font-size:12px}}
@media (max-width:860px){{
  .dir-logos{{grid-template-columns:1fr 1fr}} .dir-logos .sq{{grid-column:1/-1}}
  .dir-banners,.dir-facts{{grid-template-columns:1fr}}
  .opts.two,.opts.three{{grid-template-columns:1fr}}
  .dir-score{{margin-left:0}}
  .hide-s{{display:none}}
}}
@media (prefers-reduced-motion:no-preference){{ .pick{{transition:background .15s,color .15s}} }}
</style>

<div class="wrap">
<header class="top">
  <p class="eyebrow">wubba · identité visuelle · {date}</p>
  <h1>Options d'identité Wubba</h1>
  <p class="lede">Dix-sept directions complètes, chacune avec son logo, son icône, sa palette, sa typo et ses bannières, notées sur 50 et retravaillées au moins une fois. Puis les variantes des meilleures. Coche « Je garde » sur ce qui te parle : tes choix restent enregistrés dans cette page.</p>
  <p class="counts"><span><b>{n_dir}</b> directions</span><span><b>{n_sign}</b> signes</span><span><b>{n_pal}</b> palettes</span><span><b>{n_lay}</b> bannières alternatives</span><span><b>{n_type}</b> paires typo</span><span><b>{n_anim}</b> animations</span><span><b>{n_mock}</b> mises en situation</span></p>
</header>
<nav class="toc" aria-label="Sections">
  <a href="#preselection">Présélection</a><a href="#ensemble">Vue d'ensemble</a><a href="#directions">Les {n_dir} directions</a>
  <a href="#signes">Signes A</a><a href="#palettes">Palettes</a><a href="#mises-en-page">Mises en page</a><a href="#typo">Typo</a><a href="#animations">Animations</a><a href="#chaines">Chaînes</a><a href="#situation">En situation</a>
  <a href="#methode">Méthode</a><a class="sel" href="#ma-selection">Ma sélection · <span id="pick-count">0</span></a>
</nav>

<section id="preselection">
  <h2>Présélection</h2>
  <p class="intro">Les quatre directions qui ont le mieux tenu la critique. Clique pour descendre à la direction.</p>
  <div class="shortlist">{shortlist}</div>
  <div class="reco">
    <h4>Ma recommandation</h4>
    <p><b>A, Le point de trop.</b> C'est la seule direction où l'idée du studio (quelque chose placé là où il n'a pas d'affaire à être) est dite par le logo lui-même, sans explication. Elle tient à 16 px, en une couleur, en inversé, et elle a l'air d'une agence devant un directeur marketing. Le kit complet de production est déjà prêt dans le repo (<code>logo/</code>, <code>tokens/</code>, <code>palette/</code>).</p>
    <p>Son risque : le rouge sur noir est partagé avec HyperX et ROG. Si ça te gêne, la palette <b>Rose direct</b> ou <b>Outremer</b> garde tout le reste (section Palettes).</p>
    <p>Mon deuxième choix, très proche : <b>O, Touche W</b>. Le nom tapé sur cinq touches, le W allumé en lilas, parce que W veut dire avancer dans tous les jeux de tir. C'est la plus « gaming » du lot sans néon ni flamme, et la bannière (un clavier fantôme où seule la grappe WASD est allumée) se comprend en une seconde. Moins sobre que A devant un acheteur, plus attachante pour les joueurs.</p>
    <p>Si tu veux plus d'audace : <b>E, Maison</b> (un logotype de maison de couture dans un secteur tout en néon) ou <b>F, Bulle</b> (les b qui regardent de côté). Plus risqués devant un acheteur à 8 000 $, plus mémorables dans un fil.</p>
    <p>Pour sortir complètement des codes du gaming : <b>P, Topo</b> (le mot posé comme une île sur une carte, entouré de ses courbes de niveau) ou <b>Q, Mire</b> (la mire de test des télés : « test », dit sans un mot).</p>
  </div>
</section>

<section id="ensemble">
  <h2>Vue d'ensemble</h2>
  <p class="intro">Toutes les directions côte à côte : logo clair, logo sombre, icône, favicon rendu à 16, 24, 32 et 48 px réels, bannière X. Le tableau est trié par note.</p>
  <img class="overview" src="{overview}" alt="Les {n_dir} directions côte à côte" loading="lazy">
  <div class="tablewrap"><table>
    <thead><tr><th>Code</th><th>Direction</th><th class="hide-s">Type de marque</th><th>v1</th><th>v2</th><th>Palette</th><th>Garder</th></tr></thead>
    <tbody>{table}</tbody></table></div>
</section>

<section id="directions">
  <h2>Les {n_dir} directions</h2>
  <p class="intro">Chaque direction avec son idée, ses raisons, son risque honnête, sa note sur la grille du skill logo-design (10 dimensions, la barre claire est la v1) et ce que l'itération a changé.</p>
  {dirs}
</section>

<section id="signes">
  <h2>Signes de la direction A</h2>
  <p class="intro">Même idée, dessins différents : la forme du point, la graisse, la rondeur des panses. Chaque variante a son icône.</p>
  <div class="opts two">{signs}</div>
</section>

<section id="palettes">
  <h2>Palettes</h2>
  <p class="intro">Le même dessin dans d'autres couleurs, pour {n_pal_dirs} directions. La forme se choisit à part : on peut prendre le signe de A avec la palette Outremer.</p>
  {palettes}
</section>

<section id="mises-en-page">
  <h2>Mises en page des bannières</h2>
  <p class="intro">Quatre mises en page pour X et quatre pour l'aperçu de lien (quand quelqu'un colle wubba.studio dans un message).</p>
  {layouts}
</section>

<section id="typo">
  <h2>Paires typographiques</h2>
  <p class="intro">Cinq combinaisons titres, texte et étiquettes pour la direction A, toutes sur Google Fonts sous licence libre. Le logo reste dessiné à la main : la typo sert aux titres, aux documents et au site.</p>
  <div class="opts one">{types}</div>
</section>

<section id="animations">
  <h2>Animations</h2>
  <p class="intro">Le logo en mouvement, pour la fin des vidéos : à gauche le sting 16:9 (3 secondes), à droite le carton vertical pour Shorts, TikTok et Reels. Chaque animation existe aussi en WebM à fond transparent pour OBS, dans <code>options/&lt;direction&gt;/motion/</code>.</p>
  <div class="opts two">{motions}</div>
</section>

<section id="chaines">
  <h2>Chaînes YouTube et Twitch</h2>
  <p class="intro">La couverture YouTube fait 2560 × 1440, mais un téléphone n'en montre que le centre (1546 × 423) et un ordinateur une bande de 2560 × 423 : le nom, la ligne et les coordonnées tiennent dans le centre, le motif remplit le reste. La petite vue avec les cadres montre ces recadrages (cyan : téléphone, rose : ordinateur). À côté, la bannière Twitch.</p>
  <div class="opts two">{chans}</div>
</section>

<section id="situation">
  <h2>En situation</h2>
  <p class="intro">Chaque direction sur une planche d'autocollants (sur un couvercle de portable) et dans une signature courriel. Utile pour voir comment le logo tient une fois découpé, en petit et sur du blanc.</p>
  <div class="opts two">{mocks}</div>
</section>

<section id="ma-selection">
  <h2>Ma sélection</h2>
  <p class="intro">Ce que tu as coché, et un espace pour tes commentaires. Dis-moi ensuite « lis ma sélection » : je la retrouve dans la page et je sors le kit complet de ce que tu as choisi.</p>
  <p id="picked-empty">Rien de coché pour l'instant.</p>
  <ul id="picked"></ul>
  <h4><label for="notes">Tes notes pour Claude</label></h4>
  <textarea id="notes" placeholder="Ex. : A mais en Outremer, bannière Symbole géant, typo T2."></textarea>
  <p class="status" id="save-status" role="status"></p>
</section>

<section id="methode">
  <h2>Méthode</h2>
  <div class="method">
    <div><h4>Les skills utilisés</h4><ul>
      <li><b>logo-design</b> : concepts, construction SVG, grille de critique /50, tests 16 px, audit des fichiers (98 à 100/100).</li>
      <li><b>visual-identity-designer</b> : structure couleur et typo ; la phase d'interrogatoire est remplacée par ton vault.</li>
      <li><b>brand-kit</b> : couche d'alias sémantiques dans <code>tokens.css</code>, jetons de mouvement, base 8 px.</li>
      <li><b>design-logo</b> (logoloom) : planche claire et sombre systématique, liste des tailles d'icônes.</li>
      <li><b>brand-design-skill</b> : standard des planches VI (grilles, fonds, icônes) ; ses étapes d'approbation sautées à ta demande.</li>
      <li><b>ai-graphic-design</b> : formats de livraison (SVG, PDF vectoriel, PNG), nettoyage des tracés au minimum d'ancres.</li>
    </ul></div>
    <div><h4>Les deux MCP</h4><ul>
      <li><b>branding-mcp</b> : validation WCAG de la palette (90/100) et exports Tailwind, Figma, Sass, Style Dictionary, React.</li>
      <li><b>logoloom</b> : optimiseur SVGO testé et écarté (2 % de gain, il supprimait le titre accessible) ; son kit automatique écarté (son icône écrasait le mot entier dans un carré).</li>
    </ul>
    <h4>Comment c'est fabriqué</h4><ul>
      <li>Lettres construites en géométrie (unions booléennes), ou vectorisées depuis des polices libres avec HarfBuzz.</li>
      <li>Aucun texte vivant, aucun filtre, aucune image dans les SVG.</li>
      <li>Tout se régénère avec <code>python3 src/build_options.py</code>.</li>
    </ul></div>
    <div><h4>Ce qui est prêt maintenant</h4><ul>
      <li>Kit complet de A : 22 SVG, PNG à toutes les tailles, favicons, avatars, PDF, filigrane pour les previews client.</li>
      <li>Tokens : CSS, JSON W3C, Tailwind, Figma, Sass, React, palettes .ase et .gpl.</li>
      <li>Pour une autre direction : dis-moi la lettre et je sors le même kit.</li>
    </ul>
    <h4>À faire de ton côté</h4><ul>
      <li>Recherche de marque déposée avant le lancement (je ne peux pas la garantir).</li>
      <li>Épreuve papier si tu imprimes : les rouges vifs bougent en CMJN.</li>
    </ul></div>
  </div>
</section>
<footer>wubba · identité visuelle · options · {date}</footer>
</div>

<script>
const LABELS = {labels};
const picks = new Set();
let db = null, notesTimer = null, lastNotes = "";
const $ = (s, r = document) => r.querySelector(s);
const status = (t) => {{ $("#save-status").textContent = t; }};

function paint() {{
  document.querySelectorAll("[data-pick]").forEach((b) => b.setAttribute("aria-pressed", picks.has(b.dataset.pick) ? "true" : "false"));
  $("#pick-count").textContent = picks.size;
  const list = $("#picked");
  list.textContent = "";
  [...picks].sort().forEach((id) => {{ const li = document.createElement("li"); li.textContent = LABELS[id] || id; list.appendChild(li); }});
  $("#picked-empty").hidden = picks.size > 0;
}}

function localLoad() {{
  try {{ JSON.parse(localStorage.getItem("wubba-picks") || "[]").forEach((p) => picks.add(p)); $("#notes").value = localStorage.getItem("wubba-notes") || ""; }} catch (e) {{}}
}}
function localSave() {{
  try {{ localStorage.setItem("wubba-picks", JSON.stringify([...picks])); localStorage.setItem("wubba-notes", $("#notes").value); }} catch (e) {{}}
}}

async function toggle(id) {{
  const on = !picks.has(id);
  on ? picks.add(id) : picks.delete(id);
  paint(); localSave();
  if (!db) return;
  try {{
    const ref = db.collection("picks").doc(id);
    if (on) await ref.set({{ kept: true, label: LABELS[id] || id, at: new Date().toISOString() }});
    else await ref.delete();
    status("Sélection enregistrée.");
  }} catch (e) {{ status("Pas pu enregistrer dans la page : ton choix reste dans ce navigateur."); }}
}}

document.addEventListener("click", (e) => {{
  const b = e.target.closest("[data-pick]");
  if (b) toggle(b.dataset.pick);
}});

$("#notes").addEventListener("input", () => {{
  localSave();
  clearTimeout(notesTimer);
  notesTimer = setTimeout(async () => {{
    const text = $("#notes").value;
    if (!db || text === lastNotes) return;
    try {{ await db.doc("notes/main").set({{ text, at: new Date().toISOString() }}); lastNotes = text; status("Notes enregistrées."); }}
    catch (e) {{ status("Pas pu enregistrer les notes dans la page : elles restent dans ce navigateur."); }}
  }}, 900);
}});

localLoad(); paint();

(async () => {{
  try {{ db = window.claude && (await window.claude.use("db")); }} catch (e) {{ db = null; }}
  if (!db) {{ status("Tes choix restent dans ce navigateur."); return; }}
  db.collection("picks").onSnapshot((snap) => {{
    picks.clear();
    snap.docs.forEach((d) => {{ if (d.exists) picks.add(d.id); }});
    paint(); localSave();
  }}, () => status("Lecture de la sélection impossible : ce navigateur garde la sienne."));
  db.doc("notes/main").onSnapshot((d) => {{
    if (d.exists && document.activeElement !== $("#notes")) {{ lastNotes = d.data().text || ""; $("#notes").value = lastNotes; }}
  }}, () => {{}});
}})();
</script>
"""


if __name__ == "__main__":
    build()
