class Settings:
    def __init__(self):
        # --- Taille fenêtre ---
        self.window_width = 960
        self.window_height = 540

        # Taille fenêtrée (pour revenir depuis fullscreen)
        self.windowed_width = 960
        self.windowed_height = 540

        # --- Fullscreen ---
        self.full_screen = False

        # --- Volume ---
        self.volume = 0.5  # 🔥 Volume par défaut (50%)

        # --- Couleurs ---
        self.White = (255, 255, 255)
        self.Black = (0, 0, 0)

        # --- Chemins ---
        self.background_path = r"Assets/Image_Menu/background.png"
        self.music_path = r"Assets/Musique_Menu/Ost.mp3"

        # --- Menus ---
        self.main_menu = ["New Game", "Continue", "Options", "Quit"]
        self.options_menu = ["Fullscreen", "Volume", "Back"]
