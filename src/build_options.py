"""Construit toutes les directions : logos, icônes, bannières, maquette de profil, planche.

    python3 src/build_options.py            # toutes
    python3 src/build_options.py A C        # seulement certaines (par code)
"""
from __future__ import annotations

import sys
import time

import boards
import compose
from directions import ALL


def build(d):
    out = compose.OPT / f"{d.code}-{d.key}"
    out.mkdir(parents=True, exist_ok=True)
    compose.logo_set(d, out)
    compose.banner_set(d, out)
    compose.profile_mock(d, out)
    boards.board(d, out, version=getattr(d, "version", "v1"))
    return out


if __name__ == "__main__":
    want = set(sys.argv[1:])
    for d in ALL:
        if want and d.code not in want:
            continue
        t = time.time()
        out = build(d)
        print(f"{d.code} {d.name:<28} {time.time() - t:5.1f}s -> {out.relative_to(compose.ROOT)}")
