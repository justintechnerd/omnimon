"""
Scene Boot
Initial boot scene responsible for setting up the game start.
Transitions automatically to either Egg Selection or Main Game based on pet list.
"""

import platform
import pygame

from components.window_background import WindowBackground
from core import game_globals, runtime_globals
from core.constants import *
from core.utils import change_scene, distribute_pets_evenly, sprite_load


#=====================================================================
# SceneBoot
#=====================================================================
class SceneBoot:
    """
    Boot scene for the Virtual Pet game.
    Shows background while initializing the next scene.
    """

    def __init__(self) -> None:
        """
        Initializes the boot scene with a temporary timer.
        """
        self.background = WindowBackground(True)
        if platform.system() == "Windows":
            image_path = "resources/ControllersPC.png"
        else:
            image_path = "resources/ControllersPi.png"
        self.controller_sprite = sprite_load(image_path)
        self.boot_timer = BOOT_TIMER_FRAMES
        runtime_globals.game_console.log("[SceneBoot] Initialized")

    def update(self) -> None:
        """
        Updates the boot scene, transitioning to the appropriate next scene after the timer expires.
        """
        self.boot_timer -= 1

        if self.boot_timer <= 0:
            self.transition_to_next_scene()

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draws the boot background.
        """
        if self.boot_timer <= 80:
            surface.blit(self.controller_sprite, (0,0))
        else:
            self.background.draw(surface)

    def handle_event(self, input_action) -> None:
        """
        Handles key press events, allowing early skip with ENTER.
        """

        if input_action == "A" or input_action == "START":
            runtime_globals.game_console.log("[SceneBoot] Skipped boot timer with ENTER")
            self.boot_timer = 0

    def transition_to_next_scene(self) -> None:
        """
        Decides whether to transition to Main Game or Egg Selection based on saved pets.
        """
        if game_globals.pet_list:
            change_scene("game")
            runtime_globals.game_console.log("[SceneBoot] Transitioning to MainGame (pets found)")
            for pet in game_globals.pet_list:
                pet.begin_position()
                pet.food_type = -1
                if pet.state not in ["dead", "hatch", "nap"]:
                    pet.set_state("idle")
            distribute_pets_evenly()
        else:
            change_scene("egg")
            runtime_globals.game_console.log("[SceneBoot] Transitioning to EggSelection (no pets)")
