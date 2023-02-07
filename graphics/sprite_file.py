from worlds.ff6wc.WorldsCollide.graphics.sprite import Sprite
from worlds.ff6wc.WorldsCollide.graphics.sprite_tile import SpriteTile

class SpriteFile(Sprite):
    def __init__(self, path, palette):
        self.path = path
        super().__init__([], palette)

        with open(path, "rb") as input_file:
            self.data = list(input_file.read())
