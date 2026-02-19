import pygame
import json
import os
from Logique.Gameplay.General.pokemon import Pokemon
from Logique.Gameplay.General.combat import Combat
from Graphique.map import Carte, RencontreManager, ZONES
from Logique.Gameplay.General.save_manager import SaveManager
from Logique.Gameplay.Pokedex.Pokedex_manager import PokedexManager
from Logique.Gameplay.General.Evolution import peut_evoluer, obtenir_evolution


class Game:
    def __init__(self):
        # Ne pas initialiser pygame ici, c'est fait par main.py
        self.largeur_ecran = 1000
        self.hauteur_ecran = 700
        self.screen = pygame.display.get_surface()

        # Polices
        self.font_titre = pygame.font.SysFont("Arial", 32, bold=True)
        self.font_normal = pygame.font.SysFont("Arial", 20)
        self.font_petit = pygame.font.SysFont("Arial", 16)

        self.clock = pygame.time.Clock()

        # Carte et système de rencontres
        self.carte = Carte(20, 15)

        # Chercher le fichier pokemon.json
        chemin_json = "pokemon.json"
        if not os.path.exists(chemin_json):
            chemin_json = "/mnt/user-data/outputs/pokemon.json"
        self.rencontre_manager = RencontreManager(chemin_json)

        # Position du joueur
        self.joueur_x = 10
        self.joueur_y = 7

        # Taille des cases
        self.taille_case = 40

        # Équipe du joueur
        self.equipe_joueur = []
        self.initialiser_equipe()

        # État du jeu
        self.etat = "exploration"  # "exploration", "combat", "menu_equipe", "menu_reserve"
        self.combat_actuel = None
        self.pokemon_sauvage = None

        # Compteur de pas
        self.pas_depuis_combat = 0
        self.pas_min_entre_combats = 5

        # Inventaire
        self.potions = 5
        self.pokeballs = 10
        self.pokeballs_max = 20

        # Réserve de Pokémon (stockage illimité)
        self.reserve_pokemon = []

        # Cache des images
        self.images_cache = {}

        # Charger l'image de l'arène
        self.arena_background = self.charger_arena_ameliore()

        # État running
        self.running = True

        # Menu équipe
        self.selection_equipe = 0

        # Menu réserve
        self.selection_reserve = 0
        self.mode_reserve = "equipe"  # "equipe" ou "reserve"

        # Gestionnaire de sauvegarde
        self.save_manager = SaveManager()
        self.pokedex = PokedexManager()
        self.evolution_en_cours = None
        self.pokemon_a_evoluer = None


    def afficher_pokedex(self):
        """Affiche le Pokédex complet avec images"""
        self.screen.fill((20, 30, 50))

        # Charger pokemon.json pour liste complète
        with open("pokemon.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            all_pokemon = data["pokemon"]

        # Titre
        titre = self.font_titre.render("POKÉDEX", True, (255, 215, 0))
        titre_rect = titre.get_rect(center=(500, 40))
        self.screen.blit(titre, titre_rect)

        # Stats
        stats = self.pokedex.obtenir_stats()
        total = len(all_pokemon)
        completion = self.pokedex.obtenir_completion(total)

        stats_text = f"Vus: {stats['vus']}/{total}  |  Capturés: {stats['captures']}/{total}  |  Complétion: {completion:.1f}%"
        stats_render = self.font_normal.render(stats_text, True, (200, 200, 200))
        stats_rect = stats_render.get_rect(center=(500, 75))
        self.screen.blit(stats_render, stats_rect)

        # Cadre de détails à droite
        pygame.draw.rect(self.screen, (50, 50, 70), (600, 120, 350, 500))
        pygame.draw.rect(self.screen, (100, 100, 120), (600, 120, 350, 500), 2)

        # Liste des Pokémon à gauche (scroll)
        y = 120
        start_idx = max(0, self.selection_pokedex - 10)
        visible_pokemon = all_pokemon[start_idx:start_idx + 12]

        for i, poke in enumerate(visible_pokemon):
            actual_idx = start_idx + i
            nom = poke["name"]

            # Sélection
            if actual_idx == self.selection_pokedex:
                pygame.draw.rect(self.screen, (255, 215, 0), (50, y - 5, 530, 40), 2)

            # Numéro
            numero = f"#{actual_idx + 1:03d}"
            self.afficher_texte(numero, 70, y + 5, self.font_normal, (150, 150, 150))

            # Déterminer statut
            est_capture = self.pokedex.est_capture(nom)
            est_vu = self.pokedex.est_vu(nom)

            # Mini image (30x30) à gauche
            if est_capture or est_vu:
                img_path = f"Assets/pokemon/{nom}.png"
                if os.path.exists(img_path):
                    try:
                        mini_img = pygame.image.load(img_path)
                        mini_img = pygame.transform.scale(mini_img, (30, 30))

                        # Si seulement vu, assombrir l'image
                        if est_vu and not est_capture:
                            mini_img.set_alpha(100)

                        self.screen.blit(mini_img, (170, y))
                    except:
                        # Image par défaut si erreur
                        pygame.draw.circle(self.screen, (100, 100, 100), (185, y + 15), 15)
                else:
                    # Pas d'image trouvée
                    pygame.draw.circle(self.screen, (100, 100, 100), (185, y + 15), 15)
            else:
                # Pokémon inconnu - point d'interrogation
                pygame.draw.circle(self.screen, (50, 50, 50), (185, y + 15), 15)
                unknown = self.font_petit.render("?", True, (150, 150, 150))
                self.screen.blit(unknown, (180, y + 5))

            # Nom
            if est_capture:
                couleur = (100, 255, 100)
                nom_affiche = nom
            elif est_vu:
                couleur = (255, 255, 100)
                nom_affiche = nom
            else:
                couleur = (100, 100, 100)
                nom_affiche = "???"

            self.afficher_texte(nom_affiche, 220, y + 5, self.font_normal, couleur)

            # Statut
            if est_capture:
                statut = "✓"
                statut_couleur = (100, 255, 100)
            elif est_vu:
                statut = "👁"
                statut_couleur = (255, 255, 100)
            else:
                statut = "?"
                statut_couleur = (100, 100, 100)

            self.afficher_texte(statut, 520, y + 5, self.font_normal, statut_couleur)

            y += 42

        # PANNEAU DE DÉTAILS À DROITE
        if 0 <= self.selection_pokedex < len(all_pokemon):
            pokemon_selectionne = all_pokemon[self.selection_pokedex]
            nom_pokemon = pokemon_selectionne["name"]

            est_capture = self.pokedex.est_capture(nom_pokemon)
            est_vu = self.pokedex.est_vu(nom_pokemon)

            if est_capture or est_vu:
                # Nom du Pokémon
                detail_y = 140
                nom_detail = self.font_titre.render(nom_pokemon, True, (255, 255, 255))
                nom_rect = nom_detail.get_rect(center=(775, detail_y))
                self.screen.blit(nom_detail, nom_rect)

                detail_y += 50

                # Grande image (120x120)
                img_path = f"Assets/pokemon/{nom_pokemon}.png"
                if os.path.exists(img_path):
                    try:
                        grande_img = pygame.image.load(img_path)
                        grande_img = pygame.transform.scale(grande_img, (120, 120))

                        # Si seulement vu, assombrir
                        if est_vu and not est_capture:
                            grande_img.set_alpha(150)

                        img_rect = grande_img.get_rect(center=(775, detail_y + 60))
                        self.screen.blit(grande_img, img_rect)
                    except:
                        # Image par défaut
                        pygame.draw.circle(self.screen, (100, 100, 100), (775, detail_y + 60), 60)
                else:
                    # Pas d'image
                    pygame.draw.circle(self.screen, (100, 100, 100), (775, detail_y + 60), 60)

                detail_y += 140

                # Types
                types = " / ".join(pokemon_selectionne["type"])
                types_render = self.font_normal.render(f"Type: {types}", True, (200, 200, 200))
                types_rect = types_render.get_rect(center=(775, detail_y))
                self.screen.blit(types_render, types_rect)

                detail_y += 40

                # Stats (si capturé)
                if est_capture:
                    stats_pokemon = pokemon_selectionne["stats"]

                    stat_labels = [
                        f"PV: {stats_pokemon['pv']}",
                        f"Attaque: {stats_pokemon['attaque']}",
                        f"Défense: {stats_pokemon['defense']}"
                    ]

                    for label in stat_labels:
                        stat_render = self.font_petit.render(label, True, (200, 200, 200))
                        stat_rect = stat_render.get_rect(center=(775, detail_y))
                        self.screen.blit(stat_render, stat_rect)
                        detail_y += 25

                    # Légendaire ?
                    if pokemon_selectionne.get("legendary", False):
                        detail_y += 15
                        legendary_text = self.font_normal.render("★ LÉGENDAIRE ★", True, (255, 215, 0))
                        legendary_rect = legendary_text.get_rect(center=(775, detail_y))
                        self.screen.blit(legendary_text, legendary_rect)
                else:
                    # Seulement vu - stats masquées
                    vu_text = self.font_normal.render("Capturez-le pour voir ses stats !", True, (150, 150, 150))
                    vu_rect = vu_text.get_rect(center=(775, detail_y + 40))
                    self.screen.blit(vu_text, vu_rect)
            else:
                # Pokémon inconnu
                unknown_y = 300
                unknown_title = self.font_titre.render("???", True, (100, 100, 100))
                unknown_rect = unknown_title.get_rect(center=(775, unknown_y))
                self.screen.blit(unknown_title, unknown_rect)

                unknown_y += 60
                pygame.draw.circle(self.screen, (50, 50, 50), (775, unknown_y), 60)

                unknown_y += 100
                unknown_text = self.font_normal.render("Pokémon inconnu", True, (100, 100, 100))
                unknown_text_rect = unknown_text.get_rect(center=(775, unknown_y))
                self.screen.blit(unknown_text, unknown_text_rect)

        # Instructions en bas
        instructions = "↑↓: Naviguer | ESC: Retour"
        instr_render = self.font_petit.render(instructions, True, (200, 200, 200))
        instr_rect = instr_render.get_rect(center=(500, 660))
        self.screen.blit(instr_render, instr_rect)

    def gerer_input_pokedex(self, event):
        """Gère les inputs du Pokédex"""
        if event.type == pygame.KEYDOWN:
            # Charger la liste pour connaître la taille
            with open("pokemon.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                total = len(data["pokemon"])

            if event.key == pygame.K_UP:
                self.selection_pokedex = max(0, self.selection_pokedex - 1)
            elif event.key == pygame.K_DOWN:
                self.selection_pokedex = min(total - 1, self.selection_pokedex + 1)
            elif event.key == pygame.K_ESCAPE:
                self.etat = "exploration"
                print("↩ Retour à l'exploration")

    def afficher_evolution(self):
        """Affiche l'écran d'évolution"""
        self.screen.fill((30, 20, 60))

        # Titre
        titre = self.font_titre.render("OH COMME IL EST MIGNON", True, (255, 215, 0))
        titre_rect = titre.get_rect(center=(500, 100))
        self.screen.blit(titre, titre_rect)

        # Message
        msg1 = f"{self.pokemon_a_evoluer.nom} atteint le niveau {self.pokemon_a_evoluer.niveau} !"
        msg2 = f"Il peut évoluer en {self.evolution_en_cours} !"

        msg1_render = self.font_normal.render(msg1, True, (255, 255, 255))
        msg2_render = self.font_normal.render(msg2, True, (255, 255, 255))

        msg1_rect = msg1_render.get_rect(center=(500, 250))
        msg2_rect = msg2_render.get_rect(center=(500, 290))

        self.screen.blit(msg1_render, msg1_rect)
        self.screen.blit(msg2_render, msg2_rect)

        # Choix
        choix1 = "[O] Accepter l'évolution"
        choix2 = "[N] Annuler"

        choix1_render = self.font_normal.render(choix1, True, (100, 255, 100))
        choix2_render = self.font_normal.render(choix2, True, (255, 100, 100))

        choix1_rect = choix1_render.get_rect(center=(500, 400))
        choix2_rect = choix2_render.get_rect(center=(500, 440))

        self.screen.blit(choix1_render, choix1_rect)
        self.screen.blit(choix2_render, choix2_rect)

    def gerer_input_evolution(self, event):
        """Gère les inputs de l'écran d'évolution"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_o:
                # Accepter l'évolution
                self.evoluer_pokemon(self.pokemon_a_evoluer, self.evolution_en_cours)
                self.evolution_en_cours = None
                self.pokemon_a_evoluer = None
                self.etat = "exploration"
            elif event.key == pygame.K_n:
                # Refuser l'évolution
                print(f"⏸ {self.pokemon_a_evoluer.nom} n'a pas évolué")
                self.evolution_en_cours = None
                self.pokemon_a_evoluer = None
                self.etat = "exploration"

    def evoluer_pokemon(self, pokemon, nouveau_nom):
        """Fait évoluer un Pokémon"""
        # Charger les stats du Pokémon évolué
        with open("pokemon.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            for p in data["pokemon"]:
                if p["name"] == nouveau_nom:
                    # Augmenter les stats
                    boost_pv = (p["stats"]["pv"] - pokemon.pv_max) // 2
                    boost_att = (p["stats"]["attaque"] - pokemon.attaque) // 2
                    boost_def = (p["stats"]["defense"] - pokemon.defense) // 2

                    pokemon.nom = nouveau_nom
                    pokemon.types = p["type"]
                    pokemon.pv_max += boost_pv
                    pokemon.pv += boost_pv
                    pokemon.attaque += boost_att
                    pokemon.defense += boost_def

                    print(f"✨ {nouveau_nom} !")
                    print(f"  PV +{boost_pv} | ATK +{boost_att} | DEF +{boost_def}")

                    # Marquer comme vu/capturé dans le Pokédex
                    self.pokedex.marquer_capture(nouveau_nom)
                    break

    def sauvegarder_partie(self):
        """Sauvegarde la partie en cours"""
        return self.save_manager.sauvegarder(self)

    def charger_partie(self, save_data):
        """Charge une partie sauvegardée"""
        try:
            # Restaurer la position
            self.joueur_x = save_data["joueur"]["position_x"]
            self.joueur_y = save_data["joueur"]["position_y"]
            self.potions = save_data["joueur"]["potions"]
            self.pokeballs = save_data["joueur"]["pokeballs"]

            # Restaurer l'équipe
            self.equipe_joueur = []
            for pokemon_data in save_data["equipe"]:
                pokemon = Pokemon(
                    nom=pokemon_data["nom"],
                    types=pokemon_data["types"],
                    pv_max=pokemon_data["pv_max"],
                    attaque=pokemon_data["attaque"],
                    defense=pokemon_data["defense"],
                    niveau=pokemon_data["niveau"],
                    legendary=pokemon_data["legendary"]
                )
                # Restaurer les PV actuels et l'expérience
                pokemon.pv = pokemon_data["pv"]
                pokemon.experience = pokemon_data["experience"]
                self.equipe_joueur.append(pokemon)

            # Restaurer la réserve
            self.reserve_pokemon = []
            if "reserve" in save_data:
                for pokemon_data in save_data["reserve"]:
                    pokemon = Pokemon(
                        nom=pokemon_data["nom"],
                        types=pokemon_data["types"],
                        pv_max=pokemon_data["pv_max"],
                        attaque=pokemon_data["attaque"],
                        defense=pokemon_data["defense"],
                        niveau=pokemon_data["niveau"],
                        legendary=pokemon_data["legendary"]
                    )
                    pokemon.pv = pokemon_data["pv"]
                    pokemon.experience = pokemon_data["experience"]
                    self.reserve_pokemon.append(pokemon)

            print("✓ Partie chargée avec succès !")
            return True

        except Exception as e:
            print(f"✗ Erreur lors du chargement de la partie : {e}")
            import traceback
            traceback.print_exc()
            return False

    def charger_arena(self):
        """Charge l'image de l'arène pour le combat"""
        chemins_possibles = [
            "Assets/arène_pokemon.png",  # En premier car c'est là qu'elle est
            "Assets/arena.png",
            "arène_pokemon.png",
            "arena.png",
            "backgrounds/arena.png",
            "backgrounds/arène_pokemon.png"
        ]

        for chemin in chemins_possibles:
            try:
                if os.path.exists(chemin):
                    img = pygame.image.load(chemin)
                    # Redimensionner à la taille de l'écran
                    img = pygame.transform.scale(img, (self.largeur_ecran, self.hauteur_ecran))
                    print(f"✓ Arène chargée: {chemin}")
                    return img
            except Exception as e:
                print(f"✗ Erreur chargement arène {chemin}: {e}")
                continue

        print("⚠ Aucune image d'arène trouvée, utilisation du fond par défaut")
        return None

    def charger_image_pokemon(self, nom_pokemon):
        """Charge l'image d'un Pokémon avec plusieurs tentatives de chemins"""
        # Vérifier le cache
        if nom_pokemon in self.images_cache:
            return self.images_cache[nom_pokemon]

        # Liste des chemins possibles
        chemins_possibles = [
            f"Assets/pokemon/{nom_pokemon}.png",
            f"Assets/pokemon/{nom_pokemon.lower()}.png",
            f"Assets/pokemon/{nom_pokemon.upper()}.png",
            f"assets/pokemon/{nom_pokemon}.png",
            f"assets/pokemon/{nom_pokemon.lower()}.png",
            f"pokemon/{nom_pokemon}.png",
            f"sprites/{nom_pokemon}.png",
            f"images/{nom_pokemon}.png"
        ]

        for chemin in chemins_possibles:
            try:
                if os.path.exists(chemin):
                    img = pygame.image.load(chemin)
                    # Redimensionner
                    img = pygame.transform.scale(img, (120, 120))
                    # Mettre en cache
                    self.images_cache[nom_pokemon] = img
                    print(f"✓ Image chargée: {chemin}")
                    return img
            except Exception as e:
                print(f"✗ Erreur chargement {chemin}: {e}")
                continue

        # Aucune image trouvée
        print(f"⚠ Aucune image trouvée pour {nom_pokemon}")
        return None

    def render(self):
        """Affiche le jeu"""
        self.screen.fill((20, 20, 40))

        if self.etat == "exploration":
            self.afficher_carte()
            self.afficher_infos_zone()
            self.afficher_equipe()

            # Instructions
            self.afficher_texte("Déplacement: Flèches ou ZQSD", 50, 650, self.font_petit, (200, 200, 200))
            self.afficher_texte("[H] Soigner | [E] Équipe | [G] Sauvegarder | [ESC] Menu", 50, 670, self.font_petit,
                                (200, 200, 200))

        elif self.etat == "combat":
            self.afficher_combat()

        elif self.etat == "menu_equipe":
            self.afficher_menu_equipe()

        elif self.etat == "menu_reserve":
            self.afficher_menu_reserve()

        elif self.etat == "pokedex":
            self.afficher_pokedex()
        elif self.etat == "evolution":
            self.afficher_evolution()

    def initialiser_equipe(self):
        """Initialise l'équipe de départ du joueur"""
        starter_data = self.rencontre_manager.pokedex.get("Keunotor")
        if starter_data:
            starter = Pokemon.from_pokedex(starter_data, 5)
            self.equipe_joueur.append(starter)

    def deplacer_joueur(self, dx, dy):
        """Déplace le joueur et vérifie les rencontres"""
        nouveau_x = self.joueur_x + dx
        nouveau_y = self.joueur_y + dy

        if 0 <= nouveau_x < self.carte.largeur and 0 <= nouveau_y < self.carte.hauteur:
            self.joueur_x = nouveau_x
            self.joueur_y = nouveau_y
            self.pas_depuis_combat += 1

            if self.pas_depuis_combat >= self.pas_min_entre_combats:
                zone = self.carte.get_zone(self.joueur_x, self.joueur_y)
                pokemon_rencontre = self.rencontre_manager.verifier_rencontre(
                    zone, (self.joueur_x, self.joueur_y)
                )

                if pokemon_rencontre and self.equipe_joueur:
                    self.demarrer_combat(pokemon_rencontre)
                    self.pas_depuis_combat = 0

    def demarrer_combat(self, pokemon_sauvage):
        """Démarre un combat contre un Pokémon sauvage"""
        self.etat = "combat"
        self.pokemon_sauvage = pokemon_sauvage
        pokemon_actif = self.get_pokemon_actif()
        if pokemon_actif:
            self.combat_actuel = Combat(pokemon_actif, pokemon_sauvage)
            self.pokedex.marquer_vu(self.pokemon_sauvage.nom)

    def get_pokemon_actif(self):
        """Retourne le premier Pokémon vivant de l'équipe"""
        for pokemon in self.equipe_joueur:
            if pokemon.est_vivant():
                return pokemon
        return None

    def afficher_carte(self):
        """Affiche la carte et le joueur"""
        offset_x = 50
        offset_y = 50

        for y in range(self.carte.hauteur):
            for x in range(self.carte.largeur):
                zone_type = self.carte.grille[y][x]
                couleur = ZONES[zone_type]["couleur"]

                rect = pygame.Rect(
                    offset_x + x * self.taille_case,
                    offset_y + y * self.taille_case,
                    self.taille_case,
                    self.taille_case
                )
                pygame.draw.rect(self.screen, couleur, rect)
                pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)

        # Joueur
        joueur_rect = pygame.Rect(
            offset_x + self.joueur_x * self.taille_case + 5,
            offset_y + self.joueur_y * self.taille_case + 5,
            self.taille_case - 10,
            self.taille_case - 10
        )
        pygame.draw.circle(
            self.screen,
            (255, 0, 0),
            joueur_rect.center,
            15
        )

    def afficher_infos_zone(self):
        """Affiche les informations de la zone actuelle"""
        zone_type = self.carte.get_zone(self.joueur_x, self.joueur_y)
        zone_info = ZONES[zone_type]

        y_offset = 50
        self.afficher_texte(f"Zone: {zone_info['nom']}", 850, y_offset, self.font_normal)
        self.afficher_texte(f"Position: ({self.joueur_x}, {self.joueur_y})", 850, y_offset + 30, self.font_petit)
        self.afficher_texte(f"Potions: {self.potions}", 850, y_offset + 60, self.font_petit)
        self.afficher_texte(f"Pokéballs: {self.pokeballs}", 850, y_offset + 85, self.font_petit)

    def afficher_equipe(self):
        """Affiche l'équipe du joueur"""
        y_offset = 200
        self.afficher_texte("Votre équipe:", 850, y_offset, self.font_normal, (255, 215, 0))

        for i, pokemon in enumerate(self.equipe_joueur):
            y = y_offset + 30 + i * 80

            # Nom et niveau
            self.afficher_texte(f"{pokemon.nom} Nv.{pokemon.niveau}", 850, y, self.font_petit)

            # Barre de PV
            self.afficher_barre_pv(pokemon, 850, y + 20, 120)

            # Stats
            self.afficher_texte(
                f"ATK:{pokemon.attaque} DEF:{pokemon.defense}",
                850, y + 45, self.font_petit, (200, 200, 200)
            )

    def afficher_combat(self):
        """Affiche l'écran de combat avec l'arène"""
        if not self.combat_actuel:
            return

        # Fond d'arène ou couleur par défaut
        if self.arena_background:
            self.screen.blit(self.arena_background, (0, 0))
        else:
            pygame.draw.rect(self.screen, (40, 40, 60), (0, 0, self.largeur_ecran, self.hauteur_ecran))

        # POKÉMON SAUVAGE (sur le logo P au centre-gauche)
        pos_sauvage_x = 380
        pos_sauvage_y = 480

        # Charger et afficher l'image du Pokémon sauvage
        img_sauvage = self.charger_image_pokemon(self.pokemon_sauvage.nom)
        if img_sauvage:
            img_sauvage_grande = pygame.transform.scale(img_sauvage, (100, 100))
            img_rect = img_sauvage_grande.get_rect(center=(pos_sauvage_x, pos_sauvage_y))
            self.screen.blit(img_sauvage_grande, img_rect)
        else:
            pygame.draw.circle(self.screen, (255, 100, 100), (pos_sauvage_x, pos_sauvage_y), 50)

        # Infos Pokémon sauvage (en haut à gauche)
        y_info_sauvage = 80
        self.afficher_texte(
            f"{self.pokemon_sauvage.nom} Nv.{self.pokemon_sauvage.niveau}",
            15, y_info_sauvage, self.font_normal, (255, 255, 255)
        )
        if self.pokemon_sauvage.legendary:
            self.afficher_texte("★ LÉGENDAIRE ★", 15, y_info_sauvage + 30, self.font_petit, (255, 215, 0))

        # Barre de PV sauvage
        self.afficher_barre_pv(self.pokemon_sauvage, 15, y_info_sauvage + 55, 250)

        # POKÉMON DU JOUEUR (sur le logo P au centre-droite)
        pokemon_joueur = self.combat_actuel.pokemon_joueur
        pos_joueur_x = 620
        pos_joueur_y = 480

        # Charger et afficher l'image du Pokémon du joueur
        img_joueur = self.charger_image_pokemon(pokemon_joueur.nom)
        if img_joueur:
            img_joueur_grande = pygame.transform.scale(img_joueur, (100, 100))
            img_joueur_flip = pygame.transform.flip(img_joueur_grande, True, False)
            img_rect = img_joueur_flip.get_rect(center=(pos_joueur_x, pos_joueur_y))
            self.screen.blit(img_joueur_flip, img_rect)
        else:
            pygame.draw.circle(self.screen, (100, 255, 100), (pos_joueur_x, pos_joueur_y), 50)

        # Infos Pokémon joueur (EN HAUT À DROITE)
        y_info_joueur = 80
        x_info_joueur = 735
        self.afficher_texte(
            f"Votre {pokemon_joueur.nom} Nv.{pokemon_joueur.niveau}",
            x_info_joueur, y_info_joueur, self.font_normal, (255, 255, 255)
        )

        # Barre de PV joueur (EN HAUT À DROITE)
        self.afficher_barre_pv(pokemon_joueur, x_info_joueur, y_info_joueur + 30, 250)

        # ZONE DES BOUTONS ET LOGS avec fond opaque RÉDUIT
        fond_interface = pygame.Surface((450, 180))
        fond_interface.set_alpha(220)
        fond_interface.fill((30, 30, 50))
        self.screen.blit(fond_interface, (530, 520))

        # Logs de combat
        y_logs = 530
        x_logs = 550

        self.afficher_texte("Combat:", x_logs, y_logs, self.font_petit, (255, 215, 0))
        logs = self.combat_actuel.get_derniers_logs(2)
        for i, log in enumerate(logs):
            self.afficher_texte(log, x_logs, y_logs + 25 + i * 20, self.font_petit, (255, 255, 255))

        # Boutons d'action dans la zone opaque
        if not self.combat_actuel.termine:
            self.afficher_boutons_combat()
        else:
            self.afficher_fin_combat()

    def afficher_boutons_combat(self):
        """Affiche les boutons d'action en combat sur 2 colonnes"""
        # Organisation en 2 colonnes avec attaque spéciale
        boutons_gauche = [
            "[A] Attaquer",
            "[S] Attaque Spé.",
            f"[P] Potion ({self.potions})",
            f"[C] Capturer ({self.pokeballs})"
        ]

        boutons_droite = [
            "[X] Changer",
            "[F] Fuir"
        ]

        # Position dans la zone opaque réduite
        x_gauche = 550
        x_droite = 760
        y_start = 590

        # Colonne de gauche
        for i, texte in enumerate(boutons_gauche):
            couleur = (255, 100, 255) if "Spé" in texte else (255, 255, 100)
            self.afficher_texte(texte, x_gauche, y_start + i * 25, self.font_petit, couleur)

        # Colonne de droite
        for i, texte in enumerate(boutons_droite):
            self.afficher_texte(texte, x_droite, y_start + i * 25, self.font_petit, (255, 255, 100))

    def afficher_fin_combat(self):
        """Affiche le résultat du combat"""
        if self.combat_actuel.pokemon_capture:
            texte = f"{self.pokemon_sauvage.nom} CAPTURÉ !"
            couleur = (255, 215, 0)
        elif self.combat_actuel.joueur_gagne:
            texte = "VICTOIRE !"
            couleur = (100, 255, 100)
        else:
            texte = "TU ES MAUVAIS"
            couleur = (255, 100, 100)

        self.afficher_texte(texte, 400, 300, self.font_titre, couleur)
        self.afficher_texte("[ESPACE] Continuer", 350, 350, self.font_normal, (255, 255, 255))

    def afficher_barre_pv(self, pokemon, x, y, largeur):
        """Affiche une barre de PV"""
        ratio_pv = pokemon.pv / pokemon.pv_max if pokemon.pv_max > 0 else 0

        if ratio_pv > 0.5:
            couleur = (100, 255, 100)
        elif ratio_pv > 0.2:
            couleur = (255, 200, 50)
        else:
            couleur = (255, 50, 50)

        pygame.draw.rect(self.screen, (50, 50, 50), (x, y, largeur, 20))
        pygame.draw.rect(self.screen, couleur, (x, y, int(largeur * ratio_pv), 20))
        pygame.draw.rect(self.screen, (255, 255, 255), (x, y, largeur, 20), 2)

        texte_pv = f"{pokemon.pv}/{pokemon.pv_max}"
        self.afficher_texte(texte_pv, x + largeur + 10, y, self.font_petit)

    def afficher_texte(self, texte, x, y, font=None, couleur=(255, 255, 255)):
        """Affiche du texte à l'écran"""
        if font is None:
            font = self.font_normal
        surface = font.render(texte, True, couleur)
        self.screen.blit(surface, (x, y))

    def gerer_input_exploration(self, event):
        """Gère les inputs en mode exploration"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_z:
                self.deplacer_joueur(0, -1)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.deplacer_joueur(0, 1)
            elif event.key == pygame.K_LEFT or event.key == pygame.K_q:
                self.deplacer_joueur(-1, 0)
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                self.deplacer_joueur(1, 0)
            elif event.key == pygame.K_h:
                for pokemon in self.equipe_joueur:
                    pokemon.soigner()
                print("✓ Équipe soignée !")
            elif event.key == pygame.K_e:
                # Ouvrir menu équipe
                self.etat = "menu_equipe"
                self.selection_equipe = 0
            elif event.key == pygame.K_r:
                # Recharger Pokéballs en ville OU ouvrir menu réserve
                zone = self.carte.get_zone(self.joueur_x, self.joueur_y)
                if zone == "ville":
                    # Si on est en ville, R ouvre le menu réserve
                    self.etat = "menu_reserve"
                    self.mode_reserve = "equipe"
                    self.selection_reserve = 0
                    self.selection_equipe = 0
                else:
                    print("Bah les pokemons réserves ils sont où ? EN VILLE")
            elif event.key == pygame.K_t:
                # Recharger Pokéballs en ville (nouveau raccourci)
                self.recharger_pokeballs()
            elif event.key == pygame.K_g:
                # Sauvegarder la partie (touche G)
                if self.sauvegarder_partie():
                    print("💾 Partie sauvegardée !")
            elif event.key == pygame.K_p:
                # Ouvrir le Pokédex
                self.etat = "pokedex"
                self.selection_pokedex = 0

    def gerer_input_combat(self, event):
        """Gère les inputs en mode combat"""
        if event.type == pygame.KEYDOWN:
            if self.combat_actuel.termine:
                if event.key == pygame.K_SPACE:
                    # Si capturé, ajouter à l'équipe ou à la réserve
                    if self.combat_actuel.pokemon_capture:
                        self.pokedex.marquer_capture(self.pokemon_sauvage.nom)
                        if len(self.equipe_joueur) < 6:
                            self.equipe_joueur.append(self.pokemon_sauvage)
                            print(f"✓ {self.pokemon_sauvage.nom} ajouté à l'équipe !")
                        else:
                            self.reserve_pokemon.append(self.pokemon_sauvage)
                            print(f"✓ {self.pokemon_sauvage.nom} envoyé à la réserve ! (Équipe pleine)")
                            print(f" Allez en ville et appuyez sur [R] pour gérer votre réserve")

                    self.etat = "exploration"
                    self.combat_actuel = None
                    self.pokemon_sauvage = None
            else:
                if event.key == pygame.K_a:
                    self.combat_actuel.tour_combat("attaque")
                elif event.key == pygame.K_s:
                    # Attaque spéciale : 50% réussite, 100% critique
                    self.combat_actuel.tour_combat("attaque_speciale")
                elif event.key == pygame.K_p and self.potions > 0:
                    self.combat_actuel.utiliser_potion()
                    self.potions -= 1
                elif event.key == pygame.K_c and self.pokeballs > 0:
                    self.combat_actuel.tour_combat("capture")
                    self.pokeballs -= 1
                elif event.key == pygame.K_x:
                    # Changer de Pokémon en combat
                    self.etat = "menu_equipe"
                    self.selection_equipe = 0
                elif event.key == pygame.K_f:
                    self.combat_actuel.tour_combat("fuite")

    def recharger_pokeballs(self):
        """Recharge les Pokéballs en ville"""
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

    def afficher_menu_equipe(self):
        """Affiche le menu de l'équipe"""
        self.screen.fill((30, 30, 50))

        # Titre
        titre = self.font_titre.render("VOTRE ÉQUIPE", True, (255, 215, 0))
        titre_rect = titre.get_rect(center=(500, 50))
        self.screen.blit(titre, titre_rect)

        # Afficher chaque Pokémon
        y_start = 120
        spacing = 90

        for i, pokemon in enumerate(self.equipe_joueur):
            y = y_start + i * spacing

            # Cadre de sélection
            if i == self.selection_equipe:
                pygame.draw.rect(self.screen, (100, 255, 100), (50, y - 10, 900, 80), 3)

            # Indicateur Pokémon actif
            if i == 0:
                self.afficher_texte("★", 70, y + 10, self.font_titre, (255, 215, 0))

            # Nom et niveau
            couleur_nom = (255, 100, 100) if not pokemon.est_vivant() else (255, 255, 255)
            self.afficher_texte(f"{pokemon.nom} Nv.{pokemon.niveau}", 120, y, self.font_normal, couleur_nom)

            # Types
            types_text = " / ".join(pokemon.types)
            self.afficher_texte(types_text, 120, y + 25, self.font_petit, (200, 200, 200))

            # Barre de PV
            self.afficher_barre_pv(pokemon, 400, y + 15, 300)

            # Stats
            self.afficher_texte(f"ATK:{pokemon.attaque} DEF:{pokemon.defense}", 750, y + 15, self.font_petit,
                                (200, 200, 200))

            # État K.O.
            if not pokemon.est_vivant():
                self.afficher_texte("K.O.", 850, y + 15, self.font_normal, (255, 50, 50))

        # Instructions
        instructions = [
            "↑↓ : Naviguer",
            "ENTRÉE : Changer Pokémon actif",
            "ESC : Retour"
        ]
        y_instructions = 600
        for i, instruction in enumerate(instructions):
            self.afficher_texte(instruction, 50, y_instructions + i * 25, self.font_petit, (150, 150, 150))

    def gerer_input_menu_equipe(self, event):
        """Gère les inputs du menu équipe"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selection_equipe = (self.selection_equipe - 1) % len(self.equipe_joueur)
            elif event.key == pygame.K_DOWN:
                self.selection_equipe = (self.selection_equipe + 1) % len(self.equipe_joueur)
            elif event.key == pygame.K_RETURN:
                # Changer le Pokémon actif
                if self.equipe_joueur[self.selection_equipe].est_vivant():
                    # Échanger avec le premier
                    self.equipe_joueur[0], self.equipe_joueur[self.selection_equipe] = \
                        self.equipe_joueur[self.selection_equipe], self.equipe_joueur[0]
                    self.selection_equipe = 0
                    print(f"✓ {self.equipe_joueur[0].nom} est maintenant actif !")

                    # Si on était en combat, mettre à jour le combat et y retourner
                    if self.combat_actuel:
                        self.combat_actuel.pokemon_joueur = self.equipe_joueur[0]
                        self.combat_actuel.logs.append(f"Vous envoyez {self.equipe_joueur[0].nom} !")

                        # Le Pokémon sauvage attaque pendant le changement
                        if not self.combat_actuel.termine:
                            resultat = self.combat_actuel.pokemon_sauvage.attaquer(self.combat_actuel.pokemon_joueur)
                            self.combat_actuel.logs.append(resultat["message"])

                            if not self.combat_actuel.pokemon_joueur.est_vivant():
                                self.combat_actuel.logs.append(f"{self.combat_actuel.pokemon_joueur.nom} est K.O. !")
                                # Vérifier si tous les Pokémon sont K.O.
                                if not any(p.est_vivant() for p in self.equipe_joueur):
                                    self.combat_actuel.termine = True
                                    self.combat_actuel.joueur_gagne = False

                        self.etat = "combat"
                    else:
                        # Si on était en exploration, retourner à l'exploration
                        self.etat = "exploration"
                else:
                    print("⚠ Ce Pokémon est K.O. !")
            elif event.key == pygame.K_ESCAPE:
                # Retour à l'état précédent
                if self.combat_actuel:
                    self.etat = "combat"
                else:
                    self.etat = "exploration"

    def charger_arena_ameliore(self):
        """Charge l'image de l'arène avec tous les noms possibles"""
        # Liste exhaustive de tous les noms possibles
        noms_fichiers = [
            "arène_pokemon.png",
            "arene_pokemon.png",  # sans accent
            "arena_pokemon.png",
            "arena.png",
            "arène pokemon.png",  # avec espace
            "arene pokemon.png"
        ]

        dossiers = ["Assets/", "assets/", "Assets/backgrounds/", ""]

        for dossier in dossiers:
            for nom in noms_fichiers:
                chemin = dossier + nom
                try:
                    if os.path.exists(chemin):
                        img = pygame.image.load(chemin)
                        img = pygame.transform.scale(img, (self.largeur_ecran, self.hauteur_ecran))
                        print(f"✓ Arène chargée: {chemin}")
                        return img
                except Exception as e:
                    continue

        print("IL N'Y A RIEN A VOIR")
        return None

    def afficher_menu_reserve(self):
        """Affiche le menu de gestion de la réserve (en ville uniquement)"""
        self.screen.fill((20, 30, 50))

        # Titre
        titre = self.font_titre.render("GESTION DE LA RÉSERVE", True, (255, 215, 0))
        titre_rect = titre.get_rect(center=(500, 40))
        self.screen.blit(titre, titre_rect)

        # Info
        info = self.font_petit.render(f"Équipe: {len(self.equipe_joueur)}/6 | Réserve: {len(self.reserve_pokemon)}",
                                      True, (200, 200, 200))
        info_rect = info.get_rect(center=(500, 75))
        self.screen.blit(info, info_rect)

        # Deux colonnes : Équipe (gauche) et Réserve (droite)
        # Colonne ÉQUIPE
        x_equipe = 50
        y_start = 120

        equipe_label = self.font_normal.render("ÉQUIPE ACTIVE", True,
                                               (100, 255, 100) if self.mode_reserve == "equipe" else (150, 150, 150))
        self.screen.blit(equipe_label, (x_equipe, y_start))

        # Cadre équipe
        cadre_couleur = (100, 255, 100) if self.mode_reserve == "equipe" else (100, 100, 100)
        pygame.draw.rect(self.screen, cadre_couleur, (x_equipe - 10, y_start + 30, 420, 450), 2)

        y = y_start + 40
        for i, pokemon in enumerate(self.equipe_joueur):
            # Sélection
            if self.mode_reserve == "equipe" and i == self.selection_equipe:
                pygame.draw.rect(self.screen, (255, 215, 0), (x_equipe, y - 5, 400, 70), 2)

            # Pokémon actif
            if i == 0:
                self.afficher_texte("★", x_equipe + 10, y + 10, self.font_titre, (255, 215, 0))

            # Nom et niveau
            couleur_nom = (255, 100, 100) if not pokemon.est_vivant() else (255, 255, 255)
            self.afficher_texte(f"{pokemon.nom} Nv.{pokemon.niveau}", x_equipe + 50, y, self.font_normal, couleur_nom)

            # Types
            types_text = " / ".join(pokemon.types)
            self.afficher_texte(types_text, x_equipe + 50, y + 25, self.font_petit, (200, 200, 200))

            # Barre de PV
            self.afficher_barre_pv(pokemon, x_equipe + 220, y + 10, 150)

            y += 75

        # Colonne RÉSERVE
        x_reserve = 530

        reserve_label = self.font_normal.render(f"RÉSERVE ({len(self.reserve_pokemon)})", True,
                                                (100, 200, 255) if self.mode_reserve == "reserve" else (150, 150, 150))
        self.screen.blit(reserve_label, (x_reserve, y_start))

        # Cadre réserve
        cadre_couleur = (100, 200, 255) if self.mode_reserve == "reserve" else (100, 100, 100)
        pygame.draw.rect(self.screen, cadre_couleur, (x_reserve - 10, y_start + 30, 420, 450), 2)

        y = y_start + 40

        # Scroll pour la réserve (afficher max 6 à la fois)
        start_idx = max(0, self.selection_reserve - 5)
        visible_reserve = self.reserve_pokemon[start_idx:start_idx + 6]

        if len(self.reserve_pokemon) == 0:
            no_pokemon = self.font_normal.render("Aucun Pokémon en réserve", True, (150, 150, 150))
            no_pokemon_rect = no_pokemon.get_rect(center=(x_reserve + 200, y_start + 200))
            self.screen.blit(no_pokemon, no_pokemon_rect)
        else:
            for i, pokemon in enumerate(visible_reserve):
                actual_idx = start_idx + i

                # Sélection
                if self.mode_reserve == "reserve" and actual_idx == self.selection_reserve:
                    pygame.draw.rect(self.screen, (255, 215, 0), (x_reserve, y - 5, 400, 70), 2)

                # Nom et niveau
                couleur_nom = (255, 100, 100) if not pokemon.est_vivant() else (255, 255, 255)
                self.afficher_texte(f"{pokemon.nom} Nv.{pokemon.niveau}", x_reserve + 10, y, self.font_normal,
                                    couleur_nom)

                # Types
                types_text = " / ".join(pokemon.types)
                self.afficher_texte(types_text, x_reserve + 10, y + 25, self.font_petit, (200, 200, 200))

                # Barre de PV
                self.afficher_barre_pv(pokemon, x_reserve + 220, y + 10, 150)

                y += 75

        # Instructions en bas
        y_instructions = 610
        instructions = [
            "TAB: Changer de colonne | ↑↓: Naviguer",
            "ENTRÉE: Échanger Équipe ↔ Réserve | ESC: Retour"
        ]
        for i, instruction in enumerate(instructions):
            txt = self.font_petit.render(instruction, True, (200, 200, 200))
            txt_rect = txt.get_rect(center=(500, y_instructions + i * 25))
            self.screen.blit(txt, txt_rect)

    def gerer_input_menu_reserve(self, event):
        """Gère les inputs du menu réserve"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                # Changer de colonne
                if self.mode_reserve == "equipe":
                    self.mode_reserve = "reserve"
                    self.selection_reserve = 0
                else:
                    self.mode_reserve = "equipe"
                    self.selection_equipe = 0

            elif event.key == pygame.K_UP:
                if self.mode_reserve == "equipe":
                    self.selection_equipe = max(0, self.selection_equipe - 1)
                else:
                    self.selection_reserve = max(0, self.selection_reserve - 1)

            elif event.key == pygame.K_DOWN:
                if self.mode_reserve == "equipe":
                    self.selection_equipe = min(len(self.equipe_joueur) - 1, self.selection_equipe + 1)
                else:
                    self.selection_reserve = min(len(self.reserve_pokemon) - 1, self.selection_reserve + 1)

            elif event.key == pygame.K_RETURN:
                # Échanger entre équipe et réserve
                self.echanger_equipe_reserve()

            elif event.key == pygame.K_ESCAPE:
                self.etat = "exploration"

    def echanger_equipe_reserve(self):
        """Échange un Pokémon entre l'équipe et la réserve"""
        if self.mode_reserve == "equipe":
            # Envoyer un Pokémon de l'équipe vers la réserve
            if len(self.equipe_joueur) <= 1:
                print(" Faut au moins 1 pokemon tu penses pas !")
                return

            pokemon = self.equipe_joueur[self.selection_equipe]
            self.equipe_joueur.pop(self.selection_equipe)
            self.reserve_pokemon.append(pokemon)
            print(f"→ {pokemon.nom} envoyé à la réserve")

            # Ajuster la sélection
            self.selection_equipe = min(self.selection_equipe, len(self.equipe_joueur) - 1)

        else:
            # Récupérer un Pokémon de la réserve vers l'équipe
            if len(self.reserve_pokemon) == 0:
                print("IL N'Y A PLUS RIEN DU TOUT  !")
                return

            if len(self.equipe_joueur) >= 6:
                print("ON EST PLEIN ! GO EN ZONZON")
                return

            pokemon = self.reserve_pokemon[self.selection_reserve]
            self.reserve_pokemon.pop(self.selection_reserve)
            self.equipe_joueur.append(pokemon)
            print(f"→ {pokemon.nom} ajouté à l'équipe")

            # Ajuster la sélection
            if len(self.reserve_pokemon) > 0:
                self.selection_reserve = min(self.selection_reserve, len(self.reserve_pokemon) - 1)