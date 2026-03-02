
import pygame
from map.zones import ZONES



class RendererExploration:
    def __init__(self, screen, ui, taille_case=40):
        self.screen = screen
        self.ui = ui
        self.taille_case = taille_case
        self.offset_x = 50
        self.offset_y = 50
        self.font_normal = pygame.font.SysFont("Arial", 14, bold=True)
        self.font_petit  = pygame.font.SysFont("Arial", 11)


    def render(self, game):
        self._dessiner_carte(game.carte, game.joueur_x, game.joueur_y)
        self._dessiner_hud_zone(game)
        self._dessiner_hud_equipe(game)
        self._dessiner_champions(game)
        self._dessiner_instructions()


    def _dessiner_carte(self, carte, jx, jy):
        tc = self.taille_case
        ox, oy = self.offset_x, self.offset_y

        for y in range(carte.hauteur):
            for x in range(carte.largeur):
                zone_type = carte.grille[y][x]
                couleur = ZONES[zone_type]["couleur"]
                rect = pygame.Rect(ox + x * tc, oy + y * tc, tc, tc)
                pygame.draw.rect(self.screen, couleur, rect)
                pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)

        # Joueur
        cx = ox + jx * tc + tc // 2
        cy = oy + jy * tc + tc // 2
        pygame.draw.circle(self.screen, (255, 0, 0), (cx, cy), 15)

    def _dessiner_hud_zone(self, game):
        zone_type = game.carte.get_zone(game.joueur_x, game.joueur_y)
        info = ZONES[zone_type]
        ui = self.ui
        ui.texte(f"Zone: {info['nom']}",              850, 50,  ui.font_normal)
        ui.texte(f"Position: ({game.joueur_x}, {game.joueur_y})", 850, 80,  ui.font_petit)
        ui.texte(f"Potions: {game.potions}",          850, 110, ui.font_petit)
        ui.texte(f"Pokéballs: {game.pokeballs}",      850, 135, ui.font_petit)

    def _dessiner_hud_equipe(self, game):
        ui = self.ui
        ui.texte("Votre équipe:", 850, 200, ui.font_normal, (255, 215, 0))
        for i, pokemon in enumerate(game.equipe_joueur):
            y = 230 + i * 80
            ui.texte(f"{pokemon.nom} Nv.{pokemon.niveau}", 850, y, ui.font_petit)
            ui.barre_pv(pokemon, 850, y + 20, 120)
            ui.texte(f"ATK:{pokemon.attaque} DEF:{pokemon.defense}",
                     850, y + 45, ui.font_petit, (200, 200, 200))

    def _dessiner_champions(self, game):
        #Dessine les portraits/icônes des champions sur la carte.
        from champions import POSITION_CHAMPION_PLANTE, POSITION_CHAMPION_FEU, CHAMPIONS
        tc = self.taille_case
        postes = [
            ("plante", POSITION_CHAMPION_PLANTE, (50, 180, 80)),
            ("feu",    POSITION_CHAMPION_FEU,    (220, 80, 30)),
        ]
        for cid, (cx, cy), couleur in postes:
            px = cx * tc + tc // 2
            py = cy * tc + tc // 2
            # Cercle coloré
            pygame.draw.circle(self.screen, couleur, (px, py), tc // 2 - 2)
            pygame.draw.circle(self.screen, (255, 255, 255), (px, py), tc // 2 - 2, 2)
            # Lettre
            lettre = CHAMPIONS[cid]["nom"][0]
            t = self.font_normal.render(lettre, True, (255, 255, 255))
            self.screen.blit(t, t.get_rect(center=(px, py)))
            # Badge si déjà battu
            if hasattr(game, "champions_battus") and cid in game.champions_battus:
                b = self.font_petit.render("✦", True, (255, 215, 0))
                self.screen.blit(b, (px + tc//2 - 8, py - tc//2))

    def _dessiner_instructions(self):
        ui = self.ui
        ui.texte("Déplacement: Flèches ou ZQSD", 50, 650, ui.font_petit, (200, 200, 200))
        ui.texte("[H] Soigner | [E] Équipe | [R] Réserve (ville) | [G] Sauvegarder | [P] Pokédex | [ESC] Menu",
                 50, 670, ui.font_petit, (200, 200, 200))