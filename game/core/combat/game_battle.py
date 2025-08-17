import random
from game.core import constants
from game.core.combat import combat_constants

class GameBattle:
    def __init__(self, team1, team2, hp_buff, attack_buff, module):
        self.module = module
        self.attack_buff = attack_buff  # Attack boost for the player
        self.team1 = team1  # Player's team
        self.team2 = team2  # Enemy's team

        self.team1_hp = [0] * len(team1)  # HP for each pet in team1
        self.team1_max_hp = [0] * len(team1)  # Max HP for team1
        self.team2_hp = [0] * len(team1)  # HP for each
        self.team2_max_hp = [0] * len(team2)

        self.team1_total_hp = self.get_hp(team1, self.team1_hp, hp_buff)
        self.team1_max_total_hp = self.team1_total_hp  # Store max HP for team1
        self.team1_max_hp = [hp for hp in self.team1_hp]  # Max HP with buff
        self.team2_total_hp = self.get_hp(team2, self.team2_hp)
        if len(team2) == 1 and len(team1) > 1:
            # Boss Fight scalling
            self.team2_total_hp *= len(team1)
            self.team2_hp[0] = self.team2_total_hp
        self.team2_max_total_hp = self.team2_total_hp  # Store max HP for team2
        self.team2_max_hp = [hp for hp in self.team2_hp]

        self.turns = [1] * len(team1)  # Track turns for each pet

        self.team1_projectiles = [[] for _ in range(len(team1))]  # List of projectiles for the player's team
        self.team2_projectiles = [[] for _ in range(len(team1))]  # List of projectiles for the enemy team
        self.team1_bar_counters = [0] * len(team1)  # Bar counters for each pet in team1
        self.team2_bar_counters = [0] * len(team2)  # Bar counters for each pet in team2
        self.phase = ["pet_charge"] * len(self.team1)
        self.victory_status = "Ongoing"  # Track battle status
        self.winners = [None] * len(self.team1)  # Track winners for each pair
        self.team1_shot = [False] * len(self.team1)  # Track if a shot was fired
        self.team2_shot = [False] * len(self.team1)  # Track if a shot was fired by the enemy
        self.shot_wait = [0] * len(self.team1)  # Track shot wait time for each pet
        self.xp = 0
        self.bonus = 0
        self.prize_item = None  # Prize item after battle
        self.level_up = [False] * len(self.team1)  # Track if pets level up
        self.reset_frame_counters()
        self.reset_cooldowns()
        self.reset_jump_and_forward()

    def get_hp(self, team, team_hp, buff=0):
        """
        Calculates the total HP of a team.
        """
        total_hp = 0
        for i, pet in enumerate(team):
            hp = 0
            if self.module and self.module.battle_global_hit_points > 0:
                hp = self.module.battle_global_hit_points
                if hasattr(pet, "get_hp"):
                    hp += buff
            else:
                if hasattr(pet, "get_hp"):
                    hp += pet.get_hp() + buff
                elif hasattr(pet, "hp"):
                    hp += pet.hp + buff
            team_hp[i] = hp
            total_hp += hp
        return total_hp
    
    def increment_frame_counters(self):
        """
        Increments the frame counters for each pet in the player's team.
        """
        for i in range(len(self.frame_counters)):
            self.frame_counters[i] += 1

    def reset_frame_counters(self):
        """
        Resets the frame counters for each pet in the player's team.
        """
        self.frame_counters = [0] * len(self.team1)

    def reset_cooldowns(self):
        """
        Resets the cooldowns for each pet in the player's team.
        """
        self.cooldowns = [self.calculate_deterministic_cooldown(i) for i in range(len(self.team1))]

    def calculate_deterministic_cooldown(self, pet_index):
        """
        Calculates a deterministic cooldown value based on pet name, turn, phase, and team size.
        Returns a value between 30-70 * (FRAME_RATE / 30), scaled by team size.
        """
        # Get pet name for consistency
        pet_name = ""
        if hasattr(self.team1[pet_index], 'name'):
            pet_name = self.team1[pet_index].name
        elif hasattr(self.team1[pet_index], 'species'):
            pet_name = self.team1[pet_index].species
        else:
            pet_name = f"pet_{pet_index}"
        
        # Get current phase for this pet
        current_phase = self.phase[pet_index] if pet_index < len(self.phase) else "pet_charge"
        current_turn = self.turns[pet_index] if pet_index < len(self.turns) else 1
        team_size = len(self.team1)
        
        # Create a deterministic seed from all variables
        seed_string = f"{pet_name}_{current_turn}_{current_phase}_{team_size}"
        
        # Simple hash function to convert string to number
        hash_value = 0
        for char in seed_string:
            hash_value = (hash_value * 31 + ord(char)) % 1000000
        
        # Base range is 30-70
        base_min = 30
        base_max = 70
        base_range = base_max - base_min
        
        # Team size scaling: smaller teams tend toward smaller numbers
        # Team size 1: bias toward lower end (30-50)
        # Team size 2-3: normal range (30-70)  
        # Team size 4+: bias toward higher end (50-70)
        if team_size == 1:
            # Scale to 30-50 range
            adjusted_min = base_min
            adjusted_max = base_min + (base_range * 0.5)
        elif team_size <= 3:
            # Normal range 30-70
            adjusted_min = base_min
            adjusted_max = base_max
        else:
            # Scale to 50-70 range for larger teams
            adjusted_min = base_min + (base_range * 0.5)
            adjusted_max = base_max
        
        # Map hash to the adjusted range
        cooldown_base = adjusted_min + (hash_value % int(adjusted_max - adjusted_min + 1))
        
        # Apply frame rate scaling
        cooldown_scaled = int(cooldown_base * (constants.FRAME_RATE / 30))
        
        return cooldown_scaled

    def decrement_cooldowns(self):
        """
        Decrements the cooldowns for each pet in the player's team.
        """
        for i in range(len(self.cooldowns)):
            if self.cooldowns[i] > 0:
                self.cooldowns[i] -= 1

    def reset_jump_and_forward(self):
        """
        Resets the attack jump and forward distance for each pet in the player's team.
        """
        self.attack_jump = [0] * len(self.team1)
        self.attack_forward = [0] * len(self.team1)

    def update(self):
        """
        Updates the player's team state, including frame counters and attack jump/forward.
        """
        self.decrement_cooldowns()
        self.update_bar_counters()
        for i in range(len(self.team1)):
            if self.turns[i] > 12:
                self.phase[i] = "result"
                continue
            
            if self.phase[i] in ["result"]:
                continue
            
            if (self.phase[i] == "pet_charge" and self.team1_hp[i] > 0) or (self.phase[i] == "enemy_charge" and self.team2_hp[i] > 0):
                self.update_charge(i)

            if self.cooldowns[i] <= 0:
                if self.phase[i] == "pet_attack" and (self.shot_wait[i] or self.team1_hp[i] <= 0):
                    self.shot_wait[i] = False
                    self.phase[i] = "enemy_charge"
                    self.attack_forward[i] = 0
                    self.attack_jump[i] = 0
                elif self.phase[i] == "pet_charge":
                    self.phase[i] = "pet_attack"
                    self.team1_shot[i] = True if self.team1_hp[i] > 0 else False
                elif self.phase[i] == "enemy_attack" and (self.shot_wait[i] or self.team2_hp[i] <= 0):
                    self.shot_wait[i] = False
                    self.phase[i] = "pet_charge"
                    self.attack_forward[i] = 0
                    self.attack_jump[i] = 0
                    self.turns[i] += 1
                    if self.turns[i] > 12:
                        self.phase[i] = "result"
                elif self.phase[i] == "enemy_charge":
                    self.phase[i] = "enemy_attack"
                    self.team2_shot[i] = True if self.team2_hp[i] > 0 else False

                if not self.shot_wait[i]:
                    self.cooldowns[i] = self.calculate_deterministic_cooldown(i)
                    self.frame_counters[i] = 0

    def update_charge(self, index):
        """
        Updates the charge state for each pet in the player's team.
        """
        if self.cooldowns[index] <= 9 * int(constants.FRAME_RATE / 30):
            self.attack_forward[index] -= 1 * (30 / constants.FRAME_RATE)
        elif self.cooldowns[index] <= 18 * int(constants.FRAME_RATE / 30):
            self.attack_forward[index] += 1 * (30 / constants.FRAME_RATE)
            if self.cooldowns[index] < 14 * int(constants.FRAME_RATE / 30):
                self.attack_jump[index] -= 1 * (30 / constants.FRAME_RATE)
            elif self.cooldowns[index] > 14 * int(constants.FRAME_RATE / 30):
                self.attack_jump[index] += 1 * (30 / constants.FRAME_RATE)
        else:
            self.attack_forward[index] = 0
            self.attack_jump[index] = 0

    def update_bar_counters(self):
        """
        Updates the bar counters for each pet in the player's team.
        """
        for i in range(len(self.team1_bar_counters)):
            if self.team1_bar_counters[i] > 0:
                self.team1_bar_counters[i] -= 1
        for i in range(len(self.team2_bar_counters)):
            if self.team2_bar_counters[i] > 0:
                self.team2_bar_counters[i] -= 1