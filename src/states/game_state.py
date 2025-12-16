import logging
import arcade
from arcade import SpriteList, camera

from .base_state import BaseState
from ..entities import Player
from ..world.map import GameMap
from ..world.tilemanager import TileManager


class GameplayState(BaseState):
    """
    Состояние основной игры.
    Здесь происходит вся игровая логика.
    """

    def __init__(self, gsm, asset_loader):
        super().__init__("game", gsm, asset_loader)

        self.input_manager = self.gsm.input_manager

        # Загружаем текстуры (словарь)
        player_textures = self.asset_loader.load_player_sprites(scale=1)

        # Создаем игрока с словарем текстур
        self.player = Player(player_textures, self.input_manager, scale=1)

        self.player_list = SpriteList()
        self.player_list.append(self.player)

        # Камера
        # self.camera = arcade.Camera(self.gsm.window.width, self.gsm.window.height)
        self.camera = camera.Camera2D() # для игрока
        self.camera.viewport = (arcade.rect.XYWH( self.gsm.window.width//2,
                                                  self.gsm.window.height//2,
                                                  self.gsm.window.width,
                                                  self.gsm.window.height))

        # ИНИЦИАЛИЗИРУЕМ флаги в конструкторе
        self.is_paused = False
        self.is_initialized = False

        # Создаем TileManager и загружаем тайлы
        self.tile_manager = TileManager(self.gsm.window.resource_manager, tile_size=16)
        self.tile_manager.load_tileset("tiles/")  # Путь к вашим тайлам

        # Создаем карту
        self.game_map = GameMap(self.tile_manager, "maps/forest.txt", tile_size=16)

        # Обновляем камеру - используем нашу камеру
        from src.world.camera import Camera
        self.camera = Camera(self.gsm.window.width, self.gsm.window.height)

        # Устанавливаем границы карты для камеры
        bounds = self.game_map.get_bounds()
        self.camera.set_map_bounds(
            bounds['left'], bounds['bottom'],
            bounds['width'], bounds['height']
        )

        # Позиционируем игрока в центре карты
        player_start_x = bounds['width'] // 2
        player_start_y = bounds['height'] // 2
        self.player.center_x = player_start_x
        self.player.center_y = player_start_y

    def on_enter(self, **kwargs):
        """Вызывается при входе в это состояние"""
        # СБРАСЫВАЕМ все флаги при каждом входе!
        self.is_paused = False
        self.is_initialized = True

        # Инициализируем UI
        self._init_ui()

    def on_exit(self):
        """Вызывается при выходе из состояния"""
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

    def _handle_camera_input(self):
        """Обработка ввода для управления камерой"""
        if not self.input_manager:
            return

        # Масштабирование (Ctrl + Plus/Minus)
        # Нужно добавить соответствующие действия в InputManager
        # Пока оставим как TODO

    def update(self, delta_time: float):
        """Обновление игровой логики"""
        if self.is_paused:
            return

            # Обновляем игрока
        self.player.update(delta_time)

        # Камера следует за игроком
        self.camera.follow_player(self.player.center_x, self.player.center_y)

        # Обработка ввода для камеры (масштабирование)
        self._handle_camera_input()

        self._handle_input()

    def draw(self):
        """Отрисовка игры"""
        # Активируем камеру
        self.camera.use()

        # Рисуем карту
        self.game_map.draw()

        # Рисуем игрока
        self.player_list.draw()

        # Отключаем камеру для UI (если нужно)
        # arcade.set_viewport(0, self.gsm.window.width, 0, self.gsm.window.height)

        # Рисуем UI поверх
        arcade.draw_text(
            "ИГРА АКТИВНА",
            self.gsm.window.width // 2,
            self.gsm.window.height - 50,
            arcade.color.BLACK, 36,
            anchor_x="center"
        )





    def on_resize(self, width, height):
        """При изменении размера окна обновляем камеру"""
        # Обновляем viewport камеры
        self.camera.viewport =self.camera.viewport = (arcade.rect.XYWH( self.gsm.window.width//2,
                                                  self.gsm.window.height//2,
                                                  self.gsm.window.width,
                                                  self.gsm.window.height))

        # Также можно обновить проекцию, если она используется
        # self.camera.projection = (0, width, 0, height)

        print(f"Размер окна изменен: {width}x{height}")


    def _handle_input(self):
        """Обработка ввода для игрового состояния"""
        if not self.input_manager:
            return

        # ESC - открыть меню паузы
        if self.input_manager.get_action("escape"):
            print("🔼 Нажата пауза")
            self._open_pause_menu()

        # Для теста - выводим нажатые клавиши движения
        # if self.input_manager.get_action("up"):
        #     print("↑ Движение вверх")
        # if self.input_manager.get_action("down"):
        #     print("↓ Движение вниз")
        # if self.input_manager.get_action("left"):
        #     print("← Движение влево")
        # if self.input_manager.get_action("right"):
        #     print("→ Движение вправо")

    def _init_ui(self):
        """Инициализирует UI элементы"""
        # Пока пусто - добавим позже
        pass

    def _open_pause_menu(self):
        """Открывает меню паузы поверх игры"""
        self.gsm.push_overlay("pause_menu", )