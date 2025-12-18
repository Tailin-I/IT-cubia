import logging


class CollisionSystem:
    """Система проверки и разрешения коллизий"""

    logger = logging.getLogger(__name__)

    @staticmethod
    def check_map_collision(entity, game_map, dx=0, dy=0):
        """
        Проверяет коллизии сущности с картой при заданном смещении.

        Args:
            entity: Сущность для проверки
            game_map: Карта игры
            dx, dy: Смещение для проверки

        Returns:
            (can_move_x, can_move_y) - можно ли двигаться по X и Y
        """
        if not entity.hitbox:
            # Если хитбокса нет - разрешаем движение
            return True, True

        # Получаем углы хитбокса
        corners = entity.hitbox.get_corners()

        can_move_x = True
        can_move_y = True

        # Проверяем каждый угол с учетом смещения
        for corner_x, corner_y in corners:
            # Проверка по X
            if dx != 0:
                future_x = corner_x + dx
                if game_map.is_solid_at_pixel(future_x, corner_y):
                    can_move_x = False
                    CollisionSystem.logger.debug(f"Коллизия по X в точке ({future_x}, {corner_y})")

            # Проверка по Y
            if dy != 0:
                future_y = corner_y + dy
                if game_map.is_solid_at_pixel(corner_x, future_y):
                    can_move_y = False
                    CollisionSystem.logger.debug(f"Коллизия по Y в точке ({corner_x}, {future_y})")

        return can_move_x, can_move_y

    @staticmethod
    def resolve_map_collision(entity, game_map, dx, dy):
        """
        Разрешает коллизии с картой, возвращая разрешенное смещение.
        Использует метод "скольжения" вдоль стен.

        Args:
            entity: Сущность
            game_map: Карта игры
            dx, dy: Запланированное смещение

        Returns:
            (actual_dx, actual_dy) - разрешенное смещение
        """
        # Сначала проверяем движение по X
        can_move_x, _ = CollisionSystem.check_map_collision(entity, game_map, dx, 0)
        if can_move_x:
            entity.center_x += dx
            actual_dx = dx
        else:
            actual_dx = 0

        # Затем проверяем движение по Y
        _, can_move_y = CollisionSystem.check_map_collision(entity, game_map, 0, dy)
        if can_move_y:
            entity.center_y += dy
            actual_dy = dy
        else:
            actual_dy = 0

        return actual_dx, actual_dy

    @staticmethod
    def check_entity_collision(entity1, entity2):
        """
        Проверяет коллизию между двумя сущностями.

        Args:
            entity1, entity2: Сущности для проверки

        Returns:
            bool: Есть ли коллизия
        """
        if not entity1.collision_enabled or not entity2.collision_enabled:
            return False

        if not entity1.collides_with_entities or not entity2.collides_with_entities:
            return False

        # Получаем прямоугольники коллизий
        left1, bottom1, right1, top1 = entity1.get_collision_rect()
        left2, bottom2, right2, top2 = entity2.get_collision_rect()

        # Проверяем пересечение
        return not (right1 < left2 or left1 > right2 or
                    top1 < bottom2 or bottom1 > top2)