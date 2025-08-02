from core import game_globals, runtime_globals
from game.core import constants

def get_selected_pets():
    """
    Returns the list of currently selected pets, or all alive pets if none are selected.
    """
    if runtime_globals.selected_pets:
        pet_list = [pet for pet in runtime_globals.selected_pets if pet.state != "dead"]
    else:
        pet_list = [pet for pet in game_globals.pet_list if pet.state != "dead"]
    return pet_list

def get_training_targets():
    """
    Returns pets eligible for training based on the current strategy.
    """
    if runtime_globals.strategy_index == 0:
        return [pet for pet in get_selected_pets() if pet.can_train()]
    else:
        return [pet for pet in get_selected_pets() if pet.can_train() and pet.effort < 16]

def get_battle_targets():
    """
    Returns pets eligible for battle.
    """
    return [pet for pet in get_selected_pets() if pet.can_battle() and pet.dp > 0]

def pets_need_care():
    """
    Returns True if any pet needs care (callsign is active).
    """
    for pet in game_globals.pet_list:
        if pet.call_sign():
            return True
    return False

def all_pets_hatched():
    """
    Returns True if all pets are hatched (stage > 0).
    """
    return all(pet.stage > 0 for pet in game_globals.pet_list)

def distribute_pets_evenly():
    """
    Evenly distributes pets across the screen horizontally.
    """
    pet_list = [pet for pet in game_globals.pet_list if pet.state != "dead"]
    count = len(pet_list)
    if count == 0:
        return
    if count == 1:
        pet_list[0].x = (constants.SCREEN_WIDTH - constants.PET_WIDTH) // 2
        pet_list[0].subpixel_x = float(pet_list[0].x)
        return
    section_width = constants.SCREEN_WIDTH / count
    center_positions = [(section_width * i + section_width / 2) for i in range(count)]
    for i, pet in enumerate(pet_list):
        pet.x = int(center_positions[i] - constants.PET_WIDTH / 2)
        pet.subpixel_x = float(pet.x)

def draw_pet_outline(surface, frame, x, y, color=(255, 255, 0)):
    """
    Draws an outline around a pet sprite frame.
    """
    import pygame
    mask = pygame.mask.from_surface(frame)
    outline = mask.outline()
    if outline:
        outline = [(x + px, y + py) for px, py in outline]
        pygame.draw.lines(surface, color, True, outline, 2)