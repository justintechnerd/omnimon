#=====================================================================
# DummyTraining (Simple Strength Bar Training)
#=====================================================================

import random
import pygame

from core import runtime_globals
from core.animation import PetFrame
from core.combat.training import Training
from core.constants import *
from core.utils import blit_with_shadow, get_training_targets, sprite_load
from scenes.scene_battle import ATTACK_SPEED, BAR_HOLD_TIME_MS

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

        self.bag1 = sprite_load(selected_sprites[0], size=(60, 120))
        self.bag2 = sprite_load(selected_sprites[1], size=(60, 120))

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
                x -= ATTACK_SPEED
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
            bag_x = 50
            for sprite, (x, y) in self.attack_positions:
                x -= ATTACK_SPEED

                if x <= bag_x + 48:
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
        bar_x = (SCREEN_WIDTH // 2 - self.bar_piece.get_width() // 2) - 40
        bar_bottom_y = SCREEN_HEIGHT // 2 + 110

        if self.strength == 14:
            surface.blit(self.training_max, (bar_x - 18, bar_bottom_y - 209))
        
        blit_with_shadow(surface, self.bar_back, (bar_x - 3, bar_bottom_y - 169))

        for i in range(self.strength):
            y = bar_bottom_y - (i + 1) * self.bar_piece.get_height()
            blit_with_shadow(surface, self.bar_piece, (bar_x, y))

        self.draw_pets(surface, PetFrame.IDLE1)

    def draw_attack_move(self, surface):
        if self.attack_phase == 1:
            self.draw_pets(surface, PetFrame.ATK1)
        else:
            blit_with_shadow(surface, self.bag1, (50, SCREEN_HEIGHT // 2 - self.bag1.get_height() // 2))

        for sprite, (x, y) in self.attack_positions:
            blit_with_shadow(surface, sprite, (x, y))

    def draw_result(self, surface):
        result_img = None
        if 10 <= self.strength < 14:
            result_img = self.bag2
        elif self.strength < 10:
            result_img = self.bag1

        if self.frame_counter < 30:
            if result_img:
                x = 50
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
        spacing = min(spacing, OPTION_ICON_SIZE + 20)
        start_y = ((SCREEN_HEIGHT - (spacing * total_pets)) // 2)

        for i, pet in enumerate(targets):
            print(f"Pet {i}: atk_main = {pet.atk_main}")
            atk_sprite = self.attack_sprites.get(str(pet.atk_main))
            if atk_sprite:
                for j in range(attack_count):
                    #offset_y = j * 15  # slight spread if multiple shots
                    x = SCREEN_WIDTH - OPTION_ICON_SIZE - 70
                    y = start_y + i * spacing
                    if j == 1:
                        x -= 20
                        y -= 10
                    elif j == 2:
                        x -= 40
                        y += 10
                    self.attack_positions.append((atk_sprite, (x, y)))

    def get_attack_count(self):
        if self.strength < 10:
            return 1
        elif self.strength < 14:
            return 2
        else:
            return 3