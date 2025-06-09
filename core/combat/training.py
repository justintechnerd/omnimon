#=====================================================================
# DummyTraining (Simple Strength Bar Training)
#=====================================================================

import random
import pygame

from core import runtime_globals
from core.animation import PetFrame
from core.constants import *
from core.utils import blit_with_shadow, change_scene, distribute_pets_evenly, get_training_targets, load_attack_sprites, sprite_load
from scenes.scene_battle import ALERT_DURATION_FRAMES, ATTACK_SPEED, BAR_HOLD_TIME_MS, IMPACT_DURATION_FRAMES, RESULT_SCREEN_FRAMES, WAIT_ATTACK_READY_FRAMES

class Training:
    """
    Training mode where players build up strength by holding a bar.
    """

    def __init__(self) -> None:
        self.phase = "alert"
        self.frame_counter = 0

        self.attack_positions = []

        self.attack_phase = 0
        self.attack_waves = []
        self.current_wave_index = 0
        
        self.attack_phase = 1
        self.flash_frame = 0
        self.impact_counter = 0
        self.attacks_prepared = False

        self.ready_sprite = sprite_load(READY_SPRITE_PATH, scale=2.5)
        self.go_sprite = sprite_load(GO_SPRITE_PATH, scale=2.5)
        self.bar_piece = sprite_load(BAR_PIECE_PATH, size=(24, 12))
        self.training_max = sprite_load(TRAINING_MAX_PATH, size=(60, 60))
        self.bar_back = sprite_load(BAR_BACK_PATH, size=(30, 170))
        self.battle1 = sprite_load(BATTLE1_PATH)  # No scaling applied
        self.battle2 = sprite_load(BATTLE2_PATH)  # No scaling applied

        self.bad_sprite = sprite_load(BAD_SPRITE_PATH, scale=2.5)
        self.good_sprite = sprite_load(GOOD_SPRITE_PATH, scale=2.5)
        self.great_sprite = sprite_load(GREAT_SPRITE_PATH, scale=2.5)
        self.excellent_sprite = sprite_load(EXCELLENT_SPRITE_PATH, scale=2.5)

        self.attack_jump = 0
        self.attack_forward = 0
        
        self.attack_sprites = load_attack_sprites()

        self.pet_sprites = {}
        self.pet_state = None

    def update(self):
        if self.phase == "alert":
            self.update_alert_phase()
        elif self.phase == "charge":
            self.update_charge_phase()
        elif self.phase == "wait_attack":
            self.update_wait_attack_phase()
        elif self.phase == "attack_move":
            self.move_attacks()
        elif self.phase == "impact":
            self.update_impact_phase()
        elif self.phase == "result":
            self.update_result_phase()
        self.frame_counter += 1

    def update_alert_phase(self):
        if self.frame_counter == 30:
            runtime_globals.game_sound.play("happy")
        if self.frame_counter >= ALERT_DURATION_FRAMES:
            self.phase = "charge"
            self.frame_counter = 0
            self.bar_timer = pygame.time.get_ticks()

    def update_charge_phase(self):
        pass

    def update_wait_attack_phase(self):
        if self.frame_counter <= 9:
            self.attack_forward += 1
            if self.frame_counter < 5:
                self.attack_jump += 1
            elif self.frame_counter > 5:
                self.attack_jump -= 1
        else:
            self.attack_forward -= 1

        if self.frame_counter >= WAIT_ATTACK_READY_FRAMES:
            self.phase = "attack_move"
            self.frame_counter = 0
            runtime_globals.game_sound.play("attack")

    def update_impact_phase(self):
        self.flash_frame += 1
        if self.flash_frame >= IMPACT_DURATION_FRAMES:
            self.phase = "result"
            self.frame_counter = 0

    def update_result_phase(self):
        if self.frame_counter >= RESULT_SCREEN_FRAMES:
            self.finish_training()

    def move_attacks(self):
        pass

    def finish_training(self):
        """Apply training results and return to game."""
        won = self.check_victory()
        if won:
            runtime_globals.game_sound.play("attack_fail")
        else:
            runtime_globals.game_sound.play("fail")

        for pet in get_training_targets():
            pet.finish_training(won)

        distribute_pets_evenly()
        change_scene("game")

    def draw(self, screen: pygame.Surface):
        if self.phase == "alert":
            self.draw_alert(screen)
        elif self.phase == "charge":
            self.draw_charge(screen)
        elif self.phase == "wait_attack":
            self.draw_attack_ready(screen)
        elif self.phase == "attack_move":
            self.draw_attack_move(screen)
        elif self.phase == "impact":
            self.draw_impact(screen)
        elif self.phase == "result":
            self.draw_result(screen)

    def draw_pets(self, surface, frame_enum=PetFrame.IDLE1):
        """
        Draws pets vertically aligned, using the specified animation frame.
        Dynamically adjusts spacing based on number of targets.
        """

        if frame_enum != self.pet_state:
            self.pet_sprites = []
            for pet in get_training_targets():
                sprite = runtime_globals.pet_sprites[pet][frame_enum.value]
                sprite = pygame.transform.scale(sprite, (OPTION_ICON_SIZE, OPTION_ICON_SIZE))
                self.pet_sprites.append(sprite)
        self.pet_state = frame_enum
        
        total_pets = len(self.pet_sprites)

        available_height = SCREEN_HEIGHT  # Padding
        spacing = available_height // total_pets
        spacing = min(spacing, OPTION_ICON_SIZE + 20)  # Avoid too large gaps
        start_y = (SCREEN_HEIGHT - (spacing * total_pets)) // 2

        for i, pet in enumerate(self.pet_sprites):
            x = SCREEN_WIDTH - OPTION_ICON_SIZE - 16 + self.attack_forward
            y = start_y + i * spacing - self.attack_jump
            blit_with_shadow(surface, pet, (x, y))

    def draw_alert(self, screen):
        center_y = SCREEN_HEIGHT // 2 - self.ready_sprite.get_height() // 2
        blit_with_shadow(screen, self.ready_sprite, (0, center_y))

    def draw_attack_ready(self, surface):
        self.draw_pets(surface, PetFrame.ATK2)

    def draw_charge(self, surface):
        pass

    def draw_attack_move(self, surface):
        pass

    def draw_impact(self, screen):
        flash = self.battle1 if (self.flash_frame // 2) % 2 == 0 else self.battle2
        flash = pygame.transform.scale(flash, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(flash, (0, 0))

    def draw_result(self, surface):
        pass
    
    def handle_event(self, input_action):
        if self.phase == "charge" and input_action == "A":
            runtime_globals.game_sound.play("menu")
            self.strength = min(self.strength + 1, self.bar_level)
        elif self.phase in ["wait_attack","attack_move","impact","result"] and input_action in ["B","START"]:
            self.finish_training()
        elif self.phase in ["alert","charge"] and input_action in ["B","START"]:
            runtime_globals.game_sound.play("cancel")
            change_scene("game")