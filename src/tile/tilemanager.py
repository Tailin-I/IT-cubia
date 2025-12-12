import os
import logging
from typing import Dict, Optional, List

import arcade

from src.core.resource_manager import resource_manager


class TileManager:
    """
    Менеджер для загрузки и управления тайлами.
    Использует ResourceManager для загрузки текстур.
    """

    def __init__(self, original_tile_size: int = 16, tile_scale: int = 4):
        """
        Инициализация менеджера тайлов.

        Args:
            original_tile_size: Исходный размер тайлов в пикселях
            tile_scale: Масштаб для увеличения тайлов
        """
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        self.logger.info("Инициализация TileManager...")

        # Параметры масштабирования
        self.original_tile_size = original_tile_size
        self.tile_scale = tile_scale
        self.tile_size = original_tile_size * tile_scale  # Итоговый размер

        # Используем ResourceManager
        self.resource_manager = resource_manager

        # Словари для хранения данных
        self.textures: Dict[int, arcade.Texture] = {}  # номер -> текстура
        self.collisions: Dict[int, bool] = {}  # номер -> есть коллизия?
        self.tile_names: Dict[int, str] = {}  # номер -> имя файла

        # Счетчики
        self.loaded_count = 0
        self.collision_count = 0

        # Загружаем тайлы и данные о коллизии
        self._load_tiles_from_folder()
        self._load_collision_data()

        self.logger.info(f"TileManager готов. Загружено тайлов: {self.loaded_count}")

    def _load_tiles_from_folder(self):
        """Загружает все тайлы из папки res/tiles/ используя ResourceManager"""
        tiles_dir = "tiles"

        # Получаем список всех возможных тайлов (от 000 до 999)
        # Сначала попробуем загрузить существующие

        for tile_num in range(1000):  # До 999
            # Форматируем номер с ведущими нулями
            filename = f"{tile_num:03d}.png"
            relative_path = os.path.join(tiles_dir, filename)

            # Пытаемся загрузить через ResourceManager
            try:
                # Проверяем существует ли файл через ResourceManager
                full_path = self.resource_manager.get_resource_path(relative_path)

                if os.path.exists(full_path):
                    # Загружаем текстуру
                    texture = self.resource_manager.load_texture(relative_path)

                    # Сохраняем данные
                    self.textures[tile_num] = texture
                    self.tile_names[tile_num] = filename
                    self.loaded_count += 1

                    self.logger.debug(f"Загружен тайл: #{tile_num:03d} ({filename})")
                else:
                    # Файл не существует, пропускаем
                    continue

            except Exception as e:
                self.logger.warning(f"Ошибка загрузки тайла {filename}: {e}")
                continue

        self.logger.info(f"Успешно загружено тайлов: {self.loaded_count}")

    def _load_collision_data(self):
        """Загружает данные о коллизии из tiledata.txt"""
        tiledata_path = "maps/tiledata.txt"

        try:
            # Получаем полный путь через ResourceManager
            full_path = self.resource_manager.get_resource_path(tiledata_path)

            if not os.path.exists(full_path):
                self.logger.warning(f"Файл с данными о коллизии не найден: {full_path}")
                self.logger.info("Будут использованы значения по умолчанию (все тайлы без коллизии)")
                return

            self.logger.info(f"Загрузка данных о коллизии из: {tiledata_path}")

            with open(full_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]

            # Проверяем четность количества строк
            if len(lines) % 2 != 0:
                self.logger.warning(f"Нечетное количество строк в {tiledata_path}")

            # Обрабатываем строки попарно: имя файла -> true/false
            for i in range(0, len(lines), 2):
                if i + 1 >= len(lines):
                    break

                filename = lines[i]
                collision_str = lines[i + 1]

                # Извлекаем номер тайла из имени файла
                try:
                    # Удаляем .png и преобразуем в число
                    tile_number = int(filename.replace('.png', ''))
                except ValueError:
                    self.logger.warning(f"Неверный формат имени файла в tiledata.txt: {filename}")
                    continue

                # Преобразуем строку в булево значение
                has_collision = False
                if collision_str.lower() == "true":
                    has_collision = True
                    self.collision_count += 1
                elif collision_str.lower() == "false":
                    has_collision = False
                else:
                    self.logger.warning(f"Неверное значение коллизии для {filename}: {collision_str}")
                    continue

                # Сохраняем
                self.collisions[tile_number] = has_collision

                # Проверяем, загружен ли тайл
                if tile_number not in self.textures:
                    self.logger.debug(f"Тайл #{tile_number} упомянут в tiledata.txt, но не загружен")

            self.logger.info(f"Загружено данных о коллизии для {len(self.collisions)} тайлов")
            self.logger.info(f"Тайлов с коллизией: {self.collision_count}")

        except Exception as e:
            self.logger.error(f"Ошибка при загрузке данных о коллизии: {e}")

    # Остальные методы остаются без изменений...
    def get_tile_texture(self, tile_number: int) -> Optional[arcade.Texture]:
        """Возвращает текстуру тайла по номеру."""
        return self.textures.get(tile_number)

    def has_collision(self, tile_number: int) -> bool:
        """Проверяет, имеет ли тайл коллизию."""
        return self.collisions.get(tile_number, False)

    def get_tile_info(self, tile_number: int) -> Dict:
        """Возвращает полную информацию о тайле."""
        return {
            'number': tile_number,
            'name': self.tile_names.get(tile_number, 'Unknown'),
            'has_texture': tile_number in self.textures,
            'has_collision': self.has_collision(tile_number),
            'original_size': self.original_tile_size,
            'scaled_size': self.tile_size
        }

    def get_all_tile_numbers(self) -> List[int]:
        """Возвращает список всех загруженных номеров тайлов."""
        return sorted(list(self.textures.keys()))

    def get_tile_count(self) -> int:
        """Возвращает количество загруженных тайлов."""
        return self.loaded_count

    def debug_info(self) -> str:
        """Возвращает отладочную информацию о менеджере."""
        return (
            f"TileManager Debug Info:\n"
            f"  Загружено тайлов: {self.loaded_count}\n"
            f"  Размер тайла: {self.original_tile_size} -> {self.tile_size}px\n"
            f"  Масштаб: {self.tile_scale}\n"
            f"  Тайлов с коллизией: {self.collision_count}\n"
            f"  Диапазон номеров: {min(self.textures.keys()) if self.textures else 0} "
            f"- {max(self.textures.keys()) if self.textures else 0}"
        )


# Глобальный экземпляр для удобного доступа
tile_manager: Optional[TileManager] = None


def init_tile_manager(original_tile_size: int = 16, tile_scale: int = 4) -> TileManager:
    """Инициализирует глобальный TileManager."""
    global tile_manager
    tile_manager = TileManager(original_tile_size, tile_scale)
    return tile_manager


def get_tile_manager() -> TileManager:
    """Возвращает глобальный TileManager (инициализирует если нужно)."""
    global tile_manager
    if tile_manager is None:
        tile_manager = TileManager()
    return tile_manager