"""Planche VI d'une direction : logo, fonds, icônes, favicon réel, palette, typo, bannières, maquette.

Rendu HTML -> PNG (Chromium), avec les vraies polices de la direction pour les spécimens.
"""
from __future__ import annotations

import palette as wbpal
from compose import TAGLINE, DOMAIN, HANDLE, font_faces, css_var, render_html


def contrast_label(fg, bg):
    r = wbpal.contrast(fg, bg)
    grade = "AAA" if r >= 7 else "AA" if r >= 4.5 else "AA grand" if r >= 3 else "décor"
    return f"{r:.1f}:1 {grade}"


def board(d, out, version="v1"):
    P = d.palette
    f = lambda name: f"file://{out / name}"  # noqa: E731
    chips = []
    for name, hexv, note in P.chips():
        on = "#FFFFFF" if wbpal.luminance(hexv) < 0.35 else "#0E0F12"
        chips.append(f'<div class="chip" style="background:{hexv};color:{on}"><b>{name}</b><span>{hexv}</span>'
                     f'<i>{note}</i></div>')
    pairs = [(P.paper, P.ink, "papier / encre"), (P.accent, P.ink, "accent / encre"),
             (P.accent, P.paper, "accent / papier")]
    contrasts = "".join(f"<li><span>{lab}</span><b>{contrast_label(a, b)}</b></li>" for a, b, lab in pairs)
    why = "".join(f"<li>{w}</li>" for w in d.why)
    html = f"""<!doctype html><meta charset="utf-8"><style>{font_faces(d.display, d.body, d.mono)}
@font-face{{font-family:"LabelMono";src:url("file://{out.parent.parent / '.fonts' / 'MartianMono[wdth,wght].ttf'}");font-weight:100 900}}
*{{box-sizing:border-box}}
body{{margin:0;background:#EDEDEA;color:#141416;font:15px/1.45 '{d.body.family}',sans-serif;width:1800px}}
.wrap{{padding:48px 56px 56px}}
header{{display:grid;grid-template-columns:auto 1fr auto;gap:28px;align-items:end;border-bottom:1px solid #C9C8C3;padding-bottom:22px}}
.code{{font:600 64px/1 'LabelMono';letter-spacing:-.02em}}
h1{{margin:0;font-size:44px;line-height:1.02;{css_var(d.display)}}}
.type{{font:500 12px 'LabelMono';letter-spacing:.08em;text-transform:uppercase;color:#6A6A66;margin-top:8px}}
.idea{{max-width:560px;font-size:17px;line-height:1.4;text-align:right;color:#2A2A2C}}
.lab{{font:500 11px 'LabelMono';letter-spacing:.08em;text-transform:uppercase;color:#77766F;margin:0 0 10px}}
.grid{{display:grid;gap:18px;margin-top:22px}}
.g1{{grid-template-columns:1.35fr 1fr}}
.g2{{grid-template-columns:repeat(5,1fr)}}
.g3{{grid-template-columns:1fr 1.25fr}}
.g4{{grid-template-columns:1.5fr 1.14fr}}
.g5{{grid-template-columns:1.9fr 1fr}}
.panel{{background:#F7F7F5;border:1px solid #D9D8D3;padding:18px}}
.panel img{{display:block;width:100%;height:auto}}
.fit{{height:250px;display:flex;align-items:center;justify-content:center}}
.fit img{{max-height:100%;width:auto;max-width:100%}}
.icons{{display:flex;gap:16px;align-items:center;justify-content:center;height:160px}}
.icons img{{width:120px;height:120px}}
.icons .round{{border-radius:50%}}
.chip{{height:118px;padding:14px;display:flex;flex-direction:column;gap:2px;border:1px solid rgba(0,0,0,.08)}}
.chip b{{font-size:15px}} .chip span{{font:500 13px 'LabelMono'}} .chip i{{font-style:normal;font-size:12px;opacity:.8;margin-top:auto}}
.chips{{display:grid;grid-template-columns:repeat({len(P.chips())},1fr);gap:10px}}
ul.c{{list-style:none;padding:0;margin:14px 0 0;display:grid;gap:4px;font-size:13px}}
ul.c li{{display:flex;justify-content:space-between;border-top:1px solid #E1E0DB;padding-top:4px}}
.spec .d{{font-size:54px;line-height:1;{css_var(d.display)};margin:6px 0 12px}}
.spec .b{{font-size:18px;line-height:1.45;max-width:640px;{css_var(d.body)}}}
.spec .m{{font-size:13px;letter-spacing:.06em;text-transform:uppercase;{css_var(d.mono)};margin-top:12px}}
.fonts{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:16px;font-size:12px;color:#55544F}}
.fonts b{{display:block;color:#141416;font-size:14px}}
ul.w{{margin:8px 0 0;padding-left:18px}} .risk{{margin-top:10px;color:#8A2A1F}}
.fav{{display:flex;align-items:flex-end;height:160px}} .fav img{{width:auto;height:auto;max-width:100%;image-rendering:pixelated}}
footer{{margin-top:22px;display:flex;justify-content:space-between;font:500 11px 'LabelMono';letter-spacing:.08em;text-transform:uppercase;color:#8A8984}}
</style><div class="wrap">
<header><div class="code">{d.code}</div><div><h1>{d.name}</h1><div class="type">{d.mark_type}</div></div>
<div class="idea">{d.idea}</div></header>
<div class="grid g1">
 <div class="panel"><p class="lab">Logo principal · fond clair</p><div class="fit"><img src="{f('logo-light.png')}"></div></div>
 <div class="panel"><p class="lab">Fond sombre</p><div class="fit"><img src="{f('logo-dark.png')}"></div></div>
</div>
<div class="grid g2">
 <div class="panel"><p class="lab">Symbole</p><div class="icons"><img src="{f('symbol-light.png')}"></div></div>
 <div class="panel"><p class="lab">Icône</p><div class="icons"><img src="{f('icon.png')}"></div></div>
 <div class="panel"><p class="lab">Icône inversée</p><div class="icons"><img src="{f('icon-alt.png')}"></div></div>
 <div class="panel"><p class="lab">Avatar (recadrage rond)</p><div class="icons"><img class="round" src="{f('avatar.png')}"></div></div>
 <div class="panel"><p class="lab">Favicon 16 · 24 · 32 · 48 px réels</p><div class="fav"><img src="{f('favicon-test.png')}"></div></div>
</div>
<div class="grid g3">
 <div class="panel"><p class="lab">Palette</p><div class="chips">{''.join(chips)}</div><ul class="c">{contrasts}</ul></div>
 <div class="panel spec"><p class="lab">Typographie</p>
  <div class="d">wubba</div>
  <div class="b">{TAGLINE}.</div>
  <div class="m">{DOMAIN} · {HANDLE}</div>
  <div class="fonts"><div><b>{d.display.family}</b>titres</div><div><b>{d.body.family}</b>texte</div><div><b>{d.mono.family}</b>étiquettes, données</div></div>
 </div>
</div>
<div class="grid g4">
 <div class="panel"><p class="lab">X · 1500 × 500</p><img src="{f('x-header.png')}"></div>
 <div class="panel"><p class="lab">Aperçu de lien · 1200 × 630</p><img src="{f('og.png')}"></div>
</div>
<div class="grid g5">
 <div class="panel"><p class="lab">LinkedIn · 1584 × 396</p><img src="{f('linkedin.png')}">
  <p class="lab" style="margin-top:16px">LinkedIn page · 1128 × 191</p><img src="{f('linkedin-company.png')}"></div>
 <div class="panel"><p class="lab">En situation</p><img src="{f('profile-mock.png')}"></div>
</div>
<div class="grid g1">
 <div class="panel"><p class="lab">Pourquoi</p><ul class="w">{why}</ul><div class="risk"><b>Risque :</b> {d.risk}</div></div>
 <div class="panel"><p class="lab">Sur l'accent</p><div class="fit" style="height:150px"><img src="{f('logo-accent.png')}"></div></div>
</div>
<footer><span>wubba · identité visuelle · options</span><span>{d.code} · {version}</span></footer>
</div>"""
    hp = out / "_board.html"
    hp.write_text(html)
    render_html(hp, out / "board.png", 1800, "auto", 1)
    hp.unlink()
    return out / "board.png"
