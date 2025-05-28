#=====================================================================
# Screen and Window Constants
#=====================================================================
SCREEN_WIDTH, SCREEN_HEIGHT = 240, 240
FRAME_SIZE = 48  # Original pet sprite frame size
FRAME_RATE = 30  # Frames per second

#=====================================================================
# Pet Constants
#=====================================================================
PET_WIDTH, PET_HEIGHT = 60, 60
PET_ICON_SIZE = 48
MAX_PETS = 4
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
BOOT_TIMER_FRAMES = 150
ROUND_LIMITS = {
    "DMC": {1: 3, 2: 3, 3: 3, 4: 4, 5: 4, 6: 4, 7: 5, 8: 5},
    "PenC": {1: 3, 2: 3, 3: 3, 4: 3, 5: 3, 6: 3, 7: 3, 8: 3, 9: 3, 10: 3}
}

#=====================================================================
# UI Settings
#=====================================================================
MENU_ICON_SIZE = 24  # Icon size (24x24)
OPTION_ICON_SIZE = 48
OPTION_FRAME_WIDTH = 96
OPTION_FRAME_HEIGHT = 116

FONT_SIZE_SMALL = 24
FONT_SIZE_MEDIUM = 28
FONT_SIZE_MEDIUM_LARGE = 30
FONT_SIZE_LARGE = 40

FONT_COLOR_DEFAULT = (255, 255, 255)
FONT_COLOR_GRAY = (150, 150, 150)
FONT_COLOR_GREEN = (0, 231, 58)
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
JOGRESS_ICON_PATH = "resources/Jogress.png"
DUMMY_TRAINING_ICON_PATH = "resources/BagIcon.png"
SHAKE_MATCH_ICON_PATH = "resources/CountTrainingIcon.png"

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

#=====================================================================
# Paths: UI Icons
#=====================================================================
HEART_EMPTY_ICON_PATH = "resources/Heart Empty.png"
HEART_HALF_ICON_PATH = "resources/Heart Half.png"
HEART_FULL_ICON_PATH = "resources/Heart Full.png"
ENERGY_BAR_ICON_PATH = "resources/Energy Bar Count - Green.png"
ENERGY_BAR_BACK_ICON_PATH = "resources/Energy Bar.png"

#=====================================================================
# Paths: Scene Backgrounds
#=====================================================================
SPLASH_PATH = "resources/Splash.png"
EGG_BACKGROUND_PATH = "resources/EggBackground.png"
MAIN_MENU_PATH = "resources/Menu.png"

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
BATTLE1_PATH = "resources/Battle1.png"
BATTLE2_PATH = "resources/Battle2.png"
BAG1_PATH = "resources/Bag1.png"
BAG2_PATH = "resources/Bag2.png"

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

__all__ = [
    # Screen and Window Constants
    "SCREEN_WIDTH", "SCREEN_HEIGHT", "FRAME_SIZE", "FRAME_RATE",

    # Pet Constants
    "PET_WIDTH", "PET_HEIGHT", "PET_ICON_SIZE", "MAX_PETS", "STAGES", "ATTR_COLORS",

    # Game Mechanics
    "MOVE_SPEED", "IDLE_PROBABILITY", "CLEANING_SPEED",
    "SLEEP_DISTURBANCE_THRESHOLD_SECONDS", "SLEEP_RECOVERY_HOURS",
    "SLEEP_MANUAL_DURATION_HOURS", "BOOT_TIMER_FRAMES", "ROUND_LIMITS",

    # UI Settings
    "MENU_ICON_SIZE", "OPTION_ICON_SIZE", "OPTION_FRAME_WIDTH", "OPTION_FRAME_HEIGHT",
    "FONT_SIZE_SMALL", "FONT_SIZE_MEDIUM", "FONT_SIZE_MEDIUM_LARGE", "FONT_SIZE_LARGE",
    "FONT_COLOR_DEFAULT", "FONT_COLOR_GREEN", "FONT_COLOR_YELLOW", "FONT_COLOR_BLUE",
    "BACKGROUND_COLOR", "FONT_COLOR_GRAY",

    # Paths: General Resources
    "MODULES_FOLDER", "ARROW_IMAGE_PATH", "FOOD_SHEET_PATH", "ATK_FOLDER",

    # Paths: UI Sprites
    "SELECTION_OFF_PATH", "SELECTION_ON_PATH", "PET_SELECTION_BACKGROUND_PATH",
    "MENU_BACKGROUND_PATH", "PET_SELECTION_SMALL_ON_PATH", "PET_SELECTION_SMALL_OFF_PATH",

    # Paths: Battle & Training Sprites
    "BATTLE_BACKGROUND_PATH", "TRAINING_BACKGROUND_PATH", "HEADTRAINING_PATH",
    "BATTLE_ICON_PATH", "HEAD_TRAINING_ICON_PATH", "JOGRESS_ICON_PATH", "VS_PATH",
    "STRIKES_BACK_PATH", "STRIKE_PATH", "NEXT_BATTLE_ICON_PATH", "RESTART_BATTLE_ICON_PATH",
    "CLEAR1_PATH", "CLEAR2_PATH", "WARNING1_PATH", "WARNING2_PATH", "HIT_ANIMATION_PATH",
    "DUMMY_TRAINING_ICON_PATH", "SHAKE_MATCH_ICON_PATH",

    # Paths: Pet Sprites
    "DEAD_FRAME_PATH", "AGE_ICON_PATH", "WEIGHT_ICON_PATH", "MODULE_ICON_PATH",
    "VERSION_ICON_PATH", "MISTAKES_ICON_PATH", "TRAITED_ICON_PATH", "SPECIAL_ICON_PATH",
    "SHINY_ICON_PATH", "SHOOK_ICON_PATH", "OVERFEED_ICON_PATH", "SICK_ICON_PATH",
    "SLEEP_DISTURBANCES_ICON_PATH",

    # Paths: UI Icons
    "HEART_EMPTY_ICON_PATH", "HEART_HALF_ICON_PATH", "HEART_FULL_ICON_PATH",
    "ENERGY_BAR_ICON_PATH", "ENERGY_BAR_BACK_ICON_PATH",

    # Paths: Scene Backgrounds
    "SPLASH_PATH", "EGG_BACKGROUND_PATH", "MAIN_MENU_PATH",

    # Paths: Battle Scene Sprites
    "BATTLE_SPRITE_PATH", "BATTLE_LEVEL_SPRITE_PATH", "BAR_BACK_PATH",
    "BAR_PIECE_PATH", "TRAINING_MAX_PATH", "ALERT_SPRITE_PATH", "GO_SPRITE_PATH",
    "BATTLE1_PATH", "BATTLE2_PATH", "BAG1_PATH", "BAG2_PATH",

    # Paths: Training Sprites
    "READY_SPRITES_PATHS", "COUNT_SPRITES_PATHS", "MEGA_HIT_PATH"
]