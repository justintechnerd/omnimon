import random
from core import game_globals, runtime_globals
from core.constants import *
from core.game_pet import GamePet
from core.game_poop import GamePoop
from core.utils import get_module
from core.utils_unlocks import unlock_item


class GamePetDmC(GamePet):
    def __init__(self, pet_data, traited = False):
        super().__init__(pet_data, traited)

    def set_data(self, data):
        super().set_data(data)
        self.heal_doses = data.get("heal_doses")
        
    def reset_variables(self):
        super().reset_variables()
        self.mistakes = self.overfeed = self.overfeed_timer = 0
        self.sleep_disturbances = 0
        self.protein_overdose = 0
        
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
                ("mistakes" in evo and not in_range(self.mistakes, evo["mistakes"])) or
                ("training" in evo and not in_range(self.effort, evo["training"])) or
                ("overfeed" in evo and not in_range(self.overfeed, evo["overfeed"])) or
                ("sleep_disturbances" in evo and not in_range(self.sleep_disturbances, evo["sleep_disturbances"])) or
                ("battles" in evo and not in_range(self.battles, evo["battles"])) or
                ("win_ratio" in evo and self.battles and not in_range((self.win * 100) // self.battles, evo["win_ratio"]))
            ):
                continue

            if self.module == "DMC" and evo["to"] in ("ShinMonzaemon","Ebemon","BanchoLeomon","Gankoomon","Samudramon"):
                unlock_item("DMC", "backgrounds", "25")

            self.evolve_to(evo["to"], evo.get("version", self.version))
            break

    #Poop is such an iconic part of the Digimon experience that there are over a dozen Digimon built entirely around POOP! 
    # Your Digimon will poop as time passes: every 3 minutes at Stage I, every 60 minutes at Stage II and then every 120 minutes 
    # for the rest of its life. Just select the Poop icon to clean it up, and make sure you never let 8 piles accumulate, 
    # or else your Digimon will get injured! Remember: Poop and injuries are NOT Care Mistakes, but too many injuries will 
    # kill your Digimon.
    def update_pooping(self):
        if self.stage <= 0 or self.timer < 1800: return
        if len(game_globals.poop_list) >= (len(game_globals.pet_list) * 8) and self.stage >= 2:
            if self.poop_count_flag == 0:
                self.poop_count_flag = 1
                self.set_sick()
                runtime_globals.game_console.log(f"[!] Care sick of poop ({len(game_globals.poop_list)})! Injuries: {self.injuries}")
        else:
            self.poop_count_flag = 0
            
        interval = self.poop_timer * 60 * 30
        if self.timer % interval == 0:
            self.set_state("pooping")

    #Hunger - As time proceeds, these hearts will empty at a set rate, which can be seen by clicking on that 
    # Digimon in the Evolution Guide. Feed your Digimon meat to fill the hearts back up. Your Digimon can eat 
    # more than the number of hearts, and continuing to feed it until it refuses to will result in an Overfeed. 
    # This is an evolution requirement, so pay attention to how often you Overfeed.

    #Strength - As time proceeds, these hearts will empty at a set rate, which can be seen by clicking on that
    # Digimon in the Evolution Guide. Your Digimon likes to be at maximum strength, refill these hearts by feeding
    # protein or training. When at full strength, your Digimon will receive a bonus to its Power stat, which can be
    # seen the Power section below.

    #Energy (DP) - Your stamina, this is required for battling. If you have no Energy, you can’t fight. Energy is
    #  completely restored by sleeping for at least 8 hours, or restored by 1 by feeding 4 Protein. You can see how
    #  much Energy each Digimon has by clicking on that Digimon in the Evolution Guide.
    def update_needs(self):
        if self.timer % (self.hunger_loss * 60 * 30) == 0 and self.hunger > 0:
            if self.overfeed_timer > 0 and self.hunger > 4: #skips a cicle if overfed
                self.hunger = 4
            else:
                self.hunger -= 1
        if self.timer % (self.strength_loss * 60 * 30) == 0 and self.strength > 0:
            if self.strength > 4:
                self.strength = 4
            else:
                self.strength -= 1
        if self.overfeed_timer > 0:
            self.overfeed_timer -= 1
    
    def set_eating(self):
        if self.food_type < 0: return

        self.animation_counter = 0
        self.direction = 1

        if self.food_type == 0:
            if self.hunger == self.stomach or self.overfeed_timer: #can eat if not overfed and stomach < hunger
                if self.overfeed_timer == 0:
                    self.overfeed_timer = get_module(self.module).overfeed_timer
                    self.overfeed += 1
                self.set_state("nope")
                self.food_type = -1
                runtime_globals.game_console.log(f"{self.name} is full. Overfeed Timer {self.overfeed_timer}")
            else:
                self.set_state("eat")
                self.hunger += get_module(self.module).meat_hunger_gain
                if self.weight < 99:
                    self.weight += get_module(self.module).meat_weight_gain
                self.care_food_mistake_timer = 0
                runtime_globals.game_console.log(f"{self.name} ate protein. Hunger {self.hunger}")
        else:
            #Protein Overdose - How much Protein you have fed your Digimon. Every 4 Protein counts as 1 
            # Protein Overdose, which will increase the liklihood of your Digimon getting injured in Battle. 
            # The maximum value for Protein Overdose is 7. See the Heal section for more details.
            self.set_state("eat")
            self.strength += get_module(self.module).protein_strengh_gain
            if self.protein_overdose // 4 <= 7: #protein overdose max
                self.protein_overdose += 1
            if self.weight < 99:
                self.weight += get_module(self.module).protein_weight_gain
            if self.dp < self.energy and self.protein_overdose % 4 == 0:
                self.dp += get_module(self.module).protein_dp_gain
            self.care_strength_mistake_timer = 0
            runtime_globals.game_console.log(f"{self.name} ate vitamin. Strength {self.strength}")

    #Digimon can get injured from battling or from accumulating 8 poops. When your Digimon is injured, 
    # it will have a skull floating next to it. When this happens you can use this option to heal them! 
    # Select this icon to heal your Digimon, and note that multiple doses of medicine may be necessary. 
    # You can see how many doses your Digimon requires by clicking on that Digimon in the Evolution Guide. 
    # If your Digimon gets injured 15 times, or remains injured for 6 hours, it will DIE. For battles, 
    # you have a 20% chance of getting injured when you win, and a 10% chance when you lose. That 10% 
    # chance is increased by 10% for every Protein Overdose you have, for a maximum of 80%. Every 4 
    # Protein fed creates one Protein Overdose

    #Potentially you could keep your Digimon alive forever, but you aren’t going to. You’re going to go to a party one night
    #  and forget to put them down for a nap before you leave.  And then they will die. You monster. There are actually
    #  several ways your Digimon can die, including the following:
    #Getting injured 15 times in one form
    #Remaining injured for 6 hours consecutive in one form
    #Leaving the Hunger or Strength hearts empty for 12 consecutive hours in one form
    #Having 5 or more Care Mistakes when or after the evolution timer for your Stage IV or V Digimon runs out without having
    #  fulfilled the requirements for evolution
    #Having 5 or more Care Mistakes when or after your Stage VI or VI+ Digimon has been in that form for 48 hours
    #Once your Digimon finishes singing its dying song, you are now looking at a grave. Your Digimon has died and converted
    #  back into raw data. Oh well! LET’S MAKE A NEW ONE!
    #  Press A+B simultaneously and just like that, a new egg will hatch. Note that while hearts would begin dropping at a
    #  faster rate after a certain point on other
    #  devices, this never occurs on the Digital Monster Color.

    #When a Stage V or higher Digimon dies, it has a 30% chance of leaving a Traited Egg. 
    # The egg will appear on the screen behind the grave of your Digimon, and the Digimon 
    # that hatches from it will receive a bonus to its Power. Details of that 
    # Power Bonus are in the Status section above.
    def set_traited_egg(self):
        if self.stage in [6, 7] and random.randint(0, 10) <= 3:
            key = f"{self.module}@{self.version}"
            if key not in game_globals.traited:
                game_globals.traited.append(key)
                runtime_globals.game_console.log(f"Traited Egg granted for {self.name}!")

    #If your Digimon needs you, it will call out to you with a few beeps, and this icon will light up.
    #  When this happens, act fast! If the call light goes out before you take care of the Digimon,
    #  that counts as a care mistake. The number of care mistakes you have will affect the outcome of
    #  your evolution. For evolving to Stage III or IV, your number of care mistakes is a factor in
    #  determining what Digimon you evolve into. For evolving to Stage VI, too many care mistakes will
    #  prevent you from evolving at all. Calls may occur for the following reasons:

    #The hunger meter is empty
    #The strength meter is empty
    #Your Digimon is asleep and wants the lights turned off
    #The call light will go out after 10 minutes for Hunger or Strength, and after 1 hour for sleep.
    #  Note that if you have sound off, calls will still occur. If an empty meter is not filled after 
    # the call light goes out on its own, your Digimon will call again when its timer for that heart meter 
    # runs out again, and can result in another care mistake. A Digimon will only call one time for sleep, 
    # regardless of whether or not you turn out the lights. Hunger and Strength depleting at the same time 
    # will result in two care mistakes if you don't fill them, even if you only receive one call.
    def update_care_mistakes(self):
        sound_alert = False
        #hunger call
        if self.hunger == 0:
            self.care_food_mistake_timer += 1
            if self.care_food_mistake_timer == get_module(self.module).meat_care_mistake_time:
                self.mistakes += 1
                sound_alert = True
                runtime_globals.game_console.log(f"[!] Care mistake (hunger)! Total: {self.mistakes}")
        
        #strength call
        if self.strength == 0:
            self.care_strength_mistake_timer += 1
            if self.care_strength_mistake_timer == get_module(self.module).protein_care_mistake_time:
                self.mistakes += 1
                sound_alert = True
                runtime_globals.game_console.log(f"[!] Care mistake (strength)! Total: {self.mistakes}")
        
        #sick call
        if self.sick > 0:
            self.care_sick_mistake_timer += 1
        else:
            self.care_sick_mistake_timer = 0

        #sleep call
        if self.should_sleep():
            self.care_sleep_mistake_timer += 1
            if self.care_sleep_mistake_timer >= get_module(self.module).sleep_care_mistake_timer:
                self.mistakes += 1
                sound_alert = True
                self.care_sleep_mistake_timer = 0
                runtime_globals.game_console.log(f"[!] Care mistake (sleep)! Total: {self.mistakes}")
        
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

    #Effort - Every 4 training sessions you perform will fill 1 effort heart. Training is very important for 
    # evolution: different numbers of training can lead to different evolutionary lines, so experiment with different amounts.
    #Power - How strong your Digimon is. If your power is higher than your enemy's power, then your attacks are more likely to hit. The higher the power difference, the higher the liklihood of each hit connecting. Each Digimon has a Base Power that can be seen by clicking on that Digimon in the Evolution guide. All Digimon of the same species will have the same Base Power. In addition, having full Strength Hearts will grant a bonus to power, as will hatching from a Traited egg. The below chart displays how much is added to power for each evolutionary stage.
    #    Stage	Strength Hearts	Traited Egg	Both
    #    III	+5	    +5	    +10
    #    IV	    +8	    +8	    +16
    #    V	    +15	    +15	    +30
    #    VI	    +25	    +25	    +50
    #    VI+	+25	    +25	    +50
    #hitrate = ((playerPower * 100)/(playerPower + opponentPower)) + attributeAdvantage
    def get_power(self):
        power = self.power

        multi = 1
        if self.traited:
            multi = 2

        if self.effort >= 16:
            if self.stage == 3:
                power += (5 * multi)
            elif self.stage == 4:
                power += (8 * multi)
            elif self.stage == 5:
                power += (15 * multi)
            elif self.stage >= 6:
                power += (25 * multi)
        return power
        
    def can_battle(self):
        return self.power > 0 and self.state != "dead"
    
    def can_train(self):
        return self.power > 0 and self.state != "dead"

    def set_sick(self):
        self.sick = self.heal_doses
        self.injuries += 1
        self.set_state("sick")

    def finish_training(self, won = False):
        if won:
            self.set_state("happy2")
            self.effort += get_module(self.module).training_effort_gain
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
            sick_chance = get_module(self.module).battle_base_sick_chance_lose + (10 * self.protein_overdose)

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

    #Lights - This allows you to turn on or off the lights. 
    # When a Digimon falls asleep, the lights should be turned off 
    # right away to avoid a care mistake. If your Digimon is asleep 
    # and you disturb it by attempting to feed, train or battle with 
    # it, this will count as a sleep disturbance, which is an evolution 
    # requirement for certain Digimon. Waking a sleeping Digimon 
    # does not count as a Care Mistake. After being disturbed, the 
    # Digimon will fall back asleep after 10 minutes. All Digimon 
    # wake up on their own at 8:00 AM.
    def set_back_to_sleep(self):
        self.back_to_sleep = 10

    def check_disturbed_sleep(self):
        if self.state == "nap":
            runtime_globals.game_console.log(f"[DEBUG] Sleep disturbance {self.sleep_disturbances}")
            self.set_state("idle")
            self.sleep_disturbances += 1
            self.set_back_to_sleep()
        