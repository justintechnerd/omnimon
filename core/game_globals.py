import datetime
import os
import pickle
import random
import time

#=====================================================================
# Game Global State
#=====================================================================

SAVE_FILE = "save/save_data.dat"

# Persistent variables
game_background = None
background_module_name = None

pet_list = []
poop_list = []
traited = []
unlocks = {}
debug = False
showClock = True
sound = 1
battle_area = {}
battle_round = {}
rotated = False
xai = 1
xai_date = datetime.date.today()
inventory = {}
battle_effects = {}

# Internal timer for autosave
_last_save_time = time.time()
AUTOSAVE_INTERVAL_SECONDS = 60  # 5 minutes

def save() -> None:
    """
    Saves the current global game state to a file.
    """
    data = {
        "pet_list": pet_list,
        "poop_list": poop_list,
        "traited": traited,
        "game_background": game_background,
        "battle_area": battle_area,
        "battle_round": battle_round,
        "background_module_name": background_module_name,
        "unlocks": unlocks,
        "showClock": showClock,
        "sound": sound,
        "debug": debug,
        "xai": xai,
        "xai_date": xai_date,
        "inventory": inventory,
        "battle_effects": battle_effects,
    }

    with open(SAVE_FILE, "wb") as f:
        pickle.dump(data, f)
        f.flush()
        os.fsync(f.fileno())

def load() -> None:
    """
    Loads the global game state from the save file, if it exists.
    """
    global pet_list, poop_list, traited, unlocks, battle_area, battle_round, xai, xai_date
    global game_background, background_module_name, showClock, sound, debug, inventory, battle_effects

    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "rb") as f:
            data = pickle.load(f)

            pet_list = data.get("pet_list", [])
            poop_list = data.get("poop_list", [])
            traited = data.get("traited", [])
            game_background = data.get("game_background", None)
            battle_area = data.get("battle_area", {})
            battle_round = data.get("battle_round", {})
            background_module_name = data.get("background_module_name", None)
            unlocks = data.get("unlocks", {})
            showClock = data.get("showClock", True)
            sound = data.get("sound", 1)
            debug = data.get("debug", True)
            xai = data.get("xai", random.randint(1, 7))
            xai_date = data.get("xai_date", datetime.date.today())
            inventory = data.get("inventory", {})
            battle_effects = data.get("battle_effects", {})

def autosave() -> None:
    """
    Automatically saves the game if the autosave interval has passed.
    """
    global _last_save_time
    now = time.time()

    if now - _last_save_time >= AUTOSAVE_INTERVAL_SECONDS:
        save()
        _last_save_time = now
