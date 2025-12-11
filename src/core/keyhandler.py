import arcade


class KeyHandler:
    """Класс для обработки ввода с настройкой клавиш"""

    def __init__(self):
        self.keys_pressed = set()

        # Конфигурация клавиш (можно будет загружать из файла)
        self.key_bindings = {
            'move_up': [arcade.key.W, arcade.key.UP],
            'move_down': [arcade.key.S, arcade.key.DOWN],
            'move_left': [arcade.key.A, arcade.key.LEFT],
            'move_right': [arcade.key.D, arcade.key.RIGHT],
            'interact': [arcade.key.E, arcade.key.SPACE],
            'inventory': [arcade.key.I],
            'menu': [arcade.key.ESCAPE],
            'fullscreen': [arcade.key.F11],
        }

        # Состояние действий
        self.actions = {
            'move_up': False,
            'move_down': False,
            'move_left': False,
            'move_right': False,
            'interact': False,
            'inventory': False,
            'menu': False,
            'fullscreen': False,
        }

        # Для отслеживания "полезного" нажатия
        self.last_valid_direction = None

    def on_key_press(self, key, modifiers):
        """Обработка нажатия клавиши"""
        self.keys_pressed.add(key)
        self.update_actions()

        # Определяем, какая клавиша направления была нажата
        new_direction = None
        if key in self.key_bindings['move_up']:
            new_direction = 'move_up'
        elif key in self.key_bindings['move_down']:
            new_direction = 'move_down'
        elif key in self.key_bindings['move_left']:
            new_direction = 'move_left'
        elif key in self.key_bindings['move_right']:
            new_direction = 'move_right'

        # Если нажата клавиша направления
        if new_direction:
            # Отключаем все направления
            for direction in ['move_up', 'move_down', 'move_left', 'move_right']:
                self.actions[direction] = False

            # Включаем только новое направление
            self.actions[new_direction] = True
            self.last_valid_direction = new_direction

    def on_key_release(self, key, modifiers):
        """Обработка отпускания клавиши"""
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)

        # Определяем, была ли отпущена клавиша направления
        released_direction = None
        if key in self.key_bindings['move_up']:
            released_direction = 'move_up'
        elif key in self.key_bindings['move_down']:
            released_direction = 'move_down'
        elif key in self.key_bindings['move_left']:
            released_direction = 'move_left'
        elif key in self.key_bindings['move_right']:
            released_direction = 'move_right'

        # Если отпущено текущее активное направление
        if released_direction and released_direction == self.last_valid_direction:
            self.last_valid_direction = None

            # Ищем следующее активное направление среди нажатых клавиш
            next_direction = None

            # Проверяем в порядке приоритета (можно изменить порядок)
            for direction in ['move_up', 'move_down', 'move_left', 'move_right']:
                if direction != released_direction:
                    # Проверяем, нажата ли какая-то из клавиш этого направления
                    keys = self.key_bindings[direction]
                    if any(k in self.keys_pressed for k in keys):
                        next_direction = direction
                        break

            # Отключаем все направления
            for direction in ['move_up', 'move_down', 'move_left', 'move_right']:
                self.actions[direction] = False

            # Если найдено следующее направление, включаем его
            if next_direction:
                self.actions[next_direction] = True
                self.last_valid_direction = next_direction
            # Иначе обновляем actions обычным способом
            else:
                self.update_actions()
        else:
            # Просто обновляем состояния
            self.update_actions()

    def update_actions(self):
        """Обновление состояний действий на основе нажатых клавиш"""
        # Для НЕ направлений обновляем как обычно
        for action, keys in self.key_bindings.items():
            if action not in ['move_up', 'move_down', 'move_left', 'move_right']:
                self.actions[action] = any(key in self.keys_pressed for key in keys)

    def get_action(self, action_name):
        """Проверяет, активно ли действие"""
        return self.actions.get(action_name, False)