import logging
import arcade
from arcade import SpriteList, camera, Camera2D

from .base_state import BaseState
from ..entities import Player
from ..ui.health_bar import HealthBar
from ..ui.vertical_bar import VerticalBar
from src.world.camera import Camera
from ..world.map_loader import MapLoader
from config import constants as C



class GameplayState(BaseState):
    """
    Состояние основной игры.
    Здесь происходит вся игровая логика.
    """

    def __init__(self, gsm, asset_loader):
        super().__init__("game", gsm, asset_loader)

        self.viewport_width = C.VIEWPORT_WIDTH
        self.viewport_height = C.VIEWPORT_HEIGHT

        self.input_manager = self.gsm.input_manager


        player_scale = self.tile_size / 63  # ≈1.0159 (почти не меняем)


        self.default_camera = Camera2D()
        self.default_camera.viewport = (
            arcade.rect.XYWH(self.gsm.window.width // 2, self.gsm.window.height // 2, self.gsm.window.width,
                             self.gsm.window.height))

        player_textures = self.asset_loader.load_player_sprites()
        self.player = Player(player_textures, self.input_manager, scale=player_scale)
        self.player_list = SpriteList()
        self.player_list.append(self.player)

        self.map_loader = MapLoader()


        # Загружаем Tiled карту
        success = self.map_loader.load(
            "maps/testmap.tmx",  # НОВЫЙ ФАЙЛ
            scale=1
        )

        if not success:
            print("⚠️ Не удалось загрузить Tiled карту, используем fallback")

        self.map_left = 0
        self.map_bottom = 0
        self.map_right = 0
        self.map_top = 0

        bounds = self.map_loader.get_bounds()
        self.setup_map_limits(bounds["left"], bounds["bottom"], bounds["right"], bounds["top"])

        # Получаем слой коллизий
        self.collision_layer = self.map_loader.get_collision_layer()

        # Камера
        self.camera = arcade.camera.Camera2D()

        # 6. Настраиваем игрока
        # Получаем позицию из game_data
        pos = self.player.data.get_player_position()
        self.player.center_x = pos[0] * self.scale_factor  # Масштабируем позицию!
        self.player.center_y = pos[1] * self.scale_factor  # Масштабируем позицию!

        # 7. Скорость игрока пропорциональна размеру тайлов
        self.player.speed = self.tile_size / 8  # 8 пикселей за кадр для 64px тайла

        # UI элементы
        self.ui_elements = []

        # Вертикальная полоска 1 (слева) - фиксированная позиция при 1280x768
        self.deepseek_bar = VerticalBar(
            x=15,  # Отступ от левого края при 1280px
            y=550,  # Отступ сверху при 768px (768 - 2*64 - 64)
            width=15,
            height=150,
            bg_color=arcade.color.PURPLE_NAVY,
            fill_color=arcade.color.PURPLE,
            icon_texture=asset_loader.load_ui_texture("deepseek")
        )
        self.ui_elements.append(self.deepseek_bar)

        # Вертикальная полоска 2 (рядом с первой)
        self.fatigue_bar = VerticalBar(
            x=50,  # Отступ от левого края при 1280px
            y=550,  # Такая же высота как у первой
            width=15,
            height=150,
            bg_color=arcade.color.FRENCH_BEIGE,
            fill_color=arcade.color.BEIGE,
            icon_texture=asset_loader.load_ui_texture("fatigue")
        )
        self.ui_elements.append(self.fatigue_bar)

        # Шкала здоровья (снизу слева) - фиксированная позиция
        self.health_bar = HealthBar(
            self.player,
            x=150,  # Отступ от левого края при 1280px
            y=50,  # Отступ от нижнего края при 768px
            width=200,
            height=20
        )
        self.ui_elements.append(self.health_bar)

        # Сохраняем оригинальные координаты для масштабирования
        for ui_element in self.ui_elements:
            ui_element.original_x = ui_element.x
            ui_element.original_y = ui_element.y
            if hasattr(ui_element, 'width'):
                ui_element.original_width = ui_element.width
            if hasattr(ui_element, 'height'):
                ui_element.original_height = ui_element.height

        # Устанавливаем начальные значения
        self.deepseek_bar.set_value(75, 100)
        self.fatigue_bar.set_value(30, 100)

    def setup_map_limits(self, left, bottom, width, height):
        """Устанавливает границы карты с учетом камеры"""
        self.map_left = left
        self.map_bottom = bottom
        self.map_right = left + width
        self.map_top = bottom + height

        # Логируем границы для отладки
        self.logger.debug(
            f"Границы карты: L={self.map_left}, R={self.map_right}, B={self.map_bottom}, T={self.map_top}")
    def teleport_to(self, x: int, y: int, map: str = None):
        """
        Телепортирует игрока в указанные координаты.
        Если указан map_path - загружает новую карту.
        """
        # Если нужно сменить карту
        if map:
            path = f"maps/{map}.tmx"
            self.logger.info(f"Смена карты: {map}")


            # Загружаем новую карту
            success = self.map_loader.load(path, scale=1)
            if not success:
                self.logger.error(f"Не удалось загрузить карту: {map}")
                return False

            # Обновляем слой коллизий
            self.collision_layer = self.map_loader.get_collision_layer()

            # Обновляем границы карты для камеры
            bounds = self.map_loader.get_bounds()
            self.setup_map_limits(bounds["left"], bounds["bottom"], bounds["right"], bounds["top"])

        # Устанавливаем позицию игрока
        tile_x = x * self.tile_size
        tile_y = y * self.tile_size

        self.player.center_x = tile_x
        self.player.center_y = tile_y

        # Обновляем данные игрока
        self.player.data.set_player_position(tile_x, tile_y, map)

        target_x = self.player.center_x
        target_y = self.player.center_y

        # 3. ОГРАНИЧЕНИЕ ПОЗИЦИИ (Замена set_map_bounds)
        # Учитываем половину размера экрана, чтобы камера не показывала пустоту за краем
        half_screen_w = self.gsm.window.width / 2
        half_screen_h = self.gsm.window.height / 2

        # Зажимаем камеру между границами карты
        final_x = max(self.map_left + half_screen_w, min(target_x, self.map_right - half_screen_w))
        final_y = max(self.map_bottom + half_screen_h, min(target_y, self.map_top - half_screen_h))

        # 4. ПРИМЕНЕНИЕ (Для мгновенного следования)
        self.camera.position = (final_x, final_y)

        self.logger.info(f"Телепорт в ({x}, {y}) на карте: {map or 'текущая'}")
        return True

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

    def on_resize(self, width: int, height: int):
        """Обновление при изменении размера окна"""
        # Обновляем позиции UI элементов
        if hasattr(self, 'ui_elements'):
            for ui_element in self.ui_elements:
                if hasattr(ui_element, 'on_resize'):
                    ui_element.on_resize(width, height)

        # Обновляем позиции вертикальных полосок
        if hasattr(self, 'deepseek_bar'):
            self.deepseek_bar.y = height - 2 * self.tile_size

        if hasattr(self, 'fatigue_bar'):
            self.fatigue_bar.y = height - 2 * self.tile_size

    def setup_map_limits(self, left, bottom, width, height):
        """Устанавливает границы карты с учетом камеры"""
        self.map_left = left
        self.map_bottom = bottom
        self.map_right = left + width
        self.map_top = bottom + height

        # Логируем границы для отладки
        self.logger.debug(
            f"Границы карты: L={self.map_left}, R={self.map_right}, B={self.map_bottom}, T={self.map_top}")

    def update(self, delta_time: float):
        """Обновление игровой логики"""
        if self.is_paused:
            return

        self._handle_input()
        self.player.update(delta_time, collision_layer=self.collision_layer)

        # Обновляем события
        if hasattr(self.map_loader, 'event_manager') and self.map_loader.event_manager:
            self.map_loader.event_manager.update(delta_time)
            self.map_loader.event_manager.check_collisions(self.player, self)

        target_x = self.player.center_x
        target_y = self.player.center_y

        # Получаем реальные размеры viewport камеры
        if hasattr(self.camera, 'viewport'):
            viewport_rect = self.camera.viewport
            half_screen_w = viewport_rect.width / 2
            half_screen_h = viewport_rect.height / 2
        else:
            # Запасной вариант
            half_screen_w = self.gsm.window.width / 2
            half_screen_h = self.gsm.window.height / 2

        # Увеличиваем границы на 1 тайл для плавного скроллинга
        tile_buffer = self.tile_size

        # Зажимаем камеру между границами карты с буфером
        final_x = max(self.map_left + half_screen_w - tile_buffer,
                      min(target_x, self.map_right - half_screen_w + tile_buffer))
        final_y = max(self.map_bottom + half_screen_h - tile_buffer,
                      min(target_y, self.map_top - half_screen_h + tile_buffer))

        # Если карта меньше экрана - центрируем
        if (self.map_right - self.map_left) < (half_screen_w * 2 - tile_buffer * 2):
            final_x = (self.map_left + self.map_right) / 2

        if (self.map_top - self.map_bottom) < (half_screen_h * 2 - tile_buffer * 2):
            final_y = (self.map_bottom + self.map_top) / 2

        # Плавное следование камеры
        current_x, current_y = self.camera.position
        lerp_factor = 0.1  # Коэффициент плавности

        final_x = current_x + (final_x - current_x) * lerp_factor
        final_y = current_y + (final_y - current_y) * lerp_factor

        self.camera.position = (final_x, final_y)

        # Обновляем UI
        for ui_element in self.ui_elements:
            ui_element.update(delta_time)

    def draw(self):
        """Отрисовка игры"""
        # Активируем игровую камеру
        self.camera.use()

        # Очищаем область за пределами viewport (черные полосы)
        if hasattr(self, '_clear_viewport_borders'):
            self._clear_viewport_borders()

        # Рисуем карту
        self.map_loader.draw()
        self.map_loader.event_manager.draw()
        self.player_list.draw()

        # Отладочная информация
        if hasattr(self.player, 'debug_collisions') and self.player.debug_collisions:
            self.player.draw_debug()

            # Отображаем границы карты
            arcade.draw_rect_outline(
                arcade.rect.XYWH(
                    (self.map_left + self.map_right) / 2,
                    (self.map_bottom + self.map_top) / 2,
                    self.map_right - self.map_left,
                    self.map_top - self.map_bottom
                ),
                arcade.color.RED,
                2
            )

        # Переключаемся на UI камеру
        self.default_camera.use()

        # Координаты игрока
        if self.player.debug_collisions:
            text = f"x:{int(self.player.center_x // self.tile_size)} y:{int(self.player.center_y // self.tile_size)}"
            arcade.Text(text,
                        self.gsm.window.width - 3 * self.tile_size,
                        self.gsm.window.height - self.tile_size,
                        arcade.color.LIME,
                        18).draw()

        # Рисуем UI элементы
        for ui_element in self.ui_elements:
            ui_element.draw()

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

    def _init_ui(self):
        """Инициализирует UI элементы"""
        # Пока пусто - добавим позже
        pass

    def _open_pause_menu(self):
        """Открывает меню паузы поверх игры"""
        self.gsm.push_overlay("pause_menu", )

    def _clear_viewport_borders(self):
        """Очищает черные полосы вокруг viewport"""
        if not hasattr(self.camera, 'viewport'):
            return

        viewport_rect = self.camera.viewport
        window_width = self.gsm.window.width
        window_height = self.gsm.window.height

        # Черные полосы слева/справа
        if viewport_rect.x > 0:
            # Слева
            arcade.draw_rect_filled(
                arcade.rect.XYWH(
                    viewport_rect.x / 2,
                    window_height / 2,
                    viewport_rect.x,
                    window_height
                ),
                arcade.color.BLACK
            )

        if viewport_rect.x + viewport_rect.width < window_width:
            # Справа
            right_x = viewport_rect.x + viewport_rect.width
            right_width = window_width - right_x
            arcade.draw_rect_filled(
                arcade.rect.XYWH(
                    right_x + right_width / 2,
                    window_height / 2,
                    right_width,
                    window_height
                ),
                arcade.color.BLACK
            )

        # Черные полосы сверху/снизу
        if viewport_rect.y > 0:
            # Снизу
            arcade.draw_rect_filled(
                arcade.rect.XYWH(
                    window_width / 2,
                    viewport_rect.y / 2,
                    window_width,
                    viewport_rect.y
                ),
                arcade.color.BLACK
            )

        if viewport_rect.y + viewport_rect.height < window_height:
            # Сверху
            top_y = viewport_rect.y + viewport_rect.height
            top_height = window_height - top_y
            arcade.draw_rect_filled(
                arcade.rect.XYWH(
                    window_width / 2,
                    top_y + top_height / 2,
                    window_width,
                    top_height
                ),
                arcade.color.BLACK
            )