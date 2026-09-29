"""Animations de logo : un « sting » de 3 secondes par direction, à poser en fin de vidéo.

    python3 src/motion.py A O D H M N

Sorties dans options/<code>-<key>/motion/ :
  sting.mp4          1920 × 1080, fond de marque, logo puis ligne (fin de vidéo YouTube, 3 s)
  sting-alpha.webm   1920 × 1080, fond transparent, logo seul (incrustation OBS ou montage, 2,4 s)
  endcard-9x16.mp4   1080 × 1920, logo, ligne et identifiant (Shorts, TikTok, Reels, 4 s)
  sting.webp         960 × 540, aperçu animé pour le catalogue

Chaque image est un SVG en tracés rendu par cairosvg, puis assemblé par le ffmpeg d'imageio-ffmpeg.
"""
from __future__ import annotations

import math
import subprocess
import sys
import tempfile
from multiprocessing import Pool
from pathlib import Path

import cairosvg
import imageio_ffmpeg
import pathops
from fontTools.misc.transform import Transform
from fontTools.pens.transformPen import TransformPen

import compose
import devices as dv
import geom as g
import textpath as tp
from compose import HANDLE, TAGLINE, mix
from directions import BY_CODE

FPS = 30
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


# ------------------------------------------------------------------ courbes

def clamp(x):
    return max(0.0, min(1.0, x))


def seg(t, a, b):
    """Avancement de 0 à 1 entre les instants a et b."""
    return clamp((t - a) / (b - a))


def ease_out(x):
    return 1 - (1 - x) ** 3


def ease_in(x):
    return x ** 3


def ease_in_out(x):
    return x * x * (3 - 2 * x)


def bump(x):
    """0 -> 1 -> 0 sur une demi-sinusoïde (appui de touche, rebond)."""
    return math.sin(math.pi * x) if 0 < x < 1 else 0.0


def xform(path, t):
    q = pathops.Path()
    path.draw(TransformPen(q.getPen(), t))
    return q


