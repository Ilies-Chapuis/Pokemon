#!/usr/bin/env python3
import sys
import os

print("=== Test du système Pokémon ===\n")

# Test 1: Import de types
print("1. Test d'import de pokemon_types.py...")
try:
    from Logique.Gameplay.General.pokemon_types import type_dict
    print(f"   ✓ pokemon_types.py importé avec succès")
    print(f"   ✓ Nombre de types: {len(type_dict)}")
except Exception as e:
    print(f"   ✗ Erreur: {e}")
    sys.exit(1)

# Test 2: Import de pokemon
print("\n2. Test d'import de pokemon.py...")
try:
    from Logique.Gameplay.General.pokemon import Pokemon, multiplicateur_type
    print(f"   ✓ pokemon.py importé avec succès")
except Exception as e:
    print(f"   ✗ Erreur: {e}")
    sys.exit(1)

# Test 3: Chargement du JSON
print("\n3. Test de chargement du pokemon.json...")
try:
    import json
    with open('pokemon.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"   ✓ pokemon.json chargé")
    print(f"   ✓ Nombre de Pokémon: {len(data['pokemon'])}")
except Exception as e:
    print(f"   ✗ Erreur: {e}")
    sys.exit(1)

# Test 4: Création d'un Pokémon
print("\n4. Test de création d'un Pokémon...")
try:
    pokemon_data = data['pokemon'][0]
    print(f"   Test avec: {pokemon_data['name']}")
    pokemon = Pokemon.from_pokedex(pokemon_data, 5)
    print(f"   ✓ Pokémon créé: {pokemon.nom}")
    print(f"   ✓ PV: {pokemon.pv}/{pokemon.pv_max}")
    print(f"   ✓ Attaque: {pokemon.attaque}")
    print(f"   ✓ Défense: {pokemon.defense}")
except Exception as e:
    print(f"   ✗ Erreur: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Test de multiplicateur de type
print("\n5. Test des multiplicateurs de types...")
try:
    mult = multiplicateur_type("Feu", "Plante")
    print(f"   ✓ Feu vs Plante: {mult}x")
    mult = multiplicateur_type("Eau", "Feu")
    print(f"   ✓ Eau vs Feu: {mult}x")
except Exception as e:
    print(f"   ✗ Erreur: {e}")
    sys.exit(1)

# Test 6: Import de combat
print("\n6. Test d'import de combat.py...")
try:
    from Logique.Gameplay.General.combat import Combat
    print(f"   ✓ combat.py importé avec succès")
except Exception as e:
    print(f"   ✗ Erreur: {e}")
    sys.exit(1)

# Test 7: Import de map
print("\n7. Test d'import de map.py...")
try:
    from Graphique.map import Carte, RencontreManager, ZONES
    print(f"   ✓ map.py importé avec succès")
    print(f"   ✓ Nombre de zones: {len(ZONES)}")
except Exception as e:
    print(f"   ✗ Erreur: {e}")
    sys.exit(1)

# Test 8: Création d'une carte
print("\n8. Test de création de carte...")
try:
    carte = Carte(20, 15)
    print(f"   ✓ Carte créée: {carte.largeur}x{carte.hauteur}")
except Exception as e:
    print(f"   ✗ Erreur: {e}")
    sys.exit(1)

# Test 9: Gestionnaire de rencontres
print("\n9. Test du gestionnaire de rencontres...")
try:
    manager = RencontreManager('pokemon.json')
    print(f"   ✓ RencontreManager créé")
    print(f"   ✓ Pokémon dans le Pokédex: {len(manager.pokedex)}")
except Exception as e:
    print(f"   ✗ Erreur: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 10: Import de game (sans lancer pygame)
print("\n10. Test d'import de game.py...")
try:
    # Note: on n'importe pas Game car ça lance pygame.init()
    print(f"   ⚠ Test manuel requis (pygame)")
except Exception as e:
    print(f"   ✗ Erreur: {e}")

print("\n=== Tous les tests passés avec succès! ===")
print("\nPour lancer le jeu:")
print("  python3 game.py")