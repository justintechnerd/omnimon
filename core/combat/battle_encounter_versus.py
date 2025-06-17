# core/combat/battle_encounter_versus.py

import random
import pygame
from core.combat.battle_encounter import BattleEncounter
from core.animation import PetFrame
from core import runtime_globals
from core.combat.combat_constants import ALERT_DURATION_FRAMES
from core.constants import *
from core.utils.pygame_utils import blit_with_shadow
from core.utils.scene_utils import change_scene
from core.utils.utils_unlocks import unlock_item

class BattleEncounterVersus(BattleEncounter):
    def __init__(self, pet1, pet2):
        self.pet1 = pet1
        self.pet2 = pet2

        # Set initial attacker/defender
        self.attacking_pet = self.pet1
        self.attacking_enemy = self.pet2
        self.attacking_pets = [self.pet1]
        self.attacking_enemies = [self.pet2]

        # Versus-specific setup
        self.enemies = [self.pet2]
        self.enemy_positions = [[self.pet2, -PET_WIDTH - 2]]

        self.frame_counter = 0
        self.result_timer = 0
        # skip enemy loading logic in base init by calling last
        super().__init__(self.attacking_pet.module, 1, 1, 1)

        self.attacking_pet = self.pet1
        self.attacking_enemy = self.pet2
        self.attacking_pets = [self.pet1]
        self.attacking_enemies = [self.pet2]
        self.phase = "alert"

        self.player_health = 3
        self.enemy_health = 3

    def load_enemies(self):
        self.enemy_positions.append([self.pet1, 22])

    def select_next_pair(self):
        self.attacking_pet = self.pet2
        self.attacking_enemy = self.pet1

        self.phase = "move_pair"
        runtime_globals.game_console.log("Entering move_pair phase")
        self.frame_counter = 0
        self.attack_offset = 0

    def draw(self, surface: pygame.Surface):
        super().draw(surface)
        if self.phase in ["intimidate", "alert"]:
            surface.blit(self.battle_sprite, (0, 0))


    def draw_pets(self, surface: pygame.Surface):
        anim_toggle = (self.frame_counter + 5) // 15 % 2

        if self.phase in ["alert"]:
            frame_id = PetFrame.ANGRY.value
        elif self.enemy_health <= 0:
            frame_id = PetFrame.HAPPY.value
        elif self.player_health <= 0:
            frame_id = PetFrame.LOSE.value
        elif self.phase == "pet_attack" :
            frame_id = PetFrame.ATK2.value
        else:
            frame_id = PetFrame.IDLE1.value if anim_toggle == 0 else PetFrame.IDLE2.value

        sprite = runtime_globals.pet_sprites[self.pet2][frame_id]
        sprite = pygame.transform.scale(sprite, (PET_WIDTH, PET_HEIGHT))
        x = SCREEN_WIDTH - PET_WIDTH - 2

        x -= 20

        y = self.get_y(0, 1)
        blit_with_shadow(surface, sprite, (x, y))

    def draw_enemies(self, surface: pygame.Surface):
        total = len(self.enemy_positions)
        for i, (enemy, x) in enumerate(self.enemy_positions):
            y = self.get_y(i, total)
            anim_toggle = (self.frame_counter + i * 5) // 15 % 2  # Varia com o índice

            if self.phase == "enemy_attack" and enemy == self.attacking_enemy:
                frame_id = PetFrame.ATK2.value
            elif self.enemy_health <= 0:
                frame_id = PetFrame.ANGRY.value
            elif self.phase in ["move_pair", "retreat", "post_attack_delay", "alert", "charge", "enemy_attack"]:
                frame_id = PetFrame.IDLE1.value if anim_toggle == 0 else PetFrame.IDLE2.value
            else:
                frame_id = PetFrame.IDLE1.value

            sprite = enemy.get_sprite(frame_id)

            if sprite:
                sprite = pygame.transform.flip(sprite, True, False)
                blit_with_shadow(surface, sprite, (x + 1, y))

    def update_retreat(self):
        self.forward_distance = 0
        self.phase = "prepare_attack"
        runtime_globals.game_console.log("Entering prepare_attack phase")
        self.frame_counter = 0
        self.prepare_attacks()

    def update_alert(self):
        # Skip alert/charge — go straight to attack
        if self.frame_counter == 1:
            runtime_globals.game_sound.play("battle")
        self.frame_counter += 1
        
        if self.frame_counter > ALERT_DURATION_FRAMES:
            self.frame_counter = 0
            self.phase = "move_pair"

    def prepare_attacks(self):
        # Skip full prepare logic — we already know both pets
        self.phase = "move_pair"
        self.frame_counter = 0

    def update_pet_attack(self):
        if not hasattr(self, "projectiles"):
            # Início do ataque: define os projéteis com base na força
            if self.attacking_pet.atk_alt > 0 and random.random() < 0.3:
                atk_id = str(self.attacking_pet.atk_alt)
            else:
                atk_id = str(self.attacking_pet.atk_main)
            atk_sprite = self.attack_sprites.get(atk_id)

            # Determina número de ataques com base na força
            hits = random.randint(1, 3)
            pet_index = 0
            y = self.get_y(pet_index, 1)
            x = SCREEN_WIDTH - PET_WIDTH - 2 - self.forward_distance

            self.projectiles = []
            self.projectiles.append([atk_sprite.copy(), [x, y]])

            if hits > 1:
                self.projectiles.append([atk_sprite.copy(), [x - (20 * UI_SCALE), y - (10 * UI_SCALE)]])
            if hits == 3:
                self.projectiles.append([atk_sprite.copy(), [x - (40 * UI_SCALE), y + (10 * UI_SCALE)]])

            # Calcula se o ataque acerta ANTES de mover os projéteis
            self.attack_hit = self.check_hit(self.attacking_pet, self.attacking_enemy, is_player=True)
            runtime_globals.game_sound.play("attack")

        # Move os projéteis (frame-rate independent)
        done = True
        for sprite_data in self.projectiles:
            sprite, (x, y) = sprite_data
            x -= 4 * UI_SCALE * (30 / FRAME_RATE)  # Frame-rate independent speed
            sprite_data[1][0] = x
            enemy_index = 0
            target_x = self.enemy_positions[enemy_index][1] + PET_WIDTH // 2
            if x > target_x:
                done = False

        if done:
            del self.projectiles
            self.frame_counter = 0
            if self.attack_hit:
                runtime_globals.game_sound.play("attack_hit")
                self.enemy_health = max(0, self.enemy_health - 1)

                enemy_index = 0
                enemy_y = self.get_y(enemy_index, 1)
                enemy_x = self.enemy_positions[enemy_index][1] + PET_WIDTH // 2
                self.hit_animations.append([0, [enemy_x + (16 * UI_SCALE), enemy_y + (24 * UI_SCALE)]])
            else:
                runtime_globals.game_sound.play("attack_fail")
                enemy_index = 0
                enemy_y = self.get_y(enemy_index, 1)
                enemy_x = self.enemy_positions[enemy_index][1]
                runtime_globals.game_message.add("MISS", (enemy_x + (16 * UI_SCALE), enemy_y - (10 * UI_SCALE)), (255, 0, 0))

            if self.enemy_health <= 0 or self.player_health <= 0:
                self.phase = "result"
                runtime_globals.game_console.log("Entering result phase")
            else:
                self.phase = "post_attack_delay"
                self.after_attack_phase = "enemy"
                runtime_globals.game_console.log("Entering post_attack_delay phase")

    def update_enemy_attack(self):
        self.attacking_pet = self.pet2
        self.attacking_enemy = self.pet1
        if not hasattr(self, "enemy_projectiles"):
            # Início do ataque inimigo
            if self.attacking_enemy.atk_alt > 0 and random.random() < 0.3:
                atk_id = str(self.attacking_enemy.atk_alt)
            else:
                atk_id = str(self.attacking_enemy.atk_main)
            atk_sprite = self.attack_sprites.get(atk_id)

            # Define número de projéteis
            hits = random.randint(1, 3)
            enemy_index = 0
            y_base = self.get_y(enemy_index, 1)

            self.enemy_projectiles = []
            for i in range(hits):
                x = self.enemy_positions[enemy_index][1] + PET_WIDTH
                y = y_base + i * 16
                sprite = pygame.transform.flip(atk_sprite.copy(), True, False)
                self.enemy_projectiles.append([sprite, [x, y]])

            self.enemy_hit = self.check_hit(self.attacking_enemy, self.attacking_pet, is_player=True)
            runtime_globals.game_sound.play("attack")

        # Move os projéteis (frame-rate independent)
        done = True
        for sprite_data in self.enemy_projectiles:
            sprite, (x, y) = sprite_data
            x += 4 * UI_SCALE * (30 / FRAME_RATE)  # Frame-rate independent speed
            sprite_data[1][0] = x
            pet_index = 0
            target_x = SCREEN_WIDTH - PET_WIDTH - 2 - self.forward_distance
            if x < target_x:
                done = False

        if done:
            del self.enemy_projectiles
            self.frame_counter = 0
            if self.enemy_hit:
                runtime_globals.game_sound.play("attack_hit")
                self.player_health = max(0, self.player_health - 1)

                pet_index = 0
                pet_y = self.get_y(pet_index, 1)
                pet_x = SCREEN_WIDTH - PET_WIDTH - 2 - self.forward_distance + PET_WIDTH // 2
                self.hit_animations.append([0, [pet_x, pet_y + (24 * UI_SCALE)]])
            else:
                runtime_globals.game_sound.play("attack_fail")
                pet_index = 0
                pet_y = self.get_y(pet_index, 1)
                pet_x = SCREEN_WIDTH - PET_WIDTH - 2 - self.forward_distance
                runtime_globals.game_message.add("MISS", (pet_x + (16 * UI_SCALE), pet_y - (10 * UI_SCALE)), (255, 0, 0))

            if self.enemy_health <= 0 or self.player_health <= 0:
                self.phase = "result"
                runtime_globals.game_console.log("Entering result phase")
            else:
                self.phase = "post_attack_delay"
                self.after_attack_phase = "retreat"
                runtime_globals.game_console.log("Entering post_attack_delay phase")

    def prepare_attacks(self):
        """
        Prepara listas de ataque e escolhe o primeiro par para iniciar a sequência.
        """
        self.select_next_pair()

    def update_result(self):
        self.result_timer += 1
        if self.result_timer < int(30 * (FRAME_RATE / 30)):
            return

        winner = self.pet1 if self.enemy_health <= 0 else self.pet2
        loser = self.pet2 if winner == self.pet1 else self.pet1

        runtime_globals.game_sound.play("happy")

        winner.finish_versus(True)
        loser.finish_versus(False)
        winner.set_state("happy2")
        loser.set_state("lose")

        # Unlock "versus" items for both pets if they are from the same module
        if self.pet1.module == self.pet2.module:
            module_name = self.pet1.module
            for pet in (self.pet1, self.pet2):
                unlock_item(module_name, "versus", f"Slot{pet.version}")

        change_scene("game")
