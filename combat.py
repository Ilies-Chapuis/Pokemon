import random
from pokemon_types import type_dict


# Tableau des multiplicateurs de types (attaquant -> défenseur -> multiplicateur)
MULTIPLICATEURS = type_dict


class Combat:
    def __init__(self, pokemon_joueur, pokemon_sauvage, pokedex=None):
        self.pokemon_joueur  = pokemon_joueur
        self.pokemon_sauvage = pokemon_sauvage
        self.pokedex         = pokedex   # PokedexManager optionnel
        self.tour            = 0
        self.termine         = False
        self.joueur_gagne    = False
        self.pokemon_capture = False
        self.logs            = []

        # Enregistrer automatiquement le Pokémon rencontré dans le Pokédex
        self.enregistrer_dans_pokedex()


    def calculer_degats_avec_type(self, attaquant, defenseur):

        type_atk = attaquant.types[0] if attaquant.types else "Normal"
        type_def = defenseur.types[0] if defenseur.types else "Normal"

        multiplicateur = MULTIPLICATEURS.get(type_atk, {}).get(type_def, 1.0)
        degats_bruts   = int(attaquant.attaque * multiplicateur)

        return degats_bruts, multiplicateur

    def appliquer_degats(self, cible, degats_bruts):

        degats_reels = max(1, degats_bruts - cible.defense)
        cible.pv = max(0, cible.pv - degats_reels)
        return degats_reels

    def get_vainqueur(self):

        if not self.termine:
            return None
        if self.pokemon_capture:
            return self.pokemon_joueur.nom
        return self.pokemon_joueur.nom if self.joueur_gagne else self.pokemon_sauvage.nom

    def get_resultats(self):

        if not self.termine:
            return None

        if self.joueur_gagne or self.pokemon_capture:
            gagnant = self.pokemon_joueur.nom
            perdant = self.pokemon_sauvage.nom
        else:
            gagnant = self.pokemon_sauvage.nom
            perdant = self.pokemon_joueur.nom

        return {"gagnant": gagnant, "perdant": perdant}

    def enregistrer_dans_pokedex(self):

        if self.pokedex is not None:
            self.pokedex.marquer_vu(self.pokemon_sauvage.nom)

    def enregistrer_capture_pokedex(self):

        if self.pokedex is not None:
            self.pokedex.marquer_capture(self.pokemon_sauvage.nom)


    # Logique du combat


    def _attaque_complete(self, attaquant, defenseur):

        # 10% de chance de rater
        if random.random() < 0.10:
            return {"degats": 0, "multiplicateur": 1.0,
                    "message": f"{attaquant.nom} rate son attaque !"}

        critique = random.random() < 0.10
        degats_bruts, multiplicateur = self.calculer_degats_avec_type(attaquant, defenseur)
        if critique:
            degats_bruts = int(degats_bruts * 1.5)

        degats_reels = self.appliquer_degats(defenseur, degats_bruts)

        if multiplicateur > 1.0:
            msg_eff = " C'est super efficace !"
        elif 0 < multiplicateur < 1.0:
            msg_eff = " Ce n'est pas très efficace..."
        elif multiplicateur == 0:
            msg_eff = " Ça n'a aucun effet !"
        else:
            msg_eff = ""

        msg_crit = " Coup critique !" if critique else ""
        message = (f"{attaquant.nom} inflige {degats_reels} dégâts "
                   f"à {defenseur.nom} !{msg_crit}{msg_eff}")

        return {"degats": degats_reels, "multiplicateur": multiplicateur, "message": message}

    def _gain_experience(self):
        exp = self.pokemon_sauvage.niveau * 50
        if self.pokemon_sauvage.legendary:
            exp *= 3
        self.pokemon_joueur.gagner_experience(exp)
        self.logs.append(f"{self.pokemon_joueur.nom} gagne {exp} points d'expérience !")

    def _ko_sauvage(self):
        self.logs.append(f"{self.pokemon_sauvage.nom} est K.O. !")
        self.termine      = True
        self.joueur_gagne = True
        self._gain_experience()

    def _ko_joueur(self):
        self.logs.append(f"{self.pokemon_joueur.nom} est K.O. !")
        self.termine      = True
        self.joueur_gagne = False


    def tour_combat(self, action_joueur="attaque"):
        #Exécute un tour de combat.
        if self.termine:
            return

        self.tour += 1
        self.logs.append(f"--- Tour {self.tour} ---")

        if action_joueur == "fuite":
            self._gerer_fuite()
        elif action_joueur == "capture":
            self._gerer_capture()
        elif action_joueur == "attaque_speciale":
            self._gerer_attaque_speciale()
        else:
            self._gerer_attaque_normale()

    def _gerer_fuite(self):
        if random.random() < 0.5:
            self.logs.append("Vous avez réussi à fuir !")
            self.termine = True
        else:
            self.logs.append("Impossible de fuir !")
            res = self._attaque_complete(self.pokemon_sauvage, self.pokemon_joueur)
            self.logs.append(res["message"])
            if not self.pokemon_joueur.est_vivant():
                self._ko_joueur()

    def _gerer_capture(self):
        if self.tenter_capture():
            self.logs.append(f"Vous avez capturé {self.pokemon_sauvage.nom} !")
            self.termine         = True
            self.joueur_gagne    = True
            self.pokemon_capture = True
            self.enregistrer_capture_pokedex()
        else:
            self.logs.append("NUL GERMAIN NUL !")
            res = self._attaque_complete(self.pokemon_sauvage, self.pokemon_joueur)
            self.logs.append(res["message"])
            if not self.pokemon_joueur.est_vivant():
                self._ko_joueur()

    def _gerer_attaque_speciale(self):
        if random.random() < 0.33:
            degats_bruts, _ = self.calculer_degats_avec_type(
                self.pokemon_joueur, self.pokemon_sauvage)
            degats_bruts = int(degats_bruts * 1.5)
            degats_reels = self.appliquer_degats(self.pokemon_sauvage, degats_bruts)
            self.logs.append(f"ATTAQUE SPÉCIALE CRITIQUE ! {degats_reels} dégâts !")
            if not self.pokemon_sauvage.est_vivant():
                self._ko_sauvage()
                return
        else:
            self.logs.append("L'attaque spéciale a échoué ce pokemon est nul comme les dev !")

        res = self._attaque_complete(self.pokemon_sauvage, self.pokemon_joueur)
        self.logs.append(res["message"])
        if not self.pokemon_joueur.est_vivant():
            self._ko_joueur()

    def _gerer_attaque_normale(self):
        joueur_premier = self.pokemon_joueur.attaque >= self.pokemon_sauvage.attaque

        if joueur_premier:
            res = self._attaque_complete(self.pokemon_joueur, self.pokemon_sauvage)
            self.logs.append(res["message"])
            if not self.pokemon_sauvage.est_vivant():
                self._ko_sauvage(); return
            res = self._attaque_complete(self.pokemon_sauvage, self.pokemon_joueur)
            self.logs.append(res["message"])
            if not self.pokemon_joueur.est_vivant():
                self._ko_joueur()
        else:
            res = self._attaque_complete(self.pokemon_sauvage, self.pokemon_joueur)
            self.logs.append(res["message"])
            if not self.pokemon_joueur.est_vivant():
                self._ko_joueur(); return
            res = self._attaque_complete(self.pokemon_joueur, self.pokemon_sauvage)
            self.logs.append(res["message"])
            if not self.pokemon_sauvage.est_vivant():
                self._ko_sauvage()



    def tenter_capture(self):
        #Taux de capture basé sur les PV restants du Pokémon sauvage.
        ratio_pv = self.pokemon_sauvage.pv / self.pokemon_sauvage.pv_max
        if ratio_pv < 0.25:
            taux = 90
        elif ratio_pv < 0.5:
            taux = 70
        else:
            taux = 50
        if self.pokemon_sauvage.legendary:
            taux = max(5, taux // 3)
        return random.randint(1, 100) <= taux

    def utiliser_potion(self):
        #Soigne 50 PV, le Pokémon sauvage riposte pendant ce temps.
        soin = min(50, self.pokemon_joueur.pv_max - self.pokemon_joueur.pv)
        self.pokemon_joueur.pv += soin
        self.logs.append(f"{self.pokemon_joueur.nom} récupère {soin} PV !")
        res = self._attaque_complete(self.pokemon_sauvage, self.pokemon_joueur)
        self.logs.append(res["message"])
        if not self.pokemon_joueur.est_vivant():
            self._ko_joueur()

    def get_derniers_logs(self, n=5):
        #Retourne les n derniers messages du log de combat.
        return self.logs[-n:]
