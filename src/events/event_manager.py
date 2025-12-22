
import arcade

from .event import GameEvent


class EventManager:
    """Управляет всеми событиями на карте"""

    def __init__(self):
        self.events = []  # Список всех событий
        self.active_events = {}  # Активные события по ID

    def load_from_tiled(self, tiled_object_list):
        """Загружает события из Tiled Object Layer"""
        for obj in tiled_object_list:
            # Определяем тип события
            event_type = obj.properties.get("type", "trigger")

            # Создаем событие
            event = GameEvent(
                event_id=obj.properties.get("id", f"event_{len(self.events)}"),
                event_type=event_type,
                rect=(obj.x, obj.y, obj.width, obj.height),
                properties=obj.properties
            )

            self.events.append(event)
            print(f"Загружено событие: {event.event_id} ({event_type})")

    def check_events(self, player, game_state):
        """Проверяет все события на столкновение с игроком"""
        player_rect = (
            player.center_x - player.width / 2,
            player.center_y - player.height / 2,
            player.width,
            player.height
        )

        for event in self.events:
            if event.check_collision(player_rect):
                event.activate(player, game_state)

    def update(self, delta_time: float):
        """Обновляет все события"""
        for event in self.events:
            event.update(delta_time)

    def draw_debug(self):
        """Отрисовывает события для отладки (только в режиме отладки)"""
        for event in self.events:
            # Рисуем прямоугольник события
            x, y, w, h = event.rect
            color = arcade.color.RED if event.activated else arcade.color.GREEN
            arcade.draw_rect_outline(
                arcade.rect.XYWH(x + w / 2, y + h / 2, w, h),
                color, 2
            )

            # Подпись
            arcade.Text(
                f"{event.type}",
                x + w / 2, y + h / 2,
                arcade.color.WHITE, 10,
                anchor_x="center", anchor_y="center"
            )