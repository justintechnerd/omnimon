"""
Scene Status Menu
Displays detailed information about selected pets (age, weight, strength, effort, battle win rates, etc.).
"""

import pygame

from components.window_background import WindowBackground
from components.window_petselector import WindowPetSelector
from components.window_status import WindowStatus
from core import runtime_globals
from core.constants import *
from core.utils.pygame_utils import sprite_load_percent
from core.utils.scene_utils import change_scene

PAGE_MARGIN = int(16 * UI_SCALE)

#=====================================================================
# SceneStatusMenu
#=====================================================================
class SceneStatusMenu:
    """
    Menu scene for displaying selected pets' detailed status information.
    """

    def __init__(self) -> None:
        self.background = WindowBackground(False)
        # Use new method for overlay, scale to screen width, keep proportions
        self.overlay_image = sprite_load_percent(
            MENU_BACKGROUND_PATH,
            percent=100,
            keep_proportion=True,
            base_on="width"
        )

        self.selector = WindowPetSelector()
        self.selecting_pet = True
        self.page = 1

        self.window_status = None  # Will hold WindowStatus once pet is selected
        runtime_globals.game_console.log("[SceneStatusMenu] Initialized.")


    def update(self) -> None:
        """
        Updates the status menu (currently unused).
        """
        pass

    def draw(self, surface):
        self.background.draw(surface)
        # Center overlay image on screen
        overlay_rect = self.overlay_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        surface.blit(self.overlay_image, overlay_rect)

        if self.selecting_pet:
            self.selector.draw(surface)
        else:
            self.window_status.draw_page(surface, self.page)

    def handle_event(self, input_action):
        if self.selecting_pet:
            if self.selector.handle_event(input_action):
                self.open_status()
        else:
            if input_action:
                if input_action == "RIGHT":
                    runtime_globals.game_sound.play("menu")
                    self.page = (self.page % 4) + 1
                elif input_action == "LEFT":
                    runtime_globals.game_sound.play("menu")
                    self.page = (self.page - 2) % 4 + 1
                elif input_action in ["UP","DOWN"]:
                    self.selector.handle_event(input_action)
                    self.open_status(self.page)
                elif input_action == "A" or input_action == "B":
                    runtime_globals.game_sound.play("menu")
                    self.selecting_pet = True
                elif input_action == "START":
                    change_scene("game")

    def open_status(self, page=1):
        pet = self.selector.get_selected_pet()
        self.window_status = WindowStatus(pet)
        self.pet = pet
        self.page = page
        self.selecting_pet = False