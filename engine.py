# Game rules only. Narrative text and balance numbers are loaded from content.py.

import random

from content import (
    ACTIONS,
    ACTION_ENEMY_MAP,
    BATTLE_FAILURE_PENALTY,
    BOSS_DAY,
    DAY_STORIES,
    DAY_TRANSITIONS,
    ENDING_MESSAGES,
    ENEMIES,
    EVENTS,
    FINAL_ENDING_THRESHOLDS,
    ITEMS,
    MAX_INVENTORY_SIZE,
    PERSONA_ACTION_FLAVOUR,
    PERSONAS,
    SKILLS,
)
from models import Enemy, GameResult, GameState, Player

AUTO_PAGE_PREFIX = "[[AUTO]] "


class GameEngine:
    def __init__(self, state: GameState | None = None) -> None:
        self.state = state or GameState()
        self._last_event_id: str | None = None

    def new_game(self, player_name: str = "Student", persona_id: str = "balanced") -> GameResult:
        persona = PERSONAS.get(persona_id, PERSONAS["balanced"])
        player = Player(
            name=player_name.strip() or "Student",
            persona=persona_id,
            **persona["stats"],
        )
        self.state = GameState(player=player)
        self._last_event_id = None
        intro = (
            f"Welcome, {player.name}.\n\n"
            f"You are playing as: {persona['label']}.\n"
            f"{persona['description']}\n\n"
            f"{DAY_STORIES[1]}\n\n"
            "Survive five days, keep stress under control, "
            "and prepare for the Final Exam Dragon.\n\n"
            "Today is Day 1. What should you do first?"
        )
        return GameResult(intro, self.state)

    def perform_action(self, action_id: str) -> GameResult:
        if self.state.game_over:
            return GameResult("The game is over. Start a new game to play again.", self.state)
        if self.state.in_battle:
            return GameResult("You must finish the current battle first.", self.state)
        if self.state.pending_event:
            return GameResult("Resolve the current event first.", self.state)
        if self.state.pending_encounter:
            return GameResult("Resolve the current encounter first.", self.state)
        if action_id not in ACTIONS:
            return GameResult("That action is not available.", self.state)

        action = ACTIONS[action_id]
        self.state.last_action = action.get("scene", action_id)
        self.state.last_animation = action.get("scene", action_id)
        self.state.player.apply_effects(action["effects"])

        messages = [
            f"Day {self.state.day}: {DAY_STORIES.get(self.state.day, DAY_STORIES[BOSS_DAY])}",
            action["message"],
            self._persona_flavour(action_id),
            self._auto_page(self._format_effects(action["effects"])),
        ]

        if self._check_loss_condition():
            return GameResult(_join(messages + [self._ending_message()]), self.state)

        event_page, event_result, event_effects, event_animation = self._roll_event(action)
        self.state.pending_event = {
            "event_page": event_page,
            "result": event_result,
            "effects": event_effects,
            "animation": event_animation,
            "action_id": action_id,
        }
        messages.append(event_page)
        messages.append("Event ready. Continue to resolve its outcome.")
        return GameResult(_join(messages), self.state)

    def start_battle(self, enemy_id: str) -> GameResult:
        data = ENEMIES[enemy_id]
        self.state.current_enemy = Enemy(
            enemy_id=enemy_id,
            name=data["name"],
            max_hp=data["hp"],
            attack=data["attack"],
            moves=data["moves"],
            reward=data["reward"],
        )
        self.state.battle_turn = 1
        return GameResult(f"A wild {self.state.current_enemy.name} appears!", self.state)

    def start_pending_battle(self) -> GameResult:
        if self.state.pending_encounter is None:
            return GameResult("There is no encounter waiting.", self.state)
        enemy_id = self.state.pending_encounter["enemy_id"]
        self.state.pending_encounter = None
        return self.start_battle(enemy_id)

    def use_skill(self, skill_id: str) -> GameResult:
        if not self.state.in_battle or self.state.current_enemy is None:
            return GameResult("There is no enemy to fight right now.", self.state)
        if skill_id not in SKILLS:
            return GameResult("That move is not available.", self.state)

        skill = SKILLS[skill_id]
        player = self.state.player
        enemy = self.state.current_enemy

        if skill_id != "drink_coffee" and player.energy <= 0:
            return GameResult("You are too tired to move.", self.state)

        player.apply_effects(skill["effects"])
        damage, missed = self._calculate_damage(skill)

        player_pages = [f"You use {skill['label']}.", skill["message"]]

        if missed:
            self.state.last_animation = "miss"
            player_pages.append(skill.get("miss_message", "The move misses."))
        elif damage > 0:
            self.state.last_animation = "player"
            enemy.hp = max(0, enemy.hp - damage)
            player_pages.append(self._auto_page(f"You deal {damage} damage to {enemy.name}."))
        else:
            self.state.last_animation = "support"
            player_pages.append(self._auto_page(self._format_effects(skill["effects"])))
            if skill["effects"].get("focus", 0) > 0:
                bonus = self.state.player.focus * 4
                player_pages.append(
                    self._auto_page(
                        f"Focus is now {self.state.player.focus}. "
                        f"Your next damaging skill gains +{bonus} bonus damage."
                    )
                )

        if enemy.is_defeated:
            return GameResult(_join(player_pages + [self._finish_battle()]), self.state)

        enemy_page = self._enemy_attack()
        settle_page = self._turn_settlement()

        if self._check_loss_condition():
            settle_page = _join([settle_page, self._ending_message()])

        return GameResult(_join(player_pages + [enemy_page, settle_page]), self.state)

    def use_item(self, item_id: str) -> GameResult:
        if not self.state.in_battle or self.state.current_enemy is None:
            return GameResult("You can only use items during battle.", self.state)
        if item_id not in self.state.inventory:
            return GameResult("That item is not in your inventory.", self.state)

        item = ITEMS.get(item_id)
        if item is None:
            return GameResult("This item is unavailable.", self.state)

        self.state.inventory.remove(item_id)
        self.state.player.apply_effects(item["effects"])
        self.state.last_animation = "support"
        return GameResult(
            _join(
                [
                    f"You use {item['label']}.",
                    item["description"],
                    self._auto_page(self._format_effects(item["effects"])),
                ]
            ),
            self.state,
        )

    def forfeit_battle(self) -> GameResult:
        if not self.state.in_battle:
            return GameResult("There is no battle to forfeit.", self.state)

        self.state.current_enemy = None
        self.state.battle_turn = 0
        self.state.player.apply_effects(BATTLE_FAILURE_PENALTY)
        messages = [
            "You fail the battle and retreat.",
            self._auto_page(self._format_effects(BATTLE_FAILURE_PENALTY)),
        ]
        if self._check_loss_condition():
            messages.append(self._ending_message())
            return GameResult(_join(messages), self.state)
        self._advance_day(messages)
        return GameResult(_join(messages), self.state)

    def forfeit_pending_encounter(self) -> GameResult:
        if self.state.pending_encounter is None:
            return GameResult("There is no encounter to forfeit.", self.state)
        self.state.pending_encounter = None
        self.state.player.apply_effects(BATTLE_FAILURE_PENALTY)
        messages = [
            "You avoid the fight and move on.",
            self._auto_page(self._format_effects(BATTLE_FAILURE_PENALTY)),
        ]
        if self._check_loss_condition():
            messages.append(self._ending_message())
            return GameResult(_join(messages), self.state)
        self._advance_day(messages)
        return GameResult(_join(messages), self.state)

    def resolve_event(self, choice_id: str) -> GameResult:
        _ = choice_id
        if self.state.pending_event is None:
            return GameResult("There is no event to resolve.", self.state)
        if self.state.in_battle:
            return GameResult("Finish the current battle first.", self.state)

        data = self.state.pending_event
        self.state.pending_event = None

        effects = data["effects"]
        self.state.last_animation = data.get("animation", "event")
        self.state.player.apply_effects(effects)

        messages = [
            data["result"],
            self._auto_page(self._format_effects(effects)),
        ]

        if self._check_loss_condition():
            return GameResult(_join(messages + [self._ending_message()]), self.state)

        if self.state.day == BOSS_DAY:
            self.state.pending_encounter = {
                "enemy_id": "final_exam",
                "label": ENEMIES["final_exam"]["name"],
            }
            self.state.last_animation = "enemy"
            messages.append(
                "Final day: no more detours. The exam hall is waiting, and this is the last fight."
            )
            messages.append(self._encounter_preview("final_exam"))
            messages.append("No way around it. Step in and fight.")
            return GameResult(_join(messages), self.state)

        action_id = data["action_id"]
        enemy_id = ACTION_ENEMY_MAP[action_id]
        self.state.pending_encounter = {
            "enemy_id": enemy_id,
            "label": ENEMIES[enemy_id]["name"],
        }
        self.state.last_animation = "enemy"
        messages.append(self._encounter_preview(enemy_id))
        messages.append("Choose to fight or forfeit.")
        return GameResult(_join(messages), self.state)

    def available_actions(self) -> dict[str, str]:
        return {aid: a["label"] for aid, a in ACTIONS.items()}

    def available_skills(self) -> dict[str, str]:
        return {sid: s["label"] for sid, s in SKILLS.items()}

    def available_event_choices(self) -> dict[str, str]:
        return {}

    def _roll_event(self, action: dict) -> tuple[str, str, dict[str, int], str]:
        pool = action.get("event_pool", list(EVENTS))
        candidates = [event_id for event_id in pool if event_id != self._last_event_id] or pool
        event_id = random.choice(candidates)
        self._last_event_id = event_id

        event = EVENTS[event_id]
        _choice_id, choice = random.choice(list(event["choices"].items()))
        effects = choice.get("effects", {})
        event_page = f"Story event: {event['title']}\n\n{event['message']}"
        return event_page, choice["result"], effects, event.get("animation", "event")

    def _calculate_damage(self, skill: dict) -> tuple[int, bool]:
        if "hit_chance" in skill and random.random() > skill["hit_chance"]:
            return 0, True

        base = skill.get("damage", 0)
        focus_bonus = self.state.player.focus * 4 if base > 0 else 0
        if base > 0:
            self.state.player.focus = 0
        return base + focus_bonus, False

    def _enemy_attack(self) -> str:
        player = self.state.player
        enemy = self.state.current_enemy
        if enemy is None:
            return ""

        move = random.choice(enemy.moves)
        stress_hit = move.get("stress", enemy.attack)
        energy_hit = abs(move.get("energy", max(2, enemy.attack // 2)))
        player.apply_effects({"stress": stress_hit, "energy": -energy_hit})
        self.state.battle_turn += 1
        self.state.last_animation = "enemy"

        return self._auto_page(
            (
            f"{enemy.name} uses {move['name']}: {move['description']}.\n"
            f"You lose {energy_hit} energy and gain {stress_hit} stress."
            )
        )

    def _turn_settlement(self) -> str:
        player = self.state.player
        return self._auto_page(
            f"Turn result: Energy {player.energy}, Stress {player.stress}, "
            f"Knowledge {player.knowledge}, Money ${player.money}, Focus {player.focus}."
        )

    def _finish_battle(self) -> str:
        enemy = self.state.current_enemy
        if enemy is None:
            return ""

        self.state.player.apply_effects(enemy.reward)
        reward_text = self._format_effects(enemy.reward)
        enemy_name = enemy.name
        enemy_id = enemy.enemy_id
        self.state.current_enemy = None
        self.state.battle_turn = 0

        if enemy_id == "final_exam":
            self._resolve_final_ending()
            return f"You defeat {enemy_name}!\n{self._auto_page(reward_text)}\n\n{self._ending_message()}"

        messages = [f"You defeat {enemy_name}!", self._auto_page(reward_text), self._auto_page(self._grant_item_drop(enemy_id))]
        self._advance_day(messages)
        return _join(messages)

    def _grant_item_drop(self, enemy_id: str) -> str:
        drops = ENEMIES[enemy_id].get("item_drop")
        if not drops:
            return "No item dropped."
        item_id = random.choice(drops)
        if len(self.state.inventory) >= MAX_INVENTORY_SIZE:
            self.state.inventory.pop(0)
        self.state.inventory.append(item_id)
        return f"Item obtained: {ITEMS[item_id]['label']}."

    def _advance_day(self, messages: list[str]) -> None:
        self.state.day += 1
        self.state.last_animation = "day_transition"

        if self.state.day > BOSS_DAY:
            self._set_ending("deadline_missed")
            messages.append(self._ending_message())
        else:
            transition = DAY_TRANSITIONS.get(
                self.state.day, f"Day {self.state.day} begins."
            )
            messages.append(self._auto_page(transition))

    def _check_loss_condition(self) -> bool:
        player = self.state.player
        if player.energy <= 0:
            self._set_ending("burnout")
            return True
        if player.stress >= 100:
            self._set_ending("panic")
            return True
        return False

    def _resolve_final_ending(self) -> None:
        player = self.state.player
        hd = FINAL_ENDING_THRESHOLDS["high_distinction"]
        bb = FINAL_ENDING_THRESHOLDS["broke_but_brilliant"]

        if player.knowledge >= hd["min_knowledge"] and player.stress <= hd["max_stress"]:
            self._set_ending("high_distinction")
        elif player.money <= bb["max_money"] and player.knowledge >= bb["min_knowledge"]:
            self._set_ending("broke_but_brilliant")
        else:
            self._set_ending("barely_survived")

    def _set_ending(self, ending: str) -> None:
        self.state.ending = ending
        self.state.game_over = True
        self.state.last_animation = "idle"

    def _ending_message(self) -> str:
        return ENDING_MESSAGES.get(self.state.ending or "", "The story ends.")

    def _persona_flavour(self, action_id: str) -> str:
        flavour_map = PERSONA_ACTION_FLAVOUR.get(action_id, {})
        return flavour_map.get(self.state.player.persona, "")

    def _encounter_preview(self, enemy_id: str) -> str:
        data = ENEMIES[enemy_id]
        skills = ", ".join(move["name"] for move in data["moves"])
        drops = ", ".join(ITEMS[item]["label"] for item in data.get("item_drop", [])) or "No drop"
        return (
            f"Encounter: {data['name']}\n\n"
            f"Enemy skills: {skills}\n"
            f"Failure penalty: {self._format_effects(BATTLE_FAILURE_PENALTY)}\n"
            f"Possible drop: {drops}"
        )

    def _auto_page(self, text: str) -> str:
        return f"{AUTO_PAGE_PREFIX}{text}"

    def _format_effects(self, effects: dict[str, int]) -> str:
        if not effects:
            return ""
        preferred_order = ("energy", "stress", "knowledge", "money", "focus")
        ordered_keys = [key for key in preferred_order if key in effects]
        ordered_keys.extend(key for key in effects if key not in preferred_order)
        parts = [f"{stat.title()} {'+' if effects[stat] >= 0 else ''}{effects[stat]}" for stat in ordered_keys]
        return "Effects: " + ", ".join(parts)


def _join(parts: list[str]) -> str:
    """Join non-empty message parts with double newlines."""
    return "\n\n".join(p for p in parts if p)
