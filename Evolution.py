"""
Système d'évolution des Pokémon
"""

# Table d'évolution : nom_base -> (nom_evolution, niveau_requis)
EVOLUTIONS = {
    # Starters
    "Keunotor": ("Keunotaure", 16),
    "Keunotaure": ("Keunotitan", 32),

    "Timiki": ("Timidragon", 16),
    "Timidragon": ("Timileviathan", 32),

    "Rubycire": ("Rubyflame", 16),
    "Rubyflame": ("Rubypyros", 32),

    # Pokémon communs
    "Zaptile": ("Zapdragon", 18),
    "Minikoal": ("Megakoal", 20),

    "Bloupy": ("Blouvern", 20),
    "Voltalin": ("Voltamax", 22),

    "Floraclaw": ("Floratank", 18),
    "Brisaflamme": ("Brisadragon", 25),

    "Bavoir": ("Bavoirath", 20),
    "Magmire": ("Magmigos", 22),

    "Skelerat": ("Skelevil", 24),
    "Noctyssor": ("Noctydemon", 26),

    "Muddew": ("Mudderon", 20),
    "ZapZap": ("Zapking", 24),

    # Pokémon peu communs
    "Lupika": ("Lupiknight", 28),
    "Scalydra": ("Scalyking", 30),
    "Okeloke": ("Okelegend", 30),

    # Pokémon rares (pas d'évolution pour la plupart)
    "Flamydra": ("Flamelord", 40),
    "Cendralis": ("Cendrahawk", 38),
}


def peut_evoluer(nom_pokemon, niveau):
    """Vérifie si un Pokémon peut évoluer"""
    if nom_pokemon in EVOLUTIONS:
        evolution_data = EVOLUTIONS[nom_pokemon]
        nom_evolution, niveau_requis = evolution_data
        return niveau >= niveau_requis, nom_evolution, niveau_requis
    return False, None, None


def obtenir_evolution(nom_pokemon):
    """Retourne le nom de l'évolution si elle existe"""
    if nom_pokemon in EVOLUTIONS:
        return EVOLUTIONS[nom_pokemon][0]
    return None


def obtenir_niveau_evolution(nom_pokemon):
    """Retourne le niveau d'évolution requis"""
    if nom_pokemon in EVOLUTIONS:
        return EVOLUTIONS[nom_pokemon][1]
    return None


def a_une_evolution(nom_pokemon):
    """Vérifie si un Pokémon a une évolution"""
    return nom_pokemon in EVOLUTIONS