"""Rendu des écrans de dialogue et de combat Champion"""

import pygame
import os


class RendererChampion:
    """Affiche le dialogue avec le champion et adapte l'UI de combat."""

    def __init__(self, screen, ui):
        self.screen = screen
        self.ui     = ui
        self.W, self.H = screen.get_size()

        self.font_titre   = pygame.font.SysFont("Arial", 28, bold=True)
        self.font_normal  = pygame.font.SysFont("Arial", 20)
        self.font_petit   = pygame.font.SysFont("Arial", 15)
        self.font_nom     = pygame.font.SysFont("Arial", 22, bold=True)

        self._images_cache = {}

    # ── Chargement image champion ────────────────────────────────────────
    def _charger_image_champion(self, nom_fichier, taille=(200, 300)):
        if nom_fichier in self._images_cache:
            return self._images_cache[nom_fichier]

        racine = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

        # Tous les noms possibles selon le champion
        if "plante" in nom_fichier:
            noms = ["champion_plante.png", "champion_arène_plante.png",
                    "champion_arene_plante.png"]
        elif "feu" in nom_fichier:
            noms = ["champion_feu.png", "champion_arène_feu.png",
                    "champion_arene_feu.png"]
        else:
            noms = [nom_fichier]

        # Tous les dossiers possibles
        dossiers = [
            racine,                                          # racine projet
            os.path.join(racine, "Data", "Assets"),          # Data/Assets/
            os.path.join(racine, "Data"),                    # Data/
            os.getcwd(),                                     # dossier courant
        ]

        for dossier in dossiers:
            for nom in noms:
                chemin = os.path.join(dossier, nom)
                if os.path.exists(chemin):
                    try:
                        img = pygame.image.load(chemin).convert_alpha()
                        img = pygame.transform.scale(img, taille)
                        self._images_cache[nom_fichier] = img
                        return img
                    except Exception:
                        continue

        self._images_cache[nom_fichier] = None
        return Nonepygame
import os


