class GameStateManager:
    """
    Центральный менеджер состояний.
    ТОЛЬКО ОН решает, какое состояние сейчас активно.
    """

    def __init__(self, window):
        self.window = window
        self.states = {}  # Словарь всех состояний: {0: LobbyState, 1: GameState...}
        self.current_state_id = 0  # Начинаем с лобби
        self.previous_state_id = None
        self._initialized = False

    def register_state(self, state_id, state_instance):
        """Регистрируем состояние"""
        self.states[state_id] = state_instance

    def switch_to(self, new_state_id, **kwargs):
        """Переключаемся на новое состояние"""
        old_state = self.current_state
        if old_state:
            old_state.on_exit()  # Выходим из старого

        self.previous_state_id = self.current_state_id
        self.current_state_id = new_state_id

        new_state = self.current_state
        new_state.on_enter(**kwargs)  # Входим в новое

    def update(self, delta_time):
        """Обновляем только текущее состояние"""
        if self.current_state:
            self.current_state.update(delta_time)

    def draw(self):
        """Рисуем только текущее состояние"""
        if self.current_state:
            self.current_state.draw()

    @property
    def current_state(self):
        return self.states.get(self.current_state_id)