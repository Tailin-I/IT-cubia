# src/states/gameplay_state.py
import arcade
from .base_state import BaseState


class GameplayState(BaseState):
    """
    Состояние основной игры.
    Здесь происходит вся игровая логика.
    """

    def __init__(self, gsm, asset_loader):
        super().__init__("game", gsm, asset_loader)  # ⬅️ Добавляем asset_loader!

        self.input_manager = None
        self.player = None
        self.game_map = None
        self.camera = None
        self.ui_elements = arcade.SpriteList()
        self.is_paused = False

    def on_enter(self, **kwargs):
        """Вызывается при входе в это состояние"""
        print(f"🎮 ВХОДИМ В ИГРУ: {self.state_id}")

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
        # Сохраняем прогресс, освобождаем ресурсы...

    # ⬇️⬇️⬇️ ДОБАВЛЯЕМ ЭТИ МЕТОДЫ ⬇️⬇️⬇️
    def on_pause(self):
        """Вызывается при постановке игры на паузу (для overlay)"""
        print("⏸️ ИГРА НА ПАУЗЕ")
        self.is_paused = True

    def on_resume(self):
        """Вызывается при возобновлении игры"""
        print("▶️ ИГРА ВОЗОБНОВЛЕНА")
        self.is_paused = False

    # ⬆️⬆️⬆️ ВОТ ЭТИ МЕТОДЫ ⬆️⬆️⬆️

    def update(self, delta_time: float):
        """Обновление игровой логики"""
        if self.is_paused:
            return  # Не обновляем, если игра на паузе

        # 1. Обрабатываем ввод игрока
        self._handle_input()

        # Пока нет игрока и карты - просто ждем

    def draw(self):
        """Отрисовка игры"""
        # Красивый фон игры
        arcade.draw_texture_rect(
            arcade.load_texture(":resources:images/backgrounds/abstract_2.jpg"),
            arcade.rect.XYWH(
                x=self.gsm.window.width // 2,
                y=self.gsm.window.height // 2,
                width=self.gsm.window.width,
                height=self.gsm.window.height)
        )

        # Затемняющая панель
        arcade.draw_rect_filled(arcade.rect.XYWH(
            x=self.gsm.window.width,
            y=self.gsm.window.height,
            width=600,
            height=400),
            color=(0, 0, 0, 200)
        )

        # Текст для теста
        title = arcade.Text(
            "🎮 ITCUBIA - ИГРА 🎮",
            self.gsm.window.width // 2,
            self.gsm.window.height // 2 + 50,
            arcade.color.GOLD,
            font_size=36,
            anchor_x="center",
            anchor_y="center",
            bold=True
        )
        title.draw()

        instruction = arcade.Text(
            "Пока здесь пусто, но скоро будет эпическая игра!\n\n" +
            "Управление:\n" +
            "WASD/Стрелки - Движение\n" +
            "E - Взаимодействие\n" +
            "I - Инвентарь\n" +
            "ESC - Вернуться в лобби\n" +
            "F11 - Полный экран",
            self.gsm.window.width // 2,
            self.gsm.window.height // 2 - 50,
            arcade.color.LIGHT_GRAY,
            font_size=20,
            anchor_x="center",
            anchor_y="center",
            align="center",
            multiline=True,
            width=500
        )
        instruction.draw()

    def _handle_input(self):
        """Обработка ввода для игрового состояния"""
        if not self.input_manager:
            return

        # ESC - вернуться в лобби
        if self.input_manager.is_action_pressed("pause"):
            print("🔙 Возвращаемся в лобби...")
            self.gsm.switch_to("lobby", selected_index=0)

        # Полноэкранный режим (работает всегда)
        if self.input_manager.is_action_pressed("fullscreen"):
            self.gsm.window.set_fullscreen(not self.gsm.window.fullscreen)

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