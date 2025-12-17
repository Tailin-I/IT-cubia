import arcade
import logging


class Camera:
    """
    Камера, которая следует за игроком с ограничениями по границам карты.
    Поддерживает масштабирование и плавное следование.
    """

    def __init__(self, width, height):
        """
        Инициализация камеры.

        Args:
            width: ширина viewport (ширина окна)
            height: высота viewport (высота окна)
        """
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        self.camera = arcade.camera.Camera2D()

        # Размеры viewport
        self.viewport_width = width
        self.viewport_height = height

        # Мировые координаты центра камеры
        self.position = (0, 0)

        # Масштаб (1.0 = нормальный)
        self.zoom = 1.0
        self.min_zoom = 0.5
        self.max_zoom = 2.0

        # Границы карты (установятся позже)
        self.map_bounds = None

        # Плавное следование (0-1, чем больше - тем быстрее)
        self.follow_speed = 0.1

        # Обновляем viewport
        self._update_viewport()

        self.logger.debug(f"Камера создана: {width}x{height}")

    def _update_viewport(self):
        """Обновляет viewport камеры"""
        self.camera.viewport = arcade.rect.XYWH(
            self.viewport_width // 2,
            self.viewport_height // 2,
            self.viewport_width,
            self.viewport_height
        )
        self.logger.debug(f"Viewport обновлен: {self.camera.viewport}")

    def resize(self, width, height):
        """При изменении размера окна"""
        self.logger.info(f"Изменение размера камеры: {width}x{height}")
        self.viewport_width = width
        self.viewport_height = height
        self._update_viewport()

    def set_map_bounds(self, left, bottom, width, height):
        """
        Устанавливает границы карты.

        Args:
            left: левая граница в пикселях
            bottom: нижняя граница в пикселях
            width: ширина карты в пикселях
            height: высота карты в пикселях
        """
        self.map_bounds = {
            'left': left,
            'bottom': bottom,
            'right': left + width,
            'top': bottom + height,
            'width': width,
            'height': height
        }
        self.logger.info(f"Границы карты установлены: {self.map_bounds}")

    def follow_player(self, player_x, player_y):
        """
        Плавное следование за игроком с учетом границ карты.

        Args:
            player_x: X координата игрока
            player_y: Y координата игрока
        """
        # Целевая позиция - позиция игрока
        target_x = player_x
        target_y = player_y

        # Если есть границы карты - ограничиваем
        if self.map_bounds:
            # Вычисляем половину видимой области с учетом зума
            half_viewport_width = (self.viewport_width / 2) / self.zoom
            half_viewport_height = (self.viewport_height / 2) / self.zoom

            # Проверяем, помещается ли вся карта на экране
            map_fits_width = self.map_bounds['width'] <= self.viewport_width / self.zoom
            map_fits_height = self.map_bounds['height'] <= self.viewport_height / self.zoom

            if map_fits_width:
                # Карта полностью помещается по ширине - центрируем
                target_x = (self.map_bounds['left'] + self.map_bounds['right']) / 2
                self.logger.debug(f"Карта помещается по ширине, центрируем: {target_x}")
            else:
                # Ограничиваем по границам
                min_x = self.map_bounds['left'] + half_viewport_width
                max_x = self.map_bounds['right'] - half_viewport_width
                target_x = max(min_x, min(max_x, target_x))

            if map_fits_height:
                # Карта полностью помещается по высоте - центрируем
                target_y = (self.map_bounds['bottom'] + self.map_bounds['top']) / 2
                self.logger.debug(f"Карта помещается по высоте, центрируем: {target_y}")
            else:
                min_y = self.map_bounds['bottom'] + half_viewport_height
                max_y = self.map_bounds['top'] - half_viewport_height
                target_y = max(min_y, min(max_y, target_y))

        # Плавное движение к цели
        self.position = (
            self.position[0] + (target_x - self.position[0]) * self.follow_speed,
            self.position[1] + (target_y - self.position[1]) * self.follow_speed
        )

        # Обновляем камеру
        self.camera.position = self.position
        self.camera.zoom = self.zoom

        self.logger.debug(f"Камера: позиция={self.position}, зум={self.zoom}")

    def zoom_in(self):
        """Приближение"""
        new_zoom = self.zoom * 1.1
        if new_zoom <= self.max_zoom:
            self.zoom = new_zoom
            self.logger.debug(f"Приближение: зум={self.zoom}")

    def zoom_out(self):
        """Отдаление"""
        new_zoom = self.zoom / 1.1
        if new_zoom >= self.min_zoom:
            self.zoom = new_zoom
            self.logger.debug(f"Отдаление: зум={self.zoom}")

    def reset_zoom(self):
        """Сброс масштаба"""
        self.zoom = 1.0
        self.logger.debug("Сброс зума: 1.0")

    def use(self):
        """Активирует камеру для отрисовки"""
        self.camera.use()