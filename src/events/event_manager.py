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
        Вызывается из MapLoader для слоя "events".
        """
        print(f"🎯 Загрузка {len(object_list)} зон взаимодействия...")

        for i, obj in enumerate(object_list):
            event = self._create_event_from_object(obj, scale, i)
            if event:
                self.events.append(event)

                if self.debug_mode:
                    x, y, w, h = event.rect
                    print(f"  {i}. {event.event_id} ({event.type}) "
                          f"в ({x:.0f}, {y:.0f}) {w:.0f}x{h:.0f}")

        print(f"✅ Загружено {len(self.events)} зон взаимодействия")

    def _create_event_from_object(self, obj, scale: float, index: int):
        """Создает логическое событие из объекта Tiled"""
        try:
            # Получаем координаты и размеры объекта
            x = getattr(obj, 'x', 0) * scale
            y = getattr(obj, 'y', 0) * scale
            width = getattr(obj, 'width', self.tile_size) * scale
            height = getattr(obj, 'height', self.tile_size) * scale

            # Получаем свойства
            properties = getattr(obj, 'properties', {})
            event_type = getattr(obj, 'type', 'trigger').lower()
            event_id = properties.get('id', f"{event_type}_{index}")

            # Создаем соответствующее событие
            if event_type == "chest":
                return self._create_chest_event(event_id, (x, y, width, height), properties)

            elif event_type == "teleport":
                return TeleportEvent(event_id, (x, y, width, height), properties)

            else:
                return GameEvent(event_id, event_type, (x, y, width, height), properties)

        except Exception as e:
            print(f"❌ Ошибка создания события {index}: {e}")
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
            print("⚠️ Слой chests_visual не найден или пуст")
            return

        print(f"🎨 Создание спрайтов из {len(tile_layer)} тайлов сундуков...")

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
                    properties={"event_id": chest_event.event_id}
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

    def _find_nearest_chest_event(self, x: float, y: float, max_distance: float = 32.0):
        """
        Находит ближайшее событие сундука к координатам.
        Используется для связывания тайлов сундуков с зонами взаимодействия.
        """
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

                if distance < min_distance and distance <= max_distance:
                    min_distance = distance
                    nearest_event = event

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
                # Для сундуков дополнительная проверка дистанции
                if event.type == "chest" and hasattr(event, 'sprite'):
                    if self._is_player_close_enough(player, event):
                        event.activate(player, game_state)
                else:
                    event.activate(player, game_state)

    def _is_player_close_enough(self, player, chest_event) -> bool:
        """Проверяет, достаточно ли близко игрок к сундуку"""
        # Центр сундука (из спрайта)
        if chest_event.sprite:
            chest_x = chest_event.sprite.center_x
            chest_y = chest_event.sprite.center_y
        else:
            # Если нет спрайта, используем центр зоны
            x, y, w, h = chest_event.rect
            chest_x = x + w / 2
            chest_y = y + h / 2

        # Дистанция
        distance = ((player.center_x - chest_x) ** 2 +
                    (player.center_y - chest_y) ** 2) ** 0.5

        # Максимальная дистанция для взаимодействия (1.5 тайла)
        max_distance = self.tile_size * 1.5

        if distance > max_distance:
            if self.debug_mode:
                print(f"   📏 Игрок слишком далеко от сундука: {distance:.1f} > {max_distance}")
            return False

        return True

    def draw(self):
        """Отрисовывает визуальные элементы событий"""
        self.chest_sprites.draw()
        self.event_sprites.draw()

    def draw_debug(self):
        """Отрисовывает отладочную информацию"""
        # Зоны взаимодействия
        for event in self.events:
            x, y, width, height = event.rect

            # Цвет в зависимости от типа
            if event.type == "chest":
                color = arcade.color.GOLD if not event.is_opened else arcade.color.GRAY
            elif event.type == "teleport":
                color = arcade.color.CYAN
            else:
                color = arcade.color.GREEN

            # Рамка зоны
            arcade.draw_rect_outline(
                arcade.rect.XYWH(x + width / 2, y + height / 2, width, height),
                color, 2
            )

            # Подпись
            arcade.draw_text(
                f"{event.type}",
                x + width / 2, y + height / 2,
                arcade.color.WHITE, 10,
                anchor_x="center", anchor_y="center"
            )

            # ID события
            if hasattr(event, 'event_id'):
                arcade.draw_text(
                    event.event_id,
                    x + width / 2, y + height / 2 - 15,
                    arcade.color.LIGHT_GRAY, 8,
                    anchor_x="center", anchor_y="center"
                )

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