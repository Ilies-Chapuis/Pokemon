
import pygame


class MenuReserve:
    def __init__(self, screen, ui):
        self.screen = screen
        self.ui     = ui

    def afficher(self, equipe, reserve, sel_equipe, sel_reserve, mode):
        self.screen.fill((20, 30, 50))
        self.ui.texte_centre("GESTION DE LA RÉSERVE", 500, 40,
                             self.ui.font_titre, (255, 215, 0))
        self.ui.texte_centre(
            f"Équipe: {len(equipe)}/6  |  Réserve: {len(reserve)}", 500, 75,
            self.ui.font_petit, (200, 200, 200))
        self._colonne_equipe(equipe, sel_equipe, mode)
        self._colonne_reserve(reserve, sel_reserve, mode)
        self._instructions()

    def _colonne_equipe(self, equipe, sel, mode):
        actif = (mode == "equipe")
        col_l = (100, 255, 100) if actif else (150, 150, 150)
        col_c = (100, 255, 100) if actif else (100, 100, 100)
        self.ui.texte("ÉQUIPE ACTIVE", 50, 120, couleur=col_l)
        pygame.draw.rect(self.screen, col_c, (40, 150, 420, 450), 2)
        for i, poke in enumerate(equipe):
            y = 160 + i * 75
            if actif and i == sel:
                pygame.draw.rect(self.screen, (255, 215, 0), (50, y - 5, 400, 70), 2)
            if i == 0:
                self.ui.texte("★", 60, y + 10, self.ui.font_titre, (255, 215, 0))
            c = (255, 100, 100) if not poke.est_vivant() else (255, 255, 255)
            self.ui.texte(f"{poke.nom}  Nv.{poke.niveau}", 100, y, couleur=c)
            self.ui.texte(" / ".join(poke.types), 100, y + 25,
                          self.ui.font_petit, (200, 200, 200))
            self.ui.barre_pv(poke, 270, y + 10, 150)

    def _colonne_reserve(self, reserve, sel, mode):
        actif = (mode == "reserve")
        col_l = (100, 200, 255) if actif else (150, 150, 150)
        col_c = (100, 200, 255) if actif else (100, 100, 100)
        self.ui.texte(f"RÉSERVE ({len(reserve)})", 530, 120, couleur=col_l)
        pygame.draw.rect(self.screen, col_c, (520, 150, 420, 450), 2)
        if not reserve:
            self.ui.texte_centre("Aucun Pokémon en réserve! libérer moi !", 730, 320,
                                 self.ui.font_normal, (150, 150, 150))
            return
        start = max(0, sel - 5)
        for i, poke in enumerate(reserve[start:start + 6]):
            idx = start + i
            y   = 160 + i * 75
            if actif and idx == sel:
                pygame.draw.rect(self.screen, (255, 215, 0), (530, y - 5, 400, 70), 2)
            c = (255, 100, 100) if not poke.est_vivant() else (255, 255, 255)
            self.ui.texte(f"{poke.nom}  Nv.{poke.niveau}", 540, y, couleur=c)
            self.ui.texte(" / ".join(poke.types), 540, y + 25,
                          self.ui.font_petit, (200, 200, 200))
            self.ui.barre_pv(poke, 710, y + 10, 150)

    def _instructions(self):
        lignes = ["TAB: Changer de colonne  |  ↑↓: Naviguer",
                  "ENTRÉE: Échanger Équipe ↔ Réserve  |  ESC: Retour"]
        for i, txt in enumerate(lignes):
            self.ui.texte_centre(txt, 500, 615 + i * 25,
                                 self.ui.font_petit, (200, 200, 200))
