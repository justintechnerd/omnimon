import pygame
from core import game_globals, runtime_globals
from core.constants import *
from core.utils.pygame_utils import blit_with_shadow, get_font
from core.utils.scene_utils import change_scene

PAGE_MARGIN = 0
LEFT_PADDING = int(12 * UI_SCALE)
ITEM_HEIGHT = int(60 * UI_SCALE)

class WindowPetSelector:
    """
    Window to select a pet from a list, re-rendered every frame (no caching).
    """

    def __init__(self) -> None:
        self.pets = game_globals.pet_list
        self.selected_index = 0
        self.scroll_offset = 0
        self.font = get_font(FONT_SIZE_MEDIUM_LARGE)
        self.max_visible_items = (SCREEN_HEIGHT - 2 * PAGE_MARGIN) // ITEM_HEIGHT

        # Preload module flags (scaled only once)
        self.module_flags = {}
        for pet in self.pets:
            if pet and pet.module not in self.module_flags:
                flag_path = getattr(runtime_globals.game_modules[pet.module], "flag_path", None)
                if flag_path:
                    flag = pygame.image.load(flag_path).convert_alpha()
                    self.module_flags[pet.module] = pygame.transform.scale(
                        flag, (OPTION_ICON_SIZE, OPTION_ICON_SIZE)
                    )
                else:
                    self.module_flags[pet.module] = pygame.transform.scale(
                        runtime_globals.game_module_flag[pet.module],
                        (OPTION_ICON_SIZE, OPTION_ICON_SIZE)
                    )

    def handle_event(self, input_action) -> None:
        if input_action:
            if input_action == "DOWN":
                runtime_globals.game_sound.play("menu")
                self.selected_index = (self.selected_index + 1) % len(self.pets)
                self.adjust_scroll()
            elif input_action == "UP":
                runtime_globals.game_sound.play("menu")
                self.selected_index = (self.selected_index - 1) % len(self.pets)
                self.adjust_scroll()
            elif input_action == "A":
                runtime_globals.game_sound.play("menu")
                return True
            elif input_action == "B":
                runtime_globals.game_sound.play("cancel")
                change_scene("game")
        return False

    def adjust_scroll(self) -> None:
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + self.max_visible_items:
            self.scroll_offset = self.selected_index - self.max_visible_items + 1

    def draw(self, surface: pygame.Surface) -> None:
        """
        Redraw everything directly, no caching.
        """
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

            if pet.get_sprite(0):
                sprite = pygame.transform.scale(pet.get_sprite(0), (OPTION_ICON_SIZE, OPTION_ICON_SIZE))
                blit_with_shadow(surface, sprite, (PAGE_MARGIN + LEFT_PADDING, y_pos + int(6 * UI_SCALE)))

                flag = self.module_flags.get(pet.module)
                if flag:
                    blit_with_shadow(surface, flag, (PAGE_MARGIN + LEFT_PADDING, y_pos + int(6 * UI_SCALE)))

            name_text = self.font.render(f"{pet.name}", True, FONT_COLOR_DEFAULT)
            stage_name = STAGES[pet.stage] if pet.stage < len(STAGES) else "Unknown"
            attribute_text = self.font.render(f"{stage_name} | {pet.attribute}", True, (200, 200, 200))

            blit_with_shadow(surface, name_text, (PAGE_MARGIN + ITEM_HEIGHT + LEFT_PADDING, y_pos))
            blit_with_shadow(surface, attribute_text, (PAGE_MARGIN + ITEM_HEIGHT + LEFT_PADDING, y_pos + int(25 * UI_SCALE)))

            if idx == self.selected_index:
                pygame.draw.rect(
                    surface,
                    FONT_COLOR_GREEN,
                    (PAGE_MARGIN, y_pos, SCREEN_WIDTH - PAGE_MARGIN * 2, ITEM_HEIGHT),
                    2
                )

    def get_selected_pet(self):
        return self.pets[self.selected_index]
