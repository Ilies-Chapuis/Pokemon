#

import pygame
import os

_RACINE = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def _chercher_image(nom_fichier, taille):
    #Cherche un fichier image uniquement dans Data/Assets/."
    chemin = os.path.join(_RACINE, "Data", "Assets", nom_fichier)
    if os.path.exists(chemin):
        try:
            img = pygame.image.load(chemin).convert_alpha()
            return pygame.transform.scale(img, taille)
        except Exception:
            pass
    return None


class RendererChampion:
    #Écrans de dialogue, bandeau de combat et fin de combat champion.

    def __init__(self, screen, ui):
        self.screen = screen
        self.ui     = ui
        self.W, self.H = screen.get_size()
        self._cache = {}

        self.font_titre  = pygame.font.SysFont("Arial", 28, bold=True)
        self.font_normal = pygame.font.SysFont("Arial", 20)
        self.font_petit  = pygame.font.SysFont("Arial", 15)
        self.font_nom    = pygame.font.SysFont("Arial", 22, bold=True)

    #  cache image
    def _image(self, nom_fichier, taille):
        cle = (nom_fichier, taille)
        if cle not in self._cache:
            self._cache[cle] = _chercher_image(nom_fichier, taille)
        return self._cache[cle]

    # dialogue
    def afficher_dialogue(self, champion_data, lignes, ligne_active, badges):
        self.screen.fill((15, 15, 30))
        col = champion_data["couleur_theme"]

        pygame.draw.rect(self.screen, col, (0, 0, self.W, 8))
        pygame.draw.rect(self.screen, col, (0, self.H - 8, self.W, 8))

        # Portrait gauche
        img = self._image(champion_data["image"], (220, 320))
        if img:
            self.screen.blit(img, (40, (self.H - 320) // 2))
        else:
            pygame.draw.rect(self.screen, (50, 50, 80), (40, 150, 200, 320))
            t = self.font_titre.render("?", True, (120, 120, 120))
            self.screen.blit(t, t.get_rect(center=(140, 310)))

        # Panneau texte
        px, py, pw, ph = 290, 100, self.W - 320, self.H - 160
        fond = pygame.Surface((pw, ph), pygame.SRCALPHA)
        fond.fill((10, 10, 25, 225))
        self.screen.blit(fond, (px, py))
        pygame.draw.rect(self.screen, col, (px, py, pw, ph), 2, border_radius=8)

        self.screen.blit(self.font_nom.render(champion_data["nom"], True, col),
                         (px + 20, py + 15))
        self.screen.blit(self.font_petit.render(champion_data["titre"], True, (170, 170, 170)),
                         (px + 20, py + 45))
        pygame.draw.line(self.screen, col, (px + 10, py + 68), (px + pw - 10, py + 68), 1)

        for i, ligne in enumerate(lignes):
            if i > ligne_active:
                break
            if "[ENTRÉE]" in ligne or "[ÉCHAP]" in ligne:
                c_txt = (255, 215, 0)
                surf  = self.font_petit.render(ligne, True, c_txt)
            else:
                c_txt = (240, 240, 240) if i == ligne_active else (120, 120, 120)
                surf  = self.font_normal.render(ligne, True, c_txt)
            self.screen.blit(surf, (px + 20, py + 85 + i * 38))

        # Flèche "suite"
        if ligne_active < len(lignes) - 1:
            tx = px + pw - 30
            ty = py + ph - 30
            pygame.draw.polygon(self.screen, col,
                                [(tx, ty), (tx + 12, ty), (tx + 6, ty + 10)])

        # Badges
        if badges:
            self.screen.blit(self.font_petit.render("Badges :", True, (170, 170, 170)),
                             (30, self.H - 60))
            for j, badge in enumerate(badges):
                c_b = (255, 215, 0) if "Feuille" in badge else (255, 120, 30)
                self.screen.blit(self.font_petit.render(f"✦ {badge}", True, c_b),
                                 (30, self.H - 38 + j * 18))

    # bandeau combat
    def afficher_bandeau_combat(self, champion_data, equipe_champion, idx_actif):
        col = champion_data["couleur_theme"]
        bh  = 60
        fond = pygame.Surface((self.W, bh), pygame.SRCALPHA)
        fond.fill((5, 5, 15, 200))
        self.screen.blit(fond, (0, 0))
        pygame.draw.line(self.screen, col, (0, bh), (self.W, bh), 2)

        img = self._image(champion_data["image"], (45, 55))
        if img:
            self.screen.blit(img, (8, 2))

        t = self.font_nom.render(
            f"{champion_data['nom']} — {champion_data['titre']}", True, col)
        self.screen.blit(t, (60, 8))

        for i, poke in enumerate(equipe_champion):
            cx, cy = 60 + i * 28, 42
            r      = 9 if i == idx_actif else 7
            c_p    = (100, 255, 100) if i == idx_actif \
                     else ((180, 180, 180) if poke.est_vivant() else (80, 40, 40))
            pygame.draw.circle(self.screen, c_p, (cx, cy), r)
            if i == idx_actif:
                pygame.draw.circle(self.screen, (255, 255, 255), (cx, cy), r, 2)

    #  fin de combat
    def afficher_fin_combat(self, champion_data, joueur_gagne, recompenses):
        fond = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        fond.fill((0, 0, 0, 170))
        self.screen.blit(fond, (0, 0))

        if joueur_gagne:
            titre_txt = f"VICTOIRE contre {champion_data['nom']} !"
            titre_col = (255, 215, 0)
        else:
            titre_txt = f"Défaite... {champion_data['nom']} est trop fort."
            titre_col = (255, 80, 80)

        t = self.font_titre.render(titre_txt, True, titre_col)
        self.screen.blit(t, t.get_rect(center=(self.W // 2, self.H // 2 - 80)))

        if joueur_gagne:
            for i, ligne in enumerate(recompenses):
                c_r = (255, 215, 0) if ("Badge" in ligne or "✦" in ligne) \
                      else (200, 255, 200)
                surf = self.font_normal.render(ligne, True, c_r)
                self.screen.blit(surf, surf.get_rect(
                    center=(self.W // 2, self.H // 2 - 20 + i * 35)))

        hint = self.font_petit.render("[ESPACE] Continuer", True, (180, 180, 180))
        self.screen.blit(hint, hint.get_rect(center=(self.W // 2, self.H // 2 + 130)))
