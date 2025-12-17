# src/entities/hitbox_component.py
import arcade


class HitboxComponent:
    """
    Компонент хитбокса для Entity.
    Позволяет задавать кастомные отступы от спрайта.
    """

    def __init__(self, entity, offsets=None):
        """
        Инициализация хитбокса.

        Args:
            entity: Сущность, к которой привязан хитбокс
            offsets: Словарь с отступами от спрайта в процентах (0-1)
                    Пример: {'left': -0.1, 'right': -0.1, 'top': -0.2, 'bottom': -0.1}
                    Отрицательные значения = уменьшение хитбокса
                    Положительные = увеличение
        """
        self.entity = entity

        # Отступы по умолчанию (без изменений)
        self.offsets = {
            'left': 0,
            'right': 0,
            'top': 0,
            'bottom': 0
        }

        if offsets:
            self.offsets.update(offsets)

    def get_rect(self):
        """
        Возвращает прямоугольник хитбокса в мировых координатах.

        Returns:
            (left, bottom, right, top) - границы прямоугольника
        """
        # Получаем размеры спрайта с учетом scale
        width = self.entity.width
        height = self.entity.height

        # Вычисляем размеры хитбокса с отступами
        hitbox_width = width * (1 - (self.offsets['left'] + self.offsets['right']))
        hitbox_height = height * (1 - (self.offsets['top'] + self.offsets['bottom']))

        # Центр хитбокса совпадает с центром спрайта
        center_x = self.entity.center_x
        center_y = self.entity.center_y

        # Вычисляем границы
        left = center_x - (hitbox_width / 2)
        right = center_x + (hitbox_width / 2)
        bottom = center_y - (hitbox_height / 2)
        top = center_y + (hitbox_height / 2)

        return left, bottom, right, top

    def get_corners(self):
        """
        Возвращает 4 угла хитбокса для более точной проверки коллизий.

        Returns:
            [(x1, y1), (x2, y2), (x3, y3), (x4, y4)] - углы по часовой стрелке
        """
        left, bottom, right, top = self.get_rect()

        return [
            (left, bottom),  # левый нижний
            (right, bottom),  # правый нижний
            (right, top),  # правый верхний
            (left, top)  # левый верхний
        ]

    def draw_debug(self):
        """Отрисовывает хитбокс для отладки (красный прямоугольник)"""
        left, bottom, right, top = self.get_rect()

        # Рисуем прямоугольник
        arcade.draw_rect_outline(
            arcade.rect.XYWH(
                (left + right) / 2,
                (bottom + top) / 2,
                right - left,
                top - bottom
            ),
            arcade.color.RED,
            2
        )