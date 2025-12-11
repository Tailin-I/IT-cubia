import os
import arcade
from typing import Dict, Optional


class ResourceManager:
    """Менеджер для загрузки и кэширования ресурсов"""

    def __init__(self):
        self._textures: Dict[str, arcade.Texture] = {}
        self._sounds: Dict[str, arcade.Sound] = {}
        self._project_root = None

    def get_project_root(self) -> str:
        """Ленивая загрузка корня проекта"""
        if self._project_root is None:
            current_file = os.path.abspath(__file__)
            core_dir = os.path.dirname(current_file)
            src_dir = os.path.dirname(core_dir)
            self._project_root = os.path.dirname(src_dir)
        return self._project_root

    def get_resource_path(self, relative_path: str) -> str:
        """Получить абсолютный путь к ресурсу"""
        return os.path.join(self.get_project_root(), "res", relative_path)

    def load_texture(self, relative_path: str) -> arcade.Texture:
        """Загрузить текстуру с кэшированием"""
        if relative_path in self._textures:
            return self._textures[relative_path]

        path = self.get_resource_path(relative_path)
        texture = arcade.load_texture(path)
        self._textures[relative_path] = texture
        return texture

    def load_spritesheet(self, relative_path: str, size=(16, 16), columns=8, count=8):
        """Загрузить spritesheet"""
        path = self.get_resource_path(relative_path)
        grid = arcade.load_spritesheet(path)
        return grid.get_texture_grid(size=size, columns=columns, count=count)

    def load_sound(self, relative_path: str) -> arcade.Sound:
        """Загрузить звук с кэшированием"""
        if relative_path in self._sounds:
            return self._sounds[relative_path]

        path = self.get_resource_path(relative_path)
        sound = arcade.load_sound(path)
        self._sounds[relative_path] = sound
        return sound

    def clear_cache(self):
        """Очистить кэш ресурсов"""
        self._textures.clear()
        self._sounds.clear()


# Глобальный экземпляр менеджера
resource_manager = ResourceManager()