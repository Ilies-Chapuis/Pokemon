
import random
from combat import Combat


class CombatChampion:
    #Orchestre un combat complet contre un champion (6 vs 6).

    def __init__(self, pokemon_joueur_actif, equipe_joueur,
                 equipe_champion, champion_data, pokedex=None):
        self.equipe_joueur   = equipe_joueur       # liste complète du joueur
        self.equipe_champion = equipe_champion      # liste de 6 Pokemon
        self.champion_data   = champion_data
        self.pokedex         = pokedex

        self.idx_champion = 0   # index du Pokémon actif du champion
        self.termine      = False
        self.joueur_gagne = False
        self.logs         = []

        # Créer le premier duel
        self.combat_actuel = self._nouveau_duel(pokemon_joueur_actif)

    #  Propriétés utiles
    @property
    def pokemon_champion_actif(self):
        return self.equipe_champion[self.idx_champion]

    @property
    def pokemon_joueur_actif(self):
        return self.combat_actuel.pokemon_joueur

    def get_derniers_logs(self, n=5):
        logs = self.combat_actuel.get_derniers_logs(n)
        return logs if logs else self.logs[-n:]

    #  Création d'un nouveau duel
    def _nouveau_duel(self, pokemon_joueur):
        poke_champ = self.equipe_champion[self.idx_champion]
        # Remettre le Pokémon champion à plein si c'est un nouveau (déjà KO sinon)
        combat = Combat(pokemon_joueur, poke_champ, pokedex=self.pokedex)
        return combat

    #  Tour de combat
    def tour_combat(self, action):
        #Délègue au Combat interne, puis gère les enchaînements.
        if self.termine:
            return

        pv_avant_joueur  = self.combat_actuel.pokemon_joueur.pv
        pv_avant_champion = self.pokemon_champion_actif.pv

        self.combat_actuel.tour_combat(action)

        # Pokémon champion KO → il en envoie un autre
        if not self.pokemon_champion_actif.est_vivant():
            self._champion_suivant()
            return

        # Pokémon joueur KO → le joueur doit choisir (géré dans game.py)
        # On ne fait rien ici, game.py détecte .pokemon_joueur_actif.est_vivant()

    def utiliser_potion(self):
        self.combat_actuel.utiliser_potion()
        if not self.combat_actuel.pokemon_joueur.est_vivant():
            pass  # game.py détecte le KO

    def _champion_suivant(self):
        #Le champion envoie son prochain Pokémon.
        nom_ko = self.equipe_champion[self.idx_champion].nom
        self.logs.append(f"{nom_ko} du Champion est K.O. !")

        # Chercher le prochain Pokémon vivant
        for i in range(self.idx_champion + 1, len(self.equipe_champion)):
            if self.equipe_champion[i].est_vivant():
                self.idx_champion = i
                self.logs.append(
                    f"{self.champion_data['nom']} envoie {self.equipe_champion[i].nom} !")
                # Nouveau duel avec le même Pokémon joueur
                pj = self.combat_actuel.pokemon_joueur
                self.combat_actuel = self._nouveau_duel(pj)
                return

        # Plus de Pokémon vivant → victoire du joueur
        self.termine      = True
        self.joueur_gagne = True
        self.logs.append(f"Tu as vaincu {self.champion_data['nom']} !")

    def changer_pokemon_joueur(self, nouveau_pokemon):
        #Le joueur envoie un remplaçant (après KO ou volontairement).
        poke_champ = self.equipe_champion[self.idx_champion]
        # Remettre les PV du Pokémon champion à ce qu'ils sont
        self.combat_actuel = Combat(nouveau_pokemon, poke_champ, pokedex=self.pokedex)
        self.logs.append(f"Allez {nouveau_pokemon.nom} !")

    def verifier_defaite_joueur(self):
        #Retourne True si toute l'équipe du joueur est KO.
        return all(not p.est_vivant() for p in self.equipe_joueur)
