import logging
import arcade
from arcade import LRBT

from config import  constants as C
from src.core.game_state_manager import GameStateManager
from src.core.input_manager import InputManager
from src.core.resource_manager import resource_manager
from src.core.asset_loader import AssetLoader
from src.states.base_state import BaseState
from src.states.cheat_console_state import CheatConsoleState
from src.states.lobby_state import LobbyState
from src.states.game_state import GameplayState
from src.states.lock_picking_state import LockPickingState
from src.states.pause_menu_state import PauseMenuState
from src.states.settings_state import SettingsState


class MainWindow(arcade.Window):
    """
    Главное окно игры.
    (Вся логика делегируется GameStateManager)
    """

    def __init__(self):

        # КОНСТАНТЫ
        self.screen_title = C.SCREEN_TITLE

        self.screen_width = C.SCREEN_WIDTH
        self.screen_height = C.SCREEN_HEIGHT

        self.viewport_width = C.VIEWPORT_WIDTH
        self.viewport_height = C.VIEWPORT_HEIGHT

        super().__init__(
            width=self.screen_width,
            height=self.screen_height,
            title=self.screen_title,
            fullscreen=False,
            update_rate=1 / 60
        )

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"Создано окно: {self.screen_width}x{self.screen_height}")

        # Устанавливаем цвет фона
        arcade.set_background_color(arcade.color.ASH_GREY)

        # СОЗДАЕМ МЕНЕДЖЕРЫ
        self.resource_manager = resource_manager
        self.asset_loader = AssetLoader()
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
        cheat_state = CheatConsoleState(self.gsm, self.asset_loader)
        lock_state = LockPickingState(self.gsm, self.asset_loader)

        # Регистрация состояний
        self.gsm.register_state("lobby", lobby_state)
        self.gsm.register_state("game", game_state)
        self.gsm.register_state("pause_menu", pause_state)
        self.gsm.register_state("settings", settings_state)
        self.gsm.register_state("cheat_console", cheat_state)
        self.gsm.register_state("lock_picking", lock_state)


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
            self.toggle_fullscreen()
            return

        # 2. Остальные клавиши - в InputManager и GSM
        self.input_manager.on_key_press(key, modifiers)
        self.gsm.handle_key_press(key, modifiers)

    def on_key_release(self, key: int, modifiers: int):
        """Отпускание клавиши"""
        if key == arcade.key.F11:
            return

        self.input_manager.on_key_release(key, modifiers)
        self.gsm.handle_key_release(key, modifiers)

    def _update_all_cameras(self, width: int, height: int):
        """Обновляет ВСЕ камеры в проекте с фиксированным обзором"""
        # Рассчитываем масштаб для сохранения фиксированного обзора
        scale_x = width / self.viewport_width
        scale_y = height / self.viewport_height
        scale = min(scale_x, scale_y)  # Используем минимальный масштаб для сохранения пропорций

        # Рассчитываем viewport с черными полосами (letterbox/pillarbox)
        viewport_width = int(self.viewport_width * scale)
        viewport_height = int(self.viewport_height * scale)
        viewport_x = (width - viewport_width) // 2
        viewport_y = (height - viewport_height) // 2

        self.logger.info(
            f"Фиксированный обзор: {viewport_width}x{viewport_height}, окно: {width}x{height}, масштаб: {scale:.2f}")

        # Обновляем камеры в активном состоянии
        active_state = self.gsm.get_active_state()
        if active_state:
            self._update_state_cameras(active_state, viewport_x, viewport_y, viewport_width, viewport_height, scale)

        # Обновляем камеры в основном состоянии
        if self.gsm.current_state and self.gsm.current_state != active_state:
            self._update_state_cameras(self.gsm.current_state, viewport_x, viewport_y, viewport_width, viewport_height,
                                       scale)

        # Обновляем камеры во всех overlay
        for overlay in self.gsm.overlay_stack:
            self._update_state_cameras(overlay, viewport_x, viewport_y, viewport_width, viewport_height, scale)

    def _update_state_cameras(self, state: BaseState, x: int, y: int, width: int, height: int, scale: float):
        """Обновляет камеры с фиксированным обзором"""
        if not state:
            return

        # 1. Основная игровая камера
        if hasattr(state, 'camera') and state.camera:
            # Устанавливаем фиксированный viewport в центре экрана
            state.camera.viewport = arcade.rect.XYWH(
                x + width // 2,  # Центрируем по X
                y + height // 2,  # Центрируем по Y
                width,
                height
            )

            # Для фиксированного обзора НЕ меняем projection
            # Projection должен оставаться таким же как при 1280x768
            # Только обновляем viewport

        # 2. UI камера (default_camera) - должна использовать полный экран
        if hasattr(state, 'default_camera') and state.default_camera:
            # UI камера должна использовать полный экран для корректного отображения UI
            state.default_camera.viewport = arcade.rect.XYWH(
                self.screen_width // 2,
                self.screen_height // 2,
                self.screen_width,
                self.screen_height
            )

        # 3. Обновляем UI элементы с учетом масштаба
        if hasattr(state, 'ui_elements'):
            for ui_element in state.ui_elements:
                self._update_ui_element(ui_element, x, y, width, height, scale)

    def _update_ui_element(self, ui_element, x: int, y: int, width: int, height: int, scale: float):
        """Обновляет позицию и размер UI элемента с учетом масштаба"""
        try:
            # Если UI элемент имеет метод on_resize с нужными параметрами
            if hasattr(ui_element, 'on_resize'):
                ui_element.on_resize(x, y, width, height, scale)
            else:
                # Базовая логика масштабирования для UI элементов
                if hasattr(ui_element, 'x') and hasattr(ui_element, 'y'):
                    # Пересчитываем позицию из фиксированных координат
                    original_x = ui_element.x
                    original_y = ui_element.y

                    # Преобразуем из фиксированных координат (1280x768) в текущие
                    ui_element.x = x + (original_x * scale)
                    ui_element.y = y + (original_y * scale)

                    # Масштабируем размеры
                    if hasattr(ui_element, 'width'):
                        ui_element.width = ui_element.width * scale
                    if hasattr(ui_element, 'height'):
                        ui_element.height = ui_element.height * scale
        except Exception as e:
            self.logger.warning(f"Ошибка обновления UI элемента: {e}")

    def toggle_fullscreen(self):
        """Переключает полноэкранный режим"""
        new_fullscreen = not self.fullscreen
        self.set_fullscreen(new_fullscreen)

        # Небольшая задержка для обновления размеров
        import pyglet
        pyglet.clock.schedule_once(lambda dt: self._delayed_resize(), 0.2)

    def _delayed_resize(self):
        """Обновляет камеры после небольшой задержки"""
        width, height = self.get_size()
        self.logger.info(f"Обновление после переключения режима: {width}x{height}")
        self.on_resize(width, height)

    def on_resize(self, width: int, height: int):
        """Вызывается при изменении размера окна"""
        super().on_resize(width, height)
        self.logger.info(f"Окно изменено: {width}x{height}")

        # Обновляем размеры окна
        self.screen_width = width
        self.screen_height = height

        # Обновляем все камеры с фиксированным обзором
        self._update_all_cameras(width, height)

    def on_close(self):
        """Закрытие окна"""
        super().on_close()
