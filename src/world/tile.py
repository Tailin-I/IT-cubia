import arcade


class Tile:
    """Класс для представления одного тайла"""

    def __init__(self, texture, is_blocked):
        self.texture = texture
        self.is_blocked = is_blocked
        self.sprite = None  # Можно добавить спрайт для отрисовки

    def create_sprite(self, x, y, tile_size):
        """Создает спрайт для этого тайла"""
        if not self.sprite:
            self.sprite = arcade.Sprite()
            self.sprite.texture = self.texture
        self.sprite.center_x = x
        self.sprite.center_y = y
        self.sprite.width = tile_size
        self.sprite.height = tile_size
        return self.sprite