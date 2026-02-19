#!/usr/bin/env python3
"""
Pokémon JVSI - Édition Aventure
Point d'entrée principal du jeu
"""

import pygame
import sys
import os
import json

# Imports locaux
from pokemon import Pokemon


class Menu:
    """Menu principal du jeu"""

    def __init__(self, screen, font_titre, font_normal):
        self.screen = screen
        self.font_titre = font_titre
        self.font_normal = font_normal
        self.font_petit = pygame.font.SysFont("Arial", 16)

        self.options = [
            "Nouvelle partie",
            "Continuer",
            "Créateur de Pokémon",
            "Pokédex",
            "Options",
            "Quitter"
        ]
        self.selection = 0

    def afficher(self):
        """Affiche le menu principal"""
        self.screen.fill((20, 20, 40))

        # Titre
        titre = self.font_titre.render("POKÉMON JVSI", True, (255, 215, 0))
        titre_rect = titre.get_rect(center=(500, 150))
        self.screen.blit(titre, titre_rect)

        # Sous-titre
        sous_titre = self.font_normal.render("Édition Aventure", True, (200, 200, 200))
        sous_titre_rect = sous_titre.get_rect(center=(500, 200))
        self.screen.blit(sous_titre, sous_titre_rect)

        # Options
        y_start = 300
        for i, option in enumerate(self.options):
            couleur = (100, 255, 100) if i == self.selection else (255, 255, 255)
            texte = self.font_normal.render(option, True, couleur)
            texte_rect = texte.get_rect(center=(500, y_start + i * 60))
            self.screen.blit(texte, texte_rect)

            if i == self.selection:
                indicateur = self.font_normal.render(">", True, (100, 255, 100))
                self.screen.blit(indicateur, (texte_rect.left - 40, texte_rect.top))

        # Instructions
        instructions = [
            "Utilisez les flèches HAUT/BAS pour naviguer",
            "Appuyez sur ENTRÉE pour sélectionner"
        ]
        y_instructions = 600
        for i, instruction in enumerate(instructions):
            texte = self.font_petit.render(instruction, True, (150, 150, 150))
            texte_rect = texte.get_rect(center=(500, y_instructions + i * 25))
            self.screen.blit(texte, texte_rect)

    def naviguer(self, direction):
        """Change la sélection du menu"""
        self.selection = (self.selection + direction) % len(self.options)

    def obtenir_choix(self):
        """Retourne l'option sélectionnée"""
        return self.options[self.selection]


class MenuOptions:
    """Menu des options"""

    def __init__(self, screen, font_titre, font_normal):
        self.screen = screen
        self.font_titre = font_titre
        self.font_normal = font_normal
        self.font_petit = pygame.font.SysFont("Arial", 16)

        self.parametres = {
            "volume_musique": 50,
            "volume_effets": 70,
            "difficulte": "Normal",
            "animations": True
        }

        self.options = list(self.parametres.keys()) + ["Retour"]
        self.selection = 0

    def afficher(self):
        """Affiche le menu des options"""
        self.screen.fill((20, 20, 40))

        # Titre
        titre = self.font_titre.render("OPTIONS", True, (255, 215, 0))
        titre_rect = titre.get_rect(center=(500, 100))
        self.screen.blit(titre, titre_rect)

        # Options
        y_start = 200
        for i, option in enumerate(self.options):
            couleur = (100, 255, 100) if i == self.selection else (255, 255, 255)

            if option == "Retour":
                texte = self.font_normal.render("< Retour au menu", True, couleur)
                texte_rect = texte.get_rect(center=(500, y_start + i * 70))
                self.screen.blit(texte, texte_rect)
            else:
                # Nom du paramètre
                nom = option.replace("_", " ").title()
                texte_nom = self.font_normal.render(f"{nom}:", True, couleur)
                self.screen.blit(texte_nom, (250, y_start + i * 70))

                # Valeur
                valeur = str(self.parametres[option])
                if isinstance(self.parametres[option], bool):
                    valeur = "Activé" if self.parametres[option] else "Désactivé"
                elif option in ["volume_musique", "volume_effets"]:
                    valeur = f"{valeur}%"

                texte_valeur = self.font_normal.render(valeur, True, (200, 200, 200))
                self.screen.blit(texte_valeur, (550, y_start + i * 70))

        # Instructions
        instructions = [
            "HAUT/BAS: Naviguer",
            "GAUCHE/DROITE: Modifier",
            "ENTRÉE: Retour"
        ]
        y_instructions = 550
        for i, instruction in enumerate(instructions):
            texte = self.font_petit.render(instruction, True, (150, 150, 150))
            self.screen.blit(texte, (50, y_instructions + i * 25))

    def naviguer(self, direction):
        self.selection = (self.selection + direction) % len(self.options)

    def modifier(self, direction):
        if self.selection >= len(self.parametres):
            return

        option = self.options[self.selection]

        if option == "volume_musique" or option == "volume_effets":
            self.parametres[option] = max(0, min(100, self.parametres[option] + direction * 10))
        elif option == "difficulte":
            difficultes = ["Facile", "Normal", "Difficile"]
            idx = difficultes.index(self.parametres[option])
            idx = (idx + direction) % len(difficultes)
            self.parametres[option] = difficultes[idx]
        elif option == "animations":
            self.parametres[option] = not self.parametres[option]


