#=====================================================================
# WindowPetSelector
#=====================================================================
import pygame
from core import game_globals, runtime_globals
from core.constants import *
from core.utils import blit_with_shadow, change_scene, get_font

PAGE_MARGIN = 0
LEFT_PADDING = 12
ITEM_HEIGHT = 60

class WindowPetSelector:
    """
    Window to select a pet from a list, with support for scrolling if needed.
    """

    def __init__(self) -> None:
        self.pets = game_globals.pet_list
        self.selected_index = 0
        self.scroll_offset = 0

        self.font = get_font(FONT_SIZE_MEDIUM_LARGE)
        self.max_visible_items = (SCREEN_HEIGHT - 2 * PAGE_MARGIN) // ITEM_HEIGHT

    def handle_event(self, input_action) -> None:
        """
        Handles key inputs and GPIO button presses for navigating pets and confirming selection.
        """
        if input_action:
            if input_action == "DOWN":  # Move selection down
                runtime_globals.game_sound.play("menu")
                self.selected_index = (self.selected_index + 1) % len(self.pets)
                self.adjust_scroll()
            elif input_action == "UP":  # Move selection up
                runtime_globals.game_sound.play("menu")
                self.selected_index = (self.selected_index - 1) % len(self.pets)
                self.adjust_scroll()
            elif input_action == "A":  # Accept (Enter/Z or A button on Pi)
                runtime_globals.game_sound.play("menu")
                return True  # Signal selection complete
            elif input_action == "B":  # Escape (Cancel/Menu)
                runtime_globals.game_sound.play("cancel")
                change_scene("game")

        return False

    def adjust_scroll(self) -> None:
        """
        Adjusts scroll offset so the selected item is always visible.
        """
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + self.max_visible_items:
            self.scroll_offset = self.selected_index - self.max_visible_items + 1

    def draw(self, surface: pygame.Surface) -> None:
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

            if pet:
                color = attr_colors.get(pet.attribute, (150, 150, 150))
            else:
                color = (150, 150, 150)
            pygame.draw.rect(surface, color, (PAGE_MARGIN + LEFT_PADDING, y_pos + 6, OPTION_ICON_SIZE, OPTION_ICON_SIZE))

            # Draw sprite
            if pet.get_sprite(0):
                sprite = pygame.transform.scale(pet.get_sprite(0), (OPTION_ICON_SIZE, OPTION_ICON_SIZE))
                blit_with_shadow(surface, sprite, (PAGE_MARGIN + LEFT_PADDING, y_pos + 6))
                blit_with_shadow(surface, runtime_globals.game_module_flag[pet.module], (PAGE_MARGIN + LEFT_PADDING, y_pos + 6))

            # Draw name, stage, attribute
            name_text = self.font.render(f"{pet.name}", True, FONT_COLOR_DEFAULT)
            stage_name = STAGES[pet.stage] if pet.stage < len(STAGES) else "Unknown"
            attribute_text = self.font.render(f"{stage_name} | {pet.attribute}", True, (200, 200, 200))

            blit_with_shadow(surface, name_text, (PAGE_MARGIN + ITEM_HEIGHT + LEFT_PADDING, y_pos))
            blit_with_shadow(surface, attribute_text, (PAGE_MARGIN + ITEM_HEIGHT + LEFT_PADDING, y_pos + 25))

            # Highlight selected
            if idx == self.selected_index:
                pygame.draw.rect(surface, FONT_COLOR_GREEN, (PAGE_MARGIN, y_pos, SCREEN_WIDTH - PAGE_MARGIN * 2, ITEM_HEIGHT), 2)

    def get_selected_pet(self):
        #runtime_globals.game_console.log(f"Selected {self.selected_index}")
        return self.pets[self.selected_index]