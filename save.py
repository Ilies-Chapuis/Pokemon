import os
import json
import pathlib

from map import Map
from player import Player
from sql import SQL
from keylistener import KeyListener
from dialogue import Dialogue

class Save:
    def __init__(self, path: str, map: Map, player: Player, keylistener: KeyListener, dialogue: Dialogue):
        self.path: str = path
        self.map: Map = map
        self.player: Player = player
        self.keylistener: KeyListener = keylistener
        self.dialogue: Dialogue = dialogue
        self.sql: SQL = SQL()

    def save(self) -> None:
        position = self.map.player.position
        player_info = {
            "name": self.map.player.name,
            "gender": self.player.gender,
            "position": {
                "x": position[0],
                "y": position[1]
            },
            "direction": self.map.player.direction,
            "pokemon": [pokemon.to_dict() for pokemon in self.player.pokemons],
            "inventory": self.map.player.inventory,
            "pokedex": self.map.player.pokedex,
            "pokedollars": self.map.player.pokedollars,
            "ingame_time": self.map.player.ingame_time.seconds
        }
        map_info = {
            "path": self.map.current_map.name,
            "map_name": self.map.map_name
        }
        data = {
            "player": player_info,
            "map": map_info
        }

        if not pathlib.Path(f"../../assets/Saves/{self.path}/data.pkmn").exists():
            os.makedirs(f"../../assets/Saves/{self.path}")
            pathlib.Path(f"../../assets/Saves/{self.path}/data.pkmn").touch()

        with open(f"../../assets/Saves/{self.path}/data.pkmn", "w") as file:
            file.write(self.dump(data))

    def load(self) -> None:
        if pathlib.path(f"../../assets/Saves/{self.path}/data.pkmn").exists():
            with open (f"../../assets/Saves/{self.path}/data.pkmn", "r") as file:
                data = json.load(file)
            self.map.load_map(data["map"]["path"])
            self.player.from_dict(data["player"])
        else:
            self.map.load_map("map_0")
            self.player.set_position(512, 288)
        self.map.add_player(self.player)

    def dumb(self, element: dict) -> str:
        return json.dumps(element, indent=4)
