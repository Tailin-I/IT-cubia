from src.core.resource_manager import ResourceManager


class AssetLoader:
    """
    Знает КАК загружать разные типы ресурсов.
    Использует ResourceManager для кэширования.
    """

    def __init__(self, resource_manager: ResourceManager):
        self.rm = resource_manager

    def load_player_sprites(self, scale: int = 4):
        """Загружает ВСЕ спрайты игрока с правильной логикой"""
        # 1. Загружаем основной spritesheet
        textures = self.rm.load_spritesheet(
            "player/player.png",
            size=(16, 16),
            columns=8,
            count=8
        )

        # 2. Можем добавить дополнительную логику
        # Например, разделить на направления
        player_assets = {
            "down": [textures[0], textures[1]],
            "up": [textures[2], textures[3]],
            "left": [textures[4], textures[5]],
            "right": [textures[6], textures[7]],
            "idle_down": textures[0],
            "idle_up": textures[2],
            # и т.д.
        }

        return player_assets

    def load_map_tiles(self):
        """Загружает все тайлы для карты"""
        # Специфичная логика загрузки тайлов
        pass

    def load_ui_assets(self):
        """Загружает UI элементы"""
        pass