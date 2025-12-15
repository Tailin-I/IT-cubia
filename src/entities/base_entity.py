import arcade


class Entity(arcade.Sprite):
    """Главный класс для всех сущностей"""

    def __init__(self, texture_list, scale):
        super().__init__(texture_list[0], scale)

        self.time_elapsed = 0  # задержка времени для анимации

        # Базовые параметры
        self.speed = 0
        self.health = 100
        self.is_alive = True
        self.direction = "down"

        # Инициализируем текстуры для анимации
        self.textures = texture_list
        self.cur_texture_index = 0

    def update(self, delta_time: float = 1 / 60, *args, **kwargs) -> None:
        pass