import pygame
import time
import random

from core import runtime_globals
from core.animation import PetFrame
from core.combat.combat_constants import ATTACK_SPEED
from core.combat.training import Training
from core.constants import *
from core.utils.pet_utils import get_training_targets
from core.utils.pygame_utils import blit_with_shadow, sprite_load_percent
from core.utils.scene_utils import change_scene

class CountMatchTraining(Training):
    def __init__(self):
        super().__init__()

        self.press_counter = 0
        self.rotation_index = 0
        self.start_time = 0
        self.final_color = 3
        self.correct_color = 0
        self.super_hits = {}

        self.result_text = None
        self.flash_frame = 0
        self.anim_counter = -1

        self.load_sprites()

    def load_sprites(self):
        """Loads and scales sprites using predefined constants and sprite_load()."""
        self.ready_sprites = {key: sprite_load_percent(path, 100, keep_proportion=True, base_on="width") for key, path in READY_SPRITES_PATHS.items()}
        self.count_sprites = {key: sprite_load_percent(path, 100, keep_proportion=True, base_on="width") for key, path in COUNT_SPRITES_PATHS.items()}
        self.mega_hit = sprite_load_percent(MEGA_HIT_PATH, 100, keep_proportion=True, base_on="width")

    def update_charge_phase(self):
        if self.frame_counter == 1:
            self.start_count_phase()
        # Use frame-rate independent timing (3 seconds)
        if self.frame_counter > int(3 * FRAME_RATE):
            self.phase = "wait_attack"
            self.calculate_results()
            self.prepare_attack()

    def start_count_phase(self):
        self.phase = "charge"
        self.press_counter = 0
        self.rotation_index = 3

    def handle_event(self, input_action):
        if self.phase == "charge" and input_action == "Y" or input_action == "SHAKE": 
            if self.phase == "alert":
                self.phase = "charge"
            elif self.phase == "charge":
                self.press_counter += 1
                if self.press_counter % 2 == 0:
                    self.rotation_index -= 1
                    if self.rotation_index < 1:
                        self.rotation_index = 3
        elif self.phase in ["wait_attack","attack_move","impact","result"] and input_action in ["B","START"]:
            self.finish_training()
        elif self.phase in ("alert", "charge") and input_action in ["B","START"]:
            runtime_globals.game_sound.play("cancel")
            change_scene("game")


    def get_first_pet_attribute(self):
        pet = get_training_targets()[0]
        if pet.attribute in ["", "Va"]:
            return 1
        elif pet.attribute == "Da":
            return 2
        elif pet.attribute == "Vi":
            return 3
        return 1

    def calculate_results(self):
        self.correct_color = self.get_first_pet_attribute()
        self.final_color = self.rotation_index
        pets = get_training_targets()
        if not pets:
            return

        # Calculate hits for the first pet only
        pet = pets[0]
        shakes = self.press_counter
        attr_type = getattr(pet, "attribute", "")


        if shakes < 2:
            hits = 0
        else:
            # Color mapping: 1=Red, 2=Yellow, 3=Blue
            color = self.final_color
            if attr_type in ("", "Va"):
                if color == 1:      # Red
                    hits = 5
                elif color == 2:    # Yellow
                    hits = random.choice([3, 4])
                elif color == 3:    # Blue
                    hits = 2
                else:
                    hits = 1
            elif attr_type == "Da":
                if color == 2:      # Yellow
                    hits = 5
                elif color == 1:    # Red
                    hits = random.choice([3, 4])
                elif color == 3:    # Blue
                    hits = 2
                else:
                    hits = 1
            elif attr_type == "Vi":
                if color == 3:      # Blue
                    hits = 5
                elif color == 2:    # Yellow
                    hits = random.choice([3, 4])
                elif color == 1:    # Red
                    hits = 2
                else:
                    hits = 1
            else:
                hits = 1

        # Assign the same result to all pets
        for p in pets:
            self.super_hits[p] = hits

    def prepare_attack(self):
        self.attack_phase = 0
        self.attack_waves = [[] for _ in range(5)]
        pets = get_training_targets()
        total_pets = len(pets)

        available_height = SCREEN_HEIGHT
        spacing = available_height // total_pets
        spacing = min(spacing, OPTION_ICON_SIZE + (20 * UI_SCALE))
        start_y = (SCREEN_HEIGHT - (spacing * total_pets)) // 2

        for i, pet in enumerate(pets):
            sprite = self.attack_sprites.get(str(pet.atk_main))
            if not sprite:
                continue

            count = self.super_hits.get(pet, 0)

            if count == 5:
                pattern = [3] * 5
            else:
                pattern = [2] * count + [1] * (5 - count)

            pet_y = start_y + i * spacing + OPTION_ICON_SIZE // 2 - sprite.get_height() // 2
            for j, kind in enumerate(pattern):
                # Start to the right of the pet sprite (aligned horizontally)
                x = SCREEN_WIDTH - OPTION_ICON_SIZE - (20 * UI_SCALE)
                y = pet_y
                self.attack_waves[j].append((sprite, kind, x, y))
        
        self.frame_counter = 0

    def move_attacks(self):
        """Handles the attack movement towards the bag, all in one phase."""
        if self.current_wave_index >= len(self.attack_waves):
            self.phase = "result"
            self.frame_counter = 0
            return

        wave = self.attack_waves[self.current_wave_index]
        new_wave = []
        all_off_screen = True

        if self.frame_counter <= 1:
            runtime_globals.game_sound.play("attack")

        for sprite, kind, x, y in wave:
            x -= ATTACK_SPEED * (30 / FRAME_RATE)  # Frame-rate independent speed
            if x + (24 * UI_SCALE) > 0:
                all_off_screen = False
                new_wave.append((sprite, kind, x, y))

        self.attack_waves[self.current_wave_index] = new_wave

        # Wait at least 10 frames (at 30fps) before next wave
        if all_off_screen and self.frame_counter >= int(10 * (FRAME_RATE / 30)):
            self.current_wave_index += 1
            self.frame_counter = 0

    def draw_pets(self, surface, frame_enum=PetFrame.IDLE1):
        """
        Draws pets using appropriate frame based on attack animation phase.
        Animation runs for 20 frames before the attack appears (frame 48 at 30fps),
        and scales with frame rate and resolution.
        """
        if self.phase == "attack_move":
            frame_enum = self.animate_attack(46)

        super().draw_pets(surface, frame_enum)

    def draw_alert(self, surface):
        attr = self.get_first_pet_attribute()
        sprite = self.ready_sprites[attr]
        y = (SCREEN_HEIGHT - sprite.get_height()) // 2
        surface.blit(sprite, (0, y))

    def draw_charge(self, surface):
        sprite = self.count_sprites[4 if self.press_counter == 0 else self.rotation_index]
        y = (SCREEN_HEIGHT - sprite.get_height()) // 2
        surface.blit(sprite, (0, y))

    def draw_attack_move(self, surface):
        self.draw_pets(surface)
        for wave in self.attack_waves:
            for sprite, kind, x, y in wave:
                if x < SCREEN_WIDTH - (90 * UI_SCALE):
                    blit_with_shadow(surface, sprite, (x, y))
                    if kind > 1:
                        blit_with_shadow(surface, sprite, (x - (20 * UI_SCALE), y - (10 * UI_SCALE)))
                    if kind == 3:
                        blit_with_shadow(surface, sprite, (x - (40 * UI_SCALE), y + (10 * UI_SCALE)))


    def draw_result(self, screen):
        pets = get_training_targets()
        pet = pets[0]
        hits = self.super_hits.get(pet, 0)
        if hits == 5:
            sprite = self.mega_hit
            x = SCREEN_WIDTH // 2 - sprite.get_width() // 2
            y = SCREEN_HEIGHT // 2 - sprite.get_height() // 2
            blit_with_shadow(screen, sprite, (x, y))
        else:
            font = pygame.font.Font(None, FONT_SIZE_LARGE)
            text = font.render(f"{hits} Super-Hits", True, (255, 255, 255))
            x = SCREEN_WIDTH // 2 - text.get_width() // 2
            y = (100 * UI_SCALE)
            screen.blit(text, (x, y))

    def check_victory(self):
        """Apply training results and return to game."""
        return self.super_hits.get(get_training_targets()[0], 0) > 1
