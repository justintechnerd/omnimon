#=====================================================================
# DummyTraining (Simple Strength Bar Training)
#=====================================================================

import pygame

from core import runtime_globals
from core.animation import PetFrame
from core.constants import *
from core.utils import blit_with_shadow, change_scene, distribute_pets_evenly, get_training_targets, load_attack_sprites, sprite_load
from scenes.scene_battle import ALERT_DURATION_FRAMES, ATTACK_SPEED, BAR_HOLD_TIME_MS, IMPACT_DURATION_FRAMES, RESULT_SCREEN_FRAMES, WAIT_ATTACK_READY_FRAMES

class DummyTraining:
    """
    Dummy training mode where players build up strength by holding a bar.
    """

    def __init__(self) -> None:
        self.phase = "alert"
        self.frame_counter = 0
        self.strength = 0
        self.bar_level = 14
        self.bar_timer = 0

        self.attack_positions = []
        self.attack_phase = 1
        self.flash_frame = 0
        self.impact_counter = 0
        self.attacks_prepared = False

        self.alert_sprite = sprite_load(ALERT_SPRITE_PATH, size=(48, 48))
        self.go_sprite = sprite_load(GO_SPRITE_PATH, size=(48, 48))
        self.bar_piece = sprite_load(BAR_PIECE_PATH, size=(24, 12))
        self.training_max = sprite_load(TRAINING_MAX_PATH, size=(60, 60))
        self.bar_back = sprite_load(BAR_BACK_PATH, size=(30, 170))
        self.battle1 = sprite_load(BATTLE1_PATH)  # No scaling applied
        self.battle2 = sprite_load(BATTLE2_PATH)  # No scaling applied
        self.bag1 = sprite_load(BAG1_PATH, size=(60, 120))
        self.bag2 = sprite_load(BAG2_PATH, size=(60, 120))
        
        self.attack_sprites = load_attack_sprites()

        self.pet_sprites = {}
        self.pet_state = None

    def update(self):
        if self.phase == "alert":
            self.update_alert_phase()
        elif self.phase == "bar":
            self.update_bar_phase()
        elif self.phase == "wait_attack":
            self.update_wait_attack_phase()
        elif self.phase == "attack_move":
            self.move_attacks()
        elif self.phase == "impact":
            self.update_impact_phase()
        elif self.phase == "result":
            self.update_result_phase()

    def update_alert_phase(self):
        if self.frame_counter == 30:
            runtime_globals.game_sound.play("happy")
        self.frame_counter += 1
        if self.frame_counter >= ALERT_DURATION_FRAMES:
            self.phase = "bar"
            self.bar_timer = pygame.time.get_ticks()

    def update_bar_phase(self):
        if pygame.time.get_ticks() - self.bar_timer > BAR_HOLD_TIME_MS:
            self.phase = "wait_attack"
            self.frame_counter = 0
            self.prepare_attacks()
            runtime_globals.game_sound.play("attack")

    def update_wait_attack_phase(self):
        self.frame_counter += 1
        if self.frame_counter >= WAIT_ATTACK_READY_FRAMES:
            self.phase = "attack_move"
            self.frame_counter = 0

    def update_impact_phase(self):
        self.flash_frame += 1
        if self.flash_frame >= IMPACT_DURATION_FRAMES:
            self.phase = "result"
            self.frame_counter = 0

    def update_result_phase(self):
        self.frame_counter += 1
        if self.frame_counter >= RESULT_SCREEN_FRAMES:
            self.finish_training()

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
                self.attack_phase = 2
                #self.attack_positions.clear()

            self.attack_positions = new_positions

        elif self.attack_phase == 2:
            bag_x = 50
            for sprite, (x, y) in self.attack_positions:
                x -= ATTACK_SPEED

                if x < 0:
                    x = SCREEN_WIDTH

                if x <= bag_x + 48:
                    finished = True
                new_positions.append((sprite, (x, y)))

            if finished:
                runtime_globals.game_sound.play("attack_hit")
                self.phase = "impact"
                self.flash_frame = 0

            self.attack_positions = new_positions

    def finish_training(self):
        """Apply training results and return to game."""
        if self.strength == 14:
            runtime_globals.game_sound.play("attack_fail")
        else:
            runtime_globals.game_sound.play("fail")

        for pet in get_training_targets():
            pet.finish_training(self.strength == 14)

        distribute_pets_evenly()
        change_scene("game")

    def draw(self, screen: pygame.Surface):
        if self.phase == "alert":
            self.draw_alert(screen)
        elif self.phase == "bar":
            self.draw_strength_bar(screen)
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
            x = SCREEN_WIDTH - OPTION_ICON_SIZE - 16
            y = start_y + i * spacing
            blit_with_shadow(surface, pet, (x, y))

    def draw_alert(self, screen):
        self.draw_pets(screen, PetFrame.IDLE1)
        if self.frame_counter < 30:
            center_x = SCREEN_WIDTH // 2 - self.alert_sprite.get_width() // 2
            screen.blit(self.alert_sprite, (center_x, 40))
        else:
            center_x = SCREEN_WIDTH // 2 - self.alert_sprite.get_width() // 2
            screen.blit(self.go_sprite, (center_x, 40))

    def draw_strength_bar(self, surface):
        bar_x = (SCREEN_WIDTH // 2 - self.bar_piece.get_width() // 2) - 40
        bar_bottom_y = SCREEN_HEIGHT // 2 + 110

        if self.strength == 14:
            surface.blit(self.training_max, (bar_x - 18, bar_bottom_y - 209))
        

        blit_with_shadow(surface, self.bar_back, (bar_x - 3, bar_bottom_y - 169))

        for i in range(self.strength):
            y = bar_bottom_y - (i + 1) * self.bar_piece.get_height()
            surface.blit(self.bar_piece, (bar_x, y))

        self.draw_pets(surface, PetFrame.IDLE1)

    def draw_attack_ready(self, surface):
        self.draw_pets(surface, PetFrame.ATK2)
        for sprite, (x, y) in self.attack_positions:
            blit_with_shadow(surface, sprite, (x, y))

    def draw_attack_move(self, surface):
        if self.attack_phase == 1:
            self.draw_pets(surface, PetFrame.ATK2)
        else:
            blit_with_shadow(surface, self.bag1, (50, SCREEN_HEIGHT // 2 - self.bag1.get_height() // 2))

        for sprite, (x, y) in self.attack_positions:
            blit_with_shadow(surface, sprite, (x, y))

    def draw_impact(self, screen):
        flash = self.battle1 if (self.flash_frame // 2) % 2 == 0 else self.battle2
        flash = pygame.transform.scale(flash, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(flash, (0, 0))

    def draw_result(self, surface):
        result_img = None
        if 10 <= self.strength < 14:
            result_img = self.bag2
        elif self.strength < 10:
            result_img = self.bag1

        if result_img:
            x = 50
            y = SCREEN_HEIGHT // 2 - result_img.get_height() // 2
            blit_with_shadow(surface, result_img, (x, y))

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
                    offset_y = j * 15  # slight spread if multiple shots
                    x = SCREEN_WIDTH - OPTION_ICON_SIZE - 70
                    y = start_y + i * spacing + offset_y
                    self.attack_positions.append((atk_sprite, (x, y)))

    def get_attack_count(self):
        if self.strength < 10:
            return 1
        elif self.strength < 14:
            return 2
        else:
            return 3
    
    def handle_event(self, input_action):
        if self.phase == "bar" and input_action == "A":
            runtime_globals.game_sound.play("menu")
            self.strength = min(self.strength + 1, self.bar_level)
        elif self.phase in ["wait_attack","attack_move","impact","result"] and input_action in ["B","START"]:
            self.finish_training()
        elif self.phase in ["alert","bar"] and input_action in ["B","START"]:
            runtime_globals.game_sound.play("cancel")
            change_scene("game")