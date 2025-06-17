#=====================================================================
# BattleEncounter
#=====================================================================

import random
import pygame
from components.window_xai import WindowXai
from components.window_xaibar import WindowXaiBar
from core import game_globals, runtime_globals
from core.animation import PetFrame
from core.combat.combat_constants import (
    AFTER_ATTACK_DELAY_FRAMES, ALERT_DURATION_FRAMES, BAR_HOLD_TIME_MS, ENEMY_ENTRY_SPEED,
    IDLE_ANIM_DURATION, LEVEL_DURATION_FRAMES, READY_FRAME_COUNTER, WAIT_ATTACK_READY_FRAMES
)
from core.constants import *
from core.game_module import sprite_load
from core.utils.module_utils import get_module
from core.utils.pet_utils import distribute_pets_evenly, get_battle_targets
from core.utils.pygame_utils import blit_with_shadow, get_font, load_attack_sprites, sprite_load_percent
from core.utils.scene_utils import change_scene
from core.utils.utils_unlocks import unlock_item
from core.utils import inventory_utils

#=====================================================================
# BattleEncounter Class
#=====================================================================

class BattleEncounter:
    """
    Handles the logic and rendering for a battle encounter.
    """

    #========================
    # Region: Setup & State
    #========================

    def __init__(self, module, area=0, round=0, version=1):
        """
        Initializes the BattleEncounter, loading graphics and setting initial state.
        """
        self.module = get_module(module)
        self.set_initial_state(area, round, version)

        # Graphics and assets (keep in __init__)
        self.backgroundIm = sprite_load_percent(BATTLE_BACKGROUND_PATH, percent=100, keep_proportion=True, base_on="width")
        self.battle_sprite = sprite_load_percent(BATTLE_SPRITE_PATH, percent=100, keep_proportion=True, base_on="width")
        self.level_sprite = sprite_load_percent(BATTLE_LEVEL_SPRITE_PATH, percent=100, keep_proportion=True, base_on="width")
        self.bar_piece = sprite_load_percent(BAR_PIECE_PATH, percent=(int(12 * UI_SCALE) / SCREEN_HEIGHT) * 100, keep_proportion=True, base_on="height")
        self.bar_back = sprite_load_percent(BAR_BACK_PATH, percent=(int(170 * UI_SCALE) / SCREEN_HEIGHT) * 100, keep_proportion=True, base_on="height")
        self.training_max = sprite_load_percent(TRAINING_MAX_PATH, percent=(int(60 * UI_SCALE) / SCREEN_HEIGHT) * 100, keep_proportion=True, base_on="height")
        self.ready_sprite = sprite_load_percent(READY_SPRITE_PATH, percent=100, keep_proportion=True, base_on="width")
        self.go_sprite = sprite_load_percent(GO_SPRITE_PATH, percent=100, keep_proportion=True, base_on="width")

        self.font = get_font(FONT_SIZE_LARGE)
        self.result_sprites = {
            "clear": [
                sprite_load_percent(CLEAR1_PATH, percent=100, keep_proportion=True, base_on="width"),
                sprite_load_percent(CLEAR2_PATH, percent=100, keep_proportion=True, base_on="width")
            ],
            "warning": [
                sprite_load_percent(WARNING1_PATH, percent=100, keep_proportion=True, base_on="width"),
                sprite_load_percent(WARNING2_PATH, percent=100, keep_proportion=True, base_on="width")
            ]
        }
        self.ready_sprites = {
            1: sprite_load_percent(READY_SPRITES_PATHS[1], 100, keep_proportion=True, base_on="width"),
            2: sprite_load_percent(READY_SPRITES_PATHS[2], 100, keep_proportion=True, base_on="width"),
            3: sprite_load_percent(READY_SPRITES_PATHS[3], 100, keep_proportion=True, base_on="width")
        }
        self.count_sprites = {
            4: sprite_load_percent(COUNT_SPRITES_PATHS[4], 100, keep_proportion=True, base_on="width"),
            3: sprite_load_percent(COUNT_SPRITES_PATHS[3], 100, keep_proportion=True, base_on="width"),
            2: sprite_load_percent(COUNT_SPRITES_PATHS[2], 100, keep_proportion=True, base_on="width"),
            1: sprite_load_percent(COUNT_SPRITES_PATHS[1], 100, keep_proportion=True, base_on="width")
        }
        self.mega_hit = sprite_load_percent(MEGA_HIT_PATH, 100, keep_proportion=True, base_on="width")
        self.attack_sprites = load_attack_sprites()
        self.hit_animation_frames = self.load_hit_animation()
        self.hit_animations = []

    def set_initial_state(self, area=0, round=0, version=1):
        """
        Set all non-graphic variables for (re)initialization.
        """
        # --- Jumper Gate: skip to boss if status_boost is active ---
        if (
            "skip_to_boss" in game_globals.battle_effects
            and game_globals.battle_effects["skip_to_boss"].get("amount", 0) > 0
        ):
            # Find the next boss round for this area
            current_area = game_globals.battle_area[self.module.name] if area == 0 else area
            round_to_check = game_globals.battle_round[self.module.name] if round == 0 else round
            # Only skip if not already at boss
            while not self.module.is_boss(current_area, round_to_check, version):
                round_to_check += 1
            # Use local variables for area and round
            area = current_area
            round = round_to_check  # Set round to boss round

        self.phase = "level"
        self.frame_counter = 0
        self.enemies = []
        self.enemy_positions = []

        # Use self.area and self.round, not the global values
        self.area = area if area != 0 else game_globals.battle_area[self.module.name]
        self.round = round if round != 0 else game_globals.battle_round[self.module.name]

        self.boss = self.module.is_boss(self.area, self.round, version)

        self.strength = 0
        self.bar_level = 14
        self.pet_anim_index = 0
        self.pet_anim_counter = 0

        self.attacking_pets = []
        self.attacking_enemies = []
        self.attacking_pet = None
        self.attacking_enemy = None
        self.forward_distance = 0

        # --- Apply HP boost from status_boost items if present ---
        hp_boost = 0
        if "hp" in game_globals.battle_effects:
            hp_boost = game_globals.battle_effects["hp"].get("amount", 0)
            runtime_globals.game_console.log(f"[BattleEncounter] HP boost applied: +{hp_boost}")

        if self.module.battle_global_hit_points > 0:
            base_hp = self.module.battle_global_hit_points
            self.player_health = base_hp + hp_boost
            self.enemy_health = base_hp
            self.player_max_health = base_hp + hp_boost
            self.enemy_max_health = base_hp
        else:
            base_hp = sum(p.get_hp() for p in get_battle_targets())
            num_pets = len(get_battle_targets())
            self.player_health = base_hp + (hp_boost * num_pets if hp_boost else 0)
            self.player_max_health = self.player_health

        # --- Apply Attack boost from status_boost items (DMX ruleset) ---
        attack_boost = 0
        if self.module.ruleset == "dmx" and "attack" in game_globals.battle_effects:
            num_pets = len(get_battle_targets())
            attack_boost = game_globals.battle_effects["attack"].get("amount", 0) * num_pets if num_pets else 0
            runtime_globals.game_console.log(f"[BattleEncounter] Attack boost applied: +{attack_boost}")

        self.player_attack = (
            sum(p.get_attack() for p in get_battle_targets()) + attack_boost
            if get_battle_targets() else 1
        )

        # --- Apply Strength boost from status_boost items (PW Board) ---
        self.strength_bonus = 0
        if "strength" in game_globals.battle_effects:
            self.strength_bonus = game_globals.battle_effects["strength"].get("amount", 0)
            runtime_globals.game_console.log(f"[BattleEncounter] Strength boost applied: +{self.strength_bonus}")

        # --- Apply XAI roll boost (Seven Switch) ---
        if "xai_roll" in game_globals.battle_effects:
            xai_val = game_globals.battle_effects["xai_roll"].get("amount", None)
            if xai_val is not None:
                runtime_globals.game_console.log(f"[BattleEncounter] XAI roll boost applied: {xai_val}")

        # --- Apply EXP multiplier boost (EXP Coat) ---
        if "exp_multiplier" in game_globals.battle_effects:
            exp_val = game_globals.battle_effects["exp_multiplier"].get("amount", None)
            if exp_val is not None:
                runtime_globals.game_console.log(f"[BattleEncounter] EXP multiplier boost applied: x{exp_val}")

        # --- Apply Jumper Gate boost ---
        if "skip_to_boss" in game_globals.battle_effects:
            skip_val = game_globals.battle_effects["skip_to_boss"].get("amount", None)
            if skip_val:
                runtime_globals.game_console.log(f"[BattleEncounter] Jumper Gate: Skipping to boss round.")

        self.xai_phase = 0
        self.xai_number = 1
        self.window_xai = None
        self.window_xaibar = None

        self.attack_jump = 0
        self.attack_forward = 0

        self.result_timer = 0
        self.press_counter = 0
        self.final_color = 3
        self.correct_color = 0
        self.super_hits = 0
        self.super_hit_damage = False

        self.load_enemies()

    def load_enemies(self):
        """
        Loads enemy data for the current area and round, sets up enemy positions and health.
        """
        selected_pets = get_battle_targets()
        version_range = self.module.get_enemy_versions(self.area, self.round)
        versions = []
        for p in selected_pets:
            if not version_range:
                versions.append(p.version)
            elif p.version not in version_range:
                versions.append(random.choice(version_range))
            else:
                versions.append(p.version)

        self.enemies = self.module.get_enemies(self.area, self.round, versions)

        for enemy in self.enemies:
            if enemy:
                enemy.load_sprite(self.module.folder_path)
                x = -PET_WIDTH + (2 * UI_SCALE)
                self.enemy_positions.append([enemy, x])

        if self.module.battle_global_hit_points == 0:
            self.enemy_health = sum(getattr(e, "hp", 4) for e in self.enemies if e)
            self.enemy_max_health = self.enemy_health
        self.enemy_attack = sum(ATK_LEVEL[e.stage] for e in self.enemies if e) if self.enemies else 1

    def load_hit_animation(self):
        """
        Loads the hit animation sprite sheet and splits it into frames.
        """
        sprite_sheet = sprite_load(HIT_ANIMATION_PATH, (PET_WIDTH * 12, PET_HEIGHT))
        frames = []
        for i in range(12):
            frame = sprite_sheet.subsurface(pygame.Rect(i * PET_WIDTH, 0, PET_WIDTH, PET_HEIGHT))
            frames.append(frame)
        return frames

    #========================
    # Region: Update Methods
    #========================

    def update(self):
        """
        Main update loop for the battle encounter, calls phase-specific updates.
        """
        self.update_pet_animation()
        self.frame_counter += 1
        if self.phase == "level":
            self.update_level()
        elif self.phase == "entry":
            self.update_entry()
        elif self.phase == "intimidate":
            self.update_intimidate()
        elif self.phase == "set_attribute":
            self.update_set_attribute()
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

        advance_every = max(1, int(FRAME_RATE // 15))
        if self.frame_counter % advance_every == 0:
            for anim in self.hit_animations:
                anim[0] += 1  # Advance one frame

        self.hit_animations = [a for a in self.hit_animations if a[0] < len(self.hit_animation_frames)]

    def update_level(self):
        """
        Update logic for the level phase, transitions to entry phase after duration.
        """
        if self.frame_counter >= LEVEL_DURATION_FRAMES:
            self.phase = "entry"
            self.frame_counter = 0
            runtime_globals.game_sound.play("battle")

    def update_entry(self):
        """
        Update logic for the enemy entry phase, moves enemies into position.
        """
        all_in_position = True
        for i, (enemy, x) in enumerate(self.enemy_positions):
            target_x = 2 * (SCREEN_WIDTH / 240)
            if x < target_x:
                x += ENEMY_ENTRY_SPEED * (30 / FRAME_RATE)  # Frame-rate independent speed
                all_in_position = False
            self.enemy_positions[i][1] = x

        if all_in_position:
            runtime_globals.game_console.log("Entering intimidate phase")
            self.phase = "intimidate"
            self.frame_counter = 0
            self.idle_anim_index = 0
            self.idle_anim_counter = 0

    def update_intimidate(self):
        """
        Update logic for the intimidate phase, transitions to set_attribute or alert phase.
        """
        if self.frame_counter >= IDLE_ANIM_DURATION:
            self.phase = "set_attribute" if self.module.ruleset == "penc" else "alert"
            self.frame_counter = 0

    def update_set_attribute(self):
        """
        Update logic for setting pet attributes, transitions to alert phase.
        """
        self.frame_counter += 1
        if self.frame_counter >= int(READY_FRAME_COUNTER):
            self.phase = "alert"
            self.frame_counter = 0

    def update_alert(self):
        """
        Update logic for the alert phase, prepares for charge phase after duration.
        """
        if self.frame_counter == int(ALERT_DURATION_FRAMES * 0.8):
            runtime_globals.game_sound.play("happy")
        if self.frame_counter > ALERT_DURATION_FRAMES:
            runtime_globals.game_console.log("Entering charge phase")
            self.phase = "charge"
            self.frame_counter = 0
            self.bar_timer = pygame.time.get_ticks()
            self.setup_charge()

    def setup_charge(self):
        """
        Setup logic for the charge phase, varies by ruleset.
        """
        if self.module.ruleset == "dmc":
            self.strength = 0
            self.bar_level = 14
            self.pet_anim_index = 0
            self.pet_anim_counter = 0
        elif self.module.ruleset == "dmx":
            self.xai_phase = 1  # Start Xai roll
            self.window_xai = WindowXai(
                x=SCREEN_WIDTH // 2 - int(100 * UI_SCALE) // 2,
                y=SCREEN_HEIGHT // 2 - int(100 * UI_SCALE) // 2,
                width=int(100 * UI_SCALE),
                height=int(100 * UI_SCALE),
                xai_number=1
            )
            self.window_xai.roll()
        elif self.module.ruleset == "penc":
            self.press_counter = 0
            self.rotation_index = 3

    def update_charge(self):
        """
        Update logic for the charge phase, handles input and transitions to prepare_attack phase.
        """
        if self.module.ruleset == "dmx":
            if self.xai_phase == 1:
                self.window_xai.update()
                if not self.window_xai.rolling and not self.window_xai.stopping:
                    self.xai_phase = 2
                    self.window_xaibar = WindowXaiBar(
                        x=SCREEN_WIDTH // 2 - int(152 * UI_SCALE) // 2,
                        y=SCREEN_HEIGHT // 2 - int(72 * UI_SCALE) // 2 + int(48 * UI_SCALE),
                        xai_number=self.xai_number,
                        pet=self.attacking_pet if hasattr(self, "attacking_pet") and self.attacking_pet else get_battle_targets()[0]
                    )
                    self.window_xaibar.start()
            elif self.xai_phase == 2:
                self.window_xaibar.update()
        if self.module.ruleset != "dmx" or self.xai_phase == 3:
            if pygame.time.get_ticks() - self.bar_timer > BAR_HOLD_TIME_MS:
                runtime_globals.game_console.log("Entering prepare_attack phase")
                self.phase = "prepare_attack"
                self.frame_counter = 0
                if self.module.ruleset == "penc":
                    self.calculate_results()
                self.prepare_attacks()

    def calculate_results(self):
        """
        Calculate the result of the charge based on player input and pet attributes.
        """
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

    def get_first_pet_attribute(self):
        """
        Get the attribute of the first pet, used for determining attack color in charge phase.
        """
        pet = get_battle_targets()[0]
        if pet.attribute in ["", "Vi"]:
            return 1
        elif pet.attribute == "Va":
            return 2
        elif pet.attribute == "Da":
            return 3
        return 1
    
    def prepare_attacks(self):
        """
        Prepara listas de ataque e escolhe o primeiro par para iniciar a sequência.
        """
        pets = get_battle_targets()
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
        """
        Animates the movement of the attacking pair (pet and enemy) towards each other.
        """
        self.forward_distance += 1 * (30 / FRAME_RATE)
        if self.frame_counter >= int(20 * (FRAME_RATE / 30)):
            self.phase = "pet_charge"
            runtime_globals.game_console.log("Entering pet_attack phase")
            self.frame_counter = 0

    def update_pet_charge(self):
        """
        Update logic for the pet charge phase, animates the pet charging towards the enemy.
        """
        if self.frame_counter <= 9 * int(FRAME_RATE / 30):
            self.attack_forward += 1 * (30 / FRAME_RATE)
            if self.frame_counter < 5 * int(FRAME_RATE / 30):
                self.attack_jump += 1 * (30 / FRAME_RATE)
            elif self.frame_counter > 5 * int(FRAME_RATE / 30):
                self.attack_jump -= 1 * (30 / FRAME_RATE)
        else:
            self.attack_forward -= 1 * (30 / FRAME_RATE)

        if self.frame_counter >= WAIT_ATTACK_READY_FRAMES:
            self.phase = "pet_attack"
            self.frame_counter = 0

    def update_enemy_charge(self):
        """
        Update logic for the enemy charge phase, animates the enemy charging towards the pet.
        """
        if self.frame_counter <= 10 * int(FRAME_RATE / 30):
            self.attack_forward += 1 * (30 / FRAME_RATE)
            if self.frame_counter < 5 * int(FRAME_RATE / 30):
                self.attack_jump += 1 * (30 / FRAME_RATE)
            elif self.frame_counter > 5 * int(FRAME_RATE / 30):
                self.attack_jump -= 1 * (30 / FRAME_RATE)
        else:
            self.attack_forward -= 1 * (30 / FRAME_RATE)

        if self.frame_counter >= WAIT_ATTACK_READY_FRAMES:
            self.phase = "enemy_attack"
            self.frame_counter = 0

    def update_pet_attack(self):
        """
        Update logic for the pet attack phase, handles pet projectile creation and movement.
        """
        if not hasattr(self, "projectiles"):
            # Início do ataque: define os projéteis com base na força
            if self.attacking_pet.atk_alt > 0 and random.random() < 0.3:
                atk_id = str(self.attacking_pet.atk_alt)
            else:
                atk_id = str(self.attacking_pet.atk_main)
            atk_sprite = self.attack_sprites.get(atk_id)

            # Determina número de ataques com base na força
            hits = self.get_player_hits()
            pet_index = get_battle_targets().index(self.attacking_pet)
            y = self.get_y(pet_index, len(get_battle_targets())) + atk_sprite.get_height() // 2

            self.projectiles = []
            x = SCREEN_WIDTH - PET_WIDTH - (2 * UI_SCALE ) - int(self.forward_distance * UI_SCALE)
            
            self.projectiles.append([atk_sprite.copy(), [x, y]])

            if hits > 1:
                self.projectiles.append([atk_sprite.copy(), [x - (20 * UI_SCALE), y - (10 * UI_SCALE)]])
            if hits == 3:
                self.projectiles.append([atk_sprite.copy(), [x - (40 * UI_SCALE), y + (10 * UI_SCALE)]])

            # Calcula se o ataque acerta ANTES de mover os projéteis
            self.attack_hit = self.check_hit(self.attacking_pet, self.attacking_enemy, is_player=True)
            runtime_globals.game_sound.play("attack")

        # Move os projéteis
        done = True
        for sprite_data in self.projectiles:
            sprite, (x, y) = sprite_data
            x -= 4 * UI_SCALE * (30 / FRAME_RATE)  # Frame-rate independent speed
            sprite_data[1][0] = x
            enemy_index = get_battle_targets().index(self.attacking_pet)
            target_x = self.enemy_positions[enemy_index][1] + PET_WIDTH
            if x > target_x:
                done = False

        if done:
            del self.projectiles
            self.frame_counter = 0
            if self.attack_hit:
                runtime_globals.game_sound.play("attack_hit")
                self.damage_enemy()

                enemy_index = get_battle_targets().index(self.attacking_pet)
                enemy_y = self.get_y(enemy_index, len(get_battle_targets()))
                enemy_x = self.enemy_positions[enemy_index][1] + PET_WIDTH // 2
                self.hit_animations.append([0, [enemy_x + int(self.forward_distance * UI_SCALE), enemy_y + (16 * UI_SCALE)]])
            else:
                runtime_globals.game_sound.play("attack_fail")
                enemy_index = get_battle_targets().index(self.attacking_pet)
                enemy_y = self.get_y(enemy_index, len(get_battle_targets()))
                enemy_x = self.enemy_positions[enemy_index][1]
                runtime_globals.game_message.add("MISS", (enemy_x + (16 * UI_SCALE), enemy_y - (10 * UI_SCALE)), (255, 0, 0))

            if self.enemy_health <= 0 or self.player_health <= 0:
                self.phase = "result"
                runtime_globals.game_console.log("Entering result phase")
            else:
                self.phase = "post_attack_delay"
                self.after_attack_phase = "enemy"
                runtime_globals.game_console.log("Entering post_attack_delay phase")

    def get_player_hits(self):
        """
        Determines the number of hits for the player's attack based on the current ruleset.
        """
        if self.module.ruleset == "dmc":
            return 1 if self.strength <= 5 else 2 if self.strength <= 10 else 3
        elif self.module.ruleset == "dmx":
            return 1 if self.window_xaibar.selected_strength <= 1 else self.window_xaibar.selected_strength
        elif self.module.ruleset == "penc":
            if self.super_hits == 5 and random.random() < 0.8:
                hits = 3
                self.super_hit_damage = True
            elif self.super_hits > 2 and random.random() < 0.5:
                hits = 2
            else:
                hits = 1
            return hits
    
    def get_enemy_hits(self):
        """
        Determines the number of hits for the enemy's attack, can trigger super hit.
        """
        if random.random() < 0.15:
            hits = 3
            if self.module.ruleset == "penc":
                self.super_hit_damage = True
        elif random.random() < 0.6:
            hits = 2
        else:
            hits = 1
        return hits
    
    def damage_player(self):
        """
        Applies damage to the player based on the enemy's attack power.
        """
        if self.module.ruleset == "dmx":
            self.player_health = max(0, self.player_health - self.enemy_attack)
        elif self.module.ruleset == "penc" and self.super_hit_damage:
            self.player_health = max(0, self.player_health - 2)
            self.super_hit_damage = 0
        else:
            self.player_health = max(0, self.player_health - 1)
    
    def damage_enemy(self):
        """
        Applies damage to the enemy based on the player's attack power.
        """
        if self.module.ruleset == "dmx":
            self.enemy_health = max(0, self.enemy_health - self.player_attack)
        elif self.module.ruleset == "penc" and self.super_hit_damage:
            self.enemy_health = max(0, self.enemy_health - 2)
            self.super_hit_damage = 0
        else:
            self.enemy_health = max(0, self.enemy_health - 1)

    def update_enemy_attack(self):
        """
        Update logic for the enemy attack phase, handles enemy projectile creation and movement.
        """
        if not hasattr(self, "enemy_projectiles"):
            # Início do ataque inimigo
            if self.attacking_enemy.atk_alt > 0 and random.random() < 0.3:
                atk_id = str(self.attacking_enemy.atk_alt)
            else:
                atk_id = str(self.attacking_enemy.atk_main)
            atk_sprite = self.attack_sprites.get(atk_id)
            atk_sprite = pygame.transform.flip(atk_sprite, True, False)

            # Define número de projéteis
            hits = self.get_enemy_hits()
            enemy_index = self.enemies.index(self.attacking_enemy)
            y = self.get_y(enemy_index, len(self.enemies)) + atk_sprite.get_height() // 2
            x = self.enemy_positions[enemy_index][1] + PET_WIDTH

            self.enemy_projectiles = []

            self.enemy_projectiles.append([atk_sprite.copy(), [x, y]])

            if hits > 1:
                self.enemy_projectiles.append([atk_sprite.copy(), [x + (20 * UI_SCALE), y + (10 * UI_SCALE)]])
            if hits == 3:
                self.enemy_projectiles.append([atk_sprite.copy(), [x + (40 * UI_SCALE), y - (10 * UI_SCALE)]])

            self.enemy_hit = self.check_hit(self.attacking_enemy, self.attacking_pet, is_player=False)
            runtime_globals.game_sound.play("attack")

        # Move os projéteis
        done = True
        for sprite_data in self.enemy_projectiles:
            sprite, (x, y) = sprite_data
            x += 4 * UI_SCALE * (30 / FRAME_RATE)  # Frame-rate independent speed
            sprite_data[1][0] = x
            pet_index = get_battle_targets().index(self.attacking_pet)
            target_x = SCREEN_WIDTH - PET_WIDTH - (2 * UI_SCALE) - int(self.forward_distance * UI_SCALE)
            if x < target_x:
                done = False

        if done:
            if hasattr(self, "projectiles"):
                del self.projectiles
            del self.enemy_projectiles
            self.frame_counter = 0
            if self.enemy_hit:
                runtime_globals.game_sound.play("attack_hit")
                self.damage_player()

                pet_index = get_battle_targets().index(self.attacking_pet)
                pet_y = self.get_y(pet_index, len(get_battle_targets()))
                pet_x = SCREEN_WIDTH - PET_WIDTH - (2 * UI_SCALE) - int(self.forward_distance * UI_SCALE) + PET_WIDTH // 2
                self.hit_animations.append([0, [pet_x, pet_y + (24 * UI_SCALE)]])
            else:
                runtime_globals.game_sound.play("attack_fail")
                pet_index = get_battle_targets().index(self.attacking_pet)
                pet_y = self.get_y(pet_index, len(get_battle_targets()))
                pet_x = SCREEN_WIDTH - PET_WIDTH - (2 * UI_SCALE) - int(self.forward_distance * UI_SCALE)
                runtime_globals.game_message.add("MISS", (pet_x + (16 * UI_SCALE), pet_y - (10 * UI_SCALE)), (255, 0, 0))

            if self.enemy_health <= 0 or self.player_health <= 0:
                self.phase = "result"
                runtime_globals.game_console.log("Entering result phase")
            else:
                self.phase = "post_attack_delay"
                self.after_attack_phase = "retreat"
                runtime_globals.game_console.log("Entering post_attack_delay phase")
            

    def update_retreat(self):
        """
        Update logic for the retreat phase, animates the pet retreating after attack.
        """
        # Retreat movement should be frame-rate independent
        self.forward_distance -= 1 * (30 / FRAME_RATE)

        if self.forward_distance <= 0:
            self.forward_distance = 0
            self.attack_jump = 0
            self.attack_forward = 0
            self.attacking_pet = None
            self.attacking_enemy = None
            self.phase = "prepare_attack"
            runtime_globals.game_console.log("Entering prepare_attack phase")
            self.frame_counter = 0
            self.prepare_attacks()

    def update_post_attack_delay(self):
        """
        Update logic for the post-attack delay phase, transitions to enemy_charge or retreat phase.
        """
        # Wait for a fixed time after attack, frame-rate independent
        if self.frame_counter >= AFTER_ATTACK_DELAY_FRAMES:
            if self.after_attack_phase == "enemy":
                self.phase = "enemy_charge"
                runtime_globals.game_console.log("Entering enemy_attack phase")
            elif self.after_attack_phase == "retreat":
                self.phase = "retreat"
                runtime_globals.game_console.log("Entering retreat phase")
            self.frame_counter = 0

    def update_pet_animation(self):
        """
        Update logic for pet animation, switches animation frames.
        """
        # Animation frame switch, frame-rate independent
        self.pet_anim_counter += 1
        if self.pet_anim_counter >= int(10 * (FRAME_RATE / 30)):
            self.pet_anim_index = 1 - self.pet_anim_index
            self.pet_anim_counter = 0

    def update_result(self):
        """
        Update logic for the result phase, handles victory or defeat actions.
        """
        # Result timer, frame-rate independent
        self.result_timer += 1

        if self.result_timer < int(30 * (FRAME_RATE / 30)):
            # pisca aviso clear
            return

        if self.enemy_health == 0:
            runtime_globals.game_sound.play("happy")
            if not self.boss:
                self.round += 1
                if self.round > game_globals.battle_round[self.module.name]:
                    game_globals.battle_round[self.module.name] = self.round

                if self.module.battle_sequential_rounds:
                    self.set_initial_state(round=self.round, area=self.area)
                    return
            else:
                # --- Unlock adventure items of the area just won ---
                unlocks = getattr(self.module, "unlocks", None)
                if isinstance(unlocks, list):
                    for unlock in unlocks:
                        if unlock.get("type") == "adventure" and unlock.get("area") == self.area:
                            unlock_item(self.module.name, "adventure", unlock["name"])

                # --- Award item prize if enemy has a valid prize ---
                # Only when player clears an area (boss defeated)
                if self.enemies:
                    prize_enemies = [e for e in self.enemies if hasattr(e, "prize") and e.prize]
                    if prize_enemies:
                        enemy = random.choice(prize_enemies)
                        prize_name = getattr(enemy, "prize", None)
                        if prize_name and hasattr(self.module, "items") and self.module.items:
                            # Find item by name in module's items
                            for item in self.module.items.values():
                                if item.name == prize_name:
                                    inventory_utils.add_to_inventory(item.id, 1)
                                    runtime_globals.game_console.log(f"Received item: {item.name}")
                                    break

                self.area += 1
                self.round = 1

                if self.module.area_exists(self.area):
                    game_globals.battle_round[self.module.name] = self.round
                    game_globals.battle_area[self.module.name] = self.area
        else:
            runtime_globals.game_sound.play("fail")
            # perdeu
            game_globals.battle_round[self.module.name] = 1

        self.return_to_main_scene()

    def load_next_round(self):
        """
        Prepares the next round by resetting health and loading new enemies.
        """
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

    def draw(self, surface: pygame.Surface):
        """
        Main draw loop for the battle encounter, calls phase-specific draws.
        """
        self.draw_health_bars(surface)
        surface.blit(self.backgroundIm, (0, 0))

        # Draw by phase
        if self.phase == "level":
            self.draw_level(surface)
        elif self.phase == "entry":
            self.draw_entry(surface)
        elif self.phase == "intimidate":
            self.draw_intimidate(surface)
        elif self.phase == "set_attribute":
            self.draw_set_attribute(surface)
        elif self.phase == "alert":
            self.draw_alert(surface)
        elif self.phase == "charge":
            self.draw_charge(surface)
        elif self.phase == "move_pair":
            self.draw_move_pair(surface)
        elif self.phase == "pet_charge":
            self.draw_pet_charge(surface)
        elif self.phase == "pet_attack":
            self.draw_pet_attack(surface)
        elif self.phase == "enemy_attack":
            self.draw_enemy_attack(surface)
        elif self.phase == "enemy_charge":
            self.draw_enemy_charge(surface)
        elif self.phase == "retreat":
            self.draw_retreat(surface)
        elif self.phase == "post_attack_delay":
            self.draw_post_attack_delay(surface)
        elif self.phase == "result":
            self.draw_result(surface)

    def draw_level(self, surface):
        """
        Draws the level information on the screen.
        """
        surface.blit(self.level_sprite, (0, SCREEN_HEIGHT // 2 - self.level_sprite.get_height() // 2))
        level_text = self.font.render(f"Round {self.round}", True, FONT_COLOR_GREEN).convert_alpha()
        blit_with_shadow(surface, level_text, (6 * UI_SCALE, 116 * UI_SCALE))

    def draw_entry(self, surface):
        """
        Draws the entry phase, showing enemies and pets in their starting positions.
        """
        self.draw_enemies(surface)
        self.draw_pets(surface)
        runtime_globals.game_message.draw(surface)
        self.draw_hit_animations(surface)

    def draw_intimidate(self, surface):
        """
        Draws the intimidate phase, showing warning or battle sprites.
        """
        if self.frame_counter >= IDLE_ANIM_DURATION // 2:
            if self.boss:
                sprite = self.result_sprites["warning"][(self.frame_counter // int(10 * FRAME_RATE / 30)) % 2]
                surface.blit(sprite, (0, SCREEN_HEIGHT // 2 - sprite.get_height() // 2))
            else:
                surface.blit(self.battle_sprite, (0, SCREEN_HEIGHT // 2 - self.battle_sprite.get_height() // 2))
        else:
            self.draw_enemies(surface)
            self.draw_pets(surface)
            runtime_globals.game_message.draw(surface)
            self.draw_hit_animations(surface)

    def draw_set_attribute(self, surface):
        """
        Draws the attribute selection for the pet, indicating readiness to attack.
        """
        attr = self.get_first_pet_attribute()
        sprite = self.ready_sprites[attr]
        y = (SCREEN_HEIGHT - sprite.get_height()) // 2
        surface.blit(sprite, (0, y))

    def draw_alert(self, surface):
        """
        Draws the alert phase, showing readiness sprites or count down.
        """
        if self.module.ruleset == "penc":
            sprite = self.count_sprites[4]
            y = (SCREEN_HEIGHT - sprite.get_height()) // 2
            surface.blit(sprite, (0, y))
        else:
            center_y = SCREEN_HEIGHT // 2 - self.ready_sprite.get_height() // 2
            surface.blit(self.ready_sprite, (0, center_y))

    def draw_charge(self, surface):
        """
        Draws the charge phase, showing strength bar or Xai roll.
        """
        self.draw_enemies(surface)
        self.draw_pets(surface)
        if self.module.ruleset == "dmc":
            self.draw_strength_bar(surface)
        elif self.module.ruleset == "penc":
            sprite = self.count_sprites[self.rotation_index]
            y = (SCREEN_HEIGHT - sprite.get_height()) // 2
            surface.blit(sprite, (0, y))
        elif self.module.ruleset == "dmx":
            if self.xai_phase == 1:
                self.window_xai.draw(surface)
            elif self.xai_phase >= 2:
                self.window_xaibar.draw(surface)

    def draw_move_pair(self, surface):
        """
        Draws the moving pair (pet and enemy) during their attack approach.
        """
        self.draw_enemies(surface)
        self.draw_pets(surface)

    def draw_pet_charge(self, surface):
        """
        Draws the pet charge animation towards the enemy.
        """
        self.draw_enemies(surface)
        self.draw_pets(surface)

    def draw_pet_attack(self, surface):
        """
        Draws the pet attack animation, including projectiles and hit effects.
        """
        self.draw_enemies(surface)
        self.draw_pets(surface)
        runtime_globals.game_message.draw(surface)
        self.draw_hit_animations(surface)
        self.draw_projectiles(surface)

    def draw_enemy_attack(self, surface):
        """
        Draws the enemy attack animation, including projectiles and hit effects.
        """
        self.draw_enemies(surface)
        self.draw_pets(surface)
        runtime_globals.game_message.draw(surface)
        self.draw_hit_animations(surface)
        self.draw_enemy_projectiles(surface)

    def draw_enemy_charge(self, surface):
        """
        Draws the enemy charge animation towards the pet.
        """
        self.draw_enemies(surface)
        self.draw_pets(surface)

    def draw_retreat(self, surface):
        """
        Draws the retreating animation of the pet after an attack.
        """
        self.draw_enemies(surface)
        self.draw_pets(surface)

    def draw_post_attack_delay(self, surface):
        """
        Draws the post-attack delay phase, showing any hit animations.
        """
        self.draw_enemies(surface)
        self.draw_pets(surface)
        runtime_globals.game_message.draw(surface)
        self.draw_hit_animations(surface)

    def draw_result(self, surface):
        """
        Draws the result of the battle, showing clear or warning sprites.
        """
        if self.enemy_health == 0 and self.boss:
            sprites = self.result_sprites["clear"]
            sprite = sprites[(self.result_timer // (10 * int(FRAME_RATE / 30))) % 2]
            surface.blit(sprite, (0, SCREEN_HEIGHT // 2 - sprite.get_height() // 2))

    def draw_hit_animations(self, surface):
        """
        Draws the hit animations at the impact points of attacks.
        """
        for frame_index, (x, y) in self.hit_animations:
            if 0 <= frame_index < len(self.hit_animation_frames):
                sprite = self.hit_animation_frames[frame_index]
                blit_with_shadow(surface, sprite, (x - sprite.get_width() // 2, y - 32))

    def draw_enemies(self, surface: pygame.Surface):
        """
        Draws the enemy sprites on the screen, with animations based on the battle phase.
        """
        total = len(self.enemy_positions)
        anim_frames = 10 * (FRAME_RATE / 30)

        for i, (enemy, x) in enumerate(self.enemy_positions):
            y = self.get_y(i, total)
            anim_toggle = (self.frame_counter + i * 5) // (15 * FRAME_RATE/30) % 2  # Varia com o índice

            if self.phase == "enemy_attack" and enemy == self.attacking_enemy:
                if self.frame_counter <= anim_frames:
                    frame_id = PetFrame.ATK2.value
                else:
                    frame_id = PetFrame.ATK1.value
            elif self.phase == "enemy_charge" and enemy == self.attacking_enemy:
                if self.frame_counter > WAIT_ATTACK_READY_FRAMES - anim_frames:
                    frame_id = PetFrame.ATK2.value
                else:
                    frame_id = PetFrame.ATK1.value
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
                x += int(self.forward_distance * UI_SCALE)

            if self.phase == "enemy_charge" and enemy == self.attacking_enemy:
                y -= int(self.attack_jump * UI_SCALE)
                x -= int(self.attack_forward * UI_SCALE)

            if sprite:
                sprite = pygame.transform.flip(sprite, True, False)
                blit_with_shadow(surface, sprite, (x + (2 * UI_SCALE), y))

    def draw_pets(self, surface: pygame.Surface):
        """
        Draws the player pets on the screen, with animations based on the battle phase.
        """
        pets = get_battle_targets()
        total = len(pets)

        anim_frames = 10 * (FRAME_RATE / 30)

        for i, pet in enumerate(pets):
            anim_toggle = (self.frame_counter + i * 5) // (15 * FRAME_RATE/30) % 2

            if self.phase in ["alert"]:
                frame_id = PetFrame.ANGRY.value
            elif self.enemy_health <= 0:
                frame_id = PetFrame.HAPPY.value
            elif self.player_health <= 0:
                frame_id = PetFrame.LOSE.value
            elif self.phase == "pet_attack" and pet == self.attacking_pet:
                if self.frame_counter <= anim_frames:
                    frame_id = PetFrame.ATK2.value
                else:
                    frame_id = PetFrame.ATK1.value
                frame_id = PetFrame.ATK1.value
            elif self.phase == "pet_charge" and pet == self.attacking_pet:
                if self.frame_counter > WAIT_ATTACK_READY_FRAMES - anim_frames:
                    frame_id = PetFrame.ATK2.value
                else:
                    frame_id = PetFrame.ATK1.value
            else:
                frame_id = PetFrame.IDLE1.value if anim_toggle == 0 else PetFrame.IDLE2.value

            sprite = runtime_globals.pet_sprites[pet][frame_id]
            sprite = pygame.transform.scale(sprite, (PET_WIDTH, PET_HEIGHT))
            x = SCREEN_WIDTH - PET_WIDTH - (2 * UI_SCALE)

            if pet == self.attacking_pet:
                x -= int(self.forward_distance * UI_SCALE)

            y = self.get_y(i, total)
            if self.phase == "pet_charge" and pet == self.attacking_pet:
                y -= int(self.attack_jump * UI_SCALE)
                x += int(self.attack_forward * UI_SCALE)
            blit_with_shadow(surface, sprite, (x, y))

    def draw_projectiles(self, surface):
        """
        Draws the projectiles fired by the player's pets during their attack.
        """
        if hasattr(self, "projectiles"):
            for sprite, (x, y) in self.projectiles:
                blit_with_shadow(surface, sprite, (x, y))

    def draw_enemy_projectiles(self, surface):
        """
        Draws the projectiles fired by the enemies during their attack.
        """
        if hasattr(self, "enemy_projectiles"):
            for sprite, (x, y) in self.enemy_projectiles:
                blit_with_shadow(surface, sprite, (x, y))

    def draw_strength_bar(self, surface):
        """
        Draws the strength training bar for the DMC ruleset.
        """
        bar_x = (SCREEN_WIDTH // 2) - (self.bar_back.get_width() // 2)
        bar_bottom_y = SCREEN_HEIGHT - int(2 * UI_SCALE)

        if self.strength == 14:
            surface.blit(self.training_max, (bar_x - int(18 * UI_SCALE), bar_bottom_y - int(209 * UI_SCALE)))

        blit_with_shadow(surface, self.bar_back, (bar_x - int(3 * UI_SCALE), bar_bottom_y - int(169 * UI_SCALE)))

        for i in range(self.strength):
            y = bar_bottom_y - (i + 1) * self.bar_piece.get_height()
            surface.blit(self.bar_piece, (bar_x, y))

    def draw_health_bars(self, surface):
        """
        Draws the health bars for the player and enemy, showing current and max health.
        """
        max_player_health = self.player_max_health 
        max_enemy_health = self.enemy_max_health

        width_scale = SCREEN_WIDTH / 240
        section_width_player = int(67 * width_scale / max_player_health)
        section_width_enemy = int(67 * width_scale / max_enemy_health)
        bar_height = int(18 * width_scale) 

        # Cores
        red = (181, 41, 41)
        green = (0, 255, 108)

        # Player bar (lado direito → centro)
        start_x_player = SCREEN_WIDTH - int(96 * width_scale)
        for i in range(max_player_health):
            x = start_x_player + i * section_width_player
            pygame.draw.rect(surface, red, (x, int(6 * width_scale), section_width_player, bar_height))
            if i >= (max_player_health - self.player_health):
                pygame.draw.rect(surface, green, (x, int(6 * width_scale), section_width_player, bar_height))

        # Enemy bar (lado esquerdo → centro)
        start_x_enemy = int(96 * width_scale)
        for i in range(max_enemy_health):
            x = start_x_enemy - (i + 1) * section_width_enemy
            pygame.draw.rect(surface, red, (x, 6 * width_scale, section_width_enemy, bar_height))
            if i >= (max_enemy_health - self.enemy_health):
                pygame.draw.rect(surface, green, (x, 6 * width_scale, section_width_enemy, bar_height))

    def get_y(self, index, total):
        """
        Calculates the vertical position for drawing based on index and total number of sprites.
        """
        spacing = min((SCREEN_HEIGHT - int(30 * UI_SCALE)) // total, int(PET_HEIGHT * UI_SCALE))
        total_height = spacing * total
        offset = (SCREEN_HEIGHT - total_height) // 2
        return offset + index * spacing

    #========================
    # Region: Event Handling
    #========================

    def handle_event(self, input_action):
        """
        Handles input events for the battle encounter, phase and ruleset specific.
        """
        if self.module.ruleset == 'dmc':
            if self.phase == "charge":
                if input_action == "A":
                    runtime_globals.game_sound.play("menu")
                    self.strength = min(self.strength + 1, self.bar_level)
        elif self.module.ruleset == 'dmx':
            if self.phase == "charge":
                if self.xai_phase == 1 and input_action == "A":
                    # --- Seven Switch: force XAI roll to 7 if status_boost is active ---
                    if (
                        "xai_roll" in game_globals.battle_effects
                        and game_globals.battle_effects["xai_roll"].get("amount", 0) == 7
                    ):
                        self.window_xai.stop()
                        self.xai_number = 7
                        self.window_xai.current_frame = 6  # 0-based index for 7
                    else:
                        self.window_xai.stop()
                        self.xai_number = self.window_xai.current_frame + 1
                elif self.xai_phase == 2 and input_action == "A":
                    self.window_xaibar.stop()
                    self.strength = self.window_xaibar.selected_strength or 1
                    self.xai_phase = 3
                    self.bar_timer = pygame.time.get_ticks()
        elif self.module.ruleset == 'penc':
            if input_action == "Y" or input_action == "SHAKE":
                if self.phase == "alert":
                    self.frame_counter = ALERT_DURATION_FRAMES
                elif self.phase == "charge":
                    self.press_counter += 1
                    if self.press_counter % 2 == 0:
                        self.rotation_index -= 1
                        if self.rotation_index < 1:
                            self.rotation_index = 3

    #========================
    # Region: Utility Methods
    #========================

    def return_to_main_scene(self):
        """
        Ends the battle and returns to the main game scene.
        """
        player_won = self.enemy_health == 0
        for i, pet in enumerate(get_battle_targets()):
            # Pass xp_multiplier=1 by default, or use exp_multiplier boost if present
            exp_multiplier = 1
            if "exp_multiplier" in game_globals.battle_effects:
                exp_multiplier = game_globals.battle_effects["exp_multiplier"].get("amount", 1)
            pet.finish_battle(player_won, self.enemies[i], self.area, self.round, exp_multiplier)

        # --- Reduce boost_time for all status_boost effects and remove expired ones ---
        to_remove = []
        for status, effect in game_globals.battle_effects.items():
            if "boost_time" in effect:
                effect["boost_time"] -= 1
                if effect["boost_time"] <= 0:
                    to_remove.append(status)
        if to_remove:
            runtime_globals.game_console.log(f"[BattleEncounter] Removing expired boosts: {', '.join(to_remove)}")
        for status in to_remove:
            del game_globals.battle_effects[status]

        runtime_globals.game_console.log(f"[Scene_Battle] exiting to main game")
        distribute_pets_evenly()
        change_scene("game")

    def check_hit(self, attacker, defender, is_player=False) -> bool:
        """
        Calculates if an attack hits, considering attributes and power.
        """
        advantage = 0
        if attacker.attribute == "Va":
            if defender.attribute == "Da":
                advantage = -1 * self.module.battle_atribute_advantage
            elif defender.attribute == "Vi":
                advantage = self.module.battle_atribute_advantage
        elif attacker.attribute == "Da":
            if defender.attribute == "Va":
                advantage = self.module.battle_atribute_advantage
            elif defender.attribute == "Vi":
                advantage = -1 * self.module.battle_atribute_advantage
        elif attacker.attribute == "Vi":
            if defender.attribute == "Va":
                advantage = -1 * self.module.battle_atribute_advantage
            elif defender.attribute == "Da":
                advantage = self.module.battle_atribute_advantage

        # --- Apply strength bonus to get_power if present (only for pets) ---
        if is_player and hasattr(attacker, "get_power"):
            power = attacker.get_power(self.strength_bonus) if hasattr(self, "strength_bonus") and self.strength_bonus else attacker.get_power()
        else:
            power = getattr(attacker, "power", 1)

        enemy_power = getattr(defender, "power", 1)

        if not is_player:
            advantage -= getattr(attacker, "handicap", 0)

        hit_rate = (power * 100) / (power + enemy_power) if (power + enemy_power) > 0 else 0
        hit_rate = max(0, min(hit_rate + advantage, 100))

        return random.randint(0, 99) < hit_rate

# (Keep all other methods in their respective regions, with docstrings as needed.)
