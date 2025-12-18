import logging
from abc import ABC, abstractmethod

from src.core.game_data import game_data
from src.core.resource_manager import ResourceManager


class BaseState(ABC):
    """
    Базовый класс для всех состояний.
    Только ОСНОВНЫЕ методы обязательны.
    """

    def __init__(self, state_id: str, gsm, asset_loader=None):
        self.logger = logging.getLogger(self.__class__.__name__)



        self.game_data = game_data
        self.rm = ResourceManager()
        self.asset_loader = asset_loader

        self.state_id = state_id
        self.gsm = gsm
        self.is_active = False

        # РАЗМЕРЫ:
        self.ORIGINAL_TILE_SIZE = self.gsm.window.ORIGINAL_TILE_SIZE
        self.TILE_SIZE = self.gsm.window.TARGET_TILE_SIZE
        self.SCALE_FACTOR = self.gsm.window.SCALE_FACTOR

    # ТОЛЬКО ЭТИ методы обязательны для всех состояний
    @abstractmethod
    def on_enter(self, **kwargs):
        """Вход в состояние - ОБЯЗАТЕЛЬНО"""
        pass

    @abstractmethod
    def on_exit(self):
        """Выход из состояния - ОБЯЗАТЕЛЬНО"""
        pass

    @abstractmethod
    def update(self, delta_time: float):
        """Обновление - ОБЯЗАТЕЛЬНО"""


    @abstractmethod
    def draw(self):
        """Отрисовка - ОБЯЗАТЕЛЬНО"""
        pass

    # Эти методы НЕ обязательны (убираем @abstractmethod)
    def on_pause(self):
        """Пауза - НЕ обязательно для всех"""
        pass

    def on_resume(self):
        """Возобновление - НЕ обязательно для всех"""
        pass

    def handle_key_press(self, key: int, modifiers: int):
        """Обработка клавиш - НЕ обязательно"""
        pass

    def handle_key_release(self, key: int, modifiers: int):
        """Обработка отпускания - НЕ обязательно"""
        pass