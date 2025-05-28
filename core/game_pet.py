from abc import abstractmethod
from datetime import datetime, timedelta
import pygame
import random
import os

from core import game_globals, runtime_globals
from core.animation import Animation
from core.constants import *
from core.game_digidex import register_digidex_entry
from core.game_poop import GamePoop
from core.utils import change_scene, get_module, sprite_load


class GamePet:
    def __init__(self, pet_data, traited = False):
        self.hunger = self.strength = self.age = self.injuries = self.poop_count_flag = self.weight = 0
        self.totalWin = self.totalBattles = 0

        self.set_data(pet_data)
        self.reset_variables()
        self.load_sprite()
        self.begin_position()

        self.state = ""
        self.set_state("idle")
        
        self.age_timer = 0
        self.direction = -1
        self.food_type = -1
        self.injuries = 0
        self.move_timer = random.randint(60, 120)

        self.traited = traited
        self.shiny = False
        self.shook = False

        self.sleep_start_time = None
        self.sleep_timer = 0 
        self.back_to_sleep = 0

    def set_data(self, data):
        self.module = data["module"]
        self.name = data["name"]
        self.stage = data["stage"]
        self.version = data["version"]
        self.special = data["special"]
        if self.special:
            self.special_key = data.get("special_key")
        else:
            self.special_key = None
        self.evolve = data["evolve"]
        self.sleeps = data.get("sleeps")
        self.wakes = data.get("wakes")
        self.atk_main = data.get("atk_main", 0)
        self.atk_alt = data.get("atk_alt", 0)
        self.time = data.get("time", 0)
        self.poop_timer = data.get("poop_timer", 60)
        self.min_weight = data.get("min_weight")
        self.stomach = data.get("stomach")
        self.hunger_loss = data.get("hunger_loss")
        self.strength_loss = data.get("strength_loss")
        self.power = data.get("power")
        self.attribute = data.get("attribute")
        self.energy = data.get("energy")

    def reset_variables(self):
        self.timer = 0
        if self.weight < self.min_weight:
            self.weight = self.min_weight
        self.dp = self.energy
        self.effort = 0
        self.sick = 0
        self.win = self.battles = 0
        self.animation_counter = self.frame_counter = self.frame_index = 0
        self.care_food_mistake_timer = self.care_strength_mistake_timer = self.care_sleep_mistake_timer = self.care_sick_mistake_timer = 0

    def load_sprite(self):
        """Loads animation frames for the pet, replacing `$` in module paths."""
        runtime_globals.pet_sprites[self] = []
        
        module = get_module(self.module)
        folder = os.path.join(module.folder_path, "monsters", module.name_format.replace("$", self.name))

        for i in range(20):
            frame_file = os.path.join(folder, f"{i}.png")
            if not os.path.exists(frame_file):
                break
            
            runtime_globals.pet_sprites[self].append(sprite_load(frame_file, size=(PET_WIDTH, PET_HEIGHT)))

    def begin_position(self):
        self.subpixel_x = float(SCREEN_WIDTH - PET_WIDTH) / 2
        self.x = int(self.subpixel_x)
        self.y = 24 + (SCREEN_HEIGHT - PET_HEIGHT) // 2
        self.x_range = (0, SCREEN_WIDTH - PET_WIDTH)

    def get_sprite(self, index):
        return runtime_globals.pet_sprites[self][index]

    def set_state(self, new_state):
        if self.state == "dead":
            return

        if self.state != new_state:
            self.state = new_state
            self.animation_counter = 0
            self.animation_frames = getattr(Animation, new_state.upper(), Animation.IDLE)
            self.frame_index = self.frame_counter = self.animation_counter = 0
            runtime_globals.game_console.log(f"{self.name} status {self.state}")

            if self.state == "nap" and self.should_sleep() and new_state != "nap":
                self.set_back_to_sleep()

            # Handle sleeping
            if new_state == "nap":
                from datetime import datetime
                self.sleep_start_time = datetime.now()
                self.sleep_timer = 0
            elif self.state == "idle":
                self.sleep_start_time = None
                self.sleep_timer = 0

    def draw(self, surface):
        # Get base frame; skip if missing
        sprite_list = runtime_globals.pet_sprites.get(self)
        if not sprite_list:
            return
        
        frame_key = self.animation_frames[self.frame_index].value
        frame = sprite_list[frame_key]
        
        # Flip if facing right
        if self.direction == 1:
            frame = pygame.transform.flip(frame, True, False)
        
        # Draw base pet sprite
        surface.blit(frame, (self.x, self.y))
        
        # Determine overlay, if any
        overlay = None
        anim_phase = (self.animation_counter // 30) % 2  # precompute phase

        if self.state == "eat":
            idx = 0 if self.food_type == 0 else 4
            frame_index = idx + min(self.animation_counter // 30, 3)
            overlay = runtime_globals.feeding_frames[frame_index]
        elif self.state == "nap":
            overlay = runtime_globals.misc_sprites.get(f"Sleep{anim_phase + 1}")
        elif self.state in {"happy2", "happy3"} and anim_phase == 0:
            overlay = runtime_globals.misc_sprites.get("Cheer")
        elif self.sick > 0 and self.state != "dead":
            overlay = runtime_globals.misc_sprites.get(f"Sick{anim_phase + 1}")
        elif self.state == "angry":
            overlay = runtime_globals.misc_sprites.get(f"Mad{anim_phase + 1}")
        
        if overlay:
            base_pos = (self.x + PET_WIDTH, self.y)
            surface.blit(overlay, base_pos)
            
            if self.state == "happy3":
                # Draw additional overlay positions
                surface.blit(overlay, (self.x + PET_WIDTH, self.y + 24))
                surface.blit(overlay, (self.x - 24, self.y))
                surface.blit(overlay, (self.x - 24, self.y + 24))

    def update(self):
        self.timer += 1
        self.age_timer += 1
        self.update_animation()

        if self.state in ("moving", "idle"):
            self.update_idle_movement()
        elif self.state == "nap":
            self.sleep_timer += 1
            self.check_wake_up()
        elif self.state == "pooping":
            if self.frame_counter in [0,6]:
                self.x += 2
            elif self.frame_counter in [3,9]:
                self.x -= 2

            if self.animation_counter == 10:
                self.poop()
        elif self.state in ("moving", "idle") and self.timer % 15 == 0 and self.should_sleep():
            self.set_state("tired")

        # Increase age every day (30fps * 24 * 60 * 60 = 2,592,000 ticks)
        if self.age_timer % 2592000 == 0:
            self.age += 1
            runtime_globals.game_console.log(f"{self.name} aged to {self.age}")

        # Periodic updates every minute (30fps * 60 = 1,800 ticks)
        if self.timer % 1800 == 0:
            if self.state not in ("nap", "dead"):
                self.update_evolution()
                self.update_needs()
                self.update_pooping()
                self.update_care_mistakes()
            if self.state != "nap":
                self.update_death_check()
            
            if self.back_to_sleep > 0:
                self.back_to_sleep -= 1
                if self.back_to_sleep == 0 and self.state != "nap" and self.should_sleep():
                    self.set_state("nap")

    def update_idle_movement(self):
        if self.stage == 0 or self.state == "nap":
            return

        self.move_timer -= 1
        # Determine if we should move
        move_chance = (1 - IDLE_PROBABILITY)

        if self.move_timer <= 0:
            if self.state == "idle" and random.random() < 0.30:
                self.set_state("sick" if self.sick > 0 else ("happy" if not self.need_care() else "angry"))
                self.move_timer = random.randint(60, 120)
                return

            if random.random() < move_chance:
                self.set_state("moving")
                self.direction = random.choice([-1, 1])
                self.move_timer = random.randint(20, 60)
            else:
                self.set_state("idle")
                self.move_timer = random.randint(90, 180)

        # Move in sync with frame updates (choppy movement)
        if self.state == "moving" and self.frame_counter % 10 == 0:  # move only when animation frame updates
            step = random.choice([2, 6])
            self.x += step * self.direction
            if self.x <= self.x_range[0]:
                self.x = self.x_range[0]
                self.direction = 1
            elif self.x >= self.x_range[1]:
                self.x = self.x_range[1]
                self.direction = -1

    def update_animation(self):
        if not runtime_globals.pet_sprites[self]:
            return

        # Handle special 'nope' animation with direction flip
        if self.state == "nope" and self.timer % 30 == 0:
            self.direction *= -1

        # Choppy animation sync for movement
        if self.state == "moving":
            # Move every N frames, same as movement (e.g., every 15 frames)
            self.frame_counter += 1
            if self.frame_counter % 10 == 0:
                self.frame_index = (self.frame_index + 1) % len(self.animation_frames)
        else:
            # Regular animation update for non-moving states
            self.frame_counter += 1
            if self.frame_counter > 15:
                self.frame_counter = 0
                self.frame_index = (self.frame_index + 1) % len(self.animation_frames)

        # Handle timed state resets
        self.animation_counter += 1
        if self.state not in ("moving", "idle", "nap", "dead"):
            if self.state != "nap" and self.animation_counter > 119:
                self.set_state("happy" if self.food_type == 1 or (self.food_type == 0 and self.overfeed_timer == 0) else "idle")
                self.food_type = -1

        # Handle hatching animation
        if self.stage == 0 and self.timer >= 1750:
            self.set_state("hatch")

    def evolve_to(self, name, version):
        runtime_globals.game_console.log(f"Evolving to {name}")
        runtime_globals.game_sound.play("evolution")
        module = get_module(self.module)
        pet_data = module.get_monster(name, version)
        pet_data["module"] = module.name
        self.set_data(pet_data)
        self.reset_variables()
        self.load_sprite()
        self.set_state("happy1")
        register_digidex_entry(self.name, module.name, self.version)

    def force_poop(self):
        self.set_state("pooping")

    def poop(self):
        runtime_globals.game_sound.play("cancel")
        game_globals.poop_list.append(GamePoop(12 + self.x + (FRAME_SIZE // 2), self.y + (PET_HEIGHT-24)))
        if self.weight > self.min_weight:
            self.weight -= 1
        self.set_state("idle")

    def check_death_conditions(self):
        if self.state in ["nap", "dead"]:
            return False

        result = False

        # 1. 15 ou mais ferimentos em uma forma
        if self.injuries >= get_module(self.module).death_max_injuries:
            result = True

        # 2. Ficou ferido por 6h contínuas (sem curar)
        if self.care_sick_mistake_timer > get_module(self.module).death_sick_timer:
            result = True

        # 3. Fome OU força vazia por 12h contínuas
        if self.care_food_mistake_timer > get_module(self.module).death_hunger_timer or self.care_strength_mistake_timer > get_module(self.module).death_strength_timer:
            result = True

        # 4. Stage IV ou V + 5+ erros após fim do tempo de evolução
        if self.stage in [4, 5] and self.mistakes >= get_module(self.module).death_stage45_mistake:
            if self.timer > self.time * 60 * 30:
                result = True

        # 5. Stage VI ou VI+ + 5+ erros após 48h
        if self.stage >= 6 and self.mistakes >= get_module(self.module).death_stage67_mistake:
            if self.age_timer >= 48 * 60 * 60 * 30:
                result = True

        return result

    def update_death_check(self):
        """Checks pet death conditions and updates the sprite accordingly."""
        if self.check_death_conditions():
            self.set_state("dead")
            runtime_globals.game_sound.play("death")

            # 🔹 Load dead frame with sprite_load()
            dead_sprite = sprite_load(DEAD_FRAME_PATH, size=(PET_WIDTH, PET_HEIGHT))
            runtime_globals.pet_sprites[self][0] = dead_sprite
            runtime_globals.pet_sprites[self][1] = dead_sprite

            self.timer = 0

        # 🔥 Remove pet from game if dead for too long
        if self.state == "dead" and self.timer > 9000:
            if self in game_globals.pet_list:
                game_globals.pet_list.remove(self)
                del runtime_globals.pet_sprites[self]

            self.set_traited_egg()

            # 🔹 If no pets remain, reset to egg scene
            if not game_globals.pet_list:
                change_scene("egg")

    @abstractmethod
    def set_traited_egg(self):
        pass

    @abstractmethod
    def set_eating(self):
        pass

    @abstractmethod
    def set_sick(self):
        pass

    @abstractmethod
    def update_evolution(self):
        pass

    @abstractmethod
    def update_needs(self):
        pass

    @abstractmethod
    def update_pooping(self):
        pass

    @abstractmethod
    def update_care_mistakes(self):
        pass
    
    @abstractmethod
    def need_care(self):
        pass

    @abstractmethod
    def get_power(self):
        pass

    @abstractmethod
    def can_battle(self):
        pass

    @abstractmethod
    def can_train(self):
        pass

    @abstractmethod
    def set_back_to_sleep(self):
        pass

    @abstractmethod
    def check_disturbed_sleep(self):
        pass

    @abstractmethod
    def finish_training(self, won = False):
        pass

    def should_sleep(self):
        if not self.sleeps or not self.wakes:
            return False

        try:
            now_time = datetime.now().time()

            # Cache parsing whenever sleeps/wakes change
            if not hasattr(self, '_cached_sleep_time') or self._last_sleeps != self.sleeps or self._last_wakes != self.wakes:
                self._cached_sleep_time = datetime.strptime(self.sleeps.strip(), "%H:%M").time()
                self._cached_wake_time = datetime.strptime(self.wakes.strip(), "%H:%M").time()
                self._last_sleeps = self.sleeps
                self._last_wakes = self.wakes

            sleep_time = self._cached_sleep_time
            wake_time = self._cached_wake_time

            if sleep_time < wake_time:
                return sleep_time <= now_time < wake_time
            else:
                return now_time >= sleep_time or now_time < wake_time

        except Exception as e:
            runtime_globals.game_console.log(f"[!] Error parsing sleep range: {e}")
            return False


    def check_wake_up(self):
        now = datetime.now()

        if not hasattr(self, 'sleep_start_time'):
            return

        try:
            # Cache parsing if sleeps/wakes change
            if not hasattr(self, '_cached_wake_time') or self._last_wakes != self.wakes:
                self._cached_wake_time = datetime.strptime(self.wakes.strip(), "%H:%M").time()
                self._last_wakes = self.wakes

            wake_time = self._cached_wake_time

            # Wake up if it's the wake time exactly (match hour and minute)
            if now.hour == wake_time.hour and now.minute == wake_time.minute:
                slept_seconds = (now - self.sleep_start_time).total_seconds()
                slept_hours = int(slept_seconds // 3600)

                if slept_hours >= SLEEP_RECOVERY_HOURS:
                    self.dp = self.energy
                    runtime_globals.game_console.log(f"{self.name} slept {slept_hours}h and recovered DP!")

                self.set_state("idle")
                runtime_globals.game_console.log(f"{self.name} woke up naturally at {wake_time.strftime('%H:%M')}")

        except Exception as e:
            runtime_globals.game_console.log(f"[!] Error parsing wake time: {e}")




    def __getstate__(self):
        if self.state not in ("dead", "idle", "moving", "hatch"):
            self.state = "idle"
            self.food_type = -1
            self.animation_counter = 0
        state = self.__dict__.copy()
        state.pop("frames", None)
        return state
    
    def __setstate__(self, state):
        self.__dict__.update(state)
        if self.state not in ("dead", "idle", "moving", "hatch", "nap"):
            self.set_state("idle")
            self.food_type = -1
            self.animation_counter = 0
        self.load_sprite()
        if self.state == "dead":
            runtime_globals.pet_sprites[self][0] = pygame.image.load(DEAD_FRAME_PATH).convert_alpha()
            runtime_globals.pet_sprites[self][0] = pygame.transform.scale(runtime_globals.pet_sprites[self][0], (PET_WIDTH, PET_HEIGHT))
            runtime_globals.pet_sprites[self][1] = runtime_globals.pet_sprites[self][0]
        
