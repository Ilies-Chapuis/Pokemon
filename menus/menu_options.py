
import pygame


class MenuOptions:
    DIFFICULTES = ["Facile", "Normal", "Difficile"]

    def __init__(self, screen, font_titre, font_normal):
        self.screen = screen
        self.font_titre  = font_titre
        self.font_normal = font_normal
        self.font_petit  = pygame.font.SysFont("Arial", 16)

        self.parametres = {
            "volume_musique": 50,
            "volume_effets":  70,
            "difficulte":     "Normal",
            "animations":     True,
        }
        self.options   = list(self.parametres.keys()) + ["Retour"]
        self.selection = 0


    def naviguer(self, direction):
        self.selection = (self.selection + direction) % len(self.options)

    def modifier(self, direction):
        if self.selection >= len(self.parametres):
            return
        opt = self.options[self.selection]
        if opt in ("volume_musique", "volume_effets"):
            self.parametres[opt] = max(0, min(100, self.parametres[opt] + direction * 10))
        elif opt == "difficulte":
            idx = (self.DIFFICULTES.index(self.parametres[opt]) + direction) % len(self.DIFFICULTES)
            self.parametres[opt] = self.DIFFICULTES[idx]
        elif opt == "animations":
            self.parametres[opt] = not self.parametres[opt]


    def afficher(self):
        self.screen.fill((20, 20, 40))
        self._titre()
        self._options()
        self._instructions()

    def _titre(self):
        surf = self.font_titre.render("OPTIONS", True, (255, 215, 0))
        self.screen.blit(surf, surf.get_rect(center=(500, 100)))

    def _options(self):
        for i, opt in enumerate(self.options):
            couleur = (100, 255, 100) if i == self.selection else (255, 255, 255)
            y = 200 + i * 70
            if opt == "Retour":
                surf = self.font_normal.render("< Retour au menu", True, couleur)
                self.screen.blit(surf, surf.get_rect(center=(500, y)))
            else:
                nom = opt.replace("_", " ").title()
                self.screen.blit(self.font_normal.render(f"{nom}:", True, couleur), (250, y))
                valeur = self._valeur_affichee(opt)
                self.screen.blit(self.font_normal.render(valeur, True, (200, 200, 200)), (550, y))

    def _valeur_affichee(self, opt):
        val = self.parametres[opt]
        if isinstance(val, bool):
            return "Activé" if val else "Désactivé"
        if opt in ("volume_musique", "volume_effets"):
            return f"{val}%"
        return str(val)

    def _instructions(self):
        lignes = ["HAUT/BAS: Naviguer", "GAUCHE/DROITE: Modifier", "ENTRÉE: Retour"]
        for i, ligne in enumerate(lignes):
            surf = self.font_petit.render(ligne, True, (150, 150, 150))
            self.screen.blit(surf, (50, 550 + i * 25))
