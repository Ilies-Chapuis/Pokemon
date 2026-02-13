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
        self.etat = "exploration"  # "exploration", "combat", "menu"
        self.combat_actuel = None
        self.pokemon_sauvage = None

        # Compteur de pas (pour éviter trop de rencontres)
        self.pas_depuis_combat = 0
        self.pas_min_entre_combats = 5

        # Potions
        self.potions = 5

        # État running pour l'application principale
        self.running = True

    def render(self):
        """Affiche le jeu"""
        self.screen.fill((20, 20, 40))

        if self.etat == "exploration":
            self.afficher_carte()
            self.afficher_infos_zone()
            self.afficher_equipe()

            # Instructions
            self.afficher_texte("Déplacement: Flèches ou ZQSD", 50, 650, self.font_petit, (200, 200, 200))
            self.afficher_texte("[H] Soigner l'équipe | [ESC] Menu", 50, 670, self.font_petit, (200, 200, 200))

        elif self.etat == "combat":
            self.afficher_combat()

    def initialiser_equipe(self):
        # Initialise l'équipe de départ du joueur
        # Charger un Pokémon de départ
        starter_data = self.rencontre_manager.pokedex.get("Keunotor")
        if starter_data:
            starter = Pokemon.from_pokedex(starter_data, 5)
            self.equipe_joueur.append(starter)

    def deplacer_joueur(self, dx, dy):
        # Déplace le joueur et vérifie les rencontres
        nouveau_x = self.joueur_x + dx
        nouveau_y = self.joueur_y + dy

        # Vérifier les limites
        if 0 <= nouveau_x < self.carte.largeur and 0 <= nouveau_y < self.carte.hauteur:
            self.joueur_x = nouveau_x
            self.joueur_y = nouveau_y
            self.pas_depuis_combat += 1

            # Vérifier rencontre
            if self.pas_depuis_combat >= self.pas_min_entre_combats:
                zone = self.carte.get_zone(self.joueur_x, self.joueur_y)
                pokemon_rencontre = self.rencontre_manager.verifier_rencontre(
                    zone, (self.joueur_x, self.joueur_y)
                )

                if pokemon_rencontre and self.equipe_joueur:
                    self.demarrer_combat(pokemon_rencontre)
                    self.pas_depuis_combat = 0

    def demarrer_combat(self, pokemon_sauvage):
        # Démarre un combat contre un Pokémon sauvage
        self.etat = "combat"
        self.pokemon_sauvage = pokemon_sauvage
        pokemon_actif = self.get_pokemon_actif()
        if pokemon_actif:
            self.combat_actuel = Combat(pokemon_actif, pokemon_sauvage)

    def get_pokemon_actif(self):
        # Retourne le premier Pokémon vivant de l'équipe
        for pokemon in self.equipe_joueur:
            if pokemon.est_vivant():
                return pokemon
        return None

    def afficher_carte(self):
        # Affiche la carte et le joueur
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

        # Dessiner le joueur
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
        # Affiche les informations de la zone actuelle
        zone_type = self.carte.get_zone(self.joueur_x, self.joueur_y)
        zone_info = ZONES[zone_type]

        y_offset = 50
        self.afficher_texte(f"Zone: {zone_info['nom']}", 850, y_offset, self.font_normal)
        self.afficher_texte(f"Position: ({self.joueur_x}, {self.joueur_y})", 850, y_offset + 30, self.font_petit)
        self.afficher_texte(f"Potions: {self.potions}", 850, y_offset + 60, self.font_petit)

    def afficher_equipe(self):
        # Affiche l'équipe du joueur
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
        # Affiche l'écran de combat
        if not self.combat_actuel:
            return

        # Fond de combat
        pygame.draw.rect(self.screen, (40, 40, 60), (0, 0, self.largeur_ecran, self.hauteur_ecran))

        # Pokémon sauvage
        y_sauvage = 100
        self.afficher_texte(
            f"Pokémon sauvage: {self.pokemon_sauvage.nom} Nv.{self.pokemon_sauvage.niveau}",
            50, y_sauvage, self.font_titre, (255, 100, 100)
        )
        if self.pokemon_sauvage.legendary:
            self.afficher_texte("★ LÉGENDAIRE ★", 50, y_sauvage + 35, self.font_normal, (255, 215, 0))

        self.afficher_barre_pv(self.pokemon_sauvage, 50, y_sauvage + 60, 300)

        # Pokémon du joueur
        pokemon_joueur = self.combat_actuel.pokemon_joueur
        y_joueur = 300
        self.afficher_texte(
            f"Votre {pokemon_joueur.nom} Nv.{pokemon_joueur.niveau}",
            50, y_joueur, self.font_titre, (100, 255, 100)
        )
        self.afficher_barre_pv(pokemon_joueur, 50, y_joueur + 40, 300)

        # Logs de combat
        y_logs = 450
        self.afficher_texte("Combat:", 50, y_logs, self.font_normal)
        logs = self.combat_actuel.get_derniers_logs(4)
        for i, log in enumerate(logs):
            self.afficher_texte(log, 50, y_logs + 30 + i * 25, self.font_petit, (200, 200, 200))

        # Boutons d'action
        if not self.combat_actuel.termine:
            self.afficher_boutons_combat()
        else:
            self.afficher_fin_combat()

    def afficher_boutons_combat(self):
        # Affiche les boutons d'action en combat
        boutons_texte = [
            "[A] Attaquer",
            f"[P] Potion ({self.potions})",
            "[C] Capturer",
            "[F] Fuir"

        ]

        x_boutons = 600
        y_boutons = 500

        for i, texte in enumerate(boutons_texte):
            self.afficher_texte(texte, x_boutons, y_boutons + i * 40, self.font_normal, (255, 255, 100))

    def afficher_fin_combat(self):
        # Affiche le résultat du combat
        if self.combat_actuel.joueur_gagne:
            texte = "VICTOIRE !"
            couleur = (100, 255, 100)
        else:
            texte = "DÉFAITE..."
            couleur = (255, 100, 100)

        self.afficher_texte(texte, 400, 300, self.font_titre, couleur)
        self.afficher_texte("[ESPACE] Continuer", 350, 350, self.font_normal, (255, 255, 255))

    def afficher_barre_pv(self, pokemon, x, y, largeur):
        # Affiche une barre de PV
        ratio_pv = pokemon.pv / pokemon.pv_max if pokemon.pv_max > 0 else 0

        # Couleur selon les PV
        if ratio_pv > 0.5:
            couleur = (100, 255, 100)
        elif ratio_pv > 0.2:
            couleur = (255, 200, 50)
        else:
            couleur = (255, 50, 50)

        # Fond
        pygame.draw.rect(self.screen, (50, 50, 50), (x, y, largeur, 20))
        # Barre
        pygame.draw.rect(self.screen, couleur, (x, y, int(largeur * ratio_pv), 20))
        # Contour
        pygame.draw.rect(self.screen, (255, 255, 255), (x, y, largeur, 20), 2)

        # Texte PV
        texte_pv = f"{pokemon.pv}/{pokemon.pv_max}"
        self.afficher_texte(texte_pv, x + largeur + 10, y, self.font_petit)

    def afficher_texte(self, texte, x, y, font=None, couleur=(255, 255, 255)):
        # Affiche du texte à l'écran
        if font is None:
            font = self.font_normal
        surface = font.render(texte, True, couleur)
        self.screen.blit(surface, (x, y))

    def gerer_input_exploration(self, event):
        # Gère les inputs en mode exploration
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
                # Soigner tous les Pokémon (pour test)
                for pokemon in self.equipe_joueur:
                    pokemon.soigner()

    def gerer_input_combat(self, event):
        # Gère les inputs en mode combat
        if event.type == pygame.KEYDOWN:
            if self.combat_actuel.termine:
                if event.key == pygame.K_SPACE:
                    self.etat = "exploration"
                    self.combat_actuel = None
                    self.pokemon_sauvage = None
            else:
                if event.key == pygame.K_a:
                    # Attaquer
                    self.combat_actuel.tour_combat("attaque")
                elif event.key == pygame.K_p and self.potions > 0:
                    # Utiliser potion
                    self.combat_actuel.utiliser_potion()
                    self.potions -= 1
                elif event.key == pygame.K_f:
                    # Fuir
                    self.combat_actuel.tour_combat("fuite")
                elif event.key == pygame.K_c:
                    self.combat_actuel.tour_combat("capture")
                if self.combat_actuel.pokemon_capture:
                    if len(self.equipe_joueur) < 6:
                        self.equipe_joueur.append(self.pokemon_sauvage)