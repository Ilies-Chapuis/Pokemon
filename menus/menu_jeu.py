"""Menus in-game : équipe, réserve, pokédex, évolution"""

import json
import os
import pygame
from Evolution import peut_forme_ultime, NIVEAU_FORME_ULTIME


class MenuEquipe:
    def __init__(self, screen, ui):
        self.screen = screen
        self.ui = ui

    def afficher(self, equipe, selection):
        self.screen.fill((30, 30, 50))
        self.ui.texte_centre("VOTRE ÉQUIPE", 500, 50, self.ui.font_titre, (255, 215, 0))
        for i, pokemon in enumerate(equipe):
            self._ligne(pokemon, i, i == selection)
        self._instructions()

    def _ligne(self, pokemon, i, selectionne):
        y = 120 + i * 90
        if selectionne:
            pygame.draw.rect(self.screen, (100, 255, 100), (50, y - 10, 900, 80), 3)
        if i == 0:
            self.ui.texte("★", 70, y + 10, self.ui.font_titre, (255, 215, 0))
        couleur = (255, 100, 100) if not pokemon.est_vivant() else (255, 255, 255)
        self.ui.texte(f"{pokemon.nom} Nv.{pokemon.niveau}", 120, y, couleur=couleur)
        self.ui.texte(" / ".join(pokemon.types), 120, y + 25, self.ui.font_petit, (200, 200, 200))
        self.ui.barre_pv(pokemon, 400, y + 15, 300)
        self.ui.texte(f"ATK:{pokemon.attaque} DEF:{pokemon.defense}",
                      750, y + 15, self.ui.font_petit, (200, 200, 200))
        if not pokemon.est_vivant():
            self.ui.texte("K.O.", 850, y + 15, couleur=(255, 50, 50))
        elif peut_forme_ultime(pokemon):
            self.ui.texte("✦ FORME ULTIME DISPO", 820, y + 15,
                          self.ui.font_petit, (255, 215, 0))

    def _instructions(self):
        for i, txt in enumerate([
            "↑↓ : Naviguer",
            "ENTRÉE : Changer actif",
            "[U] : Forme Ultime (si disponible)",
            "ESC : Retour"
        ]):
            self.ui.texte(txt, 50, 590 + i * 22, self.ui.font_petit, (150, 150, 150))


# --------------------------------------------------------------------------- #
class MenuReserve:
    def __init__(self, screen, ui):
        self.screen = screen
        self.ui = ui

    def afficher(self, equipe, reserve, sel_equipe, sel_reserve, mode):
        self.screen.fill((20, 30, 50))
        self.ui.texte_centre("GESTION DE LA RÉSERVE", 500, 40,
                             self.ui.font_titre, (255, 215, 0))
        self.ui.texte_centre(
            f"Équipe: {len(equipe)}/6 | Réserve: {len(reserve)}", 500, 75,
            self.ui.font_petit, (200, 200, 200))

        self._colonne_equipe(equipe, sel_equipe, mode)
        self._colonne_reserve(reserve, sel_reserve, mode)
        self._instructions()

    def _colonne_equipe(self, equipe, selection, mode):
        actif = (mode == "equipe")
        couleur_label = (100, 255, 100) if actif else (150, 150, 150)
        couleur_cadre = (100, 255, 100) if actif else (100, 100, 100)
        self.ui.texte("ÉQUIPE ACTIVE", 50, 120, couleur=couleur_label)
        pygame.draw.rect(self.screen, couleur_cadre, (40, 150, 420, 450), 2)
        for i, poke in enumerate(equipe):
            y = 160 + i * 75
            if actif and i == selection:
                pygame.draw.rect(self.screen, (255, 215, 0), (50, y - 5, 400, 70), 2)
            if i == 0:
                self.ui.texte("★", 60, y + 10, self.ui.font_titre, (255, 215, 0))
            c = (255, 100, 100) if not poke.est_vivant() else (255, 255, 255)
            self.ui.texte(f"{poke.nom} Nv.{poke.niveau}", 100, y, couleur=c)
            self.ui.texte(" / ".join(poke.types), 100, y + 25, self.ui.font_petit, (200, 200, 200))
            self.ui.barre_pv(poke, 270, y + 10, 150)

    def _colonne_reserve(self, reserve, selection, mode):
        actif = (mode == "reserve")
        couleur_label = (100, 200, 255) if actif else (150, 150, 150)
        couleur_cadre = (100, 200, 255) if actif else (100, 100, 100)
        self.ui.texte(f"RÉSERVE ({len(reserve)})", 530, 120, couleur=couleur_label)
        pygame.draw.rect(self.screen, couleur_cadre, (520, 150, 420, 450), 2)

        if not reserve:
            self.ui.texte_centre("Aucun Pokémon en réserve", 730, 320,
                                 self.ui.font_normal, (150, 150, 150))
            return

        start = max(0, selection - 5)
        for i, poke in enumerate(reserve[start:start + 6]):
            idx = start + i
            y = 160 + i * 75
            if actif and idx == selection:
                pygame.draw.rect(self.screen, (255, 215, 0), (530, y - 5, 400, 70), 2)
            c = (255, 100, 100) if not poke.est_vivant() else (255, 255, 255)
            self.ui.texte(f"{poke.nom} Nv.{poke.niveau}", 540, y, couleur=c)
            self.ui.texte(" / ".join(poke.types), 540, y + 25, self.ui.font_petit, (200, 200, 200))
            self.ui.barre_pv(poke, 710, y + 10, 150)

    def _instructions(self):
        for i, txt in enumerate(["TAB: Changer de colonne | ↑↓: Naviguer",
                                  "ENTRÉE: Échanger Équipe ↔ Réserve | ESC: Retour"]):
            self.ui.texte_centre(txt, 500, 615 + i * 25, self.ui.font_petit, (200, 200, 200))


