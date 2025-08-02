import datetime
import os
import pickle
import random
import time

#=====================================================================
# Game Global State
#=====================================================================

SAVE_FILE = "save/save_data.dat"
SAVE_DIR = "save"
MAX_BACKUPS = 5  # Keep 5 backup files

# Persistent variables
game_background = None
background_module_name = None
background_high_res = False

pet_list = []
poop_list = []
traited = []
unlocks = {}
showClock = True
sound = 3
battle_area = {}
battle_round = {}
rotated = False
xai = 1
xai_date = datetime.date.today()
inventory = {}
battle_effects = {}
wake_time = None
sleep_time = None

# Internal timer for autosave
_last_save_time = time.time()
AUTOSAVE_INTERVAL_SECONDS = 60  # 5 minutes

def get_next_save_number():
    """Get the next save file number for backup rotation."""
    if not os.path.exists(SAVE_DIR):
        return 1
    
    # Find existing save files
    save_numbers = []
    for filename in os.listdir(SAVE_DIR):
        if filename.startswith("save_data") and filename.endswith(".dat"):
            if filename == "save_data.dat":
                save_numbers.append(1)
            else:
                # Extract number from save_data_X.dat
                try:
                    number_part = filename.replace("save_data_", "").replace(".dat", "")
                    save_numbers.append(int(number_part))
                except ValueError:
                    continue
    
    if not save_numbers:
        return 1
    
    return max(save_numbers) + 1

def get_latest_save_file():
    """Get the path to the most recent save file."""
    if not os.path.exists(SAVE_DIR):
        return None
    
    # Find existing save files with their numbers
    save_files = []
    for filename in os.listdir(SAVE_DIR):
        if filename.startswith("save_data") and filename.endswith(".dat"):
            full_path = os.path.join(SAVE_DIR, filename)
            if filename == "save_data.dat":
                save_files.append((1, full_path))
            else:
                # Extract number from save_data_X.dat
                try:
                    number_part = filename.replace("save_data_", "").replace(".dat", "")
                    save_files.append((int(number_part), full_path))
                except ValueError:
                    continue
    
    if not save_files:
        return None
    
    # Return the file with the highest number
    save_files.sort(key=lambda x: x[0], reverse=True)
    return save_files[0][1]

def cleanup_old_saves():
    """Remove old backup saves beyond MAX_BACKUPS."""
    if not os.path.exists(SAVE_DIR):
        return
    
    # Find all save files with their numbers
    save_files = []
    for filename in os.listdir(SAVE_DIR):
        if filename.startswith("save_data") and filename.endswith(".dat"):
            full_path = os.path.join(SAVE_DIR, filename)
            if filename == "save_data.dat":
                save_files.append((1, full_path))
            else:
                try:
                    number_part = filename.replace("save_data_", "").replace(".dat", "")
                    save_files.append((int(number_part), full_path))
                except ValueError:
                    continue
    
    # Keep only the most recent MAX_BACKUPS files
    if len(save_files) > MAX_BACKUPS:
        save_files.sort(key=lambda x: x[0], reverse=True)
        files_to_remove = save_files[MAX_BACKUPS:]
        
        for _, file_path in files_to_remove:
            try:
                os.remove(file_path)
                print(f"[Save] Removed old backup: {os.path.basename(file_path)}")
            except Exception as e:
                print(f"[Save] Failed to remove old backup {file_path}: {e}")

def save() -> None:
    """
    Saves the current global game state to a file with backup rotation.
    """
    # Ensure save directory exists
    if not os.path.exists(SAVE_DIR):
        try:
            os.makedirs(SAVE_DIR)
            print(f"[Save] Created save directory: {SAVE_DIR}")
        except Exception as e:
            print(f"[Save] Failed to create save directory: {e}")
            return
    
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
        "xai": xai,
        "xai_date": xai_date,
        "inventory": inventory,
        "battle_effects": battle_effects,
        "background_high_res": background_high_res,
        "wake_time": wake_time,
        "sleep_time": sleep_time,
    }

    # Get the next save number and create the filename
    save_number = get_next_save_number()
    if save_number == 1:
        save_path = SAVE_FILE  # First save uses the original name
    else:
        save_path = os.path.join(SAVE_DIR, f"save_data_{save_number}.dat")

    try:
        with open(save_path, "wb") as f:
            pickle.dump(data, f)
            f.flush()
            os.fsync(f.fileno())
        
        print(f"[Save] Game saved successfully to: {os.path.basename(save_path)}")
        
        # Clean up old saves
        cleanup_old_saves()
        
    except Exception as e:
        print(f"[Save] Failed to save game: {e}")

