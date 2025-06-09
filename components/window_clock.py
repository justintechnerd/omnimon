import platform
import pygame
import time
import os

from core import runtime_globals
from core.constants import *
from core.utils import get_font

class WindowClock:
    """
    Displays the current time and a battery icon in the top bar.
    """

    def __init__(self):
        self.font = get_font(FONT_SIZE_SMALL)
        self.x = 10
        self.y = 0
        self.height = 22
        self.padding = 0

        self.battery_icons = self.load_battery_icons()
        self.current_icon_key = "battery_full"
        self.battery_icon = self.battery_icons.get(self.current_icon_key)
        self.last_battery_update = 0

        self.last_time_update = 0
        self.last_time_string = ""
        self.time_surface = None

        self.battery = runtime_globals.i2c  # I2C Battery instance

    def load_battery_icons(self):
        names = [
            "battery_charging",
            "battery_empty",
            "battery_low",
            "battery_half",
            "battery_full"
        ]
        icons = {}
        for name in names:
            try:
                path = os.path.join("resources", f"{name}.png")
                icons[name] = pygame.image.load(path).convert_alpha()
            except pygame.error:
                runtime_globals.game_console.log(f"⚠️ Failed to load {name}.png")
                icons[name] = None
        return icons

    def select_icon_key(self, percent, charging):
        if charging:
            return "battery_charging"
        elif percent <= 5.0:
            return "battery_empty"
        elif percent <= 20.0:
            return "battery_low"
        elif percent <= 50.0:
            return "battery_half"
        else:
            return "battery_full"

    def update_battery_icon(self):
        now = time.time()
        if now - self.last_battery_update < 5:
            return

        percent = self.battery.get_battery_percentage()
        charging = self.battery.is_charging()
        icon_key = self.select_icon_key(percent, charging)

        icon = self.battery_icons.get(icon_key)
        if icon is not None:
            self.battery_icon = icon
            self.current_icon_key = icon_key

        self.last_battery_update = now

    def draw(self, surface):
        now = time.time()

        # Only update time string and surface once per second
        if now - self.last_time_update >= 1:
            self.last_time_string = time.strftime("%H:%M:%S")
            self.time_surface = self.font.render(self.last_time_string, True, FONT_COLOR_DEFAULT)
            self.last_time_update = now

        # Draw top black bar
        pygame.draw.rect(surface, (0, 0, 0), (0, self.y, SCREEN_WIDTH, self.height))

        # Draw cached time surface
        if self.time_surface:
            surface.blit(self.time_surface, (self.x, self.padding))

        # Update and draw battery icon
        self.update_battery_icon()
        if self.battery_icon:
            battery_x = SCREEN_WIDTH - self.battery_icon.get_width() - self.padding
            battery_y = self.y + (self.height - self.battery_icon.get_height()) // 2
            surface.blit(self.battery_icon, (battery_x, battery_y))
