import logging
import os

import arcade
from typing import Final
from .resource_manager import resource_manager
from .input_manager import KeyHandler
from src.entities.player import Player

# ===== НАСТРОЙКИ ЭКРАНА И МАСШТАБИРОВАНИЕ =====
# Размеры в исходных файлах
ORIGINAL_TILE_SIZE: Final[int] = 16  # Размер тайла в оригинальной графике
PLAYER_TEXTURE_SIZE: Final[int] = 16  # Размер спрайта игрока в файле

# Масштабы (можно менять отдельно)
TILE_SCALE: Final[int] = 4  # Масштаб тайлов (16*4=64)
PLAYER_SCALE: Final[int] = 4  # Масштаб игрока (16*4=64)

# Итоговые размеры после масштабирования
TILE_SIZE: Final[int] = ORIGINAL_TILE_SIZE * TILE_SCALE  # 64 px
PLAYER_SIZE: Final[int] = PLAYER_TEXTURE_SIZE * PLAYER_SCALE  # 64 px

# Настройки экрана
MAX_SCREEN_COL: Final[int] = 20  # Количество тайлов по горизонтали
MAX_SCREEN_ROW: Final[int] = 12  # Количество тайлов по вертикали

SCREEN_WIDTH: Final[int] = TILE_SIZE * MAX_SCREEN_COL  # 1280 px
SCREEN_HEIGHT: Final[int] = TILE_SIZE * MAX_SCREEN_ROW  # 768 px

# Дополнительные настройки
FPS_LIMIT: Final[int] = 60
SCREEN_TITLE: Final[str] = "ITCUBIA"
CAMERA_MIN_ZOOM: Final[float] = 0.5  # Минимальное приближение
CAMERA_MAX_ZOOM: Final[float] = 2.0  # Максимальное отдаление
CAMERA_ZOOM_SPEED: Final[float] = 0.1  # Скорость изменения зума

class GamePanel(arcade.Window):
    """Оптимизированный основной класс игры"""

    def __init__(self):
        # Получаем логгер для этого класса

        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        self.logger.info(f"Инициализация игры: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
        super().__init__(
            width=SCREEN_WIDTH,
            height=SCREEN_HEIGHT,
            title=SCREEN_TITLE,
            fullscreen=False,
            update_rate=1 / FPS_LIMIT,

        )
        self.tile_size = TILE_SIZE
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT

        arcade.set_background_color(arcade.color.ASH_GREY)

        # Флаги состояния
        self.should_close = False
        self._is_closing = False
        self._cleanup_performed = False

        # инициализация классов
        self.key_handler = KeyHandler()  # обработчик ввода

        self.player_textures = None
        self.player_list = arcade.SpriteList()

    def setup(self):
        """Инициализация игры"""
        # создание игрока (БЕЗ вызова setup_hitbox)
        self.player_textures = resource_manager.load_spritesheet(
            "player/player.png",
            size=(16, 16),
            columns=8,
            count=8
        )

        # Передаем PLAYER_SCALE из констант
        self.player = Player(
            self.player_textures,
            self.key_handler,
            scale=PLAYER_SCALE
        )

        # НЕ вызываем setup_hitbox
        self.player_list.append(self.player)

        # Загрузка других ресурсов (пример)
        # self.background = resource_manager.load_texture("backgrounds/forest.png")
        # self.jump_sound = resource_manager.load_sound("sounds/jump.wav")

    def on_draw(self):
        self.clear()
        self.player_list.draw()

    def on_update(self, delta_time):

        # Проверяем флаг закрытия
        if hasattr(self, 'should_close') and self.should_close:
            self._perform_cleanup()
            # После очистки закрываем окно
            self.close()
            return

        self.player.move()
        self.player.update()

    def get_file_size_stat(self, filepath):
        try:
            stat_info = os.stat(filepath)
            return stat_info.st_size
        except FileNotFoundError:
            return None


    def on_key_press(self, key, modifiers):
        self.key_handler.on_key_press(key, modifiers)

        if self.key_handler.actions['fullscreen']:
            if not self.fullscreen:
                self.set_fullscreen(True)
                self.logger.info("Включен полноэкранный режим")
            else:
                self.set_fullscreen(False)
                self.logger.info("Включен оконный режим")

        # Ctrl+Q для выхода
        if key == arcade.key.Q and modifiers & arcade.key.MOD_CTRL:
            self._initiate_shutdown()

    def _initiate_shutdown(self):
        """Инициировать завершение работы"""
        if self._is_closing:
            return

        self._is_closing = True
        self.logger.info("Инициировано завершение работы")

        # Устанавливаем флаг для on_update
        self.should_close = True

    def on_key_release(self, key, modifiers):
        self.key_handler.on_key_release(key, modifiers)

    def _perform_cleanup(self):
        """Выполнить очистку ресурсов (вызывается только один раз)"""
        if self._cleanup_performed:
            return

        self.logger.info("Выполнение очистки ресурсов...")

        try:
            # 1. Сохраняем настройки клавиш
            if hasattr(self, 'key_handler') and self.key_handler:
                success = self.key_handler.save_key_bindings()
                if success:
                    self.logger.info("Настройки клавиш сохранены")
                else:
                    self.logger.warning("Не удалось сохранить настройки клавиш")

            # 2. Освобождаем спрайты и текстуры
            if hasattr(self, 'player_list'):
                self.player_list.clear()
                self.logger.debug("Спрайтлист очищен")

            # 3. Сохраняем другие данные игры если нужно
            # self.save_game_state()

            self.logger.info("Очистка завершена успешно")

        except Exception as e:
            self.logger.error(f"Ошибка при очистке ресурсов: {e}", exc_info=True)
        finally:
            self._cleanup_performed = True

    def on_close(self):
        """
        Вызывается когда окно закрывается (крестик или self.close())
        """
        self.logger.info("Событие on_close вызвано")

        # Если очистка еще не выполнена (закрыли через крестик)
        if not self._cleanup_performed:
            self._perform_cleanup()

        # Всегда вызываем родительский метод
        try:
            super().on_close()
        except Exception as e:
            self.logger.error(f"Ошибка в родительском on_close: {e}")

        self.logger.info("Окно закрыто")

