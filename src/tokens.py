"""Tokens de design Wubba : CSS, JSON (format W3C DTCG), palettes .gpl/.ase, et le BrandIdentity
attendu par branding-mcp (qui s'occupe ensuite des exports Tailwind, Figma, Sass, Style Dictionary).
"""
from __future__ import annotations

import json
import struct
from pathlib import Path

import palette as pal

ROOT = Path(__file__).resolve().parent.parent

FONTS = {
    "display": {"family": "Archivo", "stack": '"Archivo", "Arial Black", "Helvetica Neue", Arial, sans-serif',
                "stretch": "125%", "weights": [700, 800],
                "url": "https://fonts.google.com/specimen/Archivo"},
    "body": {"family": "Instrument Sans", "stack": '"Instrument Sans", "Helvetica Neue", Arial, sans-serif',
             "stretch": "100%", "weights": [400, 500, 600],
             "url": "https://fonts.google.com/specimen/Instrument+Sans"},
    "mono": {"family": "Martian Mono", "stack": '"Martian Mono", "SFMono-Regular", Menlo, Consolas, monospace',
             "stretch": "100%", "weights": [400, 500],
             "url": "https://fonts.google.com/specimen/Martian+Mono"},
}
GOOGLE_CSS = ("https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900"
              "&family=Instrument+Sans:wdth,wght@75..100,400..700"
              "&family=Martian+Mono:wdth,wght@75..112.5,100..800&display=swap")

# Échelle quarte juste (1.333) sur une base de 16 px, arrondie au pixel.
TYPE_SCALE = [
    # nom, taille px, interligne, approche, famille, graisse
    ("label", 12, 1.3, "0.08em", "mono", 500),
    ("small", 14, 1.45, "0em", "body", 400),
    ("body", 16, 1.55, "0em", "body", 400),
    ("lead", 21, 1.45, "-0.005em", "body", 400),
    ("h4", 21, 1.15, "-0.005em", "display", 700),
    ("h3", 28, 1.1, "-0.01em", "display", 800),
    ("h2", 38, 1.05, "-0.01em", "display", 800),
    ("h1", 50, 1.02, "-0.015em", "display", 800),
    ("display", 67, 1.0, "-0.02em", "display", 800),
    ("hero", 90, 0.96, "-0.025em", "display", 800),
]
SPACE = {"0": 0, "1": 4, "2": 8, "3": 12, "4": 16, "5": 24, "6": 32, "7": 48, "8": 64, "9": 96, "10": 128}
RADIUS = {"none": "0px", "sm": "4px", "md": "8px", "lg": "14px", "tile": "22%", "full": "9999px"}
MOTION = {
    "ease-out": "cubic-bezier(0.2, 0, 0, 1)", "ease-in-out": "cubic-bezier(0.6, 0, 0.2, 1)",
    "fast": "120ms", "base": "200ms", "slow": "320ms",
    "rec-blink": "1.2s steps(1, end) infinite",  # le point clignote comme un voyant REC, rien d'autre ne clignote
}


def color_table():
    n, s = pal.NEUTRAL, pal.SIGNAL_SCALE
    rows = [("Encre", "ink", pal.INK, "Primaire. Texte, fonds sombres, le logo"),
            ("Papier", "paper", pal.PAPER, "Secondaire. Fonds clairs, texte sur sombre"),
            ("Signal", "signal", pal.SIGNAL, "Accent. Le point du logo, un seul élément par composition"),
            ("Signal profond", "signal-deep", s[600], "Texte rouge sur fond clair (4,7:1)")]
    return rows


