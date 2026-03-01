
import json
import os
import pygame

from pokemon import Pokemon
from combat import Combat
from map import Carte, RencontreManager, ZONES
from save_manager import SaveManager
from Pokedex_manager import PokedexManager
from Evolution import peut_evoluer, peut_forme_ultime, appliquer_forme_ultime

from renderers import RendererUI, RendererExploration, RendererCombat, RendererChampion
from menus import MenuEquipe, MenuReserve, MenuPokedex, MenuEvolution
from champions import (CHAMPIONS, champion_a_proximite, creer_equipe_champion,
                       POSITION_CHAMPION_PLANTE, POSITION_CHAMPION_FEU)
from combat_champion import CombatChampion




def _chemin_json():
    import os
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "Data", "pokemon.json")


class Game:

    def __init__(self):
        self.largeur_ecran = 1000
        self.hauteur_ecran = 700
        self.screen = pygame.display.get_surface()

        fonts = {
            "titre":  pygame.font.SysFont("Arial", 32, bold=True),
            "normal": pygame.font.SysFont("Arial", 20),
            "petit":  pygame.font.SysFont("Arial", 16),
        }
        self.font_titre  = fonts["titre"]
        self.font_normal = fonts["normal"]
        self.font_petit  = fonts["petit"]

        self._init_carte()
        self._init_joueur()
        self._init_combat()
        self._init_inventaire()
        self._init_renderers(fonts)

        self.save_manager = SaveManager()
        self.pokedex      = PokedexManager()

        # États d'évolution
        self.evolution_en_cours = None
        self.pokemon_a_evoluer  = None

    def _init_carte(self):
        # Chercher pokemon.json dans le dossier du projet
        chemin_json = _chemin_json()
        self.carte             = Carte(20, 15)
        self.rencontre_manager = RencontreManager(chemin_json)
        self.taille_case       = 40
        self.joueur_x          = 10
        self.joueur_y          = 7

    def _init_joueur(self):
        self.equipe_joueur   = []
        self.reserve_pokemon = []
        self.selection_equipe  = 0
        self.selection_reserve = 0
        self.selection_pokedex = 0
        self.mode_reserve      = "equipe"
        self.etat              = "exploration"
        self._init_equipe_depart()

    def _init_equipe_depart(self):
        starter = self.rencontre_manager.pokedex.get("Keunotor")
        if starter:
            self.equipe_joueur.append(Pokemon.from_pokedex(starter, 5))

    def _init_combat(self):
        self.combat_actuel    = None
        self.pokemon_sauvage  = None
        self.pas_depuis_combat    = 0
        self.pas_min_entre_combats = 5
        self.etat_ko     = False   # True quand le pokémon actif est KO en combat
        self.selection_ko = 0      # index dans la liste des remplaçants
        self.etat_forme_ultime   = False
        self.pokemon_forme_ultime = None
        # Champions
        self.champions_battus    = set()   # ids des champions vaincus
        self.badges              = []       # badges obtenus
        self.champion_actif_id   = None    # champion en cours de dialogue/combat
        self.dialogue_ligne      = 0       # ligne de dialogue courante
        self.dialogue_phase      = None    # "approche"|"avant_combat"|"victoire"|"defaite"
        self.combat_champion     = None    # CombatChampion en cours
        self.etat_ko_champion    = False   # KO pendant combat champion
        self.selection_ko_champ  = 0

    def _init_inventaire(self):
        self.potions      = 5
        self.pokeballs    = 10
        self.pokeballs_max = 20

    def _init_renderers(self, fonts):
        self.images_cache    = {}
        self.ui              = RendererUI(self.screen, fonts)
        self.arena_background = self.ui.charger_arena(self.largeur_ecran, self.hauteur_ecran)
        self.r_exploration   = RendererExploration(self.screen, self.ui, self.taille_case)
        self.r_combat        = RendererCombat(self.screen, self.ui, self.images_cache, self.arena_background)
        self.r_champion      = RendererChampion(self.screen, self.ui)
        self.m_equipe        = MenuEquipe(self.screen, self.ui)
        self.m_reserve       = MenuReserve(self.screen, self.ui)
        self.m_pokedex       = MenuPokedex(self.screen, self.ui)
        self.m_evolution     = MenuEvolution(self.screen, self.ui)

    # ------------------------------------------------------------------ #
    # RENDU
    # ------------------------------------------------------------------ #
    def render(self):
        self.screen.fill((20, 20, 40))
        dispatch = {
            "exploration":       self._render_exploration,
            "combat":            self._render_combat,
            "menu_equipe":       self._render_equipe,
            "menu_reserve":      self._render_reserve,
            "pokedex":           self._render_pokedex,
            "evolution":         self._render_evolution,
            "forme_ultime":      self._render_forme_ultime,
            "dialogue_champion": self._render_dialogue_champion,
            "combat_champion":   self._render_combat_champion,
        }
        dispatch.get(self.etat, lambda: None)()

    def _render_exploration(self):
        self.r_exploration.render(self)

    def _render_combat(self):
        self.r_combat.render(self)

    def _render_equipe(self):
        self.m_equipe.afficher(self.equipe_joueur, self.selection_equipe)

    def _render_reserve(self):
        self.m_reserve.afficher(self.equipe_joueur, self.reserve_pokemon,
                                self.selection_equipe, self.selection_reserve,
                                self.mode_reserve)

    def _render_pokedex(self):
        with open(_chemin_json(), "r", encoding="utf-8") as f:
            all_pokemon = json.load(f)["pokemon"]
        self.m_pokedex.afficher(self.pokedex, self.selection_pokedex, all_pokemon)

    def _render_evolution(self):
        self.m_evolution.afficher(self.pokemon_a_evoluer, self.evolution_en_cours)

    # ------------------------------------------------------------------ #
    # DÉPLACEMENT & COMBATS
    # ------------------------------------------------------------------ #
    def deplacer_joueur(self, dx, dy):
        nx, ny = self.joueur_x + dx, self.joueur_y + dy
        if not (0 <= nx < self.carte.largeur and 0 <= ny < self.carte.hauteur):
            return
        self.joueur_x, self.joueur_y = nx, ny
        self.pas_depuis_combat += 1
        if self.pas_depuis_combat >= self.pas_min_entre_combats:
            self._verifier_rencontre()
        self._verifier_champion_proximite()

    def _verifier_rencontre(self):
        zone = self.carte.get_zone(self.joueur_x, self.joueur_y)
        poke = self.rencontre_manager.verifier_rencontre(zone, (self.joueur_x, self.joueur_y), self.equipe_joueur)
        if poke and self.equipe_joueur:
            self._demarrer_combat(poke)
            self.pas_depuis_combat = 0

    def _demarrer_combat(self, pokemon_sauvage):
        self.etat = "combat"
        self.pokemon_sauvage = pokemon_sauvage
        actif = self._get_pokemon_actif()
        if actif:
            # Combat reçoit le pokedex : il gère lui-même marquer_vu et marquer_capture
            self.combat_actuel = Combat(actif, pokemon_sauvage, pokedex=self.pokedex)

    def _get_pokemon_actif(self):
        return next((p for p in self.equipe_joueur if p.est_vivant()), None)

    # ------------------------------------------------------------------ #
    # INPUTS — EXPLORATION
    # ------------------------------------------------------------------ #
    TOUCHES_DEPLACEMENT = {
        pygame.K_UP: (0, -1), pygame.K_z: (0, -1),
        pygame.K_DOWN: (0, 1), pygame.K_s: (0, 1),
        pygame.K_LEFT: (-1, 0), pygame.K_q: (-1, 0),
        pygame.K_RIGHT: (1, 0), pygame.K_d: (1, 0),
    }

    def gerer_input_exploration(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key in self.TOUCHES_DEPLACEMENT:
            self.deplacer_joueur(*self.TOUCHES_DEPLACEMENT[event.key])
        elif event.key == pygame.K_h:
            for p in self.equipe_joueur:
                p.soigner()
            print("✓ Équipe soignée !")
        elif event.key == pygame.K_e:
            self.etat = "menu_equipe"
            self.selection_equipe = 0
        elif event.key == pygame.K_r:
            zone = self.carte.get_zone(self.joueur_x, self.joueur_y)
            if zone == "ville":
                self.etat = "menu_reserve"
                self.mode_reserve = "equipe"
                self.selection_reserve = self.selection_equipe = 0
            else:
                print("Bah les pokemons réserves ils sont où ? EN VILLE")
        elif event.key == pygame.K_t:
            self._recharger_pokeballs()
        elif event.key == pygame.K_g:
            if self.sauvegarder_partie():
                print("💾 Partie sauvegardée !")
        elif event.key == pygame.K_p:
            self.etat = "pokedex"
            self.selection_pokedex = 0

    # INPUTS — COMBAT
    def gerer_input_combat(self, event):

        if self.etat_ko:
            if event.type == pygame.KEYDOWN:
                self._gerer_input_ko(event.key)
            return

        if self.combat_actuel.termine:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self._fin_combat()
            return

        # Clavier
        if event.type == pygame.KEYDOWN:
            self._action_combat(event.key)

        # Clic souris
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            action = self.r_combat.get_action_clic(event.pos)
            if action:
                self._action_combat_id(action)

    def _action_combat_id(self, action_id):
        #Traduit un id de bouton en touche clavier puis délègue
        mapping = {
            "attaque":  pygame.K_a,
            "special":  pygame.K_s,
            "potion":   pygame.K_p,
            "capturer": pygame.K_c,
            "changer":  pygame.K_x,
            "fuir":     pygame.K_f,
        }
        key = mapping.get(action_id)
        if key:
            self._action_combat(key)

    def _action_combat(self, key):
        c = self.combat_actuel
        pv_avant_sauvage = c.pokemon_sauvage.pv
        pv_avant_joueur  = c.pokemon_joueur.pv

        if key == pygame.K_a:
            c.tour_combat("attaque")
        elif key == pygame.K_s:
            c.tour_combat("attaque_speciale")
        elif key == pygame.K_p and self.potions > 0:
            c.utiliser_potion()
            self.potions -= 1
        elif key == pygame.K_c and self.pokeballs > 0:
            c.tour_combat("capture")
            self.pokeballs -= 1
            if c.pokemon_capture:
                self.r_combat.declencher_animation("capture", "sauvage")
        elif key == pygame.K_x:
            self.etat = "menu_equipe"
            self.selection_equipe = 0
        elif key == pygame.K_f:
            c.tour_combat("fuite")

        # Animations selon résultat
        if c.pokemon_sauvage.pv < pv_avant_sauvage:
            if not c.pokemon_sauvage.est_vivant():
                self.r_combat.declencher_animation("ko", "sauvage")
            else:
                self.r_combat.declencher_animation("attaque", "sauvage")

        if c.pokemon_joueur.pv < pv_avant_joueur:
            if not c.pokemon_joueur.est_vivant():
                self.r_combat.declencher_animation("ko", "joueur")
                self._gerer_ko_joueur()
            else:
                self.r_combat.declencher_animation("attaque", "joueur")

        self._verifier_evolution_combat()

    def _gerer_ko_joueur(self):
        #Appelé quand le Pokémon actif vient d'être mis KO
        vivants = [p for i, p in enumerate(self.equipe_joueur)
                   if p.est_vivant() and i != 0]
        if vivants:
            # Annuler le termine mis par combat._ko_joueur, on gère nous-mêmes
            self.combat_actuel.termine      = False
            self.combat_actuel.joueur_gagne = False
            self.etat_ko      = True
            self.selection_ko = 0


    def _gerer_input_ko(self, key):
        #Gère la navigation et la sélection du remplaçant
        vivants = [(i, p) for i, p in enumerate(self.equipe_joueur)
                   if p.est_vivant() and i != 0]

        if key == pygame.K_UP:
            self.selection_ko = max(0, self.selection_ko - 1)
        elif key == pygame.K_DOWN:
            self.selection_ko = min(len(vivants) - 1, self.selection_ko + 1)
        elif key == pygame.K_RETURN and vivants:
            idx_reel, pokemon_choisi = vivants[self.selection_ko]
            # Mettre le remplaçant en position 0
            self.equipe_joueur[0], self.equipe_joueur[idx_reel] = (
                self.equipe_joueur[idx_reel], self.equipe_joueur[0])
            # Mettre à jour le combat
            self.combat_actuel.pokemon_joueur = self.equipe_joueur[0]
            self.combat_actuel.logs.append(
                f"Allez {self.equipe_joueur[0].nom} !")
            self.etat_ko      = False
            self.selection_ko = 0
        elif key == pygame.K_SPACE and not vivants:
            # Aucun remplaçant → confirmer défaite
            self.combat_actuel.termine      = True
            self.combat_actuel.joueur_gagne = False
            self.etat_ko = False

    def _appliquer_forme_ultime_joueur(self):
        #Applique la Forme Ultime au pokemon_forme_ultime
        poke = self.pokemon_forme_ultime
        if not poke:
            return
        try:
            with open(_chemin_json(), "r", encoding="utf-8") as f:
                data = json.load(f)
            # Chercher par le nom de base (sans le suffixe ★)
            nom_base = poke.nom.replace(" ★", "").strip()
            pokedex_data = next(
                (p for p in data["pokemon"] if p["name"] == nom_base), None)
            if pokedex_data:
                appliquer_forme_ultime(poke, pokedex_data)
        except Exception as e:
            print(f"Erreur Forme Ultime : {e}")
        finally:
            self.pokemon_forme_ultime = None
            self.etat_forme_ultime    = False
            self.etat = "menu_equipe"

    def _fin_combat(self):
        if self.combat_actuel.pokemon_capture:
            # Pokédex déjà mis à jour par Combat.enregistrer_capture_pokedex()
            if len(self.equipe_joueur) < 6:
                self.equipe_joueur.append(self.pokemon_sauvage)
                print(f"✓ {self.pokemon_sauvage.nom} ajouté à l'équipe !")
            else:
                self.reserve_pokemon.append(self.pokemon_sauvage)
                print(f"✓ {self.pokemon_sauvage.nom} envoyé à la réserve !")
        self.etat     = "exploration"
        self.etat_ko  = False
        self.combat_actuel   = None
        self.pokemon_sauvage = None

    def gerer_input_forme_ultime(self, event):
        #Écran de confirmation Forme Ultime
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_o:
            self._appliquer_forme_ultime_joueur()
        elif event.key in (pygame.K_n, pygame.K_ESCAPE):
            self.pokemon_forme_ultime = None
            self.etat_forme_ultime    = False
            self.etat = "menu_equipe"

    def _render_dialogue_champion(self):
        if not self.champion_actif_id:
            return
        data   = CHAMPIONS[self.champion_actif_id]
        lignes = data["dialogues"][self.dialogue_phase]
        self.r_champion.afficher_dialogue(
            data, lignes, self.dialogue_ligne, self.badges)

    def _render_combat_champion(self):
        if not self.combat_champion:
            return
        cc = self.combat_champion
        # Réutilise le renderer de combat normal pour le duel actif
        # Crée un objet proxy avec les attributs attendus par renderer_combat
        class _Proxy:
            pass
        proxy = _Proxy()
        proxy.combat_actuel  = cc.combat_actuel
        proxy.pokemon_sauvage = cc.pokemon_champion_actif
        proxy.potions        = self.potions
        proxy.pokeballs      = 0   # pas de capture contre champion
        proxy.equipe_joueur  = self.equipe_joueur
        proxy.etat_ko        = self.etat_ko_champion
        proxy.selection_ko   = self.selection_ko_champ

        self.r_combat.render(proxy)
        # Bandeau champion par-dessus
        self.r_champion.afficher_bandeau_combat(
            CHAMPIONS[self.champion_actif_id],
            cc.equipe_champion,
            cc.idx_champion)
        # Fin du combat champion
        if cc.termine:
            recomp = []
            if cc.joueur_gagne:
                r = CHAMPIONS[self.champion_actif_id]["recompense"]
                if r.get("badge"):
                    recomp.append(f"✦ {r['badge']} obtenu !")
                if r.get("potions"):
                    recomp.append(f"+{r['potions']} Potions")
                if r.get("pokeballs"):
                    recomp.append(f"+{r['pokeballs']} Pokéballs")
            self.r_champion.afficher_fin_combat(
                CHAMPIONS[self.champion_actif_id],
                cc.joueur_gagne, recomp)

    def _render_forme_ultime(self):
        #Affiche l'écran de confirmation Forme Ultime
        from Evolution import NIVEAU_FORME_ULTIME, BONUS_FORME_ULTIME
        poke = self.pokemon_forme_ultime
        if not poke:
            return
        self.screen.fill((10, 10, 30))
        W, H = self.screen.get_size()
        # Titre
        t = self.font_titre.render("✦ FORME ULTIME ✦", True, (255, 215, 0))
        self.screen.blit(t, t.get_rect(center=(W//2, 100)))
        # Description
        lignes = [
            f"{poke.nom} a atteint le niveau {poke.niveau} !",
            "",
            "Il peut accéder à sa FORME ULTIME :",
            f"  → Revient au niveau 5",
            f"  → Stats de base × {BONUS_FORME_ULTIME}  (+{int((BONUS_FORME_ULTIME-1)*100)}%)",
            f"  → Nom : {poke.nom} ★",
            "",
            "Cette transformation est IRRÉVERSIBLE.",
            "",
            "[O] Oui, transformer !        [N] Non, pas maintenant",
        ]
        couleurs = {0: (255,255,100), 3:(100,255,150), 4:(100,255,150),
                    5:(255,200,100), 7:(255,100,100), 9:(200,200,200)}
        for i, ligne in enumerate(lignes):
            c = couleurs.get(i, (220,220,220))
            surf = self.font_normal.render(ligne, True, c)
            self.screen.blit(surf, surf.get_rect(center=(W//2, 200 + i*38)))

    # CHAMPIONS D'ARÈNE

    def _verifier_champion_proximite(self):
        #Déclenche le dialogue si le joueur est proche d'un champion.
        if self.etat != "exploration":
            return
        cid = champion_a_proximite(self.joueur_x, self.joueur_y, self.champions_battus)
        if cid and self.champion_actif_id is None:
            self._demarrer_dialogue_champion(cid)

    def _demarrer_dialogue_champion(self, champion_id):
        self.champion_actif_id = champion_id
        if champion_id in self.champions_battus:
            self.dialogue_phase = "deja_battu"
        else:
            self.dialogue_phase = "approche"
        self.dialogue_ligne = 0
        self.etat = "dialogue_champion"

    def gerer_input_dialogue_champion(self, event):
        if event.type != pygame.KEYDOWN:
            return
        data = CHAMPIONS[self.champion_actif_id]
        lignes = data["dialogues"][self.dialogue_phase]

        if event.key == pygame.K_ESCAPE:
            # Annuler / fermer
            self.etat = "exploration"
            self.champion_actif_id = None
            return

        if event.key == pygame.K_RETURN:
            # Avancer dans le dialogue
            if self.dialogue_ligne < len(lignes) - 1:
                self.dialogue_ligne += 1
            else:
                # Fin du dialogue selon la phase
                if self.dialogue_phase == "approche":
                    # Dernière ligne = choix combat → ENTRÉE lance le combat
                    self._lancer_combat_champion(self.champion_actif_id)
                elif self.dialogue_phase in ("deja_battu", "victoire_champion"):
                    self.etat = "exploration"
                    self.champion_actif_id = None
                elif self.dialogue_phase == "avant_combat":
                    self.etat = "combat_champion"
                elif self.dialogue_phase in ("defaite_champion",):
                    # Donner les récompenses puis fermer
                    self._donner_recompenses_champion(self.champion_actif_id)
                    self.etat = "exploration"
                    self.champion_actif_id = None

    def _lancer_combat_champion(self, champion_id):
        equipe_champ = creer_equipe_champion(champion_id)
        actif = self._get_pokemon_actif()
        if not actif:
            return
        self.combat_champion = CombatChampion(
            actif, self.equipe_joueur, equipe_champ,
            CHAMPIONS[champion_id], pokedex=self.pokedex)
        # Petit dialogue avant combat
        self.dialogue_phase = "avant_combat"
        self.dialogue_ligne = 0
        self.etat = "dialogue_champion"

    def _donner_recompenses_champion(self, champion_id):
        data = CHAMPIONS[champion_id]
        recomp = data["recompense"]
        if recomp.get("badge") and recomp["badge"] not in self.badges:
            self.badges.append(recomp["badge"])
        self.potions   += recomp.get("potions", 0)
        self.pokeballs += recomp.get("pokeballs", 0)
        self.champions_battus.add(champion_id)

    def gerer_input_combat_champion(self, event):
        #Gère les inputs pendant le combat champion.
        if not self.combat_champion:
            return
        cc = self.combat_champion

        # Fin du combat (prioritaire, même si etat_ko_champion est True)
        if cc.termine:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self._fin_combat_champion()
            return

        # KO du joueur → choisir remplaçant
        if self.etat_ko_champion:
            if event.type == pygame.KEYDOWN:
                self._gerer_ko_champion(event.key)
            return

        if event.type == pygame.KEYDOWN:
            self._action_combat_champion(event.key)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            action = self.r_combat.get_action_clic(event.pos)
            if action and action not in ("capturer",):  # pas de capture
                self._action_combat_champion_id(action)

    def _action_combat_champion(self, key):
        cc = self.combat_champion
        pv_avant = cc.pokemon_joueur_actif.pv

        if key == pygame.K_a:
            cc.tour_combat("attaque")
        elif key == pygame.K_s:
            cc.tour_combat("attaque_speciale")
        elif key == pygame.K_p and self.potions > 0:
            cc.utiliser_potion()
            self.potions -= 1
        elif key == pygame.K_f:
            cc.tour_combat("fuite")
        elif key == pygame.K_x:
            self.etat = "menu_equipe"
            self.selection_equipe = 0
            return

        # Animations
        if cc.pokemon_joueur_actif.pv < pv_avant:
            if not cc.pokemon_joueur_actif.est_vivant():
                self.r_combat.declencher_animation("ko", "joueur")
                vivants = [p for p in self.equipe_joueur if p.est_vivant()]
                if vivants:
                    # Annuler le termine éventuel, on va choisir un remplaçant
                    cc.combat_actuel.termine = False
                    self.etat_ko_champion   = True
                    self.selection_ko_champ = 0
                else:
                    # Toute l'équipe KO → défaite immédiate
                    cc.termine      = True
                    cc.joueur_gagne = False
                    self.etat_ko_champion = False
            else:
                self.r_combat.declencher_animation("attaque", "joueur")

        poke_champ = cc.pokemon_champion_actif
        if not poke_champ.est_vivant():
            self.r_combat.declencher_animation("ko", "sauvage")

    def _action_combat_champion_id(self, action_id):
        mapping = {"attaque": pygame.K_a, "special": pygame.K_s,
                   "potion": pygame.K_p, "fuir": pygame.K_f, "changer": pygame.K_x}
        key = mapping.get(action_id)
        if key:
            self._action_combat_champion(key)

    def _gerer_ko_champion(self, key):
        vivants = [(i, p) for i, p in enumerate(self.equipe_joueur) if p.est_vivant()]
        if key == pygame.K_UP:
            self.selection_ko_champ = max(0, self.selection_ko_champ - 1)
        elif key == pygame.K_DOWN:
            self.selection_ko_champ = min(len(vivants)-1, self.selection_ko_champ)
        elif key == pygame.K_RETURN and vivants:
            _, poke = vivants[self.selection_ko_champ]
            self.combat_champion.changer_pokemon_joueur(poke)
            self.etat_ko_champion   = False
            self.selection_ko_champ = 0

    def _fin_combat_champion(self):
        cc = self.combat_champion
        cid = self.champion_actif_id
        data = CHAMPIONS[cid]
        if cc.joueur_gagne:
            self.dialogue_phase = "defaite_champion"
        else:
            self.dialogue_phase = "victoire_champion"
        self.dialogue_ligne  = 0
        self.combat_champion = None
        self.etat_ko_champion = False
        self.etat = "dialogue_champion"

    def _verifier_evolution_combat(self):
        #Vérifie si le Pokémon actif peut évoluer après gain d'XP
        actif = self._get_pokemon_actif()
        if not actif:
            return
        # Évolution classique (prioritaire)
        peut, nom_evo, _ = peut_evoluer(actif.nom, actif.niveau)
        if peut and nom_evo:
            self.evolution_en_cours = nom_evo
            self.pokemon_a_evoluer  = actif
            self.etat = "evolution"
            return
        # Forme Ultime proposée hors combat (via menu équipe, touche U)
        if peut_forme_ultime(actif):
            self.pokemon_forme_ultime = actif

    # INPUTS — MENU ÉQUIPE
    def gerer_input_menu_equipe(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_UP:
            self.selection_equipe = (self.selection_equipe - 1) % len(self.equipe_joueur)
        elif event.key == pygame.K_DOWN:
            self.selection_equipe = (self.selection_equipe + 1) % len(self.equipe_joueur)
        elif event.key == pygame.K_RETURN:
            self._changer_pokemon_actif()
        elif event.key == pygame.K_u:
            # Proposer la Forme Ultime pour le Pokémon sélectionné
            poke = self.equipe_joueur[self.selection_equipe]
            if peut_forme_ultime(poke):
                self.pokemon_forme_ultime = poke
                self.etat_forme_ultime    = True
                self.etat = "forme_ultime"
        elif event.key == pygame.K_ESCAPE:
            self.etat = "combat" if self.combat_actuel else "exploration"

    def _changer_pokemon_actif(self):
        sel = self.selection_equipe
        if not self.equipe_joueur[sel].est_vivant():
            print("⚠ Ce Pokémon est K.O. !")
            return
        self.equipe_joueur[0], self.equipe_joueur[sel] = \
            self.equipe_joueur[sel], self.equipe_joueur[0]
        self.selection_equipe = 0
        print(f"✓ {self.equipe_joueur[0].nom} est maintenant actif !")
        if self.combat_actuel:
            self._riposte_sauvage_pendant_changement()
            self.etat = "combat"
        else:
            self.etat = "exploration"

    def _riposte_sauvage_pendant_changement(self):
        self.combat_actuel.pokemon_joueur = self.equipe_joueur[0]
        self.combat_actuel.logs.append(f"Vous envoyez {self.equipe_joueur[0].nom} !")
        if not self.combat_actuel.termine:
            res = self.combat_actuel.pokemon_sauvage.attaquer(self.combat_actuel.pokemon_joueur)
            self.combat_actuel.logs.append(res["message"])
            if not self.combat_actuel.pokemon_joueur.est_vivant():
                self.combat_actuel.logs.append(f"{self.combat_actuel.pokemon_joueur.nom} est K.O. !")
                if not any(p.est_vivant() for p in self.equipe_joueur):
                    self.combat_actuel.termine = True
                    self.combat_actuel.joueur_gagne = False

    # INPUTS — MENU RÉSERVE
    def gerer_input_menu_reserve(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_TAB:
            self.mode_reserve = "reserve" if self.mode_reserve == "equipe" else "equipe"
            self.selection_reserve = self.selection_equipe = 0
        elif event.key == pygame.K_UP:
            self._naviguer_reserve(-1)
        elif event.key == pygame.K_DOWN:
            self._naviguer_reserve(1)
        elif event.key == pygame.K_RETURN:
            self._echanger_equipe_reserve()
        elif event.key == pygame.K_ESCAPE:
            self.etat = "exploration"

    def _naviguer_reserve(self, direction):
        if self.mode_reserve == "equipe":
            self.selection_equipe = max(0, min(len(self.equipe_joueur) - 1,
                                               self.selection_equipe + direction))
        else:
            self.selection_reserve = max(0, min(len(self.reserve_pokemon) - 1,
                                                self.selection_reserve + direction))

    def _echanger_equipe_reserve(self):
        if self.mode_reserve == "equipe":
            if len(self.equipe_joueur) <= 1:
                print("⚠ Gardez au moins 1 Pokémon !"); return
            poke = self.equipe_joueur.pop(self.selection_equipe)
            self.reserve_pokemon.append(poke)
            self.selection_equipe = min(self.selection_equipe, len(self.equipe_joueur) - 1)
            print(f"→ {poke.nom} envoyé à la réserve")
        else:
            if not self.reserve_pokemon:
                print("IL N'Y A PLUS RIEN !"); return
            if len(self.equipe_joueur) >= 6:
                print("ON EST PLEIN !"); return
            poke = self.reserve_pokemon.pop(self.selection_reserve)
            self.equipe_joueur.append(poke)
            self.selection_reserve = min(self.selection_reserve, max(0, len(self.reserve_pokemon) - 1))
            print(f"→ {poke.nom} ajouté à l'équipe")


    # INPUTS — POKÉDEX
    def gerer_input_pokedex(self, event):
        if event.type != pygame.KEYDOWN:
            return
        with open(_chemin_json(), "r", encoding="utf-8") as f:
            total = len(json.load(f)["pokemon"])
        if event.key == pygame.K_UP:
            self.selection_pokedex = max(0, self.selection_pokedex - 1)
        elif event.key == pygame.K_DOWN:
            self.selection_pokedex = min(total - 1, self.selection_pokedex + 1)
        elif event.key == pygame.K_ESCAPE:
            self.etat = "exploration"


    # INPUTS — ÉVOLUTION
    def gerer_input_evolution(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_o:
            self._appliquer_evolution()
        elif event.key == pygame.K_n:
            print(f"⏸ {self.pokemon_a_evoluer.nom} n'a pas évolué")
            self.evolution_en_cours = self.pokemon_a_evoluer = None
            self.etat = "exploration"

    def _appliquer_evolution(self):
        poke     = self.pokemon_a_evoluer
        nouveau  = self.evolution_en_cours
        with open(_chemin_json(), "r", encoding="utf-8") as f:
            data = json.load(f)
        for p in data["pokemon"]:
            if p["name"] == nouveau:
                boost_pv  = (p["stats"]["pv"]       - poke.pv_max) // 2
                boost_att = (p["stats"]["attaque"]   - poke.attaque) // 2
                boost_def = (p["stats"]["defense"]   - poke.defense) // 2
                poke.nom      = nouveau
                poke.types    = p["type"]
                poke.pv_max  += boost_pv
                poke.pv      += boost_pv
                poke.attaque += boost_att
                poke.defense += boost_def
                self.pokedex.marquer_capture(nouveau)
                print(f"✨ {nouveau} ! PV+{boost_pv} ATK+{boost_att} DEF+{boost_def}")
                break
        self.evolution_en_cours = self.pokemon_a_evoluer = None
        self.etat = "exploration"


    # SAUVEGARDE / CHARGEMENT

    def sauvegarder_partie(self):
        return self.save_manager.sauvegarder(self)

    def charger_partie(self, save_data):
        try:
            j = save_data["joueur"]
            self.joueur_x  = j["position_x"]
            self.joueur_y  = j["position_y"]
            self.potions   = j["potions"]
            self.pokeballs = j["pokeballs"]
            self.equipe_joueur   = [self._pokemon_from_save(d) for d in save_data["equipe"]]
            self.reserve_pokemon = [self._pokemon_from_save(d) for d in save_data.get("reserve", [])]
            print("✓ Partie chargée avec succès !")
            return True
        except Exception as e:
            print(f"✗ Erreur chargement : {e}")
            import traceback; traceback.print_exc()
            return False

    @staticmethod
    def _pokemon_from_save(d):
        poke = Pokemon(d["nom"], d["types"], d["pv_max"],
                       d["attaque"], d["defense"], d["niveau"], d["legendary"])
        poke.pv         = d["pv"]
        poke.experience = d["experience"]
        return poke


    # DIVERS
    def _recharger_pokeballs(self):
        zone = self.carte.get_zone(self.joueur_x, self.joueur_y)
        if zone == "ville":
            if self.pokeballs < self.pokeballs_max:
                recharge = min(10, self.pokeballs_max - self.pokeballs)
                self.pokeballs += recharge
                print(f"Merci c'est gentil ! +{recharge} (Total: {self.pokeballs})")
            else:
                print(f"LA LIMITE C'EST 20 CONNARD ({self.pokeballs_max})")
        else:
            print("IL FAUT ÊTRE EN VILLE ABRUTI")