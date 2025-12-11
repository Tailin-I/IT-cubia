import arcade
import json
import os


class KeyHandler:
    """Класс для обработки ввода с настройкой клавиш"""

    def __init__(self, config_file="settings/key_bindings.json"):
        """
        Инициализация обработчика клавиш
        config_file: имя файла для сохранения/загрузки настроек
        """
        self.keys_pressed = set()
        self.config_file = config_file

        # Конфигурация клавиш по умолчанию
        self.default_key_bindings = {
            'move_up': [arcade.key.W, arcade.key.UP],
            'move_down': [arcade.key.S, arcade.key.DOWN],
            'move_left': [arcade.key.A, arcade.key.LEFT],
            'move_right': [arcade.key.D, arcade.key.RIGHT],
            'interact': [arcade.key.E],
            'inventory': [arcade.key.I],
            'menu': [arcade.key.ESCAPE],
            'fullscreen': [arcade.key.F11],
        }

        # Загружаем настройки или используем значения по умолчанию
        self.key_bindings = self.load_key_bindings()

        # Состояние действий
        self.actions = {}
        self._init_actions()

        # Для отслеживания "полезного" нажатия
        self.last_valid_direction = None

    def _init_actions(self):
        """Инициализирует состояния всех действий как False"""
        for action in self.key_bindings:
            self.actions[action] = False

    # работа с JSON
    def load_key_bindings(self):
        """
        Загружает привязки клавиш из JSON файла.
        Если файл не существует, создает его с настройками по умолчанию.
        """
        # Проверка, существует ли файл
        if os.path.exists(self.config_file):
            try:
                # Открываем файл для чтения
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    # Загружаем данные из JSON
                    saved_data = json.load(f)
                    print(saved_data)


                print(f"✓ Настройки загружены из {self.config_file}")
                return saved_data

            except json.JSONDecodeError:
                print(f"✗ Ошибка чтения файла {self.config_file}.\nКлавиши установлены по умолчанию.")
                return self.default_key_bindings.copy()
            except Exception as e:
                print(f"✗ Ошибка при загрузке настроек: {e}.\nКлавиши установлены по умолчанию.")
                return self.default_key_bindings.copy()
        else:
            # Файл не существует, создаем его с настройками по умолчанию
            print(f"ℹ Файл настроек не найден. Создан новый...")
            self.save_key_bindings()
            return self.default_key_bindings.copy()

    def save_key_bindings(self):
        """
        Сохраняет текущие привязки клавиш в JSON файл.
        """
        try:
            # Открываем файл для записи
            with open(self.config_file, 'w', encoding='utf-8') as f:
                # Сохраняем данные в JSON с красивым форматированием
                json.dump(self.key_bindings, f, indent=4, ensure_ascii=False)

            print(f"✓ Настройки сохранены в {self.config_file}")
            return True

        except Exception as e:
            print(f"✗ Ошибка при сохранении настроек: {e}")
            return False

    def reset_to_defaults(self):
        """
        Сбрасывает все привязки к значениям по умолчанию.
        """
        self.key_bindings = self.default_key_bindings.copy()
        self._init_actions()
        self.save_key_bindings()
        print("✓ Настройки сброшены к значениям по умолчанию")

    def rebind_action(self, action_name, new_key):
        """
        Переназначает клавишу для указанного действия.

        Args:
            action_name (str): Название действия ('move_up', 'interact' и т.д.)
            new_key (int): Код новой клавиши из arcade.key.*

        Returns:
            bool: True если переназначение успешно, False в противном случае
        """
        if action_name not in self.key_bindings:
            print(f"✗ Ошибка: действие '{action_name}' не найдено")
            return False

        # Проверяем, не используется ли клавиша для другого действия
        conflict_action = None
        for action, keys in self.key_bindings.items():
            if new_key in keys and action != action_name:
                conflict_action = action
                break

        if conflict_action:
            # Можно либо запретить, либо удалить из старого действия
            print(f"⚠ Клавиша уже используется для '{conflict_action}'")
            # Удаление клавиши из старого действия
            # self.key_bindings[conflict_action].remove(new_key)

        # Добавляем новую клавишу к действию
        if new_key not in self.key_bindings[action_name]:
            self.key_bindings[action_name].append(new_key)

        # Сохраняем изменения
        self.save_key_bindings()
        print(f"✓ Клавиша переназначена для действия '{action_name}'")
        return True

    def remove_key_binding(self, action_name, key_to_remove):
        """
        Удаляет привязку клавиши для указанного действия.
        """
        if action_name in self.key_bindings and key_to_remove in self.key_bindings[action_name]:
            self.key_bindings[action_name].remove(key_to_remove)
            self.save_key_bindings()
            print(f"✓ Привязка удалена для действия '{action_name}'")
            return True
        return False

    # Шаг 5: Методы для отображения информации (полезно в меню настроек)
    def get_key_names(self, key_codes):
        """
        Преобразует коды клавиш в читаемые имена.

        Args:
            key_codes (list): Список кодов клавиш

        Returns:
            list: Список имен клавиш
        """
        # Словарь для преобразования кодов в имена
        key_names = {
            arcade.key.W: "W",
            arcade.key.A: "A",
            arcade.key.S: "S",
            arcade.key.D: "D",
            arcade.key.E: "E",
            arcade.key.I: "I",
            arcade.key.ESCAPE: "Esc",
            arcade.key.F11: "F11",
            arcade.key.UP: "↑",
            arcade.key.DOWN: "↓",
            arcade.key.LEFT: "←",
            arcade.key.RIGHT: "→",
            arcade.key.SPACE: "Пробел",
        }

        names = []
        for key_code in key_codes:
            names.append(key_names.get(key_code, f"Клавиша {key_code}"))

        return names

    def get_action_info(self):
        """
        Возвращает информацию о всех действиях и их привязках.
        Полезно для отображения в меню настроек.
        """
        info = {}
        for action, keys in self.key_bindings.items():
            info[action] = {
                'keys': keys,
                'key_names': self.get_key_names(keys)
            }
        return info

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