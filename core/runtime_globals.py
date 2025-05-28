import os
import pygame

from core.game_console import GameConsole
from core.game_message import GameMessage
from core.game_sound import GameSound
from core.input.i2c_utils import I2CUtils
from core.input.input_manager import InputManager
from core.input.shake_detector import ShakeDetector
from core.utils import sprite_load

#=====================================================================
# Runtime (Non-Persistent) Global Variables
#=====================================================================

# Scene control
game_state = "boot"
game_state_update = False

# Main menu navigation
main_menu_index = -1

# Feeding menu selections
food_index = 0
strategy_index = 0
training_index = 0
battle_index = {}

# Runtime-only assets and selections
feeding_frames = []
selected_pets = []
misc_sprites = {}
battle_enemies = {}
pet_sprites = {}
evolution_data = []
evolution_pet = None

# Global managers
game_sound = GameSound()
game_console = GameConsole()
game_message = GameMessage()
game_input = InputManager()
game_modules = {}
game_module_flag = {}

pet_alert = False
show_hearts = False

#rulesets
dmc_enabled = False
penc_enabled = False

i2c = I2CUtils()
shake_detector = ShakeDetector(i2c)

def load_misc_sprites() -> None:
    """Loads miscellaneous sprites used across various parts of the game."""
    global misc_sprites

    sprite_files = [
        "Cheer.png", "Mad1.png", "Mad2.png",
        "Sick1.png", "Sick2.png", "Sleep1.png",
        "Sleep2.png", "Poop1.png", "Poop2.png", "Wash.png"
    ]

    misc_sprites.clear()

    for filename in sprite_files:
        path = os.path.join("resources", filename)
        try:
            misc_sprites[filename.split('.')[0]] = sprite_load(path)
        except pygame.error as e:
            game_console.log(f"[!] Error loading {filename}: {e}")
