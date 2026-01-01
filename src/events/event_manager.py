import logging

import arcade
from typing import List
from .event import GameEvent
from .chest_event import ChestEvent
from .teleport_event import TeleportEvent
from config import  constants as C
from ..core.resource_manager import resource_manager


class EventManager:
    def __init__(self):
        """
        Инициализация менеджера событий.
        """
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")

        self.rm = resource_manager
        self.tile_size = C.TILE_SIZE

        # Логика событий (зоны взаимодействия из Object Layer)
        self.events: List[GameEvent] = []

        # Визуальные спрайты (будут созданы из Tile Layer "chests_visual")
        self.chest_sprites = arcade.SpriteList()

        # Спрайты других событий (телепорты, NPC и т.д.)
        self.event_sprites = arcade.SpriteList()

        self.debug_mode = False

    def load_events_from_objects(self, object_list, scale: float = 1.0):
        """
        Загружает события (зоны взаимодействия) из events
        """

        for i, obj in enumerate(object_list):
            event = self._create_event_from_object(obj, scale, i)
            if event:
                self.events.append(event)

    def _create_event_from_object(self, obj, scale: float, index: int):
        """Создаёт события"""
        try:
            if hasattr(obj, 'shape') and isinstance(obj.shape, list) and len(obj.shape) >= 4:
                points = obj.shape

                left = points[0][0]
                top = points[0][1]
                right = points[1][0]
                bottom = points[3][1]

                width = right - left
                height = bottom - top

                x = left
                y = top

                if height < 0:
                    height = abs(height)
                    y = bottom


            else:
                x = getattr(obj, 'x', 0) * scale
                y = getattr(obj, 'y', 0) * scale
                width = getattr(obj, 'width', self.tile_size) * scale
                height = getattr(obj, 'height', self.tile_size) * scale

            # Получаем свойства
            properties = getattr(obj, 'properties', {})
            event_type = getattr(obj, 'type', 'trigger').lower()
            name = getattr(obj, 'name','!')
            event_id = properties.get('id', f"{event_type}_{index}")

            # Создаем событие
            if event_type == "chest":
                return self._create_chest_event(event_id, name, (x, y, width, height), properties)
            elif event_type == "teleport":
                return TeleportEvent(event_id, name,(x, y, width, height), properties)
            else:
                return GameEvent(event_id, name, event_type, (x, y, width, height), properties)

        except Exception as e:
            self.logger.warning(f"❌ Ошибка создания события {index}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _create_chest_event(self, event_id: str, name: str, rect: tuple, properties: dict):
        """Создает событие сундука"""
        # Добавляем лут по умолчанию если не указан
        if "loot" not in properties:
            properties["loot"] = "healing_potion:3"

        return ChestEvent(event_id, name, rect, properties)

    def find_nearest_chest_event(self, x: float, y: float, max_distance: float = None):
        """
        Находит ближайшее событие сундука к координатам.
        """
        if max_distance is None:
            # Используем 3 тайла как максимальное расстояние
            max_distance = self.tile_size * 3

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


                # ДЛЯ ВСЕХ СОБЫТИЙ проверяем дистанцию через общий метод
                if self._is_player_close_enough(player, event):
                    # Для сундуков проверяем кнопку взаимодействия
                    if event.type == "chest":
                        event.show_text_description = True
                        if hasattr(player, 'input_manager') and player.input_manager:
                            if player.input_manager.get_action('select'):
                                event.activate(player, game_state)
                    else:
                        # Для других событий (телепортов) активируем сразу
                        event.activate(player, game_state)

    def _is_player_close_enough(self, player, event) -> bool:
        """Проверяет, достаточно ли близко игрок к событию."""
        # Центр события (из rect)
        x, y, w, h = event.rect
        event_center_x = x + w / 2
        event_center_y = y + h / 2


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

        for i in self.events:
            if i.type == "chest":
                i.draw_names()



        if C.debug_mode:
            for i in self.events:
                i.draw_debug()

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
