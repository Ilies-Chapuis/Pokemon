import pygame
import json
import os
from pokemon import Pokemon
from combat import Combat
from map import Carte, RencontreManager, ZONES


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
        self.etat = "exploration"  # "exploration", "combat", "menu_equipe"
        self.combat_actuel = None
        self.pokemon_sauvage = None

        # Compteur de pas
        self.pas_depuis_combat = 0
        self.pas_min_entre_combats = 5

        # Inventaire
        self.potions = 5
        self.pokeballs = 10
        self.pokeballs_max = 20

        # Cache des images
        self.images_cache = {}

        # Charger l'image de l'arène
        self.arena_background = self.charger_arena_ameliore()

        # État running
        self.running = True

        # Menu équipe
        self.selection_equipe = 0

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
            self.afficher_texte("[H] Soigner | [E] Équipe | [ESC] Menu", 50, 670, self.font_petit, (200, 200, 200))

        elif self.etat == "combat":
            self.afficher_combat()

        elif self.etat == "menu_equipe":
            self.afficher_menu_equipe()

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
        #Affiche l'écran de combat avec l'arène
        if not self.combat_actuel:
            return

        # Fond d'arène ou couleur par défaut
        if self.arena_background:
            self.screen.blit(self.arena_background, (0, 0))
        else:
            pygame.draw.rect(self.screen, (40, 40, 60), (0, 0, self.largeur_ecran, self.hauteur_ecran))

        # Pokemon sauvage au milieu
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

        # Infos du Pokémon sauvage
        y_info_sauvage = 80
        self.afficher_texte(
            f"{self.pokemon_sauvage.nom} Nv.{self.pokemon_sauvage.niveau}",
            15, y_info_sauvage, self.font_normal, (255, 255, 255)
        )
        if self.pokemon_sauvage.legendary:
            self.afficher_texte("★ LÉGENDAIRE ★", 15, y_info_sauvage + 30, self.font_petit, (255, 215, 0))

        # Barre de PV adverse
        self.afficher_barre_pv(self.pokemon_sauvage, 15, y_info_sauvage + 55, 250)

        # Notre pokemon
        pokemon_joueur = self.combat_actuel.pokemon_joueur
        pos_joueur_x = 620
        pos_joueur_y = 480

        # Charger et afficher l'image de notre pokemon
        img_joueur = self.charger_image_pokemon(pokemon_joueur.nom)
        if img_joueur:
            img_joueur_grande = pygame.transform.scale(img_joueur, (100, 100))
            img_joueur_flip = pygame.transform.flip(img_joueur_grande, True, False)
            img_rect = img_joueur_flip.get_rect(center=(pos_joueur_x, pos_joueur_y))
            self.screen.blit(img_joueur_flip, img_rect)
        else:
            pygame.draw.circle(self.screen, (100, 255, 100), (pos_joueur_x, pos_joueur_y), 50)

        # Infos Pokémon joueur
        y_info_joueur = 80
        x_info_joueur = 735
        self.afficher_texte(
            f"Votre {pokemon_joueur.nom} Nv.{pokemon_joueur.niveau}",
            x_info_joueur, y_info_joueur, self.font_normal, (255, 255, 255)
        )

        # Barre de PV joueur
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
        #Affiche les boutons d'action en combat sur 2 colonnes
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
            texte = "DÉFAITE..."
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
                print("TUT TUT TUT C'EST L'AMBULANCE")
            elif event.key == pygame.K_e:
                # Ouvrir menu équipe
                self.etat = "menu_equipe"
                self.selection_equipe = 0
            elif event.key == pygame.K_r:
                # Recharger Pokéballs en ville
                self.recharger_pokeballs()

    def gerer_input_combat(self, event):
        """Gère les inputs en mode combat"""
        if event.type == pygame.KEYDOWN:
            if self.combat_actuel.termine:
                if event.key == pygame.K_SPACE:
                    # Si capturé, ajouter à l'équipe
                    if self.combat_actuel.pokemon_capture:
                        if len(self.equipe_joueur) < 6:
                            self.equipe_joueur.append(self.pokemon_sauvage)
                            print(f"✓ {self.pokemon_sauvage.nom} ajouté à l'équipe !")
                        else:
                            print(f"C'est complet bordel on est trop serré {self.pokemon_sauvage.nom} tu dégages")

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
                print(f"Merci c'est très gentil +{recharge} (Total: {self.pokeballs})")
            else:
                print(f"PAS PLUS DE 20 CONNARD ({self.pokeballs_max})")
        else:
            print("Tu dois être en ville abruti")

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
                    print("IL EST KO DUGLAND LAISSE LE TRANQUILLE")
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

        print("ALLEZ ON SE BARRE IL N'Y A RIEN A VOIR")
        return None