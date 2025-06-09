
#=====================================================================
# GamePoop - Represents a poop object on screen
#=====================================================================

from core import runtime_globals

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
        self.frame_counter = 0
        self.jumbo = jumbo

    def update(self) -> None:
        """
        Updates the internal animation counter.
        """
        self.frame_counter += 1

    def draw(self, surface) -> None:
        """
        Draws the poop on the given surface.

        Args:
            surface: The Pygame surface where the poop is drawn.
        """
        # Alternate between "Poop1" and "Poop2" every 30 frames
        self.frame_index = (self.frame_counter // 30) % 2
        sprite_key = f"JumboPoop{self.frame_index + 1}" if self.jumbo else f"Poop{self.frame_index + 1}"
        sprite = runtime_globals.misc_sprites.get(sprite_key)
        surface.blit(sprite, (self.x, self.y))
