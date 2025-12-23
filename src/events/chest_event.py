from typing import Dict, Any

from .event import GameEvent
from src.entities.items.item_factory import ItemFactory


class ChestEvent(GameEvent):
    """Событие сундука с добычей"""

    def __init__(self, event_id: str, rect: tuple, properties: Dict[str, Any]):
        super().__init__(event_id, "chest", rect, properties)

        # Парсим свойства
        self.lock_sequence = properties.get("lock", "")  # например "<<><"
        self.is_locked = len(self.lock_sequence) > 0
        self.is_opened = False
        self.player_sequence = ""

        # Добыча
        loot_str = properties.get("loot", "")
        self.loot_items = ItemFactory.parse_loot_string(loot_str)

        # Для отладки
        print(f"📦 Создан сундук {event_id}: "
              f"замок='{self.lock_sequence}', "
              f"предметов={len(self.loot_items)}")

    def activate(self, player, game_state):
        """Игрок взаимодействует с сундуком"""
        if self.activated and self.cooldown > 0:
            return

        print(f"📦 Взаимодействие с сундуком '{self.event_id}'")

        if self.is_opened:
            print("   Сундук уже пуст!")
            return

        if self.is_locked:
            print(f"🔒 Заперт! Комбинация: {self.lock_sequence}")
            # Открываем мини-игру взлома
            game_state.gsm.push_overlay("lock_picking",
                                        chest_event=self,
                                        player=player)
        else:
            self._open_chest(player)

        self.activated = True
        self.cooldown = self.max_cooldown

    def _open_chest(self, player):
        """Открыть сундук и выдать добычу"""
        print(f"🎉 Сундук открыт! Получено:")

        for item in self.loot_items:
            # Добавляем в инвентарь игрока
            self._add_to_inventory(player, item)

        self.is_opened = True

    def _add_to_inventory(self, player, item):
        """Добавляет предмет в инвентарь игрока"""
        # Ищем, есть ли уже такой предмет
        found = False
        for inv_item in player.data.inventory["items"]:
            if inv_item.get("id") == item.item_id and item.is_stackable:
                inv_item["count"] += item.count
                found = True
                break

        if not found:
            player.data.inventory["items"].append({
                "id": item.item_id,
                "name": item.name,
                "count": item.count,
                "stackable": item.is_stackable
            })

        print(f"   +{item.count} {item.name}")

    def check_lock_attempt(self, direction: str) -> tuple:
        """
        Проверяет попытку взлома.
        Возвращает: (успех, завершено, текущая_последовательность)
        """
        self.player_sequence += direction

        # Если ввели достаточно символов
        if len(self.player_sequence) == len(self.lock_sequence):
            if self.player_sequence == self.lock_sequence:
                return True, True, self.player_sequence  # Успех!
            else:
                self.player_sequence = ""  # Сбрасываем
                return False, True, ""  # Неудача

        # Еще вводим
        return None, False, self.player_sequence
