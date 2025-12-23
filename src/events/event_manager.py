import arcade

from .event import GameEvent
from .chest_event import ChestEvent
from .teleport_event import TeleportEvent


class EventManager:
    def __init__(self, rm):
        self.events = []
        self.rm = rm
        self.tileSize = 70
        self.chest_sprites = arcade.SpriteList()

    def load_from_tiled(self, object_list, scale: float = 1.0):
        """Загружает события из списка объектов Tiled"""
        print(f"=== ЗАГРУЗКА {len(object_list)} СОБЫТИЙ ===")

        for i, obj in enumerate(object_list):
            print(f"\n🔍 Обрабатываю объект {i}:")
            print(f"   name: {getattr(obj, 'name', 'без имени')}")
            print(f"   type: {getattr(obj, 'type', 'не указан')}")
            print(f"   shape: {getattr(obj, 'shape', 'нет')}")

            properties = getattr(obj, 'properties', {})
            print(f"   properties: {properties}")

            # Создаем событие
            event = self._create_event_from_object(obj, properties, scale, i)
            if event:
                self.events.append(event)

        print(f"\n✅ Всего загружено событий: {len(self.events)}")
        for i, obj in enumerate(object_list):
            print(f"Объект {i}:")
            print(f"  Все атрибуты: {[attr for attr in dir(obj) if not attr.startswith('_')]}")
            print(f"  Тип: {type(obj)}")

    def _create_event_from_object(self, obj, properties, scale, index):
        """Создает событие из TiledObject"""
        try:
            # Извлекаем координаты из shape
            if not hasattr(obj, 'shape') or not obj.shape:
                print(f"⚠️ Объект {index} не имеет shape")
                return None

            points = obj.shape
            if len(points) < 2:
                print(f"⚠️ Объект {index} имеет недостаточно точек в shape")
                return None

            # Вычисляем bounding box
            xs = [p[0] for p in points]
            ys = [p[1] for p in points]

            x = min(xs)
            y = min(ys)

            width = max(xs) - min(xs)
            height = max(ys) - min(ys)

            # Масштабируем
            x *= scale
            y *= scale
            width *= scale
            height *= scale

            # Определяем тип события
            event_type = obj.type.lower() if hasattr(obj, 'type') else "trigger"
            event_id = properties.get("id", f"{event_type}_{index}")

            print(f"   📏 Размеры: {width:.0f}x{height:.0f} в ({x:.0f}, {y:.0f})")

            # Создаем соответствующее событие
            if event_type == "chest":
                tile_x = properties.get("tile_x", x) * self.tileSize
                tile_y = properties.get("tile_y", y) * self.tileSize
                container = properties.get("type", "chest")
                # Сундук
                if "loot" not in properties:
                    properties["loot"] = ""  # Тестовый лут
                event = ChestEvent(event_id, (x, y, width, height), properties)

                if container == "chest":
                    from src.entities.chest import ChestSprite
                    texture = self.rm.load_texture("containers/chest.png")
                    texture_opened = self.rm.load_texture("containers/chest_opened.png")
                    sprite = ChestSprite(texture,texture_opened, tile_x, tile_y,properties)
                    event.set_sprite(sprite)
                    self.chest_sprites.append(sprite)

                return event

            elif event_type == "teleport":
                # Телепорт
                return TeleportEvent(event_id, (x, y, width, height), properties)

            elif event_type == "trigger":
                # Простой триггер
                return GameEvent(event_id, "trigger", (x, y, width, height), properties)

            else:
                # Неизвестный тип - создаем как GameEvent
                print(f"⚠️ Неизвестный тип события: {event_type}")
                return GameEvent(event_id, event_type, (x, y, width, height), properties)

        except Exception as e:
            print(f"❌ Ошибка создания события из объекта {index}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def draw(self):
        self.chest_sprites.draw()
    def update(self, delta_time: float):
        """Обновляет все события"""
        for event in self.events:
            event.update(delta_time)

    def check_collisions(self, player, game_state):
        """Проверяет столкновения игрока со всеми событиями"""
        if not player:
            return

        player_rect = (
            player.center_x - player.width / 2,
            player.center_y - player.height / 2,
            player.width,
            player.height
        )

        for event in self.events:
            if event.check_collision(player_rect):
                event.activate(player, game_state)

    def draw_debug(self):
        """Отрисовывает события для отладки"""
        for event in self.events:
            x, y, width, height = event.rect

            # Цвет в зависимости от типа и состояния
            if event.type == "chest":
                color = arcade.color.GOLD if not event.is_opened else arcade.color.GRAY
            elif event.type == "teleport":
                color = arcade.color.CYAN
            else:
                color = arcade.color.GREEN

            # Рисуем прямоугольник
            arcade.draw_rect_outline(
                arcade.rect.XYWH(x + width / 2, y + height / 2, width, height),
                color, 2
            )

            # Подпись
            arcade.draw_text(
                event.type,
                x + width / 2, y + height / 2,
                arcade.color.WHITE, 10,
                anchor_x="center", anchor_y="center"
            )
