import time
import pygame

from core import game_globals, runtime_globals
import game.core.constants as constants
from core.utils.pet_utils import pets_need_care
from core.utils.pygame_utils import blit_with_cache

#=====================================================================
# WindowMenu - Main Menu Icon Bar (Optimized)
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
        self.bottom_y = constants.SCREEN_HEIGHT - (constants.MENU_ICON_SIZE * 2) - 10

        self.top_positions = []
        self.bottom_positions = []

        self.prev_menu_index = -2
        self.prev_alert_state = None

        self.top_cache = None
        self.bottom_cache = None

        self.last_alert_check = time.time()

        self.load_icons()
        self.calculate_spacing()
        self.update_cache(True)


    def load_icons(self):
        """
        Loads and scales the menu icons from the sprite sheet.
        """
        try:
            menu_sheet = pygame.transform.scale(
                pygame.image.load(constants.MAIN_MENU_PATH).convert_alpha(),
                (constants.MENU_ICON_SIZE * 2, constants.MENU_ICON_SIZE * 8)
            )
            for i in range(8):  # 8 menu items
                normal = menu_sheet.subsurface((0, i * constants.MENU_ICON_SIZE, constants.MENU_ICON_SIZE, constants.MENU_ICON_SIZE))
                selected = menu_sheet.subsurface((constants.MENU_ICON_SIZE, i * constants.MENU_ICON_SIZE, constants.MENU_ICON_SIZE, constants.MENU_ICON_SIZE))
                normal = pygame.transform.scale(normal, (constants.MENU_ICON_SIZE * 2, constants.MENU_ICON_SIZE * 2))
                selected = pygame.transform.scale(selected, (constants.MENU_ICON_SIZE * 2, constants.MENU_ICON_SIZE * 2))
                self.icons.append((normal, selected))
        except pygame.error:
            runtime_globals.game_console.log("⚠️ Failed to load Menu.png")


    def calculate_spacing(self):
        """Precomputes icon positions to avoid unnecessary calculations."""
        self.spacing_x = (constants.SCREEN_WIDTH - (4 * constants.MENU_ICON_SIZE * 2)) // 5
        self.top_y = 20 * constants.UI_SCALE if game_globals.showClock else 4

        self.top_positions = [
            (self.spacing_x + i * (constants.MENU_ICON_SIZE * 2 + self.spacing_x), 0) for i in range(4)
        ]
        self.bottom_positions = [
            (self.spacing_x + (i - 4) * (constants.MENU_ICON_SIZE * 2 + self.spacing_x), 0) for i in range(4, 8)
        ]


    def update_cache(self, force=False):
        """
        Rebuilds top and bottom caches only if state changes.
        """
        menu_index = runtime_globals.main_menu_index
        alert = self.check_alert()

        # Update top cache if selection changed
        if self.prev_menu_index != menu_index or force:
            self.top_cache = pygame.Surface((constants.SCREEN_WIDTH, constants.MENU_ICON_SIZE * 2), pygame.SRCALPHA)
            for i, (x, y) in enumerate(self.top_positions):
                selected = (i == menu_index)
                icon = self.icons[i][1] if selected else self.icons[i][0]
                self.top_cache.blit(icon, (x, y))
        
        # Update bottom cache if selection or alert changed
        if self.prev_menu_index != menu_index or self.prev_alert_state != alert or force:
            self.bottom_cache = pygame.Surface((constants.SCREEN_WIDTH, constants.MENU_ICON_SIZE * 2), pygame.SRCALPHA)
            for i, (x, y) in enumerate(self.bottom_positions, start=4):
                selected = (i == menu_index)
                if i == 7 and alert:
                    icon = self.icons[i][1]
                else:
                    icon = self.icons[i][1] if selected else self.icons[i][0]
                self.bottom_cache.blit(icon, (x, y))

        self.prev_menu_index = menu_index
        self.prev_alert_state = alert


    def draw(self, surface):
        """
        Efficiently draws menu icons using pre-rendered surfaces.
        """
        if not self.icons:
            return

        self.update_cache()
        if self.top_cache:
            #surface.blit(self.top_cache, (0, self.top_y))
            blit_with_cache(surface, self.top_cache, (0, self.top_y))
        if self.bottom_cache:
            #surface.blit(self.bottom_cache, (0, self.bottom_y))
            blit_with_cache(surface, self.bottom_cache, (0, self.bottom_y))


    def move_selection(self, direction):
        """
        Moves the menu selection cursor left or right.

        Args:
            direction (int): -1 for left, 1 for right
        """
        runtime_globals.main_menu_index = (runtime_globals.main_menu_index + direction) % 8


    def check_alert(self):
        now = time.time()
        if now - self.last_alert_check < 2:  # Check alert at most once per second
            return runtime_globals.pet_alert

        alert = pets_need_care()
        self.last_alert_check = now

        if alert != runtime_globals.pet_alert:
            runtime_globals.pet_alert = alert
            if alert:
                runtime_globals.game_sound.play("alarm")

        return runtime_globals.pet_alert
