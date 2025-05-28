import pygame

from core import game_globals, runtime_globals
from core.constants import *
from core.utils import pets_need_care

#=====================================================================
# WindowMenu - Main Menu Icon Bar
#=====================================================================

class WindowMenu:
    """
    Displays the main menu icons at the top and bottom of the screen,
    and highlights the currently selected item.
    """

    def __init__(self):
        self.icons = []
        self.spacing_x = 0
        self.top_y = 0
        self.bottom_y = SCREEN_HEIGHT - (MENU_ICON_SIZE * 2) - 10

        self.load_icons()
        self.calculate_spacing()

    def load_icons(self):
        """
        Loads and scales the menu icons from the sprite sheet.
        """
        try:
            menu_sheet = pygame.image.load(MAIN_MENU_PATH).convert_alpha()
            for i in range(8):  # 8 menu items
                normal = menu_sheet.subsurface((0, i * MENU_ICON_SIZE, MENU_ICON_SIZE, MENU_ICON_SIZE))
                selected = menu_sheet.subsurface((MENU_ICON_SIZE, i * MENU_ICON_SIZE, MENU_ICON_SIZE, MENU_ICON_SIZE))
                normal = pygame.transform.scale(normal, (MENU_ICON_SIZE * 2, MENU_ICON_SIZE * 2))
                selected = pygame.transform.scale(selected, (MENU_ICON_SIZE * 2, MENU_ICON_SIZE * 2))
                self.icons.append((normal, selected))
        except pygame.error:
            runtime_globals.game_console.log("⚠️ Failed to load Menu.png")

    def calculate_spacing(self):
        """
        Calculates the horizontal spacing for menu icons.
        Adjusts top bar position depending on clock visibility.
        """
        self.spacing_x = (SCREEN_WIDTH - (4 * MENU_ICON_SIZE * 2)) // 5
        self.top_y = 20 if game_globals.showClock else 4

    def draw(self, surface):
        """
        Draws the menu icons, highlighting the currently selected item.
        
        Args:
            surface (pygame.Surface): Surface to draw on.
        """
        if not self.icons:
            return

        # Draw top row (indices 0–3)
        for i in range(4):
            x = self.spacing_x + i * (MENU_ICON_SIZE * 2 + self.spacing_x)
            selected = (i == runtime_globals.main_menu_index)
            icon = self.icons[i][1] if selected else self.icons[i][0]
            surface.blit(icon, (x, self.top_y))

        # Draw bottom row (indices 4–7)
        for i in range(4, 8):
            col = i - 4
            x = self.spacing_x + col * (MENU_ICON_SIZE * 2 + self.spacing_x)
            if i == 7 and self.check_alert():
                icon = self.icons[i][1]
            else:
                selected = (i == runtime_globals.main_menu_index)
                icon = self.icons[i][1] if selected else self.icons[i][0]
            surface.blit(icon, (x, self.bottom_y))

    def move_selection(self, direction):
        """
        Moves the menu selection cursor left or right.
        
        Args:
            direction (int): -1 for left, 1 for right
        """
        runtime_globals.main_menu_index = (runtime_globals.main_menu_index + direction) % 8

    def check_alert(self):
        alert = pets_need_care()
        if alert != runtime_globals.pet_alert:
            runtime_globals.pet_alert = alert
            if alert:
                runtime_globals.game_sound.play("alarm")
        return runtime_globals.pet_alert
