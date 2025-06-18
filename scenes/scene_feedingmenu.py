"""
Scene Feeding Menu
Allows the player to choose food type and feeding strategy for pets.
"""

import os
import pygame

from components.window_background import WindowBackground
from components.window_horizontalmenu import WindowHorizontalMenu
from components.window_petview import WindowPetList
from core import game_globals, runtime_globals
from core.constants import *
from core.utils.pet_utils import distribute_pets_evenly, get_selected_pets
from core.utils.pygame_utils import sprite_load_percent
from core.utils.scene_utils import change_scene

#=====================================================================
# SceneFeedingMenu
#=====================================================================
class SceneFeedingMenu:
    """
    Scene for selecting food and feeding pets.
    """

    def __init__(self) -> None:
        """
        Initializes the feeding menu, loading food frames if necessary.
        """
        self.background = WindowBackground()

        # Add default items (Protein and Vitamin) as the first options, without amount
        self.options = []
        default_sprite_folder = os.path.join("resources", "items")
        for default_item in runtime_globals.default_items.values():
            sprite_path = os.path.join(default_sprite_folder, default_item.sprite_name)
            anim_path = os.path.join(default_sprite_folder, f"{default_item.sprite_name.split('.')[0]}_anim.png")
            if os.path.exists(sprite_path):
                icon = pygame.image.load(sprite_path).convert_alpha()
            else:
                icon = pygame.Surface((48 * UI_SCALE, 48 * UI_SCALE), pygame.SRCALPHA)
            
            self.options.append((default_item.name, icon, -1, anim_path if os.path.exists(anim_path) else None))

        # Add items from inventory (from all modules)
        for module in runtime_globals.game_modules.values():
            if hasattr(module, "items"):
                for item in module.items.values():
                    amount = game_globals.inventory.get(item.id, 0)
                    if amount > 0:
                        sprite_path = os.path.join(module.folder_path, "items", item.sprite_name)
                        anim_path = os.path.join(module.folder_path, "items", f"{item.sprite_name.split('.')[0]}_anim.png")
                        if os.path.exists(sprite_path):
                            icon = pygame.image.load(sprite_path).convert_alpha()
                        else:
                            icon = pygame.Surface((48 * UI_SCALE, 48 * UI_SCALE), pygame.SRCALPHA)
                        # For inventory items, include amount
                        self.options.append((item.name, icon, amount, anim_path if os.path.exists(anim_path) else None))

        

        # Use new method for selection background, scale to screen width, keep proportions
        self.selectionBackground = sprite_load_percent(
            PET_SELECTION_BACKGROUND_PATH,
            percent=100,
            keep_proportion=True,
            base_on="width"
        )

        self.pet_list_window = WindowPetList(lambda: self.get_targets())

        self.menu_window = WindowHorizontalMenu(
            options=self.options,
            get_selected_index_callback=lambda: runtime_globals.food_index,
        )    

        runtime_globals.game_console.log("[SceneFeedingMenu] Feeding frames loaded.")

        # Ensure food_index is valid
        if runtime_globals.food_index >= len(self.options):
            runtime_globals.food_index = 0

    def get_targets(self) -> list:
        """
        Returns a list of pets to feed based on the selected strategy and food type.
        """
        selected_option = self.options[runtime_globals.food_index]
        food_name = selected_option[0]

        # Find the corresponding GameItem object (default or module)
        item_obj = None
        for item in runtime_globals.default_items.values():
            if item.name == food_name:
                item_obj = item
                break
        if not item_obj:
            for module in runtime_globals.game_modules.values():
                if hasattr(module, "items"):
                    for item in module.items.values():
                        if item.name == food_name:
                            item_obj = item
                            break
                    if item_obj:
                        break

        # Fallback: if not found, treat as default hunger
        food_status = getattr(item_obj, "status", "hunger")
        effect = getattr(item_obj, "effect", "status_change")

        if runtime_globals.strategy_index == 0:
            # Manual selection
            if effect == "status_boost":
                # Only allow pets that can battle
                return [pet for pet in get_selected_pets() if pet.can_battle()]
            else:
                # For now, allow all selected pets for hunger/strength/other
                return get_selected_pets()
        else:
            # Auto selection
            if food_status == "hunger":
                return [pet for pet in game_globals.pet_list if pet.hunger < 4 and pet.state != "dead"]
            elif food_status == "strength":
                return [pet for pet in game_globals.pet_list if pet.strength < 4 and pet.state != "dead"]
            elif effect == "status_boost":
                return [pet for pet in game_globals.pet_list if pet.can_battle() and pet.state != "dead"]
            else:
                # For other types, allow all alive pets
                return [pet for pet in game_globals.pet_list if pet.state != "dead"]

    def update(self) -> None:
        """
        Updates the feeding menu scene (currently no dynamic behavior).
        """
        pass

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draws the feeding menu and pet list.
        """
        self.background.draw(surface)
        # Desenha menu horizontal (positions scaled)
        if len(self.options) > 2:
            self.menu_window.draw(surface, x=int(72 * UI_SCALE), y=int(16 * UI_SCALE), spacing=int(30 * UI_SCALE))
        else:
            self.menu_window.draw(surface, x=int(16 * UI_SCALE), y=int(16 * UI_SCALE), spacing=int(16 * UI_SCALE))

        # Desenha pets na parte inferior
        self.pet_list_window.draw(surface)

    def handle_event(self, input_action) -> None:
        """
        Handles keyboard and GPIO button inputs for food and strategy selection.
        """
        if input_action == "B":  # Escape (Cancel/Menu)
            runtime_globals.game_sound.play("cancel")
            change_scene("game")

        elif input_action == "LEFT":  # Move food selection left
            runtime_globals.game_sound.play("menu")
            runtime_globals.food_index = (runtime_globals.food_index - 1) % len(self.options)

        elif input_action == "RIGHT":  # Move food selection right
            runtime_globals.game_sound.play("menu")
            runtime_globals.food_index = (runtime_globals.food_index + 1) % len(self.options)

        elif input_action == "SELECT":  # Cycle strategy
            runtime_globals.game_sound.play("menu")
            runtime_globals.strategy_index = (runtime_globals.strategy_index + 1) % 2

        elif input_action == "A":  # Confirm feeding action (ENTER on PC, A button on Pi)
            targets = self.get_targets()

            if not targets:
                runtime_globals.game_sound.play("cancel")
                return

            runtime_globals.game_sound.play("menu")
            distribute_pets_evenly()

            selected_option = self.options[runtime_globals.food_index]
            food_name = selected_option[0]
            icon = selected_option[1]
            anim_path = selected_option[3] if len(selected_option) > 3 else None

            # Find the corresponding GameItem object (default or module)
            item_obj = None
            food_status = None
            food_amount = 1

            # Look for the GameItem in default_items
            for item in runtime_globals.default_items.values():
                if item.name == food_name:
                    item_obj = item
                    break
            # If not found, look in module items
            if not item_obj:
                for module in runtime_globals.game_modules.values():
                    if hasattr(module, "items"):
                        for item in module.items.values():
                            if item.name == food_name:
                                item_obj = item
                                break
                        if item_obj:
                            break

            if item_obj:
                food_status = item_obj.status
                food_amount = item_obj.amount

            # If the item is a status_boost, update global battle_effects
            if item_obj and item_obj.effect == "status_boost":
                eff = game_globals.battle_effects.get(food_status, {"amount": 0, "boost_time": 0})
                eff["amount"] += food_amount
                eff["boost_time"] += item_obj.boost_time
                game_globals.battle_effects[food_status] = eff

            # Feed each pet and track accepted ones for animation
            runtime_globals.game_pet_eating = {}
            for pet in targets:
                pet.check_disturbed_sleep()
                try:
                    pet_index = game_globals.pet_list.index(pet)
                except ValueError:
                    continue

                accepted = pet.set_eating(food_status, food_amount)
                if accepted:
                    anim_frames = None
                    if anim_path and os.path.exists(anim_path):
                        anim_image = pygame.image.load(anim_path).convert_alpha()
                        w, h = anim_image.get_width() // 4, anim_image.get_height()
                        anim_frames = [
                            pygame.transform.smoothscale(
                                anim_image.subsurface((i * w, 0, w, h)).copy(),
                                (int(PET_WIDTH * 0.75), int(PET_HEIGHT * 0.75))
                            )
                            for i in range(4)
                        ]
                    runtime_globals.game_pet_eating[pet_index] = {
                        "item": item_obj,
                        "sprite": pygame.transform.smoothscale(
                            icon, (int(PET_WIDTH * 0.75), int(PET_HEIGHT * 0.75))
                        ),
                        "anim_frames": anim_frames  # None if not found
                    }

                    # Remove 1 from inventory for non-default items
                    if item_obj and item_obj.id not in [ditem.id for ditem in runtime_globals.default_items.values()]:
                        if item_obj.id in game_globals.inventory:
                            game_globals.inventory[item_obj.id] -= 1
                            if game_globals.inventory[item_obj.id] <= 0:
                                del game_globals.inventory[item_obj.id]

            runtime_globals.game_console.log(f"[SceneFeedingMenu] Fed {len(runtime_globals.game_pet_eating)} pets with {food_name}")
            change_scene("game")
