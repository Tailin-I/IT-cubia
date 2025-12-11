from entity.entity import Entity


class Player(Entity):
    def __init__(self, texture_list, key_h):
        # Вызываем конструктор Entity
        super().__init__(texture_list, 3)

        # Для отслеживания смены направления
        self.last_direction = None

        self.textures = texture_list

        self.key_h = key_h

        self.setdefault()

    def setdefault(self):

        # Позиция
        self.center_x = 120
        self.center_y = 300

        # Скорость игрока
        self.speed = 4

    def update(self, delta_time: float = 1 / 60, *args, **kwargs) -> None:
        self.time_elapsed += delta_time

        if self.time_elapsed > 1: # значение увеличено  лдя отладки
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
           self.time_elapsed = 0  # Сбрасываем таймер анимации
           self.last_direction = current_direction

        if dx == 0 and dy == 0:
            self.last_direction = None
            if self.cur_texture_index == 1:
                self.cur_texture_index = 0
            if self.cur_texture_index == 3:
                self.cur_texture_index = 2
            if self.cur_texture_index == 5:
                self.cur_texture_index = 4
            if self.cur_texture_index == 7:
                self.cur_texture_index = 6

        return dx, dy

    def move(self):
        """"персонаж всегда двигается (пусть порой и на 0 px) """
        dx, dy = self.get_movement()
        self.center_x += dx
        self.center_y += dy
