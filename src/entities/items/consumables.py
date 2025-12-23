from .base_item import Item


class HealingPotion(Item):
    """Целебное зелье"""

    def __init__(self, count: int = 1):
        super().__init__(

            item_id="healing_potion",
            name="Целебное зелье",
            texture_path="res/consumables/potion_red.png"
        )
        self.count = count
        self.is_consumable = True
        self.heal_amount = 50
        self.description = f"Восстанавливает {self.heal_amount} здоровья"

    def use(self, user) -> bool:
        if user.health < user.max_health:
            heal_amount = min(self.heal_amount, user.max_health - user.health)
            user.health += heal_amount
            self.count -= 1
            print(f"💚 {user.name} восстановил {heal_amount} HP")
            return True  # Предмет израсходован
        print(f"❤️ У {user.name} и так полное здоровье")
        return False


class ManaPotion(Item):
    """Зелье маны"""

    def __init__(self, count: int = 1):
        super().__init__(
            item_id="mana_potion",
            name="Зелье маны",
            texture_path="res/consumables/manacrystal_full.png"
        )
        self.count = count
        self.is_consumable = True
        self.restore_amount = 30
        self.description = f"Восстанавливает {self.restore_amount} маны"

    def use(self, user) -> bool:
        # Если у игрока есть мана
        if hasattr(user, 'mana'):
            if user.mana < user.max_mana:
                restore = min(self.restore_amount, user.max_mana - user.mana)
                user.mana += restore
                self.count -= 1
                print(f"🔵 {user.name} восстановил {restore} маны")
                return True
        return False
