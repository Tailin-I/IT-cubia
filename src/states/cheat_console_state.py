import arcade

from src.states.base_state import BaseState


class CheatConsoleState(BaseState):
    """Чит-консоль поверх игры"""

    def __init__(self, gsm, asset_loader):
        super().__init__("cheat_console", gsm, asset_loader)
        self.input_buffer = "|"  # Введенный текст
        self.cursor_visible = True
        self.history = []  # История команд

    def handle_key_press(self, key, modifiers):
        first_part, second_part = self.input_buffer.split("|")
        if self.gsm.input_manager.get_action("cheat_console") or self.gsm.input_manager.get_action("escape"):
            self.gsm.pop_overlay()
        elif self.gsm.input_manager.get_action("select"):
            self._execute_command(first_part+second_part)
            self.input_buffer = "|"
            self.gsm.pop_overlay()
        else:

            self.input_buffer = self.gsm.input_manager.typing(key, first_part, second_part)

    def draw(self):
        """Отрисовка консоли в своем стиле"""
        # Полупрозрачный темный фон
        arcade.draw_rect_filled(
            arcade.rect.XYWH(
                self.gsm.window.width // 2, self.gsm.window.height // 2,
                self.gsm.window.width, self.gsm.window.height),
            (0, 0, 0, 180)  # Полупрозрачный черный
        )

        # ---ПАНЕЛЬ КОНСОЛИ---
        panel_width = self.gsm.window.width // 2
        panel_height = 2 * self.TILE_SIZE
        arcade.draw_rect_filled(
            arcade.rect.XYWH(
                self.gsm.window.width // 2, self.gsm.window.height - self.TILE_SIZE,
                panel_width, panel_height),
            (30, 30, 40, 100)  # Темно-синий
        )
        arcade.draw_rect_outline(
            arcade.rect.XYWH(
                self.gsm.window.width // 2, self.gsm.window.height - self.TILE_SIZE,
                panel_width, panel_height),
            arcade.color.LIME, 2
        )

        # ---РЕЧЬ ДИП СИКА---
        arcade.draw_text(
            "Бог, слушает тебя...",
            self.gsm.window.width // 2, self.gsm.window.height - self.TILE_SIZE,
            arcade.color.LIME, 24,
            anchor_x="center"
        )

        # ---ПОЛЕ ДЛЯ ВВОДА---
        arcade.draw_rect_filled(
            arcade.rect.XYWH(
                self.gsm.window.width // 2,  self.gsm.window.height - 2 * self.TILE_SIZE,
                self.gsm.window.width // 2- self.TILE_SIZE,  self.TILE_SIZE),
            (0, 0, 0)
        )
        arcade.draw_rect_outline(
            arcade.rect.XYWH(
                self.gsm.window.width // 2, self.gsm.window.height - 2 * self.TILE_SIZE,
                self.gsm.window.width // 2- self.TILE_SIZE,  self.TILE_SIZE),
            arcade.color.LIME, 1
        )

        # ---ТЕКСТ---
        arcade.Text(
            self.input_buffer,
            5.6 * self.TILE_SIZE, self.gsm.window.height - 2 * self.TILE_SIZE,
            arcade.color.LIME, 20
        ).draw()

        # История команд
        arcade.Text(
            "\n".join(self.history),
            self.gsm.window.width // 2 - 260, self.gsm.window.height // 2 - 50,
            arcade.color.LIGHT_GRAY, 16
        ).draw()

    def on_enter(self, **kwargs):
        pass

    def on_exit(self):
        pass

    def update(self, delta_time: float):
        pass

    def _execute_command(self, command):
        self.history.append(command)
        if command == "GODMOD":
            self.gsm.current_state.player.health = 9999
        if command.startswith("TP_"):
            # Разбираем команду TP x y
            parts = command.split("_")
            if len(parts) == 3:
                try:
                    x = int(parts[1])
                    y = int(parts[2])

                    # Телепорт игрока
                    if self.gsm.current_state and hasattr(self.gsm.current_state, 'player'):
                        player = self.gsm.current_state.player
                        player.center_x = x
                        player.center_y = y

                        # Обновляем данные
                        if hasattr(player, 'data'):
                            player.data.set_player_position(x, y)
                except ValueError:
                    return "Неверные координаты. Используйте: TP x y"
