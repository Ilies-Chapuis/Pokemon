import pygame
import sys
from affichage_menu import MenuRenderer
from settings import Settings

pygame.init()

settings = Settings()

# --- Création de la fenêtre ---
window = pygame.display.set_mode((settings.window_width, settings.window_height))
pygame.display.set_caption("Pokemon")

# Mise à jour de la vraie taille de la fenêtre
settings.window_width, settings.window_height = window.get_size()
settings.full_screen = False  # état initial

# --- Background ---
background = pygame.image.load(settings.background_path)
background = pygame.transform.smoothscale(background, (settings.window_width, settings.window_height))

# --- Musique ---
pygame.mixer.init()
pygame.mixer.music.load(settings.music_path)
pygame.mixer.music.set_volume(settings.volume)  # volume initial
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

        # ----- ESCAPE POUR QUITTER LE FULLSCREEN -----
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:

                # Retour depuis le menu volume
                if menu_state == "volume":
                    menu_state = "options"

                # Retour depuis fullscreen
                elif settings.full_screen:
                    settings.full_screen = False

                    window = pygame.display.set_mode((settings.windowed_width, settings.windowed_height))

                    settings.window_width = settings.windowed_width
                    settings.window_height = settings.windowed_height

                    background = pygame.image.load(settings.background_path)
                    background = pygame.transform.smoothscale(
                        background,
                        (settings.window_width, settings.window_height)
                    )

        # ----- CONTROLES DU VOLUME -----
        if menu_state == "volume":
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_LEFT:
                    settings.volume = max(0, settings.volume - 0.1)
                    pygame.mixer.music.set_volume(settings.volume)

                elif event.key == pygame.K_RIGHT:
                    settings.volume = min(1, settings.volume + 0.1)
                    pygame.mixer.music.set_volume(settings.volume)

        # ----- CLIC SOURIS -----
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
                            settings.full_screen = True

                            window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

                            settings.window_width, settings.window_height = window.get_size()

                            background = pygame.image.load(settings.background_path)
                            background = pygame.transform.smoothscale(
                                background,
                                (settings.window_width, settings.window_height)
                            )

                        elif choice == "Volume":
                            menu_state = "volume"

                        elif choice == "Back":
                            menu_state = "main"

    # ----- AFFICHAGE -----
    window.blit(background, (0, 0))

    if menu_state == "main":
        rects = renderer.show(window, font, main_menu)

    elif menu_state == "options":
        rects = renderer.show(window, font, options_menu)

    elif menu_state == "volume":
        # Affichage du volume
        text = font.render(f"Volume : {int(settings.volume * 100)}%", True, settings.Black)
        text_x = settings.window_width // 2 - text.get_width() // 2
        text_y = settings.window_height // 2 - 20
        window.blit(text, (text_x, text_y))

        info = font.render("← / → pour changer, ESC pour revenir", True, settings.Black)
        info_x = settings.window_width // 2 - info.get_width() // 2
        info_y = settings.window_height // 2 + 40
        window.blit(info, (info_x, info_y))

    elif menu_state == "game":
        text = font.render("Starting new game...", True, settings.Black)
        text_x = settings.window_width // 2 - text.get_width() // 2
        text_y = settings.window_height - 80
        window.blit(text, (text_x, text_y))

    elif menu_state == "continue":
        text = font.render("Loading save...", True, settings.Black)
        text_x = settings.window_width // 2 - text.get_width() // 2
        text_y = settings.window_height - 80
        window.blit(text, (text_x, text_y))

    pygame.display.flip()
