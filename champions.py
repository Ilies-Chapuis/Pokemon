
import os
import json

#  Positions des champions dans la ville (cases de la grille)

POSITION_CHAMPION_PLANTE = (9,  7)
POSITION_CHAMPION_FEU    = (10, 7)

# Distance (en cases) à laquelle le champion "interpelle" le joueur
DISTANCE_INTERACTION = 0


#  Données des champions
CHAMPIONS = {
    "plante": {
        "id":     "plante",
        "nom":    "Ilies",
        "titre":  "Champion de l'Arène Plante",
        "image":  "champion_plante.png",   # dans Data/Assets/
        "couleur_theme": (50, 180, 80),

        "dialogues": {
            "approche": [
                "Hé, toi ! Je t'ai vu traverser la plaine...",
                "Tu as l'air de te battre depuis un moment.",
                "Je suis Ilies, Champion de l'Arène Plante.",
                "Si tu veux prouver ta valeur, affronte-moi !",
                "[ENTRÉE] Combattre    [ÉCHAP] Pas maintenant",
            ],
            "avant_combat": [
                "Bien. Alors montre-moi ce que tu vaux.",
                "Mes Pokémon ont été entraînés dans la forêt la plus profonde.",
                "Ils ne connaissent pas la pitié. Bonne chance !",
            ],
            "victoire_champion": [   # le champion gagne
                "...",
                "Tu t'en es bien sorti pour un débutant.",
                "Reviens t'entraîner et tu pourras peut-être me battre.",
            ],
            "defaite_champion": [    # le joueur gagne
                "Impossible... mes Pokémon de la forêt ancienne...",
                "Tu mérites ce badge, dresseur.",
                "Garde-le bien. Il prouve que tu as vaincu l'Arène Plante !",
                "✦ Badge Feuille obtenu !",
            ],
            "deja_battu": [
                "Ilies : Tu m'as déjà battu, dresseur.",
                "Je m'entraîne encore. Reviens plus tard pour un revanche.",
            ],
        },

        # Équipe de 6 Pokémon (nom, niveau, types, pv, atk, def, legendary)
        "equipe": [
            {"nom": "Floratank",  "niveau": 35, "types": ["Plante"],         "pv": 210, "attaque": 185,  "defense": 175,  "legendary": False},
            {"nom": "Lumyntha",    "niveau": 38, "types": ["Plante", "Psy"],  "pv": 205, "attaque": 190,  "defense": 170,  "legendary": False},
            {"nom": "Verdalune",   "niveau": 40, "types": ["Plante", "Lune"], "pv": 220, "attaque": 195,  "defense": 180,  "legendary": False},
            {"nom": "Mudderon",    "niveau": 37, "types": ["Sol", "Plante"],  "pv": 215, "attaque": 188,  "defense": 185,  "legendary": False},
            {"nom": "Floraclaw",   "niveau": 42, "types": ["Plante"],         "pv": 208, "attaque": 200, "defense": 178,  "legendary": False},
            {"nom": "SylphraL",   "niveau": 45, "types": ["Plante", "Vol"],  "pv": 445, "attaque": 420, "defense": 300, "legendary": True},
        ],

        "recompense": {
            "badge": "Badge Feuille",
            "potions": 3,
            "pokeballs": 5,
        },
    },

    "feu": {
        "id":     "feu",
        "nom":    "Melvin",
        "titre":  "Champion de l'Arène Feu",
        "image":  "champion_feu.png",
        "couleur_theme": (220, 80, 30),

        "dialogues": {
            "approche": [
                "Tiens, un visiteur qui ose entrer en ville...",
                "Je suis Melvin. Je règne sur l'Arène Feu de cette région.",
                "Mes flammes ont consumé des centaines de dresseurs.",
                "Tu veux tenter ta chance ?",
                "[ENTRÉE] Combattre    [ÉCHAP] Pas maintenant",
            ],
            "avant_combat": [
                "Melvin : Parfait. Tu ne manques pas de courage.",
                "Mais le courage sans puissance, ça brûle vite.",
                "Allez — que le combat commence !",
            ],
            "victoire_champion": [
                "Comme prévu. Tu avais du potentiel, mais pas assez.",
                "Entraîne-toi encore et reviens quand tu seras prêt.",
            ],
            "defaite_champion": [
                "Non... mes flammes éteintes...",
                "Tu es... vraiment fort, dresseur.",
                "Ce badge, tu le mérites plus que quiconque.",
                "✦ Badge Flamme obtenu !",
            ],
            "deja_battu": [
                "Melvin : Tu m'as déjà vaincu. Je le reconnais.",
                "Mes Pokémon se remettent de leur défaite.",
                "Reviens pour un revanche quand tu te sens prêt.",
            ],
        },

        "equipe": [
            {"nom": "Brisadragon", "niveau": 36, "types": ["Feu", "Dragon"], "pv": 212, "attaque": 195,  "defense": 172,  "legendary": False},
            {"nom": "Magmigos",    "niveau": 38, "types": ["Feu", "Roche"],  "pv": 218, "attaque": 190,  "defense": 188,  "legendary": False},
            {"nom": "Rubypyros",   "niveau": 41, "types": ["Feu"],           "pv": 278, "attaque": 255, "defense": 175,  "legendary": False},
            {"nom": "Cendralis",   "niveau": 39, "types": ["Feu", "Vol"],    "pv": 195, "attaque": 198,  "defense": 170,  "legendary": False},
            {"nom": "Flamelord",   "niveau": 43, "types": ["Feu"],           "pv": 282, "attaque": 290, "defense": 180,  "legendary": False},
            {"nom": "BraseoL",     "niveau": 46, "types": ["Feu", "Combat"], "pv": 450, "attaque": 430, "defense": 305, "legendary": True},
        ],

        "recompense": {
            "badge": "Badge Flamme",
            "potions": 3,
            "pokeballs": 5,
        },
    },
}


#  Helpers
def get_champion(champion_id):
    return CHAMPIONS.get(champion_id)


def position_champion(champion_id):
    if champion_id == "plante":
        return POSITION_CHAMPION_PLANTE
    return POSITION_CHAMPION_FEU


def champion_a_proximite(joueur_x, joueur_y, champions_battus):

    for cid, pos in [("plante", POSITION_CHAMPION_PLANTE),
                     ("feu",    POSITION_CHAMPION_FEU)]:
        dist = abs(joueur_x - pos[0]) + abs(joueur_y - pos[1])
        if dist <= DISTANCE_INTERACTION:
            return cid
    return None


def creer_equipe_champion(champion_id):
    #Crée la liste de Pokémon de l'équipe du champion.
    from pokemon import Pokemon
    data = CHAMPIONS[champion_id]
    equipe = []
    for p in data["equipe"]:
        poke = Pokemon(
            nom=p["nom"],
            types=p["types"],
            pv_max=p["pv"],
            attaque=p["attaque"],
            defense=p["defense"],
            niveau=p["niveau"],
            legendary=p["legendary"],
        )
        equipe.append(poke)
    return equipe