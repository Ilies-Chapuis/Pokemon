"""
Gestionnaire de sauvegarde pour Pokémon JVSI
"""
import json
import os
from datetime import datetime


class SaveManager:
    def __init__(self, save_file="save_game.json"):
        self.save_file = save_file

    def sauvegarder(self, game_state):
        """Sauvegarde l'état du jeu"""
        try:
            save_data = {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "joueur": {
                    "position_x": game_state.joueur_x,
                    "position_y": game_state.joueur_y,
                    "potions": game_state.potions,
                    "pokeballs": game_state.pokeballs
                },
                "equipe": [
                    {
                        "nom": pokemon.nom,
                        "niveau": pokemon.niveau,
                        "pv": pokemon.pv,
                        "pv_max": pokemon.pv_max,
                        "attaque": pokemon.attaque,
                        "defense": pokemon.defense,
                        "experience": pokemon.experience,
                        "types": pokemon.types,
                        "legendary": pokemon.legendary
                    }
                    for pokemon in game_state.equipe_joueur
                ],
                "reserve": [
                    {
                        "nom": pokemon.nom,
                        "niveau": pokemon.niveau,
                        "pv": pokemon.pv,
                        "pv_max": pokemon.pv_max,
                        "attaque": pokemon.attaque,
                        "defense": pokemon.defense,
                        "experience": pokemon.experience,
                        "types": pokemon.types,
                        "legendary": pokemon.legendary
                    }
                    for pokemon in game_state.reserve_pokemon
                ]
            }

            with open(self.save_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)

            print(f"✓ Partie sauvegardée : {self.save_file}")
            print(f"  - Équipe: {len(game_state.equipe_joueur)} Pokémon")
            print(f"  - Réserve: {len(game_state.reserve_pokemon)} Pokémon")
            return True

        except Exception as e:
            print(f"✗ Erreur lors de la sauvegarde : {e}")
            import traceback
            traceback.print_exc()
            return False

    def charger(self):
        """Charge l'état du jeu"""
        try:
            if not os.path.exists(self.save_file):
                print("⚠ Aucune sauvegarde trouvée")
                return None

            with open(self.save_file, 'r', encoding='utf-8') as f:
                save_data = json.load(f)

            print(f"✓ Sauvegarde chargée : {save_data['date']}")
            return save_data

        except Exception as e:
            print(f"✗ Erreur lors du chargement : {e}")
            return None

    def existe_sauvegarde(self):
        """Vérifie si une sauvegarde existe"""
        return os.path.exists(self.save_file)

    def supprimer_sauvegarde(self):
        """Supprime la sauvegarde"""
        try:
            if os.path.exists(self.save_file):
                os.remove(self.save_file)
                print("✓ Sauvegarde supprimée")
                return True
        except Exception as e:
            print(f"✗ Erreur lors de la suppression : {e}")
            return False