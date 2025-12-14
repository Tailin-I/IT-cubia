# src/states/settings_state.py
import arcade
import time

from .base_state import BaseState


class SettingsState(BaseState):
    """
    Состояние настроек.
    Полностью заменяет лобби при открытии.
    """

    def __init__(self, gsm, asset_loader):
        super().__init__("settings", gsm, asset_loader)

        # Пункты меню настроек
        self.menu_items = [
            {"text": "ГРОМКОСТЬ", "action": "volume", "value": 70},
            {"text": "УПРАВЛЕНИЕ", "action": "controls"},
            {"text": "ГРАФИКА", "action": "graphics"},
            {"text": "НАЗАД", "action": "back"}
        ]

        self.selected_index = 0
        self.cursor_blink_timer = 0
        self.cursor_visible = True
        self.key_cooldown = 0.15
        self.last_key_time = 0

        # Цвета
        self.normal_color = arcade.color.LIGHT_GRAY
        self.selected_color = arcade.color.GOLD
        self.value_color = arcade.color.CYAN

        # Для двух режимов
        self.is_overlay = False
        self.parent_state = None

    def on_enter(self, **kwargs):
        """Вход в настройки с учётом режима"""
        # Определяем режим работы
        self.is_overlay = kwargs.get("is_overlay", False)
        self.parent_state = kwargs.get("parent_state", None)

        # Устанавливаем профиль ввода
        if self.gsm.input_manager:
            self.gsm.input_manager.set_current_profile("settings")

        # Если передали индекс для возврата
        if 'return_to_index' in kwargs:
            self.selected_index = kwargs['return_to_index']

    def on_exit(self):
        """Выход из настроек"""

    def update(self, delta_time):  # ⬅️ И ЭТОГО!
        """Обновление анимации настроек"""
        # Мигание курсора
        self.cursor_blink_timer += delta_time
        if self.cursor_blink_timer >= 0.5:
            self.cursor_blink_timer = 0
            self.cursor_visible = not self.cursor_visible

    def draw(self):
        """Отрисовка с учётом режима"""
        if self.is_overlay:
            # Режим OVERLAY: затемняем фон + окно настроек
            self._draw_as_overlay()
        else:
            # Режим САМОСТОЯТЕЛЬНОГО состояния: полный экран
            self._draw_as_fullscreen()

    def _draw_as_overlay(self):
        """Отрисовка настроек как overlay (окно поверх)"""
        # 1. Полупрозрачный фон
        arcade.draw_rect_filled(arcade.rect.LRBT(
            0,
            self.gsm.window.width,
            0,
            self.gsm.window.height),
            (0, 0, 0, 180)
        )

        # 2. Окно настроек
        window_x = self.gsm.window.width // 2
        window_y = self.gsm.window.height // 2
        window_width = 500
        window_height = 450

        # Фон окна
        arcade.draw_rect_filled(
            arcade.rect.XYWH(
                window_x, window_y,
                window_width, window_height),
            (40, 40, 50)
        )

        # Заголовок
        arcade.Text(
            "⚙ НАСТРОЙКИ",
            window_x, window_y + 180,
            arcade.color.CYAN,
            32,
            align="center",
            anchor_x="center",
            anchor_y="center",
            bold=True
        )

        # Рисуем пункты меню
        self._draw_menu_in_window(window_x, window_y)

        # Подсказки
        arcade.Text(
            "← → — Изменить  |  ESC — Назад",
            window_x, window_y - 190,
            arcade.color.LIGHT_GRAY,
            16,
            align="center",
            anchor_x="center",
            anchor_y="center"
        )

    def _draw_as_fullscreen(self):
        """Отрисовка настроек как отдельного состояния (полный экран)"""
        arcade.draw_texture_rect(
            self.rm.load_texture("backgrounds/lobby_background.png")
            , arcade.rect.XYWH(
                self.gsm.window.width // 2,
                self.gsm.window.height // 2,
                self.gsm.window.width,
                self.gsm.window.height,
            ))

        arcade.draw_rect_filled(arcade.rect.XYWH(
            x=self.gsm.window.width // 2,
            y=self.gsm.window.height // 2,
            width=self.gsm.window.width,
            height=self.gsm.window.height),
            color=(0, 0, 0, 200))

        # Заголовок
        arcade.Text(
            "НАСТРОЙКИ",
            self.gsm.window.width // 2,
            self.gsm.window.height * 0.75,
            arcade.color.CYAN,
            64,
            align="center",
            anchor_x="center",
            anchor_y="center",
            bold=True
        ).draw()

        # Рисуем меню (полноэкранная версия)
        start_x = self.gsm.window.width // 2
        start_y = self.gsm.window.height * 0.5
        spacing = 70

        for i, item in enumerate(self.menu_items):
            # Выбираем цвет
            if i == self.selected_index:
                color = self.selected_color
                font_size = 42
                is_bold = True
            else:
                color = self.normal_color
                font_size = 36
                is_bold = False

            # Текст пункта
            if "value" in item:
                # Пункт со значением
                arcade.Text(
                    item["text"] + ": ",
                    start_x - 100,
                    start_y - i * spacing,
                    color,
                    font_size,
                    anchor_x="right",
                    anchor_y="center",
                    bold=is_bold
                ).draw()

                value_color = self.value_color if i == self.selected_index else arcade.color.LIGHT_BLUE
                arcade.Text(
                    f"{item['value']}%",
                    start_x - 80,
                    start_y - i * spacing,
                    value_color,
                    font_size,
                    anchor_x="left",
                    anchor_y="center",
                    bold=is_bold
                ).draw()
            else:
                # Обычный пункт
                arcade.Text(
                    item["text"],
                    start_x,
                    start_y - i * spacing,
                    color,
                    font_size,
                    align="center",
                    anchor_x="center",
                    anchor_y="center",
                    bold=is_bold
                ).draw()

            # Курсор
            if i == self.selected_index and self.cursor_visible:
                arcade.draw_polygon_filled([
                    (start_x - 250, start_y - i * spacing),
                    (start_x - 230, start_y - i * spacing + 15),
                    (start_x - 230, start_y - i * spacing - 15)
                ], self.selected_color)

                arcade.draw_polygon_filled([
                    (start_x + 250, start_y - i * spacing),
                    (start_x + 230, start_y - i * spacing + 15),
                    (start_x + 230, start_y - i * spacing - 15)
                ], self.selected_color)

        # Подсказки
        hints = [
            "↑ ↓ — Выбор",
            "← → — Изменить значение",
            "ENTER — Подтвердить",
            "ESC — Назад без сохранения"
        ]

        hint_y = 80
        for i, hint in enumerate(hints):
            arcade.Text(
                hint,
                self.gsm.window.width // 2,
                hint_y + i * 25,
                arcade.color.LIGHT_GRAY,
                18,
                align="center",
                anchor_x="center",
                anchor_y="center"
            ).draw()

    def _draw_menu_in_window(self, center_x, center_y):
        """Рисует меню в рамках окна overlay"""
        start_y = center_y + 100
        spacing = 60

        for i, item in enumerate(self.menu_items):
            # Выбираем цвет
            if i == self.selected_index:
                color = self.selected_color
                font_size = 24
                is_bold = True
            else:
                color = self.normal_color
                font_size = 20
                is_bold = False

            # Текст пункта
            if "value" in item:
                value_color = self.value_color if i == self.selected_index else arcade.color.LIGHT_BLUE

                arcade.Text(
                    item["text"] + ": ",
                    center_x - 80,
                    start_y - i * spacing,
                    color,
                    font_size,
                    anchor_x="right",
                    anchor_y="center",
                    bold=is_bold
                ).draw()

                arcade.Text(
                    f"{item['value']}%",
                    center_x - 60,
                    start_y - i * spacing,
                    value_color,
                    font_size,
                    anchor_x="left",
                    anchor_y="center",
                    bold=is_bold
                ).draw()
            else:
                arcade.Text(
                    item["text"],
                    center_x,
                    start_y - i * spacing,
                    color,
                    font_size,
                    align="center",
                    anchor_x="center",
                    anchor_y="center",
                    bold=is_bold
                ).draw()

            # Курсор
            if i == self.selected_index and self.cursor_visible:
                arcade.draw_polygon_filled([
                    (center_x - 180, start_y - i * spacing),
                    (center_x - 160, start_y - i * spacing + 8),
                    (center_x - 160, start_y - i * spacing - 8)
                ], self.selected_color)

                arcade.draw_polygon_filled([
                    (center_x + 180, start_y - i * spacing),
                    (center_x + 160, start_y - i * spacing + 8),
                    (center_x + 160, start_y - i * spacing - 8)
                ], self.selected_color)

    def handle_key_press(self, key, modifiers):
        """Обработка клавиш в настройках"""
        if not self.gsm.input_manager:
            return

        current_time = time.time()
        if current_time - self.last_key_time < self.key_cooldown:
            return

        # Навигация
        if self.gsm.input_manager.is_action_pressed("menu_up"):
            self.selected_index = max(0, self.selected_index - 1)
            self.last_key_time = current_time

        elif self.gsm.input_manager.is_action_pressed("menu_down"):
            self.selected_index = min(len(self.menu_items) - 1, self.selected_index + 1)
            self.last_key_time = current_time

        # Изменение значений
        elif self.gsm.input_manager.is_action_pressed("move_left"):
            self._change_value(-10)
            self.last_key_time = current_time

        elif self.gsm.input_manager.is_action_pressed("move_right"):
            self._change_value(+10)
            self.last_key_time = current_time

        # Выбор
        elif self.gsm.input_manager.is_action_pressed("select"):
            self._select_menu_item()
            self.last_key_time = current_time

        # Назад
        elif self.gsm.input_manager.is_action_pressed("back"):
            self._go_back()
            self.last_key_time = current_time

    def _change_value(self, delta):
        """Изменяет значение выбранной настройки"""
        if self.selected_index < len(self.menu_items):
            item = self.menu_items[self.selected_index]

            if "value" in item:
                # Ограничиваем значение 0-100
                new_value = max(0, min(100, item["value"] + delta))
                item["value"] = new_value
                print(f"Громкость изменена: {new_value}%")

    def _select_menu_item(self):
        """Обрабатывает выбор пункта"""
        selected = self.menu_items[self.selected_index]
        print(f"Выбрано: {selected['text']}")

        if selected["action"] == "volume":
            # Уже обрабатывается стрелками
            pass
        elif selected["action"] == "controls":
            print("Открываем настройки управления...")
        elif selected["action"] == "graphics":
            print("Открываем настройки графики...")
        elif selected["action"] == "back":
            self._go_back()

    def _go_back(self):
        """Возврат с учётом режима"""
        if self.is_overlay:
            self.gsm.pop_overlay()
        else:
            # Самостоятельный режим: возвращаемся в лобби
            print("🔙 Возвращаемся в лобби...")
            self.gsm.switch_to("lobby", selected_index=2)

    def handle_key_release(self, key, modifiers):
        """Обработка отпускания клавиш"""
        pass

    def on_pause(self):
        """Пауза (для overlay режима)"""
        pass

    def on_resume(self):
        """Возобновление (для overlay режима)"""
        pass