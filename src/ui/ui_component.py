import arcade


class UIComponent:
    """Базовый класс для UI элементов без мыши"""

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = True
        self.enabled = True

    def update(self, delta_time):
        """Обновление анимаций и логики"""
        pass

    def draw(self):
        """Отрисовка элемента"""
        pass

    def is_point_inside(self, px, py):
        """Проверяет, находится ли точка внутри элемента"""
        return (self.x - self.width / 2 <= px <= self.x + self.width / 2 and
                self.y - self.height / 2 <= py <= self.y + self.height / 2)