import logging

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
        print(f"ВХОДИМ В ИГРУ: {self.state_id}")

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
        print("ВЫХОДИМ ИЗ ИГРЫ")
        # Сохраняем прогресс, освобождаем ресурсы...

    # ⬇️⬇️⬇️ ДОБАВЛЯЕМ ЭТИ МЕТОДЫ ⬇️⬇️⬇️
    def on_pause(self):
        """Вызывается при постановке игры на паузу (для overlay)"""
        print("ИГРА НА ПАУЗЕ")
        self.is_paused = True

    def on_resume(self):
        """Вызывается при возобновлении игры"""
        print("ИГРА ВОЗОБНОВЛЕНА")
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
        # # Фон
        # arcade.start_render()

        # ... фон игры ...

        # РИСУЕМ ИГРОКА (если он есть)
        if self.player:
            self.player.draw()

        # ... UI и другие элементы ...


    def _handle_input(self):
        """Обработка ввода для игрового состояния"""
        if not self.input_manager:
            return

        # ESC - вернуться в лобби
        if self.input_manager.is_action_pressed("pause"):
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
        self.is_paused = True
        self.gsm.push_overlay("pause_menu")

    def on_pause(self):
        """Игра поставлена на паузу (вызвал overlay)"""
        logging.info("ИГРА НА ПАУЗЕ (из GameplayState)")
        self.is_paused = True

    def on_resume(self):
        """Игра возобновлена (закрыли overlay)"""
        print("▶️ ИГРА ВОЗОБНОВЛЕНА (из GameplayState)")
        self.is_paused = False