def load() -> None:
    """
    Loads the global game state from the most recent save file, with fallback to previous saves.
    """
    global pet_list, poop_list, traited, unlocks, battle_area, battle_round, xai, xai_date, background_high_res
    global game_background, background_module_name, showClock, sound, inventory, battle_effects
    global wake_time, sleep_time

    # Get all available save files in order (newest first)
    save_files_to_try = []
    
    if not os.path.exists(SAVE_DIR):
        try:
            os.makedirs(SAVE_DIR)
            print(f"[Save] Created save directory: {SAVE_DIR}")
        except Exception as e:
            print(f"[Save] Failed to create save directory: {e}")
            return

    if os.path.exists(SAVE_DIR):
        # Find all save files with their numbers
        all_saves = []
        for filename in os.listdir(SAVE_DIR):
            if filename.startswith("save_data") and filename.endswith(".dat"):
                full_path = os.path.join(SAVE_DIR, filename)
                if filename == "save_data.dat":
                    all_saves.append((1, full_path))
                else:
                    try:
                        number_part = filename.replace("save_data_", "").replace(".dat", "")
                        all_saves.append((int(number_part), full_path))
                    except ValueError:
                        continue
        
        # Sort by number (newest first)
        all_saves.sort(key=lambda x: x[0], reverse=True)
        save_files_to_try = [save_path for _, save_path in all_saves]
    
    # If no numbered saves found, try the original file
    if not save_files_to_try and os.path.exists(SAVE_FILE):
        save_files_to_try = [SAVE_FILE]

    # Try to load each save file in order
    for save_path in save_files_to_try:
        try:
            with open(save_path, "rb") as f:
                data = pickle.load(f)

                # Load pet list with error handling
                loaded_pet_list = data.get("pet_list", [])
                valid_pets = []
                
                for pet in loaded_pet_list:
                    if pet is None:
                        continue
                        
                    try:
                        # Test basic pet attributes safely
                        if (hasattr(pet, 'name') and hasattr(pet, 'module') and 
                            hasattr(pet, 'stage') and hasattr(pet, 'state')):
                            
                            # Initialize missing attributes for compatibility
                            if not hasattr(pet, 'trophies'):
                                pet.trophies = 0
                            if not hasattr(pet, 'vital_values'):
                                pet.vital_values = 0
                            
                            # Apply any patches from the pet class
                            if hasattr(pet, 'patch'):
                                pet.patch()
                                
                            valid_pets.append(pet)
                            print(f"[Game] Successfully loaded pet: {pet.name}")
                        else:
                            print(f"[Game] Pet missing required attributes, skipping")
                            continue
                            
                    except Exception as e:
                        print(f"[Game] Failed to load pet (removing from save): {e}")
                        continue
                
                pet_list = valid_pets
                poop_list = data.get("poop_list", [])
                for poop in poop_list:
                    poop.patch()  # Ensure all poops have necessary attributes

                traited = data.get("traited", [])
                game_background = data.get("game_background", None)
                battle_area = data.get("battle_area", {})
                battle_round = data.get("battle_round", {})
                background_module_name = data.get("background_module_name", None)
                unlocks = data.get("unlocks", {})
                showClock = data.get("showClock", True)
                sound = data.get("sound", 1)
                xai = data.get("xai", random.randint(1, 7))
                xai_date = data.get("xai_date", datetime.date.today())
                inventory = data.get("inventory", {})
                battle_effects = data.get("battle_effects", {})
                background_high_res = data.get("background_high_res", False)
                wake_time = data.get("wake_time", None)
                sleep_time = data.get("sleep_time", None)
                
                print(f"[Game] Successfully loaded save file: {os.path.basename(save_path)} with {len(pet_list)} valid pets")
                return  # Successfully loaded, exit the function
                
        except Exception as e:
            print(f"[Game] Failed to load save file {os.path.basename(save_path)}: {e}")
            continue  # Try the next save file
    
    # If we get here, all save files failed to load
    print(f"[Game] All save files failed to load. Starting with fresh game state.")
    # Reset to default values
    pet_list = []
    poop_list = []
    traited = []
    game_background = None
    battle_area = {}
    battle_round = {}
    background_module_name = None
    unlocks = {}
    showClock = True
    sound = 1
    xai = random.randint(1, 7)
    xai_date = datetime.date.today()
    inventory = {}
    battle_effects = {}
    background_high_res = False
    wake_time = None
    sleep_time = None

def autosave() -> None:
    """
    Automatically saves the game if the autosave interval has passed.
    """
    global _last_save_time
    now = time.time()

    if now - _last_save_time >= AUTOSAVE_INTERVAL_SECONDS:
        save()
        _last_save_time = now
