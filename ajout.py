#!/usr/bin/env python3
"""
Outil d'ajout de Pokémon personnalisés
"""
import pygame
import json
import os
import shutil




def _chemin_json():
    #Retourne le chemin absolu vers pokemon.json
    import os
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "Data", "pokemon.json")


class FileBrowser:
    #Explorateur de fichiers natif pygame"""

    def __init__(self, screen, font_normal, font_petit, font_titre,
                 extensions=(".png", ".jpg", ".jpeg")):
        self.screen = screen
        self.font_normal = font_normal
        self.font_petit = font_petit
        self.font_titre = font_titre
        self.extensions = extensions
        self.largeur = screen.get_width()
        self.hauteur = screen.get_height()

        home = os.path.expanduser("~")
        self.dossier_actuel = home if os.path.isdir(home) else os.path.abspath("/")
        self.entrees = []
        self.selection = 0
        self.scroll = 0
        self.lignes_visibles = 20
        self.chemin_saisi = ""
        self.mode_saisie = False
        self.resultat = None
        self.actif = True
        self._charger_dossier()

    def _charger_dossier(self):
        self.entrees = []
        self.selection = 0
        self.scroll = 0
        try:
            items = os.listdir(self.dossier_actuel)
        except PermissionError:
            items = []
        dossiers = sorted([i for i in items if os.path.isdir(os.path.join(self.dossier_actuel, i))], key=str.lower)
        fichiers = sorted([i for i in items if os.path.isfile(os.path.join(self.dossier_actuel, i))
                           and os.path.splitext(i)[1].lower() in self.extensions], key=str.lower)
        parent = os.path.dirname(self.dossier_actuel)
        if parent != self.dossier_actuel:
            self.entrees.append(("..", parent, "dossier"))
        for d in dossiers:
            self.entrees.append((d, os.path.join(self.dossier_actuel, d), "dossier"))
        for f in fichiers:
            self.entrees.append((f, os.path.join(self.dossier_actuel, f), "fichier"))

    def _naviguer_vers(self, chemin):
        if os.path.isdir(chemin):
            self.dossier_actuel = chemin
            self._charger_dossier()
        elif os.path.isfile(chemin):
            self.resultat = chemin
            self.actif = False

    def gerer_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.mode_saisie:
                if event.key == pygame.K_RETURN:
                    chemin = self.chemin_saisi.strip()
                    if os.path.isdir(chemin):
                        self.dossier_actuel = chemin
                        self._charger_dossier()
                    elif os.path.isfile(chemin):
                        self.resultat = chemin
                        self.actif = False
                    self.mode_saisie = False
                elif event.key == pygame.K_ESCAPE:
                    self.mode_saisie = False
                elif event.key == pygame.K_BACKSPACE:
                    self.chemin_saisi = self.chemin_saisi[:-1]
                elif event.unicode and event.unicode.isprintable():
                    self.chemin_saisi += event.unicode
            else:
                if event.key == pygame.K_ESCAPE:
                    self.actif = False
                elif event.key == pygame.K_UP:
                    self.selection = max(0, self.selection - 1)
                    if self.selection < self.scroll:
                        self.scroll = self.selection
                elif event.key == pygame.K_DOWN:
                    self.selection = min(len(self.entrees) - 1, self.selection + 1)
                    if self.selection >= self.scroll + self.lignes_visibles:
                        self.scroll = self.selection - self.lignes_visibles + 1
                elif event.key == pygame.K_RETURN:
                    if self.entrees:
                        _, chemin, _ = self.entrees[self.selection]
                        self._naviguer_vers(chemin)
                elif event.key == pygame.K_PAGEUP:
                    self.selection = max(0, self.selection - self.lignes_visibles)
                    self.scroll = max(0, self.scroll - self.lignes_visibles)
                elif event.key == pygame.K_PAGEDOWN:
                    self.selection = min(len(self.entrees) - 1, self.selection + self.lignes_visibles)
                    self.scroll = min(max(0, len(self.entrees) - self.lignes_visibles), self.scroll + self.lignes_visibles)
                elif event.key == pygame.K_F2:
                    self.chemin_saisi = self.dossier_actuel
                    self.mode_saisie = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                x, y = event.pos
                liste_y_start = 130
                h_ligne = 26
                idx_clique = (y - liste_y_start) // h_ligne + self.scroll
                if y > liste_y_start and 0 <= idx_clique < len(self.entrees):
                    self.selection = idx_clique
                    _, chemin, _ = self.entrees[idx_clique]
                    self._naviguer_vers(chemin)
            elif event.button == 4:
                self.scroll = max(0, self.scroll - 1)
            elif event.button == 5:
                max_scroll = max(0, len(self.entrees) - self.lignes_visibles)
                self.scroll = min(max_scroll, self.scroll + 1)

    def afficher(self):
        overlay = pygame.Surface((self.largeur, self.hauteur), pygame.SRCALPHA)
        overlay.fill((10, 10, 20, 230))
        self.screen.blit(overlay, (0, 0))

        titre = self.font_titre.render("Choisir une image", True, (255, 215, 0))
        self.screen.blit(titre, titre.get_rect(center=(self.largeur // 2, 40)))

        if self.mode_saisie:
            pygame.draw.rect(self.screen, (255, 255, 255), (50, 68, self.largeur - 100, 35), 2)
            self.screen.blit(self.font_petit.render(self.chemin_saisi + "_", True, (255, 255, 255)), (58, 76))
        else:
            chemin_court = self.dossier_actuel if len(self.dossier_actuel) <= 80 else "..." + self.dossier_actuel[-77:]
            self.screen.blit(self.font_petit.render("  " + chemin_court, True, (180, 220, 255)), (50, 76))

        pygame.draw.line(self.screen, (100, 100, 150), (50, 115), (self.largeur - 50, 115), 1)

        liste_y_start = 130
        h_ligne = 26
        for i, (nom, chemin, type_) in enumerate(self.entrees[self.scroll:self.scroll + self.lignes_visibles]):
            idx_reel = self.scroll + i
            y = liste_y_start + i * h_ligne
            if idx_reel == self.selection:
                pygame.draw.rect(self.screen, (60, 80, 140), (48, y - 2, self.largeur - 96, h_ligne - 2))
            prefixe = "[D] " if type_ == "dossier" else "[I] "
            couleur = (255, 220, 100) if type_ == "dossier" else (200, 255, 200)
            self.screen.blit(self.font_normal.render(prefixe + nom, True, couleur), (60, y))

        sep_y = liste_y_start + self.lignes_visibles * h_ligne + 10
        pygame.draw.line(self.screen, (100, 100, 150), (50, sep_y), (self.largeur - 50, sep_y), 1)
        hints = "Haut/Bas: Naviguer | ENTREE: Ouvrir | F2: Saisir chemin | ESC: Annuler"
        h_txt = self.font_petit.render(hints, True, (160, 160, 160))
        self.screen.blit(h_txt, h_txt.get_rect(center=(self.largeur // 2, sep_y + 18)))


class AjoutPokemon:
    def __init__(self):
        pygame.init()
        self.largeur = 1000
        self.hauteur = 700
        self.screen = pygame.display.set_mode((self.largeur, self.hauteur))
        pygame.display.set_caption("Créateur de Pokémon")
        self.clock = pygame.time.Clock()

        self.font_titre  = pygame.font.SysFont("Arial", 36, bold=True)
        self.font_normal = pygame.font.SysFont("Arial", 24)
        self.font_petit  = pygame.font.SysFont("Arial", 16)

        self.etape = 1
        self.input_text = ""
        self.message = ""
        self.message_couleur = (255, 255, 255)
        self.image_preview = None

        self.pokemon_data = {
            "name": "", "type": [], "stats": {"pv": 50, "attaque": 50, "defense": 50},
            "legendary": False, "description": "", "image_path": ""
        }

        self.types_disponibles = [
            "Feu", "Eau", "Plante", "Electrik", "Normal", "Roche",
            "Vol", "Psy", "Combat", "Poison", "Sol", "Glace",
            "Dragon", "Tenebres", "Acier", "Fee", "Spectre", "Insecte"
        ]
        self.types_selectionnes = []
        self.selection_type = 0
        self.stat_selectionnee = 0


    def selectionner_image(self):
        browser = FileBrowser(self.screen, self.font_normal, self.font_petit, self.font_titre)
        clock = pygame.time.Clock()
        while browser.actif:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    browser.actif = False
                else:
                    browser.gerer_event(event)
            self.screen.fill((30, 30, 50))
            self.afficher_etape_image()
            browser.afficher()
            pygame.display.flip()
            clock.tick(60)

        if browser.resultat:
            try:
                self.image_preview = pygame.transform.scale(pygame.image.load(browser.resultat), (150, 150))
                self.pokemon_data["image_path"] = browser.resultat
                self.message = f"Image chargee : {os.path.basename(browser.resultat)}"
                self.message_couleur = (100, 255, 100)
            except Exception as e:
                self.message = f"Erreur : {e}"
                self.message_couleur = (255, 100, 100)


    def afficher_etape_nom(self):
        self.screen.fill((30, 30, 50))
        self._titre("Etape 1/6 : Nom du Pokemon")
        self._blit("Entrez le nom :", 200, 250)
        pygame.draw.rect(self.screen, (255, 255, 255), (200, 290, 600, 50), 2)
        self._blit(self.input_text + "_", 210, 300)
        self._blit("[ENTREE] Valider  [ESC] Annuler", 200, 400, self.font_petit, (150, 150, 150))

    def afficher_etape_types(self):
        self.screen.fill((30, 30, 50))
        self._titre("Etape 2/6 : Types (max 2)")
        self._blit(f"Selectionnes : {', '.join(self.types_selectionnes) or 'Aucun'}", 100, 130, couleur=(255, 215, 0))
        cols, col_w = 6, 140
        for i, t in enumerate(self.types_disponibles):
            x = 100 + (i % cols) * col_w
            y = 180 + (i // cols) * 60
            sel = (i == self.selection_type)
            choisi = (t in self.types_selectionnes)
            couleur_cadre = (255, 215, 0) if sel else ((100, 255, 100) if choisi else (100, 100, 100))
            pygame.draw.rect(self.screen, couleur_cadre, (x - 5, y - 5, col_w - 10, 45), 2)
            self._blit(t, x, y, couleur=(255, 255, 100) if choisi else (255, 255, 255))
        self._blit("[ENTREE] Selectionner/Deselectionner  [ESPACE] Valider  [Fleches] Naviguer",
                   100, 580, self.font_petit, (150, 150, 150))

    def afficher_etape_stats(self):
        self.screen.fill((30, 30, 50))
        self._titre("Etape 3/6 : Stats de base")
        stats = [("PV", "pv"), ("Attaque", "attaque"), ("Defense", "defense")]
        for i, (label, cle) in enumerate(stats):
            y = 250 + i * 80
            couleur = (255, 215, 0) if i == self.stat_selectionnee else (255, 255, 255)
            self._blit(f"{label} : {self.pokemon_data['stats'][cle]}", 200, y, couleur=couleur)
            val = self.pokemon_data["stats"][cle]
            pygame.draw.rect(self.screen, (50, 50, 50), (400, y, 300, 20))
            pygame.draw.rect(self.screen, (100, 200, 100), (400, y, int(300 * val / 255), 20))
        self._blit("[Haut/Bas] Choisir stat  [Gauche/Droite] Modifier  [ENTREE] Suivant",
                   200, 500, self.font_petit, (150, 150, 150))

    def afficher_etape_image(self):
        self.screen.fill((30, 30, 50))
        self._titre("Etape 4/6 : Image")
        if self.image_preview:
            self.screen.blit(self.image_preview, (425, 200))
        else:
            pygame.draw.rect(self.screen, (80, 80, 80), (425, 200, 150, 150))
            self._blit("Pas d'image", 440, 265, self.font_petit, (150, 150, 150))
        if self.message:
            self._blit(self.message, 200, 380, self.font_petit, self.message_couleur)
        self._blit("[I] Parcourir  [ENTREE] Suivant  [ESC] Retour", 200, 430, self.font_petit, (150, 150, 150))

    def afficher_etape_description(self):
        self.screen.fill((30, 30, 50))
        self._titre("Etape 5/6 : Description")
        pygame.draw.rect(self.screen, (255, 255, 255), (150, 200, 700, 120), 2)
        texte = self.input_text or ""
        mots = [m for m in texte.split(' ') if m]
        ligne, y_text = "", 210
        for mot in mots:
            test = ligne + (" " if ligne else "") + mot
            if self.font_petit.size(test)[0] < 680:
                ligne = test
            else:
                self._blit(ligne, 160, y_text, self.font_petit)
                y_text += 25
                ligne = mot
        self._blit(ligne + "_", 160, y_text, self.font_petit)
        self._blit("[ENTREE] Suivant  [ESC] Retour", 200, 360, self.font_petit, (150, 150, 150))

    def afficher_etape_legendaire(self):
        self.screen.fill((30, 30, 50))
        self._titre("Etape 6/6 : Legendaire ?")
        couleur_o = (255, 215, 0) if self.pokemon_data["legendary"] else (255, 255, 255)
        couleur_n = (255, 215, 0) if not self.pokemon_data["legendary"] else (255, 255, 255)
        self._blit("[O] Oui - Pokemon legendaire !", 300, 300, couleur=couleur_o)
        self._blit("[N] Non - Pokemon normal",        300, 360, couleur=couleur_n)
        self._blit("[ENTREE] Sauvegarder et terminer", 300, 460, self.font_petit, (150, 150, 150))


    def afficher_recap(self):
        self.screen.fill((30, 30, 50))
        self._titre("Pokemon cree avec succes !")
        infos = [
            f"Nom : {self.pokemon_data['name']}",
            f"Types : {', '.join(self.pokemon_data['type'])}",
            f"PV : {self.pokemon_data['stats']['pv']}  ATK : {self.pokemon_data['stats']['attaque']}  DEF : {self.pokemon_data['stats']['defense']}",
            f"Legendaire : {'Oui' if self.pokemon_data['legendary'] else 'Non'}",
            f"Description : {self.pokemon_data['description'][:60]}...",
        ]
        for i, ligne in enumerate(infos):
            self._blit(ligne, 200, 200 + i * 40)
        if self.image_preview:
            self.screen.blit(self.image_preview, (700, 180))
        self._blit("[ENTREE] Retour au menu  [ESC] Quitter", 200, 500, self.font_petit, (150, 150, 150))


    def gerer_input(self, event):
        if event.type != pygame.KEYDOWN:
            return True

        if self.etape == 1:
            if event.key == pygame.K_RETURN and self.input_text.strip():
                self.pokemon_data["name"] = self.input_text.strip()
                self.input_text = ""
                self.etape = 2
            elif event.key == pygame.K_ESCAPE:
                return False
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif event.unicode and event.unicode.isprintable():
                self.input_text += event.unicode

        elif self.etape == 2:
            if event.key == pygame.K_UP:
                self.selection_type = max(0, self.selection_type - 6)
            elif event.key == pygame.K_DOWN:
                self.selection_type = min(len(self.types_disponibles) - 1, self.selection_type + 6)
            elif event.key == pygame.K_LEFT:
                self.selection_type = max(0, self.selection_type - 1)
            elif event.key == pygame.K_RIGHT:
                self.selection_type = min(len(self.types_disponibles) - 1, self.selection_type + 1)
            elif event.key == pygame.K_RETURN:
                t = self.types_disponibles[self.selection_type]
                if t in self.types_selectionnes:
                    self.types_selectionnes.remove(t)
                elif len(self.types_selectionnes) < 2:
                    self.types_selectionnes.append(t)
            elif event.key == pygame.K_SPACE and self.types_selectionnes:
                self.pokemon_data["type"] = self.types_selectionnes[:]
                self.etape = 3

        elif self.etape == 3:
            stats_cles = ["pv", "attaque", "defense"]
            if event.key == pygame.K_UP:
                self.stat_selectionnee = max(0, self.stat_selectionnee - 1)
            elif event.key == pygame.K_DOWN:
                self.stat_selectionnee = min(2, self.stat_selectionnee + 1)
            elif event.key == pygame.K_LEFT:
                cle = stats_cles[self.stat_selectionnee]
                self.pokemon_data["stats"][cle] = max(1, self.pokemon_data["stats"][cle] - 5)
            elif event.key == pygame.K_RIGHT:
                cle = stats_cles[self.stat_selectionnee]
                self.pokemon_data["stats"][cle] = min(255, self.pokemon_data["stats"][cle] + 5)
            elif event.key == pygame.K_RETURN:
                self.input_text = ""
                self.etape = 4

        elif self.etape == 4:
            if event.key == pygame.K_i:
                self.selectionner_image()
            elif event.key == pygame.K_RETURN:
                self.input_text = ""
                self.etape = 5
            elif event.key == pygame.K_ESCAPE:
                self.etape = 3

        elif self.etape == 5:
            if event.key == pygame.K_RETURN:
                self.pokemon_data["description"] = self.input_text.strip()
                self.input_text = ""
                self.etape = 6
            elif event.key == pygame.K_ESCAPE:
                self.etape = 4
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif event.unicode and event.unicode.isprintable():
                self.input_text += event.unicode

        elif self.etape == 6:
            if event.key == pygame.K_o:
                self.pokemon_data["legendary"] = True
            elif event.key == pygame.K_n:
                self.pokemon_data["legendary"] = False
            elif event.key == pygame.K_RETURN:
                self._sauvegarder()
                self.etape = 7

        elif self.etape == 7:
            if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                return False

        return True

    def _sauvegarder(self):
        try:
            chemin_json = _chemin_json()
            with open(chemin_json, "r", encoding="utf-8") as f:
                data = json.load(f)

            nouveau = {
                "name": self.pokemon_data["name"],
                "type": self.pokemon_data["type"],
                "stats": self.pokemon_data["stats"],
                "legendary": self.pokemon_data["legendary"],
                "description": self.pokemon_data["description"],
                "image_path": self.pokemon_data["image_path"],
            }
            data["pokemon"].append(nouveau)

            with open(chemin_json, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            # Copier l'image dans Assets/pokemon/
            if self.pokemon_data["image_path"]:
                dest_dir = "Assets/pokemon"
                os.makedirs(dest_dir, exist_ok=True)
                ext = os.path.splitext(self.pokemon_data["image_path"])[1]
                dest = os.path.join(dest_dir, self.pokemon_data["name"] + ext)
                if self.pokemon_data["image_path"] != dest:
                    shutil.copy2(self.pokemon_data["image_path"], dest)

            print(f"✓ {self.pokemon_data['name']} sauvegardé !")
        except Exception as e:
            print(f"✗ Erreur sauvegarde : {e}")


    def render(self):
        afficheurs = {
            1: self.afficher_etape_nom,
            2: self.afficher_etape_types,
            3: self.afficher_etape_stats,
            4: self.afficher_etape_image,
            5: self.afficher_etape_description,
            6: self.afficher_etape_legendaire,
            7: self.afficher_recap,
        }
        afficheurs.get(self.etape, lambda: None)()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    running = self.gerer_input(event)
            self.render()
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()


    def _titre(self, texte):
        surf = self.font_titre.render(texte, True, (255, 215, 0))
        self.screen.blit(surf, surf.get_rect(center=(self.largeur // 2, 80)))

    def _blit(self, texte, x, y, font=None, couleur=(255, 255, 255)):
        font = font or self.font_normal
        self.screen.blit(font.render(str(texte), True, couleur), (x, y))


if __name__ == "__main__":
    AjoutPokemon().run()