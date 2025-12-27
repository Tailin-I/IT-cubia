import arcade
import logging

from src.core.resource_manager import resource_manager
from src.events.event_manager import EventManager
from config import constants as C
from pathlib import Path

class MapLoader:
    """
    Загрузчик карт Tiled.
    """

    def __init__(self):
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
        self.containers_layer = None

        # Границы карты
        self.bounds = None

    def _load_events(self, scale: float):
        """Загружает события из Tiled"""
        if not self.tile_map:
            return

        # 2. Загружаем зоны взаимодействия из Object Layer "events"
        events_loaded = False
        for layer_name, object_list in self.tile_map.object_lists.items():
            if layer_name.lower() == "events":
                self.event_manager.load_events_from_objects(object_list, scale)
                events_loaded = True
                print(f"✅ Загружено событий: {len(self.event_manager.events)}")
                break

        if not events_loaded:
            print("⚠️ Слой 'events' не найден в Tiled карте")

        # 3. Создаем визуальные спрайты из Tile Layer "containers"
        containers_layer = self.tile_map.sprite_lists.get("containers")
        if containers_layer and self.event_manager:
            self._create_chest_sprites_from_layer(containers_layer, scale)

    def _create_chest_sprites_from_layer(self, containers_layer, scale):
        """Создает спрайты сундуков из визуального слоя"""
        from src.entities.chest import ChestSprite

        for tile_sprite in containers_layer:
            sprite_x = tile_sprite.center_x
            sprite_y = tile_sprite.center_y

            # Поиск события с увеличенным радиусом
            chest_event = self.event_manager.find_nearest_chest_event(
                sprite_x, sprite_y,
                max_distance=self.tile_map.tile_width * 3
            )

            if chest_event:
                try:
                    texture_closed = self.rm.load_texture("containers/chest.png")
                    texture_open = self.rm.load_texture("containers/chest_opened.png")

                    sprite = ChestSprite(
                        texture=texture_closed,
                        texture_open=texture_open,
                        x=sprite_x,
                        y=sprite_y,
                        event=chest_event,
                        scale=scale
                    )

                    chest_event.set_sprite(sprite)
                    self.event_manager.chest_sprites.append(sprite)
                    # tile_sprite.visible = False

                except Exception as e:
                    self.logger.warning(f"❌ Ошибка создания спрайта: {e}")

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

                distance = ((x - event_center_x) ** 2 + (y - event_center_y) ** 2) ** 0.5

                if distance < max_distance:
                    return event
        return None

    def load(self, map_file: str, scale: float = C.SCALE_FACTOR) -> bool:
        """
        Загружает Tiled карту.
        """
        try:
            self.event_manager = EventManager()

            # Используем pathlib для кроссплатформенных путей
            map_file_path = Path(map_file)

            # Полный путь к файлу
            project_root = Path(self.rm.get_project_root())
            map_path = project_root / "res" / map_file_path

            self.logger.info(f"Загрузка карты: {map_path}... {'успешно' if map_path.exists() else 'ошибка'}")

            # Проверяем существование файла
            if not map_path.exists():
                self.logger.warning(f"❌ Файл карты не найден: {map_path}")
                self._calculate_bounds()
                return False

            # Загружаем карту через Arcade - передаем строку
            self.tile_map = arcade.load_tilemap(
                str(map_path),  # Преобразуем Path в строку
                scaling=scale,
                layer_options={
                    "ground": {"use_spatial_hash": False},
                    "walls": {"use_spatial_hash": False},
                    "collisions": {"use_spatial_hash": True},
                    "containers": {"use_spatial_hash": False}
                }
            )
            # Получаем слои
            self.ground_layer = self.tile_map.sprite_lists.get("ground")
            self.walls_layer = self.tile_map.sprite_lists.get("walls")
            self.collisions_layer = self.tile_map.sprite_lists.get("collisions")
            self.containers_layer = self.tile_map.sprite_lists.get("containers")

            print(
                f"Слои загружены: ground={bool(self.ground_layer)}, walls={bool(self.walls_layer)}, containers={bool(self.containers_layer)}")

            # Загружаем события
            self._load_events(scale)

            # Создаем сцену для отрисовки
            self.scene = arcade.Scene.from_tilemap(self.tile_map)

            # Скрываем невидимые слои
            if self.collisions_layer:
                for sprite in self.collisions_layer:
                    sprite.visible = False

            if self.containers_layer:
                for container in self.containers_layer:
                    container.visible = False

            # Получаем границы карты
            self._calculate_bounds()

            return True

        except Exception as e:
            self.logger.error(f"Ошибка загрузки карты Tiled {map_file}: {e}")
            import traceback
            traceback.print_exc()
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
