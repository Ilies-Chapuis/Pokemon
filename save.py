class Saves:

    def __init__(self, name, levels=1, argent=0, pokemons=None):
        self.name= name
        self.levels= levels
        self.argent= argent
        self.pokemons= pokemons if pokemons else []
