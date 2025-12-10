import arcade

from entity.entity import Entity


class Player(Entity):
    def __init__(self, texture_list: list[arcade.Texture], key_h):
        # Вызываем конструктор Entity



        super().__init__(texture_list)

        self.key_h = key_h

        self.setdefault()




    def setdefault(self):


        # Позиция
        self.center_x = 120
        self.center_y = 300

        # Скорость игрока
        self.speed = 4


    # def update(self):
    #     self.move()

    # def draw(self):

    def get_movement(self):
        """Возвращает нормализованный вектор движения"""
        dx, dy = 0, 0

        if self.key_h.actions['move_up']:
            dy += self.speed
        if self.key_h.actions['move_down']:
            dy -= self.speed
        if self.key_h.actions['move_left']:
            dx -= self.speed
        if self.key_h.actions['move_right']:
            dx += self.speed

        # Нормализация
        if dx != 0 and dy != 0:
            factor = 0.7071
            dx *= factor
            dy *= factor

        return dx, dy

    def move(self):
        """"персонаж всегда двигается (пусть порой и на 0 px) """
        dx, dy = self.get_movement()
        self.center_x += dx
        self.center_y += dy
