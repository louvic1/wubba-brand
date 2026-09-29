"""Compositeur commun : pour une direction donnée, produit logos, icônes, bannières, maquettes et planche.

Tout est vectoriel (tracés) puis rastérisé. Les coordonnées de composition sont en pixels, y vers le haut
(y=0 en bas de l'image), comme le reste du projet.
"""
from __future__ import annotations

import io
import subprocess
from pathlib import Path

import cairosvg
from PIL import Image

import geom as g
import svgout
import textpath as tp

ROOT = Path(__file__).resolve().parent.parent
OPT = ROOT / "options"
TAGLINE = "AI streamers who test gaming gear where it has no business working"
DOMAIN = "wubba.studio"
HANDLE = "@wubbastudio"


# ------------------------------------------------------------------ utilitaires couleur / svg

def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    """Mélange a -> b (t=0 : a, t=1 : b)."""
    ra, rb = hex_rgb(a), hex_rgb(b)
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(ra, rb))


def page(W, H, layers, bg=None):
    parts = [f'<rect width="{W}" height="{H}" fill="{bg}"/>'] if bg else []
    for p, c in layers:
        if p is None or c is None:
            continue
        parts.append(f'<path fill="{c}" d="{g.to_d(p, H)}"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            + "".join(parts) + "</svg>\n")


def save(svg, path, png_width=None, png=True, svg_file=True):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if svg_file:
        path.with_suffix(".svg").write_text(svg)
    if png:
        cairosvg.svg2png(bytestring=svg.encode(), write_to=str(path.with_suffix(".png")), output_width=png_width)
    return path


def text_line(s, font, size, x, y, color, align="left", upper=False, tracking=0.0, max_w=None):
    """Une ligne de texte vectorisée. Réduit la taille si max_w est dépassé."""
    s = s.upper() if upper else s
    if max_w:
        _, w = tp.text(s, font.file, size, font.var, tracking)
        if w > max_w:
            size *= max_w / w
    p, w = tp.text(s, font.file, size, font.var, tracking)
    dx = {"left": x, "center": x - w / 2, "right": x - w}[align]
    return (g.translate(p, dx=dx, dy=y), color), w, size


# ------------------------------------------------------------------ logos et icônes

def tile_layers(d, scheme, T=256, ratio=None, shape="tile", small=False, lift=None):
    ratio = d.icon_ratio if ratio is None else ratio
    lift = d.icon_lift if lift is None else lift
    sym = d.icon_symbol(small)
    xmin, ymin, xmax, ymax = d.bounds(sym)
    gw, gh = xmax - xmin, ymax - ymin
    s = min(T * ratio / gw, T * ratio * d.icon_hfactor / gh)
    dx = (T - gw * s) / 2 - xmin * s
    dy = (T - gh * s) / 2 - ymin * s + T * lift
    placed = [(g.translate(p, dx=dx, dy=dy, sx=s, sy=s), r) for p, r in sym]
    if shape == "tile":
        cont = g.rounded_rect(0, 0, T, T, T * 0.22, smooth=0.6)
    elif shape == "circle":
        cont = g.circle(T / 2, T / 2, T / 2)
    else:
        cont = g.rect(0, 0, T, T)
    return [(cont, scheme["bg"])] + d.color(placed, scheme)


def logo_set(d, out):
    P = d.palette
    wm = d.wordmark()
    box = d.bounds(wm)
    pad = (box[3] - box[1]) * 0.35
    res = {}
    for kind in ("light", "dark", "accent", "mono-black"):
        sch = P.scheme(kind)
        svg = svgout.svg_doc(d.color(wm, sch), box, "wubba", pad=pad, bg=sch["bg"])
        res[f"logo-{kind}"] = save(svg, out / f"logo-{kind}", png_width=1600)
    # masters transparents
    for kind in ("light", "dark"):
        sch = P.scheme(kind)
        (out / f"logo-{kind}-transparent.svg").write_text(svgout.svg_doc(d.color(wm, sch), box, "wubba"))
    sym = d.symbol()
    sbox = d.bounds(sym)
    side = max(sbox[2] - sbox[0], sbox[3] - sbox[1])
    sq = ((sbox[0] + sbox[2]) / 2 - side / 2, (sbox[1] + sbox[3]) / 2 - side / 2,
          (sbox[0] + sbox[2]) / 2 + side / 2, (sbox[1] + sbox[3]) / 2 + side / 2)
    for kind in ("light", "dark"):
        sch = P.scheme(kind)
        svg = svgout.svg_doc(d.color(sym, sch), sq, "wubba", pad=side * 0.18, bg=sch["bg"])
        res[f"symbol-{kind}"] = save(svg, out / f"symbol-{kind}", png_width=800)
    ic = P.scheme(d.icon_scheme)
    alt = P.scheme("light" if d.icon_scheme == "dark" else "dark")
    res["icon"] = save(page(256, 256, tile_layers(d, ic)), out / "icon", png_width=512)
    res["icon-alt"] = save(page(256, 256, tile_layers(d, alt)), out / "icon-alt", png_width=512)
    res["icon-accent"] = save(page(256, 256, tile_layers(d, P.scheme("accent"))), out / "icon-accent", png_width=512)
    res["icon-circle"] = save(page(256, 256, tile_layers(d, ic, shape="circle", ratio=d.icon_ratio * 0.9)),
                              out / "icon-circle", png_width=512)
    res["avatar"] = save(page(256, 256, tile_layers(d, ic, shape="square", ratio=d.icon_ratio * 0.875)),
                         out / "avatar", png_width=400)
    favicon_test(d, out)
    return res


def favicon_test(d, out):
    """Test honnête : la tuile rendue à 16/24/32/48 px réels, agrandie au plus proche voisin."""
    ic = d.palette.scheme(d.icon_scheme)
    svg = page(256, 256, tile_layers(d, ic, small=True, ratio=d.favicon_ratio))
    row = Image.new("RGBA", (16 * 6 + 24 * 6 + 32 * 6 + 48 * 6 + 5 * 24, 48 * 6), (0, 0, 0, 0))
    x = 0
    for sz in (16, 24, 32, 48):
        data = cairosvg.svg2png(bytestring=svg.encode(), output_width=sz, output_height=sz)
        im = Image.open(io.BytesIO(data)).convert("RGBA").resize((sz * 6, sz * 6), Image.NEAREST)
        row.paste(im, (x, 48 * 6 - sz * 6), im)
        x += sz * 6 + 24
    row.save(out / "favicon-test.png")


# ------------------------------------------------------------------ bannières

FORMATS = {
    "x-header": (1500, 500),
    "og": (1200, 630),
    "linkedin": (1584, 396),
    "linkedin-company": (1128, 191),
}


def banner(d, fmt, scheme_kind=None, layout=None):
    """Mise en page générique ; chaque direction peut la remplacer via d.banner_layout(fmt, ...)."""
    W, H = FORMATS[fmt]
    sch = d.palette.scheme(scheme_kind or d.banner_scheme)
    if hasattr(d, "banner_layout"):
        custom = d.banner_layout(fmt, W, H, sch, layout)
        if custom is not None:
            return custom
    muted = mix(sch["fg"], sch["bg"], 0.45)
    layers = list(d.device(W, H, sch, fmt))
    wm = d.wordmark()
    tag_font, upper, track = (d.mono, True, 0.06) if d.tagline_mono else (d.body, False, 0.0)
    if fmt == "x-header":
        wmp, _ = d.place(wm, (W / 2 - 330, 230, W / 2 + 330, 400))
        layers += d.color(wmp, sch)
        wb = d.bounds(wmp)
        tl, _, _ = text_line(TAGLINE, tag_font, 17, W / 2, wb[1] - 62, muted, "center", upper, track, max_w=900)
        dom, _, _ = text_line(DOMAIN, d.mono, 15, W - 56, 44, muted, "right", False, 0.04)
        layers += [tl, dom]
    elif fmt == "og":
        wmp, _ = d.place(wm, (W / 2 - 300, 300, W / 2 + 300, 470))
        layers += d.color(wmp, sch)
        wb = d.bounds(wmp)
        tl, _, _ = text_line(TAGLINE, tag_font, 22 if not upper else 17, W / 2, wb[1] - 70, muted, "center", upper,
                             track, max_w=1000)
        dom, _, _ = text_line(DOMAIN, d.mono, 17, 64, 56, sch["fg"], "left", False, 0.04)
        layers += [tl, dom]
    elif fmt == "linkedin":
        wmp, _ = d.place(wm, (W - 700, 190, W - 90, 320), align="right")
        layers += d.color(wmp, sch)
        wb = d.bounds(wmp)
        tl, _, _ = text_line(TAGLINE, tag_font, 16, W - 90, wb[1] - 52, muted, "right", upper, track, max_w=820)
        layers += [tl]
    else:  # linkedin-company
        wmp, _ = d.place(wm, (W - 430, 92, W - 64, 150), align="right")
        layers += d.color(wmp, sch)
        wb = d.bounds(wmp)
        tl, _, _ = text_line(TAGLINE, tag_font, 11, W - 64, wb[1] - 34, muted, "right", upper, track, max_w=560)
        layers += [tl]
    return page(W, H, layers, bg=sch["bg"])


def banner_set(d, out, scheme_kind=None, suffix=""):
    res = {}
    for fmt, (W, H) in FORMATS.items():
        svg = banner(d, fmt, scheme_kind)
        res[fmt] = save(svg, out / f"{fmt}{suffix}", png_width=W)
    return res


# ------------------------------------------------------------------ maquette de profil et planche (HTML)

def render_html(html_path, png_path, W, H, scale=1):
    subprocess.run(["node", str(ROOT / "src" / "render.mjs"), str(html_path), str(png_path), str(W), str(H),
                    str(scale)], check=True, capture_output=True)
    return png_path


def font_faces(*fonts):
    seen, css = set(), []
    for f in fonts:
        if f is None or f.family in seen:
            continue
        seen.add(f.family)
        css.append(f'@font-face{{font-family:"{f.family}";src:url("file://{tp.FONT_DIR / f.file}");'
                   f'font-weight:100 900;font-stretch:50% 200%;}}')
    return "\n".join(css)


def css_var(font):
    parts = []
    for axis, val in font.var.items():
        if axis == "wght":
            continue
        parts.append(f'"{axis}" {val}')
    return f"font-family:'{font.family}';font-weight:{font.var.get('wght', 400)};" + (
        f"font-variation-settings:{','.join(parts)};" if parts else "")


def profile_mock(d, out):
    """Maquette générique d'un profil social : bannière, avatar rond qui chevauche, nom, identifiant, bio."""
    P = d.palette
    html = f"""<!doctype html><meta charset="utf-8"><style>{font_faces(d.display, d.body, d.mono)}
body{{margin:0;background:#E9E9E6;font-family:'{d.body.family}',sans-serif}}
.card{{width:600px;background:#fff;margin:0;overflow:hidden}}
.hdr{{width:600px;height:200px;background:url('file://{out / "x-header.png"}') center/cover}}
.av{{width:134px;height:134px;border-radius:50%;border:4px solid #fff;margin:-71px 0 0 16px;
background:url('file://{out / "avatar.png"}') center/cover;position:relative}}
.name{{padding:10px 16px 0;font-size:20px;font-weight:700;color:#0F1419}}
.handle{{padding:0 16px;font-size:15px;color:#536471}}
.bio{{padding:10px 16px 18px;font-size:15px;color:#0F1419;line-height:1.35}}
.bio a{{color:#536471;text-decoration:none}}
</style><div class="card"><div class="hdr"></div><div class="av"></div>
<div class="name">wubba</div><div class="handle">{HANDLE}</div>
<div class="bio">{TAGLINE}<br><a>{DOMAIN}</a></div></div>"""
    hp = out / "_profile.html"
    hp.write_text(html)
    render_html(hp, out / "profile-mock.png", 600, 372, 2)
    hp.unlink()
