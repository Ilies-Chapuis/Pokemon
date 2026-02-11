import random


class Combat:
    def __init__(self, pokemon_joueur, pokemon_sauvage):
        self.pokemon_joueur = pokemon_joueur
        self.pokemon_sauvage = pokemon_sauvage
        self.tour = 0
        self.termine = False
        self.joueur_gagne = False
        self.logs = []

    def tour_combat(self, action_joueur="attaque"):
        #Execute un tour de combat
        if self.termine:
            return

        self.tour += 1
        self.logs.append(f"--- Tour {self.tour} ---")

        # Le Pokémon le plus rapide attaque en premier
        # Pour simplifier, on utilise l'attaque comme stat de vitesse
        joueur_premier = self.pokemon_joueur.attaque >= self.pokemon_sauvage.attaque

        if action_joueur == "fuite":
            # 50% de chance de fuir contre un Pokémon sauvage
            if random.random() < 0.5:
                self.logs.append("Vous avez réussi à fuir !")
                self.termine = True
                return
            else:
                self.logs.append("Impossible de fuir !")
                # Le Pokémon sauvage attaque
                resultat = self.pokemon_sauvage.attaquer(self.pokemon_joueur)
                self.logs.append(resultat["message"])
                if not self.pokemon_joueur.est_vivant():
                    self.logs.append(f"{self.pokemon_joueur.nom} est K.O. !")
                    self.termine = True
                    self.joueur_gagne = False
                return

        # Action du joueur
        if joueur_premier:
            # Le joueur attaque en premier
            resultat = self.pokemon_joueur.attaquer(self.pokemon_sauvage)
            self.logs.append(resultat["message"])

            if not self.pokemon_sauvage.est_vivant():
                self.logs.append(f"{self.pokemon_sauvage.nom} est K.O. !")
                self.termine = True
                self.joueur_gagne = True

                # Gain d'expérience
                exp_gagnee = self.pokemon_sauvage.niveau * 50
                if self.pokemon_sauvage.legendary:
                    exp_gagnee *= 3
                self.pokemon_joueur.gagner_experience(exp_gagnee)
                self.logs.append(f"{self.pokemon_joueur.nom} gagne {exp_gagnee} points d'expérience !")
                return

            # Le Pokémon sauvage riposte
            resultat = self.pokemon_sauvage.attaquer(self.pokemon_joueur)
            self.logs.append(resultat["message"])

            if not self.pokemon_joueur.est_vivant():
                self.logs.append(f"{self.pokemon_joueur.nom} est K.O. !")
                self.termine = True
                self.joueur_gagne = False
        else:
            # Le Pokémon sauvage attaque en premier
            resultat = self.pokemon_sauvage.attaquer(self.pokemon_joueur)
            self.logs.append(resultat["message"])

            if not self.pokemon_joueur.est_vivant():
                self.logs.append(f"{self.pokemon_joueur.nom} est K.O. !")
                self.termine = True
                self.joueur_gagne = False
                return

            # Le joueur riposte
            resultat = self.pokemon_joueur.attaquer(self.pokemon_sauvage)
            self.logs.append(resultat["message"])

            if not self.pokemon_sauvage.est_vivant():
                self.logs.append(f"{self.pokemon_sauvage.nom} est K.O. !")
                self.termine = True
                self.joueur_gagne = True

                # Gain d'expérience
                exp_gagnee = self.pokemon_sauvage.niveau * 50
                if self.pokemon_sauvage.legendary:
                    exp_gagnee *= 3
                self.pokemon_joueur.gagner_experience(exp_gagnee)
                self.logs.append(f"{self.pokemon_joueur.nom} gagne {exp_gagnee} points d'expérience !")

    def utiliser_potion(self):
        """Utilise une potion pour soigner le Pokémon"""
        soin = min(50, self.pokemon_joueur.pv_max - self.pokemon_joueur.pv)
        self.pokemon_joueur.pv += soin
        self.logs.append(f"{self.pokemon_joueur.nom} récupère {soin} PV !")

        # Le Pokémon sauvage attaque pendant ce temps
        resultat = self.pokemon_sauvage.attaquer(self.pokemon_joueur)
        self.logs.append(resultat["message"])

        if not self.pokemon_joueur.est_vivant():
            self.logs.append(f"{self.pokemon_joueur.nom} est K.O. !")
            self.termine = True
            self.joueur_gagne = False

    def get_derniers_logs(self, n=5):
        """Retourne les n derniers logs"""
        return self.logs[-n:]
