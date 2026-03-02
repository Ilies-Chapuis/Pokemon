

import os
import pygame

COULEURS_TYPE = {
    "Feu": (255, 100, 50), "Eau": (50, 150, 255), "Plante": (100, 200, 100),
    "Électrik": (255, 220, 50), "Normal": (168, 168, 120), "Roche": (150, 100, 50),
}


class MenuStarter:
    STARTERS = ["Castopuff", "Timiki", "Rubycire"]

    def __init__(self, screen, font_titre, font_normal, pokedex):
        self.screen = screen
        self.font_titre  = font_titre
        self.font_normal = font_normal
        self.font_petit  = pygame.font.SysFont("Arial", 16)
        self.pokedex = pokedex
        self.selection = 0
        self._cache = {}


    def naviguer(self, direction):
        self.selection = (self.selection + direction) % len(self.STARTERS)

    def obtenir_choix(self):
        return self.STARTERS[self.selection]


    def afficher(self):
        self.screen.fill((20, 20, 40))
        self._titre()
        self._cartes_starters()
        self._instructions()

    def _titre(self):
        surf = self.font_titre.render("CHOISIS TON POKÉMON", True, (255, 215, 0))
        self.screen.blit(surf, surf.get_rect(center=(500, 80)))

    def _cartes_starters(self):
        for i, nom in enumerate(self.STARTERS):
            x = 200 + i * 200
            self._carte(nom, x, 250, i == self.selection)

    def _carte(self, nom, x, y, selectionne):
        couleur_cadre = (100, 255, 100) if selectionne else (100, 100, 100)
        pygame.draw.rect(self.screen, couleur_cadre, (x - 70, y - 70, 140, 220), 3)

        if nom not in self.pokedex:
            return
        data = self.pokedex[nom]

        img = self._charger_image(nom)
        if img:
            self.screen.blit(img, img.get_rect(center=(x, y)))
        else:
            couleur = COULEURS_TYPE.get(data["type"][0], (150, 150, 150))
            pygame.draw.circle(self.screen, couleur, (x, y), 50)

        self._blit_centre(nom, x, y + 90, self.font_normal)
        self._blit_centre(" / ".join(data["type"]), x, y + 115, self.font_petit, (200, 200, 200))
        stats_txt = f"PV:{data['stats']['pv']} ATK:{data['stats']['attaque']}"
        self._blit_centre(stats_txt, x, y + 135, self.font_petit, (150, 150, 150))

    def _instructions(self):
        for i, ligne in enumerate(["GAUCHE/DROITE: Choisir", "ENTRÉE: Confirmer"]):
            surf = self.font_petit.render(ligne, True, (150, 150, 150))
            self.screen.blit(surf, surf.get_rect(center=(500, 550 + i * 25)))


    def _charger_image(self, nom):
        if nom in self._cache:
            return self._cache[nom]
        base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Data", "Assets", "pokemon")
        for chemin in [os.path.join(base, f"{nom}.png"), os.path.join(base, f"{nom.lower()}.png")]:
            if os.path.exists(chemin):
                try:
                    img = pygame.transform.scale(pygame.image.load(chemin), (100, 100))
                    self._cache[nom] = img
                    return img
                except Exception:
                    continue
        return None

    def _blit_centre(self, texte, cx, cy, font, couleur=(255, 255, 255)):
        surf = font.render(texte, True, couleur)
        self.screen.blit(surf, surf.get_rect(center=(cx, cy)))