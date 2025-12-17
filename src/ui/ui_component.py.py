class UIComponent:
    """Базовый класс для всех UI элементов"""

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = True
        self.parent = None

    def update(self, delta_time):
        """Обновление логики UI"""
        pass

    def draw(self):
        """Отрисовка UI"""
        pass

    def handle_input(self, input_manager):
        """Обработка ввода"""
        pass