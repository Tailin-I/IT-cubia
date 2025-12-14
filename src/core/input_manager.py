# src/core/input_manager.py
import json
import os
import arcade
from typing import Dict, List, Set


class InputManager:
    """
    Управление вводом с профилями для разных состояний.
    Все клавиши в одном файле настроек.
    """

    def __init__(self, config_path: str = "settings/key_bindings.json"):
        # Активные нажатые клавиши
        self.pressed_keys: Set[int] = set()

        # Текущий профиль (соответствует state_id)
        self.current_profile = "game"

        # Все профили клавиш
        self.profiles: Dict[str, Dict[str, List[int]]] = {}

        # Загружаем или создаем настройки
        self.config_path = config_path
        self._load_or_create_config()

    def _load_or_create_config(self):
        """Загружает настройки или создает стандартные"""
        default_profiles = {
            "global": {
                "fullscreen": [arcade.key.F11],
                "screenshot": [arcade.key.F12],
                "console": [arcade.key.GRAVE]
            },
            "lobby": {
                "menu_up": [arcade.key.UP, arcade.key.W],
                "menu_down": [arcade.key.DOWN, arcade.key.S],
                "select": [arcade.key.ENTER, arcade.key.E],
                "back": [arcade.key.ESCAPE]
            },
            "pause_menu": {
                "menu_up": [arcade.key.UP, arcade.key.W],
                "menu_down": [arcade.key.DOWN, arcade.key.S],
                "select": [arcade.key.ENTER, arcade.key.SPACE, arcade.key.E],
                "back": [arcade.key.ESCAPE]
            },
            "settings": {
                "menu_up": [arcade.key.UP, arcade.key.W],
                "menu_down": [arcade.key.DOWN, arcade.key.S],
                "menu_left": [arcade.key.A, arcade.key.LEFT],
                "menu_right": [arcade.key.D, arcade.key.RIGHT],
                "select": [arcade.key.ENTER, arcade.key.E],
                "back": [arcade.key.ESCAPE]
            },
            "game": {
                "move_up": [arcade.key.W, arcade.key.UP],
                "move_down": [arcade.key.S, arcade.key.DOWN],
                "move_left": [arcade.key.A, arcade.key.LEFT],
                "move_right": [arcade.key.D, arcade.key.RIGHT],
                "inventory": [arcade.key.I, arcade.key.TAB],
                "interact": [arcade.key.E],
                "pause": [arcade.key.ESCAPE, arcade.key.P],
                "run": [arcade.key.LSHIFT]
            }
        }

        # Пробуем загрузить из файла
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.profiles = json.load(f)
                # Конвертируем строки в коды клавиш
                self._convert_strings_to_codes()
            except Exception as e:
                print(f"Ошибка загрузки настроек: {e}. Используем стандартные.")
                self.profiles = default_profiles
                self._save_config()
        else:
            # Создаем файл с настройками по умолчанию
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            self.profiles = default_profiles
            self._save_config()

    def _save_config(self):
        """Сохраняет текущие настройки в файл"""
        try:
            # Конвертируем коды в строки для сохранения
            save_data = self._convert_codes_to_strings()
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")

    def set_current_profile(self, profile_name: str):
        """Устанавливает активный профиль ввода"""
        self.pressed_keys.clear()

        if profile_name in self.profiles or profile_name == "global":
            self.current_profile = profile_name
            print(f"Установлен профиль ввода: {profile_name}")
        else:
            print(f"Профиль '{profile_name}' не найден, используем 'game'")
            self.current_profile = "game"

    def is_action_pressed(self, action_name: str) -> bool:
        """
        Проверяет, нажато ли указанное действие.
        Сначала проверяет текущий профиль, потом глобальный.
        """
        # Проверяем в текущем профиле
        if self.current_profile in self.profiles:
            if action_name in self.profiles[self.current_profile]:
                for key in self.profiles[self.current_profile][action_name]:
                    if key in self.pressed_keys:
                        return True

        # Проверяем в глобальных (работают всегда)
        if "global" in self.profiles:
            if action_name in self.profiles["global"]:
                for key in self.profiles["global"][action_name]:
                    if key in self.pressed_keys:
                        return True

        return False

    def on_key_press(self, key: int, modifiers: int):
        """Обработка нажатия клавиши"""
        self.pressed_keys.add(key)

    def on_key_release(self, key: int, modifiers: int):
        """Обработка отпускания клавиши"""
        self.pressed_keys.discard(key)

    # Вспомогательные методы для конвертации (упрощенные)
    def _convert_strings_to_codes(self):
        """Конвертирует строки в коды клавиш (для загрузки)"""
        # Простая реализация - можно расширить
        string_to_code = {
            "UP": arcade.key.UP, "DOWN": arcade.key.DOWN,
            "LEFT": arcade.key.LEFT, "RIGHT": arcade.key.RIGHT,
            "W": arcade.key.W, "A": arcade.key.A,
            "S": arcade.key.S, "D": arcade.key.D,
            "E": arcade.key.E, "Q": arcade.key.Q,
            "I": arcade.key.I, "TAB": arcade.key.TAB,
            "ENTER": arcade.key.ENTER, "SPACE": arcade.key.SPACE,
            "ESCAPE": arcade.key.ESCAPE, "F11": arcade.key.F11,
            "F12": arcade.key.F12, "P": arcade.key.P,
            "LSHIFT": arcade.key.LSHIFT, "GRAVE": arcade.key.GRAVE
        }

        # Конвертируем все профили
        for profile_name, actions in self.profiles.items():
            for action_name, key_strings in actions.items():
                codes = []
                for key_str in key_strings:
                    if key_str in string_to_code:
                        codes.append(string_to_code[key_str])
                self.profiles[profile_name][action_name] = codes

    def _convert_codes_to_strings(self) -> Dict:
        """Конвертирует коды клавиш в строки (для сохранения)"""
        # Обратная конвертация (упрощенная)
        code_to_string = {v: k for k, v in {
            "UP": arcade.key.UP, "DOWN": arcade.key.DOWN,
            "LEFT": arcade.key.LEFT, "RIGHT": arcade.key.RIGHT,
            "W": arcade.key.W, "A": arcade.key.A,
            "S": arcade.key.S, "D": arcade.key.D,
            "E": arcade.key.E, "Q": arcade.key.Q,
            "I": arcade.key.I, "TAB": arcade.key.TAB,
            "ENTER": arcade.key.ENTER, "SPACE": arcade.key.SPACE,
            "ESCAPE": arcade.key.ESCAPE, "F11": arcade.key.F11,
            "F12": arcade.key.F12, "P": arcade.key.P,
            "LSHIFT": arcade.key.LSHIFT, "GRAVE": arcade.key.GRAVE
        }.items()}

        save_data = {}
        for profile_name, actions in self.profiles.items():
            save_data[profile_name] = {}
            for action_name, key_codes in actions.items():
                strings = []
                for code in key_codes:
                    if code in code_to_string:
                        strings.append(code_to_string[code])
                save_data[profile_name][action_name] = strings

        return save_data