class RendererChampion:
    """Affiche le dialogue avec le champion et adapte l'UI de combat."""

    def __init__(self, screen, ui):
        self.screen = screen
        self.ui     = ui
        self.W, self.H = screen.get_size()

        self.font_titre   = pygame.font.SysFont("Arial", 28, bold=True)
        self.font_normal  = pygame.font.SysFont("Arial", 20)
        self.font_petit   = pygame.font.SysFont("Arial", 15)
        self.font_nom     = pygame.font.SysFont("Arial", 22, bold=True)

        self._images_cache = {}

    # ── Chargement image champion ────────────────────────────────────────
    def _charger_image_champion(self, nom_fichier, taille=(200, 300)):
        if nom_fichier in self._images_cache:
            return self._images_cache[nom_fichier]
        dossier = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "Data", "Assets")
        chemin = os.path.join(dossier, nom_fichier)
        if not os.path.exists(chemin):
            # Fallback : chercher à la racine du projet
            chemin = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), nom_fichier)
        try:
            img = pygame.image.load(chemin).convert_alpha()
            img = pygame.transform.scale(img, taille)
            self._images_cache[nom_fichier] = img
            return img
        except Exception:
            self._images_cache[nom_fichier] = None
            return None

    # ── Écran de dialogue ────────────────────────────────────────────────
    def afficher_dialogue(self, champion_data, lignes_dialogue,
                          ligne_active, badges_joueur):
        """
        Affiche l'écran de dialogue avec le champion.
        champion_data : dict du champion (CHAMPIONS[id])
        lignes_dialogue : liste de strings à afficher
        ligne_active : index de la ligne courante (pour l'animation)
        """
        # Fond dégradé
        self.screen.fill((15, 15, 30))
        couleur_theme = champion_data["couleur_theme"]

        # Bande de couleur en haut
        pygame.draw.rect(self.screen, couleur_theme, (0, 0, self.W, 8))
        pygame.draw.rect(self.screen, couleur_theme, (0, self.H - 8, self.W, 8))

        # Image du champion (gauche)
        img = self._charger_image_champion(champion_data["image"], (220, 320))
        if img:
            self.screen.blit(img, (40, (self.H - 320) // 2))
        else:
            # Silhouette de remplacement
            pygame.draw.rect(self.screen, (50, 50, 80), (40, 150, 180, 280))
            t = self.font_normal.render("?", True, (150, 150, 150))
            self.screen.blit(t, t.get_rect(center=(130, 290)))

        # Panneau de texte (droite)
        px, py = 290, 100
        pw, ph = self.W - px - 30, self.H - 160

        fond = pygame.Surface((pw, ph), pygame.SRCALPHA)
        fond.fill((10, 10, 25, 220))
        self.screen.blit(fond, (px, py))
        pygame.draw.rect(self.screen, couleur_theme,
                         (px, py, pw, ph), 2, border_radius=8)

        # Nom et titre du champion
        t_nom = self.font_nom.render(champion_data["nom"], True, couleur_theme)
        self.screen.blit(t_nom, (px + 20, py + 15))
        t_titre = self.font_petit.render(champion_data["titre"], True, (180, 180, 180))
        self.screen.blit(t_titre, (px + 20, py + 45))

        pygame.draw.line(self.screen, couleur_theme,
                         (px + 10, py + 68), (px + pw - 10, py + 68), 1)

        # Lignes de dialogue
        for i, ligne in enumerate(lignes_dialogue):
            if i > ligne_active:
                break
            # Dernière ligne affichée = couleur vive, les autres estompées
            if i == ligne_active:
                couleur = (240, 240, 240)
            else:
                couleur = (130, 130, 130)

            # Détecter la ligne d'instruction (dernière ligne avec [ENTRÉE])
            if "[ENTRÉE]" in ligne or "[ÉCHAP]" in ligne:
                couleur = (255, 215, 0)
                surf = self.font_petit.render(ligne, True, couleur)
            else:
                surf = self.font_normal.render(ligne, True, couleur)
            self.screen.blit(surf, (px + 20, py + 85 + i * 38))

        # Indicateur de progression
        if ligne_active < len(lignes_dialogue) - 1:
            tri_x = px + pw - 30
            tri_y = py + ph - 30
            pygame.draw.polygon(self.screen, couleur_theme,
                                [(tri_x, tri_y), (tri_x + 12, tri_y),
                                 (tri_x + 6, tri_y + 10)])

        # Badges obtenus (coin bas gauche)
        if badges_joueur:
            self.font_petit.render("Badges :", True, (200, 200, 200))
            bx = 30
            self.screen.blit(
                self.font_petit.render("Badges :", True, (180, 180, 180)),
                (bx, self.H - 55))
            for j, badge in enumerate(badges_joueur):
                col = (255, 215, 0) if "Feuille" in badge else (255, 120, 30)
                self.screen.blit(
                    self.font_petit.render(f"✦ {badge}", True, col),
                    (bx, self.H - 35 + j * 18))

    # ── Bandeau champion en combat ───────────────────────────────────────
    def afficher_bandeau_combat(self, champion_data, equipe_champion,
                                idx_actif):
        """
        Affiche en haut de l'écran le portrait du champion + état de son équipe.
        À appeler depuis renderer_combat après le fond mais avant les Pokémon.
        """
        couleur = champion_data["couleur_theme"]
        bh = 60
        fond = pygame.Surface((self.W, bh), pygame.SRCALPHA)
        fond.fill((5, 5, 15, 200))
        self.screen.blit(fond, (0, 0))
        pygame.draw.line(self.screen, couleur, (0, bh), (self.W, bh), 2)

        # Mini portrait
        img = self._charger_image_champion(champion_data["image"], (45, 55))
        if img:
            self.screen.blit(img, (8, 2))

        # Nom champion
        t = self.font_nom.render(
            f"{champion_data['nom']} — {champion_data['titre']}",
            True, couleur)
        self.screen.blit(t, (60, 8))

        # Petites icônes Pokémon (6 ronds) avec couleur selon état
        for i, poke in enumerate(equipe_champion):
            cx = 60 + i * 28
            cy = 42
            if i == idx_actif:
                col = (100, 255, 100)
                r   = 9
            elif poke.est_vivant():
                col = (180, 180, 180)
                r   = 7
            else:
                col = (80, 40, 40)
                r   = 7
            pygame.draw.circle(self.screen, col, (cx, cy), r)
            if i == idx_actif:
                pygame.draw.circle(self.screen, (255, 255, 255), (cx, cy), r, 2)

    # ── Écran de fin de combat champion ─────────────────────────────────
    def afficher_fin_combat(self, champion_data, joueur_gagne,
                            recompenses_recues):
        """Affiche le résultat du combat champion avec les récompenses."""
        fond = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        fond.fill((0, 0, 0, 170))
        self.screen.blit(fond, (0, 0))

        couleur = champion_data["couleur_theme"]

        if joueur_gagne:
            titre_txt = f"VICTOIRE contre {champion_data['nom']} !"
            titre_col = (255, 215, 0)
        else:
            titre_txt = f"Défaite... {champion_data['nom']} est trop fort."
            titre_col = (255, 80, 80)

        t = self.font_titre.render(titre_txt, True, titre_col)
        self.screen.blit(t, t.get_rect(center=(self.W // 2, self.H // 2 - 80)))

        if joueur_gagne and recompenses_recues:
            for i, ligne in enumerate(recompenses_recues):
                col = (255, 215, 0) if "Badge" in ligne or "✦" in ligne \
                    else (200, 255, 200)
                surf = self.font_normal.render(ligne, True, col)
                self.screen.blit(surf,
                                 surf.get_rect(center=(self.W // 2,
                                                       self.H // 2 - 20 + i * 35)))

        hint = self.font_petit.render("[ESPACE] Continuer", True, (180, 180, 180))
        self.screen.blit(hint, hint.get_rect(center=(self.W // 2, self.H // 2 + 130)))
