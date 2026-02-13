class Settings:
    def __init__(self):
        # Fenêtre
        self.window_width = 960
        self.window_height = 540

        # Chemins
        self.background_path = "Assets/Image_Menu/background.png"
        self.music_path = "Assets/Musique_Menu/Ost.mp3"
        self.logo_path = "Assets/Image_Menu/logo.png"

        # Couleurs
        self.White = (255, 255, 255)
        self.Black = (0, 0, 0)

        # Menus
        self.main_menu = ["New Game", "Continue", "Options", "Quit"]
        self.options_menu = ["Fullscreen", "Volume", "Back"]
