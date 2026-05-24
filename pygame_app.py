from pathlib import Path

import pygame

from content import ACTIONS, INTRO_STORY_PAGES, ITEMS, PERSONAS, SKILLS
from engine import AUTO_PAGE_PREFIX, GameEngine
from storage import load_game, save_game


WIDTH = 1120
HEIGHT = 720
ASSET_DIR = Path(__file__).with_name("pixel_assets")
SCENE_RECT = pygame.Rect(282, 18, 820, 388)
MESSAGE_PANEL_RECT = pygame.Rect(282, 422, 820, 172)
CONTROLS_Y = 604

COLORS = {
    "bg": (26, 31, 38),
    "panel": (38, 48, 58),
    "panel_light": (58, 72, 84),
    "paper": (250, 241, 219),
    "paper_dark": (222, 207, 178),
    "ink": (31, 35, 42),
    "muted": (153, 172, 177),
    "gold": (244, 184, 77),
    "coral": (224, 91, 86),
    "mint": (95, 185, 158),
    "blue": (87, 144, 194),
    "red": (184, 74, 78),
    "green": (103, 162, 104),
    "white": (255, 255, 255),
    "black": (0, 0, 0),
}

SCENE_BY_ACTION = {
    "library": "library",
    "work": "work",
    "home": "dorm",
    "cafe": "cafe",
    "tutor": "tutor",
    "sleep": "night",
    "intro": "cover",
    "day_transition": "transition",
    "event_food": "cafe",
    "event_message": "dorm",
    "event_train": "night",
    "event_light": "library",
    "event_warning": "dorm",
    "event_exam": "library",
}


class Button:
    def __init__(self, rect: pygame.Rect, label: str, action: str, hint: str = "") -> None:
        self.rect = rect
        self.label = label
        self.action = action
        self.hint = hint

    def contains(self, pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)


