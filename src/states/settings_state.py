import arcade
import time

from .base_state import BaseState
from config import constants as C

class SettingsState(BaseState):
    """
    Состояние настроек.
    Вызывается как из лобби, так и из игрового меню
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
        self.key_cooldown = 0.15
        self.last_key_time = 0

        # Цвета
        self.text_color = C.TEXT_COLOR
        self.selected_color = C.UI_MAIN_COLOR
        self.title_color = C.UI_TITLE_COLOR
        self.menu_background_color = C.MENU_BACKGROUND_COLOR
        self.bg_color = C.FOGGING_COLOR

        # Для двух режимов
        self.is_overlay = False
        self.parent_state = None

    def on_enter(self, **kwargs):
        """Вход в настройки с учётом режима"""
        # Определяем режим работы
        self.is_overlay = kwargs.get("is_overlay", False)
        self.parent_state = kwargs.get("parent_state", None)

        # Если передали индекс для возврата
        if 'return_to_index' in kwargs:
            self.selected_index = kwargs['return_to_index']

    def on_exit(self):
        """Выход из настроек"""

    def update(self, delta_time):
        pass

    def draw(self):
        """Отрисовка с учётом режима"""
        if self.is_overlay:
            # Режим OVERLAY: затемняем фон + окно настроек
            self._draw_as_overlay()
        else:
            # Режим САМОСТОЯТЕЛЬНОГО состояния: полный экран
            self._draw_as_fullscreen()

    def _draw_as_overlay(self):
        """Отрисовка настроек как overlay"""

        # Окно настроек
        window_x = self.gsm.window.width // 2
        window_y = self.gsm.window.height // 2
        window_width = 500
        window_height = 450

        # Фон окна
        arcade.draw_rect_filled(
            arcade.rect.XYWH(
                window_x, window_y,
                window_width, window_height),
            self.menu_background_color
        )

        arcade.draw_rect_outline(
            arcade.rect.XYWH(
                window_x, window_y,
                window_width, window_height),
            self.selected_color, 3
        )

        # Заголовок
        arcade.Text(
            "НАСТРОЙКИ",
            window_x, window_y*1.4,
            self.title_color,
            32,
            align="center",
            anchor_x="center",
            anchor_y="center",
            bold=True
        ).draw()

        # Отрисовка пунктов меню
        self._draw_menu_list(window_x, window_y*0.9, 22)


    def _draw_as_fullscreen(self):
        """Отрисовка настроек как отдельного состояния"""
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

        # Рисуем меню
        start_x = self.gsm.window.width // 2
        start_y = self.gsm.window.height * 0.4

        self._draw_menu_list(start_x, start_y, 36)


    def _draw_menu_list(self, center_x, center_y, font: int):
        """Рисует меню в рамках окна overlay"""
        start_y = center_y + 100
        spacing = 60

        for i, item in enumerate(self.menu_items):
            # Выбираем цвет
            if i == self.selected_index:
                color = self.selected_color
                font_size = font * 1.11
                is_bold = True
            else:
                color = self.text_color
                font_size = font
                is_bold = False

            text = item["text"]

            # Текст пункта
            if "value" in item:
                text = f"{item['text']}: {item['value']}%"

            arcade.Text(
                text,
                center_x,
                start_y - i * spacing,
                color,
                font_size,
                align="center",
                anchor_x="center",
                anchor_y="center",
                bold=is_bold
            ).draw()

    def handle_key_press(self, key, modifiers):
        """Обработка клавиш в настройках"""
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

        # Изменение значений
        elif self.gsm.input_manager.get_action("left"):
            self._change_value(-10)
            self.last_key_time = current_time

        elif self.gsm.input_manager.get_action("right"):
            self._change_value(+10)
            self.last_key_time = current_time

        # Выбор
        elif self.gsm.input_manager.get_action("select"):
            self._select_menu_item()
            self.last_key_time = current_time

        # Назад
        elif self.gsm.input_manager.get_action("escape"):
            self._go_back()
            self.last_key_time = current_time

    def _change_value(self, delta):
        """Изменяет значение выбранной настройки"""
        print(self.selected_index, len(self.menu_items))
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
