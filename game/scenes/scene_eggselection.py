import pygame
import os
from core import game_globals, runtime_globals, constants
from core.game_digidex import register_digidex_entry
from core.game_pet import GamePet
from core.utils.module_utils import get_module
from core.utils.pygame_utils import blit_with_shadow, get_font, sprite_load_percent
from core.utils.scene_utils import change_scene
from core.utils.utils_unlocks import is_unlocked, unlock_item

class SceneEggSelection:
    GRID_COLUMNS = 3
    GRID_ROWS = 2  # Number of visible rows per page

    @property
    def EGG_SIZE(self):
        return (int(40 * constants.UI_SCALE), int(40 * constants.UI_SCALE))

    @property
    def LOGO_SIZE(self):
        return (int(160 * constants.UI_SCALE), int(80 * constants.UI_SCALE))

    def __init__(self) -> None:
        self.eggs_by_module = self.load_eggs_by_module()
        self.current_module_index = 0
        self.current_egg_row = 0
        self.current_egg_col = 0
        self.scroll_offset = 0  # For vertical scrolling
        self.egg_sprites = {}
        self.module_logo = None
        self.font = get_font(constants.FONT_SIZE_SMALL)

        # Use new method for unknown sprite and scale
        self.unknown_sprite = sprite_load_percent(
            "resources/Unknown.png",
            percent=(self.EGG_SIZE[1] / constants.SCREEN_HEIGHT) * 100,
            keep_proportion=True,
            base_on="height"
        )

        runtime_globals.game_console.log(f"[SceneEggSelection] Modules loaded: {len(self.eggs_by_module)}")
        # Use new method for background, scale to screen height
        if constants.SCREEN_WIDTH > constants.SCREEN_HEIGHT:
            self.bg_sprite = sprite_load_percent(
                constants.DIGIDEX_BACKGROUND_PATH,
                percent=600,
                keep_proportion=True,
                base_on="width"
            )
        else:
            self.bg_sprite = sprite_load_percent(
                constants.DIGIDEX_BACKGROUND_PATH,
                percent=100,
                keep_proportion=True,
                base_on="height"
            )
        self.bg_frame = 0
        self.bg_timer = 0
        self.bg_frame_width = self.bg_sprite.get_width() // 6  # 326

        self.load_egg_sprites()
        self.load_module_logo()
        self.locked_special_eggs = {}
        self.cache_locked_special_eggs()

        self._last_cache = None
        self._last_cache_key = None

    def load_eggs_by_module(self):
        eggs_by_module = {}
        for module_name, module in runtime_globals.game_modules.items():
            eggs = module.get_monsters_by_stage(0)
            if eggs:
                eggs_by_module[module_name] = eggs
                for egg in eggs:
                    if egg.get("special", False):
                        special_key = egg.get("special-key", "")
                        module_val = egg.get("module", module_name)
                        if not is_unlocked(module_val, "eggs", special_key):
                            continue  # Skip locked special eggs
        return eggs_by_module

    def load_egg_sprites(self):
        for module_name, eggs in self.eggs_by_module.items():
            for egg in eggs:
                egg_name = egg["name"]
                folder_path = os.path.join(get_module(egg["module"]).folder_path, "monsters", f"{egg_name}_dmc")
                frame_path = os.path.join(folder_path, "0.png")
                try:
                    # Use new method for egg sprite, scale to EGG_SIZE height
                    self.egg_sprites[egg_name] = sprite_load_percent(
                        frame_path,
                        percent=(self.EGG_SIZE[1] / constants.SCREEN_HEIGHT) * 100,
                        keep_proportion=True,
                        base_on="height"
                    )
                    runtime_globals.game_console.log(f"[SceneEggSelection] Loaded sprite for {egg_name}")
                except Exception:
                    self.egg_sprites[egg_name] = None
                    runtime_globals.game_console.log(f"[SceneEggSelection] Failed to load {frame_path}")

    def cache_locked_special_eggs(self):
        """Cache locked status for all special eggs."""
        for module_name, eggs in self.eggs_by_module.items():
            for egg in eggs:
                if egg.get("special", False):
                    special_key = egg.get("special-key", "")
                    module = egg.get("module", module_name)
                    locked = not is_unlocked(module, "eggs", special_key)
                    self.locked_special_eggs[(module, egg["name"])] = locked
                    
    def load_module_logo(self):
        module_name = list(self.eggs_by_module.keys())[self.current_module_index]
        module_path = get_module(module_name).folder_path
        logo_path = os.path.join(module_path, "logo.png")
        try:
            # Use new method for logo, scale to LOGO_SIZE height
            self.module_logo = sprite_load_percent(
                logo_path,
                percent=(self.LOGO_SIZE[1] / constants.SCREEN_HEIGHT) * 100,
                keep_proportion=True,
                base_on="height"
            )
            runtime_globals.game_console.log(f"[SceneEggSelection] Loaded module logo: {logo_path}")
        except Exception:
            self.module_logo = None
            runtime_globals.game_console.log(f"[SceneEggSelection] Failed to load logo: {logo_path}")

    def is_empty(self, x, y):
        module_name = list(self.eggs_by_module.keys())[self.current_module_index]
        eggs = self.eggs_by_module[module_name]
        index = y * self.GRID_COLUMNS + x
        return index >= len(eggs)
    
    def move_selection(self, direction):
        module_name = list(self.eggs_by_module.keys())[self.current_module_index]
        eggs = self.eggs_by_module[module_name]
        total_rows = (len(eggs) + self.GRID_COLUMNS - 1) // self.GRID_COLUMNS

        if direction == "LEFT":
            if self.current_egg_col == 0:
                self.current_module_index = (self.current_module_index - 1) % len(self.eggs_by_module)
                self.current_egg_col = self.GRID_COLUMNS - 1
                found = False
                while not found:
                    if self.is_empty(self.current_egg_col, self.current_egg_row):
                        self.current_egg_col -= 1
                        if self.current_egg_col < 0:
                            self.current_egg_col = self.GRID_COLUMNS - 1
                            self.current_egg_row -= 1
                            if self.current_egg_row < 0:
                                self.current_egg_row = total_rows - 1
                    else:
                        found = True
                    
                self.load_module_logo()
            else:
                self.current_egg_col -= 1

        elif direction == "RIGHT":
            if self.current_egg_col == self.GRID_COLUMNS - 1 or self.is_empty(self.current_egg_col + 1, self.current_egg_row):
                self.current_module_index = (self.current_module_index + 1) % len(self.eggs_by_module)
                self.current_egg_col = 0
                self.load_module_logo()
            else:
                self.current_egg_col += 1

        elif direction == "UP":
            prev_row = self.current_egg_row
            wrapped = False
            while True:
                if self.current_egg_row > 0:
                    self.current_egg_row -= 1
                else:
                    self.current_egg_row = total_rows - 1
                    wrapped = True
                # If not empty, break; if we've looped all rows, stop
                if not self.is_empty(self.current_egg_col, self.current_egg_row) or self.current_egg_row == prev_row:
                    break
            if self.current_egg_row < self.scroll_offset or wrapped:
                self.scroll_offset = max(0, self.current_egg_row - self.GRID_ROWS + 1)

        elif direction == "DOWN":
            prev_row = self.current_egg_row
            total_rows = (len(eggs) + self.GRID_COLUMNS - 1) // self.GRID_COLUMNS
            wrapped = False
            while True:
                if self.current_egg_row < total_rows - 1:
                    self.current_egg_row += 1
                else:
                    self.current_egg_row = 0
                    wrapped = True
                # If not empty, break; if we've looped all rows, stop
                if not self.is_empty(self.current_egg_col, self.current_egg_row) or self.current_egg_row == prev_row:
                    break
            if self.current_egg_row >= self.scroll_offset + self.GRID_ROWS or wrapped:
                self.scroll_offset = max(0, self.current_egg_row - self.GRID_ROWS + 1)

        runtime_globals.game_console.log(f"[SceneEggSelection] Module: {module_name}, Position: ({self.current_egg_row}, {self.current_egg_col}), Scroll Offset: {self.scroll_offset}")

    def invalidate_cache(self):
        self._last_cache = None
        self._last_cache_key = None

    def draw(self, surface):
        # Always update background animation
        frame_rect = pygame.Rect(self.bg_frame * self.bg_frame_width, 0, self.bg_frame_width, constants.SCREEN_HEIGHT)
        surface.blit(self.bg_sprite, (0, 0), frame_rect)

        # Cache key includes module, row, col, scroll, and UI/layout
        cache_key = (
            self.current_module_index,
            self.current_egg_row,
            self.current_egg_col,
            self.scroll_offset,
            constants.SCREEN_WIDTH,
            constants.SCREEN_HEIGHT,
            constants.UI_SCALE
        )
        if self._last_cache_key != cache_key or self._last_cache is None:
            cached_surface = pygame.Surface((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT), pygame.SRCALPHA)

            # Draw module logo
            if self.module_logo:
                logo_x = (constants.SCREEN_WIDTH - self.module_logo.get_width()) // 2
                cached_surface.blit(self.module_logo, (logo_x, int(10 * constants.UI_SCALE)))

            module_name = list(self.eggs_by_module.keys())[self.current_module_index]
            eggs = self.eggs_by_module[module_name]

            start_y = constants.SCREEN_HEIGHT - int(150 * constants.UI_SCALE)
            col_width = constants.SCREEN_WIDTH // self.GRID_COLUMNS

            for index, egg in enumerate(eggs):
                row = index // self.GRID_COLUMNS
                col = index % self.GRID_COLUMNS

                if not (self.scroll_offset <= row < self.scroll_offset + self.GRID_ROWS):
                    continue  # Skip rows outside of the visible range

                visible_row = row - self.scroll_offset
                x = (col_width * col) + (col_width // 2 - self.EGG_SIZE[0] // 2)
                y = start_y + (visible_row * (self.EGG_SIZE[1] + int(35 * constants.UI_SCALE)))

                egg_name = egg["name"]
                egg_sprite = self.egg_sprites.get(egg_name, None)

                # Check if special and locked
                module = egg.get("module", module_name)
                is_locked_special = self.locked_special_eggs.get((module, egg_name), False)

                # Semi-transparent background rectangle
                rect_surface = pygame.Surface((self.EGG_SIZE[0] + int(30 * constants.UI_SCALE), self.EGG_SIZE[1] + int(30 * constants.UI_SCALE)), pygame.SRCALPHA)
                rect_surface.fill((206, 202, 239, 128))  # RGBA with alpha 128 (~50%)
                cached_surface.blit(rect_surface, (x - int(15 * constants.UI_SCALE), y))

                if is_locked_special:
                    blit_with_shadow(cached_surface, self.unknown_sprite, (x, y))
                elif egg_sprite:
                    blit_with_shadow(cached_surface, egg_sprite, (x, y))

                display_name = "???" if is_locked_special else egg_name.replace("DmC", "").replace("PenC", "").replace("Version", "")
                text = self.font.render(display_name, True, constants.FONT_COLOR_DEFAULT)
                blit_with_shadow(cached_surface, text, (x + (self.EGG_SIZE[0] // 2) - (text.get_width() // 2), y + self.EGG_SIZE[1]))

            self._last_cache = cached_surface
            self._last_cache_key = cache_key

        # Blit cached content (eggs, logo, names)
        surface.blit(self._last_cache, (0, 0))

        # Draw cursor highlight (always on top, not cached)
        module_name = list(self.eggs_by_module.keys())[self.current_module_index]
        eggs = self.eggs_by_module[module_name]
        start_y = constants.SCREEN_HEIGHT - int(150 * constants.UI_SCALE)
        col_width = constants.SCREEN_WIDTH // self.GRID_COLUMNS
        index = self.current_egg_row * self.GRID_COLUMNS + self.current_egg_col
        if 0 <= index < len(eggs):
            row = self.current_egg_row
            col = self.current_egg_col
            visible_row = row - self.scroll_offset
            if 0 <= visible_row < self.GRID_ROWS:
                x = (col_width * col) + (col_width // 2 - self.EGG_SIZE[0] // 2)
                y = start_y + (visible_row * (self.EGG_SIZE[1] + int(35 * constants.UI_SCALE)))
                pygame.draw.rect(
                    surface,
                    constants.FONT_COLOR_GREEN,
                    (x - int(15 * constants.UI_SCALE), y, self.EGG_SIZE[0] + int(30 * constants.UI_SCALE), self.EGG_SIZE[1] + int(30 * constants.UI_SCALE)),
                    3
                )

    def update(self):
        self.bg_timer += 1
        if self.bg_timer >= int(3 * (constants.FRAME_RATE / 30)):  # Change frame every 3 seconds
            self.bg_timer = 0
            self.bg_frame = (self.bg_frame + 1) % 6

    def handle_event(self, input_action):
        if input_action in ["LEFT", "RIGHT", "UP", "DOWN"]:
            runtime_globals.game_sound.play("menu")
            self.move_selection(input_action)
        elif input_action in ["A", "START"]:
            runtime_globals.game_sound.play("menu")
            module_name = list(self.eggs_by_module.keys())[self.current_module_index]
            eggs = self.eggs_by_module[module_name]
            index = self.current_egg_row * self.GRID_COLUMNS + self.current_egg_col
            if 0 <= index < len(eggs):
                selected_egg = eggs[index]
                module = selected_egg.get("module", module_name)
                if self.locked_special_eggs.get((module, selected_egg["name"]), False):
                    runtime_globals.game_console.log("[SceneEggSelection] This egg is locked!")
                    return
                self.select_egg(eggs[index])
        elif input_action == "B" and len(game_globals.pet_list) > 0:
            runtime_globals.game_sound.play("cancel")
            change_scene("game")

    def select_egg(self, selected_egg):
        runtime_globals.game_console.log(f"[SceneEggSelection] Selected egg: {selected_egg['name']}")
        pet = GamePet(selected_egg)
        egg_key = (selected_egg["module"], selected_egg["version"])
        register_digidex_entry(pet.name, pet.module, pet.version)
        if egg_key in game_globals.traited:
            pet.traited = True
            game_globals.traited.remove(egg_key)
        game_globals.pet_list.append(pet)
        bg_name = f"ver{selected_egg['version']}"

        # Only unlock objects of type "egg" with no version or matching the egg's version
        module_unlockables = get_module(selected_egg["module"]).unlocks
        unlocks = module_unlockables if isinstance(module_unlockables, list) else []
        for unlock in unlocks:
            if unlock.get("type") == "egg":
                if "version" not in unlock or unlock.get("version") == selected_egg["version"]:
                    unlock_item(selected_egg["module"], "egg", unlock["name"])

        if not game_globals.game_background:
            game_globals.game_background = bg_name
            game_globals.background_module_name = selected_egg["module"]
        change_scene("game")
