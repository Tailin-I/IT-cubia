import logging

import arcade
from typing import Final

from core.keyhandler import KeyHandler
from entity.player import Player

# ===== НАСТРОЙКИ ЭКРАНА =====
ORIGINAL_TILE_SIZE: Final[int] = 16  # Размер тайла в оригинальной графике
SCALE: Final[int] = 3  # Масштаб увеличения

TILE_SIZE: Final[int] = ORIGINAL_TILE_SIZE * SCALE  # 48 px
MAX_SCREEN_COL: Final[int] = 20  # Количество тайлов по горизонтали
MAX_SCREEN_ROW: Final[int] = 12  # Количество тайлов по вертикали

SCREEN_WIDTH: Final[int] = TILE_SIZE * MAX_SCREEN_COL  # 960 px
SCREEN_HEIGHT: Final[int] = TILE_SIZE * MAX_SCREEN_ROW  # 576 px

# Дополнительные настройки
FPS_LIMIT: Final[int] = 60
SCREEN_TITLE: Final[str] = "ITCUBIA"


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
        self._is_closing = False
        self._cleanup_performed = False

        # инициализация классов
        self.key_handler = KeyHandler()  # обработчик ввода

        self.player_textures = None
        self.player_list = arcade.SpriteList()

    def setup(self):
        """Инициализация игры"""
        self.accumulated_time = 0
        if self.player_textures is None:
            player_grid = arcade.load_spritesheet("res/player/player.png")
            self.player_textures = player_grid.get_texture_grid(size=(16, 16), columns=8, count=8)
        self.player = Player(self.player_textures, self.key_handler)
        self.player_list.append(self.player)

    def on_draw(self):
        self.clear()
        self.player_list.draw()

        # arcade.draw_rect_filled(arcade.rect.XYWH(self.player_x, self.player_y, self.tile_size, self.tile_size),
        #                         arcade.color.PINK)

    def on_update(self, delta_time):
        """Game loop с фиксированным шагом времени"""
        """это треш, хз как это работает, но дип сик меня убедил что для оптимизации это необходимо"""

        # Проверяем флаг закрытия
        if hasattr(self, 'should_close') and self.should_close:
            self._perform_cleanup()
            # После очистки закрываем окно
            self.close()
            return

        # Защита от больших дельт (при замирании окна и т.д.)
        delta_time = min(delta_time, 0.25)  # Максимум 250 мс

        # Накапливаем время
        self.accumulated_time += delta_time

        # Выполняем фиксированные обновления
        frames_processed = 0
        max_frames_per_update = 5  # Защита от "спирали смерти"

        while (self.accumulated_time >= self.fixed_delta_time and
               frames_processed < max_frames_per_update):
            self.fixed_update()  # <- вход нового on_update
            self.accumulated_time -= self.fixed_delta_time
            frames_processed += 1

        # Если накопилось слишком много обновлений, сбрасываем
        if self.accumulated_time >= self.fixed_delta_time * max_frames_per_update:
            self.accumulated_time = 0  # Пропускаем старые обновления

        # Необязательно: интерполяция для плавной графики
        # alpha = self.accumulated_time / self.fixed_delta_time
        # self.render_interpolated(alpha)

    def fixed_update(self):
        self.player.move()
        self.player.update()

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

        # Закрываем файловые обработчики логов (опционально)
        self._close_log_handlers()

    def _close_log_handlers(self):
        """Закрыть файловые обработчики логов"""
        for handler in self.logger.handlers:
            if hasattr(handler, 'close'):
                try:
                    handler.close()
                except Exception as e:
                    print(f"Не удалось закрыть обработчик логов: {e}")