def svg(W, H, layers, bg=None):
    parts = [f'<rect width="{W}" height="{H}" fill="{bg}"/>'] if bg else []
    for p, c, a in layers:
        if p is None or a <= 0.002:
            continue
        op = f' fill-opacity="{a:.3f}"' if a < 0.998 else ""
        parts.append(f'<path fill="{c}"{op} d="{g.to_d(p, H)}"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            + "".join(parts) + "</svg>")


def solid(layers, a=1.0):
    return [(p, c, a) for p, c in layers]


# ------------------------------------------------------------------ scènes (logo seul)
# Chaque scène reçoit la direction, la boîte où poser le logo, le schéma de couleurs et l'instant t.
# Elle renvoie des calques (tracé, couleur, opacité) et l'instant où le logo est au repos.

def scene_A(d, box, sch, t, W, H):
    """Le mot monte en place, le point tombe sur le w, rebondit deux fois, puis clignote comme un voyant REC."""
    placed, s, _ = d.place_t(d.wordmark(), box)
    body, dot = placed[0][0], placed[1][0]
    e = ease_out(seg(t, 0.0, 0.45))
    out = [(g.translate(body, dy=-36 * (1 - e)), sch["fg"], e)]
    if t >= 0.5:
        if t < 0.85:
            dy = 360 * (1 - ease_in(seg(t, 0.5, 0.85)))
        elif t < 1.10:
            dy = 64 * bump(seg(t, 0.85, 1.10))
        elif t < 1.25:
            dy = 16 * bump(seg(t, 1.10, 1.25))
        else:
            dy = 0
        x0, y0, x1, y1 = dot.bounds
        squash = 1.0 - 0.18 * max(0.0, 1 - abs(t - 0.87) / 0.05) - 0.08 * max(0.0, 1 - abs(t - 1.11) / 0.04)
        sx, sy = 2 - squash, squash
        cx = (x0 + x1) / 2
        p = g.translate(dot, dx=(1 - sx) * cx, dy=(1 - sy) * y0 + dy, sx=sx, sy=sy)
        on = not (1.55 <= t < 1.68 or 1.82 <= t < 1.95)
        out.append((p, sch["accent"], 1.0 if on else 0.0))
    return out, 2.0


def scene_O(d, box, sch, t, W, H):
    """Les cinq touches se tapent l'une après l'autre ; puis la touche W s'enfonce de nouveau et s'allume."""
    from directions.o_touche import U
    placed, s, _ = d.place_t(d.wordmark(), box)
    out = []
    for i in range(5):
        trio = placed[3 * i:3 * i + 3]
        t0 = 0.10 + 0.13 * i
        a = ease_out(seg(t, t0, t0 + 0.08))
        if a <= 0:
            continue
        press = bump(seg(t, t0, t0 + 0.18))
        lit = True
        if i == 0:
            press = max(press, bump(seg(t, 1.15, 1.40)))
            lit = t >= 1.27
        down = press * U * 0.075 * s
        layers = []
        for j, (p, role) in enumerate(trio):
            if i == 0 and not lit:
                role = "k" + role[1:]
            if j > 0:  # le dessus et la légende descendent, la jupe reste
                p = g.translate(p, dy=-down)
            layers.append((p, role))
        out += [(p, c, a) for p, c in d.color(layers, sch)]
    return out, 1.6


def scene_D(d, box, sch, t, W, H):
    """L'horizon se trace depuis le soleil, le mot apparaît, puis le demi-soleil se lève derrière la ligne."""
    placed, s, (tx, ty) = d.place_t(d.wordmark(), box)
    text, sun = placed[0][0], placed[1][0]
    sx0, sy0, sx1, sy1 = sun.bounds
    cx = (sx0 + sx1) / 2
    base = sy0
    half = ease_in_out(seg(t, 0.0, 0.8)) * W * 0.62
    out = []
    if half > 1:
        out.append((g.rect(max(0, cx - half), base - 2, min(W, cx + half), base + 1), mix(sch["bg"], sch["fg"], 0.30), 1.0))
    a = ease_out(seg(t, 0.35, 0.9))
    out.append((g.translate(text, dy=-20 * (1 - a)), sch["fg"], a))
    u = ease_out(seg(t, 0.85, 1.7))
    if u > 0:
        risen = g.intersect(g.translate(sun, dy=-(1 - u) * (sy1 - sy0) * 1.08), g.rect(0, base, W, H))
        x0, y0, x1, y1 = risen.bounds
        if x1 > x0:
            out.append((risen, sch["accent"], 1.0))
    return out, 1.9


def scene_H(d, box, sch, t, W, H):
    """Le nom se tape lettre par lettre derrière le curseur, qui clignote ensuite."""
    from directions.h_protocole import FONT
    placed, s, (tx, ty) = d.place_t(d.wordmark(), box)
    gl = tp.glyphs("wubba", FONT[0], 200, FONT[1])
    m = tp.metrics(FONT[0], FONT[1])
    xh = m["x"] * 200 / m["upem"]
    adv = gl[0][3]
    n = sum(1 for i in range(5) if t >= 0.35 + 0.12 * i)
    out = [(g.translate(p, dx=tx, dy=ty, sx=s, sy=s), sch["fg"], 1.0) for _, p, _, _ in gl[:n]]
    x = gl[n][2] if n < 5 else gl[-1][2] + adv * 1.12
    cursor = g.translate(g.rect(x, 0, x + adv * 0.78, xh * 1.02), dx=tx, dy=ty, sx=s, sy=s)
    typing = 0.35 <= t < 0.35 + 0.12 * 5
    on = typing or int((t + 0.02) / 0.33) % 2 == 0
    out.append((cursor, sch["accent"], 1.0 if on else 0.0))
    return out, 1.2


def scene_M(d, box, sch, t, W, H):
    """Le sceau tombe sur la page et s'imprime : écrasement, petite secousse, onde d'encre."""
    from directions.m_sceau import R_OUT
    stamp = d.wordmark()
    x0, y0, x1, y1 = box
    diam = min(x1 - x0, y1 - y0)
    k = diam / (2 * R_OUT)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    u = seg(t, 0.15, 0.42)
    if u <= 0:
        return [], 1.0
    scale = k * (1 + 0.9 * (1 - ease_in(u)))
    rot = -0.16 + 0.22 * (1 - ease_in(u))
    shake = 7 * math.sin((t - 0.42) * 70) * max(0.0, 1 - (t - 0.42) / 0.18) if t > 0.42 else 0.0
    a = ease_out(seg(t, 0.15, 0.30))
    T = Transform().translate(cx + shake, cy).rotate(rot).scale(scale)
    out = [(xform(p, T), sch.get(role, sch["fg"]), a) for p, role in stamp]
    w = seg(t, 0.42, 0.95)
    if 0 < w < 1:
        r = R_OUT * k * (1.0 + 0.35 * ease_out(w))
        out.insert(0, (dv.ring(cx, cy, r, 5 + 10 * (1 - w)), sch["accent"], 0.35 * (1 - w)))
    return out, 1.0


def scene_N(d, box, sch, t, W, H):
    """La signature se trace de gauche à droite comme sous un marqueur, puis le trait rouge la souligne d'un geste."""
    placed, s, _ = d.place_t(d.wordmark(), box)
    sig, fl = placed[0][0], placed[1][0]
    x0, y0, x1, y1 = sig.bounds
    out = []
    u = ease_in_out(seg(t, 0.15, 1.25))
    if u > 0:
        out.append((g.intersect(sig, g.rect(x0 - 10, y0 - 80, x0 - 10 + (x1 - x0 + 20) * u, y1 + 80)), sch["fg"], 1.0))
    fx0, fy0, fx1, fy1 = fl.bounds
    v = ease_out(seg(t, 1.25, 1.55))
    if v > 0:
        out.append((g.intersect(fl, g.rect(fx0 - 10, fy0 - 40, fx0 - 10 + (fx1 - fx0 + 20) * v, fy1 + 40)), sch["accent"], 1.0))
    return out, 1.7


SCENES = {"A": scene_A, "O": scene_O, "D": scene_D, "H": scene_H, "M": scene_M, "N": scene_N}


# ------------------------------------------------------------------ légendes

def tagline_layers(d, sch, W, y, size, a, lines=None, align_x=None):
    muted = sch[d.tagline_role] if d.tagline_role else mix(sch["fg"], sch["bg"], 0.32)
    font, upper, track = (d.mono, True, 0.06) if d.tagline_mono else (d.body, False, 0.0)
    out = []
    for k, line in enumerate(lines or [TAGLINE]):
        (p, c), _, _ = compose.text_line(line, font, size, align_x or W / 2, y - k * size * 1.6, muted, "center", upper, track,
                                         max_w=W * 0.86)
        out.append((g.translate(p, dy=-14 * (1 - a)), c, a))
    return out


# ------------------------------------------------------------------ rendu

def _render(job):
    svg_text, path = job
    cairosvg.svg2png(bytestring=svg_text.encode(), write_to=str(path))


def render_frames(frames, folder):
    folder.mkdir(parents=True, exist_ok=True)
    jobs = [(s, folder / f"{i:04d}.png") for i, s in enumerate(frames)]
    with Pool() as pool:
        pool.map(_render, jobs, chunksize=4)


def ffmpeg(*args):
    subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", *args], check=True)


def build(code):
    d = BY_CODE[code]
    scene = SCENES[code]
    out = compose.OPT / f"{d.code}-{d.key}" / "motion"
    out.mkdir(parents=True, exist_ok=True)
    sch = d.palette.scheme(d.banner_scheme)
    W, H = 1920, 1080
    box16 = {"M": (W / 2 - 260, H / 2 - 150, W / 2 + 260, H / 2 + 370),
             "N": (W / 2 - 560, H / 2 - 70, W / 2 + 560, H / 2 + 330)}.get(code, (W / 2 - 520, H / 2 - 40, W / 2 + 520, H / 2 + 230))
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        # 1. sting 16:9, fond de marque, 3 s
        frames = []
        for i in range(int(3.0 * FPS)):
            t = i / FPS
            layers, rest = scene(d, box16, sch, t, W, H)
            a = ease_out(seg(t, rest + 0.15, rest + 0.6))
            y_tag = (H / 2 - 150) if code != "M" else (H / 2 - 210)
            frames.append(svg(W, H, layers + (tagline_layers(d, sch, W, y_tag, 26, a) if a > 0 else []), bg=sch["bg"]))
        render_frames(frames, tmp / "a")
        ffmpeg("-framerate", str(FPS), "-i", str(tmp / "a" / "%04d.png"), "-c:v", "libx264", "-pix_fmt", "yuv420p",
               "-crf", "18", "-movflags", "+faststart", str(out / "sting.mp4"))
        ffmpeg("-i", str(out / "sting.mp4"), "-vf", "fps=20,scale=960:-1:flags=lanczos", "-c:v", "libwebp_anim",
               "-lossless", "0", "-q:v", "72", "-loop", "0", str(out / "sting.webp"))
        # 2. logo seul, fond transparent, 2,4 s
        frames = [svg(W, H, scene(d, box16, sch, i / FPS, W, H)[0]) for i in range(int(2.4 * FPS))]
        render_frames(frames, tmp / "b")
        ffmpeg("-framerate", str(FPS), "-i", str(tmp / "b" / "%04d.png"), "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p",
               "-b:v", "0", "-crf", "30", "-auto-alt-ref", "0", str(out / "sting-alpha.webm"))
        # 3. carton de fin vertical, 4 s
        W9, H9 = 1080, 1920
        box9 = (110, H9 * 0.52, W9 - 110, H9 * 0.52 + 230) if code != "M" else (W9 / 2 - 300, H9 * 0.42, W9 / 2 + 300, H9 * 0.42 + 600)
        lines = ["AI streamers who test gaming gear", "where it has no business working"]
        frames = []
        for i in range(int(4.0 * FPS)):
            t = i / FPS
            layers, rest = scene(d, box9, sch, t, W9, H9)
            a = ease_out(seg(t, rest + 0.15, rest + 0.6))
            b = ease_out(seg(t, rest + 0.5, rest + 0.95))
            y_tag = H9 * 0.52 - 90 if code != "M" else H9 * 0.42 - 90
            extra = tagline_layers(d, sch, W9, y_tag, 34, a, lines) if a > 0 else []
            if b > 0:
                (p, c), _, _ = compose.text_line(HANDLE, d.mono, 40, W9 / 2, y_tag - 230, sch["fg"], "center", False, 0.02)
                extra.append((p, c, b))
            frames.append(svg(W9, H9, layers + extra, bg=sch["bg"]))
        render_frames(frames, tmp / "c")
        ffmpeg("-framerate", str(FPS), "-i", str(tmp / "c" / "%04d.png"), "-c:v", "libx264", "-pix_fmt", "yuv420p",
               "-crf", "18", "-movflags", "+faststart", str(out / "endcard-9x16.mp4"))
    sizes = ", ".join(f"{f.name} {f.stat().st_size / 1e3:.0f} ko" for f in sorted(out.iterdir()))
    print(f"{code} {d.name:12} {sizes}")


if __name__ == "__main__":
    for c in (sys.argv[1:] or list(SCENES)):
        build(c)