class FinalsEscapePygame:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Finals Escape")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 22)
        self.font_small = pygame.font.SysFont("arial", 17)
        self.font_medium = pygame.font.SysFont("arial", 26, bold=True)
        self.font_large = pygame.font.SysFont("arial", 56, bold=True)
        self.assets = self._load_assets()

        self.engine = GameEngine()
        self.mode = "start_menu"
        self.create_step = 0
        self.player_name = "Alex"
        self.persona_id = "balanced"
        self.message = "Choose a student persona and begin finals week."
        self.page_queue: list[tuple[str, bool]] = []
        self.current_page_auto = False
        self.auto_page_timer = 0.0
        self.buttons: list[Button] = []
        self.active_input = True
        self.scene = "cover"
        self.effect = {"kind": "idle", "timer": 0}
        self.transition_timer = 0
        self.message_scroll = 0
        self.message_view_lines = 6
        self.message_panel_rect = MESSAGE_PANEL_RECT.copy()
        self.running = True

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(60) / 1000
            self._handle_events()
            self._update(dt)
            self._draw()
        pygame.quit()

    def _load_assets(self) -> dict[str, pygame.Surface]:
        assets = {}
        for path in ASSET_DIR.glob("*.png"):
            assets[path.stem] = pygame.image.load(path).convert_alpha()
        return assets

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self._handle_key(event)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_click(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button in (4, 5):
                if self.message_panel_rect.collidepoint(event.pos):
                    self._scroll_message(-1 if event.button == 4 else 1)
            elif event.type == pygame.MOUSEWHEEL:
                if self.message_panel_rect.collidepoint(pygame.mouse.get_pos()):
                    self._scroll_message(-event.y)

    def _handle_key(self, event: pygame.event.Event) -> None:
        if self.mode == "create_character" and self.create_step >= len(INTRO_STORY_PAGES):
            if event.key == pygame.K_BACKSPACE:
                self.player_name = self.player_name[:-1]
                return
            if event.key == pygame.K_RETURN:
                self._start_game()
                return
            if len(self.player_name) < 16 and event.unicode and event.unicode.isprintable():
                self.player_name += event.unicode
                return

        if self.mode != "start_menu":
            if event.key == pygame.K_UP:
                self._scroll_message(-1)
            elif event.key == pygame.K_DOWN:
                self._scroll_message(1)
            elif event.key == pygame.K_PAGEUP:
                self._scroll_message(-self.message_view_lines)
            elif event.key == pygame.K_PAGEDOWN:
                self._scroll_message(self.message_view_lines)
            return

    def _handle_click(self, pos: tuple[int, int]) -> None:
        if self.page_queue and self.mode != "start_menu":
            self._next_page()
            return
        for button in self.buttons:
            if button.contains(pos):
                self._dispatch(button.action)
                break

    def _dispatch(self, action: str) -> None:
        if action == "start":
            self.mode = "create_character"
            self.create_step = 0
            self.message = INTRO_STORY_PAGES[0]
        elif action == "load":
            self._load_game()
        elif action == "next_intro":
            self.create_step = min(self.create_step + 1, len(INTRO_STORY_PAGES))
            if self.create_step < len(INTRO_STORY_PAGES):
                self.message = INTRO_STORY_PAGES[self.create_step]
        elif action == "start_game_now":
            self._start_game()
        elif action == "save":
            save_game(self.engine.state)
            self.message = "Game saved. Your finals week is safely bookmarked."
            self._flash("save")
        elif action == "new":
            self.mode = "start_menu"
            self.create_step = 0
            self.scene = "cover"
            self.message = "Choose a student persona and begin finals week."
        elif action.startswith("persona:"):
            self.persona_id = action.split(":", 1)[1]
        elif action.startswith("action:"):
            self._choose_day_action(action.split(":", 1)[1])
        elif action.startswith("skill:"):
            self._use_skill(action.split(":", 1)[1])
        elif action.startswith("item:"):
            self._use_item(action.split(":", 1)[1])
        elif action == "forfeit":
            self._forfeit_battle()
        elif action == "fight":
            self._start_pending_battle()
        elif action == "skip_fight":
            self._forfeit_pending_encounter()
        elif action == "continue_event":
            self._resolve_event()
        elif action == "continue":
            self.mode = "battle" if self.engine.state.in_battle else "play"
            self._flash("next")

    def _start_game(self) -> None:
        result = self.engine.new_game(self.player_name, self.persona_id)
        self._queue_pages(result.message)
        self.message_scroll = 0
        self.scene = "library"
        self.mode = "play"
        self._flash("start")

    def _load_game(self) -> None:
        try:
            self.engine = GameEngine(load_game())
        except FileNotFoundError:
            self.message = "No saved game was found yet."
            self._flash("error")
            return
        if self.engine.state.in_battle:
            self.mode = "battle"
        elif self.engine.state.pending_encounter:
            self.mode = "encounter"
        else:
            self.mode = "play"
        self.scene = self._current_scene()
        self._queue_pages("Save loaded. Finals week resumes.")
        self.message_scroll = 0
        self._flash("load")

    def _choose_day_action(self, action_id: str) -> None:
        result = self.engine.perform_action(action_id)
        self._queue_pages(result.message)
        self.message_scroll = 0
        self.scene = ACTIONS[action_id]["scene"]
        self._flash(self.scene)
        self._sync_mode_after_result()

    def _use_skill(self, skill_id: str) -> None:
        result = self.engine.use_skill(skill_id)
        self._queue_pages(result.message)
        self.message_scroll = 0
        self._flash("player" if self.engine.state.in_battle else "win")
        self._sync_mode_after_result()

    def _use_item(self, item_id: str) -> None:
        result = self.engine.use_item(item_id)
        self._queue_pages(result.message)
        self.message_scroll = 0
        self._flash("support")
        self._sync_mode_after_result()

    def _forfeit_battle(self) -> None:
        result = self.engine.forfeit_battle()
        self._queue_pages(result.message)
        self.message_scroll = 0
        self._flash("error")
        self._sync_mode_after_result()

    def _start_pending_battle(self) -> None:
        result = self.engine.start_pending_battle()
        self._queue_pages(result.message)
        self.message_scroll = 0
        self._flash("enemy")
        self._sync_mode_after_result()

    def _forfeit_pending_encounter(self) -> None:
        result = self.engine.forfeit_pending_encounter()
        self._queue_pages(result.message)
        self.message_scroll = 0
        self._flash("error")
        self._sync_mode_after_result()

    def _resolve_event(self) -> None:
        result = self.engine.resolve_event("auto")
        self._queue_pages(result.message)
        self.message_scroll = 0
        self._flash("event")
        self._sync_mode_after_result()

    def _queue_pages(self, raw: str) -> None:
        normalized = raw.replace(f"\n{AUTO_PAGE_PREFIX}", f"\n\n{AUTO_PAGE_PREFIX}")
        parts = [part.strip() for part in normalized.split("\n\n") if part.strip()]
        if not parts:
            parts = [raw]
        pages = [self._parse_page(part) for part in parts]
        first_text, first_auto = pages[0]
        self.message = first_text
        self.current_page_auto = first_auto
        self.auto_page_timer = 1.2 if first_auto else 0.0
        self.page_queue = pages[1:]

    def _next_page(self) -> None:
        if not self.page_queue:
            return
        text, is_auto = self.page_queue.pop(0)
        self.message = text
        self.current_page_auto = is_auto
        self.auto_page_timer = 1.2 if is_auto else 0.0
        self.message_scroll = 0

    def _sync_mode_after_result(self) -> None:
        state = self.engine.state
        if state.game_over:
            self.mode = "ending"
        elif state.pending_event:
            self.mode = "event"
            self.scene = self._current_scene()
        elif state.in_battle:
            self.mode = "battle"
            self.scene = "battle"
        elif state.pending_encounter:
            self.mode = "encounter"
            self.scene = self._current_scene()
        elif state.last_animation == "day_transition":
            self.mode = "transition"
            self.transition_timer = 2.4
            self.scene = "transition"
        else:
            self.mode = "play"
            self.scene = self._current_scene()

    def _current_scene(self) -> str:
        state = self.engine.state
        if state.in_battle:
            return "battle"
        return SCENE_BY_ACTION.get(state.last_action, state.last_action)

    def _flash(self, kind: str) -> None:
        self.effect = {"kind": kind, "timer": 0.7}

    def _update(self, dt: float) -> None:
        if self.effect["timer"] > 0:
            self.effect["timer"] = max(0, self.effect["timer"] - dt)
        if self.current_page_auto and self.page_queue:
            self.auto_page_timer = max(0, self.auto_page_timer - dt)
            if self.auto_page_timer == 0:
                self._next_page()
        if self.mode == "transition":
            self.transition_timer = max(0, self.transition_timer - dt)
            if self.transition_timer == 0:
                self.mode = "battle" if self.engine.state.in_battle else "play"
                self.scene = self._current_scene()

    def _draw(self) -> None:
        self.screen.fill(COLORS["bg"])
        self.buttons = []
        if self.mode == "start_menu":
            self._draw_start_menu()
        elif self.mode == "create_character":
            self._draw_create_character()
        elif self.mode == "transition":
            self._draw_transition()
        else:
            self._draw_game()
        pygame.display.flip()

    def _draw_start_menu(self) -> None:
        cover = pygame.transform.scale(self.assets["cover"], (WIDTH, 630))
        self.screen.blit(cover, (0, 0))
        pygame.draw.rect(self.screen, COLORS["bg"], (0, 440, WIDTH, 280))
        self._text("FINALS ESCAPE", 70, 470, self.font_large, COLORS["gold"])
        self._text("Battle-first finals survival RPG", 74, 536, self.font_medium, COLORS["paper"])
        self._button((74, 588, 200, 52), "New Game", "start")
        self._button((286, 588, 200, 52), "Load Save", "load")

    def _draw_create_character(self) -> None:
        cover = pygame.transform.scale(self.assets["cover"], (WIDTH, 300))
        self.screen.blit(cover, (0, 0))
        self._panel(pygame.Rect(40, 320, 1040, 360), COLORS["panel"], COLORS["gold"])
        self._text("Create Character", 64, 340, self.font_medium, COLORS["gold"])

        if self.create_step < len(INTRO_STORY_PAGES):
            self._wrapped(self.message, 64, 388, 980, self.font, COLORS["paper"], max_lines=8)
            self._button((860, 620, 180, 44), "Next", "next_intro")
            return

        input_rect = pygame.Rect(64, 388, 280, 46)
        self._panel(input_rect, COLORS["paper"], COLORS["gold"])
        self._text(self.player_name or "Student name", input_rect.x + 12, input_rect.y + 11, self.font, COLORS["ink"])
        self._text("Name", 64, 360, self.font_small, COLORS["paper"])

        x = 380
        y = 380
        for idx, (persona_id, persona) in enumerate(PERSONAS.items()):
            rect = pygame.Rect(x + (idx % 2) * 330, y + (idx // 2) * 120, 300, 104)
            is_selected = persona_id == self.persona_id
            self._panel(rect, COLORS["panel_light"] if is_selected else COLORS["panel"], COLORS["gold"] if is_selected else COLORS["muted"])
            self._sprite(f"player_{persona_id}", rect.x + 10, rect.y + 8, 1)
            stats = persona["stats"]
            desc = f"{persona['label']}  E{stats['energy']} S{stats['stress']} K{stats['knowledge']} M{stats['money']}"
            self._wrapped(desc, rect.x + 72, rect.y + 10, 216, self.font_small, COLORS["paper"], max_lines=2)
            self._wrapped(persona["description"], rect.x + 72, rect.y + 42, 216, self.font_small, COLORS["muted"], max_lines=3)
            self.buttons.append(Button(rect, persona["label"], f"persona:{persona_id}"))

        self._button((64, 620, 220, 44), "Begin Finals Week", "start_game_now")

    def _draw_game(self) -> None:
        self._draw_scene()
        self._draw_sidebar()
        self._draw_message_panel()
        self._draw_controls()
        self._draw_effect()

    def _draw_scene(self) -> None:
        scene_name = "battle" if self.mode == "battle" else self.scene
        image = self.assets.get(scene_name, self.assets["library"])
        scene = pygame.transform.scale(image, (SCENE_RECT.width, SCENE_RECT.height))
        self.screen.blit(scene, SCENE_RECT.topleft)
        pygame.draw.rect(self.screen, COLORS["gold"], SCENE_RECT, 4)

        if self.mode == "battle":
            player = self.engine.state.player
            enemy = self.engine.state.current_enemy
            bob = int(pygame.time.get_ticks() / 250) % 2
            self._sprite(f"player_{player.persona}", 375, 277 + bob * 4, 3)
            if enemy:
                self._sprite(f"enemy_{enemy.enemy_id}", 800, 158 - bob * 4, 3)
                self._health_bar(780, 120, 230, 18, enemy.hp or 0, enemy.max_hp, COLORS["red"])
                self._text(enemy.name, 780, 90, self.font_medium, COLORS["paper"])
        elif self.mode == "encounter":
            self._sprite(f"player_{self.engine.state.player.persona}", 350, 305, 1)
        else:
            self._sprite(f"player_{self.engine.state.player.persona}", 468, 300, 2)

        self._text(f"Day {self.engine.state.day}", 314, 38, self.font_medium, COLORS["paper"])
        mode_name = {
            "play": "Daily Choice",
            "event": "Event Outcome",
            "encounter": "Encounter",
            "battle": "Battle Mode",
            "ending": "Ending",
            "transition": "Night Transition",
        }.get(self.mode, "Mode")
        self._text(mode_name, 314, 68, self.font, COLORS["gold"])

    def _draw_sidebar(self) -> None:
        player = self.engine.state.player
        self._panel(pygame.Rect(18, 18, 242, 684), COLORS["panel"], COLORS["gold"])
        self._sprite(f"player_{player.persona}", 78, 46, 2)
        self._text(player.name, 34, 178, self.font_medium, COLORS["paper"])
        self._text(PERSONAS[player.persona]["label"], 34, 210, self.font, COLORS["gold"])
        self._stat("Energy", player.energy, 100, 34, 270, COLORS["green"])
        self._stat("Stress", player.stress, 100, 34, 332, COLORS["red"])
        self._stat("Knowledge", player.knowledge, 100, 34, 394, COLORS["blue"])
        self._text(f"Money: ${player.money}", 34, 462, self.font, COLORS["paper"])
        self._text(f"Focus: {player.focus}", 34, 494, self.font, COLORS["paper"])
        self._text(f"Next hit bonus: +{player.focus * 4}", 34, 520, self.font_small, COLORS["muted"])
        self._text("Items", 34, 534, self.font, COLORS["gold"])
        for idx, item_id in enumerate(self.engine.state.inventory[:3]):
            label = ITEMS.get(item_id, {}).get("label", item_id)
            self._button((34, 560 + idx * 22, 190, 20), label[:18], f"item:{item_id}", ITEMS.get(item_id, {}).get("description", ""))
        self._button((34, 616, 190, 36), "Save", "save")
        self._button((34, 660, 190, 36), "New Game", "new")

    def _draw_message_panel(self) -> None:
        self._panel(self.message_panel_rect, COLORS["paper"], COLORS["gold"])
        text_x = self.message_panel_rect.x + 22
        text_y = self.message_panel_rect.y + 16
        text_w = self.message_panel_rect.width - 48
        lines = self._wrap_by_pixels(self.message, text_w, self.font)
        max_scroll = max(0, len(lines) - self.message_view_lines)
        self.message_scroll = max(0, min(self.message_scroll, max_scroll))
        visible = lines[self.message_scroll : self.message_scroll + self.message_view_lines]
        line_height = self.font.get_linesize() + 2
        for idx, line in enumerate(visible):
            self._text(line, text_x, text_y + idx * line_height, self.font, COLORS["ink"])
        self._draw_scrollbar(lines, max_scroll)
        if self.page_queue and self.mode not in {"start_menu", "create_character"}:
            hint = "Auto..." if self.current_page_auto else "Click to continue..."
            self._text(hint, self.message_panel_rect.right - 194, self.message_panel_rect.bottom - 28, self.font_small, COLORS["coral"])

    def _draw_controls(self) -> None:
        if self.mode == "ending":
            self._button((500, 630, 190, 54), "New Game", "new")
            return
        if self.mode == "play":
            items = [(action_id, data["label"], data["message"]) for action_id, data in ACTIONS.items()]
            prefix = "action:"
        elif self.mode == "event":
            self._button((282, CONTROLS_Y, 820, 44), "Continue Event", "continue_event", "Apply event effects and continue.")
            return
        elif self.mode == "encounter":
            enemy = self.engine.state.pending_encounter
            if enemy:
                self._text(f"Encounter: {enemy['label']}", 302, 394, self.font_medium, COLORS["coral"])
            self._button((282, CONTROLS_Y, 398, 44), "Fight", "fight", "Enter battle now.")
            self._button((704, CONTROLS_Y, 398, 44), "Forfeit Encounter", "skip_fight", "Skip battle and take penalty.")
            return
        elif self.mode == "battle":
            items = [(skill_id, data["label"], data["description"]) for skill_id, data in SKILLS.items()]
            prefix = "skill:"
        else:
            return

        for index, (item_id, label, hint) in enumerate(items):
            row = index // 3
            col = index % 3
            x = 282 + col * 274
            y = CONTROLS_Y + row * 52
            self._button((x, y, 258, 44), label, prefix + item_id, hint)

        if self.mode == "battle":
            self._button((830, CONTROLS_Y + 52, 252, 44), "Forfeit Battle", "forfeit", "Lose reward and take penalty.")

        mouse = pygame.mouse.get_pos()
        for button in self.buttons:
            if button.contains(mouse) and button.hint and self.mode in {"battle", "encounter"}:
                self._tooltip(mouse, button.hint)

    def _draw_transition(self) -> None:
        image = pygame.transform.scale(self.assets["transition"], (WIDTH, HEIGHT))
        self.screen.blit(image, (0, 0))
        progress = 1 - self.transition_timer / 2.4
        sun_x = int(80 + progress * 380)
        moon_x = int(870 + progress * 180)
        pygame.draw.circle(self.screen, COLORS["gold"], (sun_x, 330), 48)
        pygame.draw.circle(self.screen, COLORS["paper"], (moon_x, 190), 32)
        self._text(f"Day {self.engine.state.day} begins", 360, 520, self.font_large, COLORS["gold"])
        self._wrapped(self.message, 340, 585, 500, self.font_medium, COLORS["paper"], max_lines=2)
        self._button((468, 648, 188, 48), "Continue", "continue")

    def _draw_effect(self) -> None:
        if self.effect["timer"] <= 0:
            return
        alpha = int(255 * min(1, self.effect["timer"] / 0.45))
        pulse = int((0.7 - self.effect["timer"]) * 80)
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        color = COLORS["gold"] if self.mode != "battle" else COLORS["coral"]
        pygame.draw.rect(
            overlay,
            (*color, 60),
            (
                SCENE_RECT.x + pulse,
                SCENE_RECT.y + pulse // 2,
                SCENE_RECT.width - pulse * 2,
                SCENE_RECT.height - pulse,
            ),
        )
        self.screen.blit(overlay, (0, 0))
        label = {
            "player": "Skill activated!",
            "enemy": "Enemy strikes!",
            "event": "Event resolved!",
            "win": "Battle cleared!",
            "error": "Not available",
            "save": "Saved",
            "load": "Loaded",
            "next": "Next day",
        }.get(self.effect["kind"], "Action resolved")
        self._text(label, 714, 438, self.font_medium, (*color[:3], alpha))

    def _button(self, rect_tuple: tuple[int, int, int, int], label: str, action: str, hint: str = "") -> None:
        rect = pygame.Rect(rect_tuple)
        mouse_over = rect.collidepoint(pygame.mouse.get_pos())
        fill = COLORS["gold"] if mouse_over else COLORS["panel_light"]
        edge = COLORS["paper"] if mouse_over else COLORS["gold"]
        self._panel(rect, fill, edge)
        text_color = COLORS["ink"] if mouse_over else COLORS["paper"]
        self._center_text(label, rect, self.font, text_color)
        self.buttons.append(Button(rect, label, action, hint))

    def _panel(self, rect: pygame.Rect, fill: tuple[int, int, int], edge: tuple[int, int, int]) -> None:
        pygame.draw.rect(self.screen, COLORS["black"], rect.move(4, 4))
        pygame.draw.rect(self.screen, fill, rect)
        pygame.draw.rect(self.screen, edge, rect, 3)

    def _stat(self, label: str, value: int, max_value: int, x: int, y: int, color: tuple[int, int, int]) -> None:
        self._text(f"{label}: {value}/{max_value}", x, y, self.font, COLORS["paper"])
        self._health_bar(x, y + 28, 190, 18, value, max_value, color)

    def _health_bar(self, x: int, y: int, w: int, h: int, value: int, max_value: int, color: tuple[int, int, int]) -> None:
        pygame.draw.rect(self.screen, COLORS["ink"], (x, y, w, h))
        ratio = max(0, min(1, value / max_value))
        pygame.draw.rect(self.screen, color, (x + 3, y + 3, int((w - 6) * ratio), h - 6))
        pygame.draw.rect(self.screen, COLORS["paper"], (x, y, w, h), 2)

    def _sprite(self, name: str, x: int, y: int, scale: int) -> None:
        image = self.assets.get(name)
        if image is None and name.startswith("enemy_"):
            image = self.assets.get("enemy_exam_anxiety")
        if image is None and name.startswith("player_"):
            image = self.assets.get("player_balanced")
        if image is None:
            return
        size = (image.get_width() * scale, image.get_height() * scale)
        self.screen.blit(pygame.transform.scale(image, size), (x, y))

    def _text(self, text: str, x: int, y: int, font: pygame.font.Font, color: tuple[int, int, int]) -> None:
        if color != COLORS["ink"]:
            shadow = font.render(text, True, COLORS["black"])
            self.screen.blit(shadow, (x + 2, y + 2))
        surface = font.render(text, True, color)
        self.screen.blit(surface, (x, y))

    def _center_text(self, text: str, rect: pygame.Rect, font: pygame.font.Font, color: tuple[int, int, int]) -> None:
        surface = font.render(text, True, color)
        self.screen.blit(surface, surface.get_rect(center=rect.center))

    def _wrapped(
        self,
        text: str,
        x: int,
        y: int,
        width: int,
        font: pygame.font.Font,
        color: tuple[int, int, int],
        max_lines: int = 5,
    ) -> None:
        line_height = font.get_linesize() + 2
        lines = self._wrap_by_pixels(text, width, font)
        for index, line in enumerate(lines[:max_lines]):
            self._text(line, x, y + index * line_height, font, color)

    def _wrap_by_pixels(self, text: str, max_width: int, font: pygame.font.Font) -> list[str]:
        wrapped: list[str] = []
        for paragraph in text.splitlines():
            words = paragraph.split()
            if not words:
                wrapped.append("")
                continue
            line = words[0]
            for word in words[1:]:
                test = f"{line} {word}"
                if font.size(test)[0] <= max_width:
                    line = test
                else:
                    wrapped.append(line)
                    line = word
            wrapped.append(line)
        return wrapped

    def _tooltip(self, pos: tuple[int, int], text: str) -> None:
        rect = pygame.Rect(min(pos[0] + 12, WIDTH - 360), min(max(pos[1] - 88, 20), 528), 340, 76)
        self._panel(rect, COLORS["paper"], COLORS["gold"])
        self._wrapped(text, rect.x + 12, rect.y + 12, 312, self.font_small, COLORS["ink"], max_lines=3)

    def _draw_scrollbar(self, lines: list[str], max_scroll: int) -> None:
        track = pygame.Rect(self.message_panel_rect.right - 18, self.message_panel_rect.y + 10, 8, self.message_panel_rect.height - 20)
        pygame.draw.rect(self.screen, COLORS["paper_dark"], track)
        if max_scroll <= 0:
            thumb = track
        else:
            ratio = self.message_view_lines / max(len(lines), self.message_view_lines)
            thumb_h = max(18, int(track.height * ratio))
            progress = self.message_scroll / max_scroll
            thumb_y = track.y + int((track.height - thumb_h) * progress)
            thumb = pygame.Rect(track.x, thumb_y, track.width, thumb_h)
        pygame.draw.rect(self.screen, COLORS["panel_light"], thumb)
        pygame.draw.rect(self.screen, COLORS["gold"], track, 1)

    def _scroll_message(self, amount: int) -> None:
        lines = self._wrap_by_pixels(self.message, self.message_panel_rect.width - 48, self.font)
        max_scroll = max(0, len(lines) - self.message_view_lines)
        self.message_scroll = max(0, min(self.message_scroll + amount, max_scroll))

    def _parse_page(self, page: str) -> tuple[str, bool]:
        if page.startswith(AUTO_PAGE_PREFIX):
            return page.removeprefix(AUTO_PAGE_PREFIX).strip(), True
        return page, False


def run_pygame_app() -> None:
    FinalsEscapePygame().run()


if __name__ == "__main__":
    run_pygame_app()
