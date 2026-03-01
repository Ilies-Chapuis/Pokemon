
import os
import pygame


class MenuPokedex:
    def __init__(self, screen, ui):
        self.screen = screen
        self.ui     = ui
        self._cache = {}

    def afficher(self, pokedex_manager, selection, all_pokemon):
        self.screen.fill((20, 30, 50))
        self._entete(pokedex_manager, len(all_pokemon))
        self._liste(all_pokemon, selection, pokedex_manager)
        self._detail(all_pokemon, selection, pokedex_manager)
        self.ui.texte_centre("↑↓: Naviguer  |  ESC: Retour", 500, 660,
                             self.ui.font_petit, (200, 200, 200))

    def _entete(self, pdex, total):
        self.ui.texte_centre("POKÉDEX", 500, 40, self.ui.font_titre, (255, 215, 0))
        stats = pdex.obtenir_stats()
        comp  = pdex.obtenir_completion(total)
        self.ui.texte_centre(
            f"Vus: {stats['vus']}/{total}  |  Capturés: {stats['captures']}/{total}  |  {comp:.1f}%",
            500, 75, self.ui.font_normal, (200, 200, 200))

    def _liste(self, all_pokemon, sel, pdex):
        start = max(0, sel - 10)
        for i, poke in enumerate(all_pokemon[start:start + 12]):
            idx = start + i
            nom = poke["name"]
            capture = pdex.est_capture(nom)
            vu      = pdex.est_vu(nom)
            y       = 120 + i * 42
            if idx == sel:
                pygame.draw.rect(self.screen, (255, 215, 0), (50, y - 5, 530, 40), 2)
            self.ui.texte(f"#{idx+1:03d}", 70, y + 5, self.ui.font_normal, (150, 150, 150))
            self._mini_image(nom, capture, vu, y)
            nom_aff = nom if (capture or vu) else "???"
            col     = (100, 255, 100) if capture else ((255, 255, 100) if vu else (100, 100, 100))
            statut  = "✓" if capture else ("👁" if vu else "?")
            self.ui.texte(nom_aff, 220, y + 5, self.ui.font_normal, col)
            self.ui.texte(statut,  520, y + 5, self.ui.font_normal, col)

    def _mini_image(self, nom, capture, vu, y):
        if capture or vu:
            img = self._img(nom, (30, 30))
            if img:
                if vu and not capture:
                    img = img.copy(); img.set_alpha(100)
                self.screen.blit(img, (170, y))
                return
        col = (100, 100, 100) if (capture or vu) else (50, 50, 50)
        pygame.draw.circle(self.screen, col, (185, y + 15), 15)
        if not (capture or vu):
            self.ui.texte("?", 180, y + 5, self.ui.font_petit, (150, 150, 150))

    def _detail(self, all_pokemon, sel, pdex):
        pygame.draw.rect(self.screen, (50, 50, 70),    (600, 120, 350, 500))
        pygame.draw.rect(self.screen, (100, 100, 120), (600, 120, 350, 500), 2)
        if not (0 <= sel < len(all_pokemon)):
            return
        poke    = all_pokemon[sel]
        nom     = poke["name"]
        capture = pdex.est_capture(nom)
        vu      = pdex.est_vu(nom)
        if not (capture or vu):
            self.ui.texte_centre("???", 775, 300, self.ui.font_titre, (100, 100, 100))
            pygame.draw.circle(self.screen, (50, 50, 50), (775, 360), 60)
            self.ui.texte_centre("Pokémon inconnu", 775, 440, couleur=(100, 100, 100))
            return
        self.ui.texte_centre(nom, 775, 140, self.ui.font_titre)
        img = self._img(nom, (120, 120))
        if img:
            if vu and not capture:
                img = img.copy(); img.set_alpha(150)
            self.screen.blit(img, img.get_rect(center=(775, 250)))
        else:
            pygame.draw.circle(self.screen, (100, 100, 100), (775, 250), 60)
        self.ui.texte_centre("Type: " + " / ".join(poke["type"]), 775, 330,
                             couleur=(200, 200, 200))
        if capture:
            s = poke["stats"]
            for i, label in enumerate([f"PV: {s['pv']}",
                                        f"Attaque: {s['attaque']}",
                                        f"Défense: {s['defense']}"]):
                self.ui.texte_centre(label, 775, 360 + i * 25,
                                     self.ui.font_petit, (200, 200, 200))
            if poke.get("legendary"):
                self.ui.texte_centre("★ LÉGENDAIRE ★", 775, 460, couleur=(255, 215, 0))
        else:
            self.ui.texte_centre("Capturez-le pour ses stats !", 775, 390,
                                 couleur=(150, 150, 150))

    def _img(self, nom, taille):
        cle = (nom, taille)
        if cle not in self._cache:
            racine = os.path.normpath(
                os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
            chemin = os.path.join(racine, "Data", "Assets", "pokemon", f"{nom}.png")
            if os.path.exists(chemin):
                try:
                    self._cache[cle] = pygame.transform.scale(
                        pygame.image.load(chemin), taille)
                except Exception:
                    self._cache[cle] = None
            else:
                self._cache[cle] = None
        return self._cache[cle]
