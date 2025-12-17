# src/frame/main_window.py
import logging
import arcade
from src.core.game_state_manager import GameStateManager
from src.core.input_manager import InputManager
from src.core.resource_manager import resource_manager
from src.core.asset_loader import AssetLoader
from src.states.lobby_state import LobbyState
from src.states.game_state import GameplayState
from src.states.pause_menu_state import PauseMenuState
from src.states.settings_state import SettingsState


# from src.states.inventory_state import InventoryState


class MainWindow(arcade.Window):
    """
    Главное окно игры. Теперь только обертка.
    Вся логика делегируется GameStateManager.
    """

    def __init__(self):
        # Константы из вашего GamePanel
        SCREEN_WIDTH = 1280
        SCREEN_HEIGHT = 768
        SCREEN_TITLE = "IT-Кубия"

        super().__init__(
            width=SCREEN_WIDTH,
            height=SCREEN_HEIGHT,
            title=SCREEN_TITLE,
            fullscreen=False,
            update_rate=1 / 60
        )

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"Создано окно: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")

        # Устанавливаем цвет фона
        arcade.set_background_color(arcade.color.ASH_GREY)

        # СОЗДАЕМ МЕНЕДЖЕРЫ
        self.resource_manager = resource_manager
        self.asset_loader = AssetLoader(self.resource_manager)
        self.input_manager = InputManager()

        # СОЗДАЕМ ЦЕНТРАЛЬНЫЙ МЕНЕДЖЕР СОСТОЯНИЙ
        self.gsm = GameStateManager(self)
        self.gsm.input_manager = self.input_manager
        self.gsm.asset_loader = self.asset_loader

        # РЕГИСТРИРУЕМ ВСЕ СОСТОЯНИЯ
        self._register_states()

        # НАЧИНАЕМ С ЛОББИ
        self.gsm.switch_to("lobby")

        self.logger.info("MainWindow инициализирован")

    def _register_states(self):
        """Регистрирует все состояния игры"""
        lobby_state = LobbyState(self.gsm, self.asset_loader)
        game_state = GameplayState(self.gsm, self.asset_loader)
        pause_state = PauseMenuState(self.gsm, self.asset_loader)
        settings_state = SettingsState(self.gsm, self.asset_loader)

        # Регистрация состояний
        self.gsm.register_state("lobby", lobby_state)
        self.gsm.register_state("game", game_state)
        self.gsm.register_state("pause_menu", pause_state)
        self.gsm.register_state("settings", settings_state)

        self.logger.info(f"Зарегистрировано состояний: {len(self.gsm.states)}")

    def on_draw(self):
        """Отрисовка - делегируем GameStateManager"""
        self.clear()
        self.gsm.draw()

    def on_update(self, delta_time: float):
        """Обновление - делегируем GameStateManager"""
        self.gsm.update(delta_time)

    def on_key_press(self, key: int, modifiers: int):
        """Нажатие клавиши"""
        # 1. F11 обрабатываем СРАЗУ и ВЫХОДИМ
        if key == arcade.key.F11:
            self.set_fullscreen(not self.fullscreen)
            return  # ВАЖНО: не передаем дальше!

        # 2. Остальные клавиши - в InputManager и GSM
        self.input_manager.on_key_press(key, modifiers)
        self.gsm.handle_key_press(key, modifiers)

    def on_key_release(self, key: int, modifiers: int):
        """Отпускание клавиши"""
        # F11 игнорируем (мы уже обработали)
        if key == arcade.key.F11:
            return

        self.input_manager.on_key_release(key, modifiers)
        self.gsm.handle_key_release(key, modifiers)

    def on_resize(self, width: int, height: int):
        """Вызывается при изменении размера окна (включая переключение полноэкранного режима)"""
        super().on_resize(width, height)

        # Передаем информацию о новом размере в GSM
        if hasattr(self.gsm, 'current_state') and self.gsm.current_state:
            # Вызываем on_resize у активного состояния (если оно есть такой метод)
            if hasattr(self.gsm.current_state, 'on_resize'):
                self.gsm.current_state.on_resize(width, height)

    def on_close(self):
        """Закрытие окна"""
        super().on_close()