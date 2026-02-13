import pygame
import sys
from affichage_menu import MenuRenderer
from settings import Settings

pygame.init()

settings = Settings()

window = pygame.display.set_mode((settings.window_width, settings.window_height))
pygame.display.set_caption("Pokemon")

background = pygame.image.load(settings.background_path)
background = pygame.transform.scale(background, (settings.window_width, settings.window_height))

pygame.mixer.init()
pygame.mixer.music.load(settings.music_path)
pygame.mixer.music.play(-1)

font = pygame.font.Font(None, 40)

main_menu = settings.main_menu
options_menu = settings.options_menu

menu_state = "main"

renderer = MenuRenderer(settings)

clock = pygame.time.Clock()
running = True

rects = []

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos

            if menu_state == "main":
                for i, rect in enumerate(rects):
                    if rect.collidepoint(mouse_x, mouse_y):
                        choice = main_menu[i]

                        if choice == "New Game":
                            menu_state = "game"
                        elif choice == "Continue":
                            menu_state = "continue"
                        elif choice == "Options":
                            menu_state = "options"
                        elif choice == "Quit":
                            running = False

            elif menu_state == "options":
                for i, rect in enumerate(rects):
                    if rect.collidepoint(mouse_x, mouse_y):
                        choice = options_menu[i]

                        if choice == "Fullscreen":
                            print("Fullscreen pas encore implémenté")
                        elif choice == "Volume":
                            print("Volume pas encore implémenté")
                        elif choice == "Back":
                            menu_state = "main"

    window.blit(background, (0, 0))

    if menu_state == "main":
        rects = renderer.show(window, font, main_menu)
    elif menu_state == "options":
        rects = renderer.show(window, font, options_menu)
    elif menu_state == "game":
        text = font.render("Starting new game...", True, settings.Black)
        window.blit(text, (337, 450))
    elif menu_state == "continue":
        text = font.render("Loading save...", True, settings.Black)
        window.blit(text, (375, 450))

    pygame.display.flip()
