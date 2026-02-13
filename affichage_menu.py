import pygame

class MenuRenderer:
    def __init__(self, settings):
        self.settings = settings

    def show(self, window, font, menu_list):
        rects = []

        button_width = 240
        button_height = 40
        spacing = 40

        window_width = self.settings.window_width
        window_height = self.settings.window_height

        # Style original : boutons en bas de l'écran
        bottom_margin = 0
        total_height = len(menu_list) * spacing
        start_y = window_height - total_height - bottom_margin

        mouse_x, mouse_y = pygame.mouse.get_pos()

        for i, text in enumerate(menu_list):
            center_x = window_width // 2
            center_y = start_y + i * spacing

            rect = pygame.Rect(0, 0, button_width, button_height)
            rect.center = (center_x, center_y)

            is_hover = rect.collidepoint(mouse_x, mouse_y)
            bg_color = (0, 0, 0) if not is_hover else (40, 40, 40)

            pygame.draw.rect(window, bg_color, rect)
            pygame.draw.rect(window, (255, 255, 255), rect, 3)

            label = font.render(text, True, (255, 255, 255))
            label_rect = label.get_rect(center=rect.center)
            window.blit(label, label_rect)

            rects.append(rect)

        return rects
