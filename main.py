
import pygame
import sys
import os
import json

from pokemon import Pokemon
from menus import Menu, MenuOptions, MenuStarter




def _chemin_json():
    #Retourne le chemin absolu vers pokemon.json car pas le choix
    import os
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "Data", "pokemon.json")


class Application:
    def __init__(self):
        pygame.init()
        self.largeur_ecran = 1000
        self.hauteur_ecran = 700
        self.screen = pygame.display.set_mode((self.largeur_ecran, self.hauteur_ecran))
        pygame.display.set_caption("Pokémon JVSI - Édition Aventure")

        self.font_titre  = pygame.font.SysFont("Arial", 48, bold=True)
        self.font_normal = pygame.font.SysFont("Arial", 24)
        self.clock = pygame.time.Clock()

        self.pokedex = self._charger_pokedex()
        self.etat    = "menu_principal"
        self.game    = None
        self._game_pokedex = None  # instance simpliste pour le pokédex du menu

        self.menu_principal = Menu(self.screen, self.font_titre, self.font_normal)
        self.menu_options   = MenuOptions(self.screen, self.font_titre, self.font_normal)
        self.menu_starter   = None


    # INITIALISATION

    def _charger_pokedex(self):
        # Chercher pokemon.json dans le dossier du projet
        chemin = _chemin_json()
        try:
            with open(chemin, "r", encoding="utf-8") as f:
                data = json.load(f)
            pokedex = {p["name"]: p for p in data["pokemon"]}
            print(f" Pokédex chargé, oui je suis en dépression: {len(pokedex)} Pokémon")
            return pokedex
        except Exception as e:
            print(f" Erreur chargement Pokédex: {e}")
            return {}

    # ACTIONS

    def nouvelle_partie(self):
        self.etat = "choix_starter"
        self.menu_starter = MenuStarter(self.screen, self.font_titre, self.font_normal, self.pokedex)

    def continuer_partie(self):
        from game import Game
        from save_manager import SaveManager
        save = SaveManager()
        if not save.existe_sauvegarde():
            print(" Aucune sauvegarde — nouvelle partie. A l'aide pitié")
            self.nouvelle_partie(); return
        data = save.charger()
        if not data:
            print(" Sauvegarde illisible — nouvelle partie.")
            self.nouvelle_partie(); return
        self.game = Game()
        if self.game.charger_partie(data):
            self.etat = "jeu"
            print(f" Partie chargée, je suis fatigué: {data['date']}")
        else:
            self.nouvelle_partie()

    def lancer_jeu(self, nom_starter):
        from game import Game
        self.game = Game()
        if nom_starter in self.pokedex:
            starter = Pokemon.from_pokedex(self.pokedex[nom_starter], 5)
            self.game.equipe_joueur = [starter]
            print(f" Partie lancée avec {nom_starter} eh ben vous continué à lire")
        self.etat = "jeu"

    def lancer_createur(self):
        print("\n Lancement du Créateur de Pokémon... héhé mon bébé\n")
        pygame.quit()
        try:
            from ajout import AjoutPokemon
            AjoutPokemon().run()
        except Exception as e:
            print(f" Erreur créateur,je suis plus rouge que mes cheveux: {e}")
            import traceback; traceback.print_exc()
        pygame.init()
        self.screen = pygame.display.set_mode((self.largeur_ecran, self.hauteur_ecran))
        pygame.display.set_caption("Pokémon FRAUDE - Édition Aventure FRAUDULEUSE")
        self.etat = "menu_principal"

    def ouvrir_pokedex_menu(self):
        #Ouvre la page graphique du Pokédex depuis le menu principal.
        from game import Game
        from Pokedex_manager import PokedexManager

        pdex  = PokedexManager()
        stats = pdex.obtenir_stats()
        with open(_chemin_json(), "r", encoding="utf-8") as f:
            total = len(json.load(f)["pokemon"])
        comp = pdex.obtenir_completion(total)

        print("\n" + "=" * 50)
        print("  POKÉDEX")
        print("=" * 50)
        print(f"  Vus: {stats['vus']}/{total}")
        print(f"  Capturés: {stats['captures']}/{total}")
        print(f"  Complétion: {comp:.1f}%")
        print("=" * 50)
        print("\n[ESC] Retour au menu")

        if self._game_pokedex is None:
            self._game_pokedex = Game()
        self._game_pokedex.selection_pokedex = 0
        self.etat = "pokedex_menu"


    # Gestion des évènements

    def _gerer_menu_principal(self, event):
        if event.type != pygame.KEYDOWN:
            return True
        if event.key == pygame.K_UP:
            self.menu_principal.naviguer(-1)
        elif event.key == pygame.K_DOWN:
            self.menu_principal.naviguer(1)
        elif event.key == pygame.K_RETURN:
            actions = {
                "Nouvelle partie":      self.nouvelle_partie,
                "Continuer":            self.continuer_partie,
                "Créateur de Pokémon":  self.lancer_createur,
                "Pokédex":              self.ouvrir_pokedex_menu,
                "Options":              lambda: setattr(self, "etat", "options"),
                "Quitter":              lambda: None,
            }
            choix = self.menu_principal.obtenir_choix()
            if choix == "Quitter":
                return False
            actions.get(choix, lambda: None)()
        return True

    def _gerer_menu_options(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.menu_options.naviguer(-1)
            elif event.key == pygame.K_DOWN:
                self.menu_options.naviguer(1)
            elif event.key == pygame.K_LEFT:
                self.menu_options.modifier(-1)
            elif event.key == pygame.K_RIGHT:
                self.menu_options.modifier(1)
            elif event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                self.etat = "menu_principal"
        return True

    def _gerer_choix_starter(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.menu_starter.naviguer(-1)
            elif event.key == pygame.K_RIGHT:
                self.menu_starter.naviguer(1)
            elif event.key == pygame.K_RETURN:
                self.lancer_jeu(self.menu_starter.obtenir_choix())
            elif event.key == pygame.K_ESCAPE:
                self.etat = "menu_principal"
        return True

    def _gerer_pokedex_menu(self, event):
        if event.type == pygame.KEYDOWN:
            with open(_chemin_json(), "r", encoding="utf-8") as f:
                total = len(json.load(f)["pokemon"])
            if event.key == pygame.K_UP:
                self._game_pokedex.selection_pokedex = max(0, self._game_pokedex.selection_pokedex - 1)
            elif event.key == pygame.K_DOWN:
                self._game_pokedex.selection_pokedex = min(total - 1, self._game_pokedex.selection_pokedex + 1)
            elif event.key == pygame.K_ESCAPE:
                print("↩ Retour au menu principal")
                self.etat = "menu_principal"
        return True

    def _gerer_jeu(self, event):
        if not self.game:
            return True
        g = self.game
        # ESC depuis l'exploration uniquement → menu principal
        if g.etat == "exploration":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.etat = "menu_principal"
                self.game = None
                return True
            g.gerer_input_exploration(event)
        elif g.etat == "combat":
            g.gerer_input_combat(event)
        elif g.etat == "menu_equipe":
            g.gerer_input_menu_equipe(event)
        elif g.etat == "menu_reserve":
            g.gerer_input_menu_reserve(event)
        elif g.etat == "pokedex":
            g.gerer_input_pokedex(event)
        elif g.etat == "evolution":
            g.gerer_input_evolution(event)
        elif g.etat == "forme_ultime":
            g.gerer_input_forme_ultime(event)
        elif g.etat == "dialogue_champion":
            g.gerer_input_dialogue_champion(event)
        elif g.etat == "combat_champion":
            g.gerer_input_combat_champion(event)
        return True


    # RENDU

    def _render(self):
        if self.etat == "menu_principal":
            self.menu_principal.afficher()
        elif self.etat == "options":
            self.menu_options.afficher()
        elif self.etat == "choix_starter":
            self.menu_starter.afficher()
        elif self.etat == "pokedex_menu":
            self._game_pokedex.screen = self.screen
            self._game_pokedex._render_pokedex()
        elif self.etat == "jeu" and self.game:
            self.game.render()


    # BOUCLE PRINCIPALE

    def run(self):
        handlers = {
            "menu_principal": self._gerer_menu_principal,
            "options":        self._gerer_menu_options,
            "choix_starter":  self._gerer_choix_starter,
            "pokedex_menu":   self._gerer_pokedex_menu,
            "jeu":            self._gerer_jeu,
        }
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                handler = handlers.get(self.etat)
                if handler:
                    running = handler(event)
            self._render()
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()
        sys.exit()



def main():
    print("=" * 50)
    print("  POKÉMON FRAUDE - ÉDITION AVENTURE FRAUDULEUSE")
    print("=" * 50)
    print()
    try:
        Application().run()
    except Exception as e:
        print(f"\n✗ Erreur fatale: {e}")
        import traceback; traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()