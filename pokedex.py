import json
import os

class Pokedex:
    def __init__(self, fichier="pokedex.json"):
        self.fichier = fichier
        if not os.path.exists(fichier):
            with open(fichier, "w") as f:
                json.dump([], f)

    def enregistrer(self, pokemon):
        with open(self.fichier, "r") as f:
            data = json.load(f)

        if pokemon.nom not in [p["nom"] for p in data]:
            data.append({
                "nom": pokemon.nom,
                "types": pokemon.types,
                "pv": pokemon.pv_max,
                "attaque": pokemon.attaque,
                "defense": pokemon.defense,
                "image": pokemon.image,
            })

        with open(self.fichier, "w") as f:
            json.dump(data, f, indent=4)
