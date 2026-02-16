#!/usr/bin/env python3
"""
Outil d'ajout de Pokémon personnalisés
Permet de créer et d'ajouter des Pokémon au jeu avec une interface graphique
"""

import pygame
import json
import os
import shutil
from tkinter import Tk, filedialog


class AjoutPokemon:
    def __init__(self):
        pygame.init()

        # Configuration de l'écran
        self.largeur = 1000
        self.hauteur = 700
        self.screen = pygame.display.set_mode((self.largeur, self.hauteur))
        pygame.display.set_caption("Créateur de Pokémon - Pokémon JVSI")

        # Polices
        self.font_titre = pygame.font.SysFont("Arial", 36, bold=True)
        self.font_normal = pygame.font.SysFont("Arial", 20)
        self.font_petit = pygame.font.SysFont("Arial", 16)

        # Clock
        self.clock = pygame.time.Clock()

        # Types disponibles
        self.types_disponibles = [
            "Normal", "Feu", "Eau", "Plante", "Électrik", "Glace",
            "Combat", "Poison", "Sol", "Vol", "Psy", "Insecte",
            "Roche", "Spectre", "Dragon", "Ténèbres", "Acier", "Fée"
        ]

        # État de la création
        self.etape = 0  # 0: nom, 1: types, 2: stats, 3: image, 4: description, 5: confirmation
        self.pokemon_data = {
            "name": "",
            "type": [],
            "stats": {
                "pv": 50,
                "attaque": 50,
                "defense": 50
            },
            "description": "",
            "legendary": False,
            "image_path": None
        }

        # Input
        self.input_text = ""
        self.input_actif = True

        # Sélection de types
        self.type_selection = 0
        self.types_selectionnes = []

        # Image preview
        self.image_preview = None

        # Messages
        self.message = ""
        self.message_couleur = (255, 255, 255)

    def selectionner_image(self):
        """Ouvre un dialogue pour sélectionner une image"""
        root = Tk()
        root.withdraw()
        root.attributes('-topmost', True)

        fichier = filedialog.askopenfilename(
            title="Sélectionner l'image du Pokémon",
            filetypes=[
                ("Images PNG", "*.png"),
                ("Images JPEG", "*.jpg *.jpeg"),
                ("Toutes les images", "*.png *.jpg *.jpeg")
            ]
        )

        root.destroy()

        if fichier:
            try:
                # Charger l'image pour prévisualisation
                self.image_preview = pygame.image.load(fichier)
                self.image_preview = pygame.transform.scale(self.image_preview, (150, 150))
                self.pokemon_data["image_path"] = fichier
                self.message = f"✓ Image sélectionnée : {os.path.basename(fichier)}"
                self.message_couleur = (100, 255, 100)
            except Exception as e:
                self.message = f"✗ Erreur : {e}"
                self.message_couleur = (255, 100, 100)

    def copier_image(self, nom_pokemon):
        """Copie l'image dans le dossier Assets/pokemon/"""
        if not self.pokemon_data["image_path"]:
            return None

        # Créer le dossier si nécessaire
        os.makedirs("Assets/pokemon", exist_ok=True)

        # Nom du fichier de destination
        extension = os.path.splitext(self.pokemon_data["image_path"])[1]
        destination = f"Assets/pokemon/{nom_pokemon}{extension}"

        try:
            shutil.copy(self.pokemon_data["image_path"], destination)
            return destination
        except Exception as e:
            print(f"✗ Erreur lors de la copie de l'image : {e}")
            return None

    def sauvegarder_pokemon(self):
        """Sauvegarde le Pokémon dans pokemon.json et pokedex.json"""
        try:
            # Vérifier que le nom n'est pas vide
            if not self.pokemon_data["name"]:
                self.message = "✗ Le nom est requis !"
                self.message_couleur = (255, 100, 100)
                return False

            # Vérifier qu'au moins un type est sélectionné
            if len(self.types_selectionnes) == 0:
                self.message = "✗ Sélectionnez au moins un type !"
                self.message_couleur = (255, 100, 100)
                return False

            # Copier l'image
            if self.pokemon_data["image_path"]:
                self.copier_image(self.pokemon_data["name"])

            # Créer l'entrée Pokémon
            pokemon_entry = {
                "name": self.pokemon_data["name"],
                "type": self.types_selectionnes,
                "stats": self.pokemon_data["stats"],
                "legendary": self.pokemon_data["legendary"]
            }

            # Charger pokemon.json
            with open("pokemon.json", "r", encoding="utf-8") as f:
                data = json.load(f)

            # Vérifier si le Pokémon existe déjà
            existe = False
            for i, p in enumerate(data["pokemon"]):
                if p["name"] == self.pokemon_data["name"]:
                    data["pokemon"][i] = pokemon_entry
                    existe = True
                    break

            if not existe:
                data["pokemon"].append(pokemon_entry)

            # Sauvegarder pokemon.json
            with open("pokemon.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            # Créer/mettre à jour pokedex.json
            pokedex_entry = {
                "name": self.pokemon_data["name"],
                "type": self.types_selectionnes,
                "stats": self.pokemon_data["stats"],
                "description": self.pokemon_data["description"],
                "legendary": self.pokemon_data["legendary"]
            }

            # Charger ou créer pokedex.json
            if os.path.exists("pokedex.json"):
                with open("pokedex.json", "r", encoding="utf-8") as f:
                    pokedex_data = json.load(f)
            else:
                pokedex_data = {"pokemon": []}

            # Vérifier si existe dans le pokédex
            existe_pokedex = False
            for i, p in enumerate(pokedex_data.get("pokemon", [])):
                if p["name"] == self.pokemon_data["name"]:
                    pokedex_data["pokemon"][i] = pokedex_entry
                    existe_pokedex = True
                    break

            if not existe_pokedex:
                if "pokemon" not in pokedex_data:
                    pokedex_data["pokemon"] = []
                pokedex_data["pokemon"].append(pokedex_entry)

            # Sauvegarder pokedex.json
            with open("pokedex.json", "w", encoding="utf-8") as f:
                json.dump(pokedex_data, f, indent=2, ensure_ascii=False)

            self.message = f"✓ {self.pokemon_data['name']} ajouté avec succès !"
            self.message_couleur = (100, 255, 100)
            return True

        except Exception as e:
            self.message = f"✗ Erreur : {e}"
            self.message_couleur = (255, 100, 100)
            import traceback
            traceback.print_exc()
            return False

    def afficher_etape_nom(self):
        """Étape 1 : Saisir le nom"""
        y = 150

        titre = self.font_titre.render("Nom du Pokémon", True, (255, 215, 0))
        titre_rect = titre.get_rect(center=(self.largeur // 2, y))
        self.screen.blit(titre, titre_rect)

        y += 80

        # Champ de saisie
        pygame.draw.rect(self.screen, (255, 255, 255), (300, y, 400, 50), 2)
        texte = self.font_normal.render(self.input_text + "_", True, (255, 255, 255))
        self.screen.blit(texte, (310, y + 10))

        # Instructions
        y += 100
        instructions = [
            "Entrez le nom de votre Pokémon",
            "Appuyez sur ENTRÉE pour continuer",
            "ESC pour annuler"
        ]
        for instruction in instructions:
            txt = self.font_petit.render(instruction, True, (200, 200, 200))
            txt_rect = txt.get_rect(center=(self.largeur // 2, y))
            self.screen.blit(txt, txt_rect)
            y += 30

    def afficher_etape_types(self):
        """Étape 2 : Sélectionner les types"""
        y = 100

        titre = self.font_titre.render("Types du Pokémon", True, (255, 215, 0))
        titre_rect = titre.get_rect(center=(self.largeur // 2, y))
        self.screen.blit(titre, titre_rect)

        y += 60

        # Types sélectionnés
        if self.types_selectionnes:
            selected = self.font_normal.render(f"Sélectionnés : {' / '.join(self.types_selectionnes)}", True,
                                               (100, 255, 100))
            selected_rect = selected.get_rect(center=(self.largeur // 2, y))
            self.screen.blit(selected, selected_rect)

        y += 50

        # Grille de types
        x_start = 150
        y_start = y
        col_width = 150
        row_height = 40
        cols = 4

        for i, type_name in enumerate(self.types_disponibles):
            row = i // cols
            col = i % cols
            x = x_start + col * col_width
            y = y_start + row * row_height

            # Couleur
            if i == self.type_selection:
                couleur = (255, 215, 0)
                pygame.draw.rect(self.screen, couleur, (x - 5, y - 5, col_width - 10, row_height - 10), 2)
            elif type_name in self.types_selectionnes:
                couleur = (100, 255, 100)
            else:
                couleur = (200, 200, 200)

            txt = self.font_petit.render(type_name, True, couleur)
            self.screen.blit(txt, (x, y))

        # Instructions
        y = y_start + ((len(self.types_disponibles) // cols) + 1) * row_height + 20
        instructions = [
            "Flèches : Naviguer | ESPACE : Sélectionner/Désélectionner",
            "Max 2 types | ENTRÉE : Continuer | ESC : Retour"
        ]
        for instruction in instructions:
            txt = self.font_petit.render(instruction, True, (200, 200, 200))
            txt_rect = txt.get_rect(center=(self.largeur // 2, y))
            self.screen.blit(txt, txt_rect)
            y += 25

    def afficher_etape_stats(self):
        """Étape 3 : Définir les stats"""
        y = 100

        titre = self.font_titre.render("Statistiques", True, (255, 215, 0))
        titre_rect = titre.get_rect(center=(self.largeur // 2, y))
        self.screen.blit(titre, titre_rect)

        y += 80

        stats = ["pv", "attaque", "defense"]
        for i, stat in enumerate(stats):
            # Nom de la stat
            nom = stat.upper() if stat != "pv" else "PV"
            txt_nom = self.font_normal.render(f"{nom}:", True, (255, 255, 255))
            self.screen.blit(txt_nom, (200, y))

            # Valeur
            valeur = self.pokemon_data["stats"][stat]
            txt_val = self.font_normal.render(str(valeur), True, (100, 255, 100))
            self.screen.blit(txt_val, (350, y))

            # Barre
            barre_width = 300
            barre_fill = int((valeur / 200) * barre_width)
            pygame.draw.rect(self.screen, (100, 100, 100), (450, y + 5, barre_width, 20))
            pygame.draw.rect(self.screen, (100, 255, 100), (450, y + 5, barre_fill, 20))

            y += 60

        # Instructions
        y += 40
        instructions = [
            "Utilisez les chiffres 1-3 pour sélectionner la stat",
            "Flèches HAUT/BAS pour ajuster (+/- 5)",
            "Flèches GAUCHE/DROITE pour ajuster (+/- 1)",
            "ENTRÉE : Continuer | ESC : Retour"
        ]
        for instruction in instructions:
            txt = self.font_petit.render(instruction, True, (200, 200, 200))
            txt_rect = txt.get_rect(center=(self.largeur // 2, y))
            self.screen.blit(txt, txt_rect)
            y += 25

    def afficher_etape_image(self):
        """Étape 4 : Sélectionner l'image"""
        y = 100

        titre = self.font_titre.render("Image du Pokémon", True, (255, 215, 0))
        titre_rect = titre.get_rect(center=(self.largeur // 2, y))
        self.screen.blit(titre, titre_rect)

        y += 80

        # Preview de l'image
        if self.image_preview:
            img_rect = self.image_preview.get_rect(center=(self.largeur // 2, y + 100))
            self.screen.blit(self.image_preview, img_rect)
            y += 220
        else:
            placeholder = self.font_normal.render("Aucune image sélectionnée", True, (150, 150, 150))
            placeholder_rect = placeholder.get_rect(center=(self.largeur // 2, y + 100))
            self.screen.blit(placeholder, placeholder_rect)
            y += 150

        # Instructions
        instructions = [
            "Appuyez sur I pour sélectionner une image",
            "Format recommandé : PNG 128x128 pixels",
            "ENTRÉE : Continuer (optionnel) | ESC : Retour"
        ]
        for instruction in instructions:
            txt = self.font_petit.render(instruction, True, (200, 200, 200))
            txt_rect = txt.get_rect(center=(self.largeur // 2, y))
            self.screen.blit(txt, txt_rect)
            y += 25

    def afficher_etape_description(self):
        """Étape 5 : Ajouter une description"""
        y = 150

        titre = self.font_titre.render("Description", True, (255, 215, 0))
        titre_rect = titre.get_rect(center=(self.largeur // 2, y))
        self.screen.blit(titre, titre_rect)

        y += 80

        # Champ de saisie multiligne
        pygame.draw.rect(self.screen, (255, 255, 255), (150, y, 700, 100), 2)

        # Afficher le texte (avec retour à la ligne si trop long)
        mots = self.input_text.split(' ')
        ligne = ""
        y_text = y + 10
        for mot in mots:
            test = ligne + mot + " "
            if self.font_petit.size(test)[0] < 680:
                ligne = test
            else:
                txt = self.font_petit.render(ligne, True, (255, 255, 255))
                self.screen.blit(txt, (160, y_text))
                ligne = mot + " "
                y_text += 25

        # Dernière ligne
        if ligne:
            txt = self.font_petit.render(ligne + "_", True, (255, 255, 255))
            self.screen.blit(txt, (160, y_text))

        y += 150

        # Checkbox légendaire
        checkbox_x = 300
        checkbox_y = y
        pygame.draw.rect(self.screen, (255, 255, 255), (checkbox_x, checkbox_y, 30, 30), 2)
        if self.pokemon_data["legendary"]:
            pygame.draw.line(self.screen, (255, 215, 0), (checkbox_x + 5, checkbox_y + 15),
                             (checkbox_x + 12, checkbox_y + 25), 3)
            pygame.draw.line(self.screen, (255, 215, 0), (checkbox_x + 12, checkbox_y + 25),
                             (checkbox_x + 25, checkbox_y + 5), 3)

        txt_leg = self.font_normal.render("Pokémon Légendaire", True, (255, 215, 0))
        self.screen.blit(txt_leg, (checkbox_x + 40, checkbox_y))

        # Instructions
        y += 60
        instructions = [
            "Entrez une description (optionnel)",
            "X : Toggle Légendaire",
            "ENTRÉE : Continuer | ESC : Retour"
        ]
        for instruction in instructions:
            txt = self.font_petit.render(instruction, True, (200, 200, 200))
            txt_rect = txt.get_rect(center=(self.largeur // 2, y))
            self.screen.blit(txt, txt_rect)
            y += 25

    def afficher_etape_confirmation(self):
        """Étape 6 : Confirmation et sauvegarde"""
        y = 80

        titre = self.font_titre.render("Confirmation", True, (255, 215, 0))
        titre_rect = titre.get_rect(center=(self.largeur // 2, y))
        self.screen.blit(titre, titre_rect)

        y += 60

        # Résumé
        info_lines = [
            f"Nom : {self.pokemon_data['name']}",
            f"Type(s) : {' / '.join(self.types_selectionnes)}",
            f"PV : {self.pokemon_data['stats']['pv']}",
            f"Attaque : {self.pokemon_data['stats']['attaque']}",
            f"Défense : {self.pokemon_data['stats']['defense']}",
            f"Légendaire : {'Oui' if self.pokemon_data['legendary'] else 'Non'}",
        ]

        if self.pokemon_data["image_path"]:
            info_lines.append(f"Image : {os.path.basename(self.pokemon_data['image_path'])}")

        if self.pokemon_data["description"]:
            info_lines.append(f"Description : {self.pokemon_data['description'][:50]}...")

        for line in info_lines:
            txt = self.font_normal.render(line, True, (255, 255, 255))
            txt_rect = txt.get_rect(center=(self.largeur // 2, y))
            self.screen.blit(txt, txt_rect)
            y += 35

        # Preview image
        if self.image_preview:
            img_rect = self.image_preview.get_rect(center=(self.largeur // 2, y + 80))
            self.screen.blit(self.image_preview, img_rect)
            y += 180

        y += 20

        # Instructions
        instructions = [
            "S : Sauvegarder et ajouter au jeu",
            "ESC : Retour pour modifier"
        ]
        for instruction in instructions:
            txt = self.font_normal.render(instruction, True, (100, 255, 100))
            txt_rect = txt.get_rect(center=(self.largeur // 2, y))
            self.screen.blit(txt, txt_rect)
            y += 30

    def afficher(self):
        """Affiche l'interface"""
        self.screen.fill((30, 30, 50))

        # Afficher l'étape actuelle
        if self.etape == 0:
            self.afficher_etape_nom()
        elif self.etape == 1:
            self.afficher_etape_types()
        elif self.etape == 2:
            self.afficher_etape_stats()
        elif self.etape == 3:
            self.afficher_etape_image()
        elif self.etape == 4:
            self.afficher_etape_description()
        elif self.etape == 5:
            self.afficher_etape_confirmation()

        # Message en bas
        if self.message:
            msg = self.font_normal.render(self.message, True, self.message_couleur)
            msg_rect = msg.get_rect(center=(self.largeur // 2, self.hauteur - 30))
            self.screen.blit(msg, msg_rect)

        # Indicateur d'étape
        etape_txt = self.font_petit.render(f"Étape {self.etape + 1}/6", True, (150, 150, 150))
        self.screen.blit(etape_txt, (10, 10))

    def gerer_input(self, event):
        """Gère les inputs"""
        if event.type == pygame.KEYDOWN:
            # Étape 0 : Nom
            if self.etape == 0:
                if event.key == pygame.K_RETURN and self.input_text:
                    self.pokemon_data["name"] = self.input_text
                    self.input_text = ""
                    self.etape = 1
                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                elif event.key == pygame.K_ESCAPE:
                    return False
                elif event.unicode.isprintable() and len(self.input_text) < 20:
                    self.input_text += event.unicode

            # Étape 1 : Types
            elif self.etape == 1:
                if event.key == pygame.K_UP:
                    self.type_selection = max(0, self.type_selection - 4)
                elif event.key == pygame.K_DOWN:
                    self.type_selection = min(len(self.types_disponibles) - 1, self.type_selection + 4)
                elif event.key == pygame.K_LEFT:
                    self.type_selection = max(0, self.type_selection - 1)
                elif event.key == pygame.K_RIGHT:
                    self.type_selection = min(len(self.types_disponibles) - 1, self.type_selection + 1)
                elif event.key == pygame.K_SPACE:
                    type_name = self.types_disponibles[self.type_selection]
                    if type_name in self.types_selectionnes:
                        self.types_selectionnes.remove(type_name)
                    elif len(self.types_selectionnes) < 2:
                        self.types_selectionnes.append(type_name)
                    else:
                        self.message = "Maximum 2 types !"
                        self.message_couleur = (255, 150, 0)
                elif event.key == pygame.K_RETURN and len(self.types_selectionnes) > 0:
                    self.etape = 2
                elif event.key == pygame.K_ESCAPE:
                    self.etape = 0
                    self.input_text = self.pokemon_data["name"]

            # Étape 2 : Stats
            elif self.etape == 2:
                stat_keys = ["pv", "attaque", "defense"]

                if event.key == pygame.K_1:
                    self.message = "PV sélectionné (↑↓ pour ajuster)"
                elif event.key == pygame.K_2:
                    self.message = "Attaque sélectionnée (↑↓ pour ajuster)"
                elif event.key == pygame.K_3:
                    self.message = "Défense sélectionnée (↑↓ pour ajuster)"
                elif event.key == pygame.K_UP:
                    for stat in stat_keys:
                        self.pokemon_data["stats"][stat] = min(200, self.pokemon_data["stats"][stat] + 5)
                elif event.key == pygame.K_DOWN:
                    for stat in stat_keys:
                        self.pokemon_data["stats"][stat] = max(10, self.pokemon_data["stats"][stat] - 5)
                elif event.key == pygame.K_RIGHT:
                    for stat in stat_keys:
                        self.pokemon_data["stats"][stat] = min(200, self.pokemon_data["stats"][stat] + 1)
                elif event.key == pygame.K_LEFT:
                    for stat in stat_keys:
                        self.pokemon_data["stats"][stat] = max(10, self.pokemon_data["stats"][stat] - 1)
                elif event.key == pygame.K_RETURN:
                    self.etape = 3
                elif event.key == pygame.K_ESCAPE:
                    self.etape = 1

            # Étape 3 : Image
            elif self.etape == 3:
                if event.key == pygame.K_i:
                    self.selectionner_image()
                elif event.key == pygame.K_RETURN:
                    self.etape = 4
                elif event.key == pygame.K_ESCAPE:
                    self.etape = 2

            # Étape 4 : Description
            elif self.etape == 4:
                if event.key == pygame.K_RETURN:
                    self.pokemon_data["description"] = self.input_text
                    self.input_text = ""
                    self.etape = 5
                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                elif event.key == pygame.K_X:
                    self.pokemon_data["legendary"] = not self.pokemon_data["legendary"]
                elif event.key == pygame.K_ESCAPE:
                    self.etape = 3
                elif event.unicode.isprintable() and len(self.input_text) < 200:
                    self.input_text += event.unicode

            # Étape 5 : Confirmation
            elif self.etape == 5:
                if event.key == pygame.K_s:
                    if self.sauvegarder_pokemon():
                        # Réinitialiser pour un nouveau Pokémon
                        self.etape = 0
                        self.pokemon_data = {
                            "name": "",
                            "type": [],
                            "stats": {"pv": 50, "attaque": 50, "defense": 50},
                            "description": "",
                            "legendary": False,
                            "image_path": None
                        }
                        self.types_selectionnes = []
                        self.image_preview = None
                elif event.key == pygame.K_ESCAPE:
                    self.etape = 4
                    self.input_text = self.pokemon_data["description"]

        return True

    def run(self):
        """Boucle principale"""
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    running = self.gerer_input(event)

            self.afficher()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


def main():
    """Point d'entrée"""
    print("=" * 50)
    print("  CRÉATEUR DE POKÉMON - POKÉMON FRAUDE")
    print("=" * 50)
    print()

    app = AjoutPokemon()
    app.run()


