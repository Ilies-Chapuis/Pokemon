#Données des zones de la carte

ZONES = {
    "plaine": {
        "nom": "Plaine Verdoyante",
        "couleur": (100, 200, 100),
        "pokemon": {
            "communs":     ["Keunotor", "Timiki", "Zaptile", "Rubycire", "Minikoal"],
            "peu_communs": ["Bloupy", "Voltalin", "Lupika", "Floraclaw"],
            "rares":       ["BuffMachok", "Cendralis", "Flamydra", "Verdalune"],
            "tres_rares":  [],
            "legendaires": [],
        },
        "taux_rencontre": 0.15,
    },
    "foret": {
        "nom": "Forêt Mystique",
        "couleur": (50, 150, 50),
        "pokemon": {
            "communs":     ["Floraclaw", "Brisaflamme", "Verdalune"],
            "peu_communs": ["Floritank", "Lumyntha", "Zorova"],
            "rares":       ["Gardekrom", "Noctevoir"],
            "tres_rares":  ["Reshivoir"],
            "legendaires": ["SylphraL"],
        },
        "taux_rencontre": 0.20,
    },
    "montagne": {
        "nom": "Mont Rocheux",
        "couleur": (150, 150, 150),
        "pokemon": {
            "communs":     ["Bavoir", "Magmire", "Rubycire"],
            "peu_communs": ["Scalydra", "Tournecendre", "Minikoal"],
            "rares":       ["Flameking", "Staralon", "Arrchamp"],
            "tres_rares":  ["Reshiflame"],
            "legendaires": ["BraseoL"],
        },
        "taux_rencontre": 0.18,
    },
    "ocean": {
        "nom": "Océan Bleu",
        "couleur": (50, 100, 200),
        "pokemon": {
            "communs":     ["Muddew", "ZapZap"],
            "peu_communs": ["Luvoir", "Dragodash", "Okeloke"],
            "rares":       ["Flamydra", "Verdalune"],
            "tres_rares":  ["Reshirom"],
            "legendaires": ["PyraflinL"],
        },
        "taux_rencontre": 0.12,
    },
    "grotte": {
        "nom": "Grotte Sombre",
        "couleur": (80, 80, 100),
        "pokemon": {
            "communs":     ["Skelerat", "Noctyssor"],
            "peu_communs": ["Darkamph", "Noxor", "Lumyntha"],
            "rares":       ["Nebulyx", "Noctevoir", "Zevoir"],
            "tres_rares":  ["Dragodreavus"],
            "legendaires": ["KarionLR"],
        },
        "taux_rencontre": 0.22,
    },
    "ciel": {
        "nom": "Ciel Étoilé",
        "couleur": (150, 150, 255),
        "pokemon": {
            "communs":     ["Brisaflamme", "Dragodash"],
            "peu_communs": ["Cendralis", "Luvoir", "Reunito"],
            "rares":       ["Jiraly_Rare", "Noxalis", "Ventoryx"],
            "tres_rares":  ["Poryluff", "Snubrua"],
            "legendaires": ["AuredrisL"],
        },
        "taux_rencontre": 0.08,
    },
    "ville": {
        "nom": "Ville",
        "couleur": (200, 200, 200),
        "pokemon": {
            "communs":     [],
            "peu_communs": [],
            "rares":       [],
            "tres_rares":  [],
            "legendaires": [],
        },
        "taux_rencontre": 0.0,
    },
}
