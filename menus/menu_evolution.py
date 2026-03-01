
import pygame


class MenuEvolution:
    def __init__(self, screen, ui):
        self.screen = screen
        self.ui     = ui

    def afficher(self, pokemon, nom_evolution):
        self.screen.fill((30, 20, 60))
        self.ui.texte_centre(" ÉVOLUTION DE DINGUE!", 500, 80,
                             self.ui.font_titre, (255, 215, 0))
        self.ui.texte_centre(
            f"{pokemon.nom} atteint le niveau {pokemon.niveau} !", 500, 220)
        self.ui.texte_centre(
            f"Il peut évoluer en  {nom_evolution} !", 500, 265,
            couleur=(180, 220, 255))
        self.ui.texte_centre("[O]  Accepter l'évolution", 500, 380,
                             couleur=(100, 255, 100))
        self.ui.texte_centre("[N]  Annuler", 500, 425,
                             couleur=(255, 100, 100))
