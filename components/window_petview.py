import pygame
from core import game_globals, runtime_globals
from core.constants import *
from core.utils import blit_with_shadow, get_font

class WindowPetList:
    def __init__(self, get_targets_callback, strategy_options=["Selected pets", "Pets in need"]):
        self.get_targets_callback = get_targets_callback
        self.strategy_options = strategy_options
        self.selectionBackground = pygame.image.load(PET_SELECTION_BACKGROUND_PATH).convert_alpha()

        # Cache processed sprites to avoid recalculating every frame
        self.scaled_sprites = {}
        self.transparent_sprites = {}
        self.selected_indices = []
        self.cursor_index = 0
        self.max_selection = 2
        self.select_mode = False

    def get_scaled_sprite(self, pet):
        """Returns a cached version of the scaled sprite."""
        if pet not in self.scaled_sprites:
            sprite = pet.get_sprite(0).convert_alpha()
            sprite = pygame.transform.scale(sprite, (PET_ICON_SIZE, PET_ICON_SIZE))
            self.scaled_sprites[pet] = sprite
        return self.scaled_sprites[pet]

    def get_transparent_sprite(self, pet):
        """Returns a cached version of the transparent sprite."""
        if pet not in self.transparent_sprites:
            sprite = self.get_scaled_sprite(pet).copy()
            sprite.fill((255, 255, 255, 100), special_flags=pygame.BLEND_RGBA_MULT)  # Fast alpha blending
            self.transparent_sprites[pet] = sprite
        return self.transparent_sprites[pet]

    def draw(self, surface: pygame.Surface):
        """Draws the pet selection screen with optimized transparency handling."""
        pets = game_globals.pet_list
        targets = self.get_targets_callback()

        if pets:
            available_width = SCREEN_WIDTH  # SCREEN_WIDTH - margins
            spacing = available_width // max(1, len(pets))
            start_x = 0
            y = SCREEN_HEIGHT - self.selectionBackground.get_height() + 24

            surface.blit(self.selectionBackground, (start_x, SCREEN_HEIGHT - self.selectionBackground.get_height()))
            if self.select_mode:
                font = get_font(FONT_SIZE_SMALL)
                strategy_text = font.render("Jogress", True, FONT_COLOR_DEFAULT)
                strategy_x, strategy_y = 10, SCREEN_HEIGHT - self.selectionBackground.get_height()
                blit_with_shadow(surface, strategy_text, (strategy_x, strategy_y))
            else:
                font = get_font(FONT_SIZE_SMALL)
                strategy_text = font.render(self.strategy_options[runtime_globals.strategy_index], True, FONT_COLOR_DEFAULT)
                strategy_x, strategy_y = 10, SCREEN_HEIGHT - self.selectionBackground.get_height()
                blit_with_shadow(surface, strategy_text, (strategy_x, strategy_y))

            for i, pet in enumerate(pets):
                if pet in targets:
                    sprite = self.get_scaled_sprite(pet)  # Normal sprite
                else:
                    sprite = self.get_transparent_sprite(pet)  # Cached transparent sprite

                x = start_x + i * spacing + (spacing - sprite.get_width()) // 2
                blit_with_shadow(surface, sprite, (x, y))

                if self.select_mode:
                    # Draw selection highlight (blue)
                    if i in getattr(self, "selected_indices", []):
                        pygame.draw.rect(surface, FONT_COLOR_GREEN, (x - 2, y - 2, sprite.get_width() + 4, sprite.get_height() + 4), 2)

                    # Draw cursor highlight (yellow)
                    if i == getattr(self, "cursor_index", -1):
                        pygame.draw.rect(surface, FONT_COLOR_YELLOW, (x - 4, y - 4, sprite.get_width() + 8, sprite.get_height() + 8), 2)

    def get_selected_pets(self):
        return [game_globals.pet_list[i] for i in self.selected_indices]
    
    def handle_input(self, input_action):
        if input_action == "LEFT":
            runtime_globals.game_sound.play("menu")
            self.cursor_index = (self.cursor_index - 1) % len(game_globals.pet_list)
        elif input_action == "RIGHT":
            runtime_globals.game_sound.play("menu")
            self.cursor_index = (self.cursor_index + 1) % len(game_globals.pet_list)
        elif input_action == "A":
            if game_globals.pet_list[self.cursor_index] in self.get_targets_callback():
                runtime_globals.game_sound.play("menu")
                if self.cursor_index in self.selected_indices:
                    self.selected_indices.remove(self.cursor_index)
                elif len(self.selected_indices) < self.max_selection:
                    self.selected_indices.append(self.cursor_index)
            else:
                runtime_globals.game_sound.play("cancel")
