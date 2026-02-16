import json
import random
from pokemon import Pokemon

# Définition des zones de la carte
ZONES = {
    "plaine": {
        "nom": "Plaine Verdoyante",
        "couleur": (100, 200, 100),
        "pokemon": {
            "communs": ["Keunotor", "Timiki", "Zaptile", "Rubycire", "Minikoal"],
            "peu_communs": ["Bloupy", "Voltalin", "Lupika", "Floraclaw"],
            "rares": ["BuffMachok", "Cendralis", "Flamydra", "Verdalune"],
            "tres_rares": [],
            "legendaires": []
        },
        "taux_rencontre": 0.15  # 15% par case
    },
    "foret": {
        "nom": "Forêt Mystique",
        "couleur": (50, 150, 50),
        "pokemon": {
            "communs": ["Floraclaw", "Brisaflamme", "Verdalune"],
            "peu_communs": ["Floritank", "Lumyntha", "Zorova"],
            "rares": ["Gardekrom", "Noctevoir"],
            "tres_rares": ["Reshivoir"],
            "legendaires": ["SylphraL"]
        },
        "taux_rencontre": 0.20
    },
    "montagne": {
        "nom": "Mont Rocheux",
        "couleur": (150, 150, 150),
        "pokemon": {
            "communs": ["Bavoir", "Magmire", "Rubycire"],
            "peu_communs": ["Scalydra", "Tournecendre", "Minikoal"],
            "rares": ["Flameking", "Staralon", "Arrchamp"],
            "tres_rares": ["Reshiflame"],
            "legendaires": ["BraseoL"]
        },
        "taux_rencontre": 0.18
    },
    "ocean": {
        "nom": "Océan Bleu",
        "couleur": (50, 100, 200),
        "pokemon": {
            "communs": ["Muddew", "ZapZap"],
            "peu_communs": ["Luvoir", "Dragodash", "Okeloke"],
            "rares": ["Flamydra", "Verdalune"],
            "tres_rares": ["Reshirom"],
            "legendaires": ["PyraflinL"]
        },
        "taux_rencontre": 0.12
    },
    "grotte": {
        "nom": "Grotte Sombre",
        "couleur": (80, 80, 100),
        "pokemon": {
            "communs": ["Skelerat", "Noctyssor"],
            "peu_communs": ["Darkamph", "Noxor", "Lumyntha"],
            "rares": ["Nebulyx", "Noctevoir", "Zevoir"],
            "tres_rares": ["Dragodreavus"],
            "legendaires": ["KarionLR"]
        },
        "taux_rencontre": 0.22
    },
    "ciel": {
        "nom": "Ciel Étoilé",
        "couleur": (150, 150, 255),
        "pokemon": {
            "communs": ["Brisaflamme", "Dragodash"],
            "peu_communs": ["Cendralis", "Luvoir", "Reunito"],
            "rares": ["Jiraly_Rare", "Noxalis", "Ventoryx"],
            "tres_rares": ["Poryluff", "Snubrua"],
            "legendaires": ["AuredrisL"]
        },
        "taux_rencontre": 0.08
    },
    "ville": {
        "nom": "Ville",
        "couleur": (200, 200, 200),
        "pokemon": {
            "communs": [],
            "peu_communs": [],
            "rares": [],
            "tres_rares": [],
            "legendaires": []
        },
        "taux_rencontre": 0.0
    }
}


class Carte:
    def __init__(self, largeur=20, hauteur=15):
        self.largeur = largeur
        self.hauteur = hauteur
        self.grille = self.generer_carte()

    def generer_carte(self):
        """Génère une carte procédurale avec différentes zones"""
        grille = []

        for y in range(self.hauteur):
            ligne = []
            for x in range(self.largeur):
                # Ville au centre
                if 8 <= x <= 11 and 6 <= y <= 8:
                    ligne.append("ville")
                # Océan sur les bords
                elif x < 2 or x >= self.largeur - 2:
                    ligne.append("ocean")
                # Montagnes
                elif (x < 5 and y < 5) or (x >= self.largeur - 5 and y >= self.hauteur - 5):
                    ligne.append("montagne")
                # Grotte (zones sombres)
                elif 3 <= x <= 5 and 10 <= y <= 12:
                    ligne.append("grotte")
                # Forêt
                elif y < 7 and x > 5 and x < 14:
                    ligne.append("foret")
                # Ciel (zones hautes)
                elif y == 0 or (y < 3 and 7 <= x <= 12):
                    ligne.append("ciel")
                # Plaine par défaut
                else:
                    ligne.append("plaine")
            grille.append(ligne)

        return grille

    def get_zone(self, x, y):
        """Retourne la zone à une position donnée"""
        if 0 <= x < self.largeur and 0 <= y < self.hauteur:
            return self.grille[y][x]
        return "plaine"


class RencontreManager:
    def __init__(self, pokedex_file):
        """Initialise le gestionnaire de rencontres avec le Pokédex"""
        with open(pokedex_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.pokedex = {p["name"]: p for p in data["pokemon"]}

    def verifier_rencontre(self, zone_type, position):
        """Vérifie si une rencontre a lieu sur cette case"""
        if zone_type not in ZONES:
            return None

        zone = ZONES[zone_type]

        # Vérifier si une rencontre se produit
        if random.random() < zone["taux_rencontre"]:
            return self.generer_pokemon_sauvage(zone_type)

        return None

    def generer_pokemon_sauvage(self, zone_type):
        #Génère un Pokémon sauvage en fonction de la zone
        if zone_type not in ZONES:
            return None

        zone = ZONES[zone_type]
        pokemon_zone = zone["pokemon"]

        # Déterminer la rareté du Pokémon
        rand = random.random()

        if rand < 0.60 and pokemon_zone["communs"]:
            # 60% communs
            nom = random.choice(pokemon_zone["communs"])
            niveau = random.randint(3, 7)
        elif rand < 0.85 and pokemon_zone["peu_communs"]:
            # 25% peu communs
            nom = random.choice(pokemon_zone["peu_communs"])
            niveau = random.randint(5, 10)
        elif rand < 0.96 and pokemon_zone["rares"]:
            # 11% rares
            nom = random.choice(pokemon_zone["rares"])
            niveau = random.randint(8, 15)
        elif rand < 0.998 and pokemon_zone["tres_rares"]:
            # 3.8% très rares
            nom = random.choice(pokemon_zone["tres_rares"])
            niveau = random.randint(12, 20)
        elif rand <0.999 and pokemon_zone["legendaires"]:
            # 0.2% légendaires
            nom = random.choice(pokemon_zone["legendaires"])
            niveau = random.randint(40, 50)
        else:
            # Fallback sur commun si pas de Pokémon dans cette rareté
            if pokemon_zone["communs"]:
                nom = random.choice(pokemon_zone["communs"])
                niveau = random.randint(3, 7)
            else:
                return None

        # Créer le Pokémon à partir du Pokédex
        if nom in self.pokedex:
            return Pokemon.from_pokedex(self.pokedex[nom], niveau)

        return None

    def get_zone_info(self, zone_type):
        """Retourne les informations d'une zone"""
        if zone_type in ZONES:
            return ZONES[zone_type]
        return None