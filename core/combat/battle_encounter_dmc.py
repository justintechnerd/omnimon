#=====================================================================
# BattleEncounter
#=====================================================================

import random
import pygame
from core import runtime_globals
from core.combat.battle_encounter import ALERT_DURATION_FRAMES, IDLE_ANIM_DURATION, BattleEncounter
from core.constants import *

class BattleEncounterDMC(BattleEncounter):

    def __init__(self, module):
        super().__init__(module)

    def update_alert(self):
        if self.frame_counter == 30:
            runtime_globals.game_sound.play("happy")
        if self.frame_counter > ALERT_DURATION_FRAMES:
            runtime_globals.game_console.log("Entering charge phase")
            self.phase = "charge"
            self.frame_counter = 0
            self.pet_anim_index = 0
            self.pet_anim_counter = 0
            self.bar_timer = pygame.time.get_ticks()


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
    
    def draw(self, surface):
        super().draw(surface)

        if self.phase == "alert":
            sprite = self.alert_sprite if self.frame_counter < 30 else self.go_sprite
            center_x = SCREEN_WIDTH // 2 - sprite.get_width() // 2
            surface.blit(sprite, (center_x, 25))
        elif self.phase == "charge":
            self.draw_strength_bar(surface)