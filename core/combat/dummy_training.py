#=====================================================================
# DummyTraining (Simple Strength Bar Training)
#=====================================================================

import random
import pygame

from core import runtime_globals
from core.animation import PetFrame
from core.combat.combat_constants import ATTACK_SPEED, BAR_HOLD_TIME_MS
from core.combat.training import Training
from core.constants import *
from core.game_module import sprite_load
from core.utils.pet_utils import get_training_targets
from core.utils.pygame_utils import blit_with_shadow

class DummyTraining(Training):
    """
    Dummy training mode where players build up strength by holding a bar.
    """

    def __init__(self) -> None:
        super().__init__()
        self.strength = 0
        self.bar_level = 14
        self.bar_timer = 0

        self.attack_phase = 1
        self.flash_frame = 0

        SPRITE_SETS = [
            (BAG1_PATH, BAG2_PATH),
            (ROCK1_PATH, ROCK2_PATH),
            (TREE1_PATH, TREE2_PATH),
            (BRICK1_PATH, BRICK2_PATH),
        ]

        selected_sprites = random.choice(SPRITE_SETS)

        self.bag1 = sprite_load(selected_sprites[0], size=(60 * UI_SCALE, 120 * UI_SCALE))
        self.bag2 = sprite_load(selected_sprites[1], size=(60 * UI_SCALE, 120 * UI_SCALE))

    def update_charge_phase(self):
        if pygame.time.get_ticks() - self.bar_timer > BAR_HOLD_TIME_MS:
            self.phase = "wait_attack"
            self.frame_counter = 0
            self.prepare_attacks()

    def move_attacks(self):
        """Handles the attack movement towards the bag."""
        finished = False
        new_positions = []

        if self.attack_phase == 1:
            for sprite, (x, y) in self.attack_positions:
                x -= ATTACK_SPEED * (30 / FRAME_RATE)  # Frame-rate independent speed
                if x <= 0:
                    finished = True
                new_positions.append((sprite, (x, y)))

            if finished:
                new_positions = []
                self.attack_phase = 2
                for sprite, (x, y) in self.attack_positions:
                    x += SCREEN_WIDTH
                    new_positions.append((sprite, (x, y)))

            self.attack_positions = new_positions

        elif self.attack_phase == 2:
            bag_x = 50 * UI_SCALE
            for sprite, (x, y) in self.attack_positions:
                x -= ATTACK_SPEED * (30 / FRAME_RATE)  # Frame-rate independent speed

                if x <= bag_x + (48 * UI_SCALE):
                    finished = True
                new_positions.append((sprite, (x, y)))

            if finished:
                runtime_globals.game_sound.play("attack_hit")
                self.phase = "impact"
                self.flash_frame = 0

            self.attack_positions = new_positions

    def check_victory(self):
        """Apply training results and return to game."""
        return self.strength > 10

    def draw_charge(self, surface):
        bar_x = (SCREEN_WIDTH // 2 - self.bar_piece.get_width() // 2) - int(40 * UI_SCALE)
        bar_bottom_y = SCREEN_HEIGHT // 2 + int(110 * UI_SCALE)

        if self.strength == 14:
            surface.blit(self.training_max, (bar_x - int(18 * UI_SCALE), bar_bottom_y - int(209 * UI_SCALE)))
        
        blit_with_shadow(surface, self.bar_back, (bar_x - int(3 * UI_SCALE), bar_bottom_y - int(169 * UI_SCALE)))

        for i in range(self.strength):
            y = bar_bottom_y - (i + 1) * self.bar_piece.get_height()
            blit_with_shadow(surface, self.bar_piece, (bar_x, y))

        self.draw_pets(surface, PetFrame.IDLE1)

    def draw_attack_move(self, surface):
        if self.attack_phase == 1:
            if self.frame_counter < int(10 * (FRAME_RATE / 30)):
                self.draw_pets(surface, PetFrame.ATK2)
            else:
                self.draw_pets(surface, PetFrame.ATK1)
        else:
            blit_with_shadow(surface, self.bag1, (int(50 * UI_SCALE), SCREEN_HEIGHT // 2 - self.bag1.get_height() // 2))

        for sprite, (x, y) in self.attack_positions:
            blit_with_shadow(surface, sprite, (int(x), int(y)))

    def draw_result(self, surface):
        result_img = None
        if 10 <= self.strength < 14:
            result_img = self.bag2
        elif self.strength < 10:
            result_img = self.bag1

        if self.frame_counter < 30:
            if result_img:
                x = int(50 * UI_SCALE)
                y = SCREEN_HEIGHT // 2 - result_img.get_height() // 2
                blit_with_shadow(surface, result_img, (x, y))
        else:
            y = SCREEN_HEIGHT // 2 - self.bad_sprite.get_height() // 2
            if self.strength < 10:
                blit_with_shadow(surface, self.bad_sprite, (0, y))
            elif self.strength < 14:
                blit_with_shadow(surface, self.great_sprite, (0, y))
            elif self.strength >= 14:
                blit_with_shadow(surface, self.excellent_sprite, (0, y))

    def prepare_attacks(self):
        """Prepare multiple attacks from each pet based on strength level."""
        attack_count = self.get_attack_count()
        targets = get_training_targets()
        total_pets = len(targets)
        if total_pets == 0:
            return

        available_height = SCREEN_HEIGHT
        spacing = available_height // total_pets
        spacing = min(spacing, OPTION_ICON_SIZE + int(20 * UI_SCALE))
        start_y = ((SCREEN_HEIGHT - (spacing * total_pets)) // 2)

        for i, pet in enumerate(targets):
            atk_sprite = self.attack_sprites.get(str(pet.atk_main))
            if atk_sprite:
                for j in range(attack_count):
                    x = SCREEN_WIDTH - OPTION_ICON_SIZE - int(70 * UI_SCALE)
                    y = start_y + i * spacing
                    if j == 1:
                        x -= int(20 * UI_SCALE)
                        y -= int(10 * UI_SCALE)
                    elif j == 2:
                        x -= int(40 * UI_SCALE)
                        y += int(10 * UI_SCALE)
                    self.attack_positions.append((atk_sprite, (x, y)))

    def get_attack_count(self):
        if self.strength < 10:
            return 1
        elif self.strength < 14:
            return 2
        else:
            return 3