# game_enemy.py
import os
import pygame
from dataclasses import dataclass

from core.animation import PetFrame
from core.constants import *


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
        Loads specific animation frames for the enemy: IDLE1, IDLE2, ANGRY, ATK1, ATK2.

        Args:
            module_path (str): Path to the module directory.
        """
        self.frames = []
        folder = os.path.join(module_path, "monsters", f"{self.name}_dmc")

        max_index = max(frame.value for frame in PetFrame)
        self.frames = [None] * (max_index + 1)

        for frame in PetFrame:
            i = frame.value
            frame_file = os.path.join(folder, f"{i}.png")
            if os.path.exists(frame_file):
                self.frames[i] = sprite_load(frame_file, size=(PET_WIDTH, PET_HEIGHT))
                if boss:
                    self.frames[i] = pygame.transform.scale(self.frames[i], (PET_WIDTH * BOSS_MULTIPLIER, PET_HEIGHT * BOSS_MULTIPLIER))

    def get_sprite(self, index: int):
        if hasattr(self, "frames") and 0 <= index < len(self.frames):
            return self.frames[index]
        return None
    
def sprite_load(path, size=None, scale=1):
    """Loads a sprite and optionally scales it to a fixed size or by a scale factor."""
    img = pygame.image.load(path).convert_alpha()
    
    if size:
        return pygame.transform.scale(img, size)  # 🔹 Scale to a fixed size
    elif scale != 1:
        base_size = img.get_size()
        new_size = (int(base_size[0] * scale), int(base_size[1] * scale))
        return pygame.transform.scale(img, new_size)  # 🔹 Scale by a multiplier
    
    return img  # 🔹 Return original image if no scaling is applied