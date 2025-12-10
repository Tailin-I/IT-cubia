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

    def on_key_press(self, key, modifiers):
        """Обработка нажатия клавиши"""
        self.keys_pressed.add(key)
        self.update_actions()
        # print(arcade.key.key_string(key) + " - pressed!")

    def on_key_release(self, key, modifiers):
        """Обработка отпускания клавиши"""
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)
        self.update_actions()

    def update_actions(self):
        """Обновление состояний действий на основе нажатых клавиш"""
        for action, keys in self.key_bindings.items():
            self.actions[action] = any(key in self.keys_pressed for key in keys)

    def get_action(self, action_name):
        """Проверяет, активно ли действие"""
        return self.actions.get(action_name, False)
