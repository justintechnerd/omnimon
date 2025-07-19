"""
Scene Main Game
The main scene where pets live, eat, sleep, move, and interact.
"""
import random
import pygame
import datetime
import os
import time

from components.window_background import WindowBackground
from components.window_clock import WindowClock
from components.window_mainmenu import WindowMenu
from core import game_globals, runtime_globals
from core.constants import *
from core.game_evolution_entity import GameEvolutionEntity
from core.utils.module_utils import get_module
from core.utils.pet_utils import all_pets_hatched, distribute_pets_evenly, draw_pet_outline, get_selected_pets
from core.utils.pygame_utils import blit_with_cache
from core.utils.scene_utils import change_scene

HEARTS_SIZE = 8 * UI_SCALE
#=====================================================================
# SceneMainGame
#=====================================================================
class SceneMainGame:
    """
    Handles the main game scene, including pets, menu navigation, and interactions.
    """

    def __init__(self) -> None:
        """
        Initializes the main game scene.
        """
        self.background = WindowBackground()
        self.menu = WindowMenu()
        self.clock = WindowClock()
        self.fade_out_timer = 1800
        self.selection_mode = "menu"
        self.pet_selection_index = 0
        self.fade_alpha = 0
        self.lock_inputs = False
        self.lock_updates = False

        self.sprites = {
            "heart_empty": pygame.transform.scale(pygame.image.load(HEART_EMPTY_ICON_PATH).convert_alpha(), (HEARTS_SIZE, HEARTS_SIZE)),
            "heart_half": pygame.transform.scale(pygame.image.load(HEART_HALF_ICON_PATH).convert_alpha(), (HEARTS_SIZE, HEARTS_SIZE)),
            "heart_full": pygame.transform.scale(pygame.image.load(HEART_FULL_ICON_PATH).convert_alpha(), (HEARTS_SIZE, HEARTS_SIZE))
        }

        self.cleaning = False
        self.cleaning_x = SCREEN_WIDTH
        self.cleaning_speed = CLEANING_SPEED
        self._hearts_cache = {}
        self._fade_overlay_cache = None  # Cache fade overlay surface

        today = datetime.date.today()
        if game_globals.xai_date < today:
            game_globals.xai = random.randint(1, 7)
            game_globals.xai_date = today
            game_globals.xai_date = today

        self.food_anims = {}  # {pet_index: [frames]} for animated food sprites
        self.load()

    def update(self) -> None:
        """
        Updates all game objects (pets, background, poops, cleaning effect).
        """
        if self.lock_updates:
            self.check_evolution_start()
            return

        # Update pets and poops only if necessary
        for pet in game_globals.pet_list:
            pet.update()

        for poop in game_globals.poop_list:
            poop.update()

        # Handle fade-out timer
        if self.fade_out_timer > 0:
            self.fade_out_timer -= 1
            if self.fade_out_timer <= 0:
                runtime_globals.main_menu_index = -1
                runtime_globals.selected_pets = []

        # Update cleaning animation only if active
        if self.cleaning:
            self.update_cleaning()

        # Check evolution start
        self.check_evolution_start()

        # Update background and game messages
        self.background.update()
        runtime_globals.game_message.update()

    def check_evolution_start(self):
        """Begins evolution sequence when a pet is ready to evolve."""
        if runtime_globals.evolution_pet:
            self.start_evolution_sequence()

    def start_evolution_sequence(self):
        """Handles the epic evolution sequence based on music timing."""
        if self.lock_inputs:
            music_time = runtime_globals.game_sound.get_music_position()

            if music_time >= 5:
                self.lock_updates = True
                self.move_evolving_pet_to_center()

            if music_time >= 12:
                self.fade_out_except_evolving_pet()

            if music_time >= 18:
                evo = GameEvolutionEntity(
                    from_name = "MetalGreymon",
                    from_attribute = "Da",
                    from_sprite = runtime_globals.pet_sprites[game_globals.pet_list[0]][0],
                    to_attribute = "Vi",
                    to_name = "WarGreymon",
                    to_sprite = runtime_globals.pet_sprites[game_globals.pet_list[1]][0],
                    stage = 5)
                
                runtime_globals.evolution_data = [evo]
                change_scene("evolution")
        else:
            runtime_globals.game_sound.play("evolution_2020")  # 🔥 Start with fade-in
            self.lock_inputs = True

    def move_evolving_pet_to_center(self):
        """Moves the evolving pet toward the center of the screen."""
        pet = runtime_globals.evolution_pet
        if pet.x < (SCREEN_WIDTH - PET_WIDTH) // 2:
            pet.x += 1  # 🔥 Gradually move to center
            pet.direction = 1
            pet.set_state("moving")
        elif pet.x > (SCREEN_WIDTH - PET_WIDTH) // 2:
            pet.x -= 1
            pet.direction = -1
            pet.set_state("moving")
        else:
            pet.x = (SCREEN_WIDTH - PET_WIDTH) // 2
            pet.direction = -1
            pet.set_state("idle")

    def fade_out_except_evolving_pet(self):
        """Gradually dims the screen, leaving only the evolving pet visible."""
        self.fade_alpha = min(self.fade_alpha + 5, 255)

    def update_cleaning(self) -> None:
        """
        Updates the screen cleaning animation.
        """
        if not self.cleaning:
            return

        self.cleaning_x -= self.cleaning_speed
        for poop in game_globals.poop_list:
            poop.x -= self.cleaning_speed

        if self.cleaning_x <= -runtime_globals.misc_sprites["Wash"].get_width():
            game_globals.poop_list.clear()
            self.cleaning = False
            self.cleaning_x = SCREEN_WIDTH
            runtime_globals.game_sound.play("happy")
            for pet in game_globals.pet_list:
                pet.set_state("happy2")
            runtime_globals.game_console.log("[SceneMainGame] Cleaning complete.")

    def load(self):
        """
        Loads the scene, preparing pets, background, and any necessary resources.
        """
        # Prepare food animations for pets that are eating
        self.food_anims = {}
        for pet_index, food_info in getattr(runtime_globals, "game_pet_eating", {}).items():
            # Use preloaded anim_frames if available, otherwise fallback to icon sprite
            anim_frames = food_info.get("anim_frames")
            icon = food_info.get("sprite")
            if anim_frames and isinstance(anim_frames, list) and len(anim_frames) == 4:
                self.food_anims[pet_index] = anim_frames
            else:
                # Fallback: use the icon itself as all frames
                self.food_anims[pet_index] = [icon] * 4

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draws background, menu, pets, poops, clock, and cleaning animation if active.
        Optimized to minimize unnecessary drawing and logic.
        """
        self.background.draw(surface)
        self.menu.draw(surface)

        # Draw pets and their overlays
        pets = game_globals.pet_list
        selected_pets = set(runtime_globals.selected_pets) if runtime_globals.selected_pets else set()
        show_hearts = runtime_globals.show_hearts

        for i, pet in enumerate(pets):
            self.draw_pet(surface, pet, i, selected_pets, show_hearts)

        # Draw clock only if enabled
        if game_globals.showClock:
            self.clock.draw(surface)

        # Draw poops only if present
        if game_globals.poop_list:
            for poop in game_globals.poop_list:
                poop.draw(surface)

        # Draw cleaning animation only if active
        if self.cleaning:
            self.draw_cleaning(surface)

        # Draw fade overlay and evolved pets only if fading
        if self.lock_inputs and self.fade_alpha > 0:
            self.draw_fade_overlay(surface)
            for i, pet in enumerate(pets):
                self.draw_pet_evolved(surface, pet, i)

        # Draw food animation for eating pets
        self.draw_food_anims(surface)

        # Draw game messages last
        runtime_globals.game_message.draw(surface)

    def draw_pet(self, surface: pygame.Surface, pet, index: int, selected_pets: set, show_hearts: bool) -> None:
        """
        Draws a single pet with selection/outline indicators.
        """
        pet.draw(surface)

        frame_enum = pet.animation_frames[pet.frame_index]
        frame = runtime_globals.pet_sprites[pet][frame_enum.value]

        if pet.direction == 1:
            frame = pygame.transform.flip(frame, True, False)

        if pet in selected_pets:
            draw_pet_outline(surface, frame, pet.x, pet.y, color=FONT_COLOR_BLUE)  # blue outline
        if self.selection_mode == "pet" and index == self.pet_selection_index:
            draw_pet_outline(surface, frame, pet.x, pet.y, color=FONT_COLOR_YELLOW)  # yellow highlight

        if show_hearts:
            self.draw_hearts(surface, pet.x + (PET_WIDTH // 4), pet.y + PET_HEIGHT, pet.hunger)
            self.draw_hearts(surface, pet.x + (PET_WIDTH // 4), pet.y + PET_HEIGHT + (6 * UI_SCALE), pet.strength)

    def draw_cleaning(self, surface: pygame.Surface) -> None:
        """
        Draws the cleaning animation.
        """
        wash_sprite = runtime_globals.misc_sprites.get("Wash")
        if wash_sprite:
            pet_x = (24 * UI_SCALE) + (SCREEN_HEIGHT - PET_HEIGHT) // 2
            surface.blit(wash_sprite, (self.cleaning_x, pet_x - (wash_sprite.get_height() - PET_HEIGHT)))

    def draw_fade_overlay(self, surface: pygame.Surface) -> None:
        """
        Draws the fade overlay, caching the surface for efficiency.
        """
        if not self._fade_overlay_cache or self._fade_overlay_cache.get_alpha() != self.fade_alpha:
            fade_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fade_overlay.fill((0, 0, 0))
            fade_overlay.set_alpha(self.fade_alpha)
            self._fade_overlay_cache = fade_overlay
        surface.blit(self._fade_overlay_cache, (0, 0))

    def draw_food_anims(self, surface: pygame.Surface) -> None:
        """
        Draws food animations for eating pets.
        """
        game_pet_eating = getattr(runtime_globals, "game_pet_eating", None)
        if game_pet_eating:
            for idx, pet in enumerate(game_globals.pet_list):
                if idx in game_pet_eating and pet.state == "eat":
                    anim_frames = self.food_anims.get(idx)
                    if anim_frames:
                        frame_duration = FRAME_RATE
                        total_frames = 4
                        total_anim_time = frame_duration * total_frames
                        # Clamp frame_idx to last frame if animation_counter exceeds total_anim_time
                        if pet.animation_counter >= total_anim_time:
                            frame_idx = total_frames - 1
                        else:
                            frame_idx = (pet.animation_counter // frame_duration) % total_frames
                        food_sprite = anim_frames[frame_idx]
                        x = pet.x + PET_WIDTH
                        y = pet.y + (PET_HEIGHT // 4) - (food_sprite.get_height() // 2)
                        surface.blit(food_sprite, (x, y))
                elif idx in self.food_anims:
                    # Clean up if pet is no longer eating
                    game_pet_eating.pop(idx, None)
                    self.food_anims.pop(idx, None)

    def draw_hearts(self, surface: pygame.Surface, x: int, y: int, value: int, factor: int = 1) -> None:
        """
        Draws heart icons to represent hunger, strength or effort.
        Uses a cache to avoid redrawing every frame.
        """
        cache_key = (x, y, value, factor)
        now = time.time()
        cache_entry = self._hearts_cache.get(cache_key)

        # Refresh cache if older than 1 second or not present
        if not cache_entry or now - cache_entry[1] > 1:
            total_hearts = 4
            heart_surface = pygame.Surface((total_hearts * HEARTS_SIZE, HEARTS_SIZE), pygame.SRCALPHA)
            for i in range(total_hearts):
                heart_x = i * HEARTS_SIZE
                if value >= (i + 1) * factor:
                    heart_sprite = self.sprites["heart_full"]
                elif value >= i * factor + (factor / 2):
                    heart_sprite = self.sprites["heart_half"]
                else:
                    heart_sprite = self.sprites["heart_empty"]
                heart_surface.blit(heart_sprite, (heart_x, 0))
            self._hearts_cache[cache_key] = (heart_surface, now)
        else:
            heart_surface = cache_entry[0]

        #surface.blit(heart_surface, (x, y))
        blit_with_cache(surface, heart_surface, (x, y))

    def handle_event(self, input_action) -> None:
        """
        Handles keyboard and GPIO button inputs in the main game scene.
        """
        if input_action:
            self.fade_out_timer = 60 * FRAME_RATE  # Reset on any input

        if self.lock_inputs:
            return

        if not all_pets_hatched():
            #runtime_globals.main_menu_index = -1
            if input_action == "Y" or input_action == "SHAKE":
                for pet in game_globals.pet_list:
                    pet.shake_counter += 1
            #return
            
        if input_action == "B":
            for pet in game_globals.pet_list:
                pet.death_save_counter += 1

        if input_action == "SELECT":
            self.selection_mode = "pet" if self.selection_mode == "menu" else "menu"
            runtime_globals.game_sound.play("menu")
            runtime_globals.game_console.log(f"[SceneMainGame] Switched selection mode to {self.selection_mode}")
            return

        self.handle_debug_keys(input_action)

        if self.selection_mode == "menu":
            self.handle_navigation_keys(input_action)
            self.handle_action_keys(input_action)
        elif self.selection_mode == "pet":
            self.handle_pet_selection_keys(input_action)

    def handle_debug_keys(self, input_action) -> None:
        """
        Debugging shortcuts (F1-F12).
        """
        #if platform.system() == "Linux" and "raspberrypi" in platform.uname().nodename:
        #    return
    
        if input_action == "F1":
            for pet in get_selected_pets():
                pet.timer += FRAME_RATE * 60 * 60
                pet.age_timer += FRAME_RATE * 60 * 60
                runtime_globals.game_console.log(f"[DEBUG] {pet.name} age {(pet.timer // 30) // 60}/{(pet.age_timer // 30) // 60}")
        elif input_action == "F2":
            for pet in get_selected_pets():
                pet.sick += 1
                pet.injuries += 1
                runtime_globals.game_console.log(f"[DEBUG] {pet.name} forced to get sick")
        elif input_action == "F3":
            for pet in get_selected_pets():
                pet.set_state("nap")
                runtime_globals.game_console.log(f"[DEBUG] {pet.name} forced to nap")
        elif input_action == "F4":
            for pet in get_selected_pets():
                pet.force_poop()
                runtime_globals.game_console.log(f"[DEBUG] {pet.name} forced to poop")
        elif input_action == "F5":
            for pet in get_selected_pets():
                if get_module(pet.module).use_condition_hearts:
                    if pet.condition_hearts > 0:
                        pet.condition_hearts -= 1
                        runtime_globals.game_console.log(f"[DEBUG] {pet.name} lost a condition heart, current: {pet.condition_hearts}")
                else:
                    pet.mistakes += 1
                    runtime_globals.game_console.log(f"[DEBUG] {pet.name} got a care mistake , current: {pet.mistakes}")
        elif input_action == "F6":
            for pet in get_selected_pets():
                pet.dp = pet.energy
            #runtime_globals.evolution_pet = get_selected_pets()[0]
            return
            if len(game_globals.pet_list) > 1:
                runtime_globals.game_sound.play("evolution_plus")
                evo = GameEvolutionEntity(
                    from_name = "MetalGreymon",
                    from_attribute = "Da",
                    from_sprite = runtime_globals.pet_sprites[game_globals.pet_list[0]][0],
                    to_attribute = "Vi",
                    to_name = "WarGreymon",
                    to_sprite = runtime_globals.pet_sprites[game_globals.pet_list[1]][0],
                    stage = 5)
                
                runtime_globals.evolution_data = [evo]
                change_scene("evolution")
        elif input_action == "F7":
            for pet in get_selected_pets():
                pet.battles += 1
                pet.totalBattles += 1
                pet.win += 1
                pet.totalWin += 1
                runtime_globals.game_console.log(f"[DEBUG] {pet.battles} battle counter")

        elif input_action == "F8":
            for pet in get_selected_pets():
                pet.effort += 1
                runtime_globals.game_console.log(f"[DEBUG] {pet.effort} strength up")
        elif input_action == "F9":
            for pet in get_selected_pets():
                pet.level += 1
                runtime_globals.game_console.log(f"[DEBUG] {pet.level} level up")
        elif input_action == "F10":
            for pet in get_selected_pets():
                pet.enemy_kills[5] += 1
                runtime_globals.game_console.log(f"[DEBUG] {pet.enemy_kills[5]} stage 5 kills")
        elif input_action == "F11":
            for pet in get_selected_pets():
                pet.overfeed += 1
                runtime_globals.game_console.log(f"[DEBUG] {pet.name} overfeed counter: {pet.overfeed}")
        elif input_action == "F12":
            for pet in get_selected_pets():
                pet.sleep_disturbances += 1
                runtime_globals.game_console.log(f"[DEBUG] {pet.name} sleep_disturbances counter: {pet.sleep_disturbances}")

    def handle_navigation_keys(self, input_action) -> None:
        """Handles cyclic LEFT, RIGHT, UP, DOWN for menu navigation."""
        rows, cols = 2, 4  # 🔹 Menu layout (2 rows × 4 columns)
        max_index = rows * cols - 1  # 🔹 Maximum valid index (7)
        if runtime_globals.main_menu_index < 0 and input_action in ["LEFT","RIGHT","UP","DOWN"]:
            runtime_globals.game_sound.play("menu")
            runtime_globals.main_menu_index = 0
        elif input_action == "LEFT":
            runtime_globals.game_sound.play("menu")
            if runtime_globals.main_menu_index in [0, 4, -1]:  
                runtime_globals.main_menu_index = runtime_globals.main_menu_index + 3
            else:
                runtime_globals.main_menu_index -= 1

        elif input_action == "RIGHT":
            runtime_globals.game_sound.play("menu")
            if runtime_globals.main_menu_index in [3, 7, -1]:  
                runtime_globals.main_menu_index = runtime_globals.main_menu_index - 3
            else:
                runtime_globals.main_menu_index += 1

        elif input_action == "UP":
            runtime_globals.game_sound.play("menu")
            if runtime_globals.main_menu_index in range(0, cols) or runtime_globals.main_menu_index == -1:
                runtime_globals.main_menu_index += 4  # 🔹 Wrap from top to bottom
            else:
                runtime_globals.main_menu_index -= 4

        elif input_action == "DOWN":
            runtime_globals.game_sound.play("menu")
            if runtime_globals.main_menu_index in range(4, max_index + 1) or runtime_globals.main_menu_index == -1:
                runtime_globals.main_menu_index -= 4  # 🔹 Wrap from bottom to top
            else:
                runtime_globals.main_menu_index += 4

        # 🔹 Handle `-1` case correctly
        if runtime_globals.main_menu_index == 7:
            runtime_globals.main_menu_index = -1  

        if runtime_globals.main_menu_index != -1:
            runtime_globals.main_menu_index %= (max_index + 1)  # 🔥 Ensure cyclic behavior

    def handle_action_keys(self, input_action) -> None:
        """
        Handles Enter, Escape, and equivalent GPIO button actions for menu selection.
        """
        index = runtime_globals.main_menu_index

        if input_action == "A":
            if index == 0:
                runtime_globals.game_sound.play("menu")
                self.start_scene("status")
            elif index == 1:
                runtime_globals.game_sound.play("menu")
                self.start_scene("feeding")
            elif index == 2:
                self.start_training()
            elif index == 3:
                self.start_battle()
            elif index == 4:
                self.start_cleaning()
            elif index == 5:
                self.start_scene("sleepmenu")
            elif index == 6:
                self.heal_sick_pets()

        elif input_action == "START" or input_action == "B":  # Maps to ESC (PC) & "START" button (Pi)
            runtime_globals.game_sound.play("cancel")
            self.start_scene("settings")

        elif input_action == "L":  # Rotate screen upside-down
            runtime_globals.game_sound.play("menu")
            game_globals.rotated = True

        elif input_action == "R":
            runtime_globals.game_sound.play("menu")
            distribute_pets_evenly()

        elif input_action == "X":
            runtime_globals.game_sound.play("menu")
            runtime_globals.show_hearts = not runtime_globals.show_hearts


    def start_scene(self, scene_name: str) -> None:
        """
        Helper to start a new scene.
        """
        runtime_globals.game_state = scene_name
        runtime_globals.game_state_update = True
        runtime_globals.game_console.log(f"[SceneMainGame] Switched to {scene_name}")

    def handle_pet_selection_keys(self, input_action) -> None:
        total_pets = len(game_globals.pet_list)

        if input_action == "LEFT":
            self.pet_selection_index = (self.pet_selection_index - 1) % total_pets
            runtime_globals.game_sound.play("menu")

        elif input_action == "RIGHT":
            self.pet_selection_index = (self.pet_selection_index + 1) % total_pets
            runtime_globals.game_sound.play("menu")

        elif input_action == "A":
            self.toggle_pet_selection(self.pet_selection_index)
            runtime_globals.game_sound.play("menu")


    def toggle_pet_selection(self, pet_index: int) -> None:
        """
        Toggles pet selection on Enter press.
        """
        pet = game_globals.pet_list[pet_index]
        if pet in runtime_globals.selected_pets:
            runtime_globals.selected_pets.remove(pet)
            runtime_globals.game_console.log(f"[SceneMainGame] Deselected {pet.name}")
        else:
            runtime_globals.selected_pets.append(pet)
            runtime_globals.game_console.log(f"[SceneMainGame] Selected {pet.name}")

    def start_training(self) -> None:
        """
        Checks if training is possible and starts it.
        """
        can_train = any(pet.can_train() for pet in get_selected_pets())
        if can_train:
            runtime_globals.game_sound.play("menu")
            self.start_scene("training")
        else:
            runtime_globals.game_sound.play("cancel")
            runtime_globals.game_console.log("[SceneMainGame] Cannot start training: no eligible pets.")

    def start_battle(self) -> None:
        """
        Checks if battle is possible and starts it.
        """
        can_train = any(pet.can_battle() for pet in get_selected_pets())
        if can_train:
            runtime_globals.game_sound.play("menu")
            self.start_scene("battle")
        else:
            runtime_globals.game_sound.play("cancel")
            runtime_globals.game_console.log("[SceneMainGame] Cannot start battle: no eligible pets.")

    def start_cleaning(self) -> None:
        """
        Starts the screen cleaning action if there are poops.
        """
        if not game_globals.poop_list:
            runtime_globals.game_sound.play("cancel")
            return
        runtime_globals.game_sound.play("menu")
        self.cleaning = True
        self.cleaning_x = SCREEN_WIDTH

    def heal_sick_pets(self) -> None:
        """
        Heals sick pets by 1 sickness point, playing angry animation.
        """
        sick_pets = [pet for pet in game_globals.pet_list if pet.sick > 0]

        if not sick_pets:
            runtime_globals.game_sound.play("cancel")
            runtime_globals.game_console.log("[SceneMainGame] No sick pets to heal.")
            return

        runtime_globals.game_sound.play("fail")
        distribute_pets_evenly()

        for pet in sick_pets:
            pet.sick = max(0, pet.sick - 1)
            pet.set_state("angry")
            runtime_globals.game_console.log(f"[SceneMainGame] {pet.name} healed. Remaining sickness: {pet.sick}")
