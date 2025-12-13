# Инициализация модуля world
from .tilemanager import TileManager, init_tile_manager, get_tile_manager, tile_manager

__all__ = [
    'TileManager',
    'init_tile_manager',
    'get_tile_manager',
    'tile_manager'
]