class MenuStarter:
    """Menu de choix du Pokémon de départ"""

    def __init__(self, screen, font_titre, font_normal, pokedex):
        self.screen = screen
        self.font_titre = font_titre
        self.font_normal = font_normal
        self.font_petit = pygame.font.SysFont("Arial", 16)
        self.pokedex = pokedex

        self.starters = ["Keunotor", "Timiki", "Rubycire"]
        self.selection = 0
        self.images_cache = {}

    def charger_image_pokemon(self, nom_pokemon):
        """Charge l'image d'un Pokémon"""
        if nom_pokemon in self.images_cache:
            return self.images_cache[nom_pokemon]

        chemins_possibles = [
            f"Assets/pokemon/{nom_pokemon}.png",
            f"Assets/pokemon/{nom_pokemon.lower()}.png",
            f"assets/pokemon/{nom_pokemon}.png",
            f"pokemon/{nom_pokemon}.png"
        ]

        for chemin in chemins_possibles:
            try:
                if os.path.exists(chemin):
                    img = pygame.image.load(chemin)
                    img = pygame.transform.scale(img, (100, 100))
                    self.images_cache[nom_pokemon] = img
                    print(f"✓ Starter image chargée: {chemin}")
                    return img
            except Exception as e:
                continue

        print(f"⚠ Aucune image trouvée pour starter {nom_pokemon}")
        return None

    def afficher(self):
        """Affiche l'écran de choix du Pokémon de départ"""
        self.screen.fill((20, 20, 40))

        # Titre
        titre = self.font_titre.render("CHOISIS TON POKÉMON", True, (255, 215, 0))
        titre_rect = titre.get_rect(center=(500, 80))
        self.screen.blit(titre, titre_rect)

        # Afficher les 3 starters
        x_start = 200
        spacing = 200

        for i, starter_nom in enumerate(self.starters):
            x = x_start + i * spacing
            y = 250

            # Cadre
            couleur_cadre = (100, 255, 100) if i == self.selection else (100, 100, 100)
            pygame.draw.rect(self.screen, couleur_cadre, (x - 70, y - 70, 140, 220), 3)

            if starter_nom in self.pokedex:
                pokemon_data = self.pokedex[starter_nom]

                # Essayer de charger l'image
                img = self.charger_image_pokemon(starter_nom)
                if img:
                    img_rect = img.get_rect(center=(x, y))
                    self.screen.blit(img, img_rect)
                else:
                    # Cercle de secours
                    couleur_type = self._get_couleur_type(pokemon_data["type"][0])
                    pygame.draw.circle(self.screen, couleur_type, (x, y), 50)

                # Nom
                nom = self.font_normal.render(starter_nom, True, (255, 255, 255))
                nom_rect = nom.get_rect(center=(x, y + 90))
                self.screen.blit(nom, nom_rect)

                # Types
                types_text = " / ".join(pokemon_data["type"])
                types = self.font_petit.render(types_text, True, (200, 200, 200))
                types_rect = types.get_rect(center=(x, y + 115))
                self.screen.blit(types, types_rect)

                # Stats
                stats_text = f"PV:{pokemon_data['stats']['pv']} ATK:{pokemon_data['stats']['attaque']}"
                stats = self.font_petit.render(stats_text, True, (150, 150, 150))
                stats_rect = stats.get_rect(center=(x, y + 135))
                self.screen.blit(stats, stats_rect)

        # Instructions
        instructions = [
            "GAUCHE/DROITE: Choisir",
            "ENTRÉE: Confirmer"
        ]
        y_instructions = 550
        for i, instruction in enumerate(instructions):
            texte = self.font_petit.render(instruction, True, (150, 150, 150))
            texte_rect = texte.get_rect(center=(500, y_instructions + i * 25))
            self.screen.blit(texte, texte_rect)

    def _get_couleur_type(self, type_name):
        #Retourne une couleur en fonction du type
        couleurs = {
            "Feu": (255, 100, 50),
            "Eau": (50, 150, 255),
            "Plante": (100, 200, 100),
            "Électrik": (255, 220, 50),
            "Normal": (168, 168, 120),
            "Roche": (150, 100, 50)
        }
        return couleurs.get(type_name, (150, 150, 150))

    def naviguer(self, direction):
        self.selection = (self.selection + direction) % len(self.starters)

    def obtenir_choix(self):
        return self.starters[self.selection]