def css():
    n, s, st, stt = pal.NEUTRAL, pal.SIGNAL_SCALE, pal.STATE, pal.STATE_TEXT
    t = pal.tokens()
    lines = ["/* Wubba — tokens de design. Généré par src/tokens.py : ne pas éditer à la main. */",
             f'@import url("{GOOGLE_CSS}");', "", ":root {",
             "  /* Marque */",
             f"  --wb-ink: {pal.INK};", f"  --wb-paper: {pal.PAPER};", f"  --wb-signal: {pal.SIGNAL};",
             f"  --wb-signal-deep: {s[600]};", "", "  /* Neutres (encre -> papier) */"]
    lines += [f"  --wb-neutral-{k}: {v};" for k, v in sorted(n.items())]
    lines += ["", "  /* Signal */"] + [f"  --wb-signal-{k}: {v};" for k, v in sorted(s.items())]
    lines += ["", "  /* États */"]
    for k in st:
        lines += [f"  --wb-{k}: {st[k]};", f"  --wb-{k}-text: {stt[k]};"]
    lines += ["", "  /* Typo */"]
    for role, f in FONTS.items():
        lines += [f"  --wb-font-{role}: {f['stack']};", f"  --wb-stretch-{role}: {f['stretch']};"]
    for name, size, lh, ls, fam, wgt in TYPE_SCALE:
        lines += [f"  --wb-text-{name}: {size / 16:.4g}rem;", f"  --wb-leading-{name}: {lh};",
                  f"  --wb-tracking-{name}: {ls};"]
    lines += ["", "  /* Espace (base 8, demi-pas de 4) */"] + [f"  --wb-space-{k}: {v}px;" for k, v in SPACE.items()]
    lines += ["", "  /* Rayons */"] + [f"  --wb-radius-{k}: {v};" for k, v in RADIUS.items()]
    lines += ["", "  /* Mouvement */"] + [f"  --wb-{k}: {v};" for k, v in MOTION.items()]
    lines += ["", "  /* Rôles, thème clair par défaut */"]
    lines += [f"  --wb-{k}: {v};" for k, v in t["light"].items()]
    lines += ["  /* Alias génériques */", "  --brand-bg: var(--wb-bg);", "  --brand-text: var(--wb-text);",
              "  --brand-accent: var(--wb-accent);", "}", "",
              "@media (prefers-color-scheme: dark) {", "  :root:not([data-theme=\"light\"]) {"]
    lines += [f"    --wb-{k}: {v};" for k, v in t["dark"].items()]
    lines += ["  }", "}", "", ":root[data-theme=\"dark\"] {"]
    lines += [f"  --wb-{k}: {v};" for k, v in t["dark"].items()]
    lines += ["}", "",
              "/* Styles de base prêts à l'emploi */",
              ".wb-display { font-family: var(--wb-font-display); font-stretch: var(--wb-stretch-display); font-weight: 800; }",
              ".wb-label { font-family: var(--wb-font-mono); font-size: var(--wb-text-label); letter-spacing: var(--wb-tracking-label); text-transform: uppercase; }",
              ".wb-rec { width: .6em; height: .6em; border-radius: 50%; background: var(--wb-signal); display: inline-block; }",
              "@media (prefers-reduced-motion: no-preference) { .wb-rec.is-live { animation: wb-blink var(--wb-rec-blink); } }",
              "@keyframes wb-blink { 50% { opacity: 0; } }", ""]
    return "\n".join(lines)


def dtcg():
    """Format W3C Design Tokens Community Group ($value / $type)."""
    n, s = pal.NEUTRAL, pal.SIGNAL_SCALE

    def c(v, d=None):
        o = {"$type": "color", "$value": v}
        if d:
            o["$description"] = d
        return o
    t = pal.tokens()
    return {
        "color": {
            "brand": {k: c(v, d) for _, k, v, d in color_table()},
            "neutral": {str(k): c(v) for k, v in sorted(n.items())},
            "signal": {str(k): c(v) for k, v in sorted(s.items())},
            "state": {**{k: c(v) for k, v in pal.STATE.items()},
                      **{f"{k}-text": c(v) for k, v in pal.STATE_TEXT.items()}},
            "role": {theme: {k: c(v) for k, v in roles.items()} for theme, roles in t.items()},
        },
        "font": {role: {"family": {"$type": "fontFamily", "$value": [f["family"]] + [x.strip().strip('"') for x in f["stack"].split(",")[1:]]},
                        "stretch": {"$type": "string", "$value": f["stretch"]},
                        "weights": {"$type": "string", "$value": ",".join(map(str, f["weights"]))}}
                 for role, f in FONTS.items()},
        "type": {name: {"$type": "typography", "$value": {
            "fontFamily": FONTS[fam]["family"], "fontSize": f"{size}px", "lineHeight": lh,
            "letterSpacing": ls, "fontWeight": wgt}} for name, size, lh, ls, fam, wgt in TYPE_SCALE},
        "space": {k: {"$type": "dimension", "$value": f"{v}px"} for k, v in SPACE.items()},
        "radius": {k: {"$type": "dimension", "$value": v} for k, v in RADIUS.items()},
        "motion": {k: {"$type": "string", "$value": v} for k, v in MOTION.items()},
    }


def gpl():
    rows = ["GIMP Palette", "Name: Wubba", "Columns: 4", "#"]
    allc = [(label, v) for label, _, v, _ in color_table()]
    allc += [(f"Neutre {k}", v) for k, v in sorted(pal.NEUTRAL.items())]
    allc += [(f"Signal {k}", v) for k, v in sorted(pal.SIGNAL_SCALE.items())]
    for label, v in allc:
        r, g, b = (round(x * 255) for x in pal.hex_to_rgb(v))
        rows.append(f"{r:3d} {g:3d} {b:3d}\t{label} {v}")
    return "\n".join(rows) + "\n"


def ase():
    """Adobe Swatch Exchange : un groupe « Wubba » avec les couleurs de marque et les neutres."""
    entries = [(f"{label} {v}", v) for label, _, v, _ in color_table()]
    entries += [(f"Neutre {k} {v}", v) for k, v in sorted(pal.NEUTRAL.items())]

    def block(btype, payload):
        return struct.pack(">HI", btype, len(payload)) + payload

    def name(s):
        enc = (s + "\0").encode("utf-16-be")
        return struct.pack(">H", len(s) + 1) + enc

    blocks = [block(0xC001, name("Wubba"))]
    for label, v in entries:
        r, g, b = pal.hex_to_rgb(v)
        blocks.append(block(0x0001, name(label) + b"RGB " + struct.pack(">fffH", r, g, b, 2)))
    blocks.append(block(0xC002, b""))
    return b"ASEF" + struct.pack(">HHI", 1, 0, len(blocks)) + b"".join(blocks)


