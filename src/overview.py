"""Planche d'ensemble : toutes les directions côte à côte, une ligne chacune."""
from __future__ import annotations

import compose
from directions import ALL

ROOT = compose.ROOT


def overview(out=ROOT / "options" / "overview.png", dirs=None):
    dirs = dirs or ALL
    rows = []
    for d in dirs:
        o = compose.OPT / f"{d.code}-{d.key}"
        f = lambda n: f"file://{o / n}"  # noqa: E731
        rows.append(f"""<div class="row"><div class="id"><b>{d.code}</b><span>{d.name}</span><i>{d.mark_type}</i></div>
<div class="c"><img src="{f('logo-light.png')}"></div><div class="c"><img src="{f('logo-dark.png')}"></div>
<div class="c sq"><img src="{f('icon.png')}"></div><div class="c fav"><img src="{f('favicon-test.png')}"></div>
<div class="c x"><img src="{f('x-header.png')}"></div></div>""")
    html = f"""<!doctype html><meta charset="utf-8"><style>
@font-face{{font-family:"M";src:url("file://{ROOT / '.fonts' / 'MartianMono[wdth,wght].ttf'}")}}
body{{margin:0;background:#EDEDEA;font:13px 'M';color:#222;width:1900px}}
.row{{display:grid;grid-template-columns:170px 330px 330px 120px 250px 1fr;gap:12px;align-items:center;
padding:12px 20px;border-bottom:1px solid #D2D1CC}}
.id b{{font-size:34px;display:block;line-height:1}} .id span{{display:block;margin-top:6px;font-size:13px}}
.id i{{display:block;font-style:normal;font-size:10px;color:#77766F;margin-top:4px;line-height:1.3}}
.c img{{width:100%;display:block}} .sq img{{width:110px}} .fav img{{width:100%;image-rendering:pixelated}}
</style>{''.join(rows)}"""
    hp = out.with_suffix(".html")
    hp.write_text(html)
    compose.render_html(hp, out, 1900, "auto", 1)
    hp.unlink()
    return out


if __name__ == "__main__":
    print(overview())
