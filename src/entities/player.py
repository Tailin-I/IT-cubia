import logging
from .base_entity import Entity
from ..core.game_data import game_data


class Player(Entity):
    def __init__(self, texture_dict, input_manager, scale=1):
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        self.data = game_data

        # словарь текстур -> список
        all_textures = []
        for direction in ["up", "down", "left", "right"]:
            all_textures.extend(texture_dict[direction])

        # Вызываем конструктор Entity с масштабом
        super().__init__(all_textures, scale)

        # Сохраняем словарь для удобного доступа
        self.texture_dict = texture_dict
        self.input_manager = input_manager

        # Маппинг направлений на индексы текстур
        self.texture_indexes = {
            "up": 0,  # текстуры 0 и 1
            "down": 2,  # текстуры 2 и 3
            "left": 4,  # текстуры 4 и 5
            "right": 6  # текстуры 6 и 7
        }

        # Для отслеживания смены направления
        self.last_direction = None

        self.setdefault()
        self.setup_hitbox({'left': 0.1, 'right': 0.1, 'top': 0.2, 'bottom': 0})

        # Включаем отладку коллизий (потом можно отключить)
        self.debug_collisions = False

    def setdefault(self):
        pos = self.data.get_player_position()
        self.center_x = pos[0]
        self.center_y = pos[1]

        # Скорость игрока
        self.speed = 50

        # Текущий индекс текстуры для анимации
        self.cur_texture_index = 0

    def update(self, delta_time: float = 1 / 60, *args, **kwargs) -> None:
        super().update(delta_time)
        self.time_elapsed += delta_time

        dx, dy = 0, 0
        current_direction = None

        if self.input_manager.get_action('up'):
            current_direction = "up"
            dy += self.speed * delta_time * 60  # Умножаем на delta_time для плавности
        if self.input_manager.get_action('down'):
            current_direction = "down"
            dy -= self.speed * delta_time * 60
        if self.input_manager.get_action('left'):
            current_direction = "left"
            dx -= self.speed * delta_time * 60
        if self.input_manager.get_action('right'):
            current_direction = "right"
            dx += self.speed * delta_time * 60

        # СРАЗУ меняем текстуру при смене направления
        if current_direction and current_direction != self.last_direction:
            self._set_direction_texture(current_direction)
            self.time_elapsed = 0

        # Анимация
        if current_direction and self.time_elapsed > 0.2:
            self._animate_direction(current_direction)
            self.time_elapsed = 0

        # Если стоим - статичная текстура
        elif not current_direction:
            self._set_idle_texture()

        # Обновляем направление
        if current_direction:
            self.last_direction = current_direction

        # ВАЖНО: Двигаем с учетом коллизий!
        # Нужно передать game_map в update или хранить его в Player
        # Пока добавим через kwargs
        game_map = kwargs.get('game_map')
        if game_map:
            actual_dx, actual_dy = self.move_with_collision(game_map, dx, dy)
        else:
            # Если карты нет - двигаем без коллизий
            self.center_x += dx
            self.center_y += dy
            actual_dx, actual_dy = dx, dy

        # Синхронизируем с game_data
        self.data.set_player_position(self.center_x, self.center_y)

        # Отладочная информация
        if self.debug_collisions and (dx != 0 or dy != 0):
            if actual_dx != dx or actual_dy != dy:
                print(f"Коллизия! Запланировано: ({dx:.1f}, {dy:.1f}), Разрешено: ({actual_dx:.1f}, {actual_dy:.1f})")

    def _set_direction_texture(self, direction):
        """Сразу устанавливает первую текстуру направления"""
        if direction == "up":
            self.cur_texture_index = 0
        elif direction == "down":
            self.cur_texture_index = 2
        elif direction == "left":
            self.cur_texture_index = 4
        elif direction == "right":
            self.cur_texture_index = 6
        self.set_texture(self.cur_texture_index)

    def _animate_direction(self, direction):
        """Анимирует движение в указанном направлении"""
        direction_map = {
            "up": (0, 1),  # текстуры 0 и 1
            "down": (2, 3),  # текстуры 2 и 3
            "left": (4, 5),  # текстуры 4 и 5
            "right": (6, 7)  # текстуры 6 и 7
        }

        tex1, tex2 = direction_map[direction]

        # Переключаем между двумя текстурами
        if self.cur_texture_index == tex1:
            self.cur_texture_index = tex2
            self.set_texture(tex2)
        else:
            self.cur_texture_index = tex1
            self.set_texture(tex1)

    def _set_idle_texture(self):
        """Устанавливает статичную текстуру для стояния"""
        # Определяем последнее направление для idle-позы
        if self.last_direction == "up":
            self.cur_texture_index = 0
            self.set_texture(0)
        elif self.last_direction == "down":
            self.cur_texture_index = 2
            self.set_texture(2)
        elif self.last_direction == "left":
            self.cur_texture_index = 4
            self.set_texture(4)
        elif self.last_direction == "right":
            self.cur_texture_index = 6
            self.set_texture(6)
