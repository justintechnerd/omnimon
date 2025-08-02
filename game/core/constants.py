import json
import os
import pygame

#=====================================================================
# Pygame Version Compatibility
#=====================================================================
PYGAME_VERSION = tuple(map(int, pygame.version.ver.split('.')))
IS_PYGAME2 = PYGAME_VERSION >= (2, 0, 0)
# Use SRCALPHA for both versions - it's compatible
COMPATIBLE_SRCALPHA = pygame.SRCALPHA

#=====================================================================
# Load config values
#=====================================================================
CONFIG_PATH = "config/config.json"
DEFAULT_CONFIG = {
    "SCREEN_WIDTH": 240,
    "SCREEN_HEIGHT": 240,
    "FRAME_RATE": 30,
    "MAX_PETS": 4,
    "FULLSCREEN": False,
    "DEBUG": False,
    "LOGGING": False
}

try:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        user_config = json.load(f)
except Exception:
    user_config = {}

SCREEN_WIDTH = user_config.get("SCREEN_WIDTH", DEFAULT_CONFIG["SCREEN_WIDTH"])
SCREEN_HEIGHT = user_config.get("SCREEN_HEIGHT", DEFAULT_CONFIG["SCREEN_HEIGHT"])
FRAME_RATE = user_config.get("FRAME_RATE", DEFAULT_CONFIG["FRAME_RATE"])
MAX_PETS = user_config.get("MAX_PETS", DEFAULT_CONFIG["MAX_PETS"])
FULLSCREEN = user_config.get("FULLSCREEN", DEFAULT_CONFIG["FULLSCREEN"])
DEBUG = user_config.get("DEBUG", DEFAULT_CONFIG["DEBUG"])
LOGGING = user_config.get("LOGGING", DEFAULT_CONFIG["LOGGING"])

FRAME_SIZE = 48  # Original pet sprite frame size

#=====================================================================
# Screen and Window Constants
#=====================================================================
# SCREEN_WIDTH, SCREEN_HEIGHT = 240, 240
# FRAME_SIZE = 48  # Original pet sprite frame size
# FRAME_RATE = 30  # Frames per second

#=====================================================================
# Pet Constants
#=====================================================================
PET_WIDTH = PET_HEIGHT = SCREEN_HEIGHT // MAX_PETS
# MAX_PETS = 4
STAGES = [
    "0-Egg", "I-Fresh", "II-In-Training", "III-Rookie",
    "IV-Champion", "V-Ultimate", "VI-Mega", "VII-Super Ultimate"
]
ATTR_COLORS = {
            "Da": (66, 165, 245),
            "Va": (102, 187, 106),
            "Vi": (237, 83, 80),
            "": (171, 71, 188),
            "???": (0, 0, 0)
        }
#=====================================================================
# Game Mechanics
#=====================================================================
MOVE_SPEED = 0.5  # Movement speed in subpixels/frame
IDLE_PROBABILITY = 0.2  # 20% chance of idle vs. moving
CLEANING_SPEED = 6  # Speed of cleaning animation
SLEEP_RECOVERY_HOURS = 8  # Hours needed to fully recover
SLEEP_MANUAL_DURATION_HOURS = 1  # Duration when manually sleeping
SLEEP_DISTURBANCE_THRESHOLD_SECONDS = 7200  # 2 hours threshold for disturbance detection
BOOT_TIMER_FRAMES = int(150 * (FRAME_RATE / 30)) 

MAX_LEVEL = {0: 0, 1: 1, 2: 3, 3: 4, 4: 6, 5: 8, 6: 10, 7: 10, 8: 10}
EXPERIENCE_LEVEL = {0: 0, 1: 0, 2: 50, 3: 150, 4: 500, 5: 800, 6: 1000, 7: 1500, 8: 2000, 9: 3000, 10:5000}
HP_LEVEL = {
    0: 0,    # Egg
    1: 0,    # Fresh
    2: 10,   # In-Training
    3: 10,   # Rookie
    4: 12,   # Champion
    5: 15,   # Ultimate
    6: 18,   # Mega
    7: 20,   # Super Ultimate
    8: 20    # (If used, for extra stage)
}
ATK_LEVEL = {
    0: 0,   # Egg
    1: 0,   # Fresh
    2: 2,   # In-Training (10 // 4 = 2)
    3: 2,   # Rookie      (10 // 4 = 2)
    4: 3,   # Champion    (12 // 4 = 3)
    5: 3,   # Ultimate    (15 // 4 = 3)
    6: 4,   # Mega        (18 // 4 = 4)
    7: 5,   # Super Ultimate (20 // 4 = 5)
    8: 5    # Extra stage (20 // 4 = 5)
}
#=====================================================================
# UI Settings
#=====================================================================
# UI Settings - scale proportionally to a 240x240 reference screen
UI_SCALE = SCREEN_HEIGHT / 240

