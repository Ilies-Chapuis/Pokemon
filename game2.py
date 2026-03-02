import pygame

from screen import Screen
from map import Map
from entity import Entity
from keylistener import Keylistener
from player import Player


class game2:
    
    def __init__(self):
        self.running= True
        self.screen=Screen () #objet ecran
        self.map= Map(self.screen)
        self.keylistener= Keylistener()
        self.player = Player(self.keylistener, self.screen, 0, 0)
        self.map.add_player(self.player)
    
    def run(self):
        while self.running:
            self.handle_input()
            self.map.update()
            self.screen.update()

#permet de récupérer tout les events fait par pygame
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                self.keylistener.add_key(event.key)
            elif event.type == pygame.KEYUP:
                self.keylistener.remove_key(event.key)

