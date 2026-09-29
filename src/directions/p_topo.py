"""P — Topo. Le mot posé comme une île sur une carte, entouré de ses courbes de niveau : le matériel testé sur un terrain où il n'a rien à faire."""
import pathops

import geom as g
import textpath as tp
from directions.base import Direction, Font, Palette

FONT = ("Epilogue[wght].ttf", {"wght": 800})


def clean(path, q=0.01):
    """Recopie un tracé en arrondissant ses points et en retirant les segments nuls, qui font échouer les opérations."""
    from fontTools.pens.recordingPen import RecordingPen
    rec = RecordingPen()
    path.draw(rec)
    out = pathops.Path()
    pen = out.getPen()
    last = None
    for op, args in rec.value:
        pts = [(round(x / q) * q, round(y / q) * q) for x, y in args]
        if op == "moveTo":
            pen.moveTo(pts[0])
            last = pts[0]
        elif op in ("lineTo", "qCurveTo", "curveTo"):
            if op == "lineTo" and pts[-1] == last:
                continue
            getattr(pen, op)(*pts)
            last = pts[-1]
        elif op == "closePath":
            pen.closePath()
        elif op == "endPath":
            pen.endPath()
    try:
        out.simplify()
    except pathops.PathOpsError:
        pass
    return out


def grow(path, r):
    """Agrandit une forme de r en arrondissant les angles : plus on s'éloigne, plus la ligne s'adoucit, comme un relief."""
    if r <= 0:
        return path
    last = None
    for attempt, (src, rr) in enumerate(((path, r), (clean(path), r), (clean(path, 0.05), r + 0.37))):
        try:
            s = pathops.Path()
            src.draw(s.getPen())
            s.stroke(rr * 2, pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 4)
            s.convertConicsToQuads()
            s.simplify()
            return g.union(src, s)
        except pathops.PathOpsError as e:
            last = e
    raise last


def shrink(path, r):
    s = pathops.Path()
    path.draw(s.getPen())
    s.stroke(r * 2, pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 4)
    s.convertConicsToQuads()
    s.simplify()
    return g.diff(path, s)


def island(path, r):
    """Fermeture morphologique : bouche les fentes plus étroites que 2r (le haut du u, les creux du w, l'approche)."""
    return shrink(grow(outer(path), r), r)


def outer(path):
    """Garde les contours extérieurs : un relief n'a pas de lac dans ses lettres."""
    return g.fill_holes(path)


def terrain(W, H, shape, step, seed=7, res=3, noise=38.0, peaks=()):
    """Courbes de niveau d'un relief : l'altitude monte vers `shape` (et vers quelques sommets cachés),
    plus un bruit lisse qui grandit avec la distance. Renvoie [(indice du niveau, tracé polyligne)]."""
    import io

    import cairosvg
    import numpy as np
    from PIL import Image
    from scipy import ndimage
    from skimage import measure
    w, h = int(W / res), int(H / res)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
           f'<rect width="{W}" height="{H}" fill="#fff"/><path fill="#000" d="{g.to_d(shape, H)}"/></svg>')
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=w, output_height=h)
    mask = np.array(Image.open(io.BytesIO(png)).convert("L")) < 128
    dist = ndimage.distance_transform_edt(~mask) * res
    yy, xx = np.mgrid[0:h, 0:w]
    for px, py, lift in peaks:  # sommets cachés : d'autres collines qui se mêlent au relief du mot
        dp = np.hypot(xx * res - px, (h - yy) * res - py) + lift
        dist = np.minimum(dist, dp)
    rng = np.random.default_rng(seed)
    n = ndimage.gaussian_filter(rng.standard_normal((h, w)), sigma=70 / res, mode="wrap")
    n /= n.std()
    field = dist + noise * n * np.clip(dist / 180.0, 0, 1)
    out = []
    for k, level in enumerate(np.arange(step, field.max(), step)):
        for c in measure.find_contours(field, level):
            if len(c) < 6:
                continue
            p = pathops.Path()
            pen = p.getPen()
            pts = [(float(col) * res, H - float(row) * res) for row, col in c[::2]]
            pen.moveTo(pts[0])
            for q in pts[1:]:
                pen.lineTo(q)
            pen.endPath()
            out.append((k, p))
    return out


def stroke_lines(paths, lw):
    s = pathops.Path()
    for p in paths:
        p.draw(s.getPen())
    s.stroke(lw, pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 4)
    s.convertConicsToQuads()
    return s


def contours(path, first, step, n, lw):
    """n courbes de niveau autour d'une forme : la première à `first`, puis tous les `step`, trait `lw`."""
    rings = []
    for k in range(n):
        d = first + k * step
        rings.append(g.diff(grow(path, d + lw / 2), grow(path, d - lw / 2)))
    return g.union(*rings)


