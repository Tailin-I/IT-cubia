import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.world.tilemanager import TileManager
from src.core.resource_manager import resource_manager


def test_tile_manager():
    print("Тестирование TileManager с ResourceManager...")

    # Создаем менеджер
    tm = TileManager(original_tile_size=16, tile_scale=4)

    # Основная информация
    print(f"\nОсновная информация:")
    print(f"Загружено тайлов: {tm.get_tile_count()}")
    print(f"Размер тайла: {tm.tile_size}px")

    # Проверяем пути ResourceManager
    print(f"\nПроверка ResourceManager:")
    print(f"Корень проекта: {resource_manager.get_project_root()}")

    # Пример пути
    test_path = "tiles/001.png"
    full_path = resource_manager.get_resource_path(test_path)
    print(f"Путь к тайлу 001: {full_path}")
    print(f"Файл существует: {os.path.exists(full_path)}")

    # Тестируем получение тайлов
    print(f"\nТестируем получение тайлов:")

    test_tiles = [0, 1, 32, 17, 64, 100]

    for tile_num in test_tiles:
        texture = tm.get_tile_texture(tile_num)
        has_collision = tm.has_collision(tile_num)
        info = tm.get_tile_info(tile_num)

        if texture:
            print(f"Тайл #{tile_num:03d}: {info['name']}, коллизия={has_collision}")
        else:
            print(f"Тайл #{tile_num:03d}: не найден")

    # Отладочная информация
    print(f"\n{tm.debug_info()}")

    print("\nТестирование завершено!")


if __name__ == "__main__":
    test_tile_manager()