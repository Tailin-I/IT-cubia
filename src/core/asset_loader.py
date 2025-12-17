import arcade

from src.core.resource_manager import ResourceManager


class AssetLoader:
    def __init__(self, resource_manager: ResourceManager):
        self.rm = resource_manager
        self._ui_textures = {}  # Кэш UI текстур

    def load_player_sprites(self, scale=1.0):
        """Загружает спрайты игрока с возможностью масштабирования"""
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

    def load_ui_texture(self, path: str):
        """Загружает текстуру для UI с кэшированием"""
        if path not in self._ui_textures:
            self._ui_textures[path] = self.rm.load_texture(path)
        return self._ui_textures[path]

    def load_sound_effect(self, path: str):
        """Загружает звуковой эффект"""
        return self.rm.load_sound(path)

    def load_background(self, path: str):
        """Загружает фоновое изображение"""
        return self.rm.load_texture(path)

    def get_ui_assets(self):
        """Возвращает все стандартные UI ассеты"""
        return {
            "button_normal": self.load_ui_texture("ui/button_normal.png"),
        }