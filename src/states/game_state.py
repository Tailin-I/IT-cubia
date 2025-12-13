# src/states/gameplay_state.py
import arcade
from .base_state import BaseState
from src.core.input_manager import InputManager
from ..entities import Player


class GameplayState(BaseState):
    """
    Состояние основной игры.
    Здесь происходит вся игровая логика.
    """

    def __init__(self, gsm, asset_loader):
        super().__init__("game", gsm)

        self.asset_loader = asset_loader
        self.input_manager = None  # Будет установлен позже

        # Игровые объекты
        self.player = None
        self.game_map = None
        self.camera = None

        # UI элементы
        self.ui_elements = arcade.SpriteList()

        # Флаги
        self.is_paused = False

    def on_enter(self, **kwargs):
        """Вызывается при входе в это состояние"""
        print(f"Входим в состояние игры: {self.state_id}")

        # Получаем InputManager из GameStateManager
        self.input_manager = self.gsm.input_manager

        # Устанавливаем профиль клавиш для игры
        self.input_manager.set_profile("game")

        # Загружаем ресурсы
        player_assets = self.asset_loader.load_player_sprites()

        # Создаем игрока
        self.player = Player(
            textures=player_assets,
            scale=4
        )

        # Загружаем карту
        # self.game_map = self.asset_loader.load_map("dungeon_1")

        # Создаем камеру
        # self.camera = SmartCamera(...)

        # Инициализируем UI
        self._init_ui()

    def on_exit(self):
        """Вызывается при выходе из состояния"""
        print("Выходим из состояния игры")
        # Сохраняем прогресс, освобождаем ресурсы...

    def update(self, delta_time: float):
        """Обновление игровой логики"""
        if self.is_paused:
            return  # Не обновляем, если игра на паузе

        # 1. Обрабатываем ввод игрока
        self._handle_input()

        # 2. Обновляем игрока
        if self.player:
            self.player.update(delta_time)

        # 3. Обновляем камеру (следим за игроком)
        if self.camera and self.player:
            self.camera.update(self.player.center_x, self.player.center_y)

        # 4. Проверяем коллизии, триггеры и т.д.
        # self._check_collisions()

    def draw(self):
        """Отрисовка игры"""
        # 1. Активируем камеру (если есть)
        if self.camera:
            self.camera.use()

        # 2. Рисуем карту
        if self.game_map:
            self.game_map.draw()

        # 3. Рисуем игрока
        if self.player:
            self.player.draw()

        # 4. Рисуем UI поверх всего
        self.ui_elements.draw()

    def _handle_input(self):
        """Обработка ввода для игрового состояния"""
        if not self.input_manager:
            return

        # Движение
        if self.input_manager.is_action_pressed("move_up"):
            # Логика движения вверх
            pass
        if self.input_manager.is_action_pressed("move_down"):
            # Логика движения вниз
            pass
        if self.input_manager.is_action_pressed("move_left"):
            # Логика движения влево
            pass
        if self.input_manager.is_action_pressed("move_right"):
            # Логика движения вправо
            pass

        # Открытие инвентаря
        if self.input_manager.is_action_pressed("inventory"):
            self._open_inventory()

        # Взаимодействие
        if self.input_manager.is_action_pressed("interact"):
            self._interact()

        # Пауза
        if self.input_manager.is_action_pressed("pause"):
            self._toggle_pause()

    def _open_inventory(self):
        """Открывает инвентарь поверх игры"""
        # Сохраняем, что мы в игре
        self.is_paused = True

        # Просим GameStateManager открыть overlay
        self.gsm.push_overlay("inventory")

    def _interact(self):
        """Взаимодействие с объектами"""
        print("Игрок взаимодействует!")
        # Проверяем, с чем можно взаимодействовать...

    def _toggle_pause(self):
        """Включает/выключает паузу"""
        self.is_paused = not self.is_paused
        if self.is_paused:
            print("Игра на паузе")
        else:
            print("Игра продолжается")

    def _init_ui(self):
        """Инициализирует UI элементы"""
        # Здесь будет создание полоски здоровья, маны и т.д.
        pass

    def resume(self):
        """Возобновление после закрытия overlay"""
        self.is_paused = False
        print("Игра возобновлена")