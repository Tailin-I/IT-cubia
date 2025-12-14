import arcade
import time
from .base_state import BaseState


class LobbyState(BaseState):
    """
    Лобби полностью на клавиатуре.
    Управление: ↑↓ - выбор, ENTER - подтвердить, ESC - выход.
    """

    def __init__(self, gsm, asset_loader):
        super().__init__("lobby", gsm, asset_loader)

        # Пункты меню
        self.menu_items = [
            {"text": "НОВАЯ ИГРА", "action": "new_game"},
            {"text": "ЗАГРУЗИТЬ", "action": "load_game"},
            {"text": "НАСТРОЙКИ", "action": "settings"},
            {"text": "ВЫХОД", "action": "exit"}
        ]

        # Выбранный пункт
        self.selected_index = 0

        # Для плавного мигания курсора
        self.cursor_blink_timer = 0
        self.cursor_visible = True

        # Для предотвращения быстрых повторных нажатий
        self.key_cooldown = 0.15  # секунд
        self.last_key_time = 0

        # Цвета
        self.normal_color = arcade.color.LIGHT_GRAY
        self.selected_color = arcade.color.GOLD
        self.disabled_color = arcade.color.DARK_GRAY
        self.title_color = arcade.color.CYAN

        # Звуки (если будут)
        self.has_sounds = False

    def on_enter(self, **kwargs):
        """Вход в лобби"""
        print("ВХОД В ЛОББИ")

        # Устанавливаем профиль ввода
        if self.gsm.input_manager:
            self.gsm.input_manager.set_current_profile("lobby")

        # Сбрасываем таймеры
        self.cursor_blink_timer = 0
        self.last_key_time = time.time()

        # Если передали selected_index (например, возврат из настроек)
        if 'selected_index' in kwargs:
            self.selected_index = kwargs['selected_index']

    def on_exit(self):
        """Выход из лобби"""
        print("ВЫХОД ИЗ ЛОББИ")

    def on_pause(self):
        """Пауза (не используется в лобби)"""
        pass

    def on_resume(self):
        """Возобновление (не используется в лобби)"""
        pass

    def update(self, delta_time: float):
        """Обновление анимации"""
        # Мигание курсора
        self.cursor_blink_timer += delta_time
        if self.cursor_blink_timer >= 0.5:  # Мигаем каждые 0.5 секунд
            self.cursor_blink_timer = 0
            self.cursor_visible = not self.cursor_visible

        # Можно добавить анимацию фона
        # self.background.update(delta_time)

    def draw(self):
        """Отрисовка лобби"""
        # Очищаем экран красивым градиентом
        arcade.draw_texture_rect(
            self.rm.load_texture("backgrounds/lobby_background.png")
            , arcade.rect.XYWH(
            self.gsm.window.width // 2,
            self.gsm.window.height // 2,
            self.gsm.window.width,
            self.gsm.window.height,
        ))

        arcade.draw_rect_filled(arcade.rect.XYWH(
            x=self.gsm.window.width//2,
            y=self.gsm.window.height//2,
            width=self.gsm.window.width,
            height=self.gsm.window.height),
            color=(0, 0, 0, 200))

        # Заголовок игры (с тенью)
        title_x = self.gsm.window.width // 2
        title_y = self.gsm.window.height * 0.75

        # Тень
        arcade.Text(
            "IT-Кубия",
            title_x + 5, title_y - 5,
            arcade.color.BLACK,
            font_size=72,
            anchor_x="center",
            anchor_y="center",
            bold=True
        ).draw()

        # Основной текст
        arcade.Text(
            "IT-Кубия",
            title_x, title_y,
            self.title_color,
            font_size=72,
            anchor_x="center",
            anchor_y="center",
            bold=True
        ).draw()

        # Подзаголовок
        arcade.Text(
            "Pixel Adventure",
            title_x, title_y - 80,
            arcade.color.LIGHT_BLUE,
            font_size=24,
            anchor_x="center",
            anchor_y="center"
        ).draw()

        # Рисуем меню
        self._draw_menu()

        # Подсказки управления
        self._draw_hints()

    def _draw_menu(self):
        """Рисует пункты меню"""
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

            # Рисуем текст пункта
            text = arcade.Text(
                item["text"],
                start_x,
                start_y - i * spacing,
                color,
                font_size=font_size,
                anchor_x="center",
                anchor_y="center",
                bold=is_bold
            )
            text.draw()

            # Рисуем курсор для выбранного пункта
            if i == self.selected_index and self.cursor_visible:
                # Левый треугольник
                arcade.draw_triangle_filled(
                    start_x - 200, start_y - i * spacing,
                    start_x - 180, start_y - i * spacing + 15,
                    start_x - 180, start_y - i * spacing - 15,
                    self.selected_color
                )
                # Правый треугольник
                arcade.draw_triangle_filled(
                    start_x + 200, start_y - i * spacing,
                    start_x + 180, start_y - i * spacing + 15,
                    start_x + 180, start_y - i * spacing - 15,
                    self.selected_color
                )

    def _draw_hints(self):
        """Рисует подсказки управления"""
        hints = [
            "↑ ↓ — Выбор пункта",
            "ENTER — Подтвердить",
            "ESC — Выход из игры",
            "F11 — Полный экран"
        ]

        hint_y = 80
        hint_spacing = 25

        for i, hint in enumerate(hints):
            arcade.Text(
                hint,
                self.gsm.window.width // 8,
                hint_y + i * hint_spacing,
                arcade.color.LIGHT_GRAY,
                font_size=18,
                anchor_x="center",
                anchor_y="center"
            ).draw()

    def handle_key_press(self, key: int, modifiers: int):
        """Обработка нажатия клавиш"""
        if not self.gsm.input_manager:
            return

        # Проверяем кд (чтобы не было слишком быстрых нажатий)
        current_time = time.time()
        if current_time - self.last_key_time < self.key_cooldown:
            return

        # Навигация ВВЕРХ
        if self.gsm.input_manager.is_action_pressed("menu_up"):
            self.selected_index = max(0, self.selected_index - 1)
            self._play_menu_sound("select")
            self.last_key_time = current_time

        # Навигация ВНИЗ
        elif self.gsm.input_manager.is_action_pressed("menu_down"):
            self.selected_index = min(len(self.menu_items) - 1, self.selected_index + 1)
            self._play_menu_sound("select")
            self.last_key_time = current_time

        # Выбор пункта (ENTER/E)
        elif self.gsm.input_manager.is_action_pressed("select"):
            self._select_menu_item()
            self.last_key_time = current_time

        # Выход (ESC)
        elif self.gsm.input_manager.is_action_pressed("back"):
            self._confirm_exit()
            self.last_key_time = current_time

    def _select_menu_item(self):
        """Обрабатывает выбор пункта меню"""
        selected = self.menu_items[self.selected_index]
        self._play_menu_sound("confirm")

        if selected["action"] == "new_game":
            print("🚀 Начинаем новую игру...")
            self.gsm.switch_to("game")
            # Пока просто переходим в игру
            # self.gsm.switch_to("game")

        elif selected["action"] == "settings":
            print("⚙ Открываем настройки...")
            self.gsm.switch_to("settings")

        elif selected["action"] == "exit":
            self._confirm_exit()

    def _confirm_exit(self):
        """Подтверждение выхода"""
        print("🚪 Выход из игры")
        # Можно добавить диалог подтверждения
        # Пока просто закрываем
        self.gsm.window.close()

    def _play_menu_sound(self, sound_type: str):
        """Воспроизведение звуков меню"""
        if not self.has_sounds:
            return

        sounds = {
            "select": "menu_select.wav",
            "confirm": "menu_confirm.wav",
            "back": "menu_back.wav"
        }

        if sound_type in sounds:
            # self.asset_loader.play_sound(sounds[sound_type])
            pass

    def handle_key_release(self, key: int, modifiers: int):
        """Обработка отпускания клавиш"""
        # В лобби не нужно, но метод должен быть
        pass