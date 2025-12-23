import logging
from typing import Dict, Any, Optional


class GameEvent:
    """Базовый класс для игровых событий"""



    def __init__(self, event_id: str, event_type: str, rect: tuple, properties: Dict[str, Any] = None):
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")

        self.tileSize = 64

        self.event_id = event_id
        self.type = event_type  # "chest", "teleport", "dialogue"
        self.rect = rect  # (x, y, width, height)
        self.properties = properties or {}
        self.activated = False
        self.cooldown = 0
        self.max_cooldown = 30  # 0.5 секунды при 60 FPS

    def check_collision(self, player_rect) -> bool:
        """Проверяет пересечение с игроком"""
        px, py, pw, ph = player_rect
        ex, ey, ew, eh = self.rect

        # Простая проверка прямоугольников
        collision = (px < ex + ew and
                     px + pw > ex and
                     py < ey + eh and
                     py + ph > ey)

        if collision and hasattr(self, 'logger'):
            self.logger.debug(f"Коллизия с {self.event_id}")

        return collision

    def activate(self, player, game_state):
        """Активировать событие - будет переопределено"""
        pass

    def update(self, delta_time: float):
        """Обновление кулдауна"""
        if self.cooldown > 0:
            self.cooldown -= 1
        if self.cooldown <= 0:
            self.activated = False

    def set_sprite(self, sprite):
        pass
