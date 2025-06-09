#=====================================================================
# BattleEncounter
#=====================================================================

from abc import abstractmethod
import random

import pygame
from core import game_globals, runtime_globals
from core.animation import PetFrame
from core.constants import *
from core.utils import blit_with_shadow, change_scene, distribute_pets_evenly, get_font, get_module, get_selected_pets, load_attack_sprites, sprite_load
from core.utils_unlocks import unlock_item

ENEMY_ENTRY_SPEED = 1
IDLE_ANIM_FRAME_DELAY = 5
IDLE_ANIM_DURATION = 90
ALERT_FRAME_DELAY = 10
BAR_HOLD_TIME_MS = 2500
AFTER_ATTACK_DELAY_FRAMES = 50
ALERT_DURATION_FRAMES = 50
LEVEL_DURATION_FRAMES = 60
WAIT_ATTACK_READY_FRAMES = 19

class BattleEncounter:
    

    def __init__(self, module):
        self.module = module
        self.phase = "level"
        self.frame_counter = 0
        self.enemies = []
        self.enemy_positions = []

        self.strength = 0
        self.bar_level = 14
        self.pet_anim_index = 0
        self.pet_anim_counter = 0
        self.backgroundIm = sprite_load(BATTLE_BACKGROUND_PATH)

        self.battle_sprite = sprite_load(BATTLE_SPRITE_PATH)
        self.level_sprite = sprite_load(BATTLE_LEVEL_SPRITE_PATH, size=(240, 240))
        self.bar_back = sprite_load(BAR_BACK_PATH, size=(30, 170))
        self.bar_piece = sprite_load(BAR_PIECE_PATH, size=(24, 12))
        self.training_max = sprite_load(TRAINING_MAX_PATH, size=(60, 60))

        self.ready_sprite = sprite_load(READY_SPRITE_PATH, scale=2.5)
        self.go_sprite = sprite_load(GO_SPRITE_PATH, scale=2.5)

        self.attacking_pets = []
        self.attacking_enemies = []
        self.attacking_pet = None
        self.attacking_enemy = None
        self.forward_distance = 0
        self.player_health = 4
        self.enemy_health = 4

        self.attack_jump = 0
        self.attack_forward = 0

        self.font = get_font(FONT_SIZE_LARGE)

        self.result_timer = 0
        self.result_sprites = {
            "clear": [sprite_load(CLEAR1_PATH), sprite_load(CLEAR2_PATH)],
            "warning": [sprite_load(WARNING1_PATH), sprite_load(WARNING2_PATH)]
        }

        self.attack_sprites = load_attack_sprites()

        self.hit_animation_frames = self.load_hit_animation()
        self.hit_animations = []

        self.load_enemies()

    def load_enemies(self):
        selected_pets = get_selected_pets()
        module = get_module(self.module)
        versions = []
        for p in selected_pets:
            if (p.version <= 0 or p.version >= 6) and self.module == "DMC":  # Special case for DMC
                versions.append(random.randint(1, 5))
            elif (p.version >= 6) and self.module == "PenC":
                versions.append(random.randint(0, 5))
            else:
                versions.append(p.version)
        
        self.enemies = module.get_enemies(game_globals.battle_area[self.module], game_globals.battle_round[self.module], versions)

        for enemy in self.enemies:
            if enemy:
                enemy.load_sprite(module.folder_path)
                x = -PET_WIDTH - 2
                self.enemy_positions.append([enemy, x])

    def load_hit_animation(self):
        sprite_sheet = sprite_load(HIT_ANIMATION_PATH)
        frames = []
        for i in range(12):  # 12 frames na horizontal
            frame = sprite_sheet.subsurface(pygame.Rect(i * 64, 0, 64, 64))
            frames.append(frame)
        return frames

    def update(self):
        self.update_pet_animation()
        self.frame_counter += 1
        if self.phase == "level":
            self.update_level()
        elif self.phase == "entry":
            self.update_entry()
        elif self.phase == "intimidate":
            self.update_intimidate()
        elif self.phase == "alert":
            self.update_alert()
        elif self.phase == "charge":
            self.update_charge()
        elif self.phase == "move_pair":
            self.move_pair()
        elif self.phase == "pet_charge":
            self.update_pet_charge()
        elif self.phase == "pet_attack":
            self.update_pet_attack()
        elif self.phase == "enemy_attack":
            self.update_enemy_attack()
        elif self.phase == "enemy_charge":
            self.update_enemy_charge()
        elif self.phase == "retreat":
            self.update_retreat()
        elif self.phase == "post_attack_delay":
            self.update_post_attack_delay()
        elif self.phase == "result":
            self.update_result()

        runtime_globals.game_message.update()

        for anim in self.hit_animations:
            anim[0] += self.frame_counter % 2  # Avança frame

        self.hit_animations = [a for a in self.hit_animations if a[0] < len(self.hit_animation_frames)]

    def update_level(self):
        if self.frame_counter >= LEVEL_DURATION_FRAMES:
            self.phase = "entry"
            self.frame_counter = 0
            runtime_globals.game_sound.play("battle")

    def update_entry(self):
        all_in_position = True
        for i, (enemy, x) in enumerate(self.enemy_positions):
            target_x = 2
            if x < target_x:
                x += ENEMY_ENTRY_SPEED
                all_in_position = False
            self.enemy_positions[i][1] = x

        if all_in_position:
            runtime_globals.game_console.log("Entering intimidate phase")
            self.phase = "intimidate"
            self.frame_counter = 0
            self.idle_anim_index = 0
            self.idle_anim_counter = 0

    def update_intimidate(self):
        if self.frame_counter >= IDLE_ANIM_DURATION:
            self.phase = "alert"
            self.frame_counter = 0

    @abstractmethod
    def update_alert(self):
        pass

    def update_charge(self):
        if pygame.time.get_ticks() - self.bar_timer > BAR_HOLD_TIME_MS:
            runtime_globals.game_console.log("Entering prepare_attack phase")
            self.phase = "prepare_attack"
            self.frame_counter = 0
            self.prepare_attacks()

    def prepare_attacks(self):
        """
        Prepara listas de ataque e escolhe o primeiro par para iniciar a sequência.
        """
        pets = get_selected_pets()
        enemies = [e for e in self.enemies if e is not None]

        # Preenche listas de ataque com cópias para não modificar as originais
        self.attacking_pets = pets[:]
        self.attacking_enemies = enemies[:]

        self.select_next_pair()

    def select_next_pair(self):
        """
        Seleciona o próximo par aleatório (pet, inimigo) para atacar. Muda para a fase de movimentação.
        """
        if not self.attacking_pets or not self.attacking_enemies:
            self.phase = "result"  # Encerrar se todos já atacaram
            self.frame_counter = 0
            return

        idx = random.randrange(len(self.attacking_pets))

        pet = self.attacking_pets[idx]
        enemy = self.attacking_enemies[idx]

        self.attacking_pet = pet
        self.attacking_enemy = enemy

        self.attacking_pets.remove(pet)
        self.attacking_enemies.remove(enemy)

        self.phase = "move_pair"
        runtime_globals.game_console.log("Entering move_pair phase")
        self.frame_counter = 0
        self.attack_offset = 0  # usado para animar o avanço

        runtime_globals.game_console.log(f"🔸 Pair selected: {pet.name} vs {enemy.name}")

    def move_pair(self):
        self.forward_distance += 1
        if self.frame_counter == 20:
            self.phase = "pet_charge"
            runtime_globals.game_console.log("Entering pet_attack phase")
            self.frame_counter = 0

    def update_pet_charge(self):
        if self.frame_counter <= 9:
            self.attack_forward += 1
            if self.frame_counter < 5:
                self.attack_jump += 1
            elif self.frame_counter > 5:
                self.attack_jump -= 1
        else:
            self.attack_forward -= 1

        if self.frame_counter >= WAIT_ATTACK_READY_FRAMES:
            self.phase = "pet_attack"
            self.frame_counter = 0

    def update_enemy_charge(self):
        if self.frame_counter <= 9:
            self.attack_forward += 1
            if self.frame_counter < 5:
                self.attack_jump += 1
            elif self.frame_counter > 5:
                self.attack_jump -= 1
        else:
            self.attack_forward -= 1

        if self.frame_counter >= WAIT_ATTACK_READY_FRAMES:
            self.phase = "enemy_attack"
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
            hits = 1 if self.strength <= 5 else 2 if self.strength <= 10 else 3
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

            # Define número de projéteis
            hits = random.randint(1, 3)
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
            if hasattr(self, "projectiles"):
                del self.projectiles
            del self.enemy_projectiles
            self.frame_counter = 0
            if self.enemy_hit:
                runtime_globals.game_sound.play("attack_hit")
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
            

    def update_retreat(self):
        self.forward_distance -= 1

        if self.forward_distance <= 0:
            self.forward_distance = 0
            self.attacking_pet = None
            self.attacking_enemy = None
            self.phase = "prepare_attack"
            runtime_globals.game_console.log("Entering prepare_attack phase")
            self.frame_counter = 0
            self.prepare_attacks()

    def update_post_attack_delay(self):
        if self.frame_counter >= AFTER_ATTACK_DELAY_FRAMES:
            if self.after_attack_phase == "enemy":
                self.phase = "enemy_charge"
                runtime_globals.game_console.log("Entering enemy_attack phase")
            elif self.after_attack_phase == "retreat":
                self.phase = "retreat"
                runtime_globals.game_console.log("Entering retreat phase")
            self.frame_counter = 0

    def update_pet_animation(self):
        self.pet_anim_counter += 1
        if self.pet_anim_counter >= 10:
            self.pet_anim_index = 1 - self.pet_anim_index
            self.pet_anim_counter = 0

    def update_result(self):
        self.result_timer += 1
        #is_last_round = game_globals.battle_round == ROUND_LIMITS.get(globals.battle_area, 3)

        if self.result_timer < 30:
            # pisca aviso clear
            return

        if self.enemy_health == 0:
            runtime_globals.game_sound.play("happy")
            game_globals.battle_round[self.module] += 1
            max_round = ROUND_LIMITS[self.module].get(game_globals.battle_area[self.module], 3)
            if game_globals.battle_round[self.module] > max_round:
                game_globals.battle_round[self.module] = 1
                game_globals.battle_area[self.module] += 1
                unlock_item("DMC", "backgrounds", "the_grid")
                if game_globals.battle_area[self.module] > 4:
                    unlock_item("DMC", "backgrounds", "dmc_logo")
                if game_globals.battle_area[self.module] > 8:
                    game_globals.battle_area[self.module] = 1
                    unlock_item("DMC", "backgrounds", "box_art")

        else:
            runtime_globals.game_sound.play("fail")
            # perdeu
            game_globals.battle_round[self.module] = 1

        self.return_to_main_scene()

    def draw(self, surface: pygame.Surface):
        self.draw_health_bars(surface)
        surface.blit(self.backgroundIm, (0,0))
        if self.phase in ["entry", "intimidate", "alert", "charge", "move_pair", "pet_attack", "pet_charge", "enemy_attack", "enemy_charge", "retreat", "post_attack_delay"]:
            if self.phase == "intimidate" and self.frame_counter >= IDLE_ANIM_DURATION // 2:
                is_last_round = False
                if self.module:
                    is_last_round = game_globals.battle_round[self.module] == ROUND_LIMITS[self.module].get(game_globals.battle_area[self.module], 3)
                if is_last_round:
                    sprite = self.result_sprites["warning"][(self.frame_counter // 10) % 2]
                    surface.blit(sprite, (0, 0))
                else:
                    surface.blit(self.battle_sprite, (0, 0))
            else:
                self.draw_enemies(surface)
                self.draw_pets(surface)
                runtime_globals.game_message.draw(surface)

                for frame_index, (x, y) in self.hit_animations:
                    if 0 <= frame_index < len(self.hit_animation_frames):
                        sprite = self.hit_animation_frames[frame_index]
                        blit_with_shadow(surface, sprite, (x - sprite.get_width() // 2, y - 32))
        
        elif self.phase == "result":
            is_last_round = False
            if self.module:
                is_last_round = game_globals.battle_round[self.module] == ROUND_LIMITS[self.module].get(game_globals.battle_area[self.module], 3)
            if self.enemy_health == 0 and is_last_round:
                sprites = self.result_sprites["clear"]
                sprite = sprites[(self.result_timer // 10) % 2]
                surface.blit(sprite, (0, 0))

        if self.phase == "pet_attack":
            self.draw_projectiles(surface)
        if self.phase == "enemy_attack":
            self.draw_enemy_projectiles(surface)

        if self.phase == "level" and self.module:
            surface.blit(self.level_sprite, (0, 0))
            level_text = self.font.render(f"Round {game_globals.battle_round[self.module]}", True, FONT_COLOR_GREEN).convert_alpha()
            blit_with_shadow(surface, level_text, (6, 116))

    def draw_enemies(self, surface: pygame.Surface):
        total = len(self.enemy_positions)
        for i, (enemy, x) in enumerate(self.enemy_positions):
            y = self.get_y(i, total)
            anim_toggle = (self.frame_counter + i * 5) // 15 % 2  # Varia com o índice

            if self.phase == "enemy_attack" and enemy == self.attacking_enemy:
                frame_id = PetFrame.ATK1.value
            elif self.phase == "enemy_charge" and enemy == self.attacking_enemy:
                frame_id = PetFrame.ATK2.value
            elif self.enemy_health <= 0:
                frame_id = PetFrame.ANGRY.value
            elif self.phase in ["move_pair", "retreat", "post_attack_delay", "alert", "charge", "enemy_attack"]:
                frame_id = PetFrame.IDLE1.value if anim_toggle == 0 else PetFrame.IDLE2.value
            elif self.phase in ["intimidate", "entry"]:
                frame_id = PetFrame.IDLE1.value if anim_toggle == 0 else PetFrame.ANGRY.value
            else:
                frame_id = PetFrame.IDLE1.value

            sprite = enemy.get_sprite(frame_id)

            if enemy == self.attacking_enemy:
                x += self.forward_distance

            if self.phase == "enemy_charge" and enemy == self.attacking_enemy:
                y -= self.attack_jump
                x -= self.attack_forward

            if sprite:
                sprite = pygame.transform.flip(sprite, True, False)
                blit_with_shadow(surface, sprite, (x + 1, y))

    def draw_pets(self, surface: pygame.Surface):
        pets = get_selected_pets()
        total = len(pets)

        for i, pet in enumerate(pets):
            anim_toggle = (self.frame_counter + i * 5) // 15 % 2

            if self.phase in ["alert"]:
                frame_id = PetFrame.ANGRY.value
            elif self.enemy_health <= 0:
                frame_id = PetFrame.HAPPY.value
            elif self.player_health <= 0:
                frame_id = PetFrame.LOSE.value
            elif self.phase == "pet_attack" and pet == self.attacking_pet:
                frame_id = PetFrame.ATK1.value
            elif self.phase == "pet_charge" and pet == self.attacking_pet:
                frame_id = PetFrame.ATK2.value
            else:
                frame_id = PetFrame.IDLE1.value if anim_toggle == 0 else PetFrame.IDLE2.value

            sprite = runtime_globals.pet_sprites[pet][frame_id]
            sprite = pygame.transform.scale(sprite, (PET_WIDTH, PET_HEIGHT))
            x = SCREEN_WIDTH - PET_WIDTH - 2

            if pet == self.attacking_pet:
                x -= self.forward_distance

            y = self.get_y(i, total)
            if self.phase == "pet_charge" and pet == self.attacking_pet:
                y -= self.attack_jump
                x += self.attack_forward
            blit_with_shadow(surface, sprite, (x, y))

    def draw_projectiles(self, surface):
        if hasattr(self, "projectiles"):
            for sprite, (x, y) in self.projectiles:
                blit_with_shadow(surface, sprite, (x, y))

    def draw_enemy_projectiles(self, surface):
        if hasattr(self, "enemy_projectiles"):
            for sprite, (x, y) in self.enemy_projectiles:
                blit_with_shadow(surface, sprite, (x, y))

    def draw_strength_bar(self, surface):
        bar_x = (SCREEN_WIDTH // 2) - (self.bar_back.get_width() // 2)
        bar_bottom_y = SCREEN_HEIGHT - 2

        if self.strength == 14:
            surface.blit(self.training_max, (bar_x - 18, bar_bottom_y - 209))

        blit_with_shadow(surface, self.bar_back, (bar_x - 3, bar_bottom_y - 169))

        for i in range(self.strength):
            y = bar_bottom_y - (i + 1) * self.bar_piece.get_height()
            surface.blit(self.bar_piece, (bar_x, y))

    def draw_health_bars(self, surface):
        max_health = 4 if self.module == "DMC" else 3
        section_width = 64 / max_health
        bar_height = 17

        # Cores
        red = (181, 41, 41)
        green = (0, 255, 108)

        # Player bar (lado direito → centro)
        start_x_player = 144
        for i in range(max_health):
            x = start_x_player + i * section_width
            pygame.draw.rect(surface, red, (x, 6, section_width, bar_height))
            if i >= (max_health - self.player_health):
                pygame.draw.rect(surface, green, (x, 6, section_width, bar_height))

        # Enemy bar (lado esquerdo → centro)
        start_x_enemy = 93
        for i in range(max_health):
            x = start_x_enemy - (i + 1) * section_width
            pygame.draw.rect(surface, red, (x, 6, section_width, bar_height))
            if i >= (max_health - self.enemy_health):
                pygame.draw.rect(surface, green, (x, 6, section_width, bar_height))

    def get_y(self, index, total):
        spacing = min((SCREEN_HEIGHT - 30) // total, PET_HEIGHT)
        total_height = spacing * total
        offset = (SCREEN_HEIGHT - total_height) // 2
        return offset + index * spacing

    def handle_event(self, input_action):
        if self.phase == "charge" and input_action == "A":
            runtime_globals.game_sound.play("menu")
            self.strength = min(self.strength + 1, self.bar_level)


    def return_to_main_scene(self):
        player_won = self.enemy_health == 0
        for pet in get_selected_pets():
            pet.finish_battle(player_won)

        runtime_globals.game_console.log(f"[Scene_Battle] exiting to main game")
        distribute_pets_evenly()
        change_scene("game")

    def check_hit(self, attacker, defender, is_player=False) -> bool:
        advantage = 0
        if attacker.attribute == "Va":
            if defender.attribute == "Da":
                advantage = -5
            elif defender.attribute == "Vi":
                advantage = 5
        elif attacker.attribute == "Da":
            if defender.attribute == "Va":
                advantage = 5
            elif defender.attribute == "Vi":
                advantage = -5
        elif attacker.attribute == "Vi":
            if defender.attribute == "Va":
                advantage = -5
            elif defender.attribute == "Da":
                advantage = 5


        power = attacker.power
        enemy_power = defender.power

        if is_player:
            power = attacker.get_power()

        hit_rate = (power * 100) / (power + enemy_power) if (power + enemy_power) > 0 else 0
        hit_rate = max(0, min(hit_rate + advantage, 100))

        return random.randint(0, 99) < hit_rate
