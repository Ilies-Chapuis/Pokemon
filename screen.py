import pygame

class Screen:

    def __init__(self):
        self.display: pygame.Surface= pygame.display.set_mode((1280, 720))#, pygame.FULLSCREEN)
        pygame.display.set_caption("Pokémon Fraud")
        self.clock=pygame.time.Clock()
        self.framerate=144 #Fps
        self.deltatime: float = 0.0

#Rafraichissement de l'écran
    def update(self):
        pygame.display.flip()
        pygame.display.update()
        self.clock.tick(self.framerate)
        self.display.fill((0, 0, 0))
        self.deltatime = self.clock.get_time()

    def get_delta_time(self):
        return self.deltatime

#Renvoie la taille de la fenêtre
    def get_size(self):
        return self.display.get_size()

    def get_display(self):
        return self.display
