import logging
from typing import Dict, Optional



class GameStateManager:
    """
    Управляет всеми состояниями игры.
    Центральный мозг - решает, какое состояние активно.
    """
    # from src.states.base_state import BaseState

    def __init__(self, window):
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        self.window = window

        # Все зарегистрированные состояния
        self.states: Dict[str, 'BaseState'] = {}

        # Текущее основное состояние (игра, лобби)
        self.current_state: Optional['BaseState'] = None

        # Overlay состояния (инвентарь поверх игры)
        self.overlay_state: Optional['BaseState'] = None

        # Стек состояний для возврата назад
        self.state_stack = []

        # Внешние менеджеры (будут установлены позже)
        self.input_manager = None
        self.asset_loader = None

        self.logger.info("GameStateManager создан")

    def register_state(self, state_id: str, state_instance: 'BaseState'):
        """Регистрирует состояние в менеджере"""
        self.states[state_id] = state_instance
        state_instance.gsm = self  # Даем состоянию ссылку на менеджер
        self.logger.debug(f"Зарегистрировано состояние: {state_id}")

    def switch_to(self, state_id: str, **kwargs):
        """
        Полностью переключает на новое состояние.
        Старое состояние завершается.
        """
        self.logger.info(f"Переключение на состояние: {state_id}")

        # Выходим из текущего состояния
        if self.current_state:
            self.current_state.on_exit()

        # Очищаем overlay (при полном переключении)
        if self.overlay_state:
            self.overlay_state.on_exit()
            self.overlay_state = None

        # Входим в новое состояние
        self.current_state = self.states[state_id]
        self.current_state.on_enter(**kwargs)

        # Меняем профиль ввода
        if self.input_manager:
            self.input_manager.set_current_profile(state_id)

    def push_overlay(self, overlay_id: str, **kwargs):
        """
        Открывает состояние ПОВЕРХ текущего.
        Основное состояние ставится на паузу.
        """
        if overlay_id not in self.states:
            self.logger.error(f"Overlay состояние не найдено: {overlay_id}")
            return

        self.logger.info(f"Открываем overlay: {overlay_id}")

        # Закрываем предыдущий overlay
        if self.overlay_state:
            self.overlay_state.on_exit()

        # Ставим основное состояние на паузу
        if self.current_state:
            self.current_state.on_pause()

        # Открываем новый overlay
        self.overlay_state = self.states[overlay_id]
        self.overlay_state.on_enter(**kwargs)

        # Меняем профиль ввода
        if self.input_manager:
            self.input_manager.set_current_profile(overlay_id)

    def pop_overlay(self):
        """Закрывает текущий overlay, возобновляет основное состояние"""
        if not self.overlay_state:
            return

        self.logger.info(f"Закрываем overlay: {self.overlay_state.state_id}")

        # Закрываем overlay
        self.overlay_state.on_exit()
        self.overlay_state = None

        # Возобновляем основное состояние
        if self.current_state:
            self.current_state.on_resume()

        # Возвращаем профиль ввода
        if self.input_manager:
            self.input_manager.set_current_profile(self.current_state.state_id)

    def update(self, delta_time: float):
        """Обновляет активное состояние"""
        # Сначала overlay (если есть)
        if self.overlay_state:
            self.overlay_state.update(delta_time)
        # Затем основное состояние
        elif self.current_state:
            self.current_state.update(delta_time)

    def draw(self):
        """Отрисовывает состояния (сначала основное, потом overlay)"""
        if self.current_state:
            self.current_state.draw()

        if self.overlay_state:
            self.overlay_state.draw()

    def handle_key_press(self, key: int, modifiers: int):
        """Передает нажатие клавиши активному состоянию"""
        if self.overlay_state:
            self.overlay_state.handle_key_press(key, modifiers)
        elif self.current_state:
            self.current_state.handle_key_press(key, modifiers)

    def handle_key_release(self, key: int, modifiers: int):
        """Передает отпускание клавиши активному состоянию"""
        if self.overlay_state:
            self.overlay_state.handle_key_release(key, modifiers)
        elif self.current_state:
            self.current_state.handle_key_release(key, modifiers)