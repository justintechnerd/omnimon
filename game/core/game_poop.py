#=====================================================================
# GamePoop - Represents a poop object on screen
#=====================================================================

from core import runtime_globals
from core.utils.pygame_utils import blit_with_cache
from game.core import constants
import random

class GamePoop:
    """
    Represents a poop entity that can be drawn and animated on screen.
    """

    def __init__(self, x: int, y: int, jumbo = False) -> None:
        """
        Initializes the poop object at the given (x, y) position.

        Args:
            x (int): X-coordinate on screen.
            y (int): Y-coordinate on screen.
        """
        self.x = x
        self.y = y
        self.jumbo = jumbo
        # Use a random offset in frames for smooth desynchronization
        self._frame_offset = random.randint(0, constants.FRAME_RATE - 1)
        runtime_globals.game_console.log(f"[GamePoop] Initialized at ({self.x}, {self.y}), Jumbo: {self.jumbo}")

    def update(self) -> None:
        """
        Updates the internal animation counter.
        """
        pass

    def draw(self, surface, frame_counter) -> None:
        """
        Draws the poop on the given surface.

        Args:
            surface: The Pygame surface where the poop is drawn.
        """
        if not hasattr(self, "_frame_offset"):
            self._frame_offset = random.randint(0, constants.FRAME_RATE - 1)
        # Switch frame every second, but offset start for each poop
        self.frame_index = ((frame_counter + self._frame_offset) // constants.FRAME_RATE) % 2
        sprite_key = f"JumboPoop{self.frame_index + 1}" if self.jumbo else f"Poop{self.frame_index + 1}"
        sprite = runtime_globals.misc_sprites.get(sprite_key)
        blit_with_cache(surface, sprite, (self.x, self.y))
