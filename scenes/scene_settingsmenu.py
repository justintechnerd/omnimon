import pygame
import os

from components.window_background import WindowBackground
from core import game_globals, runtime_globals
from core.constants import *
from core.utils import blit_with_shadow, change_scene, get_font, sprite_load
from core.utils_unlocks import get_unlocked_backgrounds, is_unlocked


class SceneSettingsMenu:
    """
    Scene for navigating game settings, including background selection.
    """

    def __init__(self) -> None:
        """Initializes the settings menu."""
        self.background = WindowBackground(False)
        self.font = get_font(FONT_SIZE_MEDIUM)

        # Main options menu
        self.options = [
            "Digidex",      
            "Freezer Box",  
            "Unlockables",  
            "Settings"      
        ]
        
        # Settings submenu
        self.settings_options = [
            "Background",
            "Show Clock",
            "Sound",
            "Debug"
        ]

        # Load sprites for visual indicators
        self.settings_sprites = {
            "Show Clock": {"On": sprite_load("resources/IconOn.png"), "Off": sprite_load("resources/IconOff.png")},
            "Debug": {"On": sprite_load("resources/IconOn.png"), "Off": sprite_load("resources/IconOff.png")},
            "Sound": {
                0: sprite_load("resources/Sound0.png"),
                1: sprite_load("resources/Sound1.png"),
                2: sprite_load("resources/Sound2.png")
            }
        }

        self.mode = "menu"  # Default mode starts with the main options menu
        self.unlockables_data = []  # Holds unlockables progress for modules
        self.load_unlockables()

        self.selected_index = 0

        self.unlocked_backgrounds = [
            (module.name, background) for module in runtime_globals.game_modules.values()
            for background in get_unlocked_backgrounds(module.name)
        ]

        self.current_bg_index = self.get_current_background_index()
        runtime_globals.game_console.log("[SceneSettingsMenu] Settings menu loaded.")

    def load_unlockables(self):
        """Loads unlockable progress for all game modules."""
        self.unlockables_data = []
        
        for module in runtime_globals.game_modules.values():
            unlocks = module.unlocks  # Get unlockable content
            unlocked_backgrounds = sum(1 for bg in unlocks["backgrounds"] if is_unlocked(module.name, "backgrounds", bg["name"]))
            unlocked_eggs = sum(1 for egg in unlocks["eggs"] if is_unlocked(module.name, "eggs", egg["name"]))
            unlocked_evolutions = sum(1 for evo in unlocks["evolutions"] if is_unlocked(module.name, "evolutions", evo["name"]))

            self.unlockables_data.append({
                "name": module.name,
                "icon": runtime_globals.game_module_flag.get(module.name, None),
                "backgrounds": (unlocked_backgrounds, len(unlocks["backgrounds"])),
                "eggs": (unlocked_eggs, len(unlocks["eggs"])),
                "evolutions": (unlocked_evolutions, len(unlocks["evolutions"]))
            })

    def get_current_background_index(self) -> int:
        """Gets index of current background in the unlocked list."""
        if not game_globals.game_background:
            return 0
        for i, (mod, name) in enumerate(self.unlocked_backgrounds):
            if name == game_globals.game_background and mod == game_globals.background_module_name:
                return i
        return 0

    def draw(self, surface: pygame.Surface) -> None:
        """Draws the appropriate menu based on the current mode."""
        self.background.draw(surface)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((50, 50, 50, 200))  

        title_font = get_font(FONT_SIZE_LARGE)
        option_font = get_font(FONT_SIZE_MEDIUM)

        if self.mode == "unlockables":
            blit_with_shadow(surface, overlay, (0, 0))
            title_surface = title_font.render("Unlockables", True, (255, 200, 50))
            blit_with_shadow(surface, title_surface, (SCREEN_WIDTH // 2 - title_surface.get_width() // 2, 10))

            visible_start = max(0, self.selected_index - 2)  # Ensure selected item stays in view
            visible_unlockables = self.unlockables_data[visible_start:visible_start + 5]  # Show up to 5 modules at once

            start_y = 54 - self.selected_index * 90
            for i, module in enumerate(visible_unlockables):
                if i < self.selected_index:
                    continue
                actual_index = visible_start + i  # Adjust index for scrolling
                text_surface = option_font.render(module["name"], True, (255, 255, 0) if actual_index == self.selected_index else FONT_COLOR_DEFAULT)
                blit_with_shadow(surface, text_surface, (25, start_y + i * 90))  # Increased spacing between modules

                start_y += 25
                # Display unlock progress below the module name with more spacing
                unlock_text = [
                    f"Backgrounds: {module['backgrounds'][0]} of {module['backgrounds'][1]}",
                    f"Eggs: {module['eggs'][0]} of {module['eggs'][1]}",
                    f"Evolutions: {module['evolutions'][0]} of {module['evolutions'][1]}"
                ]
                for j, line in enumerate(unlock_text):
                    unlock_surface = option_font.render(line, True, FONT_COLOR_DEFAULT)
                    blit_with_shadow(surface, unlock_surface, (35, start_y + i * 90 + j * 25))  # Increased spacing between fields

        elif self.mode == "menu":
            blit_with_shadow(surface, overlay, (0, 0))
            title_surface = title_font.render("Settings Menu", True, (255, 200, 50))
            options_list = self.options
        elif self.mode == "settings":
            blit_with_shadow(surface, overlay, (0, 0))
            title_surface = title_font.render("Settings", True, (255, 200, 50))
            options_list = self.settings_options
        elif self.mode == "background":
            title_surface = title_font.render("Select Background", True, (255, 200, 50))
            options_list = []  # No list needed for background selection

        blit_with_shadow(surface, title_surface, (SCREEN_WIDTH // 2 - title_surface.get_width() // 2, 10))

        if self.mode in ["menu", "settings"]:
            for i, label in enumerate(options_list):
                color = (255, 255, 0) if i == self.selected_index else FONT_COLOR_DEFAULT
                text_surface = option_font.render(label, True, color)
                blit_with_shadow(surface, text_surface, (25, 60 + i * 40))

                if self.mode == "settings":
                    sprite = self.get_setting_sprite(label)
                    if sprite:
                        surface.blit(sprite, (SCREEN_WIDTH - sprite.get_width() - 20, 60 + i * 40))

                if i == self.selected_index:  # Highlight selected option
                    pygame.draw.rect(surface, (255, 200, 50), (15, 54 + i * 40, SCREEN_WIDTH - 30, 36), 2)

        elif self.mode == "background":
            if self.unlocked_backgrounds:
                mod, name = self.unlocked_backgrounds[self.current_bg_index]
                bg_surface = option_font.render(name, True, (255, 255, 0))
                blit_with_shadow(surface, bg_surface, (SCREEN_WIDTH // 2 - bg_surface.get_width() // 2, SCREEN_HEIGHT // 2))

    def get_setting_sprite(self, label: str):
        """Returns the correct sprite for a setting."""
        if label == "Show Clock":
            return self.settings_sprites["Show Clock"]["On"] if game_globals.showClock else self.settings_sprites["Show Clock"]["Off"]
        elif label == "Debug":
            return self.settings_sprites["Debug"]["On"] if game_globals.debug else self.settings_sprites["Debug"]["Off"]
        elif label == "Sound":
            return self.settings_sprites["Sound"].get(game_globals.sound, self.settings_sprites["Sound"][0])
        return None
    
    def handle_event(self, input_action) -> None:
        """Handles navigation and updates mode accordingly."""
        if input_action:
            if self.mode == "background":
                if input_action == "START" or input_action == "B":
                    self.mode = "settings"
                    runtime_globals.game_sound.play("cancel")
                elif input_action in ("LEFT", "RIGHT"):
                    runtime_globals.game_sound.play("menu")
                    self.change_background(increase=(input_action == "RIGHT"))
                return
            elif self.mode == "unlockables":
                if input_action in ["START", "B"]:
                    runtime_globals.game_sound.play("cancel")
                    self.mode = "menu"
                if input_action == "UP":
                    runtime_globals.game_sound.play("menu")
                    self.selected_index = (self.selected_index - 1) % len(self.unlockables_data)

                elif input_action == "DOWN":
                    runtime_globals.game_sound.play("menu")
                    self.selected_index = (self.selected_index + 1) % len(self.unlockables_data)
            elif input_action == "START" or input_action == "B":
                runtime_globals.game_sound.play("cancel")
                self.exit_to_game()

            elif input_action == "UP":
                runtime_globals.game_sound.play("menu")
                self.selected_index = (self.selected_index - 1) % len(self.settings_options if self.mode == "settings" else self.options)

            elif input_action == "DOWN":
                runtime_globals.game_sound.play("menu")
                self.selected_index = (self.selected_index + 1) % len(self.settings_options if self.mode == "settings" else self.options)
            elif input_action in ("LEFT", "RIGHT"):
                runtime_globals.game_sound.play("menu")
                if self.mode == "settings":
                    self.change_option(increase=(input_action == "RIGHT"))

            elif input_action == "A":
                self.handle_enter()

    def handle_enter(self) -> None:
        """Handles selection and transitions between modes."""
        runtime_globals.game_sound.play("menu")

        if self.mode == "settings" and self.settings_options[self.selected_index] == "Background":
            self.mode = "background"
            runtime_globals.game_console.log("[SceneSettingsMenu] Entered Background Selection.")
            return
        
        if self.mode == "menu":
            selected_option = self.options[self.selected_index]
            if selected_option == "Digidex":
                runtime_globals.game_console.log("[SceneSettingsMenu] Opening the Digidex.")
                change_scene("digidex")
            elif selected_option == "Freezer Box":
                runtime_globals.game_console.log("[SceneSettingsMenu] Opening the Freezer Box.")
                change_scene("freezer")
            elif selected_option == "Unlockables":
                runtime_globals.game_console.log("[SceneSettingsMenu] Opening Unlockables view.")
                self.mode = "unlockables"
                self.load_unlockables()
                self.selected_index = 0
            elif selected_option == "Settings":
                runtime_globals.game_console.log("[SceneSettingsMenu] Opening Settings menu.")
                self.mode = "settings"
                self.current_submenu = "Settings"
                self.selected_index = 0

    def exit_to_game(self) -> None:
        """Returns to the main settings menu."""
        if self.mode == "settings":
            self.selected_index = 0
            self.mode = "menu" 
            runtime_globals.game_console.log("[SceneSettingsMenu] Returning to main settings menu.")
        else:
            runtime_globals.game_console.log("[SceneSettingsMenu] Returning to main game.")
            change_scene("game")

    def change_option(self, increase: bool) -> None:
        """Changes the value of the selected setting."""
        option = self.settings_options[self.selected_index]

        if option == "Show Clock":
            game_globals.showClock = not game_globals.showClock
            runtime_globals.game_console.log(f"[SceneSettingsMenu] Show Clock set to {game_globals.showClock}")
        elif option == "Debug":
            game_globals.debug = not game_globals.debug
            runtime_globals.game_console.log(f"[SceneSettingsMenu] Debug set to {game_globals.debug}")
        elif option == "Sound":
            game_globals.sound = min(2, max(0, game_globals.sound + (1 if increase else -1)))
            runtime_globals.game_console.log(f"[SceneSettingsMenu] Sound set to {game_globals.sound}")

    def change_background(self, increase: bool) -> None:
        """Changes background index while keeping it cyclic."""
        if not self.unlocked_backgrounds:
            return  

        self.current_bg_index = (self.current_bg_index + 1) % len(self.unlocked_backgrounds) if increase else (self.current_bg_index - 1) % len(self.unlocked_backgrounds)

        mod, name = self.unlocked_backgrounds[self.current_bg_index]
        game_globals.game_background = name
        game_globals.background_module_name = mod

        self.background.load_sprite(False)
        runtime_globals.game_console.log(f"[SceneSettingsMenu] Background changed to {name} ({mod})")

    def update(self):
        pass