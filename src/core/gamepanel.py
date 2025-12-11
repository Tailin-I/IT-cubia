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

        # инициализация классов
        self.key_handler = KeyHandler()  # обработчик ввода

        player_grid = arcade.load_spritesheet("res/player/player.png")
        player_list = player_grid.get_texture_grid(size=(16, 16),columns=8, count=8)
        self.player = Player(player_list, self.key_handler)  # игрок


        # SpriteList (для отрисовки)
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)

    def setup(self):
        """Инициализация игры"""
        self.accumulated_time = 0

    def on_draw(self):
        self.clear()
        self.player_list.draw()

        # arcade.draw_rect_filled(arcade.rect.XYWH(self.player_x, self.player_y, self.tile_size, self.tile_size),
        #                         arcade.color.PINK)

    def on_update(self, delta_time):
        """Game loop с фиксированным шагом времени"""
        """это треш, хз как это работает, но дип сик меня убедил что для оптимизации это необходимо"""

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
            else:
                self.set_fullscreen(False)

        # Ctrl+Q для выхода
        if key == arcade.key.Q and modifiers & arcade.key.MOD_CTRL:
            arcade.close_window()

    def on_key_release(self, key, modifiers):
        self.key_handler.on_key_release(key, modifiers)
