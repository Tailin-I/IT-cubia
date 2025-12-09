import arcade
import os
from keyhandler import KeyHandler

# Константы
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Tile-based RPG Prototype"
TILE_SIZE = 32
PLAYER_SPEED = 5



class Player(arcade.Sprite):
    """Класс игрока"""

    def __init__(self):
        super().__init__()
        # Загружаем текстуру игрока
        self.texture = arcade.load_texture(
            ":resources:images/animated_characters/female_person/femalePerson_idle.png"
        )
        self.scale = 0.5

        # Игрок всегда в центре экрана
        self.center_x = SCREEN_WIDTH // 2
        self.center_y = SCREEN_HEIGHT // 2

        # Позиция на карте (в тайлах)
        self.map_x = 0
        self.map_y = 0

        # Скорость движения по карте
        self.speed = PLAYER_SPEED

    def update_position(self, dx, dy):
        """Обновляем позицию на карте"""
        self.map_x += dx
        self.map_y += dy


class Game(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.BLACK)

        # Игрок
        self.player = None
        self.player_list = None  # SpriteList для игрока

        # Тайлы
        self.tiles = {}  # id -> Tile объект
        self.tile_textures = {}  # id -> текстура

        # Карта
        self.tile_map = []  # 2D массив с id тайлов
        self.map_width = 0
        self.map_height = 0

        # Для оптимизации отрисовки
        self.visible_tiles = []

        # Список спрайтов для отрисовки тайлов
        self.tile_sprites = None

        # интеграция классов
        self.key_input = KeyHandler()

    def setup(self):
        """Настройка игры"""
        # Создаем списки спрайтов
        self.player_list = arcade.SpriteList()
        self.tile_sprites = arcade.SpriteList()

        # Создаем игрока
        self.player = Player()
        self.player_list.append(self.player)

        # Загружаем тайлы
        self.load_tiles()

        # Загружаем карту
        self.load_map("../../res/maps/dungeon_1.txt")

        # Инициализируем видимые тайлы
        self.update_visible_tiles()



    def find_player_start_position(self):
        self.player.map_x = self.map_width // 2
        self.player.map_y = self.map_height // 2


    def on_draw(self):
        """Отрисовка игры"""
        self.clear()

        # Рисуем видимые тайлы
        self.tile_sprites.draw()

        # Рисуем игрока (через SpriteList)
        self.player_list.draw()

        # Отладочная информация
        arcade.draw_text(
            f"Позиция: ({self.player.map_x}, {self.player.map_y})",
            10, SCREEN_HEIGHT - 20,
            arcade.color.WHITE, 14
        )
        arcade.draw_text(
            f"Видимых тайлов: {len(self.tile_sprites)}",
            10, SCREEN_HEIGHT - 40,
            arcade.color.WHITE, 14
        )
        arcade.draw_text(
            "WASD - движение, ESC - выход",
            10, 10,
            arcade.color.WHITE, 14
        )

    def on_update(self, delta_time):
        """Обновление игры"""
        # Обновляем видимые тайлы
        self.update_visible_tiles()

    def on_key_press(self, key, modifiers):
        """Обработка нажатия клавиш"""
        dx, dy = 0, 0

        if key == arcade.key.W or key == arcade.key.UP:
            dy = 1
        elif key == arcade.key.S or key == arcade.key.DOWN:
            dy = -1
        elif key == arcade.key.A or key == arcade.key.LEFT:
            dx = -1
        elif key == arcade.key.D or key == arcade.key.RIGHT:
            dx = 1
        elif key == arcade.key.ESCAPE:
            arcade.close_window()

        # Проверяем коллизии
        if dx != 0 or dy != 0:
            new_x = self.player.map_x + dx
            new_y = self.player.map_y + dy

            # Проверяем границы карты
            if 0 <= new_x < self.map_width and 0 <= new_y < self.map_height:
                # Проверяем, не блокируемый ли тайл
                tile_id = self.tile_map[new_y][new_x]
                tile = self.tiles.get(tile_id)

                if tile and not tile.is_blocked:
                    self.player.update_position(dx, dy)

    def on_key_release(self, key, modifiers):
        """Обработка отпускания клавиш"""
        pass


