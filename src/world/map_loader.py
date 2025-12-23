import arcade
import logging
import os

from src.events.event_manager import EventManager


class MapLoader:
    """
    Простой загрузчик карт Tiled.
    Только 3 слоя: ground, walls, collisions
    """

    def __init__(self, resource_manager):
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        self.rm = resource_manager
        self.event_manager = None

        # Загруженная карта
        self.tile_map = None
        self.scene = None

        # Слои
        self.ground_layer = None
        self.walls_layer = None
        self.collisions_layer = None

        # Границы карты
        self.bounds = None

    def _load_events(self, scale: float):
        """Загружает события из Tiled"""
        if not self.tile_map:
            return

        # 1. Загружаем зоны взаимодействия из Object Layer "events"
        for layer_name, object_list in self.tile_map.object_lists.items():
            if layer_name.lower() == "events":
                self.event_manager = EventManager(self.rm, self.tile_map.tile_height)
                self.event_manager.load_events_from_objects(object_list, scale)
                break

        # 2. Создаем визуальные спрайты из Tile Layer "chests_visual"
        chests_visual_layer = self.tile_map.sprite_lists.get("chests_visual")
        if chests_visual_layer and self.event_manager:
            self.event_manager.create_visual_sprites_from_tile_layer(
                chests_visual_layer, scale
            )

            # Делаем оригинальные тайлы невидимыми
            for sprite in chests_visual_layer:
                sprite.visible = False

    def _create_chest_sprites_from_layer(self):
        """Создает спрайты сундуков из визуального слоя"""
        if not self.containers_layer or not self.event_manager:
            return

        from src.entities.chest import ChestSprite
        from src.core.resource_manager import resource_manager

        # Для каждого тайла в визуальном слое
        for i, tile_sprite in enumerate(self.containers_layer):
            # Ищем событие рядом с этим тайлом
            chest_event = self._find_chest_event_near(tile_sprite.center_x, tile_sprite.center_y)

            if chest_event:
                # Создаем свой спрайт сундука на тех же координатах
                texture = resource_manager.load_texture("")
                sprite = ChestSprite(
                    texture=texture,
                    x=tile_sprite.center_x,
                    y=tile_sprite.center_y,
                    event=chest_event
                )

                # Связываем событие со спрайтом
                chest_event.set_sprite(sprite)

                # Добавляем спрайт в отдельный список
                if not hasattr(self, 'chest_sprites'):
                    self.chest_sprites = []
                self.chest_sprites.append(sprite)

                print(f"   ✅ Создан спрайт сундука для события {chest_event.event_id}")

    def _find_chest_event_near(self, x, y, max_distance=32):
        """Находит событие сундука рядом с координатами"""
        if not self.event_manager:
            return None

        for event in self.event_manager.events:
            if event.type == "chest":
                # Проверяем расстояние до центра зоны события
                ex, ey, ew, eh = event.rect
                event_center_x = ex + ew / 2
                event_center_y = ey + eh / 2

                distance = ((x - event_center_x)**2 + (y - event_center_y)**2) ** 0.5

                if distance < max_distance:
                    return event
        return None

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
                    "containers": {"use_spatial_hash": False}
                }
            )

            # Получаем слои


            self.ground_layer = self.tile_map.sprite_lists.get("ground")
            self.walls_layer = self.tile_map.sprite_lists.get("walls")
            self.collisions_layer = self.tile_map.sprite_lists.get("collisions")
            self.containers_layer = self.tile_map.sprite_lists.get("containers")

            self._load_events(scale)

            # сцена для отрисовки
            self.scene = arcade.Scene.from_tilemap(self.tile_map)

            if self.collisions_layer:
                for sprite in self.collisions_layer:
                    sprite.visible = False  # Делаем каждый спрайт невидимым

            if self.containers_layer:
                for container in self.collisions_layer:
                    container.visible = False


            # Получаем границы карты
            self._calculate_bounds()

            return True

        except Exception as e:
            self.logger.error(f"Ошибка загрузки карты Tiled {map_file}: {e}")

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


    def update_events(self, delta_time: float, player, game_state):
        """Обновляет события"""
        if self.event_manager:
            self.event_manager.update(delta_time)
            self.event_manager.check_collisions(player, game_state)

    def draw_events(self):
        """Отрисовывает события"""
        if self.event_manager:
            self.event_manager.draw()

    def draw_events_debug(self):
        """Отладочная отрисовка событий"""
        if self.event_manager:
            self.event_manager.draw_debug()