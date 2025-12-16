# src/states/pause_menu_state.py
import arcade
import time

from .base_state import BaseState


class PauseMenuState(BaseState):
    """
    Меню паузы (открывается поверх игры).
    """

    def __init__(self, gsm, asset_loader):
        super().__init__("pause_menu", gsm, asset_loader)

        # Пункты меню паузы
        self.menu_items = [
            {"text": "ПРОДОЛЖИТЬ", "action": "resume"},
            {"text": "НАСТРОЙКИ", "action": "settings"},
            {"text": "В ГЛАВНОЕ МЕНЮ", "action": "main_menu"},
            {"text": "ВЫЙТИ ИЗ ИГРЫ", "action": "exit_game"}
        ]

        self.selected_index = 0
        self.cursor_blink_timer = 0
        self.cursor_visible = True
        self.key_cooldown = 0.15
        self.last_key_time = 0

        # Цвета
        self.normal_color = arcade.color.LIGHT_GRAY
        self.selected_color = arcade.color.GOLD
        self.bg_color = (0, 0, 0, 200)  # Полупрозрачный чёрный

        # Размеры окна меню
        self.window_width = 400
        self.window_height = 400

    def on_enter(self, **kwargs):
        """Вход в меню паузы"""

    def on_exit(self):
        """Выход из меню паузы"""

    def update(self, delta_time):
        """Обновление анимации"""
        self.cursor_blink_timer += delta_time
        if self.cursor_blink_timer >= 0.5:
            self.cursor_blink_timer = 0
            self.cursor_visible = not self.cursor_visible

    def draw(self):
        """Отрисовка меню паузы ПОВЕРХ игры"""
        # Полупрозрачный тёмный фон (затемняем игру)
        arcade.draw_rect_filled(
            arcade.rect.LRBT(
                0, self.gsm.window.width,
                0,
                self.gsm.window.height),
            self.bg_color
        )

        # Окно меню (в центре экрана)
        window_x = self.gsm.window.width // 2
        window_y = self.gsm.window.height // 2

        # Фон окна
        arcade.draw_rect_filled(
            arcade.rect.XYWH(
                window_x, window_y,
                self.window_width, self.window_height),
            (30, 30, 40)  # Тёмно-синий
        )

        # Рамка окна
        arcade.draw_rect_outline(
            arcade.rect.XYWH(
                window_x, window_y,
                self.window_width, self.window_height),
                arcade.color.GOLD, 3
        )

        # Заголовок
        arcade.Text(
            "ПАУЗА",
            window_x, window_y + 150,
            arcade.color.GOLD,
            36,
            align="center",
            anchor_x="center",
            anchor_y="center",
            bold=True
        ).draw()

        # Рисуем пункты меню
        self._draw_menu(window_x, window_y)

        # Подсказки
        arcade.Text(
            "↑ ↓ — Выбор  |  ENTER — Подтвердить  |  ESC — Назад",
            window_x, window_y - 180,
            arcade.color.LIGHT_GRAY,
            16,
            align="center",
            anchor_x="center",
            anchor_y="center"
        ).draw()

    def _draw_menu(self, center_x, center_y):
        """Рисует пункты меню паузы"""
        start_y = center_y + 50
        spacing = 60

        for i, item in enumerate(self.menu_items):
            # Выбираем цвет
            if i == self.selected_index:
                color = self.selected_color
                font_size = 28
                is_bold = True
            else:
                color = self.normal_color
                font_size = 24
                is_bold = False

            # Текст пункта
            arcade.Text(
                item["text"],
                center_x, start_y - i * spacing,
                color,
                font_size,
                align="center",
                anchor_x="center",
                anchor_y="center",
                bold=is_bold
            ).draw()

            # Курсор для выбранного пункта
            if i == self.selected_index and self.cursor_visible:
                # Левый треугольник
                arcade.draw_polygon_filled([
                    (center_x - 120, start_y - i * spacing),
                    (center_x - 100, start_y - i * spacing + 10),
                    (center_x - 100, start_y - i * spacing - 10)
                ], self.selected_color)

                # Правый треугольник
                arcade.draw_polygon_filled([
                    (center_x + 120, start_y - i * spacing),
                    (center_x + 100, start_y - i * spacing + 10),
                    (center_x + 100, start_y - i * spacing - 10)
                ], self.selected_color)

    def handle_key_press(self, key, modifiers):
        """Обработка клавиш в меню паузы"""
        if not self.gsm.input_manager:
            return

        current_time = time.time()
        if current_time - self.last_key_time < self.key_cooldown:
            return

        # Навигация
        if self.gsm.input_manager.get_action("up"):
            self.selected_index = max(0, self.selected_index - 1)
            self.last_key_time = current_time

        elif self.gsm.input_manager.get_action("down"):
            self.selected_index = min(len(self.menu_items) - 1, self.selected_index + 1)
            self.last_key_time = current_time

        # Выбор (ENTER)
        elif self.gsm.input_manager.get_action("select"):
            self._select_menu_item()
            self.last_key_time = current_time

        # Назад (ESC) - закрыть меню паузы
        elif self.gsm.input_manager.get_action("escape"):
            self._close_pause_menu()
            self.last_key_time = current_time

    def _select_menu_item(self):
        """Обрабатывает выбор пункта"""
        selected = self.menu_items[self.selected_index]
        print(f"Выбрано в паузе: {selected['text']}")

        if selected["action"] == "resume":
            self._close_pause_menu()

        elif selected["action"] == "settings":
            # Открываем настройки как overlay поверх паузы
            print("Открываем настройки из паузы...")
            self.gsm.push_overlay("settings", is_overlay=True, parent_state="pause_menu")

        elif selected["action"] == "main_menu":
            # Подтверждение выхода в главное меню
            print("Возврат в главное меню...")
            self.gsm.switch_to("lobby")

        elif selected["action"] == "exit_game":
            self.gsm.window.close()

    def _close_pause_menu(self):
        """Закрывает меню паузы (возврат в игру)"""
        if self.gsm.input_manager:
            self.gsm.input_manager.reset_action('escape')
            self.gsm.input_manager.reset_action('select')
        self.gsm.pop_overlay()
