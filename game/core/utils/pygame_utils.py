import hashlib
import os
import pygame
import time
import game.core.constants as constants
from core import game_console, game_globals, runtime_globals
from game.core.utils.module_utils import get_module

shadow_cache = {}

def get_surface_hash(surface):
    """Generate a hash of the surface’s pixel data to uniquely identify it."""
    return hashlib.md5(pygame.image.tostring(surface, "RGBA")).hexdigest()

def get_shadow(sprite, shadow_color=(0, 0, 0, 100)):
    key = get_surface_hash(sprite)
    if key not in shadow_cache:
        shadow = sprite.copy()
        shadow.fill(shadow_color, special_flags=pygame.BLEND_RGBA_MULT)
        shadow_cache[key] = shadow
    return shadow_cache[key]

def blit_with_shadow(surface, sprite, pos, offset=(2, 2)):
    """
    Blits a sprite with a shadow effect and logs the number of calls per second.
    """
    if constants.DEBUG:
        global _blit_shadow_calls, _last_log_time

        # Increment the counter
        _blit_shadow_calls += 1

        # Log the count every second
        current_time = time.time()
        if current_time - _last_log_time >= 1:
            runtime_globals.game_console.log(f"blit_with_shadow calls per second: {_blit_shadow_calls}")
            _blit_shadow_calls = 0
            _last_log_time = current_time

    # Perform the blit with shadow
    shadow = get_shadow(sprite)
    surface.blit(shadow, (pos[0] + offset[0], pos[1] + offset[1]))
    surface.blit(sprite, pos)

def get_font(size=24):
    return pygame.font.Font("resources/vpet_font.TTF", size)

def get_font_alt(size=24):
    return pygame.font.Font("resources/vpet_font_alt.ttf", size)

def sprite_load(path, size=None, scale=1):
    img = pygame.image.load(path).convert_alpha()
    if size:
        return pygame.transform.scale(img, size)
    elif scale != 1:
        base_size = img.get_size()
        new_size = (int(base_size[0] * scale), int(base_size[1] * scale))
        return pygame.transform.scale(img, new_size)
    return img

def sprite_load_percent(path, percent=100, keep_proportion=True, base_on="height", alpha=True):
    img = pygame.image.load(path)
    if alpha:
        img = img.convert_alpha()
    else:
        img = img.convert()
    orig_w, orig_h = img.get_size()
    ref_size = constants.SCREEN_WIDTH if base_on == "width" else constants.SCREEN_HEIGHT
    target = int(ref_size * (percent / 100.0))
    if keep_proportion:
        scale_factor = target / orig_h if base_on == "height" else target / orig_w
        new_w = int(orig_w * scale_factor)
        new_h = int(orig_h * scale_factor)
    else:
        if base_on == "height":
            new_w = orig_w
            new_h = target
        else:
            new_w = target
            new_h = orig_h
    return pygame.transform.scale(img, (new_w, new_h))

def sprite_load_percent_wh(path, percent_w=100, percent_h=100, keep_proportion=True):
    img = pygame.image.load(path).convert_alpha()
    orig_w, orig_h = img.get_size()
    target_w = int(constants.SCREEN_WIDTH * (percent_w / 100.0))
    target_h = int(constants.SCREEN_HEIGHT * (percent_h / 100.0))
    if keep_proportion:
        scale_factor = min(target_w / orig_w, target_h / orig_h)
        new_w = int(orig_w * scale_factor)
        new_h = int(orig_h * scale_factor)
    else:
        new_w = target_w
        new_h = target_h
    return pygame.transform.scale(img, (new_w, new_h))

def load_attack_sprites():
    attack_sprites = {}
    for filename in os.listdir("resources/atk"):
        if filename.endswith(".png"):
            path = os.path.join("resources/atk", filename)
            sprite = pygame.image.load(path).convert_alpha()
            sprite = pygame.transform.scale(sprite, (24 * constants.UI_SCALE, 24 * constants.UI_SCALE))
            atk_id = filename.split(".")[0]
            attack_sprites[atk_id] = sprite
    return attack_sprites

def module_attack_sprites(module):
    """
    Returns a dictionary of attack sprites for the given module.
    Returns empty dict if module not found or no atk folder exists.
    """
    mod = get_module(module)
    if not mod:
        game_console.log(f"[!] Module {module} not found for attack sprites.")
        return {}
    
    attack_sprites = {}
    atk_folder = os.path.join(mod.folder_path, "atk")
    
    # Check if atk folder exists
    if not os.path.exists(atk_folder):
        return {}
    
    try:
        for filename in os.listdir(atk_folder):
            if filename.endswith(".png"):
                path = os.path.join(atk_folder, filename)
                sprite = pygame.image.load(path).convert_alpha()
                sprite = pygame.transform.scale(sprite, (24 * constants.UI_SCALE, 24 * constants.UI_SCALE))
                atk_id = filename.split(".")[0]
                attack_sprites[atk_id] = sprite
    except (OSError, pygame.error) as e:
        game_console.log(f"[!] Error loading attack sprites for module {module}: {e}")
        return {}
    
    return attack_sprites

def load_misc_sprites():
    global misc_sprites
    sprite_files = [
        "Cheer.png", "Mad1.png", "Mad2.png",
        "Sick1.png", "Sick2.png", "Sleep1.png",
        "Sleep2.png", "Poop1.png", "Poop2.png",
        "JumboPoop1.png", "JumboPoop2.png", "Wash.png"
    ]
    misc_sprites = {}
    for filename in sprite_files:
        path = os.path.join("resources", filename)
        try:
            sprite = sprite_load(path)
            misc_sprites[filename.split('.')[0]] = pygame.transform.scale(
                sprite, (sprite.get_width() * constants.UI_SCALE, sprite.get_height() * constants.UI_SCALE)
            )
            
        except pygame.error as e:
            runtime_globals.game_console.log(f"[!] Error loading {filename}: {e}")
    return misc_sprites

# Counter and timer for logging
_blit_shadow_calls = 0
_last_log_time = time.time()

# Counter and timer for logging
_blit_cache_calls = 0
_last_cache_log_time = time.time()

blit_cache = {}

def blit_with_cache(surface, sprite, pos):
    """
    Blits a sprite using caching and logs the number of calls per second.
    """
    if constants.DEBUG:
        global _blit_cache_calls, _last_cache_log_time

        # Generate a hash for the sprite
        key = get_surface_hash(sprite)

        # Use cached sprite if available
        if key not in blit_cache:
            blit_cache[key] = sprite.copy()

        # Increment the counter
        _blit_cache_calls += 1

        # Log the count every second
        current_time = time.time()
        if current_time - _last_cache_log_time >= 1:
            runtime_globals.game_console.log(f"blit_with_cache calls per second: {_blit_cache_calls}")
            _blit_cache_calls = 0
            _last_cache_log_time = current_time

    # Perform the blit
    surface.blit(sprite, pos)