import logging
import arcade
from arcade import SpriteList, camera, Camera2D

from .base_state import BaseState
from ..entities import Player
from ..ui.health_bar import HealthBar
from ..ui.vertical_bar import VerticalBar
from src.world.camera import Camera
from ..world.map_loader import MapLoader


class GameplayState(BaseState):
    """
    Состояние основной игры.
    Здесь происходит вся игровая логика.
    """

    def __init__(self, gsm, asset_loader):
        super().__init__("game", gsm, asset_loader)

        self.input_manager = self.gsm.input_manager


        # 1. Игрок: масштабируем под новые тайлы
        # Если оригинальный игрок 63px, а тайлы теперь 64px:
        player_scale = self.TILE_SIZE / 63  # ≈1.0159 (почти не меняем)
        # Или если хотим, чтобы игрок был точно под тайл:
        # player_scale = 64 / 63  # Делаем игрока 64px

        self.default_camera = Camera2D()
        self.default_camera.viewport = (
            arcade.rect.XYWH(self.gsm.window.width // 2, self.gsm.window.height // 2, self.gsm.window.width,
                             self.gsm.window.height))

        player_textures = self.asset_loader.load_player_sprites()
        self.player = Player(player_textures, self.input_manager, scale=player_scale)
        self.player_list = SpriteList()
        self.player_list.append(self.player)

        self.map_loader = MapLoader(self.gsm.window.resource_manager)

        # Загружаем Tiled карту
        success = self.map_loader.load(
            "maps/test_map.tmx",  # НОВЫЙ ФАЙЛ
            scale=1
        )

        if not success:
            print("⚠️ Не удалось загрузить Tiled карту, используем fallback")

        # Получаем слой коллизий
        self.collision_layer = self.map_loader.get_collision_layer()

        # Камера - используем границы из map_loader
        self.camera = Camera(self.gsm.window.width, self.gsm.window.height)
        bounds = self.map_loader.get_bounds()
        self.camera.set_map_bounds(
            bounds['left'], bounds['bottom'],
            bounds['width'], bounds['height']
        )

        # 6. Настраиваем игрока
        # Получаем позицию из game_data
        pos = self.player.data.get_player_position()
        self.player.center_x = pos[0] * self.SCALE_FACTOR  # Масштабируем позицию!
        self.player.center_y = pos[1] * self.SCALE_FACTOR  # Масштабируем позицию!

        # 7. Скорость игрока пропорциональна размеру тайлов
        self.player.speed = self.TILE_SIZE / 8  # 8 пикселей за кадр для 64px тайла

        # UI элементы
        self.ui_elements = []

        # Шкала здоровья (снизу слева)
        self.health_bar = HealthBar(
            self.player,
            x=150,  # Отступ от левого края
            y=50,  # Отступ от нижнего края
            width=200,
            height=20
        )
        self.ui_elements.append(self.health_bar)

        # Вертикальная полоска 1 (слева)
        self.deepseek_bar = VerticalBar(
            x=self.TILE_SIZE / 2,  # Ближе к краю
            y=self.gsm.window.height - 2 * self.TILE_SIZE,
            bg_color=arcade.color.PURPLE_NAVY,
            fill_color=arcade.color.PURPLE,
            icon_texture=asset_loader.load_ui_texture("deepseek")
        )
        self.ui_elements.append(self.deepseek_bar)

        # Вертикальная полоска 2 (рядом с первой)
        self.fatigue_bar = VerticalBar(
            x=self.TILE_SIZE,  # Рядом с первой
            y=self.gsm.window.height - 2 * self.TILE_SIZE,
            bg_color=arcade.color.FRENCH_BEIGE,
            fill_color=arcade.color.BEIGE,
            icon_texture=asset_loader.load_ui_texture("fatigue")
        )
        self.ui_elements.append(self.fatigue_bar)

        # Устанавливаем начальные значения
        self.deepseek_bar.set_value(75, 100)
        self.fatigue_bar.set_value(30, 100)

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

        self._handle_input()

        # Обновляем игрока
        self.player.update(delta_time, collision_layer=self.collision_layer)

        # Обновляем и проверяем события (КОЛЛИЗИИ!)
        if hasattr(self.map_loader, 'event_manager') and self.map_loader.event_manager:
            self.map_loader.event_manager.update(delta_time)
            self.map_loader.event_manager.check_collisions(self.player, self)
            # Добавим отладку

        # Камера следует за игроком
        self.camera.follow_player(self.player.center_x, self.player.center_y)

        # Обновляем UI
        for ui_element in self.ui_elements:
            ui_element.update(delta_time)

    def draw(self):
        """Отрисовка игры"""
        # Активируем камеру
        self.camera.use()

        # Рисуем карту
        self.map_loader.draw()

        # сундуки
        self.map_loader.event_manager.draw()

        # Рисуем игрока
        self.player_list.draw()

        # Отрисовываем хитбокс для отладки
        if hasattr(self.player, 'debug_collisions') and self.player.debug_collisions:
            self.player.draw_debug()


        # Отключаем камеру для UI (если нужно)
        self.default_camera.use()
        # Переключаемся на UI камеру
        self.default_camera.use()

        # координаты
        if self.player.debug_collisions:
            text = f"x:{int(self.player.center_x // self.TILE_SIZE)} y:{int(self.player.center_y // self.TILE_SIZE)}"
            arcade.Text(text,
                        self.gsm.window.width - 3*self.TILE_SIZE,
                        self.gsm.window.height - self.TILE_SIZE,
                        arcade.color.LIME,
                        18).draw()


        # Рисуем UI элементы
        for ui_element in self.ui_elements:
            ui_element.draw()

    def on_resize(self, width, height):
        """При изменении размера окна обновляем камеру"""
        # Обновляем viewport камеры
        self.camera.viewport = self.camera.viewport = (arcade.rect.XYWH(self.gsm.window.width // 2,
                                                                        self.gsm.window.height // 2,
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
        if self.input_manager.get_action("cheat_console"):  # F2
            self.gsm.push_overlay("cheat_console")

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
