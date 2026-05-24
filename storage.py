import json
from pathlib import Path

from content import ENEMIES
from models import Enemy, GameState, Player


SAVE_FILE = Path(__file__).with_name("save_data.json")


def save_game(state: GameState, path: Path = SAVE_FILE) -> None:
    data = {
        "day": state.day,
        "player": vars(state.player),
        "current_enemy": _enemy_to_data(state.current_enemy),
        "pending_event": state.pending_event,
        "pending_encounter": state.pending_encounter,
        "last_animation": state.last_animation,
        "last_action": state.last_action,
        "battle_turn": state.battle_turn,
        "game_over": state.game_over,
        "ending": state.ending,
        "inventory": state.inventory,
    }
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_game(path: Path = SAVE_FILE) -> GameState:
    if not path.exists():
        raise FileNotFoundError("No saved game was found.")

    data = json.loads(path.read_text(encoding="utf-8"))
    player = Player(**data["player"])
    enemy = _enemy_from_data(data.get("current_enemy"))

    return GameState(
        day=data["day"],
        player=player,
        current_enemy=enemy,
        pending_event=data.get("pending_event"),
        pending_encounter=data.get("pending_encounter"),
        last_animation=data.get("last_animation", "idle"),
        last_action=data.get("last_action", "intro"),
        battle_turn=data["battle_turn"],
        game_over=data["game_over"],
        ending=data["ending"],
        inventory=data.get("inventory", []),
    )


def _enemy_to_data(enemy: Enemy | None) -> dict | None:
    if enemy is None:
        return None

    return {
        "enemy_id": enemy.enemy_id,
        "hp": enemy.hp,
    }


def _enemy_from_data(data: dict | None) -> Enemy | None:
    if data is None:
        return None

    enemy_config = ENEMIES[data["enemy_id"]]
    return Enemy(
        enemy_id=data["enemy_id"],
        name=enemy_config["name"],
        max_hp=enemy_config["hp"],
        attack=enemy_config["attack"],
        moves=enemy_config["moves"],
        reward=enemy_config["reward"],
        hp=data["hp"],
    )
