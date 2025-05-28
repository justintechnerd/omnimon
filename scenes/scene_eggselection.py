"""
Scene Egg Selection
Allows the player to select an egg (stage 0 monster) from all available modules.
"""

from typing import Optional
import pygame
import os

from core import game_globals, runtime_globals
from core.constants import *
from core.game_digidex import register_digidex_entry
from core.game_pet import GamePet
from core.game_pet_dmc import GamePetDmC
from core.game_pet_penc import GamePetPenC
from core.utils import blit_with_shadow, change_scene, get_module, load_modules
from core.utils_unlocks import unlock_item

#=====================================================================
# SceneEggSelection
#=====================================================================
class SceneEggSelection:
    """
    Scene where the player selects an egg to hatch into a pet.
    """

    def __init__(self) -> None:
        """
        Initializes the egg selection scene by loading available modules and eggs.
        """
        self.eggs = self.load_eggs()
        self.current_index = 0
        self.egg_sprite = {}

        runtime_globals.game_console.log(f"[SceneEggSelection] Total eggs loaded: {len(self.eggs)}")
        self.background = pygame.image.load(EGG_BACKGROUND_PATH).convert_alpha()

        if self.eggs:
            self.load_egg_sprite()

    def load_eggs(self) -> list:
        """
        Loads all stage 0 monsters (eggs) from all modules.
        """
        eggs = []
        for module in runtime_globals.game_modules.values():
            eggs.extend(module.get_monsters_by_stage(0))
            for egg in eggs:
                register_digidex_entry(egg["name"], module.name, egg["version"])
        return eggs

    def load_egg_sprite(self) -> None:
        """
        Loads the sprite for the currently selected egg.
        """
        if not self.eggs:
            runtime_globals.game_console.log("[SceneEggSelection] Warning: No eggs available to load sprite.")
            self.egg_sprite = None
            return

        for egg in self.eggs:
            module = get_module(egg["module"])
            egg_name = egg["name"]
            folder_path = os.path.join(module.folder_path, "monsters", f"{egg_name}_dmc")
            frame_path = os.path.join(folder_path, "0.png")  # Load first frame only

            runtime_globals.game_console.log(f"[SceneEggSelection] Trying to load egg frame: {frame_path}")

            try:
                frame = pygame.image.load(frame_path).convert_alpha()
                self.egg_sprite[egg_name] = pygame.transform.scale(frame, (PET_WIDTH, PET_HEIGHT))
                runtime_globals.game_console.log(f"[SceneEggSelection] Successfully loaded egg sprite for {egg_name}")
            except pygame.error:
                self.egg_sprite = None
                runtime_globals.game_console.log(f"[SceneEggSelection] Error loading {frame_path}")

    def move_selection(self, direction: int) -> None:
        """
        Changes the selected egg based on direction (-1 for left, 1 for right).
        """
        if self.eggs:
            self.current_index = (self.current_index + direction) % len(self.eggs)
            runtime_globals.game_console.log(f"[SceneEggSelection] Changed selection to index {self.current_index}")
            self.load_egg_sprite()

    def get_selected_egg(self):
        """
        Returns the currently selected egg dictionary, or None if no eggs exist.
        """
        if self.eggs:
            return self.eggs[self.current_index]
        return None

    def update(self) -> None:
        """
        Updates the egg selection scene (no behavior needed currently).
        """
        pass

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draws the currently selected egg and its name onto the screen.
        """
        surface.blit(self.background, (0,0))

        if self.egg_sprite:
            egg_name = self.eggs[self.current_index]["name"]

            egg_x = (SCREEN_WIDTH - PET_WIDTH) // 2
            egg_y = (SCREEN_HEIGHT - PET_HEIGHT) // 2
            blit_with_shadow(surface, self.egg_sprite[egg_name], (egg_x, egg_y))
            blit_with_shadow(surface, runtime_globals.game_module_flag[self.eggs[self.current_index]["module"]], (egg_x, egg_y))

            font = pygame.font.Font(None, FONT_SIZE_SMALL)
            
            text = font.render(egg_name, True, FONT_COLOR_DEFAULT)
            blit_with_shadow(surface, text, (SCREEN_WIDTH // 2 - text.get_width() // 2, egg_y + PET_HEIGHT + 10))
        else:
            runtime_globals.game_console.log("[SceneEggSelection] Warning: No sprite to draw.")

    def handle_event(self, input_action) -> None:
        """
        Handles key inputs for navigating eggs and confirming selection.
        """
        if input_action == "LEFT":
            runtime_globals.game_sound.play("menu")
            self.move_selection(-1)
        elif input_action == "RIGHT":
            runtime_globals.game_sound.play("menu")
            self.move_selection(1)
        elif input_action == "A" or input_action == "START":
            runtime_globals.game_sound.play("menu")
            selected_egg = self.get_selected_egg()
            if selected_egg:
                runtime_globals.game_console.log(f"[SceneEggSelection] Selected egg: {selected_egg['name']}")
                module = get_module(selected_egg["module"])
                if module.ruleset == "dmc":
                    pet = GamePetDmC(selected_egg)
                else:
                    pet = GamePetPenC(selected_egg)
                egg_key = (selected_egg["module"], selected_egg["version"])
                if egg_key in game_globals.traited:
                    pet.traited = True
                    game_globals.traited.remove(egg_key)
                game_globals.pet_list.append(pet)
                bg_name = f"ver{selected_egg['version']}"
                unlock_item(selected_egg["module"], "backgrounds", bg_name)
                if selected_egg["module"] == "DMC":
                    unlock_item(selected_egg["module"], "backgrounds", "file_island")
                    unlock_item(selected_egg["module"], "backgrounds", "abandoned_office")
                    unlock_item(selected_egg["module"], "backgrounds", "blank")
                elif selected_egg["module"] == "PenC":
                    unlock_item(selected_egg["module"], "backgrounds", "folder_continent")
                    unlock_item(selected_egg["module"], "backgrounds", "living_quarters")
                # If no background is selected, use this one
                if not game_globals.game_background:
                    game_globals.game_background = bg_name
                    game_globals.background_module_name = selected_egg["module"]

                change_scene("game")
