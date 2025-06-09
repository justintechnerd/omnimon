import pygame
from core import runtime_globals
from core.constants import *
from core.utils import blit_with_shadow, get_font

GRID_DIM = 5
CELL_SIZE = 40  # Includes content and margins
MARGIN = 1
CONTENT_SIZE = 32
WINDOW_SIZE = GRID_DIM * CELL_SIZE


class WindowFreezer:
    def __init__(self, freezer_page):
        self.font = get_font(FONT_SIZE_SMALL)
        self.page_index = 0
        self.cursor_row = 0
        self.cursor_col = 0
        self.scaled_pet_sprites = {}
        self.scaled_module_flags = {}
        self.set_page(freezer_page)

    def set_page(self, freezer_page):
        self.pet_grid = freezer_page.pet_grid
        self.prepare_sprites()

    def prepare_sprites(self):
        # 🚀 Cache scaled versions of pet sprites
        for pet_key, sprite_list in runtime_globals.pet_sprites.items():
            if sprite_list:
                original_sprite = sprite_list[0]
                scaled = pygame.transform.scale(original_sprite, (CONTENT_SIZE, CONTENT_SIZE))
                self.scaled_pet_sprites[pet_key.name] = scaled

        # 🚀 Cache scaled versions of module flags
        for module_name, flag_surface in runtime_globals.game_module_flag.items():
            if flag_surface:
                scaled = pygame.transform.scale(flag_surface, (CONTENT_SIZE, CONTENT_SIZE))
                self.scaled_module_flags[module_name] = scaled

    def draw(self, surface):
        for row in range(GRID_DIM):
            for col in range(GRID_DIM):
                x = 20 + col * CELL_SIZE
                y = 35 + row * CELL_SIZE
                pet = self._get_pet_at(row, col)

                # Background
                attr_color = ATTR_COLORS.get(pet.attribute, ATTR_COLORS[""]) if pet else (50, 50, 50)
                pygame.draw.rect(surface, attr_color, (x, y, CELL_SIZE - MARGIN, CELL_SIZE - MARGIN))

                if pet:
                    # Module flag (on top)
                    flag = self.scaled_module_flags.get(pet.module)
                    if flag:
                        fx = x + (CELL_SIZE - CONTENT_SIZE) // 2
                        fy = y + 1
                        blit_with_shadow(surface, flag, (fx, fy))

                    # Pet sprite (below flag)
                    pet_sprite = self.scaled_pet_sprites.get(pet.name)
                    if pet_sprite:
                        sx = x + (CELL_SIZE - CONTENT_SIZE) // 2
                        sy = y + 5
                        surface.blit(pet_sprite, (sx, sy))
                else:
                    # Placeholder for empty slot
                    dash = self.font.render("-", True, FONT_COLOR_GRAY)
                    dx = x + (CELL_SIZE - dash.get_width()) // 2
                    dy = y + (CELL_SIZE - dash.get_height()) // 2
                    blit_with_shadow(surface, dash, (dx, dy))

                # Cursor
                if row == self.cursor_row and col == self.cursor_col:
                    pygame.draw.rect(surface, FONT_COLOR_GREEN, (x, y, CELL_SIZE - MARGIN, CELL_SIZE - MARGIN), 2)

    def _get_pet_at(self, row, col):
        if row < len(self.pet_grid) and col < len(self.pet_grid[row]):
            return self.pet_grid[row][col]
        return None

    def handle_event(self, input_action):
        # Future input handling
        pass