MENU_ICON_SIZE = int(24 * UI_SCALE)         # Icon size (24x24 at 240x240)
OPTION_ICON_SIZE = int(48 * UI_SCALE)       # Option icon size (48x48 at 240x240)
OPTION_FRAME_WIDTH = int(96 * UI_SCALE)     # Option frame width (96 at 240x240)
OPTION_FRAME_HEIGHT = int(116 * UI_SCALE)   # Option frame height (116 at 240x240)
PET_ICON_SIZE = int(48 * UI_SCALE)

FONT_SIZE_SMALL = int(24 * UI_SCALE)
FONT_SIZE_MEDIUM = int(28 * UI_SCALE)
FONT_SIZE_MEDIUM_LARGE = int(30 * UI_SCALE)
FONT_SIZE_LARGE = int(40 * UI_SCALE)

FONT_COLOR_DEFAULT = (255, 255, 255)
FONT_COLOR_GRAY = (150, 150, 150)
FONT_COLOR_GREEN = (0, 231, 58)
FONT_COLOR_RED = (237, 83, 80)
FONT_COLOR_YELLOW = (255, 255, 0)
FONT_COLOR_BLUE = (0, 0, 255)
BACKGROUND_COLOR = (198, 203, 173)

#=====================================================================
# Paths: General Resources
#=====================================================================
MODULES_FOLDER = "modules"
ARROW_IMAGE_PATH = "resources/Arrow.png"
FOOD_SHEET_PATH = "resources/FoodVitamin.png"
ATK_FOLDER = "resources/atk"

#=====================================================================
# Paths: UI Sprites
#=====================================================================
SELECTION_OFF_PATH = "resources/SelectionOff.png"
SELECTION_ON_PATH = "resources/SelectionOn.png"
MENU_BACKGROUND_PATH = "resources/MenuBackground.png"
PET_SELECTION_BACKGROUND_PATH = "resources/PetSelectionBack.png"
PET_SELECTION_SMALL_ON_PATH = "resources/PetSelectionSmallOn.png"
PET_SELECTION_SMALL_OFF_PATH = "resources/PetSelectionSmallOff.png"

#=====================================================================
# Paths: Battle & Training Sprites
#=====================================================================
BATTLE_BACKGROUND_PATH = "resources/BattleBackground.png"
TRAINING_BACKGROUND_PATH = "resources/TrainingBackground.png"
HEADTRAINING_PATH = "resources/HeadTraining.png"
VS_PATH = "resources/Vs.png"
STRIKES_BACK_PATH = "resources/StrikesBar.png"
STRIKE_PATH = "resources/Strike.png"
BATTLE_ICON_PATH = "resources/BattleIcon.png"
NEXT_BATTLE_ICON_PATH = "resources/NextBattle.png"
RESTART_BATTLE_ICON_PATH = "resources/RestartBattle.png"
HEAD_TRAINING_ICON_PATH = "resources/HeadTrainingIcon.png"
VERSUS_BATTLE_ICON_PATH = "resources/VersusBattle.png"
JOGRESS_ICON_PATH = "resources/Jogress.png"
ARMOR_EVOLUTION_ICON_PATH = "resources/ArmorEvolution.png"
DUMMY_TRAINING_ICON_PATH = "resources/BagIcon.png"
SHAKE_MATCH_ICON_PATH = "resources/CountTrainingIcon.png"
EXCITE_MATCH_ICON_PATH = "resources/ExciteTrainingIcon.png"
PUNCH_MATCH_ICON_PATH = "resources/PunchTrainingIcon.png"
XAIARROW_ICON_PATH = "resources/XaiArrow.png"
BOSS_MULTIPLIER = 1.5 

#=====================================================================
# Paths: Pet Sprites
#=====================================================================
DEAD_FRAME_PATH = "resources/Dead.png"
AGE_ICON_PATH = "resources/Age.png"
WEIGHT_ICON_PATH = "resources/Scale.png"
MODULE_ICON_PATH = "resources/Module.png"
VERSION_ICON_PATH = "resources/Version.png"
MISTAKES_ICON_PATH = "resources/Mistakes.png"
TRAITED_ICON_PATH = "resources/Traited.png"
SPECIAL_ICON_PATH = "resources/Special.png"
SHINY_ICON_PATH = "resources/Shiny.png"
SHOOK_ICON_PATH = "resources/Shook.png"
OVERFEED_ICON_PATH = "resources/Overfeed.png"
SICK_ICON_PATH = "resources/Sick1.png"
SLEEP_DISTURBANCES_ICON_PATH = "resources/SleepDisturbances.png"
XAI_ICON_PATH = "resources/Xai.png"
TROPHIES_ICON_PATH = "resources/trophies.png"
VITAL_VALUES_ICON_PATH = "resources/vitalvalues.png"

