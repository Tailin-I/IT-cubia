import logging
from .base_entity import Entity


class Player(Entity):
    def __init__(self, texture_list, key_h, scale=1):
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")

        # Вызываем конструктор Entity с масштабом
        super().__init__(texture_list, scale)

        # Для отслеживания смены направления
        self.last_direction = None

        self.textures = texture_list
        self.key_h = key_h

        # Параметры хитбокса (но пока не используем)
        self.hitbox_width_ratio = 0.8  # 80% ширины (-0.1 с каждой стороны)
        self.hitbox_height_ratio = 0.7  # 70% высоты (отступ снизу)

        self.setdefault()
        # ВРЕМЕННО ОТКЛЮЧАЕМ хитбокс
        # self.setup_hitbox()  # Настраиваем хитбокс

    def setdefault(self):
        # Позиция
        self.center_x = 120
        self.center_y = 300

        # Скорость игрока
        self.speed = 4

        # Текущий индекс текстуры для анимации
        self.cur_texture_index = 0

    def setup_hitbox(self):
        """
        Настраивает хитбокс для коллизий.
        ВРЕМЕННО ОТКЛЮЧЕНО - будет реализовано позже с коллизиями тайлов.
        """
        # TODO: Реализовать позже с правильным Polygon из Arcade
        self.logger.debug("Хитбокс временно отключен, используем стандартный")
        pass

    def update(self, delta_time: float = 1 / 60, *args, **kwargs) -> None:
        super().update(delta_time)
        self.time_elapsed += delta_time

        # Анимация при движении
        if self.time_elapsed > 0.3:  # значение увеличено для отладки
            # Обновляем анимацию только если игрок движется
            # dx, dy = self.get_movement()
            # if dx != 0 or dy != 0:
            if self.cur_texture_index < len(self.textures):
                self.set_texture(self.cur_texture_index)
            self.time_elapsed = 0

    def get_movement(self):
        """Возвращает нормализованный вектор движения"""
        dx, dy = 0, 0
        current_direction = None

        if self.key_h.actions['move_up']:
            current_direction = "up"
            dy += self.speed
            if self.cur_texture_index == 0:
                self.cur_texture_index = 1
            else:
                self.cur_texture_index = 0
        if self.key_h.actions['move_down']:
            current_direction = "down"
            dy -= self.speed
            if self.cur_texture_index == 2:
                self.cur_texture_index = 3
            else:
                self.cur_texture_index = 2
        if self.key_h.actions['move_left']:
            current_direction = "left"
            dx -= self.speed
            if self.cur_texture_index == 4:
                self.cur_texture_index = 5
            else:
                self.cur_texture_index = 4
        if self.key_h.actions['move_right']:
            current_direction = "right"
            dx += self.speed
            if self.cur_texture_index == 6:
                self.cur_texture_index = 7
            else:
                self.cur_texture_index = 6

        # Проверяем, сменилось ли направление
        if current_direction != self.last_direction:
            self.time_elapsed = 1  # Сбрасываем таймер анимации
            self.last_direction = current_direction

        if dx == 0 and dy == 0:
            self.last_direction = None
            # Возвращаем к первой текстуре в направлении
            if self.cur_texture_index in [0, 1]:
                self.cur_texture_index = 0
            elif self.cur_texture_index in [2, 3]:
                self.cur_texture_index = 2
            elif self.cur_texture_index in [4, 5]:
                self.cur_texture_index = 4
            elif self.cur_texture_index in [6, 7]:
                self.cur_texture_index = 6

        return dx, dy

    def move(self):
        """Персонаж всегда двигается (пусть порой и на 0 px)"""
        dx, dy = self.get_movement()
        self.center_x += dx
        self.center_y += dy