"""Construit project/tokens.json (forme lue par la page Design System) depuis les valeurs réelles de tokens/tokens.css."""
import json, sys
from pathlib import Path

OUT = Path(sys.argv[1])

def c(name, value, usage):
    return {"name": name, "value": value, "usage": usage}

colors = [
    # Marque (identiques dans les deux thèmes)
    c("wb-ink", "#0e0f12", "Encre de marque. Fond des versions inversées, texte sur `wb-paper` (16,8:1), le w du logo."),
    c("wb-paper", "#f1f0ec", "Papier de marque. Fond clair par défaut, texte sur `wb-ink` (16,8:1)."),
    c("wb-signal", "#ff2a36", "Le rouge du point. Réservé au point du logo et à un seul accent par mise en page. Décor sur `wb-paper` (3,27:1) : jamais pour du texte courant en clair ; texte possible sur `wb-ink` (5,14:1)."),
    c("wb-signal-deep", "#d4101e", "Rouge lisible sur fond clair : texte et liens rouges sur `wb-paper` (4,73:1) et `wb-neutral-50` (5,17:1)."),
    # Neutres, encre vers papier
    c("wb-neutral-50", "#fbfaf6", "Surface claire la plus haute (cartes sur `wb-paper`)."),
    c("wb-neutral-100", "#f1f0ec", "Égal à `wb-paper` : fond clair."),
    c("wb-neutral-150", "#e7e6e2", "Creux et zones secondaires en clair."),
    c("wb-neutral-200", "#dad9d6", "Filets décoratifs en clair. Pas une bordure de contrôle (sous 3:1)."),
    c("wb-neutral-300", "#bebebb", "Filets appuyés en clair (1,63:1 sur `wb-paper` : décor seulement)."),
    c("wb-neutral-400", "#989897", "Texte secondaire en sombre : 6,64:1 sur `wb-ink`."),
    c("wb-neutral-500", "#787979", "Texte très discret : 3,83:1 sur `wb-paper`, 4,39:1 sur `wb-ink`. Seulement pour du texte de 24 px et plus, ou non essentiel."),
    c("wb-neutral-600", "#5c5c5d", "Texte secondaire en clair : 5,86:1 sur `wb-paper`."),
    c("wb-neutral-700", "#434445", "Filets appuyés et repères en sombre (décor)."),
    c("wb-neutral-800", "#2d2e30", "Filets en sombre (décor)."),
    c("wb-neutral-850", "#222325", "Creux et zones secondaires en sombre."),
    c("wb-neutral-900", "#18191c", "Cartes et surfaces sur `wb-ink`."),
    c("wb-neutral-950", "#0e0f12", "Égal à `wb-ink` : fond sombre."),
    # Échelle du signal
    c("wb-signal-50", "#fff2f1", "Teinte d'accent en clair (fond d'une ligne mise en avant)."),
    c("wb-signal-100", "#ffe0dc", "Teinte d'accent appuyée en clair."),
    c("wb-signal-300", "#ff9289", "Accent adouci, illustrations et graphiques."),
    c("wb-signal-500", "#ff2a36", "Égal à `wb-signal`."),
    c("wb-signal-600", "#d4101e", "Égal à `wb-signal-deep`."),
    c("wb-signal-800", "#7c1216", "Accent foncé, graphiques sur fond clair."),
    c("wb-signal-900", "#400c0c", "Teinte d'accent en sombre (fond d'une ligne mise en avant sur `wb-ink`)."),
    # États : toujours avec un mot ou une icône
    c("wb-positive", "#3aba6a", "Remplissage d'état « réussi » et texte sur `wb-ink` (7,68:1). Toujours avec un mot ou une icône."),
    c("wb-positive-text", "#007b2f", "Texte « réussi » sur `wb-paper` (4,75:1) et `wb-neutral-50` (5,19:1)."),
    c("wb-caution", "#f2b036", "Remplissage d'état « attention » et texte sur `wb-ink` (10,07:1)."),
    c("wb-caution-text", "#9a5c00", "Texte « attention » sur `wb-paper` (4,72:1) et `wb-neutral-50` (5,15:1)."),
    c("wb-info", "#468de5", "Remplissage d'état « info » et texte sur `wb-ink` (5,66:1)."),
    c("wb-info-text", "#226bc0", "Texte « info » sur `wb-paper` (4,68:1) et `wb-neutral-50` (5,11:1)."),
    # Rôles : clair puis sombre
    c("wb-bg", {"light": "#f1f0ec", "dark": "#0e0f12"}, "Fond de page."),
    c("wb-surface", {"light": "#fbfaf6", "dark": "#18191c"}, "Cartes et panneaux posés sur `wb-bg`."),
    c("wb-surface-2", {"light": "#e7e6e2", "dark": "#222325"}, "Creux, zones de code, rangées alternées."),
    c("wb-line", {"light": "#dad9d6", "dark": "#2d2e30"}, "Filets et séparateurs (décor, pas une bordure de contrôle)."),
    c("wb-line-strong", {"light": "#bebebb", "dark": "#434445"}, "Filets appuyés. Sous 3:1 dans les deux thèmes : ne porte jamais seul une information."),
    c("wb-text", {"light": "#0e0f12", "dark": "#f1f0ec"}, "Texte courant sur `wb-bg` (16,8:1), `wb-surface` et `wb-surface-2` (13,8:1 et plus), dans les deux thèmes. Aussi l'anneau de focus."),
    c("wb-text-muted", {"light": "#5c5c5d", "dark": "#989897"}, "Texte secondaire sur `wb-bg`, `wb-surface` et `wb-surface-2` : 5,35:1 et plus en clair, 5,45:1 et plus en sombre."),
    c("wb-text-faint", {"light": "#787979", "dark": "#787979"}, "Texte très discret. Valeur réelle gardée : 3,83:1 sur `wb-bg` clair, 4,39:1 en sombre, donc sous 4,5:1. Seulement pour 24 px et plus, ou pour une mention non essentielle."),
    c("wb-accent", {"light": "#ff2a36", "dark": "#ff2a36"}, "Remplissage d'accent : le point, un badge, un bouton principal. Poser `wb-on-accent` dessus."),
    c("wb-accent-text", {"light": "#d4101e", "dark": "#ff2a36"}, "Texte rouge : sur `wb-bg` (4,73:1 clair, 5,14:1 sombre) et `wb-surface` (5,17:1 clair, 4,72:1 sombre). Pas sur `wb-surface-2` en sombre (4,22:1)."),
    c("wb-accent-tint", {"light": "#fff2f1", "dark": "#400c0c"}, "Fond discret d'un élément mis en avant ; y poser `wb-accent-text` (4,94:1 clair) ou `wb-text`."),
    c("wb-on-accent", {"light": "#0e0f12", "dark": "#0e0f12"}, "Texte et icônes posés sur `wb-accent` : 5,14:1 dans les deux thèmes."),
    # Alias génériques de la source
    c("brand-bg", "{wb-bg}", "Alias générique de `wb-bg` pour les outils qui attendent ce nom."),
    c("brand-text", "{wb-text}", "Alias générique de `wb-text`."),
    c("brand-accent", "{wb-accent}", "Alias générique de `wb-accent`."),
]