#=====================================================================
# Paths: UI Icons
#=====================================================================
HEART_EMPTY_ICON_PATH = "resources/Heart Empty.png"
HEART_HALF_ICON_PATH = "resources/Heart Half.png"
HEART_FULL_ICON_PATH = "resources/Heart Full.png"
ENERGY_BAR_ICON_PATH = "resources/Energy Bar Count - Green.png"
ENERGY_BAR_BACK_ICON_PATH = "resources/Energy Bar.png"
LEVEL_ICON_PATH = "resources/Level.png"
EXP_ICON_PATH = "resources/Exp.png"

#=====================================================================
# Paths: Scene Backgrounds
#=====================================================================
SPLASH_PATH = "resources/Splash.png"
MAIN_MENU_PATH = "resources/Menu.png"
DIGIDEX_BACKGROUND_PATH = "resources/Digidex.png"

#=====================================================================
# Paths: Battle Scene Sprites
#=====================================================================
BATTLE_SPRITE_PATH = "resources/Battle.png"
BATTLE_LEVEL_SPRITE_PATH = "resources/BattleLevel.png"
BAR_BACK_PATH = "resources/StrengthBarBack.png"
BAR_PIECE_PATH = "resources/StrengthBar.png"
TRAINING_MAX_PATH = "resources/TrainingMax.png"
ALERT_SPRITE_PATH = "resources/Alert.png"
GO_SPRITE_PATH = "resources/Go.png"
BAD_SPRITE_PATH = "resources/Bad.png"
GOOD_SPRITE_PATH = "resources/Good.png"
GREAT_SPRITE_PATH = "resources/Great.png"
EXCELLENT_SPRITE_PATH = "resources/Excellent.png"
READY_SPRITE_PATH = "resources/Ready.png"
BATTLE1_PATH = "resources/Battle1.png"
BATTLE2_PATH = "resources/Battle2.png"
BAG1_PATH = "resources/Bag1.png"
BAG2_PATH = "resources/Bag2.png"
BRICK1_PATH = "resources/Brick1.png"
BRICK2_PATH = "resources/Brick2.png"
ROCK1_PATH = "resources/Rock1.png"
ROCK2_PATH = "resources/Rock2.png"
TREE1_PATH = "resources/Tree1.png"
TREE2_PATH = "resources/Tree2.png"


#=====================================================================
# Paths: Training Sprites
#=====================================================================
READY_SPRITES_PATHS = {
    1: "resources/Ready1.png",
    2: "resources/Ready2.png",
    3: "resources/Ready3.png"
}

COUNT_SPRITES_PATHS = {
    4: "resources/Count4.png",
    3: "resources/Count3.png",
    2: "resources/Count2.png",
    1: "resources/Count1.png"
}

MEGA_HIT_PATH = "resources/MegaHit.png"
CLEAR1_PATH = "resources/Clear1.png"
CLEAR2_PATH = "resources/Clear2.png"
WARNING1_PATH = "resources/Warning1.png"
WARNING2_PATH = "resources/Warning2.png"
HIT_ANIMATION_PATH = "resources/Hit.png"

ITEM_SPRITESHEET = "resources/Items.png"
ITEM_SPRITE_SIZE = 48  # Each cell is 48x48 in a 5x7 grid

def update_resolution_constants(width, height):
    global SCREEN_WIDTH, SCREEN_HEIGHT, UI_SCALE, PET_WIDTH, PET_HEIGHT
    global MENU_ICON_SIZE, OPTION_ICON_SIZE, OPTION_FRAME_WIDTH, OPTION_FRAME_HEIGHT, PET_ICON_SIZE
    global FONT_SIZE_SMALL, FONT_SIZE_MEDIUM, FONT_SIZE_MEDIUM_LARGE, FONT_SIZE_LARGE

    SCREEN_WIDTH = width
    SCREEN_HEIGHT = height
    UI_SCALE = SCREEN_HEIGHT / 240  # Or your preferred base value

    MENU_ICON_SIZE = int(24 * UI_SCALE)
    OPTION_ICON_SIZE = int(48 * UI_SCALE)
    OPTION_FRAME_WIDTH = int(96 * UI_SCALE)
    OPTION_FRAME_HEIGHT = int(116 * UI_SCALE)
    PET_ICON_SIZE = int(48 * UI_SCALE)

    FONT_SIZE_SMALL = int(24 * UI_SCALE)
    FONT_SIZE_MEDIUM = int(28 * UI_SCALE)
    FONT_SIZE_MEDIUM_LARGE = int(30 * UI_SCALE)
    FONT_SIZE_LARGE = int(40 * UI_SCALE)

    PET_WIDTH = PET_HEIGHT = SCREEN_HEIGHT // MAX_PETS

    # Also update combat constants
    try:
        import game.core.combat.combat_constants as battle_constants
        if hasattr(battle_constants, "update_combat_constants"):
            battle_constants.update_combat_constants()
    except ImportError:
        pass
