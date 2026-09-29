Le logo est le mot `wubba` en minuscules, avec un point rouge niché dans le creux du w, là où aucune lettre n'en porte. Tout le système suit cette règle : de l'encre, du papier, et un seul point de `wb-signal` par composition.

## Texte public autorisé

Utilise seulement ces textes dans les visuels publics, tels quels :

| Texte | Où |
| --- | --- |
| `wubba` | le nom, toujours en minuscules, dans le logo comme dans le texte |
| `AI streamers who test gaming gear where it has no business working` | la ligne sous le nom |
| `wubba.studio` | le domaine |
| `@wubbastudio` | l'identifiant sur les réseaux |
| `contact@wubba.studio` | le courriel |

- N'ajoute ni slogan, ni chiffre, ni nom de personne sans validation.
- La ligne se compose en `body` (casse normale) ou en `label` (capitales, Martian Mono). Jamais en titre Archivo.
- Pas d'émoji dans les visuels de marque.

## Couleur

- Répartis environ 60 % de fond (`wb-bg`), 35 % de neutres et de texte, 5 % au plus de `wb-signal`.
- Réserve `wb-signal` au point du logo et à un seul accent par mise en page : un voyant d'enregistrement, un mot, un bouton principal. Deux éléments rouges dans le même visuel, c'est un de trop.
- Ne compose jamais de texte en `wb-signal` sur `wb-paper` (3,27:1). Pour du texte rouge en clair, prends `wb-accent-text` (4,73:1 sur `wb-bg`).
- Sur un aplat `wb-accent`, pose `wb-on-accent` (encre, 5,14:1). Jamais de blanc sur le rouge.
- Texte courant : `wb-text` sur `wb-bg`, `wb-surface` ou `wb-surface-2`. Texte secondaire : `wb-text-muted`. `wb-text-faint` reste sous 4,5:1 : seulement 24 px et plus, ou mention non essentielle.
- `wb-line` et `wb-line-strong` sont des filets de décor. Une bordure qui porte une information (champ, case) prend `wb-text-muted` pour tenir 3:1.
- États : `wb-positive`, `wb-caution`, `wb-info` en remplissage ou en texte sur `wb-ink`, leurs versions `-text` en texte sur fond clair. Chaque état porte aussi un mot ou une icône : le vert et le rouge ne se distinguent pas par la seule teinte.
- Thème sombre : mêmes rôles. `wb-accent-text` devient `wb-signal` (5,14:1 sur `wb-bg`). Évite le texte rouge sur `wb-surface-2` en sombre (4,22:1).
- Pas de dégradé, pas de lueur, pas de néon. Les aplats suffisent.

## Typographie

- Titres : Archivo avec `font-stretch: 125%` (la coupe Expanded), graisse 800 (`hero` à `h3`), 700 pour `h4`. La largeur 125 % fait partie du dessin : sans elle, ce n'est plus la typo de la marque.
- Texte : Instrument Sans 400 (`lead`, `body`, `small`) ; 500 ou 600 pour l'emphase.
- Étiquettes, données, domaine : Martian Mono 500 en capitales, approche 0,08 em (`label`).
- Chargement : `https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&family=Instrument+Sans:wdth,wght@75..100,400..700&family=Martian+Mono:wdth,wght@75..112.5,100..800&display=swap`. Les trois familles sont sous licence SIL OFL.
- Ne compose jamais le logo avec une police : il est dessiné. Utilise les fichiers du groupe Logos.
- Lignes de texte courant entre 60 et 75 signes.

## Logo

- `wubba-logo.svg` sur fond clair (`wb-paper`, `wb-neutral-50`). `wubba-logo-reversed.svg` sur `wb-ink` et les fonds sombres.
- `wubba-logo-sur-signal.svg` sur un aplat `wb-signal` : le mot passe en encre, le point en papier.
- `wubba-logo-mono-noir.svg` et `wubba-logo-mono-blanc.svg` pour l'impression une couleur, la gravure, le tampon. Le point reste, il change seulement d'encre.
- Espace libre autour du logo : le diamètre du point (environ 22 % de la hauteur du logo). Rien n'y entre, pas même un filet.
- Taille minimale du mot : 96 px de large à l'écran, 25 mm en impression. En dessous, passe au symbole.
- Ne déplace pas le point, ne change pas sa couleur (hors versions mono), n'étire pas le mot, n'ajoute ni ombre ni contour ni effet. Sur une photo chargée, pose le logo sur un aplat `wb-ink` ou `wb-paper`.
- `wubba-filigrane.svg` (blanc) sert au filigrane des aperçus vidéo, à 20–30 % d'opacité.
- Les lockups (horizontal, empilé) associent la tuile et le mot pour les en-têtes de document et les signatures.

