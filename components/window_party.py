import pygame
from components.scrolling_text import ScrollingText
from core import game_globals, runtime_globals
from core.constants import *
from core.constants import FONT_COLOR_GRAY
from core.utils import blit_with_shadow, get_font, sprite_load

class WindowParty:
    def __init__(self):
        self.font = get_font(FONT_SIZE_SMALL)
        self.option_font = get_font(FONT_SIZE_MEDIUM)
        self.selected_index = 0
        self.scaled_pet_sprites = {}
        self.scaled_module_flags = {}
        self.name_scrolls = {}
        self.generate_pet_sprites()
        self.generate_module_flags()

    def generate_pet_sprites(self):
        for pet in game_globals.pet_list:
            original_sprite = runtime_globals.pet_sprites[pet][0]
            self.scaled_pet_sprites[pet.name] = pygame.transform.scale(original_sprite, (60, 60))

    def generate_module_flags(self):
        for module in runtime_globals.game_modules.values():
            self.scaled_module_flags[module.name] = runtime_globals.game_module_flag[module.name]
            self.scaled_module_flags[module.name] = pygame.transform.scale(runtime_globals.game_module_flag[module.name], (60, 60))

    def draw(self, surface):
        slot_positions = [(20, 40), (130, 40), (20, 140), (130, 140)]
        for i in range(4):
            x, y = slot_positions[i]
            is_filled = i < len(game_globals.pet_list)
            attr_color = ATTR_COLORS.get(game_globals.pet_list[i].attribute, (171, 71, 188)) if is_filled else (50, 50, 50)
            pygame.draw.rect(surface, attr_color, (x, y, 90, 90))
            if i == self.selected_index:
                pygame.draw.rect(surface, FONT_COLOR_GREEN, (x, y, 90, 90), 3)

            if is_filled:
                pet = game_globals.pet_list[i]
                # Scaled module flag
                module_flag = self.scaled_module_flags.get(pet.module)
                if module_flag:
                    blit_with_shadow(surface, module_flag, (x + 15, y + 3))

                # Scaled pet sprite
                pet_sprite = self.scaled_pet_sprites.get(pet.name)
                if pet_sprite:
                    surface.blit(pet_sprite, (x + 15, y + 15))

                # Scrolling pet name
                text_surface = self.font.render(pet.name, True, FONT_COLOR_DEFAULT)
                max_name_width = 80

                if pet.name not in self.name_scrolls:
                    if text_surface.get_width() > max_name_width:
                        self.name_scrolls[pet.name] = ScrollingText(text_surface, max_name_width, speed=0.5)
                    else:
                        self.name_scrolls[pet.name] = None

                scroll_obj = self.name_scrolls[pet.name]
                name_y = y + 65
                if scroll_obj:
                    scroll_obj.update()
                    scroll_obj.draw(surface, (x + 5, name_y))
                else:
                    text_x = x + (90 - text_surface.get_width()) // 2
                    blit_with_shadow(surface, text_surface, (text_x, name_y))
            else:
                instructions = ["+", "Press A", "Add Egg"]
                for j, line in enumerate(instructions):
                    text_surface = self.font.render(line, True, FONT_COLOR_GRAY)
                    text_x = x + (90 - text_surface.get_width()) // 2
                    blit_with_shadow(surface, text_surface, (text_x, y + 10 + j * 20))

    def handle_event(self, input_action):
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
