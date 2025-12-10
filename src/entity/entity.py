import arcade


class Entity(arcade.Sprite):
    """Главный класс для всех сущностей"""

    def __init__(self, texture_list: list[arcade.Texture]):
        super().__init__(texture_list)

        # Базовые параметры

        self.speed = 0
        self.health = 100
        self.is_alive = True
        self.direction = "down"

    def update(self, delta_time: float = 1 / 60, *args, **kwargs) -> None:
        pass

