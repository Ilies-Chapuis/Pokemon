#entity c'est la ou on mets les caractéristiques player et les npc
import pygame
from tool import Tool
from screen import Screen
from keylistener import Keylistener

class Entity (pygame.sprite.Sprite):
    def __init__(self, keylistener: Keylistener, screen: Screen, x: int, y: int):
        super().__init__()
        self.screen= screen
        self.keylistener = keylistener
        self.spritesheet= pygame.image.load("Assets\Sprites\Players\Player_M/Players_M.png")
        self.image= Tool.split_image(self.spritesheet, 0, 0, 24, 32)
        self.position: pygame.math.Vector2 = pygame.math.Vector2(x + 16, y)
        self.rect: pygame.Rect = self.image.get_rect()
        self.all_images = self.get_all_images()
        self.index_image=0
        self.image_part=0
        self.reset_animation= False
        self.hitbox: pygame.Rect= pygame.Rect(0, 0, 16, 16)

        self.step: int=0
        self.animation_walk: bool = False
        self.direction= "down"

        self.animation_step_time: float =0.0    #attribut qui permet de stocker le temps( à chaque fois que maj écran il y aura compteur s'incrémenter)
        self.action_animation= 16               #le compteur est à 16 car valeurs ou sa marche bien pour les déplacements/
                                                #self.action_animation permet de dire si self.animation_step_time: float =0.0 et supérieur à self.action_animation= 16 alors on fait l'action (avancer d'un pixel)


    def update(self):
        self.animation_sprite()
        self.move()
        self.rect.center = self.position
        self.hitbox.midbottom= self.rect.midbottom  #hit box midbottom car on ne veut que le corps pour la hitbox pas la tête
        self.image=self.all_images[self.direction][self.index_image]

    def move_left(self):

        self.animation_walk = True
        self.direction= "left"


    def move_right(self):

        self.animation_walk = True
        self.direction= "right"


    def move_up(self):

        self.animation_walk = True
        self.direction= "up"

    
    def move_down(self):

        self.animation_walk = True
        self.direction= "down"

    
    def animation_sprite(self):
        if int(self.step //8) + self.image_part >=4:
            self.image_part=0
            self.reset_animation= True
        self.index_image = int(self.step //8) + self.image_part


    
    def move(self): #permet de faire déplacer le joueur sur la map
        if self.animation_walk:
            self.animation_step_time += self.screen.get_delta_time()
            if self.step < 16 and self.animation_step_time >= self.action_animation:
                self.step += 1
                if self.direction == "left":
                    self.position.x -=1
                
                elif self.direction == "right":
                    self.position.x +=1

                elif self.direction == "up":
                    self.position.y -=1

                elif self.direction == "down":
                    self.position.y +=1
                self.animation_step_time=0

            elif self.step >= 16:
                self.step=0
                self.animation_walk= False
                if self.reset_animation:
                    self.reset_animation = False
                else:
                    if self.image_part == 0:
                        self.image_part = 2
                    else:
                        self.image_part=0


    #met à jour le player bien aligné sur la grille de la map tiled
    def align_hitbox(self):
        self.rect.center = self.position
        self.hitbox.midbottom= self.rect.midbottom
        while self.hitbox.x % 16 != 0:  #verifie si le x de la hitbox n'est pas sut les petites lignes noir de la map tiled (change position x)
            self.rect.x -= 1
            self.hitbox.midbottom= self.rect.midbottom

        while self.hitbox.y % 16 != 0:  #verifie si le y de la hitbox n'est pas sut les petites lignes noir de la map tiled (change position y)
            self.rect.y -= 1
            self.hitbox.midbottom= self.rect.midbottom
        self.position= pygame.math.Vector2(self.rect.center)

    def get_all_images(self):
        all_images={

            "down":[],
            "left":[],
            "right":[],
            "up":[]
        }


        width: int = self.spritesheet.get_width() //4
        height: int = self.spritesheet.get_height() //4


        for i in range (4): #pour les lignes (sprites)
            for j, key in enumerate (all_images.keys()):
                all_images[key].append(Tool.split_image(self.spritesheet, i * width, j * height, 24, 32))
        return all_images