class Application:
    def __init__(self):
        #Initialise l'application
        pygame.init()

        # Configuration de l'écran
        self.largeur_ecran = 1000
        self.hauteur_ecran = 700
        self.screen = pygame.display.set_mode((self.largeur_ecran, self.hauteur_ecran))
        pygame.display.set_caption("Pokémon FRAUDE - Édition FRAUDE")

        # Polices
        self.font_titre = pygame.font.SysFont("Arial", 48, bold=True)
        self.font_normal = pygame.font.SysFont("Arial", 24)
        self.font_petit = pygame.font.SysFont("Arial", 16)

        # Clock
        self.clock = pygame.time.Clock()

        # Charger le Pokédex
        self.charger_pokedex()

        # État de l'application
        self.etat = "menu_principal"
        self.game = None
        self.pokemon_starter = None

        # Menus
        self.menu_principal = Menu(self.screen, self.font_titre, self.font_normal)
        self.menu_options = MenuOptions(self.screen, self.font_titre, self.font_normal)
        self.menu_starter = None

    def charger_pokedex(self):
        """Charge le Pokédex depuis le fichier JSON"""
        try:
            chemin_json = "pokemon.json"
            if not os.path.exists(chemin_json):
                chemin_json = "/mnt/user-data/outputs/pokemon.json"

            with open(chemin_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.pokedex = {p["name"]: p for p in data["pokemon"]}
                print(f" Pokédex chargé: {len(self.pokedex)} Pokémon")
        except Exception as e:
            print(f" Erreur lors du chargement du Pokédex: {e}")
            self.pokedex = {}

    def nouvelle_partie(self):
        """Démarre une nouvelle partie"""
        self.etat = "choix_starter"
        self.menu_starter = MenuStarter(self.screen, self.font_titre, self.font_normal, self.pokedex)

    def continuer_partie(self):
        #Continue une partie sauvegardée
        try:
            from game import Game
            from save_manager import SaveManager

            save_manager = SaveManager()

            # Vérifier si une sauvegarde existe
            if not save_manager.existe_sauvegarde():
                print(" Aucune sauvegarde trouvée. Démarrage d'une nouvelle partie...")
                self.nouvelle_partie()
                return

            # Charger les données
            save_data = save_manager.charger()
            if not save_data:
                print(" Impossible de charger la sauvegarde. Démarrage d'une nouvelle partie...")
                self.nouvelle_partie()
                return

            # Créer le jeu
            self.game = Game()

            # Charger l'état sauvegardé
            if self.game.charger_partie(save_data):
                self.etat = "jeu"
                print(f" Partie chargée : {save_data['date']}")
            else:
                print(" Erreur lors du chargement. Démarrage d'une nouvelle partie...")
                self.nouvelle_partie()

        except Exception as e:
            print(f" Erreur : {e}")
            import traceback
            traceback.print_exc()
            self.nouvelle_partie()

    def lancer_createur_pokemon(self):
        #Lance le créateur de Pokémon"
        try:
            print("\n🎨 Lancement du Créateur de Pokémon...\n")

            # Fermer la fenêtre actuelle
            pygame.quit()

            # Importer et lancer le créateur
            from ajout import AjoutPokemon
            createur = AjoutPokemon()
            createur.run()

            # Réinitialiser pygame et retourner au menu
            pygame.init()
            self.screen = pygame.display.set_mode((self.largeur_ecran, self.hauteur_ecran))
            pygame.display.set_caption("Pokémon JVSI - Édition Aventure")
            self.etat = "menu_principal"

        except Exception as e:
            print(f"✗ Erreur lors du lancement du créateur : {e}")
            import traceback
            traceback.print_exc()

            # Réinitialiser pygame en cas d'erreur
            pygame.init()
            self.screen = pygame.display.set_mode((self.largeur_ecran, self.hauteur_ecran))
            pygame.display.set_caption("Pokémon JVSI - Édition Aventure")
            self.etat = "menu_principal"

    def lancer_jeu(self, pokemon_starter_nom):
        #Lance le jeu avec le Pokémon de départ choisi
        try:
            from game import Game
            self.game = Game()

            # Remplacer le starter
            if pokemon_starter_nom in self.pokedex:
                starter_data = self.pokedex[pokemon_starter_nom]
                starter = Pokemon.from_pokedex(starter_data, 5)
                self.game.equipe_joueur = [starter]
                print(f"✓ Partie lancée avec {pokemon_starter_nom}")

            self.etat = "jeu"
        except Exception as e:
            print(f"✗ Erreur lors du lancement du jeu: {e}")
            import traceback
            traceback.print_exc()
            self.etat = "menu_principal"

    def gerer_menu_principal(self, event):
        #Gère les événements du menu principal
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.menu_principal.naviguer(-1)
            elif event.key == pygame.K_DOWN:
                self.menu_principal.naviguer(1)
            elif event.key == pygame.K_RETURN:
                choix = self.menu_principal.obtenir_choix()

                if choix == "Nouvelle partie":
                    self.nouvelle_partie()
                elif choix == "Continuer":
                    self.continuer_partie()
                elif choix == "Créateur de Pokémon":
                    self.lancer_createur_pokemon()
                elif choix == "Pokédex":
                    self.afficher_pokedex_menu()
                elif choix == "Options":
                    self.etat = "options"
                elif choix == "Quitter":
                    return False

        return True

    def gerer_menu_options(self, event):
        #Gère les événements du menu des options
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.menu_options.naviguer(-1)
            elif event.key == pygame.K_DOWN:
                self.menu_options.naviguer(1)
            elif event.key == pygame.K_LEFT:
                self.menu_options.modifier(-1)
            elif event.key == pygame.K_RIGHT:
                self.menu_options.modifier(1)
            elif event.key == pygame.K_RETURN:
                if self.menu_options.selection >= len(self.menu_options.parametres):
                    self.etat = "menu_principal"
            elif event.key == pygame.K_ESCAPE:
                self.etat = "menu_principal"

        return True

    def gerer_choix_starter(self, event):
        #Gère les événements du choix du Pokémon de départ
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.menu_starter.naviguer(-1)
            elif event.key == pygame.K_RIGHT:
                self.menu_starter.naviguer(1)
            elif event.key == pygame.K_RETURN:
                pokemon_choisi = self.menu_starter.obtenir_choix()
                self.lancer_jeu(pokemon_choisi)
            elif event.key == pygame.K_ESCAPE:
                self.etat = "menu_principal"

        return True

    def afficher_pokedex_menu(self):
        #Affiche le Pokédex depuis le menu (sans partie en cours)"""
        from Pokedex_manager import PokedexManager
        from game import Game

        # Créer un Pokédex temporaire
        pokedex_temp = PokedexManager()
        stats = pokedex_temp.obtenir_stats()

        # Charger la liste complète
        with open("pokemon.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            total = len(data["pokemon"])

        completion = pokedex_temp.obtenir_completion(total)

        print("\n" + "=" * 50)
        print(f"  POKÉDEX")
        print("=" * 50)
        print(f"  Vus: {stats['vus']}/{total}")
        print(f"  Capturés: {stats['captures']}/{total}")
        print(f"  Complétion: {completion:.1f}%")
        print("=" * 50)
        print("\n[ESC] Retour au menu")

        # Créer une instance Game pour l'affichage graphique du Pokédex
        if not hasattr(self, '_game_pokedex') or self._game_pokedex is None:
            self._game_pokedex = Game()
        self._game_pokedex.selection_pokedex = 0
        self.etat = "pokedex_menu"

    def run(self):
        """Boucle principale de l'application"""
        running = True

        while running:
            # Gestion des événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # Dispatch des événements selon l'état
                if self.etat == "menu_principal":
                    running = self.gerer_menu_principal(event)
                elif self.etat == "options":
                    running = self.gerer_menu_options(event)
                elif self.etat == "choix_starter":
                    running = self.gerer_choix_starter(event)
                elif self.etat == "pokedex_menu":
                    if event.type == pygame.KEYDOWN:
                        with open("pokemon.json", "r", encoding="utf-8") as pf:
                            total_poke = len(json.load(pf)["pokemon"])
                        if event.key == pygame.K_UP:
                            self._game_pokedex.selection_pokedex = max(0, self._game_pokedex.selection_pokedex - 1)
                        elif event.key == pygame.K_DOWN:
                            self._game_pokedex.selection_pokedex = min(total_poke - 1, self._game_pokedex.selection_pokedex + 1)
                        elif event.key == pygame.K_ESCAPE:
                            print(" Retour au menu principal")
                            self.etat = "menu_principal"
                elif self.etat == "jeu":
                    if self.game:
                        if self.game.etat == "exploration":
                            # ESC depuis l'exploration = retour menu principal
                            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                                self.etat = "menu_principal"
                                self.game = None
                            else:
                                self.game.gerer_input_exploration(event)
                        elif self.game.etat == "combat":
                            self.game.gerer_input_combat(event)
                        elif self.game.etat == "menu_equipe":
                            self.game.gerer_input_menu_equipe(event)
                        elif self.game.etat == "menu_reserve":
                            self.game.gerer_input_menu_reserve(event)
                        elif self.game.etat == "pokedex":
                            self.game.gerer_input_pokedex(event)
                        elif self.game.etat == "evolution":
                            self.game.gerer_input_evolution(event)
            # Affichage selon l'état
            if self.etat == "menu_principal":
                self.menu_principal.afficher()
            elif self.etat == "options":
                self.menu_options.afficher()
            elif self.etat == "choix_starter":
                self.menu_starter.afficher()
            elif self.etat == "pokedex_menu":
                self._game_pokedex.screen = self.screen
                self._game_pokedex.afficher_pokedex()
            elif self.etat == "jeu":
                if self.game:
                    self.game.render()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


def main():
    """Point d'entrée principal"""
    print("=" * 50)
    print("  POKÉMON FRAUDE - ÉDITION FRAUDE")
    print("=" * 50)
    print()

    try:
        app = Application()
        app.run()
    except Exception as e:
        print(f"\n✗ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()