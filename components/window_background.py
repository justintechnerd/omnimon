import pygame
import time
import os
from core import runtime_globals, game_globals
from core.constants import *
from core.utils import get_module


class WindowBackground:
    def __init__(self, boot=False):
        self.time_of_day = "day"
        self.image = None
        self.last_check_time = 0
        self.last_background = None
        self.last_module = None
        self.update()
        self.load_sprite(boot)

    def draw(self, surface):
        if self.image:
            surface.blit(self.image, (0, 0))

    def update(self):
        now = time.time()
        # Reload if background or module changed
        if (game_globals.game_background != self.last_background or
            game_globals.background_module_name != self.last_module):
            self.load_sprite(False)

        if now - self.last_check_time >= 60:
            self.last_check_time = now
            current_hour = time.localtime().tm_hour
            new_time_of_day = (
                "day" if 6 <= current_hour < 16
                else "dusk" if 16 <= current_hour < 19
                else "night"
            )

            if new_time_of_day != self.time_of_day:
                self.time_of_day = new_time_of_day
                self.load_sprite(False)

    def load_sprite(self, boot):
        if boot:
            path = "resources/Splash.png"
        else:
            name = game_globals.game_background
            module_name = game_globals.background_module_name
            if not name or not module_name:
                runtime_globals.game_console.log("[!] Missing background or module name.")
                self.image = None
                return

            # Check if this background supports day/night
            module = get_module(module_name)
            day_night = True
            for bg in getattr(module, "backgrounds", []):
                if bg["name"] == name:
                    day_night = bg.get("day_night", True)
                    break

            suffix = f"_{self.time_of_day}" if day_night else ""
            path = os.path.join(module.folder_path, "backgrounds", f"bg_{name}{suffix}.png")

        try:
            self.image = pygame.image.load(path).convert()
            self.image = pygame.transform.scale(self.image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.last_background = game_globals.game_background
            self.last_module = game_globals.background_module_name
        except pygame.error:
            runtime_globals.game_console.log(f"[!] Error loading background: {path}")
            self.image = None
