# wubba — identité visuelle

Dix-sept directions complètes pour choisir le visuel de wubba, notées sur 50 et retravaillées, avec le kit de production de la direction recommandée. Tout est généré par le code de `src/` : aucun fichier n'est retouché à la main.

## Par où commencer

- **Le catalogue** : `catalogue/index.html`. Toutes les options, avec un bouton « Je garde » sur chacune. Il est aussi publié en page privée sur claude.ai.
- **La vue d'ensemble** : `options/overview.png`. Une ligne par direction : logo clair, logo sombre, icône, favicon à 16, 24, 32 et 48 px, bannière X.
- **Une direction en détail** : `options/<lettre>-<nom>/board.png`.

## Les directions

| | Direction | Note v2 |
| --- | --- | --- |
| A | Le point de trop | 44 |
| O | Touche W | 43 |
| D | Horizon | 41 |
| H | Protocole | 41 |
| E | Maison | 40 |
| F | Bulle | 40 |
| J | Signal | 40 |
| B | Pixel mort | 39 |
| M | Sceau | 39 |
| N | Autographe | 39 |
| P | Topo | 39 |
| Q | Mire | 39 |
| C | Incrustation | 38 |
| G | Vitesse | 37 |
| I | Terrain | 36 |
| K | Réticule (écartée) | 34 |
| L | Tranche (écartée) | 31 |

La grille de notation, les défauts de chaque v1 et ce que chaque itération a changé sont dans `src/critique.py`.

## Ce que contient le repo

| Dossier | Contenu |
| --- | --- |
| `options/<direction>/` | logos (SVG et PNG, clair, sombre, mono, sur accent), symbole, icônes, avatar, favicon testé, bannières X, aperçu de lien, LinkedIn, planche |
| `options/<direction>/palettes/` | la même direction dans d'autres couleurs (10 directions, 44 palettes) |
| `options/<direction>/layouts/` | 8 mises en page de bannières (7 directions) |
| `options/<direction>/motion/` | animation de fin de vidéo 16:9 (MP4), version transparente (WebM, pour OBS), carton vertical 9:16, aperçu animé (8 directions) |
| `options/<direction>/mockups/` | planche d'autocollants et signature courriel (toutes les directions) |
| `options/A-point/signes/`, `typo/` | 9 variantes du signe de A, 5 paires typographiques |
| `logo/` | le kit complet de la direction A : SVG, PNG à toutes les tailles, WebP, PDF vectoriels, favicons et manifeste web, avatars, filigrane |
| `tokens/` | tokens de A : CSS, JSON (format W3C), Tailwind, Figma, Sass, Style Dictionary, TypeScript |
| `palette/` | palette de A en `.ase` (Adobe), `.gpl` (GIMP, Inkscape) et JSON |
| `design-system/` | le design system de A (tokens, guide d'usage, couverture), tel que publié sur claude.ai |
| `catalogue/` | la page de choix et ses images |
| `src/` | le code |

## Régénérer

```sh
pip install cairosvg skia-pathops fonttools uharfbuzz pillow imageio-ffmpeg numpy scipy scikit-image
npm install -g playwright   # rendu HTML -> PNG des planches
python3 src/fetch_fonts.py            # polices libres (SIL OFL, Apache) depuis google/fonts
python3 src/build_logo.py             # kit complet de la direction A
python3 src/tokens.py                 # tokens et palettes de A
python3 src/build_options.py          # les 17 directions (ou : python3 src/build_options.py A O D)
python3 src/variants.py palettes      # palettes alternatives
python3 src/variants.py marks         # variantes du signe de A
python3 src/variants.py type          # paires typographiques
python3 src/layouts.py A O D H E F J  # mises en page de bannières
python3 src/motion.py                 # animations
python3 src/mockups.py                # autocollants et signatures
python3 src/overview.py               # vue d'ensemble
python3 src/catalogue.py              # catalogue HTML
```

## Règles suivies

- Seuls les textes publics validés apparaissent dans les visuels : `wubba`, la ligne « AI streamers who test gaming gear where it has no business working », `wubba.studio`, `@wubbastudio`, `contact@wubba.studio`.
- Aucun texte vivant, filtre ou image dans les SVG : que des tracés.
- Toutes les polices sont libres (SIL OFL ou Apache 2.0).
- À faire avant le lancement : une recherche de marque déposée sur le nom et la direction retenue, et une épreuve papier si le logo s'imprime (les rouges et les orangés vifs bougent en CMJN).
