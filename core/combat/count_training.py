import pygame
import time

from core import runtime_globals
from core.animation import PetFrame
from core.constants import *
from core.utils import blit_with_shadow, change_scene, distribute_pets_evenly, get_training_targets, load_attack_sprites, sprite_load
from scenes.scene_battle import ATTACK_SPEED

READY_FRAME_COUNTER = 20
ALERT_FRAME_COUNTER = 30

class CountMatchTraining:
    def __init__(self):
        self.phase = "set_attribute"
        self.frame_counter = 0
        self.press_counter = 0
        self.rotation_index = 0
        self.start_time = 0
        self.final_color = 3  # Default to Count1
        self.correct_color = 0
        self.super_hits = {}

        self.attack_phase = 0
        self.attack_waves = []
        self.current_wave_index = 0
        self.attack_sprites = load_attack_sprites()

        self.result_text = None
        self.flash_frame = 0

        self.pet_sprites = []

        self.load_sprites()

    def load_sprites(self):
        """Loads and scales sprites using predefined constants and sprite_load()."""
        self.ready_sprites = {key: sprite_load(path, scale=2.5) for key, path in READY_SPRITES_PATHS.items()}
        self.count_sprites = {key: sprite_load(path, scale=2.5) for key, path in COUNT_SPRITES_PATHS.items()}
        self.mega_hit = sprite_load(MEGA_HIT_PATH, scale=2.5)



    def update(self):
        if self.phase == "set_attribute":
            self.frame_counter += 1
            if self.frame_counter >= READY_FRAME_COUNTER:
                self.phase = "alert"
                self.frame_counter = 0

        elif self.phase == "alert":
            self.frame_counter += 1
            if self.frame_counter >= ALERT_FRAME_COUNTER:
                self.start_count_phase()

        elif self.phase == "count":
            elapsed = time.time() - self.start_time
            if elapsed >= 3:
                self.phase = "prepare_attack"
                self.calculate_results()
                self.prepare_attack()

        elif self.phase == "attack":
            self.update_attacks()

        elif self.phase == "result":
            self.frame_counter += 1
            if self.frame_counter >= 30:
                self.finish_training()

    def start_count_phase(self):
        self.phase = "count"
        self.start_time = time.time()
        self.press_counter = 0
        self.rotation_index = 3

    def handle_event(self, input_action):
        if self.phase in ("alert", "count") and input_action == "Y" or input_action == "SHAKE": 
            if self.phase == "alert":
                self.start_count_phase()
            elif self.phase == "count":
                self.press_counter += 1
                if self.press_counter % 2 == 0:
                    self.rotation_index -= 1
                    if self.rotation_index < 1:
                        self.rotation_index = 3
        elif self.phase in ["attack","result"] and input_action in ["B","START"]:
            self.finish_training()
        elif self.phase in ("alert", "count") and input_action in ["B","START"]:
            runtime_globals.game_sound.play("cancel")
            change_scene("game")


    def get_first_pet_attribute(self):
        pet = get_training_targets()[0]
        if pet.attribute in ["", "Vi"]:
            return 1
        elif pet.attribute == "Va":
            return 2
        elif pet.attribute == "Da":
            return 3
        return 1

    def calculate_results(self):
        self.correct_color = self.get_first_pet_attribute()
        self.final_color = self.rotation_index
        for pet in get_training_targets():
            shakes = self.press_counter
            color_ok = self.final_color == self.correct_color
            if shakes >= 12 and color_ok:
                hits = 5
            elif 7 <= shakes <= 11 and color_ok:
                hits = 4
            elif 7 <= shakes <= 1 or color_ok:
                hits = 3
            elif 2 <= shakes <= 8 and color_ok:
                hits = 2
            elif 2 <= shakes <= 8 or color_ok:
                hits = 1
            else:
                hits = 0
            self.super_hits[pet] = hits

    def prepare_attack(self):
        self.phase = "attack"
        self.attack_phase = 0
        self.attack_waves = [[] for _ in range(5)]
        pets = get_training_targets()
        total_pets = len(pets)

        available_height = SCREEN_HEIGHT
        spacing = available_height // total_pets
        spacing = min(spacing, OPTION_ICON_SIZE + 20)
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
                x = SCREEN_WIDTH - OPTION_ICON_SIZE - 20
                y = pet_y
                self.attack_waves[j].append((sprite, kind, x, y))
        
        self.frame_counter = 0

    def update_attacks(self):
        if self.current_wave_index >= len(self.attack_waves):
            self.phase = "result"
            self.frame_counter = 0
            return

        wave = self.attack_waves[self.current_wave_index]
        new_wave = []
        all_off_screen = True

        if self.frame_counter == 0:
            runtime_globals.game_sound.play("attack")

        for sprite, kind, x, y in wave:
            x -= ATTACK_SPEED
            if x + 24 > 0:
                all_off_screen = False
                new_wave.append((sprite, kind, x, y))

        self.attack_waves[self.current_wave_index] = new_wave
        self.frame_counter += 1

        # Wait at least 10 frames before next wave
        if all_off_screen and self.frame_counter >= 10:
            self.current_wave_index += 1
            self.frame_counter = 0

    def draw(self, screen):
        if self.phase == "set_attribute":
            attr = self.get_first_pet_attribute()
            sprite = self.ready_sprites[attr]
            y = (SCREEN_HEIGHT - sprite.get_height()) // 2
            screen.blit(sprite, (0, y))

        elif self.phase == "alert":
            sprite = self.count_sprites[4]
            y = (SCREEN_HEIGHT - sprite.get_height()) // 2
            screen.blit(sprite, (0, y))

        elif self.phase == "count":
            sprite = self.count_sprites[self.rotation_index]
            y = (SCREEN_HEIGHT - sprite.get_height()) // 2
            screen.blit(sprite, (0, y))

        elif self.phase == "attack":
            self.draw_pets(screen)
            for wave in self.attack_waves:
                for sprite, kind, x, y in wave:
                    if x < 150:
                        screen.blit(sprite, (x, y))
                        if kind > 1:
                            blit_with_shadow(screen, sprite, (x - 20, y - 10))
                        if kind == 3:
                            blit_with_shadow(screen, sprite, (x - 40, y + 10))

        elif self.phase == "result":
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
                y = 100
                screen.blit(text, (x, y))

    def draw_pets(self, surface):
        """
        Draws pets using appropriate frame based on attack animation phase.
        """
        if self.phase == "attack":
            if self.frame_counter < 30:
                frame_enum = PetFrame.TRAIN2
            else:
                frame_enum = PetFrame.TRAIN1
        else:
            frame_enum = PetFrame.IDLE1

        self.pet_sprites = []
        for pet in get_training_targets():
            sprite = runtime_globals.pet_sprites[pet][frame_enum.value]
            sprite = pygame.transform.scale(sprite, (OPTION_ICON_SIZE, OPTION_ICON_SIZE))
            self.pet_sprites.append(sprite)

        total_pets = len(self.pet_sprites)
        available_height = SCREEN_HEIGHT
        spacing = min(available_height // total_pets, OPTION_ICON_SIZE + 20)
        start_y = (SCREEN_HEIGHT - spacing * total_pets) // 2

        for i, sprite in enumerate(self.pet_sprites):
            x = SCREEN_WIDTH - OPTION_ICON_SIZE - 16
            y = start_y + i * spacing
            blit_with_shadow(surface, sprite, (x, y))

    def finish_training(self):
        if self.super_hits.get(get_training_targets()[0], 0) > 1:
            runtime_globals.game_sound.play("attack_fail")
        else:
            runtime_globals.game_sound.play("fail")

        for pet in get_training_targets():
            pet.finish_training(self.super_hits.get(pet, 0) > 1)
        distribute_pets_evenly()
        change_scene("game")
