import random
import json
from Logique.Gameplay.General.pokemon_types import type_dict

# Tableau des multiplicateurs de types
MULTIPLICATEURS = type_dict


def multiplicateur_type(type_attaquant, type_defenseur):
    #Retourne le multiplicateur de dégâts en fonction des types
    if type_attaquant in MULTIPLICATEURS:
        return MULTIPLICATEURS[type_attaquant].get(type_defenseur, 1.0)
    return 1.0


class Pokemon:
    def __init__(self, nom, types, pv_max, attaque, defense, niveau=1, legendary=False,):
        self.nom = nom
        self.types = types
        self.pv_max = pv_max
        self.pv = pv_max
        self.attaque = attaque
        self.defense = defense
        self.niveau = niveau
        self.legendary = legendary
        self.experience = 1
        self.experience_max = niveau * 100

    def est_vivant(self):
        return self.pv > 0


    def attaque_speciale(self, adversaire):
        # 50% de réussite
        if random.random() <= 0.5:
            degats = self.attaque * 2  # critique x2
            print("OOOOOH IL A TOUCHE QUEL GOAT !")
            adversaire.subir_degats(degats)
            return True
        else:
            print("MAIS IL EST NUL A CHIER !")
            return False

    def subir_degats(self, degats):
        degats_reels = max(0, degats - self.defense)
        self.pv -= degats_reels
        if self.pv < 0:
            self.pv = 0

    def soigner(self):
        #Restaure tous les PV du Pokémon
        self.pv = self.pv_max

    def gagner_experience(self, exp):
        #Gagne de l'expérience et monte de niveau si nécessaire
        self.experience += exp
        while self.experience >= self.experience_max:
            self.monter_niveau()

    def monter_niveau(self):
        #Monte le Pokémon d'un niveau
        self.niveau += 1
        self.experience -= self.experience_max
        self.experience_max = self.niveau * 100

        # Augmentation des stats
        self.pv_max += random.randint(3, 8)
        self.attaque += random.randint(2, 5)
        self.defense += random.randint(2, 4)
        self.pv = self.pv_max

        return True

    def attaquer(self, defenseur):
        #Attaque un autre Pokémon
        # 10% de chance de rater
        if random.random() < 0.10:
            return {
                "touche": False,
                "degats": 0,
                "critique": False,
                "efficacite": 1.0,
                "message": f"{self.nom} rate son attaque !"
            }

        # Calcul des dégâts de base
        degats_base = self.attaque + random.randint(-5, 5)

        # Critique (10% de chance)
        critique = random.random() < 0.10
        if critique:
            degats_base = int(degats_base * 1.5)

        # Multiplicateur de type
        efficacite = 1.0
        if self.types and defenseur.types:
            efficacite = multiplicateur_type(self.types[0], defenseur.types[0])
            degats_base = int(degats_base * efficacite)

        # Application des dégâts
        degats_reels = defenseur.subir_degats(degats_base)

        # Message d'efficacité
        msg_efficacite = ""
        if efficacite > 1.0:
            msg_efficacite = " Bravo c'est super efficace !"
        elif efficacite < 1.0 and efficacite > 0:
            msg_efficacite = " Ce n'est pas très efficace..."
        elif efficacite == 0:
            msg_efficacite = " MAIS C'EST QUOI "

        msg_critique = " Coup critique !" if critique else ""

        message = f"{self.nom} inflige {degats_reels} dégâts à {defenseur.nom} !{msg_critique}{msg_efficacite}"

        return {
            "touche": True,
            "degats": degats_reels,
            "critique": critique,
            "efficacite": efficacite,
            "message": message
        }

    def to_dict(self):
        """Convertit le Pokémon en dictionnaire pour la sauvegarde"""
        return {
            "nom": self.nom,
            "types": self.types,
            "pv": self.pv,
            "pv_max": self.pv_max,
            "attaque": self.attaque,
            "defense": self.defense,
            "niveau": self.niveau,
            "legendary": self.legendary,
            "experience": self.experience,
            "experience_max": self.experience_max
        }

    @staticmethod
    def from_dict(data):
        #Crée un Pokémon à partir d'un dictionnaire
        pokemon = Pokemon(
            data["nom"],
            data["types"],
            data["pv_max"],
            data["attaque"],
            data["defense"],
            data.get("niveau", 5),
            data.get("legendary", False)
        )
        pokemon.pv = data.get("pv", pokemon.pv_max)
        pokemon.experience = data.get("experience", 0)
        pokemon.experience_max = data.get("experience_max", pokemon.niveau * 100)
        return pokemon

    @staticmethod
    def from_pokedex(pokedex_data, niveau=5):
        """Crée un Pokémon à partir des données du Pokédex"""
        return Pokemon(
            pokedex_data["name"],
            pokedex_data["type"],
            pokedex_data["stats"]["pv"] + (niveau - 1) * 3,
            pokedex_data["stats"]["attaque"] + (niveau - 1) * 2,
            pokedex_data["stats"]["defense"] + (niveau - 1) * 2,
            niveau,
            pokedex_data.get("legendary", False)
        )