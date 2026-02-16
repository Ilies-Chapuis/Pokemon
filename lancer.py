#!/usr/bin/env python3
"""
Lanceur du jeu Pokémon JVSI
Vérifie les dépendances avant de lancer le jeu
"""

import sys
import subprocess
import os


def verifier_pygame():
    """Vérifie si pygame est installé"""
    try:
        import pygame
        return True
    except ImportError:
        return False


def installer_pygame():
    """Installe pygame"""
    print("pygame n'est pas installé.")
    print("Installation de pygame...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame", "--break-system-packages"])
        print("✓ pygame installé avec succès!")
        return True
    except subprocess.CalledProcessError:
        print("✗ Échec de l'installation automatique")
        print("\nVeuillez installer pygame manuellement:")
        print("  pip install pygame --break-system-packages")
        return False


def verifier_fichiers():
    """Vérifie que tous les fichiers nécessaires sont présents"""
    fichiers_requis = {
        'pokemon.json': 'Base de données Pokémon',
        'pokemon_types.py': 'Système de types',
        'pokemon.py': 'Classe Pokémon',
        'combat.py': 'Système de combat',
        'map.py': 'Carte et rencontres',
        'menu.py': 'Menus du jeu',
        'game.py': 'Jeu principal',
        'main.py': 'Point d\'entrée'
    }

    manquants = []
    for fichier, description in fichiers_requis.items():
        if not os.path.exists(fichier):
            manquants.append(f"  ✗ {fichier} - {description}")

    if manquants:
        print("\n❌ Fichiers manquants:")
        for m in manquants:
            print(m)
        return False

    print("✓ Tous les fichiers requis sont présents")
    return True


def lancer_jeu():
    """Lance le jeu"""
    print("\n" + "=" * 50)
    print("  🎮 POKÉMON JVSI - ÉDITION AVENTURE")
    print("=" * 50 + "\n")

    # Vérifier les fichiers
    if not verifier_fichiers():
        return False

    # Vérifier pygame
    if not verifier_pygame():
        reponse = input("\nVoulez-vous installer pygame automatiquement? (o/n): ")
        if reponse.lower() == 'o':
            if not installer_pygame():
                return False
        else:
            print("\nLe jeu ne peut pas démarrer sans pygame.")
            return False

    # Lancer le jeu
    try:
        print("\n🎮 Lancement du jeu...\n")
        from main import main
        main()
        return True
    except Exception as e:
        print(f"\n❌ Erreur lors du lancement: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        succes = lancer_jeu()
        sys.exit(0 if succes else 1)
    except KeyboardInterrupt:
        print("\n\nArrêt du jeu...")
        sys.exit(0)