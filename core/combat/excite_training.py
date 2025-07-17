#=====================================================================
# ExciteTraining (Simple Strength Bar Training)
#=====================================================================

import pygame
from core import game_globals, runtime_globals
from core.animation import PetFrame
from core.combat.combat_constants import ATTACK_SPEED
from core.combat.training import Training
from core.constants import *
from components.window_xaibar import WindowXaiBar
from core.utils.pet_utils import get_training_targets
from core.utils.pygame_utils import blit_with_shadow
from core.utils.scene_utils import change_scene

class ExciteTraining(Training):
    """
    Excite training mode where players build up strength by holding a bar.
    """

    def __init__(self) -> None:
        super().__init__()

        self.xaibar = WindowXaiBar(10 * UI_SCALE, SCREEN_HEIGHT // 2 - (18 * UI_SCALE), game_globals.xai, get_training_targets()[0])
        self.xaibar.start()

    def update_charge_phase(self):
        self.xaibar.update()
        # End phase after a certain time or on input (like bar phase)
        if self.frame_counter > int(30 * 3 * (FRAME_RATE / 30)):
            self.xaibar.stop()
            runtime_globals.game_console.log(f"XaiBar phase ended strength {self.xaibar.selected_strength}.")
            self.phase = "wait_attack"
            self.frame_counter = 0
            self.prepare_attacks()

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

    def check_victory(self):
        """Apply training results and return to game."""
        return self.xaibar.selected_strength > 0

    def draw_charge(self, surface):
        self.xaibar.draw(surface)

        self.draw_pets(surface, PetFrame.IDLE1)

    def draw_pets(self, surface, frame_enum=PetFrame.IDLE1):
        """
        Draws pets using appropriate frame based on attack animation phase.
        """
        if self.phase == "attack_move":
            frame_enum = self.animate_attack(46)

        super().draw_pets(surface, frame_enum)

    def draw_attack_move(self, surface):
        self.draw_pets(surface)
        for wave in self.attack_waves:
            for sprite, kind, x, y in wave:
                if x < SCREEN_WIDTH - (90 * UI_SCALE):
                    blit_with_shadow(surface, sprite, (x, y))
                    if kind in [2,3]:
                        blit_with_shadow(surface, sprite, (x - (20 * UI_SCALE), y - (10 * UI_SCALE)))
                    if kind == 3:
                        blit_with_shadow(surface, sprite, (x - (40 * UI_SCALE), y + (10 * UI_SCALE)))

    def draw_result(self, surface):
        y = SCREEN_HEIGHT // 2 - self.bad_sprite.get_height() // 2
        if self.xaibar.selected_strength == 0:
            blit_with_shadow(surface, self.bad_sprite, (0, y))
        elif self.xaibar.selected_strength == 1:
            blit_with_shadow(surface, self.good_sprite, (0, y))
        elif self.xaibar.selected_strength == 2:
            blit_with_shadow(surface, self.great_sprite, (0, y))
        elif self.xaibar.selected_strength == 3:
            blit_with_shadow(surface, self.excellent_sprite, (0, y))
    
    def prepare_attacks(self):
        """Prepare 5 attacks from each pet based on selected_strength."""
        self.attack_phase = 0
        self.attack_waves = [[] for _ in range(5)]
        pets = get_training_targets()
        total_pets = len(pets)

        available_height = SCREEN_HEIGHT
        spacing = available_height // total_pets
        spacing = min(spacing, OPTION_ICON_SIZE + (20 * UI_SCALE))
        start_y = (SCREEN_HEIGHT - (spacing * total_pets)) // 2

        # Determine super-hit pattern based on selected_strength
        strength = self.xaibar.selected_strength

        if strength == 3:
            pattern = [4, 3, 3, 3, 3]  # 5 super-hits (megahit)
        elif strength == 2:
            pattern = [3, 3, 3, 2, 2]  # 3 super-hits, 2 normal
        elif strength == 1:
            pattern = [3, 2, 1, 1, 1]  # 1 super-hit, 4 normal
        else:
            pattern = [1] * 5  # all normal, fail

        for i, pet in enumerate(pets):
            sprite = self.attack_sprites.get(str(pet.atk_main))
            if not sprite:
                continue

            pet_y = start_y + i * spacing + OPTION_ICON_SIZE // 2 - sprite.get_height() // 2
            for j, kind in enumerate(pattern):
                # Start to the right of the pet sprite (aligned horizontally)
                x = SCREEN_WIDTH - OPTION_ICON_SIZE - (20 * UI_SCALE)
                y = pet_y
                if kind == 4:
                    sprite2 = pygame.transform.scale2x(sprite)
                    self.attack_waves[j].append((sprite2, kind, x, y))
                else:
                    self.attack_waves[j].append((sprite, kind, x, y))

    def get_attack_count(self):
        if self.xaibar.selected_strength < 1:
            return 1
        elif self.xaibar.selected_strength < 3:
            return 2
        else:
            return 3
    
    def handle_event(self, input_action):
        if self.phase == "charge" and input_action == "A":
            runtime_globals.game_sound.play("menu")
            self.xaibar.stop()
            runtime_globals.game_console.log(f"XaiBar phase ended strength {self.xaibar.selected_strength}.")
            self.phase = "wait_attack"
            self.frame_counter = 0
            self.prepare_attacks()
        elif self.phase in ["wait_attack","attack_move","impact","result"] and input_action in ["B","START"]:
            self.finish_training()
        elif self.phase in ["alert","charge"] and input_action in ["B","START"]:
            runtime_globals.game_sound.play("cancel")
            change_scene("game")