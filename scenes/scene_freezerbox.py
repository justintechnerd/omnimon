import json
import os
import pickle
import pygame
from components.window_freezer import CELL_SIZE, MARGIN, WindowFreezer
from components.window_menu import WindowMenu
from components.window_party import WindowParty
from components.window_status import WindowStatus
from core import game_globals, runtime_globals
from core.constants import *
from core.game_freezer import GameFreezer
from core.utils import blit_with_shadow, change_scene, get_font

class SceneFreezerBox:
    def __init__(self):
        self.font = get_font(FONT_SIZE_SMALL)
        self.bg_sprite = pygame.image.load("resources/Digidex.png").convert()
        self.bg_frame = 0
        self.bg_timer = 0
        self.bg_frame_width = self.bg_sprite.get_width() // 6
        self.mode = "party"
        self.party_view = WindowParty()
        self.freezer_pets = self.load_freezer_data()
        self.current_freezer_page = 0
        self.freezer_view = WindowFreezer(self.freezer_pets[self.current_freezer_page])
        self.menu = WindowMenu()
        self.window_status = None
        self.current_page = 1
        runtime_globals.game_console.log("[Scene_FreezerBox] Loaded.")
        self.load_current_freezer_sprites()

    def load_current_freezer_sprites(self):
        # Load sprites for pets on the current freezer page
        current_page = self.freezer_pets[self.current_freezer_page]
        for pet in current_page.pets:
            if pet not in runtime_globals.pet_sprites:
                pet.load_sprite()

    def switch_freezer_page(self, direction):
        max_pages = len(self.freezer_pets)
        self.current_freezer_page = (self.current_freezer_page + direction) % max_pages
        runtime_globals.game_console.log(f"Switched to freezer page {self.current_freezer_page}")
        self.freezer_view.set_page(self.freezer_pets[self.current_freezer_page])
        self.load_current_freezer_sprites()

    def load_freezer_data(self):
        file_path = "save/freezer.pkl"
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                pets = pickle.load(f)
                for page in pets:
                    page.rebuild()
                return pets
        else:
            pets = [GameFreezer([], i, "default_bg", "default_module") for i in range(10)]
            self.save_freezer_data(pets)
            return pets

    def save_freezer_data(self, pets=None):
        pets = pets or self.freezer_pets
        with open("save/freezer.pkl", "wb") as f:
            pickle.dump(pets, f)

    def update(self):
        self.bg_timer += 1
        if self.bg_timer >= 3:
            self.bg_timer = 0
            self.bg_frame = (self.bg_frame + 1) % 6

    def draw(self, surface):
        
        
        frame_rect = pygame.Rect(self.bg_frame * self.bg_frame_width, 0, self.bg_frame_width, SCREEN_HEIGHT)
        surface.blit(self.bg_sprite, (0, 0), frame_rect)

        if self.window_status:
            self.window_status.draw_page(surface, self.current_page)
            return
        if self.mode == "party":
            self.party_view.draw(surface)
            option1Color = FONT_COLOR_BLUE
            option2Color = FONT_COLOR_GRAY
        else:
            option2Color = FONT_COLOR_BLUE
            option1Color = FONT_COLOR_GRAY
            self.freezer_view.draw(surface)

        pygame.draw.rect(surface, option1Color, (20, 10, 90, 25))
        pygame.draw.rect(surface, option2Color, (130, 10, 90, 25))

        view_surface = self.font.render(f"Party", True, FONT_COLOR_DEFAULT)
        blit_with_shadow(surface, view_surface, (21 + view_surface.get_width() // 2, 11))

        view_surface = self.font.render(f"Box {self.current_freezer_page+1}/10", True, FONT_COLOR_DEFAULT)
        blit_with_shadow(surface, view_surface, (101 + view_surface.get_width() // 2, 11))
        
        self.menu.draw(surface)

    def handle_event(self, input_action):
        # Mode switching with SELECT
        if input_action == "SELECT":
            runtime_globals.game_sound.play("menu")
            self.mode = "party" if self.mode == "freezer" else "freezer"
            runtime_globals.game_console.log(f"[SceneFreezerBox] Switched to {self.mode}")
            if self.mode == "freezer":
                self.load_current_freezer_sprites()
            return

        if self.window_status:
            self.handle_status_input(input_action)
            return
        # If menu is active, handle its events first
        if self.menu.active:
            self.handle_menu_input(input_action)
            return

        # Mode-specific input handling
        if self.mode == "party":
            self.handle_party_input(input_action)
        else:
            self.handle_freezer_input(input_action)

    def clean_unused_pet_sprites(self):
        runtime_globals.pet_sprites = {}
        for pet in game_globals.pet_list:
            pet.load_sprite()

    def handle_status_input(self, input_action):
        if input_action == "LEFT":
            runtime_globals.game_sound.play("menu")
            self.current_page = 4 if self.current_page == 1 else self.current_page - 1
            runtime_globals.game_console.log(f"Status page {self.current_page}.")
        elif input_action == "RIGHT":
            runtime_globals.game_sound.play("menu")
            self.current_page = 1 if self.current_page == 4 else self.current_page + 1
            runtime_globals.game_console.log(f"Status page {self.current_page}.")
        elif input_action == "B":
            runtime_globals.game_sound.play("cancel")
            self.window_status = None

    def handle_menu_input(self, input_action):
        self.menu.handle_event(input_action)
        if input_action == "A":
            runtime_globals.game_sound.play("menu")
            if self.mode == "party":
                selected_pet = game_globals.pet_list[self.party_view.selected_index]
            else:
                row, col = self.freezer_view.cursor_row, self.freezer_view.cursor_col
                selected_pet = self.freezer_view.pet_grid[row][col]

            if self.menu.menu_index == 0:  # Add or Store
                if self.mode == "party":
                    # Store to freezer
                    game_globals.pet_list.pop(self.party_view.selected_index)
                    self.freezer_pets[self.current_freezer_page].pets.append(selected_pet)
                    runtime_globals.game_console.log(f"Stored {selected_pet.name}.")
                else:
                    # Move from freezer to party
                    self.freezer_pets[self.current_freezer_page].pets.remove(selected_pet)
                    game_globals.pet_list.append(selected_pet)
                    runtime_globals.game_console.log(f"Moved {selected_pet.name} to party.")

                # Save updated freezer state
                self.save_freezer_data()
                self.freezer_pets[self.current_freezer_page].rebuild()
                # Refresh freezer view to reflect current page pets
                self.freezer_view.set_page(self.freezer_pets[self.current_freezer_page])
                # Update sprites
                self.load_current_freezer_sprites()
            elif self.menu.menu_index == 1:  # Status
                runtime_globals.game_console.log(f"Viewing status of {selected_pet.name}.")
                self.window_status = WindowStatus(selected_pet)  # Replace `pet` with your active pet object
                self.current_page = 1
            self.menu.close()
        elif input_action == "B":
            runtime_globals.game_sound.play("cancel")
            self.menu.close()

    def handle_party_input(self, input_action):
        self.party_view.handle_event(input_action)
        if input_action == "A" and self.party_view.selected_index < len(game_globals.pet_list):
            runtime_globals.game_sound.play("menu")
            x, y = [(20, 40), (130, 40), (20, 140), (130, 140)][self.party_view.selected_index]
            menu_x = 20 if x > SCREEN_WIDTH // 2 else SCREEN_WIDTH - 120
            menu_y = SCREEN_HEIGHT - 100
            self.menu.open((menu_x, menu_y), ["Store", "Stats"])
        elif input_action == "A":
            runtime_globals.game_sound.play("menu")
            self.clean_unused_pet_sprites()
            change_scene("egg")
        elif input_action == "B":
            runtime_globals.game_sound.play("cancel")
            self.clean_unused_pet_sprites()
            if len(game_globals.pet_list) == 0:
                change_scene("egg")
            else:
                change_scene("game")

    def handle_freezer_input(self, input_action):
        row, col = self.freezer_view.cursor_row, self.freezer_view.cursor_col
        max_row = 5 - 1
        max_col = 5 - 1

        if input_action == "UP":
            runtime_globals.game_sound.play("menu")
            row = max_row if row == 0 else row - 1
        elif input_action == "DOWN":
            runtime_globals.game_sound.play("menu")
            row = 0 if row == max_row else row + 1
        elif input_action == "LEFT":
            runtime_globals.game_sound.play("menu")
            if col == 0:
                self.switch_freezer_page(-1)
                col = max_col
            else:
                col -= 1
        elif input_action == "RIGHT":
            runtime_globals.game_sound.play("menu")
            if col == max_col:
                self.switch_freezer_page(1)
                col = 0
            else:
                col += 1
        elif input_action == "L":
            runtime_globals.game_sound.play("menu")
            self.switch_freezer_page(-1)
            return
        elif input_action == "R":
            runtime_globals.game_sound.play("menu")
            self.switch_freezer_page(1)
            return
        elif input_action == "A":
            runtime_globals.game_sound.play("menu")
            if row < len(self.freezer_view.pet_grid) and col < len(self.freezer_view.pet_grid[row]):
                pet = self.freezer_view.pet_grid[row][col]
                if pet:
                    runtime_globals.game_sound.play("menu")
                    pet_x = col * (CELL_SIZE + MARGIN) + 20
                    menu_x = 20 if pet_x > SCREEN_WIDTH // 2 else SCREEN_WIDTH - 120
                    menu_y = SCREEN_HEIGHT - 100
                    self.menu.open((menu_x, menu_y), ["Add", "Stats"])
            return
        elif input_action == "B":
            runtime_globals.game_sound.play("cancel")
            self.clean_unused_pet_sprites()
            if len(game_globals.pet_list) == 0:
                change_scene("egg")
            else:
                change_scene("game")
        # Update cursor
        self.freezer_view.cursor_row = row
        self.freezer_view.cursor_col = col