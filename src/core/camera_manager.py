# src/core/camera_manager.py
import logging


class CameraManager:
    """Управляет несколькими камерами"""

    def __init__(self):
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        self.cameras = {}
        self.current_camera = None

    def create_camera(self, name, width, height):
        """Создает новую камеру"""
        from src.world.camera import Camera  # Ленивый импорт

        self.cameras[name] = Camera(width, height)
        if not self.current_camera:
            self.current_camera = name

        self.logger.info(f"Создана камера '{name}'")
        return self.cameras[name]

    def get_camera(self, name):
        """Возвращает камеру по имени"""
        return self.cameras.get(name)

    def set_current(self, name):
        """Устанавливает текущую камеру"""
        if name in self.cameras:
            self.current_camera = name
            self.logger.info(f"Текущая камера: '{name}'")
        else:
            self.logger.error(f"Камера '{name}' не найдена")

    def get_current(self):
        """Возвращает текущую камеру"""
        return self.cameras.get(self.current_camera)

    def resize_all(self, width, height):
        """Изменяет размер всех камер"""
        for name, camera in self.cameras.items():
            camera.resize(width, height)
        self.logger.info(f"Все камеры изменены: {width}x{height}")