def st(name, size, lh, ls, wt, sample, usage):
    return {"name": name, "fontSize": size, "lineHeight": lh, "letterSpacing": ls, "fontWeight": wt, "sample": sample, "usage": usage}

TAG = "AI streamers who test gaming gear where it has no business working"
tokens = {
    "name": "wubba",
    "version": 1,
    "color": {"themes": [{"id": "light", "name": "Clair"}, {"id": "dark", "name": "Sombre"}], "tokens": colors},
    "type": {
        "fonts": [],
        "families": {
            "display": "\"Archivo\", \"Arial Black\", \"Helvetica Neue\", Arial, sans-serif",
            "body": "\"Instrument Sans\", \"Helvetica Neue\", Arial, sans-serif",
            "mono": "\"Martian Mono\", \"SFMono-Regular\", Menlo, Consolas, monospace",
        },
        "groups": [
            {"name": "Titres", "family": "display", "styles": [
                st("hero", "90px", 0.96, "-0.025em", 800, "wubba", "Titre d'ouverture, une fois par page ou par visuel. En Archivo avec `font-stretch: 125%`."),
                st("display", "67px", 1.0, "-0.02em", 800, "wubba.studio", "Grand titre de section ou de bannière. Archivo, largeur 125 %."),
                st("h1", "50px", 1.02, "-0.015em", 800, "wubba", "Titre de page. Archivo, largeur 125 %."),
                st("h2", "38px", 1.05, "-0.01em", 800, "wubba.studio", "Titre de section. Archivo, largeur 125 %."),
                st("h3", "28px", 1.1, "-0.01em", 800, "wubba.studio", "Sous-section. Archivo, largeur 125 %."),
                st("h4", "21px", 1.15, "-0.005em", 700, "wubba.studio", "Petit titre, carte. Archivo 700, largeur 125 %."),
            ]},
            {"name": "Texte", "family": "body", "styles": [
                st("lead", "21px", 1.45, "-0.005em", 400, TAG, "Chapeau sous un titre. Instrument Sans."),
                st("body", "16px", 1.55, "0em", 400, TAG, "Texte courant. Instrument Sans ; 500 ou 600 pour l'emphase, jamais d'italique de substitution."),
                st("small", "14px", 1.45, "0em", 400, "contact@wubba.studio", "Légendes, notes, pieds de page."),
            ]},
            {"name": "Étiquettes", "family": "mono", "styles": [
                st("label", "12px", 1.3, "0.08em", 500, "@WUBBASTUDIO", "Étiquettes, données, repères, domaine. Martian Mono 500 en capitales, approche 0,08 em."),
            ]},
        ],
    },
    "spacing": {"tokens": [
        c("wb-space-0", "0px", "Aucun espace."),
        c("wb-space-1", "4px", "Demi-pas : écart icône-texte, filets serrés."),
        c("wb-space-2", "8px", "Pas de base : écart dans un groupe de contrôles."),
        c("wb-space-3", "12px", "Marge interne des étiquettes et badges."),
        c("wb-space-4", "16px", "Marge interne des boutons et des cartes compactes."),
        c("wb-space-5", "24px", "Marge interne des cartes, écart entre blocs."),
        c("wb-space-6", "32px", "Écart entre groupes, marge des bannières sociales."),
        c("wb-space-7", "48px", "Écart entre sections serrées."),
        c("wb-space-8", "64px", "Écart entre sections."),
        c("wb-space-9", "96px", "Grandes respirations, marges de page larges."),
        c("wb-space-10", "128px", "Ouverture de page, héros."),
    ]},
    "radius": {"tokens": [
        c("wb-radius-none", "0px", "Bannières, photos, grands aplats."),
        c("wb-radius-sm", "4px", "Étiquettes, champs, badges."),
        c("wb-radius-md", "8px", "Boutons, cartes."),
        c("wb-radius-lg", "14px", "Panneaux et fenêtres."),
        c("wb-radius-tile", "22%", "Tuiles d'application : le même arrondi que l'icône."),
        c("wb-radius-full", "9999px", "Pastilles et le point : un cercle parfait."),
    ]},
}
(OUT / "tokens.json").write_text(json.dumps(tokens, ensure_ascii=False, indent=2) + "\n")
names = [t["name"] for fam in ("color", "spacing", "radius") for t in tokens[fam]["tokens"]]
assert len(names) == len(set(names)), "noms en double"
print("tokens.json", len(names), "tokens")
