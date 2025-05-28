"""
Scene Feeding Menu
Allows the player to choose food type and feeding strategy for pets.
"""

import pygame

from components.window_background import WindowBackground
from components.window_horizontalmenu import WindowHorizontalMenu
from components.window_petview import WindowPetList
from core import game_globals, runtime_globals
from core.constants import *
from core.utils import blit_with_shadow, change_scene, distribute_pets_evenly, get_font, get_selected_pets, load_feeding_frames


#=====================================================================
# SceneFeedingMenu
#=====================================================================
class SceneFeedingMenu:
    """
    Scene for selecting food and feeding pets.
    """

    def __init__(self) -> None:
        """
        Initializes the feeding menu, loading food frames if necessary.
        """
        if not runtime_globals.feeding_frames:
            load_feeding_frames()

        self.background = WindowBackground()
        self.options = [("Protein", runtime_globals.feeding_frames[0]),
                        ("Vitamin", runtime_globals.feeding_frames[4])]

        self.selectionBackground = pygame.image.load(PET_SELECTION_BACKGROUND_PATH).convert_alpha()

        self.pet_list_window = WindowPetList(lambda: self.get_targets())

        self.menu_window = WindowHorizontalMenu(
            options=self.options,
            get_selected_index_callback=lambda: runtime_globals.food_index,
        )    

        runtime_globals.game_console.log("[SceneFeedingMenu] Feeding frames loaded.")

    def get_targets(self) -> list:
        """
        Returns a list of pets to feed based on the selected strategy.
        """
        if runtime_globals.strategy_index == 0:
            return get_selected_pets()
        else:
            if runtime_globals.food_index == 0:
                return [pet for pet in game_globals.pet_list if pet.hunger < 4 and pet.state != "dead"]  # Protein
            else:
                return [pet for pet in game_globals.pet_list if pet.strength < 4 and pet.state != "dead"]  # Vitamin

    def update(self) -> None:
        """
        Updates the feeding menu scene (currently no dynamic behavior).
        """
        pass

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draws the feeding menu and pet list.
        """
        self.background.draw(surface)
        # Desenha menu horizontal
        self.menu_window.draw(surface, x=16, y=16, spacing=16)

        # Desenha pets na parte inferior
        self.pet_list_window.draw(surface)

    def handle_event(self, input_action) -> None:
        """
        Handles keyboard and GPIO button inputs for food and strategy selection.
        """
        if input_action == "B":  # Escape (Cancel/Menu)
            runtime_globals.game_sound.play("cancel")
            change_scene("game")

        elif input_action == "LEFT":  # Move food selection left
            runtime_globals.game_sound.play("menu")
            runtime_globals.food_index = (runtime_globals.food_index - 1) % len(self.options)

        elif input_action == "RIGHT":  # Move food selection right
            runtime_globals.game_sound.play("menu")
            runtime_globals.food_index = (runtime_globals.food_index + 1) % len(self.options)

        elif input_action == "SELECT":  # Cycle strategy
            runtime_globals.game_sound.play("menu")
            runtime_globals.strategy_index = (runtime_globals.strategy_index + 1) % 2

        elif input_action == "A":  # Confirm feeding action (ENTER on PC, A button on Pi)
            targets = self.get_targets()

            if not targets:
                runtime_globals.game_sound.play("cancel")
                return

            runtime_globals.game_sound.play("menu")
            distribute_pets_evenly()

            for pet in targets:
                pet.check_disturbed_sleep()
                pet.food_type = runtime_globals.food_index
                pet.set_eating()

            runtime_globals.game_console.log(f"[SceneFeedingMenu] Fed {len(targets)} pets with {runtime_globals.food_index}")
            change_scene("game")
