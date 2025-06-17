import pygame
from components.scrolling_text import ScrollingText
from core import game_globals, runtime_globals
from core.constants import *
from core.utils.pygame_utils import blit_with_shadow, get_font

class WindowParty:
    def __init__(self):
        self.font = get_font(FONT_SIZE_SMALL)
        self.option_font = get_font(FONT_SIZE_MEDIUM)
        self.selected_index = 0
        self.scaled_pet_sprites = {}
        self.scaled_module_flags = {}
        self.name_scrolls = {}
        self._last_cache = None
        self._last_cache_key = None
        self.generate_pet_sprites()
        self.generate_module_flags()

    def generate_pet_sprites(self):
        for pet in game_globals.pet_list:
            original_sprite = runtime_globals.pet_sprites[pet][0]
            # Scale pet sprite proportionally
            self.scaled_pet_sprites[pet.name] = pygame.transform.scale(
                original_sprite, (int(60 * UI_SCALE), int(60 * UI_SCALE))
            )

    def generate_module_flags(self):
        for module in runtime_globals.game_modules.values():
            flag_img = runtime_globals.game_module_flag[module.name]
            # Scale module flag proportionally
            self.scaled_module_flags[module.name] = pygame.transform.scale(
                flag_img, (int(60 * UI_SCALE), int(60 * UI_SCALE))
            )

    def _precompute_party_surface(self):
        # Cache key includes selected index, pet list, and UI_SCALE
        cache_key = (
            tuple(pet.name for pet in game_globals.pet_list),
            self.selected_index,
            UI_SCALE,
            SCREEN_WIDTH,
            SCREEN_HEIGHT
        )
        if self._last_cache_key == cache_key and self._last_cache is not None:
            return self._last_cache

        width_scale = SCREEN_WIDTH / 240
        height_scale = SCREEN_HEIGHT / 240
        slot_positions = [
            (int(20 * width_scale), int(40 * height_scale)),
            (int(130 * width_scale), int(40 * height_scale)),
            (int(20 * width_scale), int(140 * height_scale)),
            (int(130 * width_scale), int(140 * height_scale)),
        ]
        slot_size = int(90 * UI_SCALE)
        party_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        for i in range(4):
            x, y = slot_positions[i]
            is_filled = i < len(game_globals.pet_list)
            attr_color = (
                ATTR_COLORS.get(game_globals.pet_list[i].attribute, (171, 71, 188))
                if is_filled else (50, 50, 50)
            )
            pygame.draw.rect(party_surface, attr_color, (x, y, slot_size, slot_size))
            if i == self.selected_index:
                pygame.draw.rect(party_surface, FONT_COLOR_GREEN, (x, y, slot_size, slot_size), 3)

            if is_filled:
                pet = game_globals.pet_list[i]
                # Scaled module flag
                module_flag = self.scaled_module_flags.get(pet.module)
                if module_flag:
                    blit_with_shadow(party_surface, module_flag, (x + int(15 * width_scale), y + int(3 * height_scale)))

                # Scaled pet sprite
                pet_sprite = self.scaled_pet_sprites.get(pet.name)
                if pet_sprite:
                    party_surface.blit(pet_sprite, (x + int(15 * width_scale), y + int(15 * height_scale)))
            else:
                instructions = ["+", "Press A", "Add Egg"]
                for j, line in enumerate(instructions):
                    text_surface = self.font.render(line, True, FONT_COLOR_GRAY)
                    text_x = x + (slot_size - text_surface.get_width()) // 2
                    blit_with_shadow(party_surface, text_surface, (text_x, y + int(10 * width_scale) + j * int(20 * height_scale)))

        self._last_cache = party_surface
        self._last_cache_key = cache_key
        return party_surface

    def draw(self, surface):
        # Draw static/cached party surface
        party_surface = self._precompute_party_surface()
        surface.blit(party_surface, (0, 0))

        # Draw dynamic name scrolls (always update every frame)
        width_scale = SCREEN_WIDTH / 240
        height_scale = SCREEN_HEIGHT / 240
        slot_positions = [
            (int(20 * width_scale), int(40 * height_scale)),
            (int(130 * width_scale), int(40 * height_scale)),
            (int(20 * width_scale), int(140 * height_scale)),
            (int(130 * width_scale), int(140 * height_scale)),
        ]
        slot_size = int(90 * UI_SCALE)
        for i in range(4):
            x, y = slot_positions[i]
            is_filled = i < len(game_globals.pet_list)
            if is_filled:
                pet = game_globals.pet_list[i]
                text_surface = self.font.render(pet.name, True, FONT_COLOR_DEFAULT)
                max_name_width = int(80 * UI_SCALE)
                if pet.name not in self.name_scrolls or \
                   (self.name_scrolls[pet.name] and self.name_scrolls[pet.name].max_width != max_name_width):
                    if text_surface.get_width() > max_name_width:
                        self.name_scrolls[pet.name] = ScrollingText(text_surface, max_name_width, speed=0.5)
                    else:
                        self.name_scrolls[pet.name] = None

                scroll_obj = self.name_scrolls[pet.name]
                name_y = y + int(65 * height_scale)
                if scroll_obj:
                    scroll_obj.update()
                    scroll_obj.draw(surface, (x + int(5 * width_scale), name_y))
                else:
                    text_x = x + (slot_size - text_surface.get_width()) // 2
                    blit_with_shadow(surface, text_surface, (text_x, name_y))

    def handle_event(self, input_action):
        prev_index = self.selected_index
        if input_action == "LEFT":
            runtime_globals.game_sound.play("menu")
            self.selected_index = (self.selected_index - 1) % 4
        elif input_action == "RIGHT":
            runtime_globals.game_sound.play("menu")
            self.selected_index = (self.selected_index + 1) % 4
        if input_action == "UP":
            runtime_globals.game_sound.play("menu")
            self.selected_index = (self.selected_index - 2) % 4
        elif input_action == "DOWN":
            runtime_globals.game_sound.play("menu")
            self.selected_index = (self.selected_index + 2) % 4
        # Invalidate cache if index changed
        if self.selected_index != prev_index:
            self._last_cache = None
