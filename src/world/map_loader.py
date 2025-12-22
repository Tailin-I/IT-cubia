import arcade
import logging
import os


class MapLoader:
    """
    Простой загрузчик карт Tiled.
    Только 3 слоя: ground, walls, collisions
    """

    def __init__(self, resource_manager):
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        self.rm = resource_manager

        # Загруженная карта
        self.tile_map = None
        self.scene = None

        # Слои
        self.ground_layer = None
        self.walls_layer = None
        self.collisions_layer = None

        # Границы карты
        self.bounds = None

    def load(self, map_file: str, scale: float = 1.0) -> bool:
        """
        Загружает Tiled карту.

        Args:
            map_file: путь к .tmx файлу (например, "maps/forest_tiled.tmx")
            scale: масштаб

        Returns:
            True если успешно
        """
        try:
            # Полный путь к файлу
            map_path = os.path.join(self.rm.get_project_root(), "res", map_file)

            # Загружаем карту через Arcade
            self.tile_map = arcade.load_tilemap(
                map_path,
                scaling=scale,
                layer_options={
                    "ground": {"use_spatial_hash": False},
                    "walls": {"use_spatial_hash": False},
                    "collisions": {"use_spatial_hash": True},  # Важно для коллизий!
                }
            )

            # Получаем слои
            self.ground_layer = self.tile_map.sprite_lists.get("ground")
            self.walls_layer = self.tile_map.sprite_lists.get("walls")
            self.collisions_layer = self.tile_map.sprite_lists.get("collisions")


            if self.collisions_layer:
                for sprite in self.collisions_layer:
                    sprite.visible = False  # Делаем каждый спрайт невидимым
            # Создаем сцену
            self.scene = arcade.Scene.from_tilemap(self.tile_map)

            # Получаем границы карты
            self._calculate_bounds()

            self.logger.info(f"Карта Tiled загружена: {map_file}")
            self.logger.info(f"Размеры: {self.bounds['width']}x{self.bounds['height']}")
            self.logger.info(f"Слои: ground={bool(self.ground_layer)}, "
                             f"walls={bool(self.walls_layer)}, "
                             f"collisions={bool(self.collisions_layer)}")

            return True

        except Exception as e:
            self.logger.error(f"Ошибка загрузки карты Tiled {map_file}: {e}")
            # Создаем fallback
            self._create_fallback_map()
            return False

    def _calculate_bounds(self):
        """Вычисляет границы карты"""
        if not self.tile_map:
            self.bounds = {'left': 0, 'right': 0, 'bottom': 0, 'top': 0, 'width': 0, 'height': 0}
            return

        # Tiled хранит размеры в тайлах, переводим в пиксели
        width_tiles = self.tile_map.width
        height_tiles = self.tile_map.height
        tile_width = self.tile_map.tile_width
        tile_height = self.tile_map.tile_height

        self.bounds = {
            'left': 0,
            'bottom': 0,
            'right': width_tiles * tile_width,
            'top': height_tiles * tile_height,
            'width': width_tiles * tile_width,
            'height': height_tiles * tile_height,
        }

    def _create_fallback_map(self):
        """Создает простую карту при ошибке"""
        self.logger.warning("Создаю fallback карту")

        # Создаем пустые спрайтлисты
        self.ground_layer = arcade.SpriteList()
        self.walls_layer = arcade.SpriteList()
        self.collisions_layer = arcade.SpriteList(use_spatial_hash=True)

        # Простая карта 20x15
        width_tiles = 20
        height_tiles = 15
        tile_size = 64

        # Здесь можно добавить простые тайлы...
        self.bounds = {
            'left': 0,
            'bottom': 0,
            'right': width_tiles * tile_size,
            'top': height_tiles * tile_size,
            'width': width_tiles * tile_size,
            'height': height_tiles * tile_size,
        }

        self.scene = arcade.Scene()
        self.scene.add_sprite_list("ground", sprite_list=self.ground_layer)
        self.scene.add_sprite_list("walls", sprite_list=self.walls_layer)
        self.scene.add_sprite_list("collisions", sprite_list=self.collisions_layer)

    def is_solid_at(self, x: float, y: float) -> bool:
        """Проверяет, есть ли коллизия в координатах (x, y)"""
        if not self.collisions_layer:
            return False

        # Создаем временный спрайт для проверки
        temp_sprite = arcade.Sprite()
        temp_sprite.center_x = x
        temp_sprite.center_y = y
        temp_sprite.width = 10
        temp_sprite.height = 10

        hits = arcade.check_for_collision_with_list(temp_sprite, self.collisions_layer)
        return len(hits) > 0

    def get_collision_layer(self):
        """Возвращает слой коллизий"""
        return self.collisions_layer

    def get_bounds(self):
        """Возвращает границы карты"""
        return self.bounds

    def draw(self):
        """Отрисовывает карту"""
        if self.scene:
            self.scene.draw()