class Topo(Direction):
    code = "P"
    key = "topo"
    name = "Topo"
    idea = "Le mot posé comme une île sur une carte, entouré de ses courbes de niveau. Le terrain où le matériel n'a rien à faire devient le décor."
    mark_type = "Wordmark + courbes de niveau, symbole w en relief"
    why = [
        "Le seul univers « dehors » du lot : carte, relief, terrain, loin du bureau gaming et de ses néons.",
        "Les courbes naissent du mot lui-même : elles s'adoucissent en s'éloignant, comme un vrai relief, et chaque bannière a le sien.",
        "Le système se prolonge tout seul : une carte par vidéo, avec le terrain du test.",
    ]
    risk = "En petit, les courbes se referment sur les lettres : sous 120 px de large, le mot se pose seul, sans relief (version fournie)."
    palette = Palette("#17231D", "#EEEADF", "#E0662F", accent2="#8FA895",
                      names={"ink": "Forêt", "paper": "Carte", "accent": "Courbe", "accent2": "Lichen"},
                      notes={"ink": "le mot, le texte", "paper": "fond carte", "accent": "les courbes de niveau",
                             "accent2": "courbes lointaines, fonds sombres"})
    display = Font("Epilogue", "Epilogue[wght].ttf", {"wght": 800})
    body = Font("Figtree", "Figtree[wght].ttf", {"wght": 400})
    mono = Font("Red Hat Mono", "RedHatMono[wght].ttf", {"wght": 500})
    banner_scheme = "light"
    icon_scheme = "light"
    version = "v1"

    def _word(self):
        t, _ = tp.text("wubba", FONT[0], 200, FONT[1], tracking=-0.01)
        return t

    def wordmark(self):
        t = self._word()
        return [(contours(island(t, 34), 16, 16, 2, 5), "accent"), (t, "fg")]

    def wordmark_plain(self):
        return [(self._word(), "fg")]

    def symbol(self):
        t, _ = tp.text("w", FONT[0], 300, FONT[1])
        return [(contours(t, 22, 22, 3, 8), "accent"), (t, "fg")]

    def symbol_small(self):
        t, _ = tp.text("w", FONT[0], 300, FONT[1])
        return [(contours(t, 30, 30, 1, 16), "accent"), (t, "fg")]

    def device(self, W, H, sch, fmt):
        """Le relief s'étend à toute la bannière : les courbes naissent du mot posé au centre."""
        return []

    def banner_layout(self, fmt, W, H, sch, layout=None):
        if layout is not None:
            return None
        from compose import TAGLINE, DOMAIN, mix, page, text_line
        near = sch["accent"]
        far = mix(sch["bg"], sch.get("fg2") or sch["accent"], 0.55)
        muted = mix(sch["fg"], sch["bg"], 0.30)
        box = {"x-header": (W / 2 - 330, 225, W / 2 + 330, 385), "og": (W / 2 - 290, 290, W / 2 + 290, 450),
               "linkedin": (W - 640, 185, W - 110, 305), "linkedin-company": (W - 400, 88, W - 70, 146)}[fmt]
        word, s, (tx, ty) = self.place_t(self.wordmark_plain(), box)
        t = word[0][0]
        step = {"x-header": 24, "og": 26, "linkedin": 22, "linkedin-company": 13}[fmt]
        lw = 2.0 if H > 250 else 1.3
        peaks = {"x-header": [(W * 0.07, H * 0.18, 60), (W * 0.93, H * 0.86, 90)],
                 "og": [(W * 0.08, H * 0.12, 70), (W * 0.92, H * 0.9, 60)],
                 "linkedin": [(W * 0.3, H * 0.75, 50)], "linkedin-company": [(W * 0.25, H * 0.3, 30)]}[fmt]
        base = island(t, 34 * s)
        lines = terrain(W, H, base, step, seed={"x-header": 7, "og": 11, "linkedin": 5, "linkedin-company": 3}[fmt],
                        noise=38 if H > 250 else 16, peaks=peaks)
        frame = g.rect(0, 0, W, H)
        layers = []
        far_p = [p for k, p in lines if k >= 2]
        if far_p:
            layers.append((g.intersect(stroke_lines(far_p, lw), frame), far))
        # les deux premières courbes : celles du logo, nettes, qui n'appartiennent qu'au mot
        layers.append((g.intersect(contours(base, step, step, 2, lw * 1.25), frame), near))
        layers.append((t, sch["fg"]))
        tb = t.bounds
        if fmt in ("x-header", "og"):
            size = 16 if fmt == "x-header" else 18
            (bg_p, _), w, _ = text_line(TAGLINE, self.mono, size, W / 2, 0, muted, "center", True, 0.04, max_w=W * 0.8)
            y = tb[1] - step * 2.5 - size
            # une plage de fond sous la ligne pour qu'elle ne se batte pas avec les courbes
            pad = 12
            x0, y0, x1, y1 = bg_p.bounds
            layers.append((g.rounded_rect(x0 - pad - 4, y + y0 - pad, x1 + pad + 4, y + y1 + pad, 4, smooth=0.5), sch["bg"]))
            layers.append((g.translate(bg_p, dy=y), muted))
            dx, dy = (W - 76, H - 64) if fmt == "x-header" else (76, H - 64)
            (dp, _), dw, _ = text_line(DOMAIN, self.mono, 15, dx, dy, sch["fg"], "right" if fmt == "x-header" else "left", False, 0.03)
            x0, y0, x1, y1 = dp.bounds
            layers.append((g.rounded_rect(x0 - 10, y0 - 8, x1 + 10, y1 + 8, 4, smooth=0.5), sch["bg"]))
            layers.append((dp, sch["fg"]))
        return page(W, H, layers, bg=sch["bg"])
