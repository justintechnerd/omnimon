#=====================================================================
# HeadToHeadTraining (Reaction Timing and Coordination)
#=====================================================================

import os
import random

import pygame

from core import runtime_globals
from core.animation import PetFrame
from core.combat.training import Training
from core.constants import *
from core.utils.pet_utils import get_training_targets
from core.utils.pygame_utils import blit_with_shadow, get_font, sprite_load_percent
from core.utils.scene_utils import change_scene

class HeadToHeadTraining(Training):
    """
    Head-to-Head training mode where two pets face off based on player's timing.
    """

    PATTERNS = [
        "ABABB", "BBAAB", "BAABB",
        "ABBAA", "BABAB", "ABABA"
    ]

    ATTACK_SPEED = int((3* UI_SCALE) * (SCREEN_WIDTH / (PET_WIDTH*3)))
    ATTACK_OFFSET_Y = int(48 * UI_SCALE)

    def __init__(self) -> None:
        super().__init__()

        self.left_pet = None
        self.right_pet = None
        self.pattern = ""
        self.current_index = 0

        self.victories = 0
        self.failures = 0
        self.player_input = None

        self.is_collision = False

        # Use sprite_load_percent for all images, scale appropriately
        self.head_training_img = sprite_load_percent(HEADTRAINING_PATH, percent=60, keep_proportion=True, base_on="width")
        self.vs_img = sprite_load_percent(VS_PATH, percent=17, keep_proportion=True, base_on="width")
        
        self.strikes = sprite_load_percent(STRIKE_PATH, percent=7, keep_proportion=True, base_on="width")
        self.strikes_back = sprite_load_percent(STRIKES_BACK_PATH, percent=40, keep_proportion=True, base_on="width")

        self.select_pets()
        self.select_pattern()

    def select_pets(self):
        """Select two random pets eligible for training."""
        candidates = get_training_targets()
        if len(candidates) >= 2:
            self.left_pet, self.right_pet = random.sample(candidates, 2)

    def select_pattern(self):
        """Selects a cyclic pattern based on previous training."""
        runtime_globals.last_headtohead_pattern = random.randint(0, 5)
        runtime_globals.last_headtohead_pattern = (runtime_globals.last_headtohead_pattern + 1) % 6

        self.pattern = self.PATTERNS[runtime_globals.last_headtohead_pattern]
        self.current_index = 0

    def draw(self, surface: pygame.Surface):
        if not (self.left_pet and self.right_pet):
            return

        if self.phase != "result":
            starting_x = SCREEN_WIDTH - self.strikes_back.get_width() - int(5 * UI_SCALE)
            starting_y = SCREEN_HEIGHT - self.strikes_back.get_height() - int(5 * UI_SCALE)
            blit_with_shadow(surface, self.strikes_back, (starting_x, starting_y))

            for i in range(5 - self.current_index):
                x = starting_x + 7 + (4 - i) * self.strikes.get_width()
                y = starting_y + (6 * UI_SCALE)
                blit_with_shadow(surface, self.strikes, (x, y))

            self.draw_pets(surface)
            if self.phase == "attack_move":
                self.draw_attacks(surface)
            elif self.phase == "alert":
                self.draw_alert(surface)
        else:
            self.draw_result(surface)

    def draw_pets(self, surface):
        """Draw pets in idle or attacking poses."""
        left_frame = PetFrame.ATK2.value if self.phase == "attack_move" else PetFrame.ATK1.value
        right_frame = PetFrame.ATK2.value if self.phase == "attack_move" else PetFrame.ATK1.value

        left_sprite = runtime_globals.pet_sprites[self.left_pet][left_frame]
        right_sprite = runtime_globals.pet_sprites[self.right_pet][right_frame]

        left_sprite = pygame.transform.flip(left_sprite, True, False)

        blit_with_shadow(surface, left_sprite, (0 + (5*UI_SCALE), SCREEN_HEIGHT // 2 - int(PET_HEIGHT) // 2))
        blit_with_shadow(surface, right_sprite, (SCREEN_WIDTH - PET_WIDTH - (5*UI_SCALE), SCREEN_HEIGHT // 2 - int(PET_HEIGHT) // 2))

    def draw_attacks(self, surface):
        """Draw attack projectiles."""
        for sprite, (x, y) in self.attack_positions:
            blit_with_shadow(surface, sprite, (int(x), int(y)))

    def draw_result(self, surface):
        """Draw final result after all attack phases."""
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2

        blit_with_shadow(
            surface,
            self.head_training_img,
            (center_x - self.head_training_img.get_width() // 2, center_y - self.head_training_img.get_height() - int(20 * UI_SCALE))
        )

        font = get_font(int(55 * UI_SCALE))
        wins_text = font.render(str(self.victories), True, FONT_COLOR_DEFAULT)
        losses_text = font.render(str(self.failures), True, FONT_COLOR_DEFAULT)

        total_width = wins_text.get_width() + self.vs_img.get_width() + losses_text.get_width() + int(20 * UI_SCALE)
        start_x = center_x - total_width // 2
        y = center_y + int(20 * UI_SCALE)

        blit_with_shadow(surface, wins_text, (start_x, y))
        blit_with_shadow(surface, self.vs_img, (start_x + wins_text.get_width() + int(10 * UI_SCALE), y))
        blit_with_shadow(surface, losses_text, (start_x + wins_text.get_width() + self.vs_img.get_width() + int(20 * UI_SCALE), y))

    def move_attacks(self):
        """Move attacks according to collision type, frame-rate independent."""
        finished = False

        if self.is_collision:
            finished = self.update_collision()
        else:
            finished = self.update_cross_attack()

        if finished:
            self.process_attack_result()

    def update_collision(self):
        """Update attacks for a collision (meet in center), frame-rate independent."""
        for atk in self.attack_positions:
            sprite, (x, y) = atk
            if x < SCREEN_WIDTH // 2 - int(12 * UI_SCALE):
                x += self.ATTACK_SPEED * (30 / FRAME_RATE)
            elif x > SCREEN_WIDTH // 2 - int(12 * UI_SCALE):
                x -= self.ATTACK_SPEED * (30 / FRAME_RATE)
            atk[1] = (x, y)

        left_x, _ = self.attack_positions[0][1]
        right_x, _ = self.attack_positions[1][1]
        return (
            abs(left_x - (SCREEN_WIDTH // 2 - int(12 * UI_SCALE))) <= int(10 * UI_SCALE)
            and abs(right_x - (SCREEN_WIDTH // 2 - int(12 * UI_SCALE))) <= int(10 * UI_SCALE)
        )

    def update_cross_attack(self):
        """Update attacks for cross fire (no collision), frame-rate independent."""
        self.attack_positions[0][1] = (
            self.attack_positions[0][1][0] + self.ATTACK_SPEED * (30 / FRAME_RATE),
            self.attack_positions[0][1][1]
        )
        self.attack_positions[1][1] = (
            self.attack_positions[1][1][0] - self.ATTACK_SPEED * (30 / FRAME_RATE),
            self.attack_positions[1][1][1]
        )

        return (
            self.attack_positions[0][1][0] >= SCREEN_WIDTH - PET_WIDTH - (5 * UI_SCALE)
            or self.attack_positions[1][1][0] <= PET_WIDTH + (5 * UI_SCALE)
        )

    def handle_event(self, input_action):
        if self.phase == "charge" and input_action:
            if input_action == "UP":  # Select Attack B
                self.player_input = "B"
                self.start_attack()
            elif input_action == "DOWN":  # Select Attack A
                self.player_input = "A"
                self.start_attack()
            elif input_action == "START" or input_action == "B":
                runtime_globals.game_sound.play("cancel")
                change_scene("game")
        elif input_action in ["A","B"]:
            runtime_globals.game_sound.play("cancel")
            change_scene("game")

    def start_attack(self):
        """Begin the attack phase after a key press."""
        self.phase = "attack_move"
        self.attack_positions.clear()

        left_dir = self.pattern[self.current_index]
        right_dir = self.player_input

        left_sprite = self.attack_sprites.get(str(self.left_pet.atk_main))
        left_sprite = pygame.transform.flip(left_sprite, True, False)
        right_sprite = self.attack_sprites.get(str(self.right_pet.atk_main))
        
        y_base = SCREEN_HEIGHT // 2 - PET_HEIGHT // 2
        y_up = y_base
        y_down = y_base + self.ATTACK_OFFSET_Y

        left_x = PET_WIDTH + (5*UI_SCALE)
        right_x = SCREEN_WIDTH - PET_WIDTH - (5*UI_SCALE)

        self.attack_positions.append([left_sprite, (left_x, y_up if left_dir == "A" else y_down)])
        self.attack_positions.append([right_sprite, (right_x, y_up if right_dir == "A" else y_down)])

        self.is_collision = (left_dir == right_dir)

    def process_attack_result(self):
        """Process the result of a single attack encounter."""
        correct = self.pattern[self.current_index] != self.player_input

        if correct:
            runtime_globals.game_sound.play("attack_hit")
            self.victories += 1
        else:
            runtime_globals.game_sound.play("attack_fail")
            self.failures += 1

        self.current_index += 1

        if self.current_index >= len(self.pattern):
            self.phase = "result"
            self.frame_counter = 0
            runtime_globals.game_console.log(f"Head-to-Head training done: {self.victories} wins, {self.failures} fails")
        else:
            self.phase = "charge"
            self.attack_positions.clear()

    def check_victory(self):
        """Apply training results and return to game."""
        return self.victories > self.failures
