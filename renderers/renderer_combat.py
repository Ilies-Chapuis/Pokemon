
import pygame
import math
import time


class Animation:
    def __init__(self, type_anim, cible_pos, couleur=(255, 255, 0), duree=0.5):
        self.type    = type_anim
        self.pos     = cible_pos
        self.couleur = couleur
        self.duree   = duree
        self.debut   = time.time()
        self.terminee = False

    @property
    def progression(self):
        return min(1.0, (time.time() - self.debut) / self.duree)

    def update(self):
        if self.progression >= 1.0:
            self.terminee = True


class RendererCombat:

    COULEURS_BTN = {
        "attaque":  ((70, 35, 10),  (255, 160,  60)),
        "special":  ((55, 15, 65),  (230,  80, 255)),
        "potion":   ((15, 60, 25),  ( 80, 230, 120)),
        "capturer": ((10, 40, 70),  ( 80, 190, 255)),
        "normal":   ((40, 40, 65),  (180, 180, 255)),
        "danger":   ((75, 15, 15),  (255,  70,  70)),
        "inactif":  ((28, 28, 30),  ( 70,  70,  70)),
    }

    # Définition des 6 boutons : (id, touche, action, style, colonne, ligne)

    BOUTONS_DEF = [
        ("attaque",  "A", "ATTAQUER",       "attaque",  0, 0),
        ("special",  "S", "ATT. SPÉCIALE",  "special",  1, 0),
        ("potion",   "P", "POTION",         "potion",   0, 1),
        ("capturer", "C", "CAPTURER",       "capturer", 1, 1),
        ("changer",  "X", "CHANGER",        "normal",   2, 0),
        ("fuir",     "F", "FUIR",           "danger",   2, 1),
    ]

    def __init__(self, screen, ui, images_cache, arena_background):
        self.screen = screen
        self.ui     = ui
        self.images_cache = images_cache
        self.arena  = arena_background
        self.W, self.H = screen.get_size()

        self.font_btn     = pygame.font.SysFont("Arial", 15, bold=True)
        self.font_key     = pygame.font.SysFont("Arial", 12)

        self.animations: list[Animation] = []

        self.POS_SAUVAGE = (320, 430)
        self.POS_JOUEUR  = (720, 430)

        # Dimensions de la zone boutons
        self.ZONE_H   = 110      # hauteur totale de la bande boutons
        self.ZONE_Y   = self.H - self.ZONE_H   # y de départ de la bande
        self.BTN_W    = 190
        self.BTN_H    = 44
        self.BTN_GAP  = 8
        self.BTN_MX   = 12      # marge gauche

        # Calcul des rects cliquables (mis à jour à chaque render)
        self._rects_boutons = {}   # id -> pygame.Rect


    # API merci le cours


    def declencher_animation(self, type_anim, cible="sauvage"):
        pos = self.POS_SAUVAGE if cible == "sauvage" else self.POS_JOUEUR
        couleurs = {"attaque": (255, 200, 50), "ko": (255, 50, 50),
                    "flash": (255, 255, 255), "capture": (100, 180, 255)}
        durees   = {"attaque": 0.45, "ko": 0.8, "flash": 0.3, "capture": 0.6}
        self.animations.append(Animation(
            type_anim, pos,
            couleurs.get(type_anim, (255, 255, 255)),
            durees.get(type_anim, 0.4)
        ))

    def update(self):
        for a in self.animations:
            a.update()
        self.animations = [a for a in self.animations if not a.terminee]

    @property
    def animation_en_cours(self):
        return bool(self.animations)

    def get_action_clic(self, pos_souris):
        #Retourne l'id du bouton cliqué, ou None
        for btn_id, rect in self._rects_boutons.items():
            if rect.collidepoint(pos_souris):
                return btn_id
        return None


    # Rendu 1er

    def render(self, game):
        if not game.combat_actuel:
            return
        self.update()
        self._fond()
        self._dessiner_pokemon_sauvage(game.pokemon_sauvage)
        self._dessiner_pokemon_joueur(game.combat_actuel.pokemon_joueur)
        self._dessiner_animations()
        self._interface(game)


    # Fond et pokemon

    def _fond(self):
        if self.arena:
            self.screen.blit(self.arena, (0, 0))
        else:
            pygame.draw.rect(self.screen, (40, 40, 60), (0, 0, self.W, self.H))

    def _dessiner_pokemon_sauvage(self, poke):
        px, py = self.POS_SAUVAGE
        px += self._offset_tremblement("sauvage")
        img = self.ui.charger_image(self.images_cache, poke.nom, (120, 120))
        if img:
            if self._anim_active("ko", "sauvage"):
                img = self._flash_img(img)
            self.screen.blit(img, img.get_rect(center=(px, py)))
        else:
            pygame.draw.circle(self.screen, (255, 100, 100), (px, py), 55)
        self.ui.texte(f"{poke.nom} Nv.{poke.niveau}", 15, 75, couleur=(255, 255, 255))
        if poke.legendary:
            self.ui.texte("★ LÉGENDAIRE ★", 15, 98, self.ui.font_petit, (255, 215, 0))
        self.ui.barre_pv(poke, 15, 120, 250)

    def _dessiner_pokemon_joueur(self, poke):
        px, py = self.POS_JOUEUR
        px += self._offset_tremblement("joueur")
        img = self.ui.charger_image(self.images_cache, poke.nom, (120, 120))
        if img:
            if self._anim_active("ko", "joueur"):
                img = self._flash_img(img)
            img_f = pygame.transform.flip(img, True, False)
            self.screen.blit(img_f, img_f.get_rect(center=(px, py)))
        else:
            pygame.draw.circle(self.screen, (100, 255, 100), (px, py), 55)
        self.ui.texte(f"Votre {poke.nom} Nv.{poke.niveau}", 720, 75, couleur=(255, 255, 255))
        self.ui.barre_pv(poke, 720, 105, 265)


    # Animation merci tuto


    def _dessiner_animations(self):
        for anim in self.animations:
            p = anim.progression
            if   anim.type == "attaque": self._anim_attaque(anim, p)
            elif anim.type == "ko":      self._anim_ko(anim, p)
            elif anim.type == "flash":   self._anim_flash(p)
            elif anim.type == "capture": self._anim_capture(anim, p)

    def _anim_attaque(self, anim, p):
        cx, cy = anim.pos
        for i in range(8):
            angle = (2 * math.pi / 8) * i
            dist  = int(110 * (1 - p))
            x = cx + int(math.cos(angle) * dist)
            y = cy + int(math.sin(angle) * dist)
            r = max(2, int(11 * (1 - p)))
            s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*anim.couleur, int(255*(1-p))), (r,r), r)
            self.screen.blit(s, (x-r, y-r))
        if p > 0.7:
            ip = (p - 0.7) / 0.3
            ri = int(55 * ip)
            s  = pygame.Surface((ri*2+1, ri*2+1), pygame.SRCALPHA)
            pygame.draw.circle(s, (*anim.couleur, int(180*(1-ip))), (ri,ri), ri)
            self.screen.blit(s, (cx-ri, cy-ri))

    def _anim_ko(self, anim, p):
        cx, cy = anim.pos
        t = int(75 * p)
        s = pygame.Surface((t*2+1, t*2+1), pygame.SRCALPHA)
        a = int(255 * (1 - p*0.5))
        pygame.draw.line(s, (255,50,50,a), (0,0), (t*2,t*2), 5)
        pygame.draw.line(s, (255,50,50,a), (t*2,0), (0,t*2), 5)
        self.screen.blit(s, (cx-t, cy-t))
        for i in range(5):
            angle = (2*math.pi/5)*i
            d = int(90*p)
            x = cx + int(math.cos(angle)*d)
            y = cy + int(math.sin(angle)*d)
            r = max(1, int(13*(1-p)))
            sc = pygame.Surface((r*2,r*2), pygame.SRCALPHA)
            pygame.draw.circle(sc, (255,100,50,int(200*(1-p))), (r,r), r)
            self.screen.blit(sc, (x-r, y-r))

    def _anim_flash(self, p):
        a = int(160 * math.sin(p * math.pi))
        s = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        s.fill((255,255,255,a))
        self.screen.blit(s, (0,0))

    def _anim_capture(self, anim, p):
        cx, cy = anim.pos
        r = int(38 * (1 - p*0.5))
        s = pygame.Surface((r*2+2, r*2+2), pygame.SRCALPHA)
        a = int(255*(1-p))
        pygame.draw.circle(s, (210,50,50,a), (r,r), r)
        pygame.draw.rect(s, (20,20,20,a), (0,r-3,r*2,6))
        pygame.draw.circle(s, (240,240,240,a), (r,r), r//3)
        rot = pygame.transform.rotate(s, p*360)
        self.screen.blit(rot, rot.get_rect(center=(cx,cy)))


    # HELPERS ANIMATION


    def _anim_active(self, type_anim, cible):
        pos = self.POS_SAUVAGE if cible == "sauvage" else self.POS_JOUEUR
        return any(a.type == type_anim and a.pos == pos for a in self.animations)

    def _offset_tremblement(self, cible):
        pos = self.POS_SAUVAGE if cible == "sauvage" else self.POS_JOUEUR
        for a in self.animations:
            if a.type == "attaque" and a.pos == pos and a.progression > 0.6:
                p = a.progression
                return int(math.sin(p * 40) * 7 * (1-p))
        return 0

    def _flash_img(self, img):
        f = img.copy()
        f.fill((255,255,255,140), special_flags=pygame.BLEND_RGBA_ADD)
        return f


    def _interface(self, game):
        if not game.combat_actuel.termine:
            self._bande_logs(game)
            self._bande_boutons(game)
        elif hasattr(game, 'etat_ko') and game.etat_ko:
            self._panneau_changement(game)
        else:
            self._ecran_fin(game)


    def _bande_logs(self, game):
        #Fine bande de logs juste au-dessus des boutons
        log_h = 55
        log_y = self.ZONE_Y - log_h
        fond = pygame.Surface((self.W, log_h), pygame.SRCALPHA)
        fond.fill((5, 5, 15, 190))
        self.screen.blit(fond, (0, log_y))
        pygame.draw.line(self.screen, (60,60,100), (0, log_y), (self.W, log_y), 1)

        logs = game.combat_actuel.get_derniers_logs(2)
        for i, log in enumerate(logs):
            gris = 140 + i * 60
            self.ui.texte(log, 15, log_y + 6 + i * 23,
                          self.ui.font_petit, (gris, gris, gris))


    def _bande_boutons(self, game):
        #Bande compacte en bas avec 6 boutons sur 2 lignes × 3 colonnes
        # Fond
        fond = pygame.Surface((self.W, self.ZONE_H), pygame.SRCALPHA)
        fond.fill((8, 8, 18, 220))
        self.screen.blit(fond, (0, self.ZONE_Y))
        pygame.draw.line(self.screen, (70,70,110),
                         (0, self.ZONE_Y), (self.W, self.ZONE_Y), 2)

        self._rects_boutons.clear()

        actifs = {
            "potion":   game.potions > 0,
            "capturer": game.pokeballs > 0,
            "changer":  bool(game.equipe_joueur),
        }

        for btn_id, touche, label, style, col, row in self.BOUTONS_DEF:
            actif = actifs.get(btn_id, True)

            # Position
            x = self.BTN_MX + col * (self.BTN_W + self.BTN_GAP)
            y = self.ZONE_Y + 8 + row * (self.BTN_H + self.BTN_GAP)

            # Label dynamique (compteurs)
            if btn_id == "potion":
                label = f"POTION ({game.potions})"
            elif btn_id == "capturer":
                label = f"CAPTURER ({game.pokeballs})"

            rect = pygame.Rect(x, y, self.BTN_W, self.BTN_H)
            self._rects_boutons[btn_id] = rect
            self._dessiner_bouton(rect, touche, label, style, actif)


    def _dessiner_bouton(self, rect, touche, label, style, actif):
        s = "inactif" if not actif else style
        fond_col, txt_col = self.COULEURS_BTN[s]

        # Fond
        surf = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        surf.fill((*fond_col, 230))
        self.screen.blit(surf, rect.topleft)

        # Bordure
        pygame.draw.rect(self.screen, txt_col if actif else (50,50,55),
                         rect, 2, border_radius=5)

        # Badge touche
        bw, bh = 22, 18
        bx, by = rect.x + 5, rect.y + (rect.h - bh)//2
        badge = pygame.Surface((bw, bh), pygame.SRCALPHA)
        badge.fill((*txt_col, 50) if actif else (35,35,35,100))
        self.screen.blit(badge, (bx, by))
        pygame.draw.rect(self.screen, txt_col if actif else (50,50,55),
                         (bx, by, bw, bh), 1, border_radius=3)
        tk = self.font_key.render(touche, True, txt_col if actif else (60,60,60))
        self.screen.blit(tk, tk.get_rect(center=(bx + bw//2, by + bh//2)))

        # Label
        tl = self.font_btn.render(label, True, txt_col if actif else (60,60,60))
        self.screen.blit(tl, tl.get_rect(center=(rect.x + rect.w//2 + 12, rect.centery)))


    def _panneau_changement(self, game):
        fond = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        fond.fill((0,0,0,155))
        self.screen.blit(fond, (0,0))

        pw, ph = 560, 380
        px = (self.W - pw)//2
        py = (self.H - ph)//2
        pan = pygame.Surface((pw, ph), pygame.SRCALPHA)
        pan.fill((18, 18, 38, 245))
        self.screen.blit(pan, (px, py))
        pygame.draw.rect(self.screen, (255,70,70), (px,py,pw,ph), 2, border_radius=8)

        self.ui.texte_centre(
            f"{game.combat_actuel.pokemon_joueur.nom} est K.O. !",
            self.W//2, py+28, self.ui.font_titre, (255,80,80))
        self.ui.texte_centre("Choisissez un remplaçant :",
            self.W//2, py+68, couleur=(210,210,210))

        vivants = [(i,p) for i,p in enumerate(game.equipe_joueur)
                   if p.est_vivant() and i != 0]

        if not vivants:
            self.ui.texte_centre("Toute l'équipe est K.O. comme moi !",
                self.W//2, py+180, couleur=(255,100,100))
            self.ui.texte_centre("[ESPACE] Accepter la défaite",
                self.W//2, py+220, self.ui.font_petit, (180,180,180))
            return

        for j, (idx, poke) in enumerate(vivants[:4]):
            lx = px+25
            ly = py+100+j*62
            sel = (j == game.selection_ko)
            bg  = pygame.Surface((pw-50, 52), pygame.SRCALPHA)
            bg.fill((50,75,50,180) if sel else (28,28,48,150))
            self.screen.blit(bg, (lx, ly))
            if sel:
                pygame.draw.rect(self.screen,(90,255,90),(lx,ly,pw-50,52),2,border_radius=4)
            num = self.font_btn.render(f"[{j+1}]", True,
                                       (90,255,90) if sel else (130,130,130))
            self.screen.blit(num, (lx+8, ly+15))
            c = (90,255,90) if sel else (230,230,230)
            self.ui.texte(f"{poke.nom}  Nv.{poke.niveau}", lx+45, ly+6, couleur=c)
            self.ui.texte("/".join(poke.types), lx+45, ly+28,
                          self.ui.font_petit, (160,160,160))
            self.ui.barre_pv(poke, lx+260, ly+16, 200)

        self.ui.texte_centre("↑↓ Naviguer  |  ENTRÉE Envoyer",
            self.W//2, py+ph-30, self.ui.font_petit, (130,130,130))


    # C'est fini


    def _ecran_fin(self, game):
        fond = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        fond.fill((0,0,0,140))
        self.screen.blit(fond, (0,0))

        if game.combat_actuel.pokemon_capture:
            msg, col = f"{game.pokemon_sauvage.nom} CAPTURÉ !", (255, 215, 0)
        elif game.combat_actuel.joueur_gagne:
            msg, col = "VICTOIRE !", (100, 255, 100)
        else:
            msg, col = "DÉFAITE...", (255, 80, 80)

        self.ui.texte_centre(msg, self.W//2, self.H//2-40,
                             self.ui.font_titre, col)
        self.ui.texte_centre("[ESPACE] Continuer", self.W//2, self.H//2+20,
                             couleur=(200,200,200))
