import arcade
from .hitbox_component import HitboxComponent  # Добавляем импорт
from ..core.resource_manager import ResourceManager


class Entity(arcade.Sprite):
    """Главный класс для всех сущностей"""

    def __init__(self, texture_list, scale):
        super().__init__(texture_list[0], scale)

        self.rm = ResourceManager()

        self.time_elapsed = 0  # задержка времени для анимации

        # Базовые параметры
        self.speed = 0
        self.health = 100
        self.is_alive = True
        self.direction = "down"

        # Инициализируем текстуры для анимации
        self.textures = texture_list
        self.cur_texture_index = 0

        # КОЛЛИЗИИ
        self.hitbox = None  # Компонент хитбокса
        self.collision_enabled = True  # Включены ли коллизии
        self.collides_with_map = True  # Коллизии с картой
        self.collides_with_entities = True  # Коллизии с другими сущностями

    def setup_hitbox(self, offsets=None):
        """
        Настраивает хитбокс с указанными отступами.

        Args:
            offsets: Словарь с отступами {'left': -0.1, 'right': -0.1, 'top': -0.2, 'bottom': -0.1}
                    или просто число для всех сторон
        """
        if isinstance(offsets, (int, float)):
            # Если передано одно число - применяем ко всем сторонам
            offsets = {
                'left': offsets,
                'right': offsets,
                'top': offsets,
                'bottom': offsets
            }

        self.hitbox = HitboxComponent(self, offsets)

    def get_collision_rect(self):
        """
        Возвращает прямоугольник для проверки коллизий.
        Если хитбокс не настроен - использует bounding box спрайта.
        """
        if self.hitbox:
            return self.hitbox.get_rect()
        else:
            # Используем bounding box спрайта
            return (
                self.center_x - self.width / 2,
                self.center_y - self.height / 2,
                self.center_x + self.width / 2,
                self.center_y + self.height / 2
            )

    def check_map_collision(self, game_map, dx=0, dy=0):
        """
        Проверяет коллизии с картой.

        Args:
            game_map: Объект GameMap
            dx, dy: Смещение для проверки (движение которое планируем сделать)

        Returns:
            (can_move_x, can_move_y) - можно ли двигаться по X и Y
        """
        if not self.collision_enabled or not self.collides_with_map:
            return True, True

        from src.systems.collision_system import CollisionSystem  # Ленивый импорт
        return CollisionSystem.check_map_collision(self, game_map, dx, dy)

    def move_with_collision(self, game_map, dx, dy):
        """
        Двигает сущность с учетом коллизий с картой.

        Args:
            game_map: Объект GameMap
            dx, dy: Запланированное смещение

        Returns:
            (actual_dx, actual_dy) - реальное смещение после учета коллизий
        """
        if not self.collision_enabled or not self.collides_with_map:
            self.center_x += dx
            self.center_y += dy
            return dx, dy

        from src.systems.collision_system import CollisionSystem  # Ленивый импорт
        return CollisionSystem.resolve_map_collision(self, game_map, dx, dy)

    def update(self, delta_time: float = 1 / 60, *args, **kwargs) -> None:
        """Базовое обновление - можно переопределять в дочерних классах"""
        pass

    def draw_debug(self):
        """Отрисовывает отладочную информацию (хитбокс)"""
        if self.hitbox:
            self.hitbox.draw_debug()