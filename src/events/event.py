import logging
from typing import Dict, Any


class GameEvent:
    """Базовый класс игрового события"""

    def __init__(self, event_id: str, event_type: str, rect, properties: Dict[str, Any] = None):
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")

        self.event_id = event_id
        self.type = event_type  # "teleport", "damage", "dialogue"..
        self.rect = rect  # (x, y, width, height) в пикселях
        self.properties = properties or {}
        self.activated = False
        self.cooldown = 0
        self.max_cooldown = 60  # 1 секунда при 60 FPS

    def check_collision(self, player_rect) -> bool:
        """Проверяет пересечение с игроком"""
        px, py, pw, ph = player_rect
        ex, ey, ew, eh = self.rect

        return (px < ex + ew and px + pw > ex and
                py < ey + eh and py + ph > ey)

    def activate(self, player, game_state):
        """Активирует событие"""
        pass


    def update(self, delta_time: float):
        """Обновление кулдауна"""
        if self.cooldown > 0:
            self.cooldown -= 1
        if self.cooldown <= 0:
            self.activated = False