import arcade
from typing import List
from .event import GameEvent
from .chest_event import ChestEvent
from .teleport_event import TeleportEvent


class EventManager:
    def __init__(self, resource_manager, tile_size: int = 64):
        """
        Инициализация менеджера событий.

        Args:
            resource_manager: Менеджер ресурсов для загрузки текстур
            tile_size: Размер тайла в пикселях (для расчетов дистанции)
        """
        self.rm = resource_manager
        self.tile_size = tile_size
        print("ивентменеджер с размером тайла: ", tile_size)

        # Логика событий (зоны взаимодействия из Object Layer)
        self.events: List[GameEvent] = []

        # Визуальные спрайты (будут созданы из Tile Layer "chests_visual")
        self.chest_sprites = arcade.SpriteList()

        # Спрайты других событий (телепорты, NPC и т.д.)
        self.event_sprites = arcade.SpriteList()

        self.debug_mode = False

    def load_events_from_objects(self, object_list, scale: float = 1.0):
        """
        Загружает ТОЛЬКО логические события (зоны взаимодействия) из Object Layer.
        """
        print(f"🎯 Загрузка {len(object_list)} зон взаимодействия...")
        print(f"📐 Масштаб для координат: {scale}")

        for i, obj in enumerate(object_list):
            event = self._create_event_from_object(obj, scale, i)
            if event:
                self.events.append(event)

                # Отладочная информация
                x, y, w, h = event.rect
                print(
                    f"  {i}. {event.event_id} ({event.type}) в Tiled координатах: x={x / scale:.0f}, y={y / scale:.0f}, w={w / scale:.0f}, h={h / scale:.0f}")
                print(f"     Игровые координаты: x={x:.0f}, y={y:.0f}, w={w:.0f}, h={h:.0f}")

                if event.type == "chest":
                    print(f"     Замок: '{getattr(event, 'lock_sequence', 'нет')}'")
                    print(f"     Лут: {getattr(event, 'loot_items', [])}")

        print(f"✅ Загружено {len(self.events)} зон взаимодействия")

    def _create_event_from_object(self, obj, scale: float, index: int):
        """ПРОСТОЙ вариант - без инверсии Y"""
        try:
            # БЕЗ ИНВЕРСИИ - используем координаты как есть
            if hasattr(obj, 'shape') and isinstance(obj.shape, list) and len(obj.shape) >= 4:
                points = obj.shape

                left = points[0][0]
                top = points[0][1]
                right = points[1][0]
                bottom = points[3][1]

                width = right - left
                height = bottom - top

                # НЕ ИНВЕРТИРУЕМ Y!
                x = left
                y = top  # Используем top как y

                # Но height должно быть ПОЛОЖИТЕЛЬНЫМ
                if height < 0:
                    height = abs(height)
                    y = bottom  # Если height отрицательный, начинаем снизу

                print(f"Объект {index}:")
                print(f"   x={x}, y={y}, width={width}, height={height}")

            else:
                x = getattr(obj, 'x', 0) * scale
                y = getattr(obj, 'y', 0) * scale
                width = getattr(obj, 'width', self.tile_size) * scale
                height = getattr(obj, 'height', self.tile_size) * scale

            # Получаем свойства
            properties = getattr(obj, 'properties', {})
            event_type = getattr(obj, 'type', 'trigger').lower()
            event_id = properties.get('id', f"{event_type}_{index}")

            # Создаем событие
            if event_type == "chest":
                return self._create_chest_event(event_id, (x, y, width, height), properties)
            elif event_type == "teleport":
                return TeleportEvent(event_id, (x, y, width, height), properties)
            else:
                return GameEvent(event_id, event_type, (x, y, width, height), properties)

        except Exception as e:
            print(f"❌ Ошибка создания события {index}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _create_chest_event(self, event_id: str, rect: tuple, properties: dict):
        """Создает событие сундука"""
        # Добавляем лут по умолчанию если не указан
        if "loot" not in properties:
            properties["loot"] = "healing_potion:3"

        return ChestEvent(event_id, rect, properties)

    def create_visual_sprites_from_tile_layer(self, tile_layer, scale: float = 1.0):
        """
        Создает визуальные спрайты из Tile Layer "chests_visual".
        Вызывается из MapLoader после загрузки тайлов сундуков.
        """
        if not tile_layer:
            return

        from src.entities.chest import ChestSprite

        for i, tile_sprite in enumerate(tile_layer):
            # Позиция тайла в мире
            sprite_x = tile_sprite.center_x
            sprite_y = tile_sprite.center_y

            # Ищем ближайшее событие сундука для этого тайла
            chest_event = self._find_nearest_chest_event(sprite_x, sprite_y)

            if chest_event:
                # Создаем спрайт сундука
                texture_closed = self.rm.load_texture("containers/chest.png")
                texture_open = self.rm.load_texture("containers/chest_opened.png")

                sprite = ChestSprite(
                    texture=texture_closed,
                    texture_open=texture_open,
                    x=sprite_x,
                    y=sprite_y,
                )

                # Связываем спрайт с событием
                chest_event.set_sprite(sprite)
                self.chest_sprites.append(sprite)

                if self.debug_mode:
                    print(f"  {i}. Спрайт для события '{chest_event.event_id}' "
                          f"в ({sprite_x:.0f}, {sprite_y:.0f})")
            else:
                print(f"⚠️ Для тайла сундука {i} не найдено соответствующего события")

        print(f"✅ Создано {len(self.chest_sprites)} спрайтов сундуков")

    def _find_nearest_chest_event(self, x: float, y: float, max_distance: float = None):
        """
        Находит ближайшее событие сундука к координатам.
        """
        if max_distance is None:
            # Используем 3 тайла как максимальное расстояние
            max_distance = self.tile_size * 3

        print(f"   🔍 Поиск события для позиции ({x:.0f}, {y:.0f}) в радиусе {max_distance}px")

        nearest_event = None
        min_distance = float('inf')

        for event in self.events:
            if event.type == "chest":
                # Получаем центр зоны события
                ex, ey, ew, eh = event.rect
                event_center_x = ex + ew / 2
                event_center_y = ey + eh / 2

                # Вычисляем расстояние
                distance = ((x - event_center_x) ** 2 + (y - event_center_y) ** 2) ** 0.5

                print(
                    f"   📏 Событие {event.event_id} в ({event_center_x:.0f}, {event_center_y:.0f}): расстояние {distance:.1f}px")

                if distance < min_distance and distance <= max_distance:
                    min_distance = distance
                    nearest_event = event

        if nearest_event:
            print(f"   ✅ Связано с событием {nearest_event.event_id} (расстояние: {min_distance:.1f}px)")
        else:
            print(f"   ❌ Событие не найдено в радиусе {max_distance}px")

        return nearest_event

    def update(self, delta_time: float):
        """Обновляет логику событий"""
        for event in self.events:
            event.update(delta_time)

        # Обновляем визуалы сундуков
        for sprite in self.chest_sprites:
            if hasattr(sprite, 'update_visual'):
                sprite.update_visual()

    def check_collisions(self, player, game_state):
        """Проверяет коллизии игрока с событиями"""
        if not player:
            return

        player_rect = (
            player.center_x - player.width / 2,
            player.center_y - player.height / 2,
            player.width,
            player.height
        )



        for event in self.events:
            if event.check_collision(player_rect):
                # print(f"🎯 Коллизия с {event.event_id} ({event.type})")

                # ДЛЯ ВСЕХ СОБЫТИЙ проверяем дистанцию через общий метод
                if self._is_player_close_enough(player, event):

                    # Для сундуков проверяем кнопку взаимодействия
                    if event.type == "chest":
                        if hasattr(player, 'input_manager') and player.input_manager:
                            if player.input_manager.get_action('select'):
                                event.activate(player, game_state)
                    else:
                        # Для других событий (телепортов) активируем сразу
                        event.activate(player, game_state)

    def _is_player_close_enough(self, player, event) -> bool:
        """
            Проверяет, достаточно ли близко игрок к событию.
            Работает для ВСЕХ событий, а не только для сундуков.
            """
        # Центр события (из rect)
        x, y, w, h = event.rect
        event_center_x = x + w / 2
        event_center_y = y + h / 2

        # Если у события есть спрайт - используем его центр
        if hasattr(event, 'sprite') and event.sprite:
            event_center_x = event.sprite.center_x
            event_center_y = event.sprite.center_y

        # Дистанция
        distance = ((player.center_x - event_center_x) ** 2 +
                    (player.center_y - event_center_y) ** 2) ** 0.5

        # Максимальная дистанция для взаимодействия
        max_distance = self.tile_size * 1.5

        if self.debug_mode:
            print(f"   📏 Дистанция до {event.event_id}: {distance:.1f}px (макс: {max_distance}px)")

        return distance <= max_distance

    def draw(self):
        """Отрисовывает визуальные элементы событий"""
        self.chest_sprites.draw()
        self.event_sprites.draw()

    def get_chest_by_id(self, event_id: str):
        """Возвращает событие сундука по ID"""
        for event in self.events:
            if event.type == "chest" and event.event_id == event_id:
                return event
        return None

    def set_debug_mode(self, enabled: bool):
        """Включает/выключает режим отладки"""
        self.debug_mode = enabled
        print(f"🔧 Отладка событий: {'ВКЛ' if enabled else 'ВЫКЛ'}")

    def clear(self):
        """Очищает все события и спрайты"""
        self.events.clear()
        self.chest_sprites.clear()
        self.event_sprites.clear()
