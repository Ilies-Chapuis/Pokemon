"""
Système de Pokédex complet avec suivi des Pokémon vus et capturés
"""
import json
import os


class PokedexManager:
    def __init__(self, save_file="pokedex_progress.json"):
        self.save_file = save_file
        self.pokemon_vus = set()
        self.pokemon_captures = set()
        self.charger_progression()

    def charger_progression(self):
        """Charge la progression du Pokédex"""
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.pokemon_vus = set(data.get("vus", []))
                    self.pokemon_captures = set(data.get("captures", []))
            except Exception as e:
                print(f"⚠ Erreur chargement Pokédex : {e}")
                self.pokemon_vus = set()
                self.pokemon_captures = set()

    def sauvegarder_progression(self):
        """Sauvegarde la progression du Pokédex"""
        try:
            data = {
                "vus": list(self.pokemon_vus),
                "captures": list(self.pokemon_captures)
            }
            with open(self.save_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"⚠ Erreur sauvegarde Pokédex : {e}")
            return False

    def marquer_vu(self, nom_pokemon):
        """Marque un Pokémon comme vu"""
        if nom_pokemon not in self.pokemon_vus:
            self.pokemon_vus.add(nom_pokemon)
            self.sauvegarder_progression()
            return True
        return False

    def marquer_capture(self, nom_pokemon):
        """Marque un Pokémon comme capturé"""
        self.pokemon_vus.add(nom_pokemon)
        if nom_pokemon not in self.pokemon_captures:
            self.pokemon_captures.add(nom_pokemon)
            self.sauvegarder_progression()
            return True
        return False

    def est_vu(self, nom_pokemon):
        """Vérifie si un Pokémon a été vu"""
        return nom_pokemon in self.pokemon_vus

    def est_capture(self, nom_pokemon):
        """Vérifie si un Pokémon a été capturé"""
        return nom_pokemon in self.pokemon_captures

    def obtenir_stats(self):
        """Retourne les statistiques du Pokédex"""
        return {
            "vus": len(self.pokemon_vus),
            "captures": len(self.pokemon_captures)
        }

    def obtenir_completion(self, total_pokemon):
        """Retourne le pourcentage de completion"""
        if total_pokemon == 0:
            return 0
        return (len(self.pokemon_captures) / total_pokemon) * 100