import random
from core import game_globals, runtime_globals
from core.constants import *
from core.game_pet import GamePet
from core.game_poop import GamePoop
from core.utils import get_module
from core.utils_unlocks import is_unlocked


class GamePetPenC(GamePet):
    def __init__(self, pet_data, traited = False):
        super().__init__(pet_data, traited)

    def set_data(self, data):
        super().set_data(data)

        self.atk_alt = self.atk_main
        self.condition_hearts_max = int(data.get("condition_hearts"))
        self.jogress_avaliable = int(data.get("jogress_avaliable"))
    

    def load_sprite(self):
        """
        Loads the sprite frames and swaps TRAIN1<->ATK1 and TRAIN2<->ATK2
        to match the consistent order used in GamePetDmC modules.
        """
        super().load_sprite()

        sprites = runtime_globals.pet_sprites[self]
        if len(sprites) > 6:
            sprites[4], sprites[5] = sprites[5], sprites[4]  # TRAIN1 ↔ TRAIN2
            sprites[5], sprites[6] = sprites[6], sprites[5]  # ATK1 ↔ ATK2
        runtime_globals.pet_sprites[self] = sprites

    def reset_variables(self):
        super().reset_variables()
        self.starvation_counter = 0
        self.condition_hearts = self.condition_hearts_max
        self.disturbance_penalty = 0
        self.overfeed_timer = 0
        self.protein_overdose = 0
        self.shake_counter = -1

    def update_evolution(self):
        if self.stage > 5:
            return
        
        if (self.stage < 4 and (self.timer / 30) < (self.time * 60)) or self.need_care():
            return
        
        if (self.stage == 4 and self.timer > 3888000) or (self.stage == 5 and self.timer > 5184000):
            return
        
        for evo in self.evolve:
            def in_range(val, r): return r[0] <= val <= r[1]
            if (
                ("jogress" in evo) or
                ("condition_hearts" in evo and not in_range(self.condition_hearts, evo["condition_hearts"])) or
                ("training" in evo and not in_range(self.effort/4, evo["training"])) or
                ("overfeed" in evo and not in_range(self.overfeed, evo["overfeed"])) or
                ("sleep_disturbances" in evo and not in_range(self.sleep_disturbances, evo["sleep_disturbances"])) or
                ("battles" in evo and not in_range(self.battles, evo["battles"])) or
                ("win_ratio" in evo and self.battles and not in_range((self.win * 100) // self.battles, evo["win_ratio"]))
            ):
                continue

            if self.stage > 0:
                module = get_module(self.module)
                pet_data = module.get_monster(evo["to"], self.version)

                if pet_data.get("special", False):
                    special_key = pet_data.get("special_key")
                    if special_key and not is_unlocked(self.module, "evolutions", special_key):
                        runtime_globals.game_console.log(f"{self.name} cannot evolve into {evo['to']}—special evolution {special_key} is locked.")
                        continue  # Skip this evolution
                    else:
                        runtime_globals.game_console.log("Special evolution check pass")


            if self.stage == 0 and self.shake_counter >= 99:
                self.shook = True
            self.evolve_to(evo["to"], evo.get("version", self.version))
            break

    def update_needs(self):
        if self.timer % (self.hunger_loss  * 60 * 30) == 0 and self.overfeed_timer == 0:
            if self.hunger > 0:
                self.hunger -= 1
            else:
                self.starvation_counter += 1
        if self.timer % (self.strength_loss * 60 * 30) == 0 and self.strength > 0:
            if self.strength > 4:
                self.strength = 4
            else:
                self.strength -= 1
        if self.overfeed_timer > 0:
            self.overfeed_timer -= 1

    def set_eating(self):
        if self.food_type < 0 or self.state == "nap": return
        self.animation_counter = 0
        self.direction = 1

        if self.food_type == 0:
            if self.hunger == self.stomach:
                self.set_state("nope")
                self.food_type = -1
                runtime_globals.game_console.log(f"{self.name} is full. Overfeed Timer {self.overfeed_timer}")
            else:
                self.set_state("eat")
                self.hunger += get_module(self.module).meat_hunger_gain
                if self.stage > 1 and self.weight < 99:
                    self.weight += get_module(self.module).meat_weight_gain
                self.starvation_counter = 0
                if self.hunger == 4:
                    self.overfeed_timer = get_module(self.module).overfeed_timer
                runtime_globals.game_console.log(f"{self.name} ate protein. Hunger {self.hunger}")
        else:
            self.set_state("eat")
            self.strength += get_module(self.module).protein_strengh_gain
            if self.stage > 1 and self.weight < 99:
                self.weight += get_module(self.module).protein_weight_gain
            self.protein_overdose += 1
            if self.dp < self.energy and self.protein_overdose % 4 == 0:
                self.dp += get_module(self.module).protein_dp_gain
            runtime_globals.game_console.log(f"{self.name} ate vitamin. Strength {self.strength}")
        
        if self.weight >= 99:
            self.set_sick()
            runtime_globals.game_console.log(f"{self.name} has reached 99GB and got sick!")


    def update_pooping(self):
        if self.stage <= 0 or self.timer < 1800: return
        if len(game_globals.poop_list) >= (len(game_globals.pet_list) * 8) and self.stage >= 2:
            if self.poop_count_flag == 0:
                self.poop_count_flag = 1
                self.set_sick()
                runtime_globals.game_console.log(f"[!] Care sick of poop ({len(game_globals.poop_list)})! Injuries: {self.injuries}")
        else:
            self.poop_count_flag = 0
            
        depletion_rate = 1
        if self.stage >= 6 and self.age_timer >= 48 * 60 * 60 * 30:
            depletion_rate = 2  # Accelerate depletion after 48 hours

        if self.timer % (self.poop_timer * 60 * 30 // depletion_rate) == 0:
            self.set_state("pooping")

    def check_death_conditions(self):
        result = super().check_death_conditions

        result = False
        if self.starvation_counter > get_module(self.module).death_starvation_count:
            result = True

        if result:
            if self.shake_counter == -1:
                self.shake_counter = 50
                return False
            elif self.shake_counter > 0:
                return True
            else:
                self.shake_counter = -1

        return False

    def set_traited_egg(self):
        win_ratio = (self.win * 100) // self.battles if self.battles > 0 else 0

        if self.stage >= 6 and self.age_timer >= 48 * 60 * 60 * 30:
            if win_ratio >= 60:
                key = f"{self.module}@{self.version}"
                if key not in game_globals.traited:
                    game_globals.traited.append(key)
                    runtime_globals.game_console.log(f"Traited Egg granted for {self.name}!")

    def update_care_mistakes(self):
        #hunger call
        sound_alert = False
        if self.hunger == 0:
            self.care_food_mistake_timer += 1
            if self.care_food_mistake_timer == get_module(self.module).meat_care_mistake_time:
                if self.condition_hearts > 0:
                    self.condition_hearts -= 1
                sound_alert = True
                runtime_globals.game_console.log(f"[!] Care mistake (hunger)! Remaining Condition Hearts: {self.condition_hearts}")
        
        #strength call
        if self.strength == 0:
            self.care_strength_mistake_timer += 1
            if self.care_strength_mistake_timer == get_module(self.module).protein_care_mistake_time:
                if self.condition_hearts > 0:
                    self.condition_hearts -= 1
                sound_alert = True
                runtime_globals.game_console.log(f"[!] Care mistake (strength)! Remaining Condition Hearts: {self.condition_hearts}")
        
        #sick call
        if self.sick > 0:
            self.care_sick_mistake_timer += 1
        else:
            self.care_sick_mistake_timer = 0

        #sleep call
        if self.should_sleep() and self.care_sleep_mistake_timer < get_module(self.module).sleep_care_mistake_timer:
            self.care_sleep_mistake_timer += 1
            if self.care_sleep_mistake_timer >= get_module(self.module).sleep_care_mistake_timer:
                if self.condition_hearts > 0:
                    self.condition_hearts -= 1
                sound_alert = True
                self.care_sleep_mistake_timer = 0
                runtime_globals.game_console.log(f"[!] Care mistake (sleep)! Remaining Condition Hearts: {self.condition_hearts}")
        
        if sound_alert:
            runtime_globals.game_sound.play("alarm")

    def need_care(self):
        return self.stage != 0 and self.state not in ("dead","nap") and (self.hunger == 0 or self.strength == 0 or self.sick > 0 or self.should_sleep())
    
    def call_sign(self):
        if self.stage != 0 and self.state not in ("dead","nap"):
            return False
        if self.hunger == 0 and self.care_food_mistake_timer < get_module(self.module).meat_care_mistake_time:
            return True
        elif self.strength == 0 and self.care_strength_mistake_timer < get_module(self.module).protein_care_mistake_time:
            return True
        elif self.should_sleep() and self.care_sleep_mistake_timer < get_module(self.module).sleep_care_mistake_timer:
            return True
        return False
    
    def get_power(self):
        power = self.power
        
        strength_bonus = 0
        traited_bonus = 0
        shaken_bonus = 0
        
        # Strength Hearts Bonus
        if self.effort >= 16:
            if self.stage == 3:
                strength_bonus = 5
            elif self.stage == 4:
                strength_bonus = 8
            elif self.stage == 5:
                strength_bonus = 15
            elif self.stage >= 6:
                strength_bonus = 20

        # Traited Egg Bonus
        if self.traited:
            if self.stage == 3:
                traited_bonus = 5
            elif self.stage == 4:
                traited_bonus = 8
            elif self.stage == 5:
                traited_bonus = 15
            elif self.stage >= 6:
                traited_bonus = 20

        # Shaken Egg Bonus
        if self.shook:
            shaken_bonus = 10

        # Total Bonus Calculation
        total_bonus = strength_bonus + traited_bonus + shaken_bonus

        return power + total_bonus

    def can_battle(self):
        return self.stage > 2 and self.state != "dead"
    
    def can_train(self):
        return self.stage > 1 and self.state != "dead"

    def set_sick(self):
        self.sick = 1
        self.injuries += 1
        self.set_state("sick")

    def finish_training(self, won = False):
        if won:
            self.set_state("happy2")
            self.effort += get_module(self.module).training_effort_gain
            if self.disturbance_penalty > 2:
                self.disturbance_penalty -= 2
        else:
            self.set_state("angry")
        self.strength += get_module(self.module).training_strengh_gain
        
        weight_loss = get_module(self.module).training_weight_win if won else get_module(self.module).training_weight_lose
        self.weight = max(self.min_weight, self.weight - weight_loss)
        

    def finish_battle(self, won=False):
        self.battles += 1
        self.dp -= 1
        self.totalBattles += 1
        if won:
            self.set_state("happy3")
            self.win += 1
            self.totalWin += 1
            sick_chance = get_module(self.module).battle_base_sick_chance_win
        else:
            sick_chance = get_module(self.module).battle_base_sick_chance_lose + self.disturbance_penalty

        sick_chance = max(0.05, min(sick_chance / 100, 0.5))

        if random.random() < sick_chance:
            self.set_sick()

    def finish_versus(self, won=False):
        self.battles += 1
        self.totalBattles += 1
        if won:
            self.set_state("happy3")
            self.win += 1
            self.totalWin += 1

    def set_back_to_sleep(self):
        self.back_to_sleep = 15

    def check_disturbed_sleep(self):
        if self.state == "nap":
            runtime_globals.game_console.log(f"[DEBUG] Sleep disturbance {self.disturbance_penalty}")
            self.set_state("idle")
            self.disturbance_penalty += 2
            self.set_back_to_sleep()
        