## Symbole et tuiles

- Le symbole est le w et son point : `wubba-symbole.svg` en clair, `wubba-symbole-reversed.svg` en sombre, versions mono pour une couleur.
- Sous 32 px, prends les versions `-petit` : le point y est plus gros et le trait plus épais, pour qu'ils survivent au rendu. `favicon.svg` en est une.
- Tuile d'application par défaut : `wubba-icone.svg` (fond encre). `wubba-icone-papier.svg` sur une interface sombre, `wubba-icone-signal.svg` pour un usage événementiel, `wubba-icone-rond.svg` pour les recadrages ronds (avatars), `wubba-icone-mono.svg` pour une couleur.
- L'arrondi des tuiles est `wb-radius-tile` (22 %) ; garde-le quand tu redessines une tuile à la main.

## Motifs graphiques

- Repères de suivi : de petites croix de 10 px, trait de 1,5 px, au pas de 100 px, en `wb-neutral-800` sur `wb-ink` ou `wb-neutral-200` sur `wb-paper`. Limite-les aux bords (13 % de la largeur de chaque côté) pour qu'ils ne passent jamais sous le texte.
- Coins de viseur : quatre équerres de 46 px, trait de 3 px, à 40 px du bord. Un seul de ces deux motifs par visuel.
- Le point peut réapparaître seul (le voyant d'enregistrement) comme unique accent, au diamètre du point du logo. Animé, il clignote avec `1.2s steps(1, end) infinite`, et reste fixe si `prefers-reduced-motion` est actif.

## Bannières

- Les formats livrés sont dans le groupe Social : X 1500 × 500, aperçu de lien 1200 × 630, LinkedIn 1584 × 396, page LinkedIn 1128 × 191, couverture YouTube 2560 × 1440 et bannière Twitch 1200 × 480.
- Sur YouTube, tout ce qui doit se lire tient dans le centre de 1546 × 423 (ce que montre un téléphone) ; les coins de viseur encadrent exactement cette zone et les repères de suivi remplissent le reste.
- Sur X, garde le coin bas gauche vide (environ 350 × 150 px) : l'avatar le recouvre.
- Fond `wb-ink`, logo inversé, ligne en `label`, domaine en Martian Mono à 15 px.

## Espacement, rayons, profondeur

- Base de 8 px, demi-pas de 4 px : `wb-space-1` à `wb-space-10`. Marge interne d'une carte : `wb-space-5` ; d'un bouton : `wb-space-4` sur les côtés, `wb-space-3` en hauteur.
- Rayons : `wb-radius-sm` pour étiquettes et champs, `wb-radius-md` pour boutons et cartes, `wb-radius-lg` pour les panneaux, `wb-radius-full` pour les pastilles et le point. Bannières et photos : `wb-radius-none`.
- Pas d'ombre portée : la profondeur vient des surfaces (`wb-surface` sur `wb-bg`) et des filets `wb-line`.

## Mouvement

- Courbes : `--wb-ease-out` = `cubic-bezier(0.2, 0, 0, 1)` pour les entrées, `--wb-ease-in-out` = `cubic-bezier(0.6, 0, 0.2, 1)` pour les déplacements.
- Durées : 120 ms (survol), 200 ms (ouverture), 320 ms (changement de page).
- Respecte `prefers-reduced-motion` : plus de mouvement, seulement des fondus de 120 ms.

## Accessibilité

- Anneau de focus : contour de 2 px en `wb-text`, décalé de 2 px (16,8:1 dans les deux thèmes, sur chaque surface).
- Tout texte tient 4,5:1 sur son fond (3:1 au-delà de 24 px) ; les notes des couleurs donnent les paires vérifiées.
