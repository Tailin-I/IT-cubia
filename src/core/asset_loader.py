from ..core.resource_manager import resource_manager


class AssetLoader:
    """Загружает игровые ресурсы (только файлы!)"""

    def __init__(self):
        self.rm = resource_manager
        self._texture_cache = {}  # Кэш ТОЛЬКО текстур

    def load_player_sprites(self, scale=1.0):
        """Загружает спрайты игрока"""
        textures = self.rm.load_spritesheet(
            "player/player_move.png",
            size=(63, 63),
            columns=8,
            count=8
        )
        return {
            "up": [textures[0], textures[1]],
            "down": [textures[2], textures[3]],
            "left": [textures[4], textures[5]],
            "right": [textures[6], textures[7]]
        }

    def load_background(self, name):
        """Загружает фоновую текстуру"""
        path = f"backgrounds/{name}.png"
        return self.rm.load_texture(path)

    def load_ui_texture(self, name):
        """Загружает текстуру для UI (иконки и т.д.)"""
        path = f"ui/{name}.png"
        if path not in self._texture_cache:
            self._texture_cache[path] = self.rm.load_texture(path)
        return self._texture_cache[path]

    def load_sound(self, name):
        """Загружает звуковой файл"""
        path = f"sounds/{name}.wav"
        return self.rm.load_sound(path)

