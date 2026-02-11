class Type:
    def __init__():
        pass


# Dictionnaire pour quel type bat/perd contre lequel.
type_dict = {

    "Bug": {"Steel": 1.5, "Combat": 1.5, "Fairy": 1.5, "Fire": 1.5, "Plant": 2, "Poison": 1.5, "Psy": 2, "Specter": 1.5, "Darkness": 2, "Fly": 1.5},

    "Combat": {"Steel": 2, "Fairy": 1.5, "Ice": 2, "Bug": 1.5, "Normal": 2, "Poison": 1.5, "Psy": 1.5, "Rock": 2, "Darkness": 2, "Fly": 1.5, "Specter": 0},

    "Darkness": {"Combat": 1.5, "Fairy": 1.5, "Psy": 2, "Specter": 2, "Darkness": 1.5},

    "Dragon": {"Steel": 1.5, "Dragon": 2, "Fairy": 0},

    "Electric": {"Dragon": 1.5, "Water": 2, "Electric": 1.5, "Plant": 1.5, "Ground": 0, "Fly": 2},

    "Fairy": {"Steel": 1.5, "Combat": 2, "Dragon": 2, "Fire": 1.5, "Poison": 1.5, "Darkness": 2},

    "Fire": {"Steel": 2, "Dragon": 1.5, "Water": 1.5, "Fire": 1.5, "Ice": 2, "Bug": 2, "Plant": 2, "Rock": 1.5},

    "Fly": {"Steel": 1.5, "Combat": 2, "Electric": 1.5, "Bug": 2, "Plant": 2, "Rock": 1.5},

    "Ground": {"Steel": 2, "Electric": 2, "Fire": 2, "Bug": 1.5, "Plant": 1.5, "Poison": 2, "Rock": 2, "Fly": 0},

    "Ice": {"Steel": 1.5, "Dragon": 2, "Water": 1.5, "Fire": 1.5, "Ice": 1.5, "Plant": 2, "Ground": 2, "Fly": 2},

    "Normal": {"Steel": 1.5, "Rock": 1.5, "Specter": 0},

    "Plant": {"Steel": 1.5, "Dragon": 1.5, "Water": 2, "Fire": 1.5, "Bug": 1.5, "Plant": 1.5, "Poison": 1.5, "Rock": 2, "Ground": 2, "Fly": 1.5},

    "Poison": {"Fairy": 2, "Plant": 2, "Poison": 1.5, "Rock": 1.5, "Ground": 1.5, "Specter": 1.5, "Steel": 0},

    "Psy": {"Steel": 1.5, "Combat": 2, "Poison": 2, "Psy": 1.5, "Darkness": 0},

    "Rock": {"Steel": 1.5, "Combat": 1.5, "Fire": 2, "Ice": 2, "Bug": 2, "Ground": 1.5, "Fly": 2},

    "Specter": {"Psy": 2, "Specter": 2, "Darkness": 1.5, "Normal": 0},

    "Steel": {"Steel": 1.5, "Water": 1.5, "Electric": 1.5, "Fairy": 2, "Fire": 1.5, "Ice": 2, "Rock": 2},

    "Water": {"Dragon": 1.5, "Water": 1.5, "Fire": 2, "Plant": 1.5, "Rock": 2, "Ground": 2}

}