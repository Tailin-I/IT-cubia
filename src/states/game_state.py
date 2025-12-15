import logging
import arcade
from arcade import SpriteList, camera

from .base_state import BaseState
from ..entities import Player


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


        self.game_map = None
        self.ui_elements = arcade.SpriteList()

        # ИНИЦИАЛИЗИРУЕМ флаги в конструкторе
        self.is_paused = False
        self.is_initialized = False

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

    def update(self, delta_time: float):
        """Обновление игровой логики"""
        if self.is_paused:
            return

        # 1. Обрабатываем ввод игрока
        self.player.update()
        self._handle_input()

        # Пока нет игрока и карты - просто ждем

    def draw(self):
        """Отрисовка игры"""
        arcade.set_background_color(arcade.color.LIME)

        arcade.draw_triangle_filled(200, 500, 900, 500, 500, 70, arcade.color.GRAY)

        # arcade.start_render()
        arcade.Text(
            "ИГРА АКТИВНА",
            500,
            600,
            arcade.color.BLACK,
            48,
            anchor_x="center",
            anchor_y="center",
            bold=True
        ).draw()


        self.camera.use()
        self.player_list.draw()





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