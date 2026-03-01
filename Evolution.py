
EVOLUTIONS = {
    # Starters
    "Keunotor":    ("Keunotaure",    16),
    "Keunotaure":  ("Keunotitan",    32),
    "Timiki":      ("Timidragon",    16),
    "Timidragon":  ("Timileviathan", 32),
    "Rubycire":    ("Rubyflame",     16),
    "Rubyflame":   ("Rubypyros",     32),
    # Pokémon communs
    "Zaptile":     ("Zapdragon",   18),
    "Minikoal":    ("Megakoal",    20),
    "Bloupy":      ("Blouvern",    20),
    "Voltalin":    ("Voltamax",    22),
    "Floraclaw":   ("Floratank",   18),
    "Brisaflamme": ("Brisadragon", 25),
    "Bavoir":      ("Bavoirath",   20),
    "Magmire":     ("Magmigos",    22),
    "Skelerat":    ("Skelevil",    24),
    "Noctyssor":   ("Noctydemon",  26),
    "Muddew":      ("Mudderon",    20),
    "ZapZap":      ("Zapking",     24),
    # Pokémon peu communs
    "Lupika":    ("Lupiknight",  28),
    "Scalydra":  ("Scalyking",   30),
    "Okeloke":   ("Okelegend",   30),
    # Pokémon rares
    "Flamydra":  ("Flamelord",   40),
    "Cendralis": ("Cendrahawk",  38),
}

#  Forme Ultime
# Niveau à partir duquel la Forme Ultime est proposée
NIVEAU_FORME_ULTIME = 30

# Multiplicateur de stats appliqué à la base du Pokédex lors du reset
BONUS_FORME_ULTIME = 1.8

# Nom affiché pour la Forme Ultime  ("<NOM> Forme Ultime")
SUFFIXE_FORME_ULTIME = " GOD MODE"


#  Fonctions classiques
def peut_evoluer(nom_pokemon, niveau):
    #Vérifie si un Pokémon peut évoluer (évolution classique).
    if nom_pokemon in EVOLUTIONS:
        nom_evo, niv_requis = EVOLUTIONS[nom_pokemon]
        return niveau >= niv_requis, nom_evo, niv_requis
    return False, None, None


def obtenir_evolution(nom_pokemon):
    if nom_pokemon in EVOLUTIONS:
        return EVOLUTIONS[nom_pokemon][0]
    return None


def obtenir_niveau_evolution(nom_pokemon):
    if nom_pokemon in EVOLUTIONS:
        return EVOLUTIONS[nom_pokemon][1]
    return None


def a_une_evolution(nom_pokemon):
    return nom_pokemon in EVOLUTIONS


#  Forme Ultime
def peut_forme_ultime(pokemon):

    return (pokemon.niveau >= NIVEAU_FORME_ULTIME
            and SUFFIXE_FORME_ULTIME not in pokemon.nom)


def appliquer_forme_ultime(pokemon, pokedex_data):

    base_pv  = int(pokedex_data["stats"]["pv"]      * BONUS_FORME_ULTIME)
    base_atk = int(pokedex_data["stats"]["attaque"]  * BONUS_FORME_ULTIME)
    base_def = int(pokedex_data["stats"]["defense"]  * BONUS_FORME_ULTIME)

    niveau_depart = 5
    pokemon.niveau    = niveau_depart
    pokemon.pv_max    = base_pv  + (niveau_depart - 1) * 3
    pokemon.attaque   = base_atk + (niveau_depart - 1) * 2
    pokemon.defense   = base_def + (niveau_depart - 1) * 2
    pokemon.pv        = pokemon.pv_max
    pokemon.experience     = 0
    pokemon.experience_max = niveau_depart * 100

    if SUFFIXE_FORME_ULTIME not in pokemon.nom:
        pokemon.nom = pokemon.nom + SUFFIXE_FORME_ULTIME

    return pokemon
