import logging
from typing import Dict, Optional, List

from src.states.base_state import BaseState


class GameStateManager:
    """
    Управляет всеми состояниями игры.
    Центральный мозг - решает, какое состояние активно.
    """

    def __init__(self, window):
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        self.window = window

        # Все зарегистрированные состояния
        self.states: Dict[str, 'BaseState'] = {}

        # Текущее основное состояние (игра, лобби)
        self.current_state: Optional['BaseState'] = None

        # СТЕК overlay состояний
        self.overlay_stack: List['BaseState'] = []

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
        Используется для кардинальной смены состояния (лобби → игра).
        """
        self.logger.info(f"Переключение на состояние: {state_id}")

        # Выходим из текущего основного состояния
        if self.current_state:
            self.current_state.on_exit()

        # Очищаем ВЕСЬ стек overlay'ов (при полном переключении)
        while self.overlay_stack:
            overlay = self.overlay_stack.pop()
            overlay.on_exit()

        # Входим в новое состояние
        self.current_state = self.states[state_id]
        self.current_state.on_enter(**kwargs)

        self.logger.info(f"Стек overlay'ов очищен. Новое состояние: {state_id}")

    def push_overlay(self, overlay_id: str, **kwargs):
        """
        Открывает состояние ПОВЕРХ текущего.
        Основное состояние или предыдущий overlay ставится на паузу.
        """
        if overlay_id not in self.states:
            self.logger.error(f"Overlay состояние не найдено: {overlay_id}")
            return

        self.logger.info(f"Открываем overlay: {overlay_id}")

        # Ставим на паузу текущий активный overlay (или основное состояние)
        active_state = self.get_active_state()
        if active_state:
            active_state.on_pause()

        # Создаем новый overlay
        new_overlay = self.states[overlay_id]

        # Добавляем его в конец стека (верх стека)
        self.overlay_stack.append(new_overlay)

        # Входим в новый overlay
        new_overlay.on_enter(**kwargs)
        self.logger.info(f"Overlay добавлен в стек. Всего overlay'ов: {len(self.overlay_stack)}")

    def pop_overlay(self):
        """
        Закрывает САМЫЙ ВЕРХНИЙ overlay из стека.
        Возобновляет предыдущий overlay или основное состояние.
        """
        if not self.overlay_stack:
            self.logger.warning("Попытка закрыть overlay, но стек пуст")
            return
        # костыль - если не вписать сюда то состояние не исчезнет а откроется снова
        self.input_manager.reset_action('cheat_console')
        self.input_manager.reset_action('escape')
        self.input_manager.reset_action('select')

        # Получаем текущий активный overlay (верх стека)
        current_overlay = self.overlay_stack[-1]
        self.logger.info(f"Закрываем overlay: {current_overlay.state_id}")

        # Выходим из него
        current_overlay.on_exit()

        # Удаляем его из стека
        self.overlay_stack.pop()

        # Определяем, какое состояние теперь активно
        if self.overlay_stack:
            # Есть еще overlay'ы в стеке
            new_active = self.overlay_stack[-1]
            new_active.on_resume()
            self.logger.info(
                f"Возобновлен overlay: {new_active.state_id}. Осталось overlay'ов: {len(self.overlay_stack)}")
        else:
            # Стек overlay'ов пуст - возвращаемся к основному состоянию
            if self.current_state:
                self.current_state.on_resume()

            self.logger.info("Стек overlay'ов опустошен. Возврат к основному состоянию")

    def get_active_state(self) -> Optional['BaseState']:
        """
        Возвращает текущее активное состояние:
        - Самый верхний overlay из стека, если он есть
        - Иначе основное состояние
        """
        if self.overlay_stack:
            return self.overlay_stack[-1]
        return self.current_state

    def update(self, delta_time: float):
        """Обновляет активное состояние"""
        active_state = self.get_active_state()
        if active_state:
            active_state.update(delta_time)

    def draw(self):
        """Отрисовывает состояния в правильном порядке"""
        # Рисуем основное состояние
        if self.current_state:
            self.current_state.draw()

        # Рисуем ВСЕ overlay'ы по порядку (от нижнего к верхнему)
        for overlay in self.overlay_stack:
            overlay.draw()

    def handle_key_press(self, key: int, modifiers: int):
        """Передает нажатие клавиши активному состоянию"""
        active_state = self.get_active_state()
        if active_state:
            active_state.handle_key_press(key, modifiers)

    def handle_key_release(self, key: int, modifiers: int):
        """Передает отпускание клавиши активному состоянию"""
        active_state = self.get_active_state()
        if active_state:
            active_state.handle_key_release(key, modifiers)