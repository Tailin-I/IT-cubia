from typing import Dict, Any

from  .event import GameEvent

class TeleportEvent(GameEvent):
    def __init__(self, event_id: str, rect: tuple, properties: Dict[str, Any]):
        super().__init__(event_id, "teleport", rect, properties)

        self.target_map = properties.get("target_map")
        self.target_x = properties.get("target_X", 0)
        self.target_y = properties.get("target_y", 0)

    def activate(self, player, game_state):
        if self.activated and self.cooldown > 0:
            return

        self.logger.info(f"перемещение на {self.target_map} x:{self.target_x} y{self.target_y}")

        if self.target_map:
            game_state.map_loader.load(f"maps/{self.target_map}.tmx")

        player.center_x = self.target_x
        player.center_y = self.target_y
        player.data.set_player_position(self.target_x, self.target_y)
        self.activated = True
        self.cooldown = self.max_cooldown