import os

import arcade

from core import SCREEN_HEIGHT, SCREEN_WIDTH, TILE_SIZE
from tile.tile import Tile


class TileManager:

    def __init__(self):

    def update_visible_tiles(self):
        """Обновляем список видимых тайлов для оптимизации"""
        # Очищаем список спрайтов тайлов
        self.tile_sprites.clear()

        # Вычисляем видимую область в тайлах
        tiles_x = SCREEN_WIDTH // TILE_SIZE + 2
        tiles_y = SCREEN_HEIGHT // TILE_SIZE + 2

        start_x = self.player.map_x - tiles_x // 2
        start_y = self.player.map_y - tiles_y // 2

        # Ограничиваем границы карты
        start_x = max(0, start_x)
        start_y = max(0, start_y)
        end_x = min(self.map_width, start_x + tiles_x)
        end_y = min(self.map_height, start_y + tiles_y)

        # Создаем спрайты для видимых тайлов
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile_id = self.tile_map[y][x]
                tile = self.tiles.get(tile_id)
                if tile:
                    # Вычисляем экранные координаты
                    screen_x = (x - self.player.map_x) * TILE_SIZE + SCREEN_WIDTH // 2
                    screen_y = (y - self.player.map_y) * TILE_SIZE + SCREEN_HEIGHT // 2

                    # Создаем спрайт для тайла
                    sprite = arcade.Sprite()
                    sprite.texture = tile.texture
                    sprite.center_x = screen_x
                    sprite.center_y = screen_y
                    sprite.width = TILE_SIZE
                    sprite.height = TILE_SIZE

                    # Добавляем в список для отрисовки
                    self.tile_sprites.append(sprite)


    def load_tiles(self):
        """Загружаем тайлы из папки и их свойства"""
        # Сначала загружаем информацию о тайлах
        tile_data = {}
        try:
            with open("../../res/maps/tiledata.txt", "r") as f:
                lines = f.readlines()
                # Читаем попарно: имя файла и свойство blocked
                for i in range(0, len(lines), 2):
                    if i + 1 < len(lines):
                        filename = lines[i].strip()
                        is_blocked = lines[i + 1].strip().lower() == "true"
                        # Извлекаем номер из имени файла (убираем .png)
                        tile_id = int(filename.replace(".png", ""))
                        tile_data[tile_id] = is_blocked
        except FileNotFoundError:
            print("Файл tiledata.txt не найден. Используем стандартные тайлы.")
            # Создаем тестовые данные
            for i in range(65):  # от 000 до 064
                tile_data[i] = i % 10 == 0  # Каждый 10-й тайл - блокируемый

        # Теперь загружаем текстуры
        for tile_id, is_blocked in tile_data.items():
            filename = f"../../res/tiles/{tile_id:03d}.png"
            try:
                # Пробуем загрузить из файла
                if os.path.exists(filename):
                    texture = arcade.load_texture(filename)
                else:
                    # Если файла нет
                    print(f"Файл {filename} не найден.")

                self.tile_textures[tile_id] = texture
                self.tiles[tile_id] = Tile(texture, is_blocked)

            except Exception as e:
                print(f"Ошибка загрузки тайла {filename}: {e}")


    def load_map(self, filename):
        """Загружаем карту из файла"""
        try:
            with open(filename, "r") as f:
                lines = f.readlines()

            self.tile_map = []
            for line in lines:
                row = [int(num) for num in line.strip().split()]
                self.tile_map.append(row)

            self.map_height = len(self.tile_map)
            self.map_width = len(self.tile_map[0]) if self.map_height > 0 else 0

            # Устанавливаем игрока в начальную позицию
            self.find_player_start_position()

            print(f"Карта загружена: {self.map_width}x{self.map_height} тайлов")

        except FileNotFoundError:
            print(f"Файл {filename} не найден. Создаем тестовую карту.")