import os
import arcade
import logging


class GameMap:
    """
    Игровая карта. Загружает матрицу тайлов и управляет их отрисовкой.
    """

    def __init__(self, tile_manager, map_file, tile_size=16):
        """
        Инициализация карты.

        Args:
            tile_manager: TileManager для доступа к тайлам
            map_file: путь к файлу карты (например, "maps/dungeon_1.txt")
            tile_size: размер тайла в пикселях
        """
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        self.tile_manager = tile_manager
        self.map_file = map_file
        self.tile_size = tile_size

        # Данные карты
        self.tile_grid = []  # 2D список tile_id
        self.width = 0  # в тайлах
        self.height = 0  # в тайлах

        # Границы карты в пикселях
        self.pixel_width = 0
        self.pixel_height = 0
        self.left_bound = 0
        self.right_bound = 0
        self.bottom_bound = 0
        self.top_bound = 0

        # Загружаем карту
        self.load_map()

        # СОЗДАЕМ SPRITELIST ДЛЯ ОПТИМИЗАЦИИ
        self.tile_sprites = arcade.SpriteList()
        self._create_tile_sprites()

    def load_map(self):
        """Загружает карту из файла"""
        self.logger.info(f"Загрузка карты из {self.map_file}...")

        try:
            # Полный путь к файлу
            map_path = os.path.join(
                self.tile_manager.rm.get_project_root(),
                "res", self.map_file
            )

            with open(map_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Парсим каждую строку
            self.tile_grid = []
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Разделяем числа
                row = [int(tile_str) for tile_str in line.split()]
                self.tile_grid.append(row)

            # Устанавливаем размеры
            self.height = len(self.tile_grid)
            if self.height > 0:
                self.width = len(self.tile_grid[0])
                # Проверяем, что все строки одинаковой длины
                for i, row in enumerate(self.tile_grid):
                    if len(row) != self.width:
                        self.logger.warning(f"Строка {i} имеет длину {len(row)}, ожидалось {self.width}")

            # Вычисляем пиксельные размеры
            self.pixel_width = self.width * self.tile_size
            self.pixel_height = self.height * self.tile_size

            # Границы карты (левая нижняя точка = (0, 0))
            self.left_bound = 0
            self.right_bound = self.pixel_width
            self.bottom_bound = 0
            self.top_bound = self.pixel_height

            self.logger.info(f"Карта загружена: {self.width}x{self.height} тайлов")
            self.logger.info(f"Пиксельные размеры: {self.pixel_width}x{self.pixel_height}")

        except FileNotFoundError:
            self.logger.error(f"Файл карты не найден: {map_path}")
            self._create_test_map()
        except Exception as e:
            self.logger.exception(f"Ошибка загрузки карты: {e}")
            self._create_test_map()

    def _create_tile_sprites(self):
        """Создает спрайты для всех тайлов карты (однократно)"""
        for y in range(self.height):
            for x in range(self.width):
                tile_id = self.tile_grid[y][x]
                tile_info = self.tile_manager.get_tile(tile_id)

                if tile_info and tile_info['texture']:
                    # Вычисляем пиксельные координаты
                    pixel_x = x * self.tile_size + self.tile_size // 2
                    pixel_y = (self.height - 1 - y) * self.tile_size + self.tile_size // 2

                    # Создаем спрайт
                    sprite = arcade.Sprite()
                    sprite.texture = tile_info['texture']
                    sprite.center_x = pixel_x
                    sprite.center_y = pixel_y
                    sprite.width = self.tile_size
                    sprite.height = self.tile_size

                    self.tile_sprites.append(sprite)

    def _create_test_map(self):
        """Создает простую тестовую карту при ошибке загрузки"""
        self.logger.warning("Создание тестовой карты...")

        # Простая карта 20x15
        self.width = 20
        self.height = 15

        # Заполняем границы тайлом 32 (стена), центр - 0 (пол)
        self.tile_grid = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                if x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1:
                    row.append(32)  # Стена
                else:
                    row.append(0)  # Пол
            self.tile_grid.append(row)

        # Вычисляем пиксельные размеры
        self.pixel_width = self.width * self.tile_size
        self.pixel_height = self.height * self.tile_size

        # Границы карты
        self.left_bound = 0
        self.right_bound = self.pixel_width
        self.bottom_bound = 0
        self.top_bound = self.pixel_height

        self.logger.info(f"Тестовая карта создана: {self.width}x{self.height}")

    def get_tile_at_pixel(self, x, y):
        """
        Возвращает ID тайла по пиксельным координатам.
        Возвращает None, если координаты вне карты.
        """
        if (x < self.left_bound or x >= self.right_bound or
                y < self.bottom_bound or y >= self.top_bound):
            return None

        # Преобразуем пиксели в индексы тайлов
        tile_x = int(x // self.tile_size)
        tile_y = int(y // self.tile_size)

        # Инвертируем Y (в файле первая строка - верх карты)
        tile_y = self.height - 1 - tile_y

        if 0 <= tile_x < self.width and 0 <= tile_y < self.height:
            return self.tile_grid[tile_y][tile_x]
        return None

    def is_solid_at_pixel(self, x, y):
        """Проверяет, есть ли коллизия в указанных пиксельных координатах"""
        tile_id = self.get_tile_at_pixel(x, y)
        if tile_id is None:
            return True  # Вне карты = стена
        return self.tile_manager.is_solid(tile_id)

    def draw(self):
        """Отрисовывает всю карту"""

        self.tile_sprites.draw()


    def get_bounds(self):
        """Возвращает границы карты в виде словаря"""
        return {
            'left': self.left_bound,
            'right': self.right_bound,
            'bottom': self.bottom_bound,
            'top': self.top_bound,
            'width': self.pixel_width,
            'height': self.pixel_height
        }