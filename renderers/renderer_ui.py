"""Utilitaires graphiques partagés par tous les renderers"""

import pygame
import os

def _chemin_assets():
    """Retourne le chemin absolu vers Data/Assets/pokemon/ (portable)"""
    import os
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Data", "Assets", "pokemon")


class RendererUI:
    """Boîte à outils graphique : texte, barres PV, images."""

    def __init__(self, screen, fonts):
        self.screen = screen
        self.font_titre  = fonts["titre"]
        self.font_normal = fonts["normal"]
        self.font_petit  = fonts["petit"]

    # ------------------------------------------------------------------ #
    def texte(self, texte, x, y, font=None, couleur=(255, 255, 255)):
        font = font or self.font_normal
        self.screen.blit(font.render(str(texte), True, couleur), (x, y))

    def texte_centre(self, texte, cx, y, font=None, couleur=(255, 255, 255)):
        font = font or self.font_normal
        surf = font.render(str(texte), True, couleur)
        self.screen.blit(surf, surf.get_rect(center=(cx, y)))

    # ------------------------------------------------------------------ #
    def barre_pv(self, pokemon, x, y, largeur):
        ratio = pokemon.pv / pokemon.pv_max if pokemon.pv_max > 0 else 0
        if ratio > 0.5:
            couleur = (100, 255, 100)
        elif ratio > 0.2:
            couleur = (255, 200, 50)
        else:
            couleur = (255, 50, 50)

        pygame.draw.rect(self.screen, (50, 50, 50),   (x, y, largeur, 20))
        pygame.draw.rect(self.screen, couleur,         (x, y, int(largeur * ratio), 20))
        pygame.draw.rect(self.screen, (255, 255, 255), (x, y, largeur, 20), 2)
        self.texte(f"{pokemon.pv}/{pokemon.pv_max}", x + largeur + 10, y, self.font_petit)

    # ------------------------------------------------------------------ #
    def charger_image(self, cache, nom, taille=(120, 120)):
        """Charge et met en cache l'image d'un Pokémon."""
        if nom in cache:
            return cache[nom]

        import os
        base = _chemin_assets()
        chemins = [
            os.path.join(base, f"{nom}.png"),
            os.path.join(base, f"{nom.lower()}.png"),
        ]
        for chemin in chemins:
            if os.path.exists(chemin):
                try:
                    img = pygame.image.load(chemin)
                    img = pygame.transform.scale(img, taille)
                    cache[nom] = img
                    return img
                except Exception:
                    continue
        return None

    def charger_arena(self, largeur, hauteur):
        """Charge l'image de fond d'arène."""
        import os
        noms = ["arène_pokemon.png", "arene_pokemon.png", "arena_pokemon.png", "arena.png"]
        base_data = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Data", "Assets")
        dossiers = [base_data, "Assets/", "assets/", ""]
        for d in dossiers:
            for n in noms:
                chemin = os.path.join(d, n) if d else n
                if os.path.exists(chemin):
                    try:
                        img = pygame.image.load(chemin)
                        return pygame.transform.scale(img, (largeur, hauteur))
                    except Exception:
                        continue
        return None
