#=====================================================================
# BattleEncounter
#=====================================================================

import random
import time

import pygame
from core import game_globals, runtime_globals
from core.combat.battle_encounter import BattleEncounter
from core.constants import *
from core.utils import get_battle_targets, get_selected_pets, sprite_load
from core.utils_unlocks import unlock_item

READY_FRAME_COUNTER = 60
ALERT_FRAME_COUNTER = 90
IDLE_ANIM_DURATION = 30

class BattleEncounterPENC(BattleEncounter):
    
    def __init__(self, module):
        super().__init__(module)
        self.press_counter = 0
        self.final_color = 3
        self.correct_color = 0
        self.super_hits = 0
        self.super_hit_damage = False
        self.ready_sprites = {
            1: sprite_load(READY_SPRITES_PATHS[1], scale=2.5),
            2: sprite_load(READY_SPRITES_PATHS[2], scale=2.5),
            3: sprite_load(READY_SPRITES_PATHS[3], scale=2.5)
        }

        self.count_sprites = {
            4: sprite_load(COUNT_SPRITES_PATHS[4], scale=2.5),
            3: sprite_load(COUNT_SPRITES_PATHS[3], scale=2.5),
            2: sprite_load(COUNT_SPRITES_PATHS[2], scale=2.5),
            1: sprite_load(COUNT_SPRITES_PATHS[1], scale=2.5)
        }

        self.mega_hit = sprite_load(MEGA_HIT_PATH, scale=2.5)

        self.player_health = 3
        self.enemy_health = 3
    
    def get_first_pet_attribute(self):
        pet = get_battle_targets()[0]
        if pet.attribute in ["", "Vi"]:
            return 1
        elif pet.attribute == "Va":
            return 2
        elif pet.attribute == "Da":
            return 3
        return 1

    def update(self):
        super().update()
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
                self.frame_counter = 0
                self.prepare_attacks()

    def calculate_results(self):
        self.correct_color = self.get_first_pet_attribute()
        self.final_color = self.rotation_index
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

        self.super_hits = hits
            
    def update_pet_attack(self):
        if not hasattr(self, "projectiles"):
            # Início do ataque: define os projéteis com base na força
            if self.attacking_enemy.atk_alt > 0 and random.random() < 0.3:
                atk_id = str(self.attacking_enemy.atk_alt)
            else:
                atk_id = str(self.attacking_enemy.atk_main)
            atk_sprite = self.attack_sprites.get(atk_id)

            self.super_hit_damage = False
            # Determina número de ataques com base na força
            if self.super_hits == 5 and random.random() < 0.8:
                hits = 3
                self.super_hit_damage = True
            elif self.super_hits > 2 and random.random() < 0.5:
                hits = 2
            else:
                hits = 1

            pet_index = get_selected_pets().index(self.attacking_pet)
            y_base = self.get_y(pet_index, len(get_selected_pets()))

            self.projectiles = []
            for i in range(hits):
                x = SCREEN_WIDTH - PET_WIDTH - 2 - self.forward_distance
                y = y_base + i * 16
                self.projectiles.append([atk_sprite.copy(), [x, y]])

            # Calcula se o ataque acerta ANTES de mover os projéteis
            self.attack_hit = self.check_hit(self.attacking_pet, self.attacking_enemy, is_player=True)
            runtime_globals.game_sound.play("attack")
        
        # Move os projéteis
        done = True
        for sprite_data in self.projectiles:
            sprite, (x, y) = sprite_data
            x -= 4  # Velocidade
            sprite_data[1][0] = x
            enemy_index = get_selected_pets().index(self.attacking_pet)
            target_x = self.enemy_positions[enemy_index][1] + PET_WIDTH // 2
            if x > target_x:
                done = False

        if done:
            del self.projectiles
            self.frame_counter = 0
            if self.attack_hit:
                runtime_globals.game_sound.play("attack_hit")
                if self.super_hit_damage:
                    self.enemy_health = max(0, self.enemy_health - 2)
                    self.super_hit_damage = 0
                else:
                    self.enemy_health = max(0, self.enemy_health - 1)

                enemy_index = get_selected_pets().index(self.attacking_pet)
                enemy_y = self.get_y(enemy_index, len(get_selected_pets()))
                enemy_x = self.enemy_positions[enemy_index][1] + PET_WIDTH // 2
                self.hit_animations.append([0, [enemy_x+ 16, enemy_y+24]])
            else:
                runtime_globals.game_sound.play("attack_fail")
                enemy_index = get_selected_pets().index(self.attacking_pet)
                enemy_y = self.get_y(enemy_index, len(get_selected_pets()))
                enemy_x = self.enemy_positions[enemy_index][1]
                runtime_globals.game_message.add("MISS", (enemy_x + 16, enemy_y - 10), (255, 0, 0))

            if self.enemy_health <= 0 or self.player_health <= 0:
                self.phase = "result"
                runtime_globals.game_console.log("Entering result phase")
            else:
                self.phase = "post_attack_delay"
                self.after_attack_phase = "enemy"
                runtime_globals.game_console.log("Entering post_attack_delay phase")

    def update_enemy_attack(self):
        if not hasattr(self, "enemy_projectiles"):
            # Início do ataque inimigo
            if self.attacking_enemy.atk_alt > 0 and random.random() < 0.3:
                atk_id = str(self.attacking_enemy.atk_alt)
            else:
                atk_id = str(self.attacking_enemy.atk_main)
            atk_sprite = self.attack_sprites.get(atk_id)

            self.super_hit_damage = False
            # Determina número de ataques com base na força
            if random.random() < 0.1:
                hits = 3
                self.super_hit_damage = True
            elif random.random() < 0.6:
                hits = 2
            else:
                hits = 1
            enemy_index = self.enemies.index(self.attacking_enemy)
            y_base = self.get_y(enemy_index, len(self.enemies))

            self.enemy_projectiles = []
            for i in range(hits):
                x = self.enemy_positions[enemy_index][1] + PET_WIDTH
                y = y_base + i * 16
                sprite = pygame.transform.flip(atk_sprite.copy(), True, False)
                self.enemy_projectiles.append([sprite, [x, y]])

            self.enemy_hit = self.check_hit(self.attacking_enemy, self.attacking_pet, is_player=False)
            runtime_globals.game_sound.play("attack")

        # Move os projéteis
        done = True
        for sprite_data in self.enemy_projectiles:
            sprite, (x, y) = sprite_data
            x += 4  # Velocidade para a direita
            sprite_data[1][0] = x
            pet_index = get_selected_pets().index(self.attacking_pet)
            target_x = SCREEN_WIDTH - PET_WIDTH - 2 - self.forward_distance
            if x < target_x:
                done = False

        if done:
            del self.enemy_projectiles
            self.frame_counter = 0
            if self.enemy_hit:
                runtime_globals.game_sound.play("attack_hit")
                if self.super_hit_damage:
                    self.player_health = max(0, self.player_health - 2)
                    self.super_hit_damage = 0
                else:
                    self.player_health = max(0, self.player_health - 1)

                pet_index = get_selected_pets().index(self.attacking_pet)
                pet_y = self.get_y(pet_index, len(get_selected_pets()))
                pet_x = SCREEN_WIDTH - PET_WIDTH - 2 - self.forward_distance + PET_WIDTH // 2
                self.hit_animations.append([0, [pet_x, pet_y+24]])
            else:
                runtime_globals.game_sound.play("attack_fail")
                pet_index = get_selected_pets().index(self.attacking_pet)
                pet_y = self.get_y(pet_index, len(get_selected_pets()))
                pet_x = SCREEN_WIDTH - PET_WIDTH - 2 - self.forward_distance
                runtime_globals.game_message.add("MISS", (pet_x + 16, pet_y - 10), (255, 0, 0))

            if self.enemy_health <= 0 or self.player_health <= 0:
                self.phase = "result"
                runtime_globals.game_console.log("Entering result phase")
            else:
                self.phase = "post_attack_delay"
                self.after_attack_phase = "retreat"
                runtime_globals.game_console.log("Entering post_attack_delay phase")
                
    def start_count_phase(self):
        self.phase = "count"
        self.start_time = time.time()
        self.press_counter = 0
        self.rotation_index = 3

    def draw(self, screen):
        super().draw(screen)
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

    def update_intimidate(self):
        if self.frame_counter >= IDLE_ANIM_DURATION:
            self.phase = "set_attribute"
            self.frame_counter = 0

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

    def update_result(self):
        self.result_timer += 1
        #is_last_round = game_globals.battle_round == ROUND_LIMITS.get(globals.battle_area, 3)

        if self.result_timer < 30:
            # pisca aviso clear
            return

        if self.enemy_health == 0:
            runtime_globals.game_sound.play("happy")
            game_globals.battle_round[self.module] += 1
            if game_globals.battle_round[self.module] < 4:
                self.player_health = 3
                self.enemy_health = 3
                self.phase = "level"
                self.result_timer  = 0
                self.pet_anim_index = 0
                self.pet_anim_counter = 0
                self.press_counter = 0
                self.final_color = 3
                self.correct_color = 0
                self.super_hits = 0
                self.frame_counter = 0
                self.enemies = []
                self.enemy_positions = []
                self.attacking_pet = None
                self.attacking_enemy = None
                self.forward_distance = 0
                self.load_enemies()
            else:
                game_globals.battle_round[self.module] = 1
                game_globals.battle_area[self.module] += 1
                unlock_item("DMC", "backgrounds", "the_net")
                if game_globals.battle_area[self.module] > 4:
                    for pet in get_selected_pets():
                        if pet.module == "PenC":
                            if pet.version == 1:
                                unlock_item("PenC", "backgrounds", "nsp_box")
                            elif pet.version == 2:
                                unlock_item("PenC", "backgrounds", "dsa_box")
                            elif pet.version == 3:
                                unlock_item("PenC", "backgrounds", "nso_box")
                            elif pet.version == 4:
                                unlock_item("PenC", "backgrounds", "wgu_box")
                            elif pet.version == 5:
                                unlock_item("PenC", "backgrounds", "mem_box")
                            elif pet.version == 0:
                                unlock_item("PenC", "backgrounds", "vbu_box")
                if game_globals.battle_area[self.module] > 10:
                    game_globals.battle_area[self.module] = 1
                    for pet in get_selected_pets():
                        if pet.module == "PenC":
                            if pet.version == 1:
                                unlock_item("PenC", "backgrounds", "nsp_neo")
                            elif pet.version == 2:
                                unlock_item("PenC", "backgrounds", "dsa_neo")
                            elif pet.version == 3:
                                unlock_item("PenC", "backgrounds", "nso_neo")
                            elif pet.version == 4:
                                unlock_item("PenC", "backgrounds", "wgu_neo")
                            elif pet.version == 5:
                                unlock_item("PenC", "backgrounds", "mem_neo")
                            elif pet.version == 0:
                                unlock_item("PenC", "backgrounds", "vbu_neo")
                self.return_to_main_scene()
        else:
            runtime_globals.game_sound.play("fail")
            # perdeu
            game_globals.battle_round[self.module] = 1

            self.return_to_main_scene()

    def check_hit(self, attacker, defender, is_player=False) -> bool:
        advantage = 0
        if attacker.attribute == "Va":
            if defender.attribute == "Da":
                advantage = -10
            elif defender.attribute == "Vi":
                advantage = 10
        elif attacker.attribute == "Da":
            if defender.attribute == "Va":
                advantage = 10
            elif defender.attribute == "Vi":
                advantage = -10
        elif attacker.attribute == "Vi":
            if defender.attribute == "Va":
                advantage = -10
            elif defender.attribute == "Da":
                advantage = 10

        power = attacker.power
        enemy_power = defender.power

        if is_player:
            power = attacker.get_power()
        else:
            advantage - attacker.handicap

        hit_rate = (power * 100) / (power + enemy_power) if (power + enemy_power) > 0 else 0
        hit_rate = max(0, min(hit_rate + advantage, 100))

        return random.randint(0, 99) < hit_rate