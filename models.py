from dataclasses import dataclass, field


@dataclass
class Player:
    name: str = "Student"
    persona: str = "balanced"
    energy: int = 80
    stress: int = 20
    money: int = 60
    knowledge: int = 10
    focus: int = 0

    def apply_effects(self, effects: dict[str, int]) -> None:
        for stat, change in effects.items():
            if not hasattr(self, stat):
                continue
            setattr(self, stat, getattr(self, stat) + change)

        self.energy = max(0, min(100, self.energy))
        self.stress = max(0, min(100, self.stress))
        self.money = max(0, self.money)
        self.knowledge = max(0, min(100, self.knowledge))
        self.focus = max(0, min(3, self.focus))


@dataclass
class Enemy:
    enemy_id: str
    name: str
    max_hp: int
    attack: int
    moves: list[dict]
    reward: dict[str, int]
    hp: int | None = None

    def __post_init__(self) -> None:
        if self.hp is None:
            self.hp = self.max_hp

    @property
    def is_defeated(self) -> bool:
        return self.hp is not None and self.hp <= 0


@dataclass
class GameState:
    day: int = 1
    player: Player = field(default_factory=Player)
    current_enemy: Enemy | None = None
    pending_event: dict | None = None
    pending_encounter: dict | None = None
    last_animation: str = "idle"
    last_action: str = "intro"
    battle_turn: int = 0
    game_over: bool = False
    ending: str | None = None
    inventory: list[str] = field(default_factory=list)

    @property
    def in_battle(self) -> bool:
        return self.current_enemy is not None and not self.game_over


@dataclass
class GameResult:
    message: str
    state: GameState
