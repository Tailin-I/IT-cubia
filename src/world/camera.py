class SmartCamera:
    """
    Камера, которая:
    1. Следит за игроком
    2. Останавливается у границ карты
    3. Позволяет игроку отходить от центра
    """

    def __init__(self, screen_width, screen_height, map_width, map_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Границы карты в пикселях
        self.map_width_px = map_width
        self.map_height_px = map_height

        # "Мертвая зона" - расстояние от центра, когда камера начинает двигаться
        self.deadzone_x = screen_width * 0.25  # 1/4 экрана
        self.deadzone_y = screen_height * 0.25

        # Текущая позиция камеры (центр)
        self.x = 0
        self.y = 0

    def update(self, player_x, player_y):
        """Обновляем позицию камеры относительно игрока"""
        # 1. Вычисляем разницу между игроком и центром камеры
        diff_x = player_x - self.x
        diff_y = player_y - self.y

        # 2. Если игрок в мертвой зоне - двигаем камеру
        if abs(diff_x) > self.deadzone_x:
            self.x += (diff_x - self.deadzone_x * (1 if diff_x > 0 else -1)) * 0.1

        if abs(diff_y) > self.deadzone_y:
            self.y += (diff_y - self.deadzone_y * (1 if diff_y > 0 else -1)) * 0.1

        # 3. Ограничиваем камеру границами карты
        half_screen_w = self.screen_width / 2
        half_screen_h = self.screen_height / 2

        self.x = max(half_screen_w, min(self.map_width_px - half_screen_w, self.x))
        self.y = max(half_screen_h, min(self.map_height_px - half_screen_h, self.y))