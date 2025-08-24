# game_enemy.py
import os
from dataclasses import dataclass

from core.animation import PetFrame
import game.core.constants as constants
from game.core.utils.sprite_utils import convert_sprites_to_list, load_enemy_sprites


@dataclass
class GameEnemy:
    name: str
    power: int
    attribute: str
    area: int
    round: int
    version: int
    atk_main: int
    atk_alt: int
    handicap: int
    id: int
    stage: int
    hp: int
    unlock: str
    prize: str

    def load_sprite(self, module_path: str, boss: bool = False):
        """
        Loads specific animation frames for the enemy using the new sprite loading utility.

        Args:
            module_path (str): Path to the module directory.
            boss (bool): Whether this enemy is a boss (applies scaling).
        """
        # Determine module name from path to get module object for name_format
        module_name = module_path
        
        # Try to get module object to access name_format
        try:
            from core.utils.module_utils import get_module
            module_obj = get_module(module_name)
            name_format = getattr(module_obj, 'name_format', '$_dmc') if module_obj else '$_dmc'
        except:
            name_format = '$_dmc'  # Default fallback
        
        # Calculate size based on boss status
        if boss:
            size = (constants.PET_WIDTH * constants.BOSS_MULTIPLIER, constants.PET_HEIGHT * constants.BOSS_MULTIPLIER)
        else:
            size = (constants.PET_WIDTH, constants.PET_HEIGHT)
        
        # Load sprites using the new utility function
        sprites_dict = load_enemy_sprites(self.name, module_path, name_format, size=size)
        
        # Convert to the expected format
        sprite_list = convert_sprites_to_list(sprites_dict)
        
        # Initialize frames array
        max_index = max(frame.value for frame in PetFrame)
        self.frames = [None] * (max_index + 1)
        
        # Populate frames array with loaded sprites
        for i, sprite in enumerate(sprite_list):
            if i < len(self.frames):
                self.frames[i] = sprite

    def get_sprite(self, index: int):
        if hasattr(self, "frames") and 0 <= index < len(self.frames):
            return self.frames[index]
        return None