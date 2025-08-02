import json
import os
from typing import List, Optional

import pygame

from core import runtime_globals
import game.core.constants as constants
from core.game_enemy import GameEnemy
import copy

from core.game_item import GameItem


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
        self.load_items()

    def load_module_data(self) -> None:
        json_path = os.path.join(self.folder_path, "module.json")
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    self.name = data.get("name", "default")
                    self.name_format = data.get("name_format", "$_dmc")
                    self.ruleset = data.get("ruleset", "dmc")
                    self.author = data.get("author", "Unknown")
                    self.version = data.get("version", "1.0")
                    self.description = data.get("description", "No description available.")

                    self.adventure_mode = data.get("adventure_mode", False)

                    self.meat_weight_gain = int(data.get("care_meat_weight_gain"))
                    self.meat_hunger_gain = int(data.get("care_meat_hunger_gain"))
                    self.meat_care_mistake_time = int(data.get("care_meat_care_mistake_time"))
                    self.overfeed_timer = int(data.get("care_overfeed_timer"))
                    self.use_condition_hearts = bool(data.get("care_condition_heart", False))
                    self.can_eat_sleeping = bool(data.get("care_can_eat_sleeping", True))
                    self.back_to_sleep_time = bool(data.get("care_back_to_sleep_time", True))
                    self.enable_shaken_egg = bool(data.get("care_enable_shaken_egg", False))

                    self.protein_weight_gain = int(data.get("care_protein_weight_gain"))
                    self.protein_strengh_gain = int(data.get("care_protein_strengh_gain"))
                    self.protein_dp_gain = int(data.get("care_protein_dp_gain"))
                    self.protein_care_mistake_time = int(data.get("care_protein_care_mistake_time"))
                    self.protein_overdose_max = int(data.get("care_protein_care_mistake_time", 0))
                    self.disturbance_penalty_max = int(data.get("care_disturbance_penalty_max", 0))

                    self.sleep_care_mistake_timer = int(data.get("care_sleep_care_mistake_timer"))

                    self.training_effort_gain = int(data.get("training_effort_gain"))
                    self.training_strengh_gain = int(data.get("training_strengh_gain"))

                    self.training_weight_win = int(data.get("training_weight_win"))
                    self.training_weight_lose = int(data.get("training_weight_lose"))

                    self.traited_egg_starting_level = int(data.get("traited_egg_starting_level"))

                    self.reverse_atk_frames = bool(data.get("reverse_atk_frames", False))

                    self.battle_base_sick_chance_win = int(data.get("battle_base_sick_chance_win"))
                    self.battle_base_sick_chance_lose = int(data.get("battle_base_sick_chance_lose"))
                    self.battle_atribute_advantage = int(data.get("battle_atribute_advantage", 5))
                    self.battle_global_hit_points = int(data.get("battle_global_hit_points", 0))
                    self.battle_sequential_rounds = int(data.get("battle_sequential_rounds", False))

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

                    self.vital_value_base = int(data.get("vital_value_base", 50))
                    self.vital_value_loss = int(data.get("vital_value_loss", 50))

                    if self.battle_global_hit_points > 0:
                        self.battle_damage_limit = 1 + (self.battle_global_hit_points // 2)
                    else:
                        self.battle_damage_limit = 99
                    
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

    def load_items(self):
        """Loads items from item.json if it exists in the module folder."""
        json_path = os.path.join(self.folder_path, "item.json")
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as file:
                try:
                    data = json.load(file)
                    # Expecting a list of items in the JSON file
                    self.items = self.load_items_from_json(data, self.name)
                except json.JSONDecodeError:
                    runtime_globals.game_console.log(f"Error: Failed to parse {json_path}")
        else:
            self.items = {}

    def load_items_from_json(self, data, module_name):
        """
        Loads items from a JSON list for a given module.
        Each item in the JSON should have: id, name, description, sprite_name, effect, status, amount, boost_time.
        """
        # If data is a string, parse it as JSON
        if isinstance(data, str):
            import json
            data = json.loads(data)
        # If data is a dict, extract the first list value (e.g., "item" or "items")
        if isinstance(data, dict):
            # Try common keys, fallback to first list found
            for key in ("items", "item"):
                if key in data and isinstance(data[key], list):
                    data = data[key]
                    break
            else:
                # Fallback: find the first list value in the dict
                for v in data.values():
                    if isinstance(v, list):
                        data = v
                        break
        # Now data should be a list of dicts
        items = []
        for entry in data:
            if not isinstance(entry, dict):
                continue  # ski p invalid entries
            items.append(GameItem(
                id=entry["id"],
                name=entry["name"],
                description=entry.get("description", ""),
                sprite_name=entry.get("sprite_name", ""),
                effect=entry.get("effect", ""),
                status=entry.get("status", ""),
                amount=entry.get("amount", 0),
                boost_time=entry.get("boost_time", 0),
                module=module_name,
                component_item=entry.get("component_item", "")
            ))
        return items

    def load_sprites(self):
        """Loads the flag sprite for the game module."""
        flag_path = os.path.join(self.folder_path, "Flag.png")
        runtime_globals.game_module_flag[self.name] = sprite_load(flag_path, size=(constants.OPTION_ICON_SIZE, constants.OPTION_ICON_SIZE))

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

    def _parse_battle_json(self, path):
        """Helper to load and normalize battle.json data to a list of dicts."""
        if not os.path.exists(path):
            return []
        try:
            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)
                if isinstance(data, dict) and "enemies" in data and isinstance(data["enemies"], list):
                    return data["enemies"]
                elif isinstance(data, list):
                    return data
                else:
                    return []
        except Exception as e:
            runtime_globals.game_console.log(f"⚠️ Failed to parse {path}: {e}")
            return []

    def get_enemies(self, area: int, round: int, versions: List[int]) -> List[Optional[GameEnemy]]:
        battle_path = os.path.join(self.folder_path, "battle.json")
        all_enemies = self._parse_battle_json(battle_path)
        if not all_enemies:
            runtime_globals.game_console.log(f"⚠️ Enemy file {battle_path} not found or empty.")
            return [None] * len(versions)

        id = 1
        selected = []
        for v in versions:
            match = next(
                (e for e in all_enemies
                 if int(e.get("area", -1)) == int(area)
                 and int(e.get("round", -1)) == int(round)
                 and int(e.get("version", -1)) == int(v)),
                None
            )
            if match:
                if "handicap" not in match:
                    match["handicap"] = 0
                match["id"] = id
                # Ensure required fields for GameEnemy
                if "unlock" not in match:
                    match["unlock"] = None
                if "prize" not in match:
                    match["prize"] = None
                if "hp" not in match:
                    match["hp"] = 0
                id += 1
                selected.append(copy.deepcopy(GameEnemy(**match)))
            else:
                selected.append(None)
        return selected

    def get_enemy_versions(self, area: int, round_: int) -> list[int]:
        battle_path = os.path.join(self.folder_path, "battle.json")
        all_enemies = self._parse_battle_json(battle_path)
        if not all_enemies:
            runtime_globals.game_console.log(f"⚠️ Enemy file {battle_path} not found or empty.")
            return []
        versions = set()
        for entry in all_enemies:
            if int(entry.get("area", -1)) == int(area) and int(entry.get("round", -1)) == int(round_):
                v = entry.get("version")
                if v is not None:
                    versions.add(v)
        return sorted(versions)

    def area_exists(self, area: int) -> bool:
        battle_path = os.path.join(self.folder_path, "battle.json")
        all_enemies = self._parse_battle_json(battle_path)
        if not all_enemies:
            runtime_globals.game_console.log(f"⚠️ Enemy file {battle_path} not found or empty.")
            return False
        for entry in all_enemies:
            if int(entry.get("area", -1)) == int(area):
                return True
        return False

    def get_area_round_counts(self) -> dict:
        battle_path = os.path.join(self.folder_path, "battle.json")
        all_enemies = self._parse_battle_json(battle_path)
        if not all_enemies:
            runtime_globals.game_console.log(f"⚠️ Enemy file {battle_path} not found or empty.")
            return {}
        area_rounds = {}
        for entry in all_enemies:
            area = int(entry.get("area", -1))
            round_ = int(entry.get("round", -1))
            if area == -1 or round_ == -1:
                continue
            if area not in area_rounds:
                area_rounds[area] = set()
            area_rounds[area].add(round_)
        return {area: len(rounds) for area, rounds in area_rounds.items()}
        
    def is_boss(self, area, round, version):
        """
        Checks if the enemy in the specified area, round, and version is a boss.
        """
        enemies = self.get_enemies(area, round + 1, [version])
        return enemies[0] == None
    
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
