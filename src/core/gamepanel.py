import arcade
from typing import Final

from core.keyhandler import KeyHandler

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

        self.accumulated_time = 0
        arcade.set_background_color(arcade.color.BLACK)
        self.player_x = 100
        self.player_y = self.screen_height
        self.player_speed = 4

        # инициализация классов
        self.key_handler = KeyHandler()



    def on_key_press(self, key, modifiers):
        self.key_handler.on_key_press(key)
        if self.key_handler.actions['fullscreen']:
            if not self.fullscreen:
                self.set_fullscreen(True)
            else:
                self.set_fullscreen(False)

    def on_key_release(self, key, modifiers):
        self.key_handler.on_key_release(key)

    def setup(self):
        """Инициализация игры"""

    def on_draw(self):
        self.clear()

        arcade.draw_rect_filled(arcade.rect.XYWH(self.player_x, self.player_y, self.tile_size, self.tile_size),
                                arcade.color.PINK)

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
        self.move()

    def get_movement(self):
        """Возвращает нормализованный вектор движения"""
        dx, dy = 0, 0

        if self.key_handler.actions['move_up']:
            dy += self.player_speed
        if self.key_handler.actions['move_down']:
            dy -= self.player_speed
        if self.key_handler.actions['move_left']:
            dx -= self.player_speed
        if self.key_handler.actions['move_right']:
            dx += self.player_speed

        # Нормализация
        if dx != 0 and dy != 0:
            factor = 0.7071
            dx *= factor
            dy *= factor

        return dx, dy

    def move(self):
        """"персонаж всегда двигается (пусть порой и на 0 px) """
        dx, dy = self.get_movement()
        self.player_x += dx
        self.player_y += dy