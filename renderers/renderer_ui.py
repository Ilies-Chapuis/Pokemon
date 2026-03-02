
import pygame
import os

def _trouver_dossier_sprites():

    import os
    base   = os.path.dirname(os.path.abspath(__file__))
    racine = os.path.normpath(os.path.join(base, ".."))
    cwd    = os.getcwd()
    candidats = [
        os.path.join(racine, "Assets", "pokemon"),
        os.path.join(racine, "Data", "Assets", "pokemon"),
        os.path.join(cwd, "Assets", "pokemon"),
        os.path.join(cwd, "Data", "Assets", "pokemon"),
        os.path.join(racine, "assets", "pokemon"),
        os.path.join(cwd, "assets", "pokemon"),
    ]
    for p in candidats:
        if os.path.isdir(p):
            return p
    return None


class RendererUI:
    #Boîte à outils graphique : texte, barres PV, images."""

    def __init__(self, screen, fonts):
        self.screen = screen
        self.font_titre  = fonts["titre"]
        self.font_normal = fonts["normal"]
        self.font_petit  = fonts["petit"]


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
    def charger_image(self, cache, nom_ou_poke, taille=(120, 120)):
        """Charge et met en cache le sprite d'un Pokémon.

        - Accepte un str ou un objet Pokémon.
        - Si l'objet a nom_sprite (Forme Ultime / GOD MODE), c'est lui qui
          sert à trouver le fichier — le sprite original est toujours affiché.
        - Ne mémorise PAS les échecs : si le dossier Assets/pokemon/ n'existe
          pas encore au premier frame, il sera retrouvé aux frames suivants.
        """
        import os

        # ── 1. Résoudre le nom de sprite ────────────────────────────────
        if hasattr(nom_ou_poke, "nom"):
            nom_sprite = getattr(nom_ou_poke, "nom_sprite", None) or nom_ou_poke.nom
        else:
            nom_sprite = str(nom_ou_poke)

        # Retirer les suffixes Forme Ultime
        for suffixe in (" GOD MODE", " ★"):
            nom_sprite = nom_sprite.replace(suffixe, "")
        nom_sprite = nom_sprite.strip()

        # ── 2. Cache HIT (seulement si valeur positive) ─────────────────
        if nom_sprite in cache and cache[nom_sprite] is not None:
            return cache[nom_sprite]

        # ── 3. Trouver le dossier sprites (re-testé à chaque miss) ──────
        dossier = _trouver_dossier_sprites()
        if dossier is None:
            return None   # dossier introuvable, on n'écrit rien en cache

        # ── 4. Essayer plusieurs variantes de nom de fichier ────────────
        chemins = [
            os.path.join(dossier, f"{nom_sprite}.png"),
            os.path.join(dossier, f"{nom_sprite.lower()}.png"),
            os.path.join(dossier, f"{nom_sprite.replace(' ', '_')}.png"),
        ]
        for chemin in chemins:
            if os.path.exists(chemin):
                try:
                    img = pygame.image.load(chemin).convert_alpha()
                    img = pygame.transform.scale(img, taille)
                    cache[nom_sprite] = img   # mémorise le succès
                    return img
                except Exception:
                    continue

        # Pas trouvé — NE PAS écrire None en cache
        # (laisse une chance au prochain frame si le fichier apparaît)
        return None

    def charger_arena(self, largeur, hauteur):
        """Charge l'image de fond d'arène par défaut."""
        return self._charger_background("defaut", largeur, hauteur)

    def charger_arena_zone(self, zone, largeur, hauteur):
        """Charge l'image de fond selon la zone de combat."""
        return self._charger_background(zone, largeur, hauteur)

    def _charger_background(self, zone, largeur, hauteur):
        #Cherche et charge un background selon la zone.
        import os
        racine = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
        base_data = os.path.join(racine, "Data", "Assets")

        # Noms de fichiers par zone
        noms_zone = {
            "ocean":   ["background_eau.png", "background_ocean.png", "arena_eau.png"],
            "foret":   ["background_foret.png", "arena_foret.png"],
            "montagne":["background_montagne.png", "arena_montagne.png"],
            "grotte":  ["background_grotte.png", "arena_grotte.png"],
            "ciel":    ["background_ciel.png", "arena_ciel.png"],
            "defaut":  ["arène_pokemon.png", "arene_pokemon.png", "arena_pokemon.png", "arena.png"],
            "prairie": ["background_prairie.png", "arena_prairie.png"],
        }
        # Noms à essayer : ceux de la zone + ceux par défaut en fallback
        noms = noms_zone.get(zone, []) + noms_zone["defaut"]

        dossiers = [racine, base_data, os.getcwd()]
        for d in dossiers:
            for n in noms:
                chemin = os.path.join(d, n)
                if os.path.exists(chemin):
                    try:
                        img = pygame.image.load(chemin)
                        return pygame.transform.scale(img, (largeur, hauteur))
                    except Exception:
                        continue
        return None
