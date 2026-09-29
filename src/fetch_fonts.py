"""Télécharge les polices (toutes sous licence SIL OFL ou Apache) depuis le dépôt officiel google/fonts.

    python3 src/fetch_fonts.py

Les fichiers atterrissent dans .fonts/ (ignoré par git). Le build les lit de là.
"""
from __future__ import annotations

import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / ".fonts"
BASE = "https://raw.githubusercontent.com/google/fonts/main/"

FILES = [
    "ofl/archivo/Archivo[wdth,wght].ttf",
    "ofl/instrumentsans/InstrumentSans[wdth,wght].ttf",
    "ofl/martianmono/MartianMono[wdth,wght].ttf",
    "ofl/geist/Geist[wght].ttf",
    "ofl/geistmono/GeistMono[wght].ttf",
    "ofl/inter/Inter[opsz,wght].ttf",
    "ofl/intertight/InterTight[wght].ttf",
    "ofl/jetbrainsmono/JetBrainsMono[wght].ttf",
    "ofl/ibmplexsans/IBMPlexSans[wdth,wght].ttf",
    "ofl/ibmplexmono/IBMPlexMono-Regular.ttf",
    "ofl/ibmplexmono/IBMPlexMono-Medium.ttf",
    "ofl/ibmplexmono/IBMPlexMono-SemiBold.ttf",
    "ofl/hankengrotesk/HankenGrotesk[wght].ttf",
    "ofl/bodonimoda/BodoniModa[opsz,wght].ttf",
    "ofl/instrumentserif/InstrumentSerif-Regular.ttf",
    "ofl/fraunces/Fraunces[SOFT,WONK,opsz,wght].ttf",
    "ofl/playfairdisplay/PlayfairDisplay[wght].ttf",
    "ofl/fredoka/Fredoka[wdth,wght].ttf",
    "ofl/baloo2/Baloo2[wght].ttf",
    "ofl/nunito/Nunito[wght].ttf",
    "ofl/unbounded/Unbounded[wght].ttf",
    "ofl/bigshouldersdisplay/BigShouldersDisplay[wght].ttf",
    "ofl/bigshouldersstencildisplay/BigShouldersStencilDisplay[wght].ttf",
    "ofl/barlow/Barlow-Regular.ttf",
    "ofl/barlow/Barlow-Medium.ttf",
    "ofl/barlow/Barlow-SemiBold.ttf",
    "ofl/spacegrotesk/SpaceGrotesk[wght].ttf",
    "ofl/spacemono/SpaceMono-Regular.ttf",
    "ofl/spacemono/SpaceMono-Bold.ttf",
    "ofl/syne/Syne[wght].ttf",
    "ofl/sora/Sora[wght].ttf",
    "ofl/manrope/Manrope[wght].ttf",
    "ofl/familjengrotesk/FamiljenGrotesk[wght].ttf",
    "ofl/schibstedgrotesk/SchibstedGrotesk[wght].ttf",
    "ofl/bricolagegrotesque/BricolageGrotesque[opsz,wdth,wght].ttf",
    "ofl/silkscreen/Silkscreen-Regular.ttf",
    "ofl/silkscreen/Silkscreen-Bold.ttf",
    "ofl/pixelifysans/PixelifySans[wght].ttf",
    "ofl/dmmono/DMMono-Regular.ttf",
    "ofl/dmmono/DMMono-Medium.ttf",
    "ofl/anybody/Anybody[wdth,wght].ttf",
    "ofl/onest/Onest[wght].ttf",
    "ofl/chivo/Chivo[wght].ttf",
    "ofl/chivomono/ChivoMono[wght].ttf",
    "ofl/azeretmono/AzeretMono[wght].ttf",
    "ofl/outfit/Outfit[wght].ttf",
    "ofl/epilogue/Epilogue[wght].ttf",
    "ofl/saira/Saira[wdth,wght].ttf",
    "ofl/figtree/Figtree[wght].ttf",
    "ofl/redhatmono/RedHatMono[wght].ttf",
    "ofl/redhatdisplay/RedHatDisplay[wght].ttf",
    "apache/permanentmarker/PermanentMarker-Regular.ttf",
    "ofl/sedgwickavedisplay/SedgwickAveDisplay-Regular.ttf",
    "ofl/barlowcondensed/BarlowCondensed-Bold.ttf",
    "ofl/barlowcondensed/BarlowCondensed-ExtraBold.ttf",
    "ofl/courierprime/CourierPrime-Regular.ttf",
    "ofl/courierprime/CourierPrime-Bold.ttf",
    "ofl/rubik/Rubik[wght].ttf",
    "ofl/lexend/Lexend[wght].ttf",
    "ofl/mrdafoe/MrDafoe-Regular.ttf",
]


def local_name(path):
    return Path(path).name


def fetch(path):
    target = DEST / local_name(path)
    if target.exists() and target.stat().st_size > 1000:
        return target, "cache"
    url = BASE + urllib.parse.quote(path)
    urllib.request.urlretrieve(url, target)
    return target, "ok"


if __name__ == "__main__":
    DEST.mkdir(exist_ok=True)
    bad = []
    for f in FILES:
        try:
            t, how = fetch(f)
            print(f"{how:5} {t.name}")
        except Exception as e:  # une police manquante ne bloque pas les autres
            bad.append((f, e))
            print(f"FAIL  {f}: {e}")
    sys.exit(1 if bad else 0)
