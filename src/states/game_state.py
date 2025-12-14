import logging
import arcade
from .base_state import BaseState


class GameplayState(BaseState):
    """
    Состояние основной игры.
    Здесь происходит вся игровая логика.
    """

    def __init__(self, gsm, asset_loader):
        super().__init__("game", gsm, asset_loader)

        self.input_manager = None
        self.player = None
        self.game_map = None
        self.camera = None
        self.ui_elements = arcade.SpriteList()

        # ИНИЦИАЛИЗИРУЕМ флаги в конструкторе
        self.is_paused = False
        self.is_initialized = False

    def on_enter(self, **kwargs):
        """Вызывается при входе в это состояние"""
        # СБРАСЫВАЕМ все флаги при каждом входе!
        self.is_paused = False
        self.is_initialized = True

        # Получаем InputManager из GameStateManager
        self.input_manager = self.gsm.input_manager

        # Устанавливаем профиль клавиш для игры
        if self.input_manager:
            self.input_manager.set_current_profile("game")

        # Пока без игрока и карты - просто тестируем переход
        print("Игра загружена (пока без контента)")

        # Инициализируем UI
        self._init_ui()

    def on_exit(self):
        """Вызывается при выходе из состояния"""
        print("🚪 ВЫХОДИМ ИЗ ИГРЫ")
        # Сбрасываем флаги
        self.is_paused = False
        self.is_initialized = False

        # Сохраняем прогресс, освобождаем ресурсы...

    def on_pause(self):
        """Вызывается при постановке игры на паузу (для overlay)"""
        print("⏸️ ИГРА НА ПАУЗЕ")
        self.is_paused = True

    def on_resume(self):
        """Вызывается при возобновлении игры"""
        print("▶️ ИГРА ВОЗОБНОВЛЕНА")
        self.is_paused = False

    def update(self, delta_time: float):
        """Обновление игровой логики"""
        if self.is_paused:
            return  # Не обновляем, если игра на паузе

        # 1. Обрабатываем ввод игрока
        self._handle_input()

        # Пока нет игрока и карты - просто ждем

    def draw(self):
        """Отрисовка игры"""
        # Очищаем экран
        # arcade.start_render()

        # Фон (просто черный для теста)
        arcade.set_background_color(arcade.color.BLACK)

        # Сообщение для теста
        arcade.Text(
            "ИГРА АКТИВНА",
            self.gsm.window.width // 2,
            self.gsm.window.height // 2,
            arcade.color.GREEN,
            48,
            anchor_x="center",
            anchor_y="center",
            bold=True
        ).draw()

        # Если пауза - показываем сообщение
        if self.is_paused:
            arcade.Text(
                "ПАУЗА (нажмите ESC для меню)",
                self.gsm.window.width // 2,
                self.gsm.window.height // 2 - 100,
                arcade.color.YELLOW,
                24,
                anchor_x="center",
                anchor_y="center"
            ).draw()

    def _handle_input(self):
        """Обработка ввода для игрового состояния"""
        if not self.input_manager:
            return

        if self.input_manager.current_profile != "game":
            print(f"⚠️ Внимание! Текущий профиль: {self.input_manager.current_profile}, должен быть 'game'")
            return


        # ESC - открыть меню паузы
        if self.input_manager.is_action_pressed("pause"):
            print("🔼 Нажата пауза")
            self._open_pause_menu()

        # Для теста - выводим нажатые клавиши движения
        if self.input_manager.is_action_pressed("move_up"):
            print("↑ Движение вверх")
        if self.input_manager.is_action_pressed("move_down"):
            print("↓ Движение вниз")
        if self.input_manager.is_action_pressed("move_left"):
            print("← Движение влево")
        if self.input_manager.is_action_pressed("move_right"):
            print("→ Движение вправо")

    def _init_ui(self):
        """Инициализирует UI элементы"""
        # Пока пусто - добавим позже
        pass

    def _open_pause_menu(self):
        """Открывает меню паузы поверх игры"""
        print("📋 Открываем меню паузы...")
        self.gsm.push_overlay("pause_menu")

    # УБИРАЕМ дублированные методы отсюда!