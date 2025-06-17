#=====================================================================
# WindowPetSelector
#=====================================================================
import pygame
from core import game_globals, runtime_globals
from core.constants import *
from core.utils.pygame_utils import blit_with_shadow, get_font, sprite_load_percent
from core.utils.scene_utils import change_scene

PAGE_MARGIN = 0
LEFT_PADDING = int(12 * UI_SCALE)
ITEM_HEIGHT = int(60 * UI_SCALE)

class WindowPetSelector:
    """
    Window to select a pet from a list, with support for scrolling if needed.
    Optimized: redraws only when index or scroll changes.
    """

    def __init__(self) -> None:
        self.pets = game_globals.pet_list
        self.selected_index = 0
        self.scroll_offset = 0

        self.font = get_font(FONT_SIZE_MEDIUM_LARGE)
        self.max_visible_items = (SCREEN_HEIGHT - 2 * PAGE_MARGIN) // ITEM_HEIGHT

        # Preload and scale module flags using the new method
        self.module_flags = {}
        for pet in self.pets:
            if pet and pet.module not in self.module_flags:
                flag_path = runtime_globals.game_modules[pet.module].flag_path if hasattr(runtime_globals.game_modules[pet.module], "flag_path") else None
                if flag_path:
                    self.module_flags[pet.module] = sprite_load_percent(
                        flag_path,
                        percent=(OPTION_ICON_SIZE / SCREEN_HEIGHT) * 100,
                        keep_proportion=True,
                        base_on="height"
                    )
                else:
                    self.module_flags[pet.module] = pygame.transform.scale(
                        runtime_globals.game_module_flag[pet.module],
                        (OPTION_ICON_SIZE, OPTION_ICON_SIZE)
                    )
        self._last_cache = None
        self._last_cache_key = None

    def handle_event(self, input_action) -> None:
        """
        Handles key inputs and GPIO button presses for navigating pets and confirming selection.
        """
        changed = False
        if input_action:
            if input_action == "DOWN":  # Move selection down
                runtime_globals.game_sound.play("menu")
                self.selected_index = (self.selected_index + 1) % len(self.pets)
                self.adjust_scroll()
                changed = True
            elif input_action == "UP":  # Move selection up
                runtime_globals.game_sound.play("menu")
                self.selected_index = (self.selected_index - 1) % len(self.pets)
                self.adjust_scroll()
                changed = True
            elif input_action == "A":  # Accept (Enter/Z or A button on Pi)
                runtime_globals.game_sound.play("menu")
                return True  # Signal selection complete
            elif input_action == "B":  # Escape (Cancel/Menu)
                runtime_globals.game_sound.play("cancel")
                change_scene("game")
        if changed:
            self._last_cache = None  # Invalidate cache
        return False

    def adjust_scroll(self) -> None:
        """
        Adjusts scroll offset so the selected item is always visible.
        """
        prev_offset = self.scroll_offset
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + self.max_visible_items:
            self.scroll_offset = self.selected_index - self.max_visible_items + 1
        if self.scroll_offset != prev_offset:
            self._last_cache = None  # Invalidate cache

    def _precompute_surface(self):
        cache_key = (self.selected_index, self.scroll_offset, SCREEN_WIDTH, SCREEN_HEIGHT, UI_SCALE)
        if self._last_cache_key == cache_key and self._last_cache is not None:
            return self._last_cache

        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        y_start = PAGE_MARGIN
        for idx in range(self.scroll_offset, min(self.scroll_offset + self.max_visible_items, len(self.pets))):
            pet = self.pets[idx]
            y_pos = y_start + (idx - self.scroll_offset) * ITEM_HEIGHT

            attr_colors = {
                "Da": (66, 165, 245),
                "Va": (102, 187, 106),
                "Vi": (237, 83, 80),
                "": (171, 71, 188),
                "???": (0, 0, 0)
            }

            color = attr_colors.get(pet.attribute, (150, 150, 150)) if pet else (150, 150, 150)
            pygame.draw.rect(
                surface,
                color,
                (PAGE_MARGIN + LEFT_PADDING, y_pos + int(6 * UI_SCALE), OPTION_ICON_SIZE, OPTION_ICON_SIZE)
            )

            # Draw sprite using new method and scale
            if pet.get_sprite(0):
                sprite = pygame.transform.scale(pet.get_sprite(0), (OPTION_ICON_SIZE, OPTION_ICON_SIZE))
                blit_with_shadow(surface, sprite, (PAGE_MARGIN + LEFT_PADDING, y_pos + int(6 * UI_SCALE)))
                # Draw module flag, scaled and positioned
                flag = self.module_flags.get(pet.module, None)
                if flag:
                    blit_with_shadow(surface, flag, (PAGE_MARGIN + LEFT_PADDING, y_pos + int(6 * UI_SCALE)))

            # Draw name, stage, attribute
            name_text = self.font.render(f"{pet.name}", True, FONT_COLOR_DEFAULT)
            stage_name = STAGES[pet.stage] if pet.stage < len(STAGES) else "Unknown"
            attribute_text = self.font.render(f"{stage_name} | {pet.attribute}", True, (200, 200, 200))

            blit_with_shadow(surface, name_text, (PAGE_MARGIN + ITEM_HEIGHT + LEFT_PADDING, y_pos))
            blit_with_shadow(surface, attribute_text, (PAGE_MARGIN + ITEM_HEIGHT + LEFT_PADDING, y_pos + int(25 * UI_SCALE)))

            # Highlight selected
            if idx == self.selected_index:
                pygame.draw.rect(
                    surface,
                    FONT_COLOR_GREEN,
                    (PAGE_MARGIN, y_pos, SCREEN_WIDTH - PAGE_MARGIN * 2, ITEM_HEIGHT),
                    2
                )
        self._last_cache = surface
        self._last_cache_key = cache_key
        return surface

    def draw(self, surface: pygame.Surface) -> None:
        cached = self._precompute_surface()
        surface.blit(cached, (0, 0))

    def get_selected_pet(self):
        return self.pets[self.selected_index]