def brand_identity(logo_svg=""):
    """BrandIdentity au format de branding-mcp, rempli avec les vraies valeurs Wubba."""
    base = json.loads((ROOT / "src" / "vendor" / "brand_identity_schema.json").read_text())
    n = pal.NEUTRAL

    def col(name, hexv, usage):
        r, g, b = pal.hex_to_rgb(hexv)
        mx, mn = max(r, g, b), min(r, g, b)
        L = (mx + mn) / 2
        d = mx - mn
        S = 0 if d == 0 else d / (1 - abs(2 * L - 1))
        if d == 0:
            H = 0
        elif mx == r:
            H = 60 * (((g - b) / d) % 6)
        elif mx == g:
            H = 60 * ((b - r) / d + 2)
        else:
            H = 60 * ((r - g) / d + 4)
        return {"name": name, "hex": hexv.lower(), "hsl": {"h": round(H), "s": round(S * 100), "l": round(L * 100)},
                "usage": usage}

    base["name"] = "wubba"
    base["industry"] = "AI video studio for gaming brands"
    base["style"] = "bold"
    base["colors"]["primary"] = col("ink", pal.INK, "Primaire : texte, fonds sombres, logo")
    base["colors"]["secondary"] = col("paper", pal.PAPER, "Secondaire : fonds clairs, texte sur sombre")
    base["colors"]["accent"] = col("signal", pal.SIGNAL, "Accent : le point, un seul élément par composition")
    base["colors"]["neutral"] = [col(f"neutral-{k}", v, f"Neutre {k}") for k, v in sorted(n.items())]
    base["colors"]["semantic"] = {
        "success": col("success", pal.STATE["positive"], "États positifs"),
        "warning": col("warning", pal.STATE["caution"], "Avertissements"),
        "error": col("error", pal.SIGNAL_SCALE[600], "Erreurs (rouge profond, lisible sur clair)"),
        "info": col("info", pal.STATE["info"], "Information"),
    }
    base["colors"].pop("contrast", None)
    ty = base["typography"]
    ty["headingFont"], ty["bodyFont"], ty["monoFont"] = "Archivo", "Instrument Sans", "Martian Mono"
    ty["baseSize"], ty["scaleRatio"] = 16, 1.333
    ty["steps"] = [{"name": name, "size": f"{size}px", "lineHeight": str(lh), "letterSpacing": ls, "weight": wgt}
                   for name, size, lh, ls, fam, wgt in TYPE_SCALE]
    base["spacing"] = {"unit": 4, "values": {k: f"{v}px" for k, v in SPACE.items()}}
    base["borders"]["radii"] = {k: v for k, v in RADIUS.items()}
    base["borders"]["widths"] = {"thin": "1px", "medium": "2px", "thick": "4px"}
    base["shadows"] = {"levels": {"none": base["shadows"]["levels"]["none"]}}
    base["motion"]["durations"] = {"fast": MOTION["fast"], "normal": MOTION["base"], "slow": MOTION["slow"]}
    base["motion"]["easings"] = {"ease-out": MOTION["ease-out"], "ease-in-out": MOTION["ease-in-out"]}
    base["gradients"] = {"presets": {}}
    if logo_svg:
        base["logo"] = {"svg": logo_svg, "variants": {}}
    return base


def write_all(out=ROOT / "tokens"):
    out.mkdir(parents=True, exist_ok=True)
    (out / "tokens.css").write_text(css())
    (out / "tokens.json").write_text(json.dumps(dtcg(), indent=2, ensure_ascii=False) + "\n")
    pdir = ROOT / "palette"
    pdir.mkdir(exist_ok=True)
    (pdir / "wubba.gpl").write_text(gpl())
    (pdir / "wubba.ase").write_bytes(ase())
    flat = {
        "brand": {k: v for _, k, v, _ in color_table()},
        "neutral": {str(k): v for k, v in sorted(pal.NEUTRAL.items())},
        "signal": {str(k): v for k, v in sorted(pal.SIGNAL_SCALE.items())},
        "state": pal.STATE, "state_text": pal.STATE_TEXT,
        "contrast": {
            "paper_on_ink": round(pal.contrast(pal.PAPER, pal.INK), 2),
            "signal_on_ink": round(pal.contrast(pal.SIGNAL, pal.INK), 2),
            "signal_on_paper": round(pal.contrast(pal.SIGNAL, pal.PAPER), 2),
            "signal_deep_on_paper": round(pal.contrast(pal.SIGNAL_SCALE[600], pal.PAPER), 2),
            "ink_on_signal": round(pal.contrast(pal.INK, pal.SIGNAL), 2),
        },
    }
    (pdir / "palette.json").write_text(json.dumps(flat, indent=2) + "\n")
    return out


if __name__ == "__main__":
    print("tokens ->", write_all())
