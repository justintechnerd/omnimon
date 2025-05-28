from core import game_globals, runtime_globals
from core.constants import FONT_SIZE_MEDIUM_LARGE, FONT_SIZE_SMALL

def ensure_module_key(module: str):
    if module not in game_globals.unlocks:
        game_globals.unlocks[module] = {
            "eggs": [],
            "backgrounds": [],
            "evolutions": []
        }

def unlock_item(module: str, category: str, name: str):
    """
    Unlocks an item (egg, background, evolution) for a specific module.
    """
    ensure_module_key(module)
    if name not in game_globals.unlocks[module][category]:
        game_globals.unlocks[module][category].append(name)
        runtime_globals.game_message.add_slide(f"New {category} unlocked!", (255, 255, 0), 56, FONT_SIZE_SMALL)

def is_unlocked(module: str, category: str, name: str) -> bool:
    """
    Checks if an item is unlocked.
    """
    ensure_module_key(module)
    return name in game_globals.unlocks[module][category]

def get_unlocked_backgrounds(module: str) -> list[str]:
    """
    Returns list of unlocked background names for a module.
    """
    ensure_module_key(module)
    return game_globals.unlocks[module]["backgrounds"]