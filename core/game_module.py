import json
import os
from typing import List, Optional

import pygame

from core import runtime_globals
from core.constants import *
from core.game_enemy import GameEnemy
import copy


#=====================================================================
# GameModule - Manages module data (monsters and metadata)
#=====================================================================

class GameModule:
    """
    Represents a game module, capable of loading metadata and monsters from its folder.
    """

    def __init__(self, folder_path: str) -> None:
        self.folder_path = folder_path
        self.name = "default"
        self.name_format = ""
        self.ruleset = ""
        self.unlocks = {"eggs": [], "backgrounds": [], "evolutions": []}
        self.backgrounds = []
        self.load_module_data()
        self.load_sprites()

    def load_module_data(self) -> None:
        json_path = os.path.join(self.folder_path, "module.json")
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    self.name = data.get("name", "default")
                    self.name_format = data.get("name_format", "$_dmc")
                    self.ruleset = data.get("ruleset", "dmc")

                    self.adventure_mode = data.get("adventure_mode", False)
                    self.adventure_version_max = int(data.get("adventure_version_max"))

                    self.meat_weight_gain = int(data.get("meat_weight_gain"))
                    self.meat_hunger_gain = int(data.get("meat_hunger_gain"))
                    self.meat_care_mistake_time = int(data.get("meat_care_mistake_time"))
                    self.overfeed_timer = int(data.get("overfeed_timer"))
                    self.use_condition_hearts = bool(data.get("condition_heart", False))
                    self.can_eat_sleeping = bool(data.get("can_eat_sleeping", True))
                    self.back_to_sleep_time = bool(data.get("back_to_sleep_time", True))
                    self.enable_shaken_egg = bool(data.get("enable_shaken_egg", False))

                    self.protein_weight_gain = int(data.get("protein_weight_gain"))
                    self.protein_strengh_gain = int(data.get("protein_strengh_gain"))
                    self.protein_dp_gain = int(data.get("protein_dp_gain"))
                    self.protein_care_mistake_time = int(data.get("protein_care_mistake_time"))
                    self.protein_overdose_max = int(data.get("protein_care_mistake_time", 0))
                    self.disturbance_penalty_max = int(data.get("disturbance_penalty_max", 0))

                    self.sleep_care_mistake_timer = int(data.get("sleep_care_mistake_timer"))

                    self.training_effort_gain = int(data.get("training_effort_gain"))
                    self.training_strengh_gain = int(data.get("training_strengh_gain"))

                    self.training_weight_win = int(data.get("training_weight_win"))
                    self.training_weight_lose = int(data.get("training_weight_lose"))

                    self.traited_egg_starting_level = int(data.get("traited_egg_starting_level"))

                    self.reverse_atk_frames = bool(data.get("reverse_atk_frames", False))

                    self.battle_base_sick_chance_win = int(data.get("battle_base_sick_chance_win"))
                    self.battle_base_sick_chance_lose = int(data.get("battle_base_sick_chance_lose"))

                    self.death_max_injuries = int(data.get("death_max_injuries"))
                    self.death_sick_timer = int(data.get("death_sick_timer"))
                    self.death_hunger_timer = int(data.get("death_hunger_timer"))
                    self.death_starvation_count = int(data.get("death_starvation_count"))
                    self.death_strength_timer = int(data.get("death_strength_timer"))
                    self.death_stage45_mistake = int(data.get("death_stage45_mistake"))
                    self.death_stage67_mistake = int(data.get("death_stage67_mistake"))
                    self.death_care_mistake = int(data.get("death_care_mistake",999999))
                    self.death_save_by_b_press = int(data.get("death_save_by_b_press",0))
                    self.death_save_by_shake = int(data.get("death_save_by_shake",0))
                    
                    self.unlocks = data.get("unlocks", {
                        "eggs": [],
                        "backgrounds": [],
                        "evolutions": []
                    })

                    self.backgrounds = data.get("backgrounds", [])
            except json.JSONDecodeError:
                runtime_globals.game_console.log(f"⚠️ Failed to parse {json_path}")
        else:
            runtime_globals.game_console.log(f"⚠️ Module metadata file {json_path} not found.")

    def load_sprites(self):
        """Loads the flag sprite for the game module."""
        flag_path = os.path.join(self.folder_path, "Flag.png")
        runtime_globals.game_module_flag[self.name] = sprite_load(flag_path, size=(OPTION_ICON_SIZE, OPTION_ICON_SIZE))

    def get_monsters_by_stage(self, stage: int, special_list: list[str] = None) -> list[dict]:
        monsters = []
        json_path = os.path.join(self.folder_path, "monster.json")

        if not os.path.exists(json_path):
            runtime_globals.game_console.log(f"⚠️ Monster file {json_path} not found.")
            return monsters

        try:
            with open(json_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                for monster in data.get("monster", []):
                    if monster["stage"] == stage and (special_list is None or (monster["special"] and monster["name"] in special_list)):
                        monster["module"] = self.name
                        monsters.append(monster)

                runtime_globals.game_console.log(f"✅ Loaded {len(monsters)} monsters from stage {stage}.")
                return monsters
        except json.JSONDecodeError:
            runtime_globals.game_console.log(f"⚠️ Failed to parse {json_path}")
            return monsters

    def get_monster(self, name: str, version: int) -> Optional[dict]:
        json_path = os.path.join(self.folder_path, "monster.json")

        if not os.path.exists(json_path):
            runtime_globals.game_console.log(f"⚠️ Monster file {json_path} not found.")
            return None

        try:
            with open(json_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                for monster in data.get("monster", []):
                    if monster["name"] == name and monster["version"] == version:
                        return monster
        except json.JSONDecodeError:
            runtime_globals.game_console.log(f"⚠️ Failed to parse {json_path}")
        return None

    def get_enemies(self, area: int, round_: int, versions: List[int]) -> List[Optional[GameEnemy]]:
        battle_path = os.path.join(self.folder_path, "battle.json")

        if not os.path.exists(battle_path):
            runtime_globals.game_console.log(f"⚠️ Enemy file {battle_path} not found.")
            return [None] * len(versions)

        try:
            id = 1
            with open(battle_path, "r", encoding="utf-8") as file:
                data = json.load(file)

                for entry in data:
                    entry.setdefault("handicap", 0)
                    entry.setdefault("id", 0)

                all_enemies = [GameEnemy(**entry) for entry in data]

                selected = []
                for v in versions:
                    match = next((e for e in all_enemies if e.area == area and e.round == round_ and e.version == v), None)

                    if match:
                        # Ensure 'handicap' exists and defaults to 0 if missing
                        if not hasattr(match, "handicap"):
                            match.handicap = 0

                    match.id = id
                    id += 1
                    selected.append(copy.deepcopy(match))

                # Save to runtime
                return selected
        except json.JSONDecodeError:
            runtime_globals.game_console.log(f"⚠️ Failed to parse {battle_path}")
            return [None] * len(versions)
        
    def get_all_monsters(self) -> list[dict]:
        """
        Retorna todos os monstros listados no monster.json deste módulo.
        """
        json_path = os.path.join(self.folder_path, "monster.json")
        if not os.path.exists(json_path):
            runtime_globals.game_console.log(f"⚠️ Monster file {json_path} not found.")
            return []

        try:
            with open(json_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                return data.get("monster", [])
        except json.JSONDecodeError:
            runtime_globals.game_console.log(f"⚠️ Failed to parse {json_path}")
            return []
        
def sprite_load(path, size=None, scale=1):
    """Loads a sprite and optionally scales it to a fixed size or by a scale factor."""
    img = pygame.image.load(path).convert_alpha()
    
    if size:
        return pygame.transform.scale(img, size)  # 🔹 Scale to a fixed size
    elif scale != 1:
        base_size = img.get_size()
        new_size = (int(base_size[0] * scale), int(base_size[1] * scale))
        return pygame.transform.scale(img, new_size)  # 🔹 Scale by a multiplier
    
    return img  # 🔹 Return original image if no scaling is applied