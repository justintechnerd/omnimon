import os
import pygame

from core import game_globals, runtime_globals
from core.constants import *
from core.game_module import GameModule


#=====================================================================
# Utility Functions
#=====================================================================

def draw_pet_outline(surface, frame, x, y, color=(255, 255, 0)):
    """
    Draws a colored outline around the non-transparent part of a pet sprite.
    
    Args:
        surface (pygame.Surface): Surface to draw on.
        frame (pygame.Surface): Sprite frame of the pet.
        x (int): X coordinate.
        y (int): Y coordinate.
        color (tuple): RGB color for the outline (default: yellow).
    """
    mask = pygame.mask.from_surface(frame)
    outline = mask.outline()

    if outline:
        outline = [(x + px, y + py) for px, py in outline]
        pygame.draw.lines(surface, color, True, outline, 2)

def get_selected_pets():
    """
    Returns selected pets if any are selected; otherwise returns all pets.
    
    Returns:
        list: List of GamePet instances.
    """
    if runtime_globals.selected_pets:
        pet_list = [pet for pet in runtime_globals.selected_pets if pet.state != "dead"]
    else:
        pet_list = [pet for pet in game_globals.pet_list if pet.state != "dead"]

    return pet_list

def get_training_targets():
    if runtime_globals.strategy_index == 0:
        return [pet for pet in game_globals.pet_list if pet.can_train()]
    else:
        return [pet for pet in get_selected_pets() if pet.can_train() and pet.effort < 16]

def get_battle_targets():
    return [pet for pet in get_selected_pets() if pet.can_battle() and pet.dp > 0]

def pets_need_care():
    for pet in game_globals.pet_list:
        if pet.call_sign():
            return True;
    return False

#=====================================================================
# Font Handling
#=====================================================================

def get_font(size=24):
    """
    Returns a font object with the given size.
    
    Args:
        size (int): Font size.
        
    Returns:
        pygame.font.Font
    """
    return pygame.font.Font("resources/vpet_font.TTF", size)

def get_font_alt(size=24):
    """
    Returns a font object with the given size.
    
    Args:
        size (int): Font size.
        
    Returns:
        pygame.font.Font
    """
    return pygame.font.Font("resources/vpet_font_alt.ttf", size)

#=====================================================================
# Pet Handling
#=====================================================================

def all_pets_hatched():
    """
    Checks if all pets have hatched (stage > 0).
    
    Returns:
        bool
    """
    return all(pet.stage > 0 for pet in game_globals.pet_list)

def distribute_pets_evenly():
    """
    Distributes all pets in game_globals.pet_list horizontally across the screen,
    centering them nicely, avoiding screen borders, and ignoring dead pets.
    """
    pet_list = [pet for pet in game_globals.pet_list if pet.state != "dead"]
    count = len(pet_list)

    if count == 0:
        return

    if count == 1:
        # Center the single pet
        pet_list[0].x = (SCREEN_WIDTH - PET_WIDTH) // 2
        pet_list[0].subpixel_x = float(pet_list[0].x)
        return

    # Calculate even spacing based on count
    section_width = SCREEN_WIDTH / count  # Split the screen into equal sections
    center_positions = [(section_width * i + section_width / 2) for i in range(count)]

    for i, pet in enumerate(pet_list):
        pet.x = int(center_positions[i] - PET_WIDTH / 2)  # Center pet in its section
        pet.subpixel_x = float(pet.x)

def blit_with_shadow(surface, sprite, pos, offset=(2, 2), shadow_color=(0, 0, 0, 100)):
    """Draw a shadow behind a sprite."""
    # Create a copy of the sprite
    shadow = sprite.copy()
    # Fill it with shadow color while preserving alpha
    shadow.fill(shadow_color, special_flags=pygame.BLEND_RGBA_MULT)
    # Blit the shadow first, slightly offset
    surface.blit(shadow, (pos[0] + offset[0], pos[1] + offset[1]))
    # Blit the real sprite on top
    surface.blit(sprite, pos)

def load_attack_sprites():
    attack_sprites = {}
    for filename in os.listdir("resources/atk"):
        if filename.endswith(".png"):
            path = os.path.join("resources/atk", filename)
            sprite = pygame.image.load(path).convert_alpha()
            sprite = pygame.transform.scale(sprite, (24, 24))
            atk_id = filename.split(".")[0]
            attack_sprites[atk_id] = sprite
    return attack_sprites

def load_modules() -> list:
    """
    Loads all available game modules from the 'modules' folder, skipping folders without 'module.json'.
    """
    module_dir = MODULES_FOLDER

    runtime_globals.game_modules = {}
    for folder in os.listdir(module_dir):
        folder_path = os.path.join(module_dir, folder)
        module_json_path = os.path.join(folder_path, "module.json")  # 🔹 Path to module.json
        
        # 🔹 Check if folder exists and contains 'module.json'
        if os.path.isdir(folder_path) and os.path.exists(module_json_path):
            module = GameModule(folder_path)
            
            # 🔥 Enable rulesets
            if module.ruleset == "dmc":
                runtime_globals.dmc_enabled = True
            if module.ruleset == "penc":
                runtime_globals.penc_enabled = True

            # 🔥 Manage adventure mode modules
            if module.adventure_mode and game_globals.battle_area.get(module.name) is None:
                game_globals.battle_area[module.name] = 1
                game_globals.battle_round[module.name] = 1
            
            # 🔥 Store module in global dictionary
            runtime_globals.game_modules[module.name] = module

    runtime_globals.game_console.log(f"[SceneEggSelection] Loaded Modules: {len(runtime_globals.game_modules)}")
    return runtime_globals.game_modules

def get_module(name):
    return runtime_globals.game_modules[name]

def change_scene(scene):
    runtime_globals.game_state_update = True
    runtime_globals.game_state = scene

def load_feeding_frames() -> None:
    """
    Loads food animation frames from the resources.
    """
    sheet = pygame.image.load(FOOD_SHEET_PATH).convert_alpha()
    cols, rows = 4, 2
    cell_size = 24

    for row in range(rows):
        for col in range(cols):
            x = col * cell_size
            y = row * cell_size
            frame = sheet.subsurface((x, y, cell_size, cell_size)).copy()
            frame = pygame.transform.scale(frame, (OPTION_ICON_SIZE, OPTION_ICON_SIZE))
            runtime_globals.feeding_frames.append(frame)

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