# --------------------------------------------------------------------------- #
class MenuPokedex:
    def __init__(self, screen, ui):
        self.screen = screen
        self.ui = ui
        self._cache = {}

    def afficher(self, pokedex_manager, selection, all_pokemon):
        self.screen.fill((20, 30, 50))
        self._entete(pokedex_manager, len(all_pokemon))
        self._liste(all_pokemon, selection, pokedex_manager)
        self._detail(all_pokemon, selection, pokedex_manager)
        self.ui.texte_centre("↑↓: Naviguer | ESC: Retour", 500, 660,
                             self.ui.font_petit, (200, 200, 200))

    def _entete(self, pdex, total):
        self.ui.texte_centre("POKÉDEX", 500, 40, self.ui.font_titre, (255, 215, 0))
        stats = pdex.obtenir_stats()
        comp  = pdex.obtenir_completion(total)
        txt = f"Vus: {stats['vus']}/{total}  |  Capturés: {stats['captures']}/{total}  |  {comp:.1f}%"
        self.ui.texte_centre(txt, 500, 75, self.ui.font_normal, (200, 200, 200))

    def _liste(self, all_pokemon, selection, pdex):
        start = max(0, selection - 10)
        y = 120
        for i, poke in enumerate(all_pokemon[start:start + 12]):
            idx = start + i
            nom = poke["name"]
            capture = pdex.est_capture(nom)
            vu      = pdex.est_vu(nom)
            if idx == selection:
                pygame.draw.rect(self.screen, (255, 215, 0), (50, y - 5, 530, 40), 2)
            self.ui.texte(f"#{idx+1:03d}", 70, y + 5, self.ui.font_normal, (150, 150, 150))
            self._mini_image(nom, capture, vu, y)
            nom_aff  = nom if (capture or vu) else "???"
            couleur  = (100, 255, 100) if capture else ((255, 255, 100) if vu else (100, 100, 100))
            statut   = "✓" if capture else ("👁" if vu else "?")
            self.ui.texte(nom_aff, 220, y + 5, self.ui.font_normal, couleur)
            self.ui.texte(statut,  520, y + 5, self.ui.font_normal, couleur)
            y += 42

    def _mini_image(self, nom, capture, vu, y):
        if capture or vu:
            img = self._img(nom, (30, 30))
            if img:
                if vu and not capture:
                    img = img.copy(); img.set_alpha(100)
                self.screen.blit(img, (170, y))
                return
        couleur = (100, 100, 100) if (capture or vu) else (50, 50, 50)
        pygame.draw.circle(self.screen, couleur, (185, y + 15), 15)
        if not (capture or vu):
            self.ui.texte("?", 180, y + 5, self.ui.font_petit, (150, 150, 150))

    def _detail(self, all_pokemon, selection, pdex):
        pygame.draw.rect(self.screen, (50, 50, 70),   (600, 120, 350, 500))
        pygame.draw.rect(self.screen, (100, 100, 120), (600, 120, 350, 500), 2)
        if not (0 <= selection < len(all_pokemon)):
            return
        poke = all_pokemon[selection]
        nom  = poke["name"]
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

        self.ui.texte_centre("Type: " + " / ".join(poke["type"]), 775, 330, couleur=(200, 200, 200))

        if capture:
            s = poke["stats"]
            for i, label in enumerate([f"PV: {s['pv']}", f"Attaque: {s['attaque']}", f"Défense: {s['defense']}"]):
                self.ui.texte_centre(label, 775, 360 + i * 25, self.ui.font_petit, (200, 200, 200))
            if poke.get("legendary"):
                self.ui.texte_centre("★ LÉGENDAIRE ★", 775, 460, couleur=(255, 215, 0))
        else:
            self.ui.texte_centre("Capturez-le pour ses stats !", 775, 390, couleur=(150, 150, 150))

    def _img(self, nom, taille):
        cle = (nom, taille)
        if cle in self._cache:
            return self._cache[cle]
        chemin = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Data", "Assets", "pokemon", f"{nom}.png")
        if os.path.exists(chemin):
            try:
                img = pygame.transform.scale(pygame.image.load(chemin), taille)
                self._cache[cle] = img
                return img
            except Exception:
                pass
        return None



class MenuEvolution:
    def __init__(self, screen, ui):
        self.screen = screen
        self.ui = ui

    def afficher(self, pokemon, nom_evolution):
        self.screen.fill((30, 20, 60))
        self.ui.texte_centre("OH COMME IL EST MIGNON", 500, 100,
                             self.ui.font_titre, (255, 215, 0))
        self.ui.texte_centre(
            f"{pokemon.nom} atteint le niveau {pokemon.niveau} !", 500, 250)
        self.ui.texte_centre(
            f"Il peut évoluer en {nom_evolution} !", 500, 290)
        self.ui.texte_centre("[O] Accepter l'évolution", 500, 400,
                             couleur=(100, 255, 100))
        self.ui.texte_centre("[N] Annuler", 500, 440,
                             couleur=(255, 100, 100))
