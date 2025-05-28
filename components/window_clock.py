import platform
import pygame
import time
import os

from core import runtime_globals
from core.constants import *
from core.input.i2c_utils import I2CUtils
from core.utils import get_font


#=====================================================================
# WindowClock - Top Bar Clock and Battery Display
#=====================================================================

class WindowClock:
    """
    Displays the current time and a battery icon in the top bar.
    """

    def __init__(self):
        # Basic dimensions and positions
        self.font = get_font(FONT_SIZE_SMALL)
        self.x = 10
        self.y = 0
        self.height = 22
        self.padding = 0

        self.battery_icons = self.load_battery_icons()
        self.current_icon_key = "battery_full"
        self.battery_icon = self.battery_icons[self.current_icon_key]
        self.last_update = 0

    def load_battery_icons(self):
        """
        Loads all battery icon images into a dictionary.
        """
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

    def select_icon_key(self, voltage, capacity):
        if platform.system() == "Windows":
            return "battery_full"
        elif voltage is None or capacity is None:
            return "battery_empty"
        elif capacity < 5:
            return "battery_empty"
        elif capacity < 20:
            return "battery_low"
        elif capacity < 60:
            return "battery_half"
        else:
            return "battery_full"

    def update_battery_icon(self):
        now = time.time()
        if now - self.last_update < 2:  # Throttle updates
            return

        voltage, capacity = runtime_globals.i2c.read_battery()
        icon_key = self.select_icon_key(voltage, capacity)

        if icon_key != self.current_icon_key and self.battery_icons.get(icon_key):
            self.battery_icon = self.battery_icons[icon_key]
            self.current_icon_key = icon_key

        self.last_update = now

    def draw(self, surface):
        # Draw top black bar
        bar_rect = pygame.Rect(0, self.y, SCREEN_WIDTH, self.height)
        pygame.draw.rect(surface, (0, 0, 0), bar_rect)

        # Draw current time
        current_time = time.strftime("%H:%M:%S")
        time_surface = self.font.render(current_time, True, FONT_COLOR_DEFAULT)
        surface.blit(time_surface, (self.x, self.padding))

        # Update and draw battery icon
        self.update_battery_icon()
        if self.battery_icon:
            battery_x = SCREEN_WIDTH - self.battery_icon.get_width() - self.padding
            battery_y = self.y + (self.height - self.battery_icon.get_height()) // 2
            surface.blit(self.battery_icon, (battery_x, battery_y))