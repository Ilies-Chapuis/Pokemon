

from .zones import ZONES


class Carte:
    def __init__(self, largeur=20, hauteur=15):
        self.largeur = largeur
        self.hauteur = hauteur
        self.grille = self._generer()


    def _generer(self):
        return [[self._zone_en(x, y) for x in range(self.largeur)]
                for y in range(self.hauteur)]

    def _zone_en(self, x, y):
        if 8 <= x <= 11 and 6 <= y <= 8:
            return "ville"
        if x < 2 or x >= self.largeur - 2:
            return "ocean"
        if (x < 5 and y < 5) or (x >= self.largeur - 5 and y >= self.hauteur - 5):
            return "montagne"
        if 3 <= x <= 5 and 10 <= y <= 12:
            return "grotte"
        if y < 7 and 5 < x < 14:
            return "foret"
        if y == 0 or (y < 3 and 7 <= x <= 12):
            return "ciel"
        return "plaine"


    def get_zone(self, x, y):
        if 0 <= x < self.largeur and 0 <= y < self.hauteur:
            return self.grille[y][x]
        return "plaine"
