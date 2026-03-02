

import pygame
from Evolution import peut_forme_ultime, peut_evoluer


class MenuEquipe:
    #Affiche et gère l'écran de l'équipe du joueur.

    def __init__(self, screen, ui):
        self.screen = screen
        self.ui     = ui

    #  rendu
    def afficher(self, equipe, selection):
        self.screen.fill((30, 30, 50))
        self.ui.texte_centre("VOTRE ÉQUIPE", 500, 50,
                             self.ui.font_titre, (255, 215, 0))
        for i, poke in enumerate(equipe):
            self._ligne(poke, i, i == selection)
        self._instructions()

    def _ligne(self, poke, i, sel):
        y = 120 + i * 90
        if sel:
            pygame.draw.rect(self.screen, (100, 255, 100), (50, y - 10, 900, 80), 3)
        if i == 0:
            self.ui.texte("★", 70, y + 10, self.ui.font_titre, (255, 215, 0))

        couleur = (255, 100, 100) if not poke.est_vivant() else (255, 255, 255)
        self.ui.texte(f"{poke.nom}  Nv.{poke.niveau}", 120, y, couleur=couleur)
        self.ui.texte(" / ".join(poke.types), 120, y + 25,
                      self.ui.font_petit, (200, 200, 200))
        self.ui.barre_pv(poke, 400, y + 15, 300)
        self.ui.texte(f"ATK:{poke.attaque}  DEF:{poke.defense}",
                      750, y + 15, self.ui.font_petit, (200, 200, 200))

        # Statut / badges disponibles
        if not poke.est_vivant():
            self.ui.texte("K.O.", 870, y + 15, couleur=(255, 50, 50))
        else:
            # Évolution classique disponible ?
            peut, nom_evo, _ = peut_evoluer(poke.nom, poke.niveau)
            if peut and nom_evo:
                self.ui.texte(f" {nom_evo} [E]", 820, y + 15,
                              self.ui.font_petit, (100, 200, 255))
            # Forme Ultime disponible ?
            elif peut_forme_ultime(poke):
                self.ui.texte(" FORME ULTIME [U]", 800, y + 15,
                              self.ui.font_petit, (255, 215, 0))

    def _instructions(self):
        lignes = [
            "↑↓ : Naviguer",
            "ENTRÉE : Mettre en actif",
            "[E] : Évoluer (si dispo)",
            "[U] : Forme Ultime (si dispo)",
            "ESC : Retour",
        ]
        for i, txt in enumerate(lignes):
            self.ui.texte(txt, 50, 585 + i * 22,
                          self.ui.font_petit, (140, 140, 140))