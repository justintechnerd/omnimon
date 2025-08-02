"""
Scene Boot
Initial boot scene responsible for setting up the game start.
Transitions automatically to either Egg Selection or Main Game based on pet list.
"""

import platform
import pygame
import os

from components.window_background import WindowBackground
from core import game_globals, runtime_globals
import game.core.constants as constants
from core.utils.module_utils import get_module
from core.utils.pet_utils import distribute_pets_evenly
from core.utils.pygame_utils import blit_with_cache, sprite_load_percent
from core.utils.scene_utils import change_scene


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
        self.logo = sprite_load_percent("resources/OmnimonLogo.png", percent=100, keep_proportion=True, base_on="height")

        # --- Platform detection ---
        is_batocera = os.path.exists("/usr/share/batocera") or os.path.exists("/etc/batocera-release")
        is_rpi = False
        try:
            with open("/proc/device-tree/model") as f:
                is_rpi = "raspberry pi" in f.read().lower()
        except Exception:
            pass

        if platform.system() == "Windows":
            image_path = "resources/ControllersPC.png"
        elif is_batocera:
            image_path = "resources/ControllersBato.png"  # Or a Batocera-specific image if you have one
        elif is_rpi:
            image_path = "resources/ControllersPi.png"
        else:
            image_path = "resources/ControllersJoy.png"  # Fallback for other Linux

        self.controller_sprite = sprite_load_percent(image_path, percent=100, keep_proportion=True, base_on="height")
        self.boot_timer = int(150 * (constants.FRAME_RATE / 30)) 
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
        self.background.draw(surface)
        if self.boot_timer <= 80 * (constants.FRAME_RATE / 30):
            # Center the controller sprite on screen
            sprite_rect = self.controller_sprite.get_rect(center=(constants.SCREEN_WIDTH // 2, constants.SCREEN_HEIGHT // 2))
            blit_with_cache(surface, self.controller_sprite, sprite_rect)
        else:
            blit_with_cache(surface, self.logo, ((constants.SCREEN_WIDTH - self.logo.get_width()) // 2, 0))

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
                # Refresh evolution data from module
                module = get_module(pet.module)
                pet_data = module.get_monster(pet.name, pet.version)
                if pet_data:
                    pet.evolve = pet_data.get("evolve", [])
                pet.begin_position()
                if pet.state not in ["dead", "hatch", "nap"]:
                    pet.set_state("idle")
                pet.patch()
            distribute_pets_evenly()
        else:
            change_scene("egg")
            runtime_globals.game_console.log("[SceneBoot] Transitioning to EggSelection (no pets)")
