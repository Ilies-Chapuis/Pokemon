
import pygame


class Menu:
    OPTIONS = ["Nouvelle partie", "Continuer", "Créateur de Pokémon",
               "Pokédex", "Options", "Quitter"]

    def __init__(self, screen, font_titre, font_normal):
        self.screen = screen
        self.font_titre  = font_titre
        self.font_normal = font_normal
        self.font_petit  = pygame.font.SysFont("Arial", 16)
        self.selection = 0


    def naviguer(self, direction):
        self.selection = (self.selection + direction) % len(self.OPTIONS)

    def obtenir_choix(self):
        return self.OPTIONS[self.selection]


    def afficher(self):
        self.screen.fill((20, 20, 40))
        self._titre()
        self._options()
        self._instructions()

    def _titre(self):
        self._blit_centre("POKÉMON FRAUD",    500, 150, self.font_titre,  (255, 215, 0))
        self._blit_centre("Édition Aventure FRAUDULEUSE", 500, 200, self.font_normal, (200, 200, 200))

    def _options(self):
        for i, option in enumerate(self.OPTIONS):
            sel = (i == self.selection)
            couleur = (100, 255, 100) if sel else (255, 255, 255)
            surf = self.font_normal.render(option, True, couleur)
            rect = surf.get_rect(center=(500, 300 + i * 60))
            self.screen.blit(surf, rect)
            if sel:
                ind = self.font_normal.render(">", True, (100, 255, 100))
                self.screen.blit(ind, (rect.left - 40, rect.top))

    def _instructions(self):
        lignes = ["Utilisez les flèches HAUT/BAS pour naviguer",
                  "Appuyez sur ENTRÉE pour sélectionner"]
        for i, ligne in enumerate(lignes):
            self._blit_centre(ligne, 500, 600 + i * 25, self.font_petit, (150, 150, 150))

    def _blit_centre(self, texte, cx, cy, font, couleur=(255, 255, 255)):
        surf = font.render(texte, True, couleur)
        self.screen.blit(surf, surf.get_rect(center=(cx, cy)))