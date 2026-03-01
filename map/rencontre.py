
import json
import random
from pokemon import Pokemon
from .zones import ZONES

# Rareté

TRANCHES_RARETE = [
    (0.60,  "communs",     -2,  3),   # communs  : niv_moy-2  à niv_moy+3
    (0.85,  "peu_communs",  0,  5),   # peu comm : niv_moy    à niv_moy+5
    (0.96,  "rares",        2,  8),   # rares    : niv_moy+2  à niv_moy+8
    (0.998, "tres_rares",   5, 10),   # très rares : niv_moy+5 à niv_moy+10
    (0.999, "legendaires", 10, 15),   # légendaires : niv_moy+10 à niv_moy+15
]


class RencontreManager:
    def __init__(self, pokedex_file):
        with open(pokedex_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.pokedex = {p["name"]: p for p in data["pokemon"]}


    def verifier_rencontre(self, zone_type, position, equipe_joueur=None):
        #Retourne un Pokémon sauvage adapté au niveau de l'équipe
        zone = ZONES.get(zone_type)
        if zone and random.random() < zone["taux_rencontre"]:
            niv_ref = self._niveau_reference(equipe_joueur)
            return self._generer(zone_type, niv_ref)
        return None

    def _niveau_reference(self, equipe):
        #Calcule le niveau de référence de l'équipe
        if not equipe:
            return 5
        vivants = [p for p in equipe if p.est_vivant()]
        if not vivants:
            return 5
        return max(1, round(sum(p.niveau for p in vivants) / len(vivants)))

    def _generer(self, zone_type, niv_ref):
        pool = ZONES[zone_type]["pokemon"]
        nom, niveau = self._tirer(pool, niv_ref)
        if nom and nom in self.pokedex:
            return Pokemon.from_pokedex(self.pokedex[nom], niveau)
        return None

    def _tirer(self, pool, niv_ref):
        #Tire au sort rareté + Pokémon, avec niveau relatif à niv_ref
        rand = random.random()
        for seuil, cle, off_min, off_max in TRANCHES_RARETE:
            if rand < seuil and pool.get(cle):
                # Niveau entre (niv_ref + off_min) et (niv_ref + off_max)
                niv_min = max(1, niv_ref + off_min)
                niv_max = max(niv_min, min(100, niv_ref + off_max))
                niveau  = random.randint(niv_min, niv_max)
                return random.choice(pool[cle]), niveau

        # Fallback communs
        if pool.get("communs"):
            return random.choice(pool["communs"]), max(1, niv_ref - 1)
        return None, None
