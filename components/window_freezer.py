import pygame
from core import runtime_globals
from core.constants import *
from core.utils import blit_with_shadow, get_font

GRID_DIM = 5
CELL_SIZE = 40  # Includes cell content and margins
MARGIN = 1
CONTENT_SIZE = 32  # Pet sprite and module flag
WINDOW_SIZE = GRID_DIM * CELL_SIZE

class WindowFreezer:
    def __init__(self, freezer_page):
        self.font = get_font(FONT_SIZE_SMALL)
        self.page_index = 0
        self.cursor_row = 0
        self.cursor_col = 0
        self.set_page(freezer_page)

    def set_page(self, freezer_page):
        self.pet_grid = freezer_page.pet_grid
        self.scaled_pet_sprites = {}
        self.scaled_module_flags = {}
        self.prepare_sprites()

    def prepare_sprites(self):
        for pet_key, sprite_list in runtime_globals.pet_sprites.items():
            original_sprite = sprite_list[0]
            self.scaled_pet_sprites[pet_key.name] = pygame.transform.scale(original_sprite, (CONTENT_SIZE, CONTENT_SIZE))
        for module_name, module_flag in runtime_globals.game_module_flag.items():
            self.scaled_module_flags[module_name] = pygame.transform.scale(module_flag, (CONTENT_SIZE, CONTENT_SIZE))

    def draw(self, surface):
        for row in range(GRID_DIM):
            for col in range(GRID_DIM):
                x = 20 + col * CELL_SIZE
                y = 35 + row * CELL_SIZE
                pet = self.pet_grid[row][col] if row < len(self.pet_grid) and col < len(self.pet_grid[row]) else None

                # Choose background color
                if pet:
                    attr_color = ATTR_COLORS.get(pet.attribute, ATTR_COLORS[""])
                else:
                    attr_color = (50, 50, 50)

                # Draw cell background
                pygame.draw.rect(surface, attr_color, (x, y, CELL_SIZE - MARGIN, CELL_SIZE - MARGIN))

                if pet:
                    # Module flag
                    module_flag = self.scaled_module_flags.get(pet.module)
                    if module_flag:
                        flag_x = x + (CELL_SIZE - CONTENT_SIZE) // 2
                        flag_y = y + 1
                        blit_with_shadow(surface, module_flag, (flag_x, flag_y))

                    # Pet sprite
                    pet_sprite = self.scaled_pet_sprites.get(pet.name)
                    if pet_sprite:
                        sprite_x = x + (CELL_SIZE - CONTENT_SIZE) // 2
                        sprite_y = y + 5  # Below module flag
                        surface.blit(pet_sprite, (sprite_x, sprite_y))
                else:
                    # Optional: Draw "+" in gray for empty slots
                    placeholder_surface = self.font.render("-", True, FONT_COLOR_GRAY)
                    text_x = x + (CELL_SIZE - placeholder_surface.get_width()) // 2
                    text_y = y + (CELL_SIZE - placeholder_surface.get_height()) // 2
                    blit_with_shadow(surface, placeholder_surface, (text_x, text_y))

                # Draw cursor
                if row == self.cursor_row and col == self.cursor_col:
                    pygame.draw.rect(surface, FONT_COLOR_GREEN, (x, y, CELL_SIZE - MARGIN, CELL_SIZE - MARGIN), 2)

    def handle_event(self, input_action):
        pass
