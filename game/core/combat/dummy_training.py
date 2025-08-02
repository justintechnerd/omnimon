#=====================================================================
# DummyTraining (Simple Strength Bar Training)
#=====================================================================

import random
import pygame

from core import runtime_globals
from core.animation import PetFrame
from core.combat.training import Training
from game.core.combat import combat_constants
import game.core.constants as constants
from core.game_module import sprite_load
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
            (constants.BAG1_PATH, constants.BAG2_PATH),
            (constants.ROCK1_PATH, constants.ROCK2_PATH),
            (constants.TREE1_PATH, constants.TREE2_PATH),
            (constants.BRICK1_PATH, constants.BRICK2_PATH),
        ]

        selected_sprites = random.choice(SPRITE_SETS)

        self.bag1 = sprite_load(selected_sprites[0], size=(60 * constants.UI_SCALE, 120 * constants.UI_SCALE))
        self.bag2 = sprite_load(selected_sprites[1], size=(60 * constants.UI_SCALE, 120 * constants.UI_SCALE))

    def update_charge_phase(self):
        if pygame.time.get_ticks() - self.bar_timer > combat_constants.BAR_HOLD_TIME_MS:
            self.phase = "wait_attack"
            self.frame_counter = 0
            self.prepare_attacks()

    def move_attacks(self):
        """Handles the attack movement towards the bag."""
        finished = False
        new_positions = []

        if self.attack_phase == 1:
            for sprite, (x, y) in self.attack_positions:
                x -= combat_constants.ATTACK_SPEED * (30 / constants.FRAME_RATE)  # Frame-rate independent speed
                if x <= 0:
                    finished = True
                new_positions.append((sprite, (x, y)))

            if finished:
                new_positions = []
                self.attack_phase = 2
                for sprite, (x, y) in self.attack_positions:
                    x += constants.SCREEN_WIDTH
                    new_positions.append((sprite, (x, y)))

            self.attack_positions = new_positions

        elif self.attack_phase == 2:
            bag_x = 50 * constants.UI_SCALE
            for sprite, (x, y) in self.attack_positions:
                x -= combat_constants.ATTACK_SPEED * (30 / constants.FRAME_RATE)  # Frame-rate independent speed

                if x <= bag_x + (48 * constants.UI_SCALE):
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

    def check_and_award_trophies(self):
        """Award trophy if strength reaches maximum (14)"""
        if self.strength == 14:
            for pet in self.pets:
                pet.trophies += 1
            runtime_globals.game_console.log(f"[TROPHY] Dummy training perfect score achieved! Trophy awarded.")

    def draw_charge(self, surface):
        bar_piece = self._sprite_cache['bar_piece']
        training_max = self._sprite_cache['training_max']
        bar_back = self._sprite_cache['bar_back']

        bar_x = (constants.SCREEN_WIDTH // 2 - bar_piece.get_width() // 2) - int(40 * constants.UI_SCALE)
        bar_bottom_y = constants.SCREEN_HEIGHT // 2 + int(110 * constants.UI_SCALE)

        if self.strength == 14:
            surface.blit(training_max, (bar_x - int(18 * constants.UI_SCALE), bar_bottom_y - int(209 * constants.UI_SCALE)))
        
        blit_with_shadow(surface, bar_back, (bar_x - int(3 * constants.UI_SCALE), bar_bottom_y - int(169 * constants.UI_SCALE)))

        for i in range(self.strength):
            y = bar_bottom_y - (i + 1) * bar_piece.get_height()
            blit_with_shadow(surface, bar_piece, (bar_x, y))

        self.draw_pets(surface, PetFrame.IDLE1)

    def draw_attack_move(self, surface):
        if self.attack_phase == 1:
            if self.frame_counter < int(10 * (constants.FRAME_RATE / 30)):
                self.draw_pets(surface, PetFrame.ATK2)
            else:
                self.draw_pets(surface, PetFrame.ATK1)
        else:
            blit_with_shadow(surface, self.bag1, (int(50 * constants.UI_SCALE), constants.SCREEN_HEIGHT // 2 - self.bag1.get_height() // 2))

        for sprite, (x, y) in self.attack_positions:
            blit_with_shadow(surface, sprite, (int(x), int(y)))

    def draw_result(self, surface):
        # Use cached result sprites
        bad_sprite = self._sprite_cache['bad']
        great_sprite = self._sprite_cache['great']
        excellent_sprite = self._sprite_cache['excellent']

        result_img = None
        if 10 <= self.strength < 14:
            result_img = self.bag2
        elif self.strength < 10:
            result_img = self.bag1

        if self.frame_counter < 30:
            if result_img:
                x = int(50 * constants.UI_SCALE)
                y = constants.SCREEN_HEIGHT // 2 - result_img.get_height() // 2
                blit_with_shadow(surface, result_img, (x, y))
        else:
            y = constants.SCREEN_HEIGHT // 2 - bad_sprite.get_height() // 2
            if self.strength < 10:
                blit_with_shadow(surface, bad_sprite, (0, y))
            elif self.strength < 14:
                blit_with_shadow(surface, great_sprite, (0, y))
            elif self.strength >= 14:
                blit_with_shadow(surface, excellent_sprite, (0, y))
                # Draw trophy notification if maximum score achieved
                self.draw_trophy_notification(surface)

    def prepare_attacks(self):
        """Prepare multiple attacks from each pet based on strength level."""
        attack_count = self.get_attack_count()
        targets = self.pets
        total_pets = len(targets)
        if total_pets == 0:
            return

        available_height = constants.SCREEN_HEIGHT
        spacing = min(available_height // total_pets, int(48 * constants.UI_SCALE) + int(20 * constants.UI_SCALE))
        start_y = (constants.SCREEN_HEIGHT - (spacing * total_pets)) // 2

        for i, pet in enumerate(targets):
            atk_sprite = self.get_attack_sprite(pet, pet.atk_main)
            x = constants.SCREEN_WIDTH - int(48 * constants.UI_SCALE) - int(70 * constants.UI_SCALE)
            y = start_y + i * spacing

            if attack_count == 1:
                self.attack_positions.append((atk_sprite, (x, y)))
            elif attack_count == 2:
                self.attack_positions.append((atk_sprite, (x, y)))
                self.attack_positions.append((atk_sprite, (x + int(20 * constants.UI_SCALE), y + int(10 * constants.UI_SCALE))))
            elif attack_count == 3:
                scaled_sprite = pygame.transform.scale2x(atk_sprite)
                self.attack_positions.append((scaled_sprite, (x, y)))
                # Optionally, add more positions for extra visual feedback:
                #self.attack_positions.append((atk_sprite, (x + int(20 * constants.UI_SCALE), y + int(10 * constants.UI_SCALE))))
                #self.attack_positions.append((atk_sprite, (x - int(20 * constants.UI_SCALE), y - int(10 * constants.UI_SCALE))))

    def get_attack_count(self):
        """Returns the number of attacks based on strength."""
        if self.strength < 10:
            return 1
        elif self.strength < 14:
            return 2
        else:
            return 3