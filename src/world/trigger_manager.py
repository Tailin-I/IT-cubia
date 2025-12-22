class Trigger:
    """Один триггер на карте"""

    def __init__(self, x, y, width, height, trigger_type, data):
        self.rect = (x, y, width, height)  # Зона триггера
        self.type = trigger_type  # "damage", "teleport", "dialogue"
        self.data = data  # Данные для триггера
        self.activated = False

    def check_collision(self, entity_rect):
        """Проверяем столкновение с сущностью"""
        # Простая проверка прямоугольников
        print(12)
        return self._rects_collide(self.rect, entity_rect)

    def activate(self, entity):
        """Активируем триггер"""
        if not self.activated:
            if self.type == "damage":
                entity.take_damage(self.data["amount"])
            elif self.type == "teleport":
                entity.teleport(self.data["x"], self.data["y"])
            # и т.д.
            self.activated = True


class TriggerManager:
    """Управляет всеми триггерами на карте"""

    def __init__(self):
        self.triggers = []  # Список всех триггеров

    def check_triggers(self, entity):
        """Проверяем все триггеры для сущности"""
        entity_rect = (entity.x, entity.y, entity.width, entity.height)

        for trigger in self.triggers:
            if trigger.check_collision(entity_rect):
                trigger.activate(entity)