# src/world/tilemanager.py
import os
import arcade
import logging


class TileManager:
    """
    Менеджер тайлов. Загружает все текстуры тайлов и их свойства.
    """

    def __init__(self, resource_manager, tile_size=16):
        """
        Инициализация менеджера тайлов.

        Args:
            resource_manager: ResourceManager для загрузки текстур
            tile_size: размер тайла в пикселях
        """
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        self.rm = resource_manager
        self.tile_size = tile_size
        self.tiles = {}  # tile_id -> {'texture': texture, 'solid': bool}

    def load_tileset(self, tileset_path, data_file="tiledata.txt"):
        """
        Загружает тайлы из папки.

        Args:
            tileset_path: путь к папке с тайлами (например, "tiles/")
            data_file: файл с информацией о коллизиях
        """
        self.logger.info(f"Загрузка тайлов из {tileset_path}...")

        # Полный путь к файлу данных
        data_path = os.path.join(self.rm.get_project_root(), "res", "maps", data_file)

        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines()]

            tile_id = 0
            i = 0

            while i < len(lines):
                # Имя файла
                if i >= len(lines):
                    break
                filename = lines[i]
                i += 1

                # Свойство solid (true/false)
                if i >= len(lines):
                    solid = False
                else:
                    solid_str = lines[i].lower()
                    solid = solid_str == 'true'
                    i += 1

                # Загружаем текстуру
                texture_path = os.path.join(tileset_path, filename)
                try:
                    texture = self.rm.load_texture(texture_path)

                    # Сохраняем тайл
                    self.tiles[tile_id] = {
                        'texture': texture,
                        'solid': solid,
                        'filename': filename
                    }

                    self.logger.debug(f"Загружен тайл {tile_id}: {filename} (solid: {solid})")

                except Exception as e:
                    self.logger.error(f"Ошибка загрузки текстуры {filename}: {e}")
                    # Создаем пустой тайл
                    self.tiles[tile_id] = {
                        'texture': None,
                        'solid': solid,
                        'filename': filename
                    }

                tile_id += 1

            self.logger.info(f"Загружено тайлов: {len(self.tiles)}")

        except FileNotFoundError:
            self.logger.error(f"Файл данных не найден: {data_path}")
            raise
        except Exception as e:
            self.logger.exception(f"Ошибка загрузки тайлов: {e}")
            raise

    def get_tile(self, tile_id):
        """Возвращает информацию о тайле по ID"""
        return self.tiles.get(tile_id)

    def is_solid(self, tile_id):
        """Проверяет, есть ли у тайла коллизия"""
        tile = self.get_tile(tile_id)
        return tile['solid'] if tile else False

    def draw_tile(self, tile_id, x, y):
        """
        Рисует тайл в указанных координатах.
        Координаты - центр тайла.
        """
        tile = self.get_tile(tile_id)
        if tile and tile['texture']:
            arcade.draw_texture_rect(
                tile['texture'],
                arcade.rect.XYWH(
                x, y,
                self.tile_size, self.tile_size)

            )
        else:
            # Рисуем placeholder для отсутствующих тайлов
            self.logger.warning(f"Тайл {tile_id} не найден, рисую placeholder")
            arcade.draw_rect_filled(
                arcade.rect.XYWH(
                x, y,
                self.tile_size, self.tile_size),
                arcade.color.RED
            )
            arcade.draw_text(
                str(tile_id),
                x, y,
                arcade.color.WHITE, 8,
                anchor_x="center", anchor_